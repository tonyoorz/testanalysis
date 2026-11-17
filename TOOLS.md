# TOOLS.md - 开发环境工具指南

## 系统环境

### 项目路径
```
/Users/tonyorz/aianalysis/
├── agent/              # Agent 系统核心
├── defect/             # 缺陷数据 (47MB)
├── database/           # 数据库文件
├── cache/              # 缓存目录
└── *.py                # 各仪表板模块
```

### Python 环境
- Python 版本: 3.10+
- 虚拟环境: venv/
- 包管理: pip + requirements.txt

## 开发工具

### 代码质量工具
```bash
# 格式化代码
black agent/ --line-length 100

# 排序导入
isort agent/ --profile black

# 代码检查
flake8 agent/ --max-line-length 100

# 类型检查
mypy agent/ --ignore-missing-imports
```

### 测试工具
```bash
# 运行所有测试
pytest tests/ -v

# 运行覆盖率测试
pytest tests/ -v --cov=agent --cov-report=html

# 运行特定测试
pytest tests/test_intelligent_agent.py -v

# 运行 Agent 评测
python agent/evaluation/run_agent_eval_cases.py
```

### 性能分析
```bash
# Python 性能分析
python -m cProfile -o profile.stats defect_explore.py

# 内存分析
python -m memory_profiler agent/core/intelligent_agent.py
```

## 数据库工具

### SQLite 操作
```bash
# 连接主数据库
sqlite3 database/local_data.db

# 连接 Agent 记忆数据库
sqlite3 database/agent_memory.db

# 查询表结构
.tables
.schema defects

# 导出数据
sqlite3 database/local_data.db ".dump defects" > defects_backup.sql
```

### 常用查询
```sql
-- 查看缺陷总数
SELECT COUNT(*) FROM defects;

-- 查看项目分布
SELECT project, COUNT(*) as count 
FROM defects 
GROUP BY project 
ORDER BY count DESC 
LIMIT 10;

-- 查看 TopIssue
SELECT * FROM defects WHERE is_topissue = 1 LIMIT 10;
```

## API 工具

### DeepSeek API 测试
```bash
# 测试 API 连接
curl -X POST https://api.deepseek.com/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### Agent API 测试
```bash
# 测试 Agent 工具选择
python -c "
from agent.tools.smart_tool_selector import SmartToolSelector
selector = SmartToolSelector()
result = selector.select_tools('idcevo项目的风险如何？')
print(result)
"
```

## 日志和调试

### 日志配置
```python
# 在代码中添加日志
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agent.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### 查看日志
```bash
# 实时查看日志
tail -f logs/agent.log

# 搜索错误
grep ERROR logs/agent.log

# 查看最近100行
tail -n 100 logs/agent.log
```

## 部署工具

### 启动仪表板
```bash
# 启动缺陷探索仪表板 (端口 8051)
python defect_explore.py

# 启动趋势分析 (端口 8052)
python defect_trend.py

# 启动风险评估 (端口 8057)
python risk_analysis.py
```

### 后台运行
```bash
# 使用 nohup 后台运行
nohup python defect_explore.py > logs/explore.log 2>&1 &

# 查看进程
ps aux | grep python

# 停止进程
kill -9 <PID>
```

## 常用脚本

### 数据处理脚本
```bash
# 刷新缓存
python -c "
import os
import shutil
cache_dir = 'cache/'
if os.path.exists(cache_dir):
    shutil.rmtree(cache_dir)
    print('Cache cleared')
"

# 重新加载数据
python -c "
from data_processor import load_defect_data
data = load_defect_data()
print(f'Loaded {len(data)} defects')
"
```

### Agent 测试脚本
```bash
# 测试 Agent 完整流程
python -c "
from agent.core.intelligent_agent import IntelligentAgent

agent = IntelligentAgent()
result = agent.analyze('idcevo项目的风险如何？')
print(result)
"
```

## 性能监控

### 内存监控
```bash
# 监控 Python 进程内存
ps aux | grep python | awk '{print $6}'

# 使用 htop
htop -p $(pgrep -d',' python)
```

### CPU 监控
```bash
# 实时监控 CPU
top -pid $(pgrep python)

# 使用 htop
htop
```

## Git 工作流

### 提交代码
```bash
# 查看状态
git status

# 添加文件
git add agent/

# 提交
git commit -m "feat: optimize tool selection algorithm"

# 推送
git push origin main
```

### 分支管理
```bash
# 创建新分支
git checkout -b feature/agent-optimization

# 切换分支
git checkout main

# 合并分支
git merge feature/agent-optimization
```

## 依赖管理

### 更新依赖
```bash
# 查看过期依赖
pip list --outdated

# 更新特定依赖
pip install --upgrade pandas

# 导出当前依赖
pip freeze > requirements.txt
```

### 检查依赖冲突
```bash
# 检查依赖关系
pip check

# 查看依赖树
pip install pipdeptree
pipdeptree
```

## 故障排查

### 常见问题

#### 1. 内存不足
```bash
# 检查内存使用
free -h

# 清理缓存
python -c "import gc; gc.collect()"
```

#### 2. 端口被占用
```bash
# 查找占用端口的进程
lsof -i :8051

# 停止进程
kill -9 <PID>
```

#### 3. 数据库锁定
```bash
# 查找锁定进程
lsof database/local_data.db

# 解锁
rm database/local_data.db-journal
```

## Mission Control 集成

### API 端点
- Mission Control: http://localhost:3000
- Backend API: http://localhost:8000
- OpenClaw Gateway: http://localhost:18789

### 认证 Token
- Mission Control: 见 `/Users/tonyorz/openclaw-docker/openclaw-mission-control/.env`
- OpenClaw Gateway: `openclaw-local-token-2024`

---

_此文件记录开发环境工具和常用操作_
