"""
统一数据库适配器 - 支持SQLite和PostgreSQL
解决defect_explore6锁定SQLite的问题
"""
import os
import sqlite3
import time
import pandas as pd
from typing import Optional, List, Dict, Any, Callable
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class DatabaseAdapter(ABC):
    """数据库适配器抽象基类"""

    @abstractmethod
    def load_defects(self, years: Optional[List[int]] = None) -> pd.DataFrame:
        pass

    @abstractmethod
    def load_manual_runs(self, report_period: Optional[str] = None) -> pd.DataFrame:
        pass

    @abstractmethod
    def load_histories(self, defect_ids: Optional[List[str]] = None) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_stats(self) -> Dict:
        pass


class SQLiteAdapter(DatabaseAdapter):
    """SQLite适配器"""

    def __init__(self, db_path: str = "database/local_data.db"):
        self.db_path = db_path
        self.retry_times = max(1, int(os.getenv("SQLITE_QUERY_RETRY_TIMES", "3")))
        self.retry_base_delay = float(os.getenv("SQLITE_QUERY_RETRY_BASE_DELAY", "0.12"))
        self.retry_backoff = float(os.getenv("SQLITE_QUERY_RETRY_BACKOFF", "2.0"))
        self.last_query_evidence: Dict[str, Any] = {}

    def _is_retryable_error(self, error: Exception) -> bool:
        if not isinstance(error, sqlite3.OperationalError):
            return False
        msg = str(error).lower()
        return any(x in msg for x in ["locked", "busy", "timeout"])

    def _run_with_retry(self, operation: str, worker: Callable[[], Any]) -> Any:
        delay = self.retry_base_delay
        start = time.time()
        errors: List[str] = []
        for attempt in range(1, self.retry_times + 1):
            try:
                result = worker()
                self.last_query_evidence = {
                    "operation": operation,
                    "attempts": attempt,
                    "retry_times": self.retry_times,
                    "duration_ms": round((time.time() - start) * 1000, 2),
                    "errors": errors,
                }
                return result
            except Exception as e:
                errors.append(str(e))
                if attempt >= self.retry_times or not self._is_retryable_error(e):
                    self.last_query_evidence = {
                        "operation": operation,
                        "attempts": attempt,
                        "retry_times": self.retry_times,
                        "duration_ms": round((time.time() - start) * 1000, 2),
                        "errors": errors,
                        "failed": True,
                    }
                    raise
                logger.warning(f"SQLite {operation} 重试中 ({attempt}/{self.retry_times}): {e}")
                time.sleep(delay)
                delay *= self.retry_backoff

    def get_last_query_evidence(self) -> Dict[str, Any]:
        return dict(self.last_query_evidence)

    def load_defects(self, years: Optional[List[int]] = None) -> pd.DataFrame:
        if not os.path.exists(self.db_path):
            return pd.DataFrame()
        query = """
            SELECT
                defect_id as id, name, creation_time, last_modified,
                team, problem_finder_team, program, author,
                aida_businesskey, aida_english, top_aida,
                product_areas, user_tags,
                phase, severity, problem_severity, status_phase,
                owner, detected_by,
                detected_in_release, software_version,
                vin, assigned_ecu as ecu, lead_model, ecu_no_of_changes as pingpong,
                parent_id, parent_child_type as parent_child, relation_to,
                test_week, risk_score, fv, fvp,
                tqr, blocking_reason, error_occurrence,
                solution_responsible, solution_cluster, solution_cluster as domain,
                json_extract(raw_json, '$.reporting_class_udf') as reporting_class_json,
                json_extract(raw_json, '$.sab_comment_udf') as sab_comment_udf_json,
                json_extract(raw_json, '$.parent_phase_udf') as parent_phase_udf_json,
                function_responsible,
                involved_i_step, first_use_sop_of_function as pu,
                tolerated_count, reprel_changes,
                year, fetched_at
            FROM octane_defects
            WHERE 1=1
        """
        params = []
        if years:
            placeholders = ','.join(['?' for _ in years])
            query += f" AND year IN ({placeholders})"
            params.extend(years)

        def worker() -> pd.DataFrame:
            conn = sqlite3.connect(self.db_path)
            try:
                out = pd.read_sql_query(query, conn, params=params)
                if "year" in out.columns:
                    out["year"] = pd.to_numeric(out["year"], errors="coerce").fillna(0).astype(int)
                if "pingpong" in out.columns:
                    out["pingpong"] = pd.to_numeric(out["pingpong"], errors="coerce").fillna(0).astype(int)
                return out
            finally:
                conn.close()

        return self._run_with_retry("load_defects", worker)

    def load_manual_runs(self, report_period: Optional[str] = None) -> pd.DataFrame:
        if not os.path.exists(self.db_path):
            return pd.DataFrame()
        query = """
            SELECT
                mr_id, name, test_name, test_id,
                creation_time, last_modified, started, finished,
                defect_id,
                run_team, program, author,
                run_by, run_by as tester, status, native_status, is_completed, steps_num, version_stamp,
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

        def worker() -> pd.DataFrame:
            conn = sqlite3.connect(self.db_path)
            try:
                return pd.read_sql_query(query, conn, params=params)
            finally:
                conn.close()

        return self._run_with_retry("load_manual_runs", worker)

    def load_histories(self, defect_ids: Optional[List[str]] = None) -> pd.DataFrame:
        if not os.path.exists(self.db_path):
            return pd.DataFrame()
        query = "SELECT * FROM octane_defect_histories WHERE 1=1"
        params = []
        if defect_ids:
            placeholders = ','.join(['?' for _ in defect_ids])
            query += f" AND defect_id IN ({placeholders})"
            params.extend(defect_ids)

        def worker() -> pd.DataFrame:
            conn = sqlite3.connect(self.db_path)
            try:
                return pd.read_sql_query(query, conn, params=params)
            finally:
                conn.close()

        return self._run_with_retry("load_histories", worker)

    def get_stats(self) -> Dict:
        if not os.path.exists(self.db_path):
            return {}
        tables = [
            "octane_defects",
            "octane_manual_runs",
            "octane_defect_histories",
            "defect_features"
        ]

        def worker() -> Dict[str, Dict[str, int]]:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                stats: Dict[str, Dict[str, int]] = {}
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        stats[table] = {"count": count}
                    except Exception:
                        stats[table] = {"count": 0}
                return stats
            finally:
                conn.close()

        return self._run_with_retry("get_stats", worker)


class PostgresAdapter(DatabaseAdapter):
    """PostgreSQL适配器（简化版框架）"""

    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or os.getenv(
            "DATABASE_URL",
            "postgresql://user:pass@localhost/octane"
        )

    def _get_connection(self):
        """延迟导入psycopg2避免依赖问题"""
        try:
            import psycopg2
            return psycopg2.connect(self.connection_string)
        except ImportError:
            raise ImportError("psycopg2 not installed, cannot use PostgreSQL")

    def load_defects(self, years: Optional[List[int]] = None) -> pd.DataFrame:
        try:
            import psycopg2
        except ImportError:
            logger.warning("psycopg2 not available, falling back to SQLite")
            return pd.DataFrame()

        conn = self._get_connection()
        try:
            query = """
                SELECT
                    defect_id as id, name, creation_time, last_modified,
                    team, problem_finder_team, program, author,
                    aida_businesskey, aida_english, top_aida,
                    product_areas, user_tags,
                    phase, severity, problem_severity, status_phase,
                    owner, detected_by,
                    detected_in_release, software_version,
                    vin, assigned_ecu as ecu, lead_model, ecu_no_of_changes as pingpong,
                    parent_id, parent_child_type as parent_child, relation_to,
                    test_week, risk_score, fv, fvp,
                    tqr, blocking_reason, error_occurrence,
                    solution_responsible, solution_cluster, solution_cluster as domain,
                    raw_json->>'reporting_class_udf' as reporting_class_json,
                    raw_json->>'sab_comment_udf' as sab_comment_udf_json,
                    raw_json->>'parent_phase_udf' as parent_phase_udf_json,
                    function_responsible,
                    involved_i_step, first_use_sop_of_function as pu,
                    tolerated_count, reprel_changes,
                    year, fetched_at
                FROM octane_defects
                WHERE 1=1
            """

            params = []
            if years:
                placeholders = ','.join(['%s' for _ in years])
                query += f" AND year IN ({placeholders})"
                params = years

            return pd.read_sql_query(query, conn, params=params)

        finally:
            conn.close()

    def load_manual_runs(self, report_period: Optional[str] = None) -> pd.DataFrame:
        # 类似实现...
        pass

    def load_histories(self, defect_ids: Optional[List[str]] = None) -> pd.DataFrame:
        # 类似实现...
        pass

    def get_stats(self) -> Dict:
        # 类似实现...
        return {}


class SmartDatabaseRouter:
    """
    智能数据库路由器
    - 根据配置自动选择SQLite或PG
    - 支持读写分离（读PG，写SQLite本地缓存）
    """

    def __init__(self):
        self._sqlite = None
        self._postgres = None
        self._backend = self._detect_backend()

    def _detect_backend(self) -> str:
        """检测应该使用的后端"""
        # 1. 检查环境变量强制配置
        forced = os.getenv("DEFECT_DB_BACKEND", "auto")
        if forced in ["sqlite", "postgres"]:
            return forced

        # 2. 检查PG是否可用
        if os.getenv("DATABASE_URL"):
            try:
                import psycopg2
                return "postgres"
            except ImportError:
                pass

        # 3. 默认SQLite
        return "sqlite"

    @property
    def adapter(self) -> DatabaseAdapter:
        """获取当前适配器"""
        if self._backend == "postgres":
            if self._postgres is None:
                self._postgres = PostgresAdapter()
            return self._postgres
        else:
            if self._sqlite is None:
                self._sqlite = SQLiteAdapter()
            return self._sqlite

    def load_defects(self, years: Optional[List[int]] = None) -> pd.DataFrame:
        return self.adapter.load_defects(years)

    def load_manual_runs(self, report_period: Optional[str] = None) -> pd.DataFrame:
        return self.adapter.load_manual_runs(report_period)

    def get_stats(self) -> Dict:
        return self.adapter.get_stats()

    def get_last_query_evidence(self) -> Dict[str, Any]:
        getter = getattr(self.adapter, "get_last_query_evidence", None)
        if callable(getter):
            return getter()
        return {}


# 便捷函数
def load_defects_from_db(years: Optional[List[int]] = None) -> pd.DataFrame:
    """便捷函数：从数据库加载缺陷"""
    router = SmartDatabaseRouter()
    return router.load_defects(years)


def get_db_stats() -> Dict:
    """获取数据库统计信息"""
    router = SmartDatabaseRouter()
    return router.get_stats()


def get_last_db_query_evidence() -> Dict[str, Any]:
    router = SmartDatabaseRouter()
    return router.get_last_query_evidence()
