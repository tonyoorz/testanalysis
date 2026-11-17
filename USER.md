# USER.md - Board Context

## 项目信息

- **项目名称**: PreAnalysis - 汽车测试数据分析平台
- **项目路径**: /Users/tonyorz/aianalysis
- **代码仓库**: 本地项目
- **主要技术栈**: 
  - Python 3.10+
  - Dash 2.13.0
  - Pandas 2.0+
  - Plotly 5.14+
  - OpenAI SDK (DeepSeek API)
  - SQLite + PostgreSQL
- **当前状态**: 生产环境运行中 (BMW DTSV 团队使用)

## 核心功能模块

### 数据分析仪表板
1. `defect_explore.py` (端口 8051) - 综合缺陷分析总览
2. `defect_matrix.py` (端口 8053) - 缺陷矩阵分析
3. `defect_trend.py` (端口 8052) - 缺陷趋势分析
4. `defect_map.py` (端口 8054) - 地理分布可视化
5. `defect_coverage.py` (端口 8056) - 缺陷覆盖率
6. `risk_analysis.py` (端口 8057) - 风险评估
7. `test_coverage.py` (端口 8055) - AIDA 测试覆盖率

### Agent 系统
- **位置**: `/agent/` 目录
- **核心文件**: 
  - `agent/core/intelligent_agent.py` (6645行) - 主Agent
  - `agent/memory/enhanced_memory_system.py` - 三层记忆
  - `agent/tools/smart_tool_selector.py` - 工具选择
  - `agent/core/smart_context_generator.py` - 智能上下文
  - `agent/core/explainable_agent.py` - 可解释性

## 业务背景

- **用户**: 宝马 DTSV (Development Test System Validation) 团队
- **认证**: BMW SSO
- **关键术语**:
  - Matrix 严重度矩阵: 1A(最高) → 4D(最低)
  - TopIssue: 高优先级缺陷
  - Long Runner: 超过30天未关闭的缺陷
  - AIDA: 核心客户功能，测试最小单元
  - Phase 状态流转: New → In Analysis → In Progress → Resolved → Closed

## 当前痛点

1. **测试覆盖率**: 单元测试较少，缺少集成测试
2. **性能优化**: 大数据集处理有优化空间 (47MB defect数据)
3. **代码规范**: 需要统一代码风格和类型检查
4. **文档完善**: 部分模块缺少详细文档
5. **Agent 优化**: 
   - intelligent_agent.py 过于庞大 (6645行)
   - 工具选择准确率待提升
   - 上下文生成效率可优化

## 工作规范

### 代码规范
- Python: Black + isort + flake8 + mypy
- 最大行长度: 100
- 命名: snake_case

### 提交规范
- feat: 新功能
- fix: 修复bug
- refactor: 重构
- test: 测试相关
- docs: 文档
- perf: 性能优化

### Agent 落位规则
> 所有 Agent 相关代码必须放在 `/agent/` 目录内
> - `agent/core` - 编排与主流程
> - `agent/tools` - 工具策略
> - `agent/memory` - 记忆
> - `agent/evaluation` - 评测

### 性能基准
| 操作 | 当前性能 | 目标性能 |
|------|---------|---------|
| 数据加载 (47MB) | ~5s | < 2s |
| Agent 响应 | ~3s | < 1.5s |
| 图表渲染 | ~1s | < 0.5s |
| 工具选择准确率 | ~75% | > 90% |

## 开发环境

### 环境配置
```bash
# 虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest tests/ -v --cov=agent

# 代码格式化
black agent/
isort agent/

# 类型检查
mypy agent/
```

### 数据库
- 主数据库: `database/local_data.db`
- Agent记忆: `database/agent_memory.db`
- 工具性能: `database/tool_performance.db`

### API 配置
- DeepSeek API: 配置在 `config.py` 中
- 基础URL: https://api.deepseek.com
- 模型: deepseek-chat

## 优化重点

### Phase 1: Agent 系统重构 (当前重点)
1. **模块拆分**
   - 从 intelligent_agent.py 提取 tool_executor.py
   - 提取 context_manager.py
   - 提取 memory_manager.py

2. **性能优化**
   - 优化工具选择算法
   - 改进上下文生成效率
   - 实现增量记忆更新

3. **测试覆盖**
   - 单元测试: agent/core/
   - 集成测试: 工具调用流程
   - 性能测试: 关键路径

### Phase 2: 数据处理优化
- 分块加载大数据集
- 实现智能缓存
- SQL查询优化

### Phase 3: 功能增强
- 多轮对话理解
- 意图检测优化
- 混合检索改进

## 联系方式

- **项目经理**: [待定]
- **技术负责人**: Tony
- **用户代表**: BMW DTSV 团队

---

_此文件由 Mission Control 管理，记录项目上下文信息_
