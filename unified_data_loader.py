"""
Unified Data Loader - 统一数据加载器

提供统一的数据访问接口，支持从文件或数据库加载数据
自动处理数据源切换、缓存管理和错误回退

Author: AI Assistant
Date: 2025-02-04
"""

import os
import json
import logging
import pandas as pd
from typing import Optional, Dict, Any, List, Union, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import sqlite3

from octane_db import OctaneSQLiteStore, default_db_path
from unified_cache_manager import UnifiedCacheManager
from db_migration_config import DB_SCHEMA_VERSION, is_using_optimized_schema
from database_utils import with_db_retry, get_connection_pool, DatabaseHelper

logger = logging.getLogger(__name__)


class DataSourceConfig:
    """Data source configuration"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('data_source', self._default_config())
            except Exception as e:
                logger.warning(f"Failed to load config: {e}, using defaults")
        return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration"""
        return {
            "mode": "db_only",  # file_only, db_only, hybrid
            "priority": "database",  # database, file
            "fallback": False,
            "cache_enabled": True,
            "cache_ttl": 3600,  # 1 hour
            "db_backend": os.environ.get("DB_BACKEND", "sqlite"),  # sqlite, postgres
            "pg_url": os.environ.get("POSTGRES_URL", ""),
            "pg_schema": os.environ.get("PG_SCHEMA", "public"),
        }
    
    @property
    def mode(self) -> str:
        return self.config.get('mode', 'hybrid')
    
    @property
    def priority(self) -> str:
        return self.config.get('priority', 'database')
    
    @property
    def fallback_enabled(self) -> bool:
        return self.config.get('fallback', True)
    
    @property
    def cache_enabled(self) -> bool:
        return self.config.get('cache_enabled', True)
    
    @property
    def cache_ttl(self) -> int:
        return self.config.get('cache_ttl', 3600)

    @property
    def db_backend(self) -> str:
        return str(self.config.get("db_backend", "sqlite")).lower()

    @property
    def pg_url(self) -> str:
        return str(self.config.get("pg_url", "")).strip()

    @property
    def pg_schema(self) -> str:
        return str(self.config.get("pg_schema", "public")).strip() or "public"


