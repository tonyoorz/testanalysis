"""
数据库迁移配置文件
用于控制数据读取模式：文件模式 vs 数据库模式
"""

import os

# ==================== 核心配置开关 ====================

# 数据读取模式
# - "file": 只从文件读取（原有方式，最安全）
# - "db_first": 优先从数据库读取，失败时降级到文件
# - "db_only": 只从数据库读取（完全迁移后）
DATA_READ_MODE = os.environ.get("DATA_READ_MODE", "db_only")

# 数据写入模式（下载器使用）
# - "file": 只写文件
# - "both": 同时写文件和数据库（推荐迁移期间使用）
# - "db_only": 只写数据库
DATA_WRITE_MODE = os.environ.get("DATA_WRITE_MODE", "db_only")

# ==================== 数据库配置 ====================

# 数据库路径
DB_PATH = os.environ.get("OCTANE_DB_PATH", os.path.join("database", "local_data.db"))

# 数据库后端
# - "sqlite": 默认本地 SQLite
# - "postgres": 读取走 PostgreSQL（需配置 POSTGRES_URL）
DB_BACKEND = os.environ.get("DB_BACKEND", "sqlite").strip().lower()

# PostgreSQL（双写/灰度）配置
ENABLE_PG_WRITE = os.environ.get("ENABLE_PG_WRITE", "false").lower() in ("true", "1", "yes")
PG_URL = os.environ.get("POSTGRES_URL", "")
PG_SCHEMA = os.environ.get("PG_SCHEMA", "public")

# 默认团队
DEFAULT_TEAM = os.environ.get("OCTANE_TEAM", "DTSV_China")

# ==================== 表名配置 ====================

# 使用新表结构还是旧表结构
# - "legacy": 使用旧表（octane_payloads, octane_defect_histories）
# - "optimized": 使用新表（octane_defects, octane_manual_runs, octane_history_events）
DB_SCHEMA_VERSION = os.environ.get("DB_SCHEMA_VERSION", "optimized")

# 表名映射
TABLE_NAMES = {
    "legacy": {
        "defects": "octane_payloads",
        "manual_runs": "octane_payloads",
        "histories": "octane_defect_histories",
    },
    "optimized": {
        "defects": "octane_defects",
        "manual_runs": "octane_manual_runs",
        "histories": "octane_defect_histories",
        "history_events": "octane_history_events",
        "aida_mappings": "aida_mappings",
    }
}

# ==================== 性能配置 ====================

# 是否启用缓存
ENABLE_CACHE = os.environ.get("ENABLE_CACHE", "true").lower() in ("true", "1", "yes")

# 缓存大小
CACHE_SIZE = int(os.environ.get("CACHE_SIZE", "2000"))

# 是否启用历史数据预加载
ENABLE_HISTORY_PRELOAD = os.environ.get("ENABLE_HISTORY_PRELOAD", "true").lower() in ("true", "1", "yes")

# 预加载线程数
PRELOAD_WORKERS = int(os.environ.get("PRELOAD_WORKERS", "10"))

# ==================== 迁移配置 ====================

# 是否启用迁移验证
ENABLE_MIGRATION_VALIDATION = os.environ.get("ENABLE_MIGRATION_VALIDATION", "true").lower() in ("true", "1", "yes")

# 批量插入大小
BATCH_INSERT_SIZE = int(os.environ.get("BATCH_INSERT_SIZE", "1000"))

# ==================== 调试配置 ====================

# 是否打印详细日志
DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() in ("true", "1", "yes")

# 是否记录性能指标
ENABLE_PERFORMANCE_LOGGING = os.environ.get("ENABLE_PERFORMANCE_LOGGING", "false").lower() in ("true", "1", "yes")

# ==================== 辅助函数 ====================

def get_table_name(data_type: str) -> str:
    """获取表名"""
    return TABLE_NAMES[DB_SCHEMA_VERSION].get(data_type)

def is_file_mode() -> bool:
    """是否为文件模式"""
    return DATA_READ_MODE == "file"

def is_db_first_mode() -> bool:
    """是否为数据库优先模式"""
    return DATA_READ_MODE == "db_first"

def is_db_only_mode() -> bool:
    """是否为纯数据库模式"""
    return DATA_READ_MODE == "db_only"

def should_write_to_file() -> bool:
    """是否应该写入文件"""
    return DATA_WRITE_MODE in ("file", "both")

def should_write_to_db() -> bool:
    """是否应该写入数据库"""
    return DATA_WRITE_MODE in ("both", "db_only")

def is_postgres_backend() -> bool:
    """是否启用 PostgreSQL 读取后端"""
    return DB_BACKEND == "postgres"

def is_using_optimized_schema() -> bool:
    """是否使用优化的表结构"""
    return DB_SCHEMA_VERSION == "optimized"

def print_config():
    """打印当前配置"""
    print("=" * 60)
    print("数据库迁移配置")
    print("=" * 60)
    print(f"数据读取模式: {DATA_READ_MODE}")
    print(f"数据写入模式: {DATA_WRITE_MODE}")
    print(f"数据库架构版本: {DB_SCHEMA_VERSION}")
    print(f"数据库后端: {DB_BACKEND}")
    print(f"数据库路径: {DB_PATH}")
    print(f"启用PostgreSQL双写: {ENABLE_PG_WRITE}")
    print(f"PostgreSQL Schema: {PG_SCHEMA}")
    print(f"默认团队: {DEFAULT_TEAM}")
    print(f"启用缓存: {ENABLE_CACHE}")
    print(f"缓存大小: {CACHE_SIZE}")
    print(f"启用历史预加载: {ENABLE_HISTORY_PRELOAD}")
    print(f"调试模式: {DEBUG_MODE}")
    print("=" * 60)

# ==================== 快速切换函数 ====================

def switch_to_file_mode():
    """切换到文件模式（回滚）"""
    global DATA_READ_MODE
    DATA_READ_MODE = "file"
    print("✅ 已切换到文件模式")

def switch_to_db_first_mode():
    """切换到数据库优先模式"""
    global DATA_READ_MODE
    DATA_READ_MODE = "db_first"
    print("✅ 已切换到数据库优先模式")

def switch_to_db_only_mode():
    """切换到纯数据库模式"""
    global DATA_READ_MODE
    DATA_READ_MODE = "db_only"
    print("✅ 已切换到纯数据库模式")

# ==================== 启动时打印配置 ====================

if __name__ == "__main__":
    print_config()
