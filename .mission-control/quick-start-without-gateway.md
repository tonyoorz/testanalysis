# 快速启动 - 无需 Gateway 配对

**创建日期**: 2026-03-18  
**状态**: 就绪

---

## 🎯 当前情况

- ✅ Mission Control 运行正常
- ✅ OpenClaw Gateway 运行正常
- ⚠️ Gateway 配对需要额外步骤
- ✅ 所有配置文件已创建完成

---

## 🚀 立即开始工作方案

**建议**: 先创建 Board，不绑定 Gateway，立即开始优化工作。

### Step 1: 创建 Board（无需 Gateway）(5分钟)

1. **访问 Mission Control**: http://localhost:3000

2. **进入 Boards 页面** (左侧菜单)

3. **点击 "Add Board"**

4. **填写表单**:
   ```
   Name: AI Analysis 项目优化
   Description: 
   持续优化 PreAnalysis 汽车测试数据分析平台
   - Agent 系统重构
   - 测试覆盖率提升
   - 性能优化
   
   Gateway: 留空或选择 "None" (如果可选)
   ```

5. **点击 "Create"**

6. **记录 Board ID** (后续需要)

---

### Step 2: 手动创建第一批任务 (10分钟)

在 Board 详情页，进入 "Tasks" 标签，创建以下任务：

#### TASK-001: 分析 intelligent_agent.py 结构

```
Title: 分析 intelligent_agent.py 结构
Priority: P0
Type: Architecture Analysis
Description:
分析 agent/core/intelligent_agent.py (6645行) 的代码结构，提出拆分重构方案。

目标:
1. 理解当前代码结构
2. 识别可拆分的模块
3. 提出拆分方案
4. 评估工作量和风险

验收标准:
- [ ] 提交结构分析文档
- [ ] 包含详细的拆分方案
- [ ] 工作量评估合理
- [ ] 风险识别完整

相关文件:
- /Users/tonyorz/aianalysis/agent/core/intelligent_agent.py
```

#### TASK-002: 建立测试基础设施

```
Title: 建立测试基础设施
Priority: P0
Type: Test Framework
Description:
建立完整的测试基础设施，包括测试目录、配置、数据和模板。

目标:
1. 配置 pytest 测试框架
2. 创建测试目录结构
3. 准备测试数据
4. 编写测试模板

验收标准:
- [ ] 测试目录结构完整
- [ ] pytest 配置正确
- [ ] 测试数据可用
- [ ] 测试模板清晰

参考文档:
- /Users/tonyorz/aianalysis/.mission-control/agents/qa-agent-config.md
```

---

### Step 3: 立即开始执行任务 (现在)

你现在就可以开始执行这些任务！

#### 执行 TASK-001 (Dev 角色)

**参考**: `/Users/tonyorz/aianalysis/.mission-control/agents/dev-agent-config.md`

1. **阅读 intelligent_agent.py**:
   ```bash
   cd /Users/tonyorz/aianalysis
   # 使用你喜欢的编辑器打开
   code agent/core/intelligent_agent.py
   ```

2. **分析结构**:
   - 统计行数和函数数量
   - 识别主要类和方法
   - 识别依赖关系

3. **编写分析报告**:
   创建文件: `agent/core/REFACTORING_ANALYSIS.md`
   
   参考模板:
   ```markdown
   # intelligent_agent.py 结构分析报告
   
   ## 概览
   - 总行数: 6645
   - 主要类: IntelligentAgent
   - 依赖模块: ...
   
   ## 当前结构
   [描述当前代码组织]
   
   ## 问题识别
   1. 问题1
   2. 问题2
   
   ## 重构方案
   ### 方案1: 提取 AgentBase
   [详细说明]
   
   ### 方案2: 提取 ToolExecutor
   [详细说明]
   
   ## 工作量评估
   - AgentBase: 1天
   - ToolExecutor: 2天
   - ContextManager: 1.5天
   - MemoryManager: 1天
   总计: 5.5天
   
   ## 风险分析
   - 风险1: [描述] - [缓解措施]
   - 风险2: [描述] - [缓解措施]
   ```

#### 执行 TASK-002 (QA 角色)

**参考**: `/Users/tonyorz/aianalysis/.mission-control/agents/qa-agent-config.md`

1. **创建测试目录**:
   ```bash
   cd /Users/tonyorz/aianalysis
   mkdir -p tests/{unit,integration,e2e,performance,fixtures}
   mkdir -p tests/unit/agent/{core,tools,memory}
   ```

