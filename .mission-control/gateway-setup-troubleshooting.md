# Gateway 配对问题解决方案

**问题**: Mission Control 中创建 Gateway 时显示 "No gateways found"

**原因**: Gateway 需要先在 Mission Control UI 中创建，然后通过 OpenClaw 的配对流程连接。

---

## 解决方案：通过 UI 创建 Gateway

### Step 1: 在 Mission Control UI 中创建 Gateway

1. **访问 Mission Control**: http://localhost:3000
2. **进入 Gateways 页面** (左侧菜单)
3. **点击 "Add Gateway"**
4. **填写表单**:
   ```
   Name: OpenClaw Docker
   URL: ws://192.168.0.200:18789
   Workspace Root: /Users/tonyorz/openclaw-docker/workspace
   Description: OpenClaw Gateway for AI Analysis project optimization
   Token: openclaw-local-token-2024
   ```

5. **点击 "Create"**

### Step 2: 配对 Gateway

创建 Gateway 后，Mission Control 会显示一个配对码或配对链接。

**选项 A: 如果显示配对码**
1. 复制配对码
2. 在 OpenClaw 中输入配对码完成配对

**选项 B: 如果显示配对链接**
1. 点击配对链接
2. 在 OpenClaw 中确认配对

**选项 C: 自动配对**
- Gateway 可能会自动配对（如果 token 正确）

### Step 3: 验证 Gateway 连接

在 Mission Control UI 中:
1. 查看 Gateway 状态
2. 状态应该显示为 **"Connected"** 或 **"Active"**

---

## 替代方案：使用现有的 Main Agent

如果 Gateway 配对困难，可以先使用现有的 OpenClaw Main Agent 进行优化：

### 方案 A: 直接在 OpenClaw 中工作

1. **访问 OpenClaw Gateway UI**:
   ```
   http://localhost:18789
   ```

2. **使用 Main Agent** 进行优化工作

3. **手动执行任务**:
   - 查看任务清单: `/Users/tonyorz/aianalysis/.mission-control/tasks/initial-tasks.md`
   - 按照 Dev Agent 和 QA Agent 的配置指南工作

### 方案 B: 使用 Mission Control Board（不需要 Gateway）

1. **在 Mission Control 中创建 Board**
   - 不绑定 Gateway
   - 使用 Board 作为任务管理工具

2. **手动创建任务**
   - 参考: `/Users/tonyorz/aianalysis/.mission-control/tasks/initial-tasks.md`

3. **手动分配和跟踪任务**

---

## 快速启动建议

**推荐方案**: 先使用 Mission Control 的本地 Board 功能

1. **创建 Board** (不需要 Gateway):
   ```
   Name: AI Analysis 项目优化
   Description: 持续优化 PreAnalysis 汽车测试数据分析平台
   Gateway: 留空或选择 "None"
   ```

2. **创建任务**:
   - TASK-001: 分析 intelligent_agent.py 结构
   - TASK-002: 建立测试基础设施

3. **手动执行**:
   - 按照 Dev Agent 和 QA Agent 的配置文件中的指南工作
   - 使用 `/Users/tonyorz/aianalysis/.mission-control/agents/` 中的详细说明

4. **后续集成 Gateway**:
   - 等 Mission Control 和 Gateway 配对问题解决后
   - 再将 Board 绑定到 Gateway

---

## 需要帮助？

### 查看日志
```bash
# Mission Control 后端日志
docker logs openclaw-mission-control-backend-1

# OpenClaw Gateway 日志
docker logs openclaw-gateway
```

### 检查连接
```bash
# 测试 OpenClaw 连接
curl http://192.168.0.200:18789/health

# 测试 WebSocket
wscat -c ws://192.168.0.200:18789
```

### 查看文档
- Mission Control 文档: `/Users/tonyorz/openclaw-docker/openclaw-mission-control/docs/`
- Gateway 配置: `/Users/tonyorz/openclaw-docker/openclaw-mission-control/backend/app/schemas/gateways.py`

---

**建议**: 先创建一个不绑定 Gateway 的 Board，立即开始优化工作。Gateway 集成可以后续完成。
