#!/usr/bin/env python3
"""
优化的缺陷探索应用部署脚本
支持多进程、缓存、局域网访问等特性
"""

import os
import sys
import argparse
from multiprocessing import cpu_count
import subprocess
import signal
import time

def check_dependencies():
    """检查依赖项"""
    required_packages = [
        'dash', 'pandas', 'plotly', 'gunicorn'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"缺少以下依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install " + " ".join(missing_packages))
        return False
    
    return True

def preload_data():
    """预加载数据"""
    print("预加载数据中...")
    try:
        from scripts.performance.loaders.data_loader_optimized import preload_defect_data
        thread = preload_defect_data()
        thread.join()  # 等待预加载完成
        print("数据预加载完成")
    except ImportError:
        print("优化数据加载器不可用，跳过预加载")

def create_gunicorn_config():
    """创建Gunicorn配置文件"""
    config_content = f"""
# Gunicorn配置文件
import multiprocessing

# 服务器套接字
bind = "0.0.0.0:8051"
backlog = 2048

# 工作进程
workers = {min(cpu_count(), 4)}
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 60
max_requests = 1000
max_requests_jitter = 100

# 安全
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# 调试
preload_app = True
reload = False

# 日志
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程命名
proc_name = "defect_explore"

# 钩子函数
def on_starting(server):
    print("正在启动缺陷探索应用...")

def when_ready(server):
    print(f"缺陷探索应用已启动，监听端口: {{server.address}}")

def on_exit(server):
    print("缺陷探索应用已停止")
"""
    
    # 创建logs目录
    os.makedirs("logs", exist_ok=True)
    
    with open("gunicorn.conf.py", "w", encoding="utf-8") as f:
        f.write(config_content)

def create_wsgi_app():
    """创建WSGI应用入口"""
    wsgi_content = '''
import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量
os.environ.setdefault('FLASK_ENV', 'production')

# 导入Dash应用
from defect_explore import app

# WSGI应用
application = app.server

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8051, debug=False)
'''
    
    with open("wsgi.py", "w", encoding="utf-8") as f:
        f.write(wsgi_content)

def start_production_server():
    """启动生产服务器"""
    print("启动生产模式服务器...")
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 创建配置文件
    create_gunicorn_config()
    create_wsgi_app()
    
    # 预加载数据
    preload_data()
    
    # 启动Gunicorn
    cmd = [
        "gunicorn",
        "--config", "gunicorn.conf.py",
        "wsgi:application"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("服务器已停止")
    except subprocess.CalledProcessError as e:
        print(f"服务器启动失败: {e}")
        return False
    
    return True

def start_development_server():
    """启动开发模式服务器"""
    print("启动开发模式服务器...")
    
    # 设置环境变量
    os.environ['DEBUG'] = 'True'
    os.environ['ENABLE_CACHE'] = 'False'
    
    # 预加载数据
    preload_data()
    
    # 直接运行应用
    from defect_explore import app
    app.run_server(
        host="0.0.0.0",
        port=8051,
        debug=True,
        threaded=True
    )

def stop_server():
    """停止服务器"""
    print("正在停止服务器...")
    
    # 查找并终止进程
    try:
        result = subprocess.run(
            ["pgrep", "-f", "defect_explore"],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"已停止进程: {pid}")
                except ProcessLookupError:
                    pass
        else:
            print("未找到运行中的服务器进程")
    
    except FileNotFoundError:
        print("无法查找进程（pgrep命令不可用）")
        print("请手动停止服务器进程")

def show_network_info():
    """显示网络访问信息"""
    import socket
    
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("\n" + "="*50)
    print("缺陷探索应用网络访问信息")
    print("="*50)
    print(f"本机访问: http://localhost:8051")
    print(f"本机访问: http://127.0.0.1:8051")
    print(f"局域网访问: http://{local_ip}:8051")
    print(f"主机名访问: http://{hostname}:8051")
    print("="*50)
    print("请确保防火墙允许8051端口访问")
    print("团队成员可通过局域网IP访问应用")
    print("="*50 + "\n")

def main():
    parser = argparse.ArgumentParser(description="缺陷探索应用部署工具")
    parser.add_argument(
        "command",
        choices=["start", "dev", "stop", "info"],
        help="执行命令: start(生产模式), dev(开发模式), stop(停止服务), info(显示网络信息)"
    )
    
    args = parser.parse_args()
    
    if args.command == "start":
        show_network_info()
        start_production_server()
    elif args.command == "dev":
        show_network_info()
        start_development_server()
    elif args.command == "stop":
        stop_server()
    elif args.command == "info":
        show_network_info()

if __name__ == "__main__":
    main() 