#!/usr/bin/env python3
"""
Defect Explorer 生产服务器启动脚本
解决内网访问卡顿问题 - 使用 Waitress (Windows) 或 Gunicorn (Linux/Mac)
"""

import os
import sys
import platform
import subprocess
import socket
import importlib

# 配置
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 8051))
WORKERS = int(os.environ.get('WORKERS', 2))
THREADS = int(os.environ.get('THREADS', 4))
TIMEOUT = int(os.environ.get('TIMEOUT', 120))
APP_MODULE = os.environ.get('APP_MODULE', 'defect_explore')

def get_local_ip():
    """获取本机IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def print_banner(server_type):
    """打印启动信息"""
    local_ip = get_local_ip()
    print("\n" + "="*50)
    print("缺陷探索应用 - 生产服务器")
    print("="*50)
    print(f"服务器类型: {server_type}")
    print(f"工作进程: {WORKERS}")
    print(f"每进程线程: {THREADS}")
    print(f"超时时间: {TIMEOUT}秒")
    print("-"*50)
    print(f"本机访问: http://localhost:{PORT}")
    print(f"局域网访问: http://{local_ip}:{PORT}")
    print("="*50)
    print("团队成员可通过局域网IP访问应用")
    print(f"请确保防火墙允许{PORT}端口访问")
    print("="*50 + "\n")

def start_with_gunicorn():
    """使用 Gunicorn 启动 (Linux/Mac)"""
    print_banner("Gunicorn (生产级)")

    cmd = [
        "gunicorn",
        "-w", str(WORKERS),
        "-k", "gthread",
        "--threads", str(THREADS),
        "--timeout", str(TIMEOUT),
        "--bind", f"{HOST}:{PORT}",
        "--max-requests", "1000",
        "--max-requests-jitter", "100",
        "--access-logfile", "access.log",
        "--error-logfile", "error.log",
        "--capture-output",
        "--enable-stdio-inheritance",
        f"{APP_MODULE}:server"
    ]

    print(f"执行命令: {' '.join(cmd)}\n")
    subprocess.run(cmd)

def start_with_waitress():
    """使用 Waitress 启动 (Windows 推荐)"""
    try:
        import waitress
    except ImportError:
        print("正在安装 Waitress (Windows 生产服务器)...")
        subprocess.run([sys.executable, "-m", "pip", "install", "waitress", "-q"])
        import waitress

    print_banner("Waitress (Windows 生产级)")

    # 导入应用
    wsgi_app = importlib.import_module(APP_MODULE).server

    print(f"启动服务器 on {HOST}:{PORT}\n")

    # 使用 waitresse 提供多线程支持
    waitress.serve(
        wsgi_app,
        host=HOST,
        port=PORT,
        threads=THREADS * WORKERS,  # 总线程数
        channel_timeout=TIMEOUT,
        ident="DefectExplorer"
    )

def start_with_flask_debug():
    """开发模式启动 (不推荐用于内网共享)"""
    print("警告: 使用Flask开发服务器，仅适合本地调试")
    print("如需内网共享，请使用生产服务器\n")

    app = importlib.import_module(APP_MODULE).app
    app.run(
        debug=False,
        host=HOST,
        port=PORT,
        threaded=True
    )

def main():
    # macOS 必需：修复 fork() 与 Objective-C 运行时冲突
    os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

    system = platform.system()

    # 检查环境变量决定使用哪个服务器
    server_type = os.environ.get('SERVER_TYPE', 'auto')

    if server_type == 'flask':
        start_with_flask_debug()
    elif server_type == 'waitress':
        start_with_waitress()
    elif server_type == 'gunicorn':
        start_with_gunicorn()
    else:
        # 自动选择
        if system == 'Windows':
            start_with_waitress()
        else:
            # Mac/Linux 使用 Gunicorn
            try:
                subprocess.run(["gunicorn", "--version"], capture_output=True, check=True)
                start_with_gunicorn()
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("Gunicorn 未安装，尝试使用 Waitress...")
                start_with_waitress()

if __name__ == '__main__':
    main()
