---
title: "AI Agent 能力盘点与演进"
type: synthesis
compiled_at: 2026-07-15
compiler: claude-sonnet-5
tags:
  - synthesis
  - compiled
---

# AI Agent 能力盘点与演进

> 跨主题综合页，基于 `60 Knowledge/` 全部知识页提炼。

# Data-Agent 能力盘点与演进建议

## 能力现状（按维度）

### 1. 工具链（Tool Chain）
**现状：中等成熟，但呈"多头并行"结构**

- **主链路**：`理解（term_resolver→entity_extractor→intent_detector）→ SQL生成（3条候选路径：Direct/Decomposed/PlanBased）→ 多路径执行比对（data_signature 判定 UNANIMOUS/MAJORITY/DISAGREE）→ 自修正（QueryFixer）→ 结果校验（ResultValidator）→ 叙事生成（Storyteller）`，这是一条设计完整、有降级兜底的分析流水线。
- **代码执行工具**已完成安全加固：从子串黑名单升级为四层防御（AST 静态分析 → 受限 builtins → OS resource limit → 最小化子进程环境），达到了工程上可信的沙箱水位。
- **工具暴露机制**已具备（`/api/agent/tools` 返回 schema + markdown 描述），说明有意识地在做"工具可发现性"设计。
- **致命短板：三套能力互相割裂**
  1. JS 主对话 Agent（`mainAgentToolLoop.mjs`）——只做 Dashboard 工具调用，最多 4 轮工具调用，浅且薄；
  2. Python Ontology 引擎——有实体对齐、规则、治理、记忆，但**未接入主对话**；
  3. Test Agent（测试用例生成）——**未接入服务端路由**，无验证闭环。
  这意味着"工具链"目前更像三个孤岛，而不是统一 Runtime 下可编排的工具集合。
- Duplicate Search Agent 是相对成熟的独立子系统（双路检索 + RRF 融合 + 渐进式重排 + 证据解释 + 反馈闭环），但被明确要求"不能改"，只能作为主 Agent 的外部工具调用，尚未真正接入。

### 2. 记忆（Memory）
**现状：有会话级/反馈级记忆，缺乏统一记忆架构**

- 短期记忆：`session_id` + `_session_agents` 字典维护多轮对话上下文（`agent/conversation/`），支持"多轮对话上下文"的能力（借鉴 BIRD-Interact 思路）。
- 反馈闭环：`/api/agent/feedback`（up/down + correction）→ `weight_adjustments`（`/api/agent/stats` 可见），说明已有"用户反馈影响后续排序/权重"的机制，这点在 Duplicate Search Agent 上表现得尤为完整（反馈重排）。
- 长期记忆/知识沉淀：目前主要靠 Ontology（`agent/ontology/objects/*.yaml`）作为"结构化长期记忆"，而不是向量库或 episodic memory；这符合当前数据规模（用户自己判断"不需要重型向量数据库"），是合理的克制而非缺陷。
- **短板**：记忆没有跨 session 的用户画像/长期偏好机制；Ontology 虽是全局事实源，但更新流程（谁来治理、如何审核变更）尚不清晰，属于"静态本体"而非"持续学习的本体"。

### 3. 可解释性（Explainability）
**现状：本项目在这一维度是相对亮点**

- 多路径执行比对（三条 SQL 路径 + data_signature 一致性判定）天然提供了"结果可信度"的可解释信号，比单路径生成再执行的传统 text-to-SQL 更透明。
- Storyteller 把 SQL 结果转成叙事化解释，ResultValidator 做结果校验，这一组合在**面向非技术用户**（测试/产品/管理层）沟通结果时是关键能力。
- Duplicate Search Agent 的"证据解释"设计（为什么这两条缺陷相似、依据哪些字段/相似度）已经达到了可以做技术分享 PPT 的成熟度。
- **短板**：可解释性目前停留在"单次结果展示"层面，缺少可追溯的决策链路记录（trace/step log 持久化），也没有把"为什么选了这条 SQL 路径 / 为什么触发 LLM 仲裁"这类元决策过程结构化留存，一旦出问题排查成本高。

