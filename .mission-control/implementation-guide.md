# AI Analysis 项目 - Mission Control 实施指南

**创建日期**: 2026-03-18  
**版本**: 1.0  
**状态**: 就绪

---

## 📋 实施概览

本指南将帮助你在 Mission Control 中配置 AI Analysis 项目的多 Agent 协作团队。

### 实施范围
- ✅ 创建 Board 和项目上下文
- ✅ 配置 Lead Agent (项目经理)
- ✅ 配置 Dev Agent (开发工程师)
- ✅ 配置 QA Agent (测试工程师)
- ✅ 创建第一批优化任务
- ✅ 启动工作流

### 预计时间
- **配置时间**: 30-45 分钟
- **启动时间**: 15 分钟
- **总计**: 1 小时

---

## 🚀 快速启动

### 前置条件检查

```bash
# 1. 检查 Mission Control 是否运行
curl http://localhost:8000/health

# 2. 检查 OpenClaw Gateway 是否运行
curl http://localhost:18789/health

# 3. 检查 AI Analysis 项目是否存在
ls -la /Users/tonyorz/aianalysis/

# 4. 检查配置文件是否创建
ls -la /Users/tonyorz/aianalysis/.mission-control/
```

**预期结果**:
```
✅ Mission Control: 运行中
✅ OpenClaw Gateway: 运行中
✅ AI Analysis 项目: 存在
✅ 配置文件: 已创建
```

---

## 📝 Step-by-Step 实施步骤

### Step 1: 访问 Mission Control Web UI (2分钟)

1. **打开浏览器**
   ```
   URL: http://localhost:3000
   ```

2. **登录认证**
   - 认证模式: Local Token
   - Token: 见 `/Users/tonyorz/openclaw-docker/openclaw-mission-control/.env`
   - 字段: `LOCAL_AUTH_TOKEN`

3. **确认页面加载成功**
   - 应该看到 Dashboard 页面
   - 左侧菜单显示: Dashboard, Boards, Agents, Gateways

---

### Step 2: 创建或确认 Gateway (5分钟)

#### 方案 A: Gateway 已存在

1. 点击左侧菜单 **"Gateways"**
2. 查看是否已有 Gateway
3. 如果已存在 OpenClaw Gateway，跳到 Step 3

#### 方案 B: 创建新 Gateway

1. 点击 **"Add Gateway"** 按钮
2. 填写表单:
   ```
   Name: OpenClaw Docker
   Type: openclaw
   Description: OpenClaw Gateway for AI Analysis project
   WebSocket URL: ws://localhost:18789
   Auth Token: openclaw-local-token-2024
   ```
3. 点击 **"Create"**
4. 等待 Gateway 连接状态变为 **"Connected"**

---

### Step 3: 创建 Board (10分钟)

1. 点击左侧菜单 **"Boards"**
2. 点击 **"Add Board"** 按钮
3. 填写表单:
   ```
   Name: AI Analysis 项目优化
   Description: 
   持续优化 PreAnalysis 汽车测试数据分析平台
   - 代码质量提升和重构
   - Agent 系统性能优化
   - 测试覆盖率提升
   - 功能迭代和产品规划
   
   Gateway: [选择 "OpenClaw Docker"]
   ```
4. 点击 **"Create"**
5. 记录 **Board ID** (后续需要使用)

**预期结果**:
- Board 创建成功
- Board Lead Agent 自动创建
- Board 显示在列表中

---

### Step 4: 注入项目上下文 (10分钟)

#### 4.1 访问 Board Workspace

1. 点击刚创建的 Board "AI Analysis 项目优化"
2. 在 Board 详情页，找到 **"Workspace"** 标签
3. 你应该看到 Board Lead Agent 的工作空间

#### 4.2 上传 USER.md

1. 在 Workspace 中，找到 **USER.md** 文件
2. 点击 **"Edit"** 或 **"Upload"**
3. 上传或粘贴以下文件内容:
   ```
   文件位置: /Users/tonyorz/aianalysis/USER.md
   ```
