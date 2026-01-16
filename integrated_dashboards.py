import multiprocessing
import subprocess
import os
import time
import sys
import webbrowser
from threading import Timer

# 看板映射：文件名 -> (端口, 说明)
dashboards = {
    "risk_analysis.py": (8057, "AIDA 覆盖率与缺陷数量分析"),
    "test_coverage.py": (8055, "测试覆盖率看板"),
    "defect_map.py": (8054, "团队缺陷发现地理分布图"),
    "defect_matrix.py": (8053, "缺陷矩阵分布看板"),
    "defectEDA.py": (8051, "缺陷管理系统 2025"),
    "defect_trend.py": (8052, "缺陷趋势分析看板"),
    "data_dashboard.py": (8070, "数据看板")
}

def is_port_in_use(port):
    """检查端口是否被占用"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def run_dashboard(script_file):
    """启动单个Dash看板"""
    port = dashboards[script_file][0]
    
    # 如果端口已被占用，输出警告但仍尝试启动
    if is_port_in_use(port):
        print(f"警告: 端口 {port} 已被占用，启动 {script_file} 可能会失败")
    
    print(f"正在启动 {script_file} 在端口 {port}...")
    
    # 使用子进程运行Python脚本
    process = subprocess.Popen([sys.executable, script_file], 
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              text=True)
    
    # 等待几秒钟确认脚本启动成功
    time.sleep(2)
    
    if process.poll() is not None:
        # 进程已退出，读取错误信息
        _, stderr = process.communicate()
        print(f"错误: 启动 {script_file} 失败: {stderr}")
        return None
    
    return process

def open_browser(port):
    """在浏览器中打开看板URL"""
    webbrowser.open_new(f"http://localhost:{port}")

def main():
    """主函数，启动所有看板"""
    print("正在启动所有Dash看板...\n")
    
    # 创建一个主页HTML文件
    with open('dashboard_index.html', 'w', encoding='utf-8') as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>缺陷分析看板系统</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
                h1 { color: #333; text-align: center; }
                .dashboard-container { 
                    display: flex; 
                    flex-wrap: wrap; 
                    justify-content: center;
                    gap: 20px;
                    margin-top: 30px;
                }
                .dashboard-card {
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    padding: 20px;
                    width: 300px;
                    text-align: center;
                    transition: transform 0.3s;
                }
                .dashboard-card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
                }
                .dashboard-card h2 {
                    color: #2c3e50;
                    margin-top: 0;
                }
                .dashboard-card p {
                    color: #7f8c8d;
                    margin-bottom: 20px;
                }
                .dashboard-link {
                    display: inline-block;
                    background-color: #3498db;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    text-decoration: none;
                    font-weight: bold;
                }
                .dashboard-link:hover {
                    background-color: #2980b9;
                }
            </style>
        </head>
        <body>
            <h1>缺陷分析看板系统</h1>
            <div class="dashboard-container">
        """)
        
        # 为每个看板添加卡片
        for script, (port, description) in dashboards.items():
            f.write(f"""
                <div class="dashboard-card">
                    <h2>{description}</h2>
                    <p>端口: {port}</p>
                    <a href="http://localhost:{port}" target="_blank" class="dashboard-link">打开看板</a>
                </div>
            """)
        
        f.write("""
            </div>
        </body>
        </html>
        """)
    
    # 启动所有看板进程
    processes = []
    for script_file in dashboards.keys():
        if os.path.exists(script_file):
            process = run_dashboard(script_file)
            if process:
                processes.append(process)
        else:
            print(f"错误: 找不到脚本文件 {script_file}")
    
    # 等待2秒后打开主页
    time.sleep(2)
    webbrowser.open_new('file://' + os.path.realpath('dashboard_index.html'))
    
    print("\n所有看板已启动。按 Ctrl+C 停止所有服务。")
    
    try:
        # 保持主进程运行，直到用户中断
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n停止所有看板...")
        # 终止所有子进程
        for process in processes:
            process.terminate()
        print("所有看板已停止。")

if __name__ == "__main__":
    # 设置启动方法为spawn以兼容Windows
    if sys.platform.startswith('win'):
        multiprocessing.set_start_method('spawn')
    main() 