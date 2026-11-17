#!/usr/bin/env python3
"""
统一应用启动器
集成所有优化功能，替代所有其他启动脚本
"""

import os
import sys
import time
import signal
import argparse
import threading
import atexit
from pathlib import Path

# 设置优化环境变量
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['DASH_SILENCE_ROUTES_LOGGING'] = 'True'

class AppLauncher:
    """统一应用启动器"""
    
    def __init__(self):
        self.start_time = time.time()
        self.data_manager = None
        self.monitoring = False
        
    def is_reloader_process(self):
        """检查是否为reloader进程"""
        return os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    
    def show_banner(self, mode="standard"):
        """显示启动横幅"""
        mode_info = {
            'standard': ('📊 标准模式', '使用现有应用，无特殊优化'),
            'optimized': ('⚡ 优化模式', '启用缓存和预加载优化'),
            'test': ('🧪 测试模式', '运行性能测试'),
            'monitor': ('📈 监控模式', '启动时监控性能指标')
        }
        
        title, desc = mode_info.get(mode, ('🚀 未知模式', ''))
        
        print("\n" + "=" * 60)
        print(f"🎯 缺陷分析系统启动器 - {title}")
        print("=" * 60)
        print(f"📝 {desc}")
        print(f"🕐 启动时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60 + "\n")
    
    def check_environment(self):
        """检查运行环境"""
        print("🔍 检查运行环境...")
        
        # 检查Python版本
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        print(f"   • Python版本: {python_version}")
        
        # 检查数据文件
        defect_files = list(Path('defect').glob('*.json')) if Path('defect').exists() else []
        history_files = list(Path('history').glob('*_history.json')) if Path('history').exists() else []
        
        print(f"   • 缺陷数据文件: {len(defect_files)} 个")
        print(f"   • 历史数据文件: {len(history_files)} 个")
        
        if len(defect_files) == 0:
            print("   ⚠️  警告: 未找到缺陷数据文件，部分功能可能不可用")
            
        return len(defect_files) > 0
    
    def initialize_optimization(self):
        """初始化优化组件"""
        if not self.is_reloader_process():
            print("⏩ Reloader进程，跳过优化初始化")
            return False
            
        print("⚡ 初始化性能优化组件...")
        
        try:
            # 导入数据管理器
            from scripts.performance.data_manager import data_manager, get_cache_info
            self.data_manager = data_manager
            
            # 检查缓存状态
            cache_info = get_cache_info()
            cached_keys = cache_info.get('cached_keys', [])
            
            if cached_keys:
                print(f"   • 发现缓存数据: {len(cached_keys)} 个")
            else:
                print("   • 准备首次加载数据")
                
            return True
            
        except Exception as e:
            print(f"   ❌ 优化组件初始化失败: {e}")
            return False
    
    def start_background_preload(self):
        """启动后台预加载"""
        if not self.is_reloader_process():
            return
            
        print("🔄 启动后台数据预加载...")
        
        try:
            from scripts.performance.data_manager import preload_all_data
            
            preload_thread = preload_all_data()
            if preload_thread:
                print("   • 后台预加载线程已启动")
            else:
                print("   • 预加载启动失败")
                
        except Exception as e:
            print(f"   ❌ 后台预加载失败: {e}")
    
    def run_performance_test(self):
        """运行性能测试"""
        print("🧪 开始性能测试...")
        
        try:
            # 导入测试模块
            from scripts.performance.performance_test import run_all_tests
            results = run_all_tests()
            
            if results:
                print("\n🎯 测试完成！")
            else:
                print("\n⚠️  部分测试失败")
            
        except Exception as e:
            print(f"❌ 性能测试失败: {e}")
    
    def start_monitoring(self):
        """启动性能监控"""
        self.monitoring = True
        print("📈 启动性能监控...")
        
        def monitor_resources():
            import psutil
            
            while self.monitoring:
                try:
                    process = psutil.Process()
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    cpu_percent = process.cpu_percent()
                    
                    elapsed = time.time() - self.start_time
                    print(f"[{elapsed:6.1f}s] 内存: {memory_mb:.1f}MB, CPU: {cpu_percent:.1f}%")
                    
                    time.sleep(10)  # 每10秒监控一次
                    
                except Exception:
                    break
        
        monitor_thread = threading.Thread(target=monitor_resources, daemon=True)
        monitor_thread.start()
    
    def launch_app(self, app_type='explore'):
        """启动应用"""
        print("🌐 启动Web应用...")
        
        try:
            # 根据类型选择应用
            if app_type == 'optimized':
                print("   • 使用优化版应用")
                try:
                    from app_launcher_optimized import app
                except ImportError:
                    print("   ⚠️  优化版应用不可用，切换到标准版")
                    app_type = 'explore'
            
            if app_type == 'explore':
                print("   • 使用标准探索应用")
                import defect_explore as app_module
                app = app_module.app
            
            # 启动配置
            host = '0.0.0.0'
            port = int(os.environ.get('PORT', 8051))
            debug = True
            
            print(f"   • 服务地址: http://localhost:{port}")
            print(f"   • 调试模式: {debug}")
            print("\n🎯 应用启动中...")
            print("-" * 50)
            
            # 启动应用
            app.run_server(
                debug=debug,
                host=host,
                port=port,
                dev_tools_hot_reload=True,
                dev_tools_silence_routes_logging=True,
                use_reloader=True,
                threaded=True
            )
            
        except KeyboardInterrupt:
            print("\n🛑 用户中断")
            self.cleanup()
            
        except Exception as e:
            print(f"❌ 应用启动失败: {e}")
            self.cleanup(1)
    
    def cleanup(self, exit_code=0):
        """清理资源"""
        self.monitoring = False
        print("\n🧹 清理资源...")
        
        try:
            if self.data_manager:
                self.data_manager.clear_cache()
                print("   • 数据缓存已清理")
        except:
            pass
        
        try:
            from data_processor import history_cache
            history_cache.clear()
            print("   • 历史缓存已清理")
        except:
            pass
        
        total_time = time.time() - self.start_time
        print(f"✅ 运行时间: {total_time:.1f}秒，再见！")
        sys.exit(exit_code)

def signal_handler(signum, frame):
    """信号处理器"""
    print(f"\n🛑 收到信号 {signum}")
    launcher.cleanup()

def main():
    """主函数"""
    global launcher
    launcher = AppLauncher()
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(launcher.cleanup)
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='缺陷分析系统启动器')
    parser.add_argument('--mode', choices=['standard', 'optimized', 'test', 'monitor'], 
                       default='standard', help='启动模式')
    parser.add_argument('--app', choices=['explore', 'optimized'], 
                       default='explore', help='应用类型')
    parser.add_argument('--port', type=int, default=8051, help='端口号')
    parser.add_argument('--no-cache', action='store_true', help='禁用缓存优化')
    
    args = parser.parse_args()
    
    # 设置环境变量
    os.environ['PORT'] = str(args.port)
    
    try:
        # 显示启动信息
        launcher.show_banner(args.mode)
        
        # 检查环境
        if not launcher.check_environment():
            response = input("数据文件缺失，是否继续？(y/N): ")
            if response.lower() != 'y':
                print("启动取消")
                return
        
        # 根据模式执行不同操作
        if args.mode == 'test':
            launcher.run_performance_test()
            return
        
        if args.mode in ['optimized', 'monitor']:
            launcher.initialize_optimization()
            
        if args.mode == 'optimized' and not args.no_cache:
            launcher.start_background_preload()
            
        if args.mode == 'monitor':
            launcher.start_monitoring()
        
        # 启动应用
        prep_time = time.time() - launcher.start_time
        print(f"⏱️  启动准备完成，耗时: {prep_time:.2f}秒\n")
        
        launcher.launch_app(args.app)
        
    except KeyboardInterrupt:
        print("\n🛑 启动被用户中断")
        launcher.cleanup()
        
    except Exception as e:
        print(f"\n❌ 启动过程中发生错误: {e}")
        launcher.cleanup(1)

if __name__ == '__main__':
    main()