4. 保存文件

#### 4.3 上传 TOOLS.md

1. 在 Workspace 中，创建 **TOOLS.md** 文件
2. 上传或粘贴以下文件内容:
   ```
   文件位置: /Users/tonyorz/aianalysis/TOOLS.md
   ```
3. 保存文件

#### 4.4 创建 MEMORY.md

1. 在 Workspace 中，创建 **MEMORY.md** 文件
2. 粘贴以下初始内容:

```markdown
# MEMORY.md - AI Analysis Board 记忆

## 项目启动 (2026-03-18)

### 项目背景
- PreAnalysis - 宝马 DTSV 团队的汽车测试数据分析平台
- 主要技术: Dash + Pandas + OpenAI SDK
- 当前状态: 生产环境运行

### 核心问题
1. Agent 系统需要优化 (intelligent_agent.py 6645行)
2. 测试覆盖率不足 (估计 < 30%)
3. 性能有优化空间

### 优化目标
- Phase 1: Agent 系统重构
- Phase 2: 测试覆盖率提升至 ≥ 80%
- Phase 3: 性能优化

### 团队成员
- Lead Agent: Alex 🎯 (项目经理)
- Dev Agent: Dev 💻 (开发工程师) - 待创建
- QA Agent: Quinn 🧪 (测试工程师) - 待创建

### 关键决策
1. 优先重构 Agent 系统
2. 保持功能不变的重构原则
3. 测试驱动的开发流程
```

3. 保存文件

**预期结果**:
- Board workspace 包含 USER.md, TOOLS.md, MEMORY.md
- Board Lead Agent 已有项目上下文

---

### Step 5: 配置 Lead Agent (5分钟)

Board Lead Agent 应该已自动创建，我们需要更新其配置。

1. 在 Board 详情页，找到 **"Agents"** 标签
2. 找到 Board Lead Agent (应该是列表中的第一个)
3. 点击 Agent 名称进入详情页
4. 找到 **"Identity"** 或 **"Settings"** 标签
5. 更新配置:

#### Identity Profile
```json
{
  "name": "Alex",
  "role": "Project Lead",
  "creature": "AI Coordinator",
  "vibe": "Organized, decisive, supportive",
  "emoji": "🎯"
}
```

#### Soul Template (SOUL.md)
1. 在 Agent workspace 中，找到 SOUL.md
2. 编辑并粘贴以下文件内容:
   ```
   文件位置: /Users/tonyorz/aianalysis/.mission-control/agents/lead-agent-config.md
   找到 "Soul 模板 (SOUL.md)" 部分的 markdown 内容
   ```
3. 保存文件

**预期结果**:
- Lead Agent 配置更新成功
- Lead Agent 有完整的 Soul 和 Identity

---

### Step 6: 创建 Dev Agent (5分钟)

1. 回到 Board 详情页
2. 点击 **"Add Agent"** 按钮
3. 填写表单:

#### 基本信息
```
Name: Dev
Role: Senior Software Engineer
Type: Worker Agent
Board: AI Analysis 项目优化
```

#### Identity Profile
```json
{
  "name": "Dev",
  "role": "Senior Software Engineer",
  "creature": "Code Craftsman",
  "vibe": "Precise, efficient, pragmatic",
  "emoji": "💻"
}
```

4. 点击 **"Create"**
5. 进入 Dev Agent 详情页

#### 上传 Soul Template
1. 在 Agent workspace 中，创建 SOUL.md
2. 编辑并粘贴以下文件内容:
   ```
   文件位置: /Users/tonyorz/aianalysis/.mission-control/agents/dev-agent-config.md
   找到 "Soul 模板 (SOUL.md)" 部分的 markdown 内容
   ```
3. 保存文件

