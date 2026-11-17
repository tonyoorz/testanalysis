"""
数据库Master数据加载器
替代硬编码文件读取，支持动态年份和多数据源
"""
import os
import sqlite3
import pandas as pd
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class MasterDataLoader:
    """
    统一Master数据加载器
    优先从数据库读取，支持文件回退
    """

    def __init__(self, db_path: str = "database/local_data.db"):
        self.db_path = db_path
        self._cache = {}

    def load_master_data(
        self,
        years: Optional[List[int]] = None,
        use_file_fallback: bool = False
    ) -> pd.DataFrame:
        """
        加载Master数据（父票信息）

        Args:
            years: 年份列表，如[2025, 2026]，None则全部
            use_file_fallback: 是否允许文件回退

        Returns:
            Master DataFrame
        """
        # 1. 优先从数据库读取
        df = self._load_from_db(years)

        if df.empty and use_file_fallback:
            # 2. 数据库为空，尝试文件
            logger.warning("DB master empty, trying file fallback")
            df = self._load_from_files(years)

        return df

    def _load_from_db(self, years: Optional[List[int]] = None) -> pd.DataFrame:
        """从SQLite读取master数据"""
        if not os.path.exists(self.db_path):
            return pd.DataFrame()

        try:
            conn = sqlite3.connect(self.db_path)

            # 构建查询 - 从defects表提取master相关信息
            query = """
                SELECT
                    defect_id,
                    name,
                    phase,
                    status_phase,
                    severity,
                    detected_in_release,
                    creation_time,
                    team,
                    program,
                    -- 判断是否为master的特征
                    CASE
                        WHEN defect_id LIKE '%parent%' OR defect_id IN (
                            SELECT DISTINCT parent_id FROM defect_relations
                        ) THEN 1
                        ELSE 0
                    END as is_master
                FROM octane_defects
                WHERE 1=1
            """

            if years:
                year_conditions = []
                for year in years:
                    year_conditions.append(f"creation_time LIKE '{year}%'")
                if year_conditions:
                    query += " AND (" + " OR ".join(year_conditions) + ")"

            df = pd.read_sql_query(query, conn)
            conn.close()

            # 标记master票
            df['is_master'] = df['is_master'].astype(bool)

            logger.info(f"Loaded {len(df)} master records from DB")
            return df

        except Exception as e:
            logger.error(f"DB master load failed: {e}")
            return pd.DataFrame()

    def _load_from_files(self, years: Optional[List[int]] = None) -> pd.DataFrame:
        """从文件读取master（兼容性代码）"""
        import json

        if years is None:
            years = [2025, 2026]  # 默认年份

        all_masters = []

        for year in years:
            master_file = f"defect/{year}_defect_master.json"
            if not os.path.exists(master_file):
                continue

            try:
                with open(master_file, encoding='utf8') as f:
                    data = json.load(f)

                if isinstance(data, dict) and "data" in data:
                    data = data["data"]

                df = pd.DataFrame(data)
                df['source_year'] = year
                all_masters.append(df)

            except Exception as e:
                logger.warning(f"Failed to load {master_file}: {e}")

        if all_masters:
            return pd.concat(all_masters, ignore_index=True)

        return pd.DataFrame()

    def get_available_years(self) -> List[int]:
        """获取数据库中可用的年份"""
        if not os.path.exists(self.db_path):
            return [2025, 2026]  # 默认值

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("""
                SELECT DISTINCT SUBSTR(creation_time, 1, 4) as year
                FROM octane_defects
                WHERE creation_time IS NOT NULL
                ORDER BY year
            """)
            years = [int(row[0]) for row in cursor.fetchall() if row[0]]
            conn.close()
            return years if years else [2025, 2026]
        except:
            return [2025, 2026]


def load_master_data_dynamic(
    years: Optional[List[int]] = None,
    db_path: str = "database/local_data.db"
) -> pd.DataFrame:
    """
    便捷函数：动态加载master数据

    Usage:
        # 自动检测年份
        master_df = load_master_data_dynamic()

        # 指定年份
        master_df = load_master_data_dynamic(years=[2025, 2026])
    """
    loader = MasterDataLoader(db_path)

    # 如果未指定年份，自动检测
    if years is None:
        years = loader.get_available_years()
        logger.info(f"Auto-detected years: {years}")

    return loader.load_master_data(years=years)
