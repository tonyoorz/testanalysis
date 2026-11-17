#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一缓存管理器
整合项目中的所有缓存系统，提供统一的管理接口
"""

import os
import sys
import shutil
import pickle
import json
import glob
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import time
from functools import lru_cache, wraps
import logging

logger = logging.getLogger(__name__)

class UnifiedCacheManager:
    """统一缓存管理器 - 管理项目中的所有缓存系统"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.cache_dir = self.project_root / "cache"
        self.pycache_dirs = []
        self.cache_stats = {}
        
        # 确保缓存目录存在
        self.cache_dir.mkdir(exist_ok=True)
        
        # 扫描所有__pycache__目录
        self._scan_pycache_dirs()
        
    def _scan_pycache_dirs(self):
        """扫描项目中的所有__pycache__目录"""
        self.pycache_dirs = list(self.project_root.rglob("__pycache__"))
        
    def clear_python_cache(self) -> Dict[str, Any]:
        """清除Python字节码缓存"""
        cleared_dirs = []
        total_size = 0
        
        for pycache_dir in self.pycache_dirs:
            if pycache_dir.exists():
                # 计算目录大小
                dir_size = sum(f.stat().st_size for f in pycache_dir.rglob('*') if f.is_file())
                total_size += dir_size
                
                # 删除目录
                shutil.rmtree(pycache_dir, ignore_errors=True)
                cleared_dirs.append(str(pycache_dir))
                
        return {
            'type': 'python_cache',
            'cleared_dirs': len(cleared_dirs),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'dirs': cleared_dirs
        }
        
    def clear_pickle_cache(self) -> Dict[str, Any]:
        """清除pickle缓存文件"""
        pickle_files = list(self.cache_dir.glob("*.pkl"))
        cleared_files = []
        total_size = 0
        
        for pkl_file in pickle_files:
            if pkl_file.exists():
                file_size = pkl_file.stat().st_size
                total_size += file_size
                pkl_file.unlink()
                cleared_files.append(str(pkl_file))
                
        return {
            'type': 'pickle_cache',
            'cleared_files': len(cleared_files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'files': cleared_files
        }
        
    def clear_json_cache(self) -> Dict[str, Any]:
        """清除JSON缓存文件"""
        json_cache_files = [
            self.project_root / "ticket_details_cache.json"
        ]
        
        cleared_files = []
        total_size = 0
        
        for json_file in json_cache_files:
            if json_file.exists():
                file_size = json_file.stat().st_size
                total_size += file_size
                json_file.unlink()
                cleared_files.append(str(json_file))
                
        return {
            'type': 'json_cache',
            'cleared_files': len(cleared_files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'files': cleared_files
        }
        
    def clear_lru_cache(self) -> Dict[str, Any]:
        """清除LRU缓存（通过重新导入模块）"""
        try:
            # 清除defect_explore中的LRU缓存
            if 'defect_explore' in sys.modules:
                defect_explore = sys.modules['defect_explore']
                if hasattr(defect_explore, '_cached_load_defect_data'):
                    defect_explore._cached_load_defect_data.cache_clear()
                if hasattr(defect_explore, '_cached_load_test_data'):
                    defect_explore._cached_load_test_data.cache_clear()
                    
            return {
                'type': 'lru_cache',
                'status': 'cleared',
                'modules': ['defect_explore']
            }
        except Exception as e:
            return {
                'type': 'lru_cache',
                'status': 'error',
                'error': str(e)
            }
            
    def clear_history_cache(self) -> Dict[str, Any]:
        """清除历史数据缓存"""
        try:
            # 清除data_processor中的历史缓存
            if 'data_processor' in sys.modules:
                data_processor = sys.modules['data_processor']
                if hasattr(data_processor, 'history_cache'):
                    data_processor.history_cache.clear()
                    
            return {
                'type': 'history_cache',
                'status': 'cleared'
            }
        except Exception as e:
            return {
                'type': 'history_cache',
                'status': 'error',
                'error': str(e)
            }
            
    def clear_inflow_outflow_cache(self) -> Dict[str, Any]:
        """清除inflow/outflow缓存"""
        try:
            # 尝试导入并清除inflow/outflow缓存
            if 'data_processor' in sys.modules:
                data_processor = sys.modules['data_processor']
                if hasattr(data_processor, 'clear_inflow_outflow_cache'):
                    data_processor.clear_inflow_outflow_cache()
                    
            return {
                'type': 'inflow_outflow_cache',
                'status': 'cleared'
            }
        except Exception as e:
            return {
                'type': 'inflow_outflow_cache',
                'status': 'error',
                'error': str(e)
            }
            
    def clear_cache_manager_cache(self) -> Dict[str, Any]:
        """清除CacheManager缓存"""
        try:
            # 尝试清除cache_manager中的缓存
            cache_manager_path = self.project_root / "scripts" / "performance" / "cache" / "cache_manager.py"
            if cache_manager_path.exists():
                sys.path.insert(0, str(cache_manager_path.parent))
                try:
                    import cache_manager
                    if hasattr(cache_manager, 'default_cache_manager'):
                        cache_manager.default_cache_manager.clear()
                except ImportError:
                    pass
                finally:
                    if str(cache_manager_path.parent) in sys.path:
                        sys.path.remove(str(cache_manager_path.parent))
                        
            return {
                'type': 'cache_manager',
                'status': 'cleared'
            }
        except Exception as e:
            return {
                'type': 'cache_manager',
                'status': 'error',
                'error': str(e)
            }
            
    def clear_empty_directories(self) -> Dict[str, Any]:
        """清除空目录"""
        cleared_dirs = []
        
        def remove_empty_dirs(path: Path):
            if not path.is_dir():
                return
                
            # 递归处理子目录
            for subdir in path.iterdir():
                if subdir.is_dir():
                    remove_empty_dirs(subdir)
                    
            # 检查当前目录是否为空
            try:
                if not any(path.iterdir()):
                    path.rmdir()
                    cleared_dirs.append(str(path))
            except OSError:
                pass  # 目录不为空或无权限删除
                
        # 从缓存目录开始清理
        if self.cache_dir.exists():
            remove_empty_dirs(self.cache_dir)
            
        return {
            'type': 'empty_directories',
            'cleared_dirs': len(cleared_dirs),
            'dirs': cleared_dirs
        }
        
    def get_cache_status(self) -> Dict[str, Any]:
        """获取缓存状态信息"""
        status = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'project_root': str(self.project_root),
            'cache_dir': str(self.cache_dir),
            'caches': {}
        }
        
        # Python缓存状态
        pycache_count = len(self.pycache_dirs)
        pycache_size = 0
        for pycache_dir in self.pycache_dirs:
            if pycache_dir.exists():
                pycache_size += sum(f.stat().st_size for f in pycache_dir.rglob('*') if f.is_file())
                
        status['caches']['python_cache'] = {
            'directories': pycache_count,
            'size_mb': round(pycache_size / (1024 * 1024), 2)
        }
        
        # Pickle缓存状态
        pickle_files = list(self.cache_dir.glob("*.pkl"))
        pickle_size = sum(f.stat().st_size for f in pickle_files if f.exists())
        
        status['caches']['pickle_cache'] = {
            'files': len(pickle_files),
            'size_mb': round(pickle_size / (1024 * 1024), 2)
        }
        
        # JSON缓存状态
        json_cache_file = self.project_root / "ticket_details_cache.json"
        json_size = json_cache_file.stat().st_size if json_cache_file.exists() else 0
        
        status['caches']['json_cache'] = {
            'files': 1 if json_cache_file.exists() else 0,
            'size_mb': round(json_size / (1024 * 1024), 2)
        }
        
        return status
        
    def clear_all_caches(self, verbose: bool = True) -> Dict[str, Any]:
        """清除所有缓存"""
        start_time = time.time()
        results = []
        
        if verbose:
            print("🧹 开始清除所有缓存...")
            
        # 1. 清除Python字节码缓存
        if verbose:
            print("  📁 清除Python字节码缓存...")
        results.append(self.clear_python_cache())
        
        # 2. 清除pickle缓存
        if verbose:
            print("  🥒 清除Pickle缓存文件...")
        results.append(self.clear_pickle_cache())
        
        # 3. 清除JSON缓存
        if verbose:
            print("  📄 清除JSON缓存文件...")
        results.append(self.clear_json_cache())
        
        # 4. 清除LRU缓存
        if verbose:
            print("  🔄 清除LRU缓存...")
        results.append(self.clear_lru_cache())
        
        # 5. 清除历史数据缓存
        if verbose:
            print("  📚 清除历史数据缓存...")
        results.append(self.clear_history_cache())
        
        # 6. 清除inflow/outflow缓存
        if verbose:
            print("  📊 清除Inflow/Outflow缓存...")
        results.append(self.clear_inflow_outflow_cache())
        
        # 7. 清除CacheManager缓存
        if verbose:
            print("  🗂️ 清除CacheManager缓存...")
        results.append(self.clear_cache_manager_cache())
        
        # 8. 清除空目录
        if verbose:
            print("  📂 清除空目录...")
        results.append(self.clear_empty_directories())
        
        end_time = time.time()
        
        summary = {
            'total_time_seconds': round(end_time - start_time, 2),
            'operations': len(results),
            'results': results,
            'summary': {
                'python_cache_dirs': sum(1 for r in results if r.get('type') == 'python_cache' and r.get('cleared_dirs', 0) > 0),
                'pickle_files': sum(r.get('cleared_files', 0) for r in results if r.get('type') == 'pickle_cache'),
                'json_files': sum(r.get('cleared_files', 0) for r in results if r.get('type') == 'json_cache'),
                'total_size_mb': sum(r.get('total_size_mb', 0) for r in results)
            }
        }
        
        if verbose:
            print(f"✅ 缓存清理完成！用时 {summary['total_time_seconds']} 秒")
            print(f"   清理了 {summary['summary']['total_size_mb']:.2f} MB 的缓存文件")
            
        return summary
        
    def optimize_cache_settings(self) -> Dict[str, Any]:
        """优化缓存设置"""
        optimizations = []
        
        # 检查缓存目录权限
        if not os.access(self.cache_dir, os.W_OK):
            optimizations.append({
                'type': 'permission_fix',
                'message': '缓存目录权限不足，尝试修复',
                'status': 'warning'
            })
            
        # 检查磁盘空间
        try:
            statvfs = os.statvfs(self.cache_dir)
            free_space_mb = (statvfs.f_frsize * statvfs.f_bavail) / (1024 * 1024)
            
            if free_space_mb < 100:  # 少于100MB
                optimizations.append({
                    'type': 'disk_space',
                    'message': f'磁盘空间不足：{free_space_mb:.1f}MB',
                    'status': 'warning'
                })
        except:
            pass
            
        # Windows兼容性检查
        if os.name == 'nt':  # Windows
            optimizations.append({
                'type': 'windows_compatibility',
                'message': '检测到Windows系统，已启用兼容模式',
                'status': 'info'
            })
            
        return {
            'optimizations': optimizations,
            'platform': os.name,
            'cache_dir_writable': os.access(self.cache_dir, os.W_OK)
        }

    # ========== 新增：版本控制缓存方法 ==========

    def _get_db_version(self, db_path: str = "database/local_data.db") -> str:
        """获取数据库版本（基于最后更新时间）"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 尝试从 octane_defects 获取最新更新时间
            cursor.execute("""
                SELECT MAX(fetched_at) FROM octane_defects
            """)
            result = cursor.fetchone()
            conn.close()

            if result and result[0]:
                return str(result[0])
        except Exception as e:
            logger.warning(f"Failed to get DB version: {e}")

        # 如果无法获取，使用文件修改时间
        try:
            db_file = Path(db_path)
            if db_file.exists():
                return str(db_file.stat().st_mtime)
        except:
            pass

        return "unknown"

    def _generate_cache_key(self, base_key: str, db_path: str = "database/local_data.db") -> str:
        """生成带版本的缓存键"""
        db_version = self._get_db_version(db_path)
        versioned_key = f"{base_key}_v{hashlib.md5(db_version.encode()).hexdigest()[:8]}"
        return versioned_key

    def get_cached_dataframe_versioned(self, base_key: str, db_path: str = "database/local_data.db") -> Optional[Any]:
        """
        获取带版本控制的 DataFrame 缓存
        如果数据库已更新，缓存自动失效
        """
        versioned_key = self._generate_cache_key(base_key, db_path)
        return self.get_cached_dataframe(versioned_key)

    def cache_dataframe_versioned(self, base_key: str, df: Any, db_path: str = "database/local_data.db", ttl: int = 3600):
        """
        缓存 DataFrame 带版本控制
        """
        versioned_key = self._generate_cache_key(base_key, db_path)
        self.cache_dataframe(versioned_key, df, ttl)

    def get_cached_dataframe(self, cache_key: str) -> Optional[Any]:
        """获取 DataFrame 缓存"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)

                # 检查是否过期
                if 'expires_at' in cached_data:
                    if time.time() > cached_data['expires_at']:
                        cache_file.unlink()
                        return None

                return cached_data.get('data')
        except Exception as e:
            logger.warning(f"Failed to load cache {cache_key}: {e}")

        return None

    def cache_dataframe(self, cache_key: str, df: Any, ttl: int = 3600):
        """缓存 DataFrame"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            cached_data = {
                'data': df,
                'created_at': time.time(),
                'expires_at': time.time() + ttl,
                'ttl': ttl
            }
            with open(cache_file, 'wb') as f:
                pickle.dump(cached_data, f)
        except Exception as e:
            logger.warning(f"Failed to cache {cache_key}: {e}")

    def get(self, key: str) -> Optional[Any]:
        """获取简单缓存值"""
        return self.get_cached_dataframe(key)

    def set(self, key: str, value: Any, ttl: int = 3600):
        """设置简单缓存值"""
        self.cache_dataframe(key, value, ttl)

    def invalidate_by_pattern(self, pattern: str) -> int:
        """根据模式删除缓存"""
        count = 0
        for cache_file in self.cache_dir.glob("*.pkl"):
            if pattern in cache_file.name:
                try:
                    cache_file.unlink()
                    count += 1
                except:
                    pass
        return count


def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='统一缓存管理器')
    parser.add_argument('--clear-all', action='store_true', help='清除所有缓存')
    parser.add_argument('--status', action='store_true', help='显示缓存状态')
    parser.add_argument('--optimize', action='store_true', help='优化缓存设置')
    parser.add_argument('--project-root', type=str, help='项目根目录路径')
    
    args = parser.parse_args()
    
    manager = UnifiedCacheManager(args.project_root)
    
    if args.clear_all:
        result = manager.clear_all_caches()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.status:
        status = manager.get_cache_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    elif args.optimize:
        optimizations = manager.optimize_cache_settings()
        print(json.dumps(optimizations, indent=2, ensure_ascii=False))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()