2. **创建 pytest.ini**:
   ```ini
   [pytest]
   testpaths = tests
   python_files = test_*.py
   python_classes = Test*
   python_functions = test_*
   addopts = 
       -v 
       --strict-markers
       --tb=short
       --cov=agent
       --cov-report=html
       --cov-report=term-missing
   markers =
       unit: Unit tests
       integration: Integration tests
       e2e: End-to-end tests
       slow: Slow running tests
   ```

3. **准备测试数据**:
   ```bash
   # 从大数据集中提取样本
   python3 << EOF
   import pandas as pd
   import json
   
   # 读取大数据集
   data = pd.read_json("defect/2025_defect.json", nrows=100)
   
   # 保存为测试数据
   data.to_json("tests/fixtures/sample_defects.json", orient='records', indent=2)
   
   print(f"Created test data with {len(data)} samples")
   EOF
   ```

4. **编写第一个测试**:
   创建文件: `tests/unit/agent/core/test_intelligent_agent.py`
   
   ```python
   import pytest
   import pandas as pd
   from agent.core.intelligent_agent import IntelligentAgent
   
   @pytest.fixture
   def agent():
       """创建测试用的 Agent 实例"""
       return IntelligentAgent()
   
   @pytest.fixture
   def sample_data():
       """加载测试数据"""
       return pd.read_json("tests/fixtures/sample_defects.json")
   
   class TestIntelligentAgent:
       """IntelligentAgent 单元测试"""
       
       def test_agent_initialization(self, agent):
           """测试 Agent 初始化"""
           assert agent is not None
   ```

5. **运行测试**:
   ```bash
   pytest tests/unit/agent/core/test_intelligent_agent.py -v
   ```

---

### Step 4: 更新任务状态

完成每个任务后，在 Mission Control Board 中:
1. 进入任务详情页
2. 更新状态为 "In Progress" → "Review" → "Done"
3. 添加评论记录工作成果

---

## 📋 完整任务清单

参考: `/Users/tonyorz/aianalysis/.mission-control/tasks/initial-tasks.md`

### Week 1 任务
- [ ] TASK-001: 分析 intelligent_agent.py 结构 (0.5天)
- [ ] TASK-002: 建立测试基础设施 (0.5天)
- [ ] TASK-003: 提取 AgentBase 基类 (1天)
- [ ] TASK-004: 编写 intelligent_agent.py 测试 (1天)

### Week 2 任务
- [ ] TASK-005: 提取 ToolExecutor (2天)
- [ ] TASK-006: 优化工具选择算法 (1.5天)

---

## 🎯 成功标准

### Phase 1 完成 (Week 1)
- ✅ intelligent_agent.py 结构分析完成
- ✅ 测试基础设施建立
- ✅ AgentBase 基类提取完成
- ✅ 测试覆盖率 > 40%

### Phase 2 完成 (Week 2)
- ✅ ToolExecutor 提取完成
- ✅ intelligent_agent.py 行数减少 > 50%
- ✅ 测试覆盖率 > 60%
- ✅ 工具选择准确率提升

---

## 💡 工作提示

### Dev Agent 工作指南
详细指南: `/Users/tonyorz/aianalysis/.mission-control/agents/dev-agent-config.md`

关键要点:
- 保持功能不变的重构原则
- 每个模块独立测试
- 代码审查后再合并

### QA Agent 工作指南
详细指南: `/Users/tonyorz/aianalysis/.mission-control/agents/qa-agent-config.md`

关键要点:
- 测试覆盖率目标是 ≥ 80%
- 编写测试优先级: Core > Tools > Memory
- 性能测试很重要

---

## 🔄 后续 Gateway 集成

Gateway 配对问题解决后:
1. 在 Mission Control 中创建 Gateway
2. 将现有 Board 绑定到 Gateway
3. 配置 Agent 自动化
4. 启动自动化工作流

参考: `/Users/tonyorz/aianalysis/.mission-control/gateway-setup-troubleshooting.md`

---

## 📚 相关文档

### 配置文件
- 项目上下文: `/Users/tonyorz/aianalysis/USER.md`
- 开发工具: `/Users/tonyorz/aianalysis/TOOLS.md`

### Agent 配置
- Lead Agent: `/Users/tonyorz/aianalysis/.mission-control/agents/lead-agent-config.md`
- Dev Agent: `/Users/tonyorz/aianalysis/.mission-control/agents/dev-agent-config.md`
- QA Agent: `/Users/tonyorz/aianalysis/.mission-control/agents/qa-agent-config.md`

### 任务定义
- 初始任务: `/Users/tonyorz/aianalysis/.mission-control/tasks/initial-tasks.md`

---

**开始工作吧！** 🚀

现在就可以开始执行 TASK-001 和 TASK-002，无需等待 Gateway 配对。