#### 创建初始记忆
1. 在 Agent workspace 中，创建 MEMORY.md
2. 编辑并粘贴以下文件内容:
   ```
   文件位置: /Users/tonyorz/aianalysis/.mission-control/agents/dev-agent-config.md
   找到 "初始记忆 (MEMORY.md)" 部分的 markdown 内容
   ```
3. 保存文件

**预期结果**:
- Dev Agent 创建成功
- Dev Agent 有完整的 Soul 和 Memory
- Dev Agent 状态为 "Active"

---

### Step 7: 创建 QA Agent (5分钟)

1. 回到 Board 详情页
2. 点击 **"Add Agent"** 按钮
3. 填写表单:

#### 基本信息
```
Name: Quinn
Role: QA Engineer
Type: Worker Agent
Board: AI Analysis 项目优化
```

#### Identity Profile
```json
{
  "name": "Quinn",
  "role": "QA Engineer",
  "creature": "Quality Guardian",
  "vibe": "Thorough, skeptical, detail-oriented",
  "emoji": "🧪"
}
```

4. 点击 **"Create"**
5. 进入 QA Agent 详情页

#### 上传 Soul Template
1. 在 Agent workspace 中，创建 SOUL.md
2. 编辑并粘贴以下文件内容:
   ```
   文件位置: /Users/tonyorz/aianalysis/.mission-control/agents/qa-agent-config.md
   找到 "Soul 模板 (SOUL.md)" 部分的 markdown 内容
   ```
3. 保存文件

#### 创建初始记忆
1. 在 Agent workspace 中，创建 MEMORY.md
2. 编辑并粘贴以下文件内容:
   ```
   文件位置: /Users/tonyorz/aianalysis/.mission-control/agents/qa-agent-config.md
   找到 "初始记忆 (MEMORY.md)" 部分的 markdown 内容
   ```
3. 保存文件

**预期结果**:
- QA Agent 创建成功
- QA Agent 有完整的 Soul 和 Memory
- QA Agent 状态为 "Active"

---

### Step 8: 创建第一批任务 (5分钟)

#### 8.1 创建 TASK-001

1. 在 Board 详情页，点击 **"Tasks"** 标签
2. 点击 **"Add Task"** 按钮
3. 填写表单:

```
Title: 分析 intelligent_agent.py 结构
Type: Architecture Analysis
Priority: P0
Assignee: Dev Agent
Due Date: 2026-03-19

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
```

4. 点击 **"Create"**

#### 8.2 创建 TASK-002

1. 点击 **"Add Task"** 按钮
2. 填写表单:

```
Title: 建立测试基础设施
Type: Test Framework
Priority: P0
Assignee: QA Agent
Due Date: 2026-03-19

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
```

3. 点击 **"Create"**

**预期结果**:
- 2 个任务创建成功
- 任务已分配给相应的 Agent
- 任务状态为 "Todo"

---

### Step 9: 验证配置 (5分钟)

#### 9.1 检查 Board 配置

1. 进入 Board 详情页
2. 检查以下内容:
   - [ ] Board 名称正确
   - [ ] Gateway 已连接
   - [ ] Workspace 包含 USER.md, TOOLS.md, MEMORY.md
   - [ ] Agents 列表显示 3 个 Agent (Lead, Dev, QA)

#### 9.2 检查 Agent 状态

1. 进入 "Agents" 标签
2. 检查每个 Agent:
   - [ ] Lead Agent: Active, 有 Soul 和 Memory
   - [ ] Dev Agent: Active, 有 Soul 和 Memory
   - [ ] QA Agent: Active, 有 Soul 和 Memory

#### 9.3 检查任务状态

1. 进入 "Tasks" 标签
2. 检查:
   - [ ] TASK-001: 状态 "Todo", 分配给 Dev Agent
   - [ ] TASK-002: 状态 "Todo", 分配给 QA Agent

#### 9.4 测试 Agent 通信

1. 进入 Board Chat 或通过 API 测试
2. 发送测试消息:
   ```
   @lead 请汇报当前团队状态
   ```
3. 检查 Lead Agent 是否响应

