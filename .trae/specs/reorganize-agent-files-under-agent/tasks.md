# Tasks
- [x] Task 1: 设计并落地 `agent/` 标准目录骨架，定义各子目录职责边界。
  - [x] SubTask 1.1: 输出目录分层方案（core、tools、memory、evaluation、adapters 等）
  - [x] SubTask 1.2: 创建目录与必要 `__init__` 文件，保证可导入

- [x] Task 2: 迁移现有 Agent 模块到 `agent/` 目录并完成引用重映射。
  - [x] SubTask 2.1: 迁移核心聊天与编排模块（如 ai_chat_manager/enhanced_ai_chat_manager/intelligent_agent）
  - [x] SubTask 2.2: 迁移配套模块（上下文、检索、实体跟踪、记忆、评测脚本）
  - [x] SubTask 2.3: 更新内部 import 路径并清理失效引用

- [x] Task 3: 保持启动链路兼容，确保 defect_explore6 不受迁移影响。
  - [x] SubTask 3.1: 更新 `defect_explore6.py` 的 Agent 依赖导入路径
  - [x] SubTask 3.2: 验证 `run_app.py` 与 `start_server.py` 启动行为不变
  - [x] SubTask 3.3: 保留必要兼容层，避免旧路径立即失效

- [x] Task 4: 更新仓库规则与文档，固化后续 Agent 开发必须在 `agent/` 目录。
  - [x] SubTask 4.1: 更新开发规范文档，声明 Agent 文件落位规则
  - [x] SubTask 4.2: 更新 README/相关说明，给出新目录导航与迁移说明

- [x] Task 5: 执行回归验证并确认 AI 助手能力可用。
  - [x] SubTask 5.1: 验证 defect_explore6 启动成功且页面可加载
  - [x] SubTask 5.2: 验证 AI 聊天入口可触发 Agent 并返回结果
  - [x] SubTask 5.3: 验证关键导入链路无错误与无循环依赖

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 2
- Task 4 can run in parallel with Task 3
- Task 5 depends on Task 3 and Task 4