class UnifiedDataLoader:
    """
    Unified data loader that supports both file and database sources
    
    Features:
    - Automatic source detection and selection
    - Transparent caching
    - Fallback mechanism
    - Unified DataFrame interface
    """
    
    def __init__(self,
                 db_path: Optional[str] = None,
                 config: Optional[DataSourceConfig] = None,
                 use_connection_pool: bool = True):
        self.db_path = db_path or default_db_path()
        self.config = config or DataSourceConfig()
        self.cache_manager = UnifiedCacheManager() if self.config.cache_enabled else None
        self.db_store = None
        self.db_helper = None
        self.pg_conn = None
        self._use_pool = use_connection_pool
        self.db_backend = self.config.db_backend
        self.pg_url = self.config.pg_url
        self.pg_schema = self.config.pg_schema

        if self.db_backend not in {"sqlite", "postgres"}:
            logger.warning(f"Unknown db_backend '{self.db_backend}', fallback to sqlite")
            self.db_backend = "sqlite"

        # Initialize database connection if needed
        if self.config.mode in ['db_only', 'hybrid']:
            try:
                if self.db_backend == "postgres":
                    if not self.pg_url:
                        raise RuntimeError("POSTGRES_URL is empty while db_backend=postgres")
                    self.pg_conn = self._connect_postgres(self.pg_url)
                    logger.info(f"PostgreSQL connection established (schema={self.pg_schema})")
                else:
                    if use_connection_pool:
                        # 使用连接池
                        pool = get_connection_pool(self.db_path)
                        self.db_helper = DatabaseHelper(self.db_path, pool)
                        logger.info(f"SQLite connection pool initialized: {self.db_path}")
                    else:
                        # 使用普通连接
                        self.db_store = OctaneSQLiteStore(self.db_path)
                        logger.info(f"SQLite connection established: {self.db_path}")
            except Exception as e:
                logger.warning(f"Failed to connect to {self.db_backend} database: {e}")
                if self.config.mode == 'db_only':
                    raise

    def _connect_postgres(self, pg_url: str):
        """Create PostgreSQL connection via psycopg/psycopg2."""
        try:
            import psycopg  # type: ignore

            conn = psycopg.connect(pg_url)
            conn.autocommit = True
            return conn
        except Exception:
            import psycopg2  # type: ignore

            conn = psycopg2.connect(pg_url)
            conn.autocommit = True
            return conn

    def _query_pg_dataframe(self, query: str, params: Optional[List[Any]] = None) -> pd.DataFrame:
        """Execute a PostgreSQL query and return DataFrame."""
        if self.pg_conn is None:
            raise RuntimeError("PostgreSQL not initialized")
        cur = self.pg_conn.cursor()
        try:
            cur.execute(f'SET search_path TO "{self.pg_schema}"')
            cur.execute(query, params or [])
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description] if cur.description else []
            return pd.DataFrame(rows, columns=columns)
        finally:
            cur.close()

    def _query_pg_json_row(self, query: str, params: Optional[List[Any]] = None):
        """Execute a PostgreSQL query returning one row."""
        if self.pg_conn is None:
            raise RuntimeError("PostgreSQL not initialized")
        cur = self.pg_conn.cursor()
        try:
            cur.execute(f'SET search_path TO "{self.pg_schema}"')
            cur.execute(query, params or [])
            return cur.fetchone()
        finally:
            cur.close()
    
    def load_defects(self, 
                     year: Optional[int] = None,
                     team: str = "DTSV_China",
                     filters: Optional[Dict[str, Any]] = None,
                     use_cache: bool = True) -> pd.DataFrame:
        """
        Load defects data
        
        Args:
            year: Year filter (None for all years)
            team: Team name
            filters: Additional filters (e.g., {'project': 'idcevo', 'severity': 'Critical'})
            use_cache: Whether to use cache
            
        Returns:
            DataFrame with defects data
        """
        cache_key = f"defects_{year}_{team}_{hash(str(filters))}"
        
        # Try cache first
        if use_cache and self.cache_manager:
            cached_df = self.cache_manager.get_cached_dataframe(cache_key)
            if cached_df is not None:
                logger.info(f"Loaded defects from cache: {cache_key}")
                return self._apply_filters(cached_df, filters)
        
        # Load from primary source
        df = None
        primary_source = self._get_primary_source()
        
        try:
            if primary_source == 'database':
                df = self._load_defects_from_db(year, team)
            else:
                df = self._load_defects_from_file(year)
        except Exception as e:
            logger.error(f"Failed to load from {primary_source}: {e}")
            
            # Try fallback
            if self.config.fallback_enabled:
                fallback_source = 'file' if primary_source == 'database' else 'database'
                logger.info(f"Trying fallback source: {fallback_source}")
                try:
                    if fallback_source == 'database':
                        df = self._load_defects_from_db(year, team)
                    # else:
                    #     df = self._load_defects_from_file(year)
                    else:
                        raise RuntimeError("数据库读取失败后已禁用本地文件回退（defects）")
                except Exception as e2:
                    logger.error(f"Fallback also failed: {e2}")
                    raise
            else:
                raise
        
        if df is None or df.empty:
            logger.warning(f"No defects data found for year={year}, team={team}")
            return pd.DataFrame()
        
        # Apply filters
        df = self._apply_filters(df, filters)
        
        # Cache result
        if use_cache and self.cache_manager:
            self.cache_manager.cache_dataframe(
                cache_key, df, ttl=self.config.cache_ttl
            )
        
        return df
    
    def load_tests(self,
                   report_period: Optional[str] = None,
                   team: str = "DTSV_China",
                   filters: Optional[Dict[str, Any]] = None,
                   use_cache: bool = True) -> pd.DataFrame:
        """
        Load test runs data
        
        Args:
            report_period: Report period (e.g., 'R2501')
            team: Team name
            filters: Additional filters
            use_cache: Whether to use cache
            
        Returns:
            DataFrame with test runs data
        """
        cache_key = f"tests_{report_period}_{team}_{hash(str(filters))}"
        
        # Try cache first
        if use_cache and self.cache_manager:
            cached_df = self.cache_manager.get_cached_dataframe(cache_key)
            if cached_df is not None:
                logger.info(f"Loaded tests from cache: {cache_key}")
                return self._apply_filters(cached_df, filters)
        
        # Load from primary source
        df = None
        primary_source = self._get_primary_source()
        
        try:
            if primary_source == 'database':
                df = self._load_tests_from_db(report_period, team)
            else:
                df = self._load_tests_from_file(report_period)
        except Exception as e:
            logger.error(f"Failed to load tests from {primary_source}: {e}")
            
            # Try fallback
            if self.config.fallback_enabled:
                fallback_source = 'file' if primary_source == 'database' else 'database'
                logger.info(f"Trying fallback source: {fallback_source}")
                try:
                    if fallback_source == 'database':
                        df = self._load_tests_from_db(report_period, team)
                    # else:
                    #     df = self._load_tests_from_file(report_period)
                    else:
                        raise RuntimeError("数据库读取失败后已禁用本地文件回退（tests）")
                except Exception as e2:
                    logger.error(f"Fallback also failed: {e2}")
                    raise
            else:
                raise
        
        if df is None or df.empty:
            logger.warning(f"No test data found for period={report_period}, team={team}")
            return pd.DataFrame()
        
        # Apply filters
        df = self._apply_filters(df, filters)
        
        # Cache result
        if use_cache and self.cache_manager:
            self.cache_manager.cache_dataframe(
                cache_key, df, ttl=self.config.cache_ttl
            )
        
        return df
    
    def load_semantic_catalog(self, 
                             catalog_type: str = "datasets",
                             use_cache: bool = True) -> Dict[str, Any]:
        """
        Load semantic catalog
        
        Args:
            catalog_type: Type of catalog ('datasets', 'charts', 'metrics')
            use_cache: Whether to use cache
            
        Returns:
            Dictionary with catalog data
        """
        cache_key = f"semantic_catalog_{catalog_type}"
        
        # Try cache first
        if use_cache and self.cache_manager:
            cached_data = self.cache_manager.get(cache_key)
            if cached_data is not None:
                logger.info(f"Loaded semantic catalog from cache: {catalog_type}")
                return cached_data
        
        # Load from primary source
        data = None
        primary_source = self._get_primary_source()
        
        try:
            if primary_source == 'database':
                data = self._load_catalog_from_db(catalog_type)
            else:
                data = self._load_catalog_from_file(catalog_type)
        except Exception as e:
            logger.error(f"Failed to load catalog from {primary_source}: {e}")
            
            # Try fallback
            if self.config.fallback_enabled:
                fallback_source = 'file' if primary_source == 'database' else 'database'
                try:
                    if fallback_source == 'database':
                        data = self._load_catalog_from_db(catalog_type)
                    else:
                        data = self._load_catalog_from_file(catalog_type)
                except Exception as e2:
                    logger.error(f"Fallback also failed: {e2}")
                    raise
            else:
                raise
        
        # Cache result
        if use_cache and self.cache_manager and data:
            self.cache_manager.set(cache_key, data, ttl=self.config.cache_ttl)
        
        return data or {}
    
    def load_aida_mappings(self, use_cache: bool = True) -> pd.DataFrame:
        """
        Load AIDA mappings
        
        Args:
            use_cache: Whether to use cache
            
        Returns:
            DataFrame with AIDA mappings
        """
        cache_key = "aida_mappings"
        
        # Try cache first
        if use_cache and self.cache_manager:
            cached_df = self.cache_manager.get_cached_dataframe(cache_key)
            if cached_df is not None:
                logger.info("Loaded AIDA mappings from cache")
                return cached_df
        
        # Load from primary source
        df = None
        primary_source = self._get_primary_source()
        
        try:
            if primary_source == 'database':
                df = self._load_aida_from_db()
            else:
                df = self._load_aida_from_file()
        except Exception as e:
            logger.error(f"Failed to load AIDA from {primary_source}: {e}")
            
            # Try fallback
            if self.config.fallback_enabled:
                fallback_source = 'file' if primary_source == 'database' else 'database'
                try:
                    if fallback_source == 'database':
                        df = self._load_aida_from_db()
                    else:
                        df = self._load_aida_from_file()
                except Exception as e2:
                    logger.error(f"Fallback also failed: {e2}")
                    raise
            else:
                raise

        if (df is None or df.empty) and self.config.fallback_enabled:
            fallback_source = 'file' if primary_source == 'database' else 'database'
            if fallback_source != primary_source:
                try:
                    if fallback_source == 'database':
                        fallback_df = self._load_aida_from_db()
                    else:
                        fallback_df = self._load_aida_from_file()
                    if fallback_df is not None and not fallback_df.empty:
                        logger.warning(
                            f"AIDA mappings from {primary_source} is empty, switched to {fallback_source}"
                        )
                        df = fallback_df
                except Exception as e3:
                    logger.error(f"AIDA fallback after empty primary failed: {e3}")
        
        if df is None or df.empty:
            logger.warning("No AIDA mappings found")
            return pd.DataFrame()
        
        # Cache result
        if use_cache and self.cache_manager:
            self.cache_manager.cache_dataframe(
                cache_key, df, ttl=self.config.cache_ttl
            )
        
        return df
    
    def _get_primary_source(self) -> str:
        """Determine primary data source"""
        if self.config.mode == 'file_only':
            return 'file'
        elif self.config.mode == 'db_only':
            return 'database'
        else:  # hybrid
            return self.config.priority
    
    def _load_defects_from_db(self, year: Optional[int], team: str) -> pd.DataFrame:
        """Load defects from database"""
        if self.db_backend == "postgres":
            if self.pg_conn is None:
                raise RuntimeError("PostgreSQL not initialized")
        elif not self.db_store and not self.db_helper:
            raise RuntimeError("SQLite database not initialized")

        # 如果使用优化后的表结构，直接查询 octane_defects
        if is_using_optimized_schema():
            return self._load_defects_from_optimized_table(year, team)

        if self.db_backend == "postgres":
            raise RuntimeError("PostgreSQL read currently requires optimized schema")

        # SQLite 旧表查询方式
        if self.db_store is None:
            self.db_store = OctaneSQLiteStore(self.db_path)
        payload = self.db_store.get_payload(
            kind='defects',
            team=team,
            year=year,
            spec='default'
        )

        if not payload or 'data' not in payload:
            return pd.DataFrame()

        return pd.DataFrame(payload['data'])

    @with_db_retry(max_retries=3)
    def _load_defects_from_optimized_table(self, year: Optional[int], team: str) -> pd.DataFrame:
        """从优化后的 octane_defects 表加载数据"""
        if self.db_backend == "postgres":
            return self._load_defects_from_optimized_table_pg(year, team)

        conn = sqlite3.connect(self.db_path)
        try:
            # 构建查询 - 选择常用字段，避免加载 raw_json 大字段
            query = """
                SELECT
                    defect_id as id, name, creation_time, last_modified,
                    team, problem_finder_team, program, author,
                    aida_businesskey as aida_businesskey_udf, aida_english, top_aida,
                    product_areas, user_tags,
                    phase, severity,
                    problem_severity as problem_severity_udf, status_phase,
                    owner, detected_by,
                    detected_in_release, software_version as software_version_udf,
                    vin as vin_udf, assigned_ecu, lead_model as lead_model_udf, ecu_no_of_changes as ecu_no_of_changes_udf,
                    parent_id, parent_child_type, relation_to as relation_to_udf,
                    test_week, risk_score, fv, fvp,
                    tqr as tqr_udf, blocking_reason as blocking_reason_udf, error_occurrence as error_occurrence_udf,
                    solution_responsible as solution_responsible_udf, solution_cluster, solution_cluster as domain,
                    reporting_class as reporting_class_udf,
                    function_responsible as function_responsible1_udf, involved_i_step as involved_i_step1_udf,
                    first_use_sop_of_function as first_use_sop_of_function_udf,
                    tolerated_count as tolerated_count_udf, reprel_changes as reprel_changes_udf,
                    json_extract(raw_json, '$.reporting_class_udf') as reporting_class_json,
                    year, fetched_at
                FROM octane_defects
                WHERE 1=1
            """
            params = []

            if year:
                query += " AND year = ?"
                params.append(year)
            if team:
                query += " AND (team = ? OR problem_finder_team = ?)"
                params.extend([team, team])

            df = pd.read_sql_query(query, conn, params=params)
            df = self._postprocess_defects_dataframe(df)
            logger.info(f"Loaded {len(df)} defects from optimized table (sqlite)")
            return df

        except Exception as e:
            logger.error(f"Failed to load from optimized table: {e}")
            raise
        finally:
            conn.close()

    def _load_defects_from_optimized_table_pg(self, year: Optional[int], team: str) -> pd.DataFrame:
        """从 PostgreSQL octane_defects 表加载数据。"""
        query = """
            SELECT
                defect_id as id, name, creation_time, last_modified,
                team, problem_finder_team, program, author,
                aida_businesskey as aida_businesskey_udf, aida_english, top_aida,
                product_areas, user_tags,
                phase, severity,
                problem_severity as problem_severity_udf, status_phase,
                owner, detected_by,
                detected_in_release, software_version as software_version_udf,
                vin as vin_udf, assigned_ecu, lead_model as lead_model_udf, ecu_no_of_changes as ecu_no_of_changes_udf,
                parent_id, parent_child_type, relation_to as relation_to_udf,
                test_week, risk_score, fv, fvp,
                tqr as tqr_udf, blocking_reason as blocking_reason_udf, error_occurrence as error_occurrence_udf,
                solution_responsible as solution_responsible_udf, solution_cluster, solution_cluster as domain,
                reporting_class as reporting_class_udf,
                function_responsible as function_responsible1_udf, involved_i_step as involved_i_step1_udf,
                first_use_sop_of_function as first_use_sop_of_function_udf,
                tolerated_count as tolerated_count_udf, reprel_changes as reprel_changes_udf,
                raw_json -> 'reporting_class_udf' as reporting_class_json,
                year, fetched_at
            FROM octane_defects
            WHERE 1=1
        """
        params: List[Any] = []

        if year:
            query += " AND year = %s"
            params.append(year)
        if team:
            query += " AND (team = %s OR problem_finder_team = %s)"
            params.extend([team, team])

        df = self._query_pg_dataframe(query, params)
        df = self._postprocess_defects_dataframe(df)
        logger.info(f"Loaded {len(df)} defects from optimized table (postgres)")
        return df

    def _postprocess_defects_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize defects dataframe loaded from SQLite/PostgreSQL."""
        if df.empty:
            return df

        # 处理存储为逗号分隔字符串的字段
        csv_columns = ['product_areas', 'user_tags']
        for col in csv_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: x.split(',') if x and isinstance(x, str) else [])

        # 处理 JSON 字符串字段
        json_columns = ['tqr_udf']
        for col in json_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: json.loads(x) if x and isinstance(x, str) and x.startswith('{') else x)

        # 从 raw_json 中提取 classification
        def extract_classification(reporting_class_json):
            if not reporting_class_json:
                return []
            try:
                if isinstance(reporting_class_json, str):
                    data = json.loads(reporting_class_json)
                else:
                    data = reporting_class_json

                if isinstance(data, dict) and 'data' in data:
                    return [item.get('name', '') for item in data['data'] if isinstance(item, dict) and item.get('name')]
                return []
            except Exception:
                return []

        if 'reporting_class_json' in df.columns:
            df['classification'] = df['reporting_class_json'].apply(extract_classification)
            # 确保没有 None 值
            df['classification'] = df['classification'].apply(lambda x: x if x is not None else [])
            # 删除临时列
            df = df.drop(columns=['reporting_class_json'])
        else:
            df['classification'] = [[] for _ in range(len(df))]

        # 再次确保 classification 列没有 None（双重保险）
        df['classification'] = df['classification'].fillna('').apply(lambda x: x if isinstance(x, list) else [])

        # 从 user_tags 中提取 matrix 标签
        def extract_matrix(user_tags):
            # 处理字符串格式（从数据库加载的user_tags是逗号分隔的字符串）
            if isinstance(user_tags, str):
                tags = [t.strip() for t in user_tags.split(',') if t.strip()]
                for tag in tags:
                    if 'matrix-' in tag.lower():
                        return tag
                return ''
            # 处理列表格式
            if isinstance(user_tags, list):
                for tag in user_tags:
                    tag_str = str(tag).strip()
                    if tag_str and 'matrix-' in tag_str.lower():
                        return tag_str
                return ''
            return ''

        if 'user_tags' in df.columns:
            df['matrix'] = df['user_tags'].apply(extract_matrix)
            df['matrix_display'] = df['matrix'].apply(
                lambda x: x.replace('matrix-', '').replace('Matrix-', '').upper() if x else ''
            )

        # 添加缺失的默认列
        default_str_columns = ['tester', 'severity_group', 'occurrence', 'release', 'istep', 'blocking_reason_udf', 'market']
        for col in default_str_columns:
            if col not in df.columns:
                df[col] = ''

        default_list_columns = ['tags', 'ticket_quality']
        for col in default_list_columns:
            if col not in df.columns:
                df[col] = [[] for _ in range(len(df))]

        # 从 product_areas 设置 aidas（现在是逗号分隔的字符串列表）
        if 'product_areas' in df.columns:
            df['aidas'] = df['product_areas'].apply(
                lambda x: [item.strip() for item in x if item.strip()] if isinstance(x, list) else []
            )
        else:
            df['aidas'] = [[] for _ in range(len(df))]

        # 添加 phase.name 和 severity.name 别名（兼容旧代码）
        if 'phase' in df.columns:
            df['phase.name'] = df['phase']
        if 'severity' in df.columns:
            df['severity.name'] = df['severity']
        if 'detected_in_release' in df.columns:
            df['detected_in_release.name'] = df['detected_in_release']

        # 添加其他兼容字段
        if 'assigned_ecu' in df.columns:
            df['ecu'] = df['assigned_ecu']
        if 'ecu_no_of_changes_udf' in df.columns:
            df['pingpong'] = df['ecu_no_of_changes_udf']
        if 'parent_child_type' in df.columns:
            df['parent_child'] = df['parent_child_type']
        if 'first_use_sop_of_function_udf' in df.columns:
            df['pu'] = df['first_use_sop_of_function_udf']
        if 'program' in df.columns:
            df['project'] = df['program']

        return df
    
    def _load_defects_from_file(self, year: Optional[int]) -> pd.DataFrame:
        """Load defects from JSON files"""
        defect_folder = Path("defect")
        if not defect_folder.exists():
            raise FileNotFoundError(f"Defect folder not found: {defect_folder}")
        
        dfs = []
        pattern = f"{year}_defect.json" if year else "*_defect.json"
        
        for filepath in defect_folder.glob(pattern):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'data' in data and isinstance(data['data'], list):
                        df = pd.DataFrame(data['data'])
                        dfs.append(df)
            except Exception as e:
                logger.warning(f"Failed to load {filepath}: {e}")
        
        if not dfs:
            return pd.DataFrame()
        
        return pd.concat(dfs, ignore_index=True)
    
    def _load_tests_from_db(self, report_period: Optional[str], team: str) -> pd.DataFrame:
        """Load tests from database"""
        if self.db_backend == "postgres":
            if self.pg_conn is None:
                raise RuntimeError("PostgreSQL not initialized")
        elif not self.db_store and not self.db_helper:
            raise RuntimeError("SQLite database not initialized")

        # 如果使用优化后的表结构
        if is_using_optimized_schema():
            return self._load_tests_from_optimized_table(report_period, team)

        if self.db_backend == "postgres":
            raise RuntimeError("PostgreSQL read currently requires optimized schema")

        # SQLite 旧表查询方式
        spec = report_period or 'all'
        if self.db_store is None:
            self.db_store = OctaneSQLiteStore(self.db_path)
        payload = self.db_store.get_payload(
            kind='tests',
            team=team,
            year=None,
            spec=spec
        )

        if not payload or 'data' not in payload:
            return pd.DataFrame()

        return pd.DataFrame(payload['data'])

    @with_db_retry(max_retries=3)
    def _load_tests_from_optimized_table(self, report_period: Optional[str], team: str) -> pd.DataFrame:
        """从优化后的 octane_manual_runs 表加载数据"""
        if self.db_backend == "postgres":
            return self._load_tests_from_optimized_table_pg(report_period, team)

        conn = sqlite3.connect(self.db_path)
        try:
            query = """
                SELECT
                    mr_id, name, test_name, test_id,
                    creation_time, last_modified, started, finished,
                    defect_id,
                    run_team, program, author,
                    run_by, status, native_status, is_completed, steps_num, version_stamp,
                    release, exec_model_series, execution_sw_version, test_version,
                    product_areas, domain, test_phase, testing_tool_type,
                    taxonomies, set_field, target_ecu_conf, testplatformid,
                    year, spec, fetched_at
                FROM octane_manual_runs
                WHERE 1=1
            """
            params = []

            if report_period:
                query += " AND spec = ?"
                params.append(report_period)
            if team:
                query += " AND run_team = ?"
                params.append(team)

            df = pd.read_sql_query(query, conn, params=params)
            df = self._postprocess_manual_runs_dataframe(df)
            logger.info(f"Loaded {len(df)} manual runs from optimized table (sqlite)")
            return df

        except Exception as e:
            logger.error(f"Failed to load tests from optimized table: {e}")
            raise
        finally:
            conn.close()

    def _load_tests_from_optimized_table_pg(self, report_period: Optional[str], team: str) -> pd.DataFrame:
        """从 PostgreSQL octane_manual_runs 表加载数据。"""
        query = """
            SELECT
                mr_id, name, test_name, test_id,
                creation_time, last_modified, started, finished,
                defect_id,
                run_team, program, author,
                run_by, status, native_status, is_completed, steps_num, version_stamp,
                release, exec_model_series, execution_sw_version, test_version,
                product_areas, domain, test_phase, testing_tool_type,
                taxonomies, set_field, target_ecu_conf, testplatformid,
                year, spec, fetched_at
            FROM octane_manual_runs
            WHERE 1=1
        """
        params: List[Any] = []

        if report_period:
            query += " AND spec = %s"
            params.append(report_period)
        if team:
            query += " AND run_team = %s"
            params.append(team)

        df = self._query_pg_dataframe(query, params)
        df = self._postprocess_manual_runs_dataframe(df)
        logger.info(f"Loaded {len(df)} manual runs from optimized table (postgres)")
        return df

    def _postprocess_manual_runs_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize manual runs dataframe loaded from SQLite/PostgreSQL."""
        if df.empty:
            return df

        # 处理逗号分隔字符串字段
        csv_columns = ['product_areas', 'taxonomies']
        for col in csv_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: x.split(',') if x and isinstance(x, str) else [])
        return df
    
    def _load_tests_from_file(self, report_period: Optional[str]) -> pd.DataFrame:
        """Load tests from JSON files"""
        mr_folder = Path("mr")
        if not mr_folder.exists():
            raise FileNotFoundError(f"MR folder not found: {mr_folder}")
        
        dfs = []
        pattern = f"{report_period}.json" if report_period else "R*.json"
        
        for filepath in mr_folder.glob(pattern):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'data' in data and isinstance(data['data'], list):
                        df = pd.DataFrame(data['data'])
                        dfs.append(df)
            except Exception as e:
                logger.warning(f"Failed to load {filepath}: {e}")
        
        if not dfs:
            return pd.DataFrame()
        
        return pd.concat(dfs, ignore_index=True)
    
    def _load_catalog_from_db(self, catalog_type: str) -> Dict[str, Any]:
        """Load semantic catalog from database"""
        if self.db_backend == "postgres":
            row = self._query_pg_json_row(
                "SELECT catalog_json FROM semantic_catalog WHERE catalog_type = %s",
                [catalog_type],
            )
            if row:
                return json.loads(row[0]) if isinstance(row[0], str) else row[0]
            return {}

        if not self.db_store and not self.db_helper:
            raise RuntimeError("SQLite database not initialized")

        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS semantic_catalog (
                    catalog_type TEXT PRIMARY KEY,
                    catalog_json TEXT NOT NULL,
                    updated_at TEXT
                )
                """
            )
            cursor = conn.cursor()
            row = cursor.execute(
                "SELECT catalog_json FROM semantic_catalog WHERE catalog_type = ?",
                (catalog_type,)
            ).fetchone()

            if row:
                return json.loads(row[0])
            try:
                seed = self._load_catalog_from_file(catalog_type)
            except Exception:
                return {}
            try:
                cursor.execute(
                    """
                    INSERT INTO semantic_catalog (catalog_type, catalog_json, updated_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(catalog_type) DO UPDATE SET
                        catalog_json=excluded.catalog_json,
                        updated_at=excluded.updated_at
                    """,
                    (catalog_type, json.dumps(seed, ensure_ascii=False), datetime.utcnow().isoformat() + "Z"),
                )
                conn.commit()
            except Exception:
                pass
            return seed or {}
        finally:
            conn.close()
    
    def _load_catalog_from_file(self, catalog_type: str) -> Dict[str, Any]:
        """Load semantic catalog from JSON file"""
        catalog_path = Path(f"semantic_catalog/{catalog_type}.json")
        if not catalog_path.exists():
            raise FileNotFoundError(f"Catalog file not found: {catalog_path}")
        
        with open(catalog_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_aida_from_db(self) -> pd.DataFrame:
        """Load AIDA mappings from database"""
        if self.db_backend == "postgres":
            return self._query_pg_dataframe("SELECT * FROM aida_mappings")

        if not self.db_store and not self.db_helper:
            raise RuntimeError("SQLite database not initialized")

        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query("SELECT * FROM aida_mappings", conn)
            return df
        finally:
            conn.close()
    
    def _load_aida_from_file(self) -> pd.DataFrame:
        """Load AIDA mappings from JSON files"""
        aida_folder = Path("aida")
        if not aida_folder.exists():
            raise FileNotFoundError(f"AIDA folder not found: {aida_folder}")
        
        dfs = []
        for filepath in aida_folder.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'data' in data and isinstance(data['data'], list):
                        df = pd.DataFrame(data['data'])
                        dfs.append(df)
            except Exception as e:
                logger.warning(f"Failed to load {filepath}: {e}")
        
        if not dfs:
            return pd.DataFrame()
        
        return pd.concat(dfs, ignore_index=True)
    
    def _apply_filters(self, df: pd.DataFrame, filters: Optional[Dict[str, Any]]) -> pd.DataFrame:
        """Apply filters to DataFrame"""
        if not filters or df.empty:
            return df
        
        filtered_df = df.copy()
        for column, value in filters.items():
            if column in filtered_df.columns:
                if isinstance(value, list):
                    filtered_df = filtered_df[filtered_df[column].isin(value)]
                else:
                    filtered_df = filtered_df[filtered_df[column] == value]
        
        return filtered_df
    
    def get_data_source_info(self) -> Dict[str, Any]:
        """Get information about current data sources"""
        db_available = (
            (self.db_backend == "postgres" and self.pg_conn is not None)
            or (self.db_backend == "sqlite" and (self.db_store is not None or self.db_helper is not None))
        )
        info = {
            "mode": self.config.mode,
            "priority": self.config.priority,
            "fallback_enabled": self.config.fallback_enabled,
            "cache_enabled": self.config.cache_enabled,
            "db_backend": self.db_backend,
            "database_available": db_available,
            "database_path": self.db_path if self.db_backend == "sqlite" else None,
            "pg_schema": self.pg_schema if self.db_backend == "postgres" else None,
        }
        
        # Check file sources
        info["file_sources"] = {
            "defects": Path("defect").exists(),
            "tests": Path("mr").exists(),
            "semantic_catalog": Path("semantic_catalog").exists(),
            "aida": Path("aida").exists()
        }
        
        return info
    
    def close(self):
        """Close database connection"""
        if self.db_store:
            self.db_store.close()
        if self.db_helper:
            self.db_helper.close()
        if self.pg_conn:
            self.pg_conn.close()


# Global instance for easy access
_global_loader = None

def get_data_loader() -> UnifiedDataLoader:
    """Get global data loader instance"""
    global _global_loader
    if _global_loader is None:
        _global_loader = UnifiedDataLoader()
    return _global_loader


if __name__ == "__main__":
    # Test the loader
    logging.basicConfig(level=logging.INFO)
    
    loader = UnifiedDataLoader()
    
    print("\n=== Data Source Info ===")
    info = loader.get_data_source_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    
    print("\n=== Testing Defects Load ===")
    try:
        df = loader.load_defects(year=2025, filters={'project': 'idcevo'})
        print(f"Loaded {len(df)} defects")
        if not df.empty:
            print(f"Columns: {df.columns.tolist()[:10]}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n=== Testing Semantic Catalog Load ===")
    try:
        catalog = loader.load_semantic_catalog('datasets')
        print(f"Loaded catalog with {len(catalog.get('datasets', []))} datasets")
    except Exception as e:
        print(f"Error: {e}")
    
    loader.close()