**预期结果**:
- Board 配置完整
- 所有 Agent 状态正常
- 任务已分配
- Agent 可以通信

---

### Step 10: 启动工作流 (3分钟)

#### 10.1 激活任务

1. 进入 TASK-001 详情页
2. 点击 **"Start Task"** 或更改状态为 **"In Progress"**
3. 添加评论:
   ```
   @dev 请开始分析 intelligent_agent.py 的结构。
   参考: /Users/tonyorz/aianalysis/agent/core/intelligent_agent.py
   ```

#### 10.2 通知团队

在 Board Chat 中发送:
```
@all 
团队已组建完成，现在开始执行第一批优化任务。

当前任务:
1. TASK-001: 分析 Agent 结构 (@dev)
2. TASK-002: 建立测试基础 (@quinn)

请大家查看分配的任务，有问题及时沟通。
```

**预期结果**:
- 任务状态更新为 "In Progress"
- Agent 收到通知
- 工作流启动

---

## ✅ 验收检查清单

完成以上步骤后，请确认以下检查项:

### Board 配置
- [ ] Board 已创建: "AI Analysis 项目优化"
- [ ] Gateway 已连接: OpenClaw Docker
- [ ] Workspace 包含: USER.md, TOOLS.md, MEMORY.md

### Agent 配置
- [ ] Lead Agent 已创建并配置
  - [ ] Name: Alex 🎯
  - [ ] Soul 模板已上传
  - [ ] Memory 已初始化
  
- [ ] Dev Agent 已创建并配置
  - [ ] Name: Dev 💻
  - [ ] Soul 模板已上传
  - [ ] Memory 已初始化
  
- [ ] QA Agent 已创建并配置
  - [ ] Name: Quinn 🧪
  - [ ] Soul 模板已上传
  - [ ] Memory 已初始化

### 任务配置
- [ ] TASK-001 已创建并分配给 Dev Agent
- [ ] TASK-002 已创建并分配给 QA Agent

### 功能验证
- [ ] Agent 可以接收任务
- [ ] Agent 可以更新任务状态
- [ ] Agent 可以在 Board Chat 中通信
- [ ] Agent 可以访问 Board workspace

---

## 🔄 日常运维

### Daily Check (每日检查)

**Morning (9:00)**
1. 检查 Board 任务状态
2. 查看 overnight Agent 活动
3. 确认无阻塞问题

**Afternoon (15:00)**
1. 检查任务进度
2. 协调资源
3. 解决阻塞问题

**Evening (18:00)**
1. 总结今日完成情况
2. 规划明日工作
3. 更新项目状态

### Weekly Review (每周回顾)

**Friday (17:00)**
1. Lead Agent 生成周报
2. 评估团队效率
3. 调整优化策略
4. 规划下周任务

### Metrics to Track (关键指标)

```bash
# 任务完成率
Completed Tasks / Total Tasks

# 平均完成时间
Avg Completion Time (hours)

# 测试覆盖率
pytest --cov=agent --cov-report=term

# Agent 响应时间
Avg Response Time (seconds)

# 工具选择准确率
Correct Selections / Total Selections
```

---

## 🆘 故障排查

### 问题 1: Gateway 无法连接

**症状**: Gateway 状态显示 "Disconnected"

**排查步骤**:
```bash
# 1. 检查 OpenClaw 是否运行
curl http://localhost:18789/health

# 2. 检查 WebSocket 连接
wscat -c ws://localhost:18789

# 3. 检查认证 Token
# 确保 Token 正确: openclaw-local-token-2024

# 4. 重启 OpenClaw
cd /Users/tonyorz/openclaw-docker
./restart.sh
```

### 问题 2: Agent 无法接收任务

**症状**: 任务状态不更新，Agent 无响应

**排查步骤**:
```bash
# 1. 检查 Agent 状态
# 在 Mission Control UI 中查看 Agent 状态

# 2. 检查 Agent 日志
# 查看后台日志文件

# 3. 重启 Agent
# 在 UI 中暂停并重新激活 Agent

# 4. 检查 Board 配置
# 确保 Board 和 Agent 绑定正确
```

