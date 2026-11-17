"""
数据库工具模块

提供数据库连接池、重试机制、事务管理等工具

Author: AI Assistant
Date: 2026-02-17
"""

import sqlite3
import time
import logging
import threading
from contextlib import contextmanager
from functools import wraps
from typing import Optional, Callable, Any, Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)


# ========== 重试装饰器 ==========

def with_db_retry(max_retries: int = 3, retry_delay: float = 0.1, backoff: float = 2.0):
    """
    数据库操作重试装饰器

    自动重试以下错误：
    - OperationalError (如 database is locked)
    - 其他临时性错误

    Args:
        max_retries: 最大重试次数
        retry_delay: 初始重试延迟（秒）
        backoff: 退避系数，每次重试延迟乘以该系数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = retry_delay
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except sqlite3.OperationalError as e:
                    last_exception = e
                    error_msg = str(e).lower()

                    # 检查是否是可重试的错误
                    if any(err in error_msg for err in ['locked', 'busy', 'timeout']):
                        if attempt < max_retries - 1:
                            logger.warning(f"Database locked, retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
                            time.sleep(delay)
                            delay *= backoff
                            continue
                    # 不可重试的错误，直接抛出
                    raise
                except sqlite3.DatabaseError as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Database error, retrying: {e}")
                        time.sleep(delay)
                        delay *= backoff
                        continue
                    raise

            # 重试次数用尽
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


# ========== 连接池管理器 ==========

class SQLiteConnectionPool:
    """
    SQLite 连接池

    特点：
    - 线程安全的连接复用
    - 自动管理连接生命周期
    - 支持 WAL 模式配置
    """

    def __init__(self, db_path: str, max_connections: int = 5, timeout: float = 30.0):
        self.db_path = db_path
        self.max_connections = max_connections
        self.timeout = timeout
        self._pool: List[sqlite3.Connection] = []
        self._in_use: set = set()
        self._lock = threading.Lock()
        self._local = threading.local()

        # 确保数据库目录存在
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    def _create_connection(self) -> sqlite3.Connection:
        """创建新连接并配置"""
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=self.timeout
        )

        # 启用 WAL 模式（更好的并发性能）
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=-64000")  # 64MB 缓存
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("PRAGMA mmap_size=268435456")  # 256MB 内存映射

        return conn

    def get_connection(self) -> sqlite3.Connection:
        """获取连接（优先从线程本地存储获取）"""
        # 检查线程本地存储
        if hasattr(self._local, 'connection') and self._local.connection:
            return self._local.connection

        with self._lock:
            # 尝试从池中获取可用连接
            while self._pool:
                conn = self._pool.pop()
                if conn not in self._in_use:
                    try:
                        # 验证连接是否有效
                        conn.execute("SELECT 1")
                        self._in_use.add(conn)
                        self._local.connection = conn
                        return conn
                    except sqlite3.Error:
                        # 连接无效，关闭它
                        try:
                            conn.close()
                        except:
                            pass
                        continue

            # 池已空，创建新连接（如果未达到上限）
            if len(self._in_use) < self.max_connections:
                conn = self._create_connection()
                self._in_use.add(conn)
                self._local.connection = conn
                return conn

        # 连接数已达上限，等待一段时间后重试
        time.sleep(0.1)
        return self.get_connection()

    def release_connection(self, conn: sqlite3.Connection):
        """释放连接回池中"""
        with self._lock:
            if conn in self._in_use:
                self._in_use.remove(conn)
                # 验证连接仍然有效
                try:
                    conn.execute("SELECT 1")
                    self._pool.append(conn)
                except sqlite3.Error:
                    # 连接无效，关闭它
                    try:
                        conn.close()
                    except:
                        pass

        # 清除线程本地存储
        if hasattr(self._local, 'connection') and self._local.connection == conn:
            self._local.connection = None

    def close_all(self):
        """关闭所有连接"""
        with self._lock:
            for conn in list(self._in_use):
                try:
                    conn.close()
                except:
                    pass
            self._in_use.clear()

            for conn in self._pool:
                try:
                    conn.close()
                except:
                    pass
            self._pool.clear()

    @contextmanager
    def connection(self):
        """上下文管理器，自动获取和释放连接"""
        conn = None
        try:
            conn = self.get_connection()
            yield conn
        finally:
            if conn:
                self.release_connection(conn)


# ========== 数据库操作封装 ==========

class DatabaseHelper:
    """数据库操作辅助类，封装常用操作"""

    def __init__(self, db_path: str, pool: Optional[SQLiteConnectionPool] = None):
        self.db_path = db_path
        self.pool = pool or SQLiteConnectionPool(db_path)

    @with_db_retry(max_retries=3)
    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """执行 SQL（带重试）"""
        with self.pool.connection() as conn:
            return conn.execute(sql, params)

    @with_db_retry(max_retries=3)
    def executemany(self, sql: str, params_list: List[tuple]):
        """批量执行 SQL（带重试）"""
        with self.pool.connection() as conn:
            conn.executemany(sql, params_list)
            conn.commit()

    @with_db_retry(max_retries=3)
    def fetchone(self, sql: str, params: tuple = ()) -> Optional[tuple]:
        """查询单行"""
        with self.pool.connection() as conn:
            return conn.execute(sql, params).fetchone()

    @with_db_retry(max_retries=3)
    def fetchall(self, sql: str, params: tuple = ()) -> List[tuple]:
        """查询所有行"""
        with self.pool.connection() as conn:
            return conn.execute(sql, params).fetchall()

    @with_db_retry(max_retries=3)
    def fetchdf(self, sql: str, params: tuple = ()) -> 'pd.DataFrame':
        """查询为 DataFrame"""
        import pandas as pd
        with self.pool.connection() as conn:
            return pd.read_sql_query(sql, conn, params=params)

    @with_db_retry(max_retries=3)
    def transaction(self):
        """事务上下文管理器"""
        return self.pool.connection()

    def close(self):
        """关闭连接池"""
        self.pool.close_all()


# ========== 便捷函数 ==========

def get_db_connection(db_path: str, timeout: float = 30.0) -> sqlite3.Connection:
    """
    获取配置好的数据库连接

    Args:
        db_path: 数据库文件路径
        timeout: 锁等待超时时间（秒）

    Returns:
        配置好的连接对象
    """
    conn = sqlite3.connect(
        db_path,
        check_same_thread=False,
        timeout=timeout
    )

    # 启用 WAL 模式
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-64000")

    return conn


@contextmanager
def db_transaction(db_path: str):
    """事务上下文管理器"""
    conn = get_db_connection(db_path)
    try:
        conn.execute("BEGIN")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ========== 单例模式 ==========

_pool_instances: Dict[str, SQLiteConnectionPool] = {}
_pool_lock = threading.Lock()


def get_connection_pool(db_path: str, max_connections: int = 5) -> SQLiteConnectionPool:
    """获取连接池（单例）"""
    global _pool_instances

    with _pool_lock:
        if db_path not in _pool_instances:
            _pool_instances[db_path] = SQLiteConnectionPool(
                db_path,
                max_connections=max_connections
            )
        return _pool_instances[db_path]


def close_all_pools():
    """关闭所有连接池"""
    global _pool_instances

    with _pool_lock:
        for pool in _pool_instances.values():
            pool.close_all()
        _pool_instances.clear()


# ========== 测试 ==========

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # 测试重试装饰器
    @with_db_retry(max_retries=3, retry_delay=0.1)
    def test_operation():
        print("Operation executed")
        return True

    print("Testing retry decorator:")
    test_operation()

    # 测试连接池
    print("\nTesting connection pool:")
    pool = SQLiteConnectionPool("test_pool.db")

    with pool.connection() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("INSERT OR REPLACE INTO test (id, name) VALUES (1, 'test')")
        conn.commit()

    with pool.connection() as conn:
        result = conn.execute("SELECT * FROM test").fetchall()
        print(f"Query result: {result}")

    pool.close_all()

    # 清理
    import os
    os.remove("test_pool.db")
    os.remove("test_pool.db-shm")
    os.remove("test_pool.db-wal")

    print("\nAll tests passed!")
