"""
智能缓存管理器 - 支持DB和文件双重感知
解决pickle缓存只看文件mtime不看DB的问题
"""
import os
import pickle
import hashlib
import sqlite3
import time
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SmartCacheManager:
    """
    智能缓存管理器
    - 同时感知文件和数据库的变更
    - 支持DB表行数、更新时间作为缓存key
    """

    def __init__(self, cache_dir: str = "cache", db_path: str = "database/local_data.db"):
        self.cache_dir = cache_dir
        self.db_path = db_path
        self._db_stats_cache = {}

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def get_cache_key(self, data_sources: Dict[str, Any]) -> str:
        """
        生成智能缓存Key

        Args:
            data_sources: 数据源配置，如：
                {
                    "files": ["defect/2025_defect.json"],
                    "db_tables": ["octane_defects", "defect_features"],
                    "years": [2025, 2026]
                }
        """
        hasher = hashlib.md5()

        # 1. 文件mtime贡献
        files = data_sources.get("files", [])
        for f in files:
            if os.path.exists(f):
                mtime = os.path.getmtime(f)
                hasher.update(f"{f}:{mtime}".encode())

        # 2. DB状态贡献（关键改进）
        tables = data_sources.get("db_tables", [])
        db_stats = self._get_db_stats(tables)
        for table, stats in sorted(db_stats.items()):
            stat_str = f"{table}:{stats['count']}:{stats['max_modified']}"
            hasher.update(stat_str.encode())

        return hasher.hexdigest()[:16]

    def _get_db_stats(self, tables: list) -> Dict[str, Dict]:
        """获取数据库表统计信息"""
        if not os.path.exists(self.db_path):
            return {}

        # 使用内存缓存避免频繁查询
        cache_key = ",".join(sorted(tables))
        if cache_key in self._db_stats_cache:
            cache_time, stats = self._db_stats_cache[cache_key]
            # 5秒内直接返回缓存结果
            if time.time() - cache_time < 5:
                return stats

        stats = {}
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for table in tables:
                try:
                    # 获取行数
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]

                    # 获取最后更新时间（如果有last_modified字段）
                    max_modified = ""
                    try:
                        cursor.execute(f"SELECT MAX(last_modified) FROM {table}")
                        result = cursor.fetchone()
                        if result:
                            max_modified = str(result[0] or "")
                    except:
                        pass

                    # 获取最后更新ID（如果没有时间字段）
                    if not max_modified:
                        try:
                            cursor.execute(f"SELECT MAX(rowid) FROM {table}")
                            max_modified = str(cursor.fetchone()[0] or "")
                        except:
                            pass

                    stats[table] = {
                        "count": count,
                        "max_modified": max_modified
                    }
                except Exception as e:
                    logger.warning(f"Failed to get stats for {table}: {e}")

            conn.close()

            # 缓存结果
            self._db_stats_cache[cache_key] = (time.time(), stats)

        except Exception as e:
            logger.error(f"DB stats query failed: {e}")

        return stats

    def load(self, cache_key: str) -> Optional[Any]:
        """加载缓存数据"""
        cache_file = f"{self.cache_dir}/data_{cache_key}.pkl"

        if os.environ.get("DEV_MODE") == "1":
            logger.info("🔧 DEV_MODE: Skip cache")
            return None

        if os.path.exists(cache_file):
            try:
                with open(cache_file, "rb") as f:
                    data = pickle.load(f)
                logger.debug(f"Cache hit: {cache_key}")
                return data
            except Exception as e:
                logger.warning(f"Cache load failed: {e}")

        return None

    def save(self, cache_key: str, data: Any):
        """保存缓存数据"""
        cache_file = f"{self.cache_dir}/data_{cache_key}.pkl"
        try:
            with open(cache_file, "wb") as f:
                pickle.dump(data, f)
            logger.debug(f"Cache saved: {cache_key}")
        except Exception as e:
            logger.error(f"Cache save failed: {e}")

    def clear_old_caches(self, max_age_hours: int = 24):
        """清理过期缓存"""
        now = time.time()
        count = 0

        for filename in os.listdir(self.cache_dir):
            if not filename.startswith("data_") or not filename.endswith(".pkl"):
                continue

            filepath = os.path.join(self.cache_dir, filename)
            mtime = os.path.getmtime(filepath)
            age_hours = (now - mtime) / 3600

            if age_hours > max_age_hours:
                os.remove(filepath)
                count += 1

        if count > 0:
            logger.info(f"Cleared {count} old cache files")


# 便捷函数
def get_smart_cache_key(
    years: list = None,
    include_files: bool = True,
    db_path: str = "database/local_data.db"
) -> str:
    """
    为defect_explore6生成智能缓存key

    Usage:
        # 替换原来的_get_cache_key()
        cache_key = get_smart_cache_key(years=[2025, 2026])
    """
    manager = SmartCacheManager(db_path=db_path)

    sources = {
        "db_tables": ["octane_defects", "octane_manual_runs", "defect_features"],
        "years": years or [2025, 2026]
    }

    if include_files:
        # 可选：同时包含文件
        files = []
        for year in (years or [2025, 2026]):
            files.extend([
                f"defect/{year}_defect.json",
                f"defect/{year}_defect_master.json"
            ])
        sources["files"] = [f for f in files if os.path.exists(f)]

    return manager.get_cache_key(sources)
