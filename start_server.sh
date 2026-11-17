#!/bin/bash

# Defect Explorer 生产服务器启动脚本
# 解决内网访问卡顿问题 - 使用 Gunicorn 替代 Flask 开发服务器

cd "$(dirname "$0")"

# 配置
export HOST=0.0.0.0
export PORT=8051
export DEBUG=False
export WORKERS=2
export THREADS=4
export TIMEOUT=120
export APP_MODULE=${APP_MODULE:-defect_explore}

# macOS 必需：修复 fork() 与 Objective-C 运行时冲突
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

echo "=========================================="
echo "Defect Explorer 生产服务器"
echo "=========================================="
echo "服务器类型: Gunicorn (生产级)"
echo "工作进程: $WORKERS"
echo "每进程线程: $THREADS"
echo "超时时间: $TIMEOUT秒"
echo "=========================================="

# 检查是否是 macOS (Darwin)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS 使用 gthread worker
    WORKER_CLASS=gthread
else
    # Linux 使用 gthread worker
    WORKER_CLASS=gthread
fi

# 获取本机IP
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)
echo "本机IP: $LOCAL_IP"
echo "访问地址: http://$LOCAL_IP:$PORT"
echo "=========================================="
echo ""

# 启动 Gunicorn
# 关键参数说明:
# -w: 工作进程数 (建议: CPU核心数 * 2 + 1)
# -k: worker类型 (gthread支持异步)
# --threads: 每进程线程数
# --timeout: 请求超时时间
# --preload: 预加载应用减少内存占用
# --max-requests: 每进程处理多少请求后重启(防内存泄漏)
# --access-logfile: 访问日志
# --error-logfile: 错误日志

gunicorn -w $WORKERS \
    -k $WORKER_CLASS \
    --threads $THREADS \
    --timeout $TIMEOUT \
    --bind $HOST:$PORT \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile access.log \
    --error-logfile error.log \
    --capture-output \
    --enable-stdio-inheritance \
    "${APP_MODULE}:server"
