---
title: "goal 全网深度分析我的项目里的agent，分析一下我这个智能问数agent如"
type: knowledge
source: "Codex"
source_file: "10 Sources/raw/conversations/Codex/goal-全网深度分析我的项目里的agent-分析一下我这个智能问数agent如何才能像pi-age-019f5c58.md"
compiled_at: 2026-07-15
compiler: claude-sonnet-5
tags:
  - compiled-knowledge
---

# goal 全网深度分析我的项目里的agent，分析一下我这个智能问数agent如

> 编译自 [[10 Sources/raw/conversations/Codex/goal-全网深度分析我的项目里的agent-分析一下我这个智能问数agent如何才能像pi-age-019f5c58.md]] 的完整对话。

## 核心问题

用户拥有一个公司内部智能问数 CoPilot（接入 Bacon、DeepSeek、Qwen、GLM 内部模型），存储了 Octane 系统的测试与缺陷数据，并搭建了 Ontology 本体智能原型。目标是让该 Agent 达到 Codex/Pi Agent 级别的智能，能够：基于项目数据进行深度对话、根据缺陷和测试数据生成测试用例、发挥 Ontology 的业务语义能力，并明确了不能修改现有 Duplicate Search Agent，同时探讨是否可采用开源 Agent 框架（Pi Agent、Codex）作为主 Runtime。

## 关键结论

**当前成熟度评估**：Agent 产品化 3～4/10、数据资产 6/10、Ontology 原型 5/10。项目本质是"带工具的智能问答"，尚非 Codex/Pi 级 Agent。

**三套能力割裂**：
1. JavaScript 主对话 Agent（[mainAgentToolLoop.mjs](/Users/tonyorz/Data-Agent/server/mainAgentToolLoop.mjs)）：仅负责 Dashboard 工具调用和缺陷检索，最多 4 轮工具调用
2. Python Ontology：有实体对齐、规则、治理、记忆，但未接入主对话
3. Test Agent：能生成测试建议，但未接入服务端路由，无验证闭环

**最终架构选型**：**LangGraph JS 作为主 Agent Runtime；Pi Agent Core 作为轻量 PoC 备选；Codex 不作为业务主 Runtime**（仅作 Coding Agent 交互参考）。

对比依据：
| 方案 | 内部模型兼容 | 持久会话/审批 | 业务适配 | 结论 |
|---|---|---|---|---|
| LangGraph JS | 高，可保留现有适配层 | 原生 Checkpoint、流式事件、HITL、中断恢复 | 很高 | **主选** |
| Pi Agent Core | 很高 | 基础循环好，企业能力需自建 | 中高 | 轻量 PoC |
| Codex SDK | 需兼容 Responses API | 强，但围绕代码/Shell/文件 | 低 | 仅借鉴 |

Codex `wire_api` 目前只支持 OpenAI Responses API，而公司模型层是 Chat Completions 形态，需额外实现 `/v1/responses` 兼容桥，成本高且不适合作为业务问数主 Runtime。

**架构边界确认**：
- Duplicate Search Agent 完全不改，仅作为主 Agent 可调用的现有工具
- 继续使用 Bacon/DeepSeek/Qwen/GLM，不依赖 Codex/OpenAI 模型
- Ontology 定位为"可执行语义内核"，不是聊天机器人，也不整份塞进 Prompt
- 测试用例首期只生成有证据溯源的 `TestCaseDraft`，不写回 Octane

**正式产出物**：架构规格文档 [main-agent-runtime-design.md](/Users/tonyorz/Data-Agent/docs/superpowers/specs/2026-07-14-main-agent-runtime-design.md)，已提交 commit `5081107a`，用户回复"规格批准"后确认。

## 操作要点

### 目标架构（推荐方案）
```
LangGraph JS 主 Runtime
├── InternalModelAdapter（Bacon / DeepSeek / Qwen / GLM）
├── Ontology Semantic Kernel
├── Analytics / Database typed tools
├── Duplicate Search（保持不改，仅作为工具）
├── Test Case Intelligence
├── Evidence Validator
└── Session / Approval / Audit / Streaming
```

### Ontology 应暴露的工具接口
`resolve_business_term`、`describe_object_type`、`get_metric_definition`、`query_object_set`、`traverse_links`、`compute_metric`、`get_traceability_path`、`find_coverage_gaps`、`rank_test_risks`、`validate_test_case`、`save_test_case_draft`

### 测试用例生成闭环（12 步）
解析目标→Ontology 取 Requirement/Feature/约束→检索缺陷/历史失败/相似测试→计算风险（严重度×频率×最近性×暴露度×覆盖缺口）→生成测试条件矩阵→生成测试用例→覆盖多场景→语义去重→验证 Expected Result→追踪完整性检查→可自动化时执行验证→Critic 审查→人工批准后写回 Octane。

### 分阶段路线
- **P0（1-2周）**：修复 Ontology 列映射、Ontology 暴露为工具、Test Agent 接线、答案携带证据、建立首批 100 条黄金问数用例
- **P1（3-6周）**：持久 Session/Task/Plan/Checkpoint、真正的 Observe→Plan→Act→Validate→Repair 循环、Semantic Query IR、结果验证器
- **P2（6-10周）**：补齐测试数据、风险覆盖矩阵、生成→去重→Critic→验证→审批闭环
- **P3（3-6月）**：变更影响分析、受控写操作、记忆驱动、持续评测

### 关键 HTTP API 设计（Task 15）
`GET /api/ai/models`、`POST /api/ai/chat`（兼容层）、`POST /api/agent/runs`、`GET /api/agent/runs/:runId/events`、`POST /api/agent/runs/:runId/resume`、`POST /api/agent/runs/:runId/cancel`、`GET /api/agent/threads/:threadId`、`POST /api/agent/threads/import`、`POST /api/agent/threads/:threadId/fork`、`PATCH /api/agent/threads/:threadId`、`POST /api/agent/artifacts`、`GET /api/agent/artifacts/:artifactId`。**明确禁止** Phase 1 增加 approval decide 接口。

### Runtime Mode 策略
默认 `legacy`；`shadow` 不返回答案、不重复调用 Duplicate；`langgraph` 只开放 legacy-equivalence allowlist，支持即时回滚。Phase 1 永远不能发出 `grounded` badge/event，UI 只能显示 `provisional`/`legacy-equivalence`。

### 评测门槛（Phase 1 硬指标，节选）
- tool schema 合法率 100%，不支持工具 0
- 数字/日期/ID 准确率 100%
- evidence 覆盖率 ≥98%，无证据关键结论 0
- 跨用户/thread 串台 0
- 重启恢复率 ≥99%
- 性能：首 lifecycle event P95 ≤300ms，单模型首 token P95 ≤5s，单工具 P95 ≤12s，多工具 P95 ≤30s

## 踩过的坑

1. **Ontology 列映射错误**：演示数据库真实字段是 `project`，但 [profiler.py](/Users/tonyorz/Data-Agent/agent/ontology/profiler.py:83) 强制映射为 `program`，导致"按项目分布"查询返回错误结果（应为 `IuK(2)、EE_MAIN(2)、AF(2)…`，实际返回错误的 `program(8)`）。现有测试 [test_ontology_intelligence.py](/Users/tonyorz/Data-Agent/tests/test_ontology_intelligence.py:42) 反而把错误映射当成期望值。

2. **假冒的 GraphRAG 能力**：所谓 Vector Retrieval 实际只是 SQL 查询却标为 `vector`（[rag.py](/Users/tonyorz/Data-Agent/agent/ontology/rag.py:163)）；Global 只是逐字段 `GROUP BY`，不是真正社区摘要；Drift 只是单层关系查询，不是多跳图探索。

3. **Reasoning Engine 未使用检索结果**：推理阶段没有把检索出的实体 ID 传给 Reasoning Engine，而是重新处理数据库前 N 条记录（[engine.py](/Users/tonyorz/Data-Agent/agent/ontology/engine.py:160)）；高相似度查询直接返回历史答案，不重新查询最新数据，容易产生过期数字（[engine.py](/Users/tonyorz/Data-Agent/agent/ontology/engine.py:124)）。

4. **Test Agent 路由未注册**：前端调用 `/api/test-agent/stats`、`/api/test-agent/analyze`（[TestAgent.tsx](/Users/tonyorz/Data-Agent/src/components/dashboard/pages/TestAgent.tsx:150)），但服务端未注册这两个路由，只有孤立处理函数（[testAgent.mjs](/Users/tonyorz/Data-Agent/server/testAgent.mjs:349)）。

5. **测试数据字段缺失**：5,335 个测试用例，15,000 次执行，但只有 148 个关联 Feature、134 个关联 Story，且缺少测试步骤、前置条件、测试数据、期望结果字段，无法支撑高质量测试用例生成。

6. **模型输出预算过小**：DeepSeek/Qwen/GLM 调用输出预算仅 2048 或 900 tokens（[chatModelConfig.mjs](/Users/tonyorz/Data-Agent/server/chatModelConfig.mjs:145)），不足以支撑多步骤业务调查、测试方案自审等复杂任务。

7. **实施规格审计发现的具体缺口**（Task 1-19 逐项对照）：
   - Ajv 默认 draft-07，规格要求 JSON Schema 2020-12，需用 `ajv/dist/2020.js`
   - `DEFAULT_CAPABILITIES` 通用配置违反"每模型独立声明能力"原则
   - `enabled
