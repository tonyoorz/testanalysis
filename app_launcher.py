#!/usr/bin/env python3
"""
应用启动器
统一管理和启动所有子应用
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
from config import SUBMODULES_CONFIG, APP_CONFIG
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AppLauncher:
    """应用启动器类"""
    
    def __init__(self):
        self.processes = {}
        self.main_app_port = APP_CONFIG['main_app']['port']
        self.main_app_url = f"http://localhost:{self.main_app_port}"
        
    def start_main_app(self):
        """启动主应用"""
        logger.info("启动主应用 defect_explore.py...")
        try:
            cmd = [sys.executable, "defect_explore.py"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes['main'] = process
            logger.info(f"主应用已启动，端口: {self.main_app_port}")
            return True
        except Exception as e:
            logger.error(f"主应用启动失败: {e}")
            return False
    
    def start_submodule(self, module_name):
        """启动子模块"""
        if module_name not in SUBMODULES_CONFIG:
            logger.error(f"未知的子模块: {module_name}")
            return False
            
        config = SUBMODULES_CONFIG[module_name]
        module_path = config['module_path']
        port = config['port']
        
        if not os.path.exists(module_path):
            logger.warning(f"子模块文件不存在: {module_path}")
            return False
            
        logger.info(f"启动子模块 {module_name} (端口: {port})...")
        try:
            cmd = [sys.executable, module_path]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes[module_name] = process
            logger.info(f"子模块 {module_name} 已启动")
            return True
        except Exception as e:
            logger.error(f"子模块 {module_name} 启动失败: {e}")
            return False
    
    def start_all_submodules(self):
        """启动所有子模块"""
        logger.info("启动所有子模块...")
        success_count = 0
        
        for module_name in SUBMODULES_CONFIG.keys():
            if self.start_submodule(module_name):
                success_count += 1
                time.sleep(1)  # 错开启动时间
        
        logger.info(f"成功启动 {success_count}/{len(SUBMODULES_CONFIG)} 个子模块")
        return success_count
    
    def stop_all(self):
        """停止所有应用"""
        logger.info("停止所有应用...")
        
        for name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"已停止 {name}")
            except subprocess.TimeoutExpired:
                process.kill()
                logger.warning(f"强制终止 {name}")
            except Exception as e:
                logger.error(f"停止 {name} 时出错: {e}")
        
        self.processes.clear()
    
    def check_port_available(self, port):
        """检查端口是否可用"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def wait_for_app_ready(self, port, timeout=30):
        """等待应用就绪"""
        import requests
        url = f"http://localhost:{port}"
        
        for _ in range(timeout):
            try:
                response = requests.get(url, timeout=1)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        
        return False
    
    def open_browser(self, url=None):
        """打开浏览器"""
        if url is None:
            url = self.main_app_url
        
        logger.info(f"打开浏览器: {url}")
        try:
            webbrowser.open(url)
        except Exception as e:
            logger.error(f"无法打开浏览器: {e}")
    
    def show_status(self):
        """显示应用状态"""
        print("\n" + "="*60)
        print("应用状态")
        print("="*60)
        
        # 检查主应用
        main_status = "运行中" if self.check_port_available(self.main_app_port) == False else "未运行"
        print(f"主应用 (端口 {self.main_app_port}): {main_status}")
        
        # 检查子模块
        for module_name, config in SUBMODULES_CONFIG.items():
            port = config['port']
            status = "运行中" if self.check_port_available(port) == False else "未运行"
            print(f"{module_name} (端口 {port}): {status}")
        
        print("="*60)
        print(f"主应用访问地址: {self.main_app_url}")
        print("="*60)
    
    def create_desktop_shortcut(self):
        """创建桌面快捷方式"""
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "DTSV数据分析平台.lnk")
            target = sys.executable
            wDir = os.getcwd()
            arguments = "app_launcher.py --quick-start"
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.Arguments = arguments
            shortcut.WorkingDirectory = wDir
            shortcut.IconLocation = target
            shortcut.save()
            
            logger.info(f"桌面快捷方式已创建: {path}")
        except ImportError:
            logger.warning("无法创建桌面快捷方式（需要安装 pywin32 和 winshell）")
        except Exception as e:
            logger.error(f"创建桌面快捷方式失败: {e}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='DTSV数据分析平台启动器')
    parser.add_argument('--main-only', action='store_true', help='仅启动主应用')
    parser.add_argument('--with-submodules', action='store_true', help='启动主应用和所有子模块')
    parser.add_argument('--status', action='store_true', help='显示应用状态')
    parser.add_argument('--stop', action='store_true', help='停止所有应用')
    parser.add_argument('--create-shortcut', action='store_true', help='创建桌面快捷方式')
    parser.add_argument('--quick-start', action='store_true', help='快速启动（主应用+打开浏览器）')
    parser.add_argument('--module', type=str, help='启动指定的子模块')
    
    args = parser.parse_args()
    
    launcher = AppLauncher()
    
    try:
        if args.status:
            launcher.show_status()
            
        elif args.stop:
            launcher.stop_all()
            
        elif args.create_shortcut:
            launcher.create_desktop_shortcut()
            
        elif args.module:
            launcher.start_submodule(args.module)
            
        elif args.main_only or args.quick_start:
            if launcher.start_main_app():
                if args.quick_start:
                    logger.info("等待主应用就绪...")
                    if launcher.wait_for_app_ready(launcher.main_app_port):
                        launcher.open_browser()
                    else:
                        logger.warning("主应用启动超时，请手动访问")
                
                try:
                    # 等待用户中断
                    input("\n按 Enter 键停止应用...\n")
                except KeyboardInterrupt:
                    pass
                finally:
                    launcher.stop_all()
                    
        elif args.with_submodules:
            logger.info("启动完整平台（主应用 + 所有子模块）...")
            if launcher.start_main_app():
                launcher.start_all_submodules()
                
                launcher.show_status()
                
                # 等待主应用就绪后打开浏览器
                if launcher.wait_for_app_ready(launcher.main_app_port):
                    launcher.open_browser()
                
                try:
                    input("\n按 Enter 键停止所有应用...\n")
                except KeyboardInterrupt:
                    pass
                finally:
                    launcher.stop_all()
                    
        else:
            # 默认行为：显示菜单
            print("\nDTSV数据分析平台启动器")
            print("=" * 40)
            print("1. 启动主应用")
            print("2. 启动完整平台（主应用+子模块）")
            print("3. 显示应用状态")
            print("4. 创建桌面快捷方式")
            print("0. 退出")
            
            choice = input("\n请选择操作 (0-4): ").strip()
            
            if choice == '1':
                subprocess.run([sys.executable, __file__, '--quick-start'])
            elif choice == '2':
                subprocess.run([sys.executable, __file__, '--with-submodules'])
            elif choice == '3':
                launcher.show_status()
            elif choice == '4':
                launcher.create_desktop_shortcut()
            elif choice == '0':
                print("退出")
            else:
                print("无效选择")
                
    except KeyboardInterrupt:
        logger.info("用户中断")
        launcher.stop_all()
    except Exception as e:
        logger.error(f"启动器出错: {e}")
        launcher.stop_all()

if __name__ == "__main__":
    main() 