### 4. 评测（Evaluation）
**现状：明显最弱的一环，几乎没有形成闭环**

- 目前没有看到独立的 eval harness、benchmark 集、回归测试套件覆盖 NL2SQL 准确率、Ontology 解析准确率、多轮对话成功率等核心指标。
- 唯一可验证的质量信号来自 `MultiPathExecutor` 的一致性判定（UNANIMOUS/MAJORITY/DISAGREE），这是运行时自检，**不等同于离线评测**。
- 分支管理上已经暴露出问题：P1-9 安全加固提交在一个分支，另一分支（`feature/2026-07-01-data-agent-sync`）已经分叉且提交内容差异很大（dashboard/qgate/voice transcribe等），无法确认该分支是否继承了安全修复——这本质上是"没有 CI 门禁 + 没有回归测试"导致的可见风险。
- 用户自己也明确判断："评测闭环未形成门禁"是当前主要差距之一，这是准确的自我诊断。

### 5. 数据与基础设施底座（补充维度）
- SQLite → PostgreSQL 迁移已有代码基础（`psycopg`、`init_postgres_db.py`、`UnifiedDataLoader`），字段基本兼容，但**数据尚未迁移，读取链路仍主要走 SQLite/本地 JSON 文件**，双写未切读，是"半成品迁移"状态，风险可控但需要收尾。
- 存在"文件依赖未完全消退"的技术债：部分分析模块（如 `longrunner_analysis.py`、`data_processor.py` 的部分函数）仍直接读 `history/*.json`，而非统一走数据层抽象，未来接 AI Agent 时会造成数据口径不一致的隐患。

---

## 与成熟框架的差距

以 LangGraph / Pi Agent Core / Codex / OpenClaw 一类成熟 Agent Runtime 为参照：

| 能力项 | 成熟框架标配 | Data-Agent 现状 | 差距等级 |
|---|---|---|---|
| 统一 Agent Runtime | 单一编排层管理所有工具/子 Agent 调用 | JS主循环/Python Ontology/Test Agent 三套割裂 | 🔴 高 |
| 持久化 Checkpoint / 中断恢复 | 原生支持（如 LangGraph Checkpoint） | 仅 session 级内存字典，无持久化/恢复机制 | 🔴 高 |
| Human-in-the-loop 审批 | 原生中断点、审批钩子 | 无（沙箱加固替代了部分风险，但无审批流） | 🟡 中 |
| 可观测性/Tracing | 全链路 trace、step log、metrics 面板 | 仅有 stats 端点（弱聚合指标），无 trace 持久化 | 🔴 高 |
| 评测/回归门禁 | CI 集成 benchmark、离线评测集、门禁阻断合并 | 无独立评测集，分支已出现"修复丢失"风险 | 🔴 高 且优先级最高 |
| 多 Agent 编排 | 原生支持子 Agent 调用/路由（如 CrewAI/LangGraph subgraph） | Duplicate Search Agent 作为孤立工具存在，未编排 | 🟡 中 |
| 记忆架构 | 短期+长期+反馈三层，向量/图混合检索可选 | 短期会话记忆 + 反馈权重，本体作准长期记忆 | 🟢 低（够用） |
| 沙箱安全 | 分层防御 | 已达到（AST+受限builtins+资源限制），持平 | 🟢 无差距 |
| 降级/离线可用性 | 视产品而定，多数商业框架不强调 | 全链路规则回退，可完全离线运行 | 🟢 反超（Data-Agent 优势项） |

**结论**：Data-Agent 不缺"分析型 Agent 的骨架"（工具、记忆、解释、降级都有），缺的是**工程治理层**——统一 Runtime、可观测性、评测门禁。这与之前项目内部结论一致："没必要重造 openclaw 级平台"，应该"借鉴通用能力，压缩为项目场景下的最小可用模块"。

---

## 演进建议（30/60