### 问题 3: 任务卡住不动

**症状**: 任务状态长时间无更新

**排查步骤**:
```bash
# 1. 检查阻塞原因
# 在任务评论中查看 Agent 的反馈

# 2. 手动干预
# 添加评论询问进度

# 3. 重新分配
# 如果 Agent 无响应，重新分配任务

# 4. 检查依赖
# 确保依赖任务已完成
```

### 问题 4: 测试覆盖率不达标

**症状**: pytest 覆盖率 < 80%

**排查步骤**:
```bash
# 1. 运行覆盖率测试
pytest tests/ --cov=agent --cov-report=html

# 2. 查看覆盖率报告
open htmlcov/index.html

# 3. 识别未覆盖代码
# 查看报告中标记为红色的代码

# 4. 创建测试任务
# 为未覆盖代码创建新的测试任务
```

---

## 📊 性能基准

### Agent 响应时间
| 操作 | 目标时间 | 告警阈值 |
|------|---------|---------|
| 意图检测 | < 200ms | > 500ms |
| 工具选择 | < 300ms | > 1s |
| 上下文生成 | < 1s | > 3s |
| 完整分析 | < 3s | > 5s |

### 测试覆盖率
| 模块 | 目标覆盖率 | 最低要求 |
|------|-----------|---------|
| agent/core/ | ≥ 85% | ≥ 70% |
| agent/tools/ | ≥ 80% | ≥ 65% |
| agent/memory/ | ≥ 75% | ≥ 60% |
| 整体 | ≥ 80% | ≥ 70% |

### 任务完成率
| 周期 | 目标 | 告警阈值 |
|------|------|---------|
| 每日 | > 80% | < 60% |
| 每周 | > 85% | < 70% |
| 每月 | > 90% | < 75% |

---

## 📚 参考文档

### 项目文档
- 项目 README: `/Users/tonyorz/aianalysis/README.md`
- Agent 文档: `/Users/tonyorz/aianalysis/CLAUDE.md`
- 配置文件: `/Users/tonyorz/aianalysis/config.py`

### Mission Control 文档
- Mission Control README: `/Users/tonyorz/openclaw-docker/openclaw-mission-control/README.md`
- API 文档: http://localhost:8000/docs
- Agent 配置: `/Users/tonyorz/openclaw-docker/openclaw-mission-control/backend/app/schemas/agents.py`

### 配置文件
- Board 配置: `/Users/tonyorz/aianalysis/.mission-control/`
- Agent 配置: `/Users/tonyorz/aianalysis/.mission-control/agents/`
- 任务定义: `/Users/tonyorz/aianalysis/.mission-control/tasks/`

---

## 🎉 完成确认

当你完成所有步骤后，请确认:

```bash
# 检查 Board
✅ Board "AI Analysis 项目优化" 存在
✅ Gateway 状态: Connected
✅ Workspace 文件: USER.md, TOOLS.md, MEMORY.md

# 检查 Agents
✅ Lead Agent (Alex 🎯): Active
✅ Dev Agent (Dev 💻): Active
✅ QA Agent (Quinn 🧪): Active

# 检查 Tasks
✅ TASK-001: 分析 intelligent_agent.py 结构
✅ TASK-002: 建立测试基础设施

# 检查文件
✅ /Users/tonyorz/aianalysis/USER.md 存在
✅ /Users/tonyorz/aianalysis/TOOLS.md 存在
✅ /Users/tonyorz/aianalysis/.mission-control/ 目录存在
```

**如果所有检查项都通过，恭喜你！配置成功完成！** 🎊

---

**创建人**: WorkBuddy  
**最后更新**: 2026-03-18  
**版本**: 1.0

**需要帮助？**
如果在实施过程中遇到问题，请查看故障排查章节或联系技术支持。
