---
title: "Data-Agent 工程路线 P0/P1/P2"
type: knowledge
source: "research-doc"
source_file: "智能问数Agent全网深度调研-2026-08-03.md"
compiled_at: 2026-11-11
compiler: zcode-night
tags:
  - compiled-knowledge
---

# Data-Agent 工程路线 P0/P1/P2

> 编译自 [[智能问数Agent全网深度调研-2026-08-03]] §9（L798–908）、§10（L912–927）、§11（L930–950）。

## 核心问题
把调研结论转成可验收的工程排期：P0 做什么才能「资格验收」，P1/P2 何时做？各对标项目的采用红线是什么？

## 关键结论

### P0：可资格验收的端到端闭环（L800–870）
| 项 | 核心改动 | 验收 |
|---|---|---|
| P0.1 统一语义路径并精简工具 | 旧 `query_analytics*`/`query_full_picture_module`/`query_defect_records` 移入 adapter/internal fallback；只暴露 `semantic_aggregate/compare/records/trace`；共享 SemanticFrame/QueryPlan/AnalysisResult envelope | 同一问题无论首问/追问进同一 planner，不同工具不给不同口径 |
| P0.2 真 records primitive | 返回 allowlisted row fields，不再调 `_aggregate_rows()`；强制 `snapshot_version`；稳定 sort、cursor 分页、最大页大小；不可用字段 fail closed 不返回 `(missing)` | 「最近四周哪个业务模块新增缺陷增长最快？」→ 聚合比较 → 选高增长模块 → 同快照取 5–10 个 ticket 样本 → 证据解释 → 追问仍用同 analysis_ref |
| P0.3 Ontology 变可执行内核 | candidate retrieval 只辅助 resolver；business rules/relationship traversal/constraints 进 planner/validator；每个 dimension/metric 标 `available/partial/unavailable` + source binding；query-relevant ontology projection；歧义超阈值只问一个聚焦问题 | 未绑定字段不能进 plan；关系路径可 explain；规则触发在 plan trace 可见 |
| P0.4 analysis_ref + Claim/Evidence 门禁 | Analysis Store；finalize 前校验所有数字/排序/增长率/样本引用；区分「相似性证据/相关性/因果结论」，缺因果证据禁止写因果；LLM 只组织已验证 claims | 删/篡改任一 evidence → 回答发布失败并返回可理解的限制说明 |
| P0.5 韧性+失败审计+端到端 eval | LLM timeout/有限 retry/错误分类/熔断降级；`graph.invoke` 成败都写 run terminal state；checkpoint 持久化但只存必要 state；30–50 条真实 golden 覆盖 aggregate/compare/records/trace/duplicate/testcase/clarification/follow-up；CI 分 deterministic fast gate 与受控 model regression | 失败 run 100% 可定位；端到端测试断言结果集、快照、引用 |

### P1：上下文与反馈飞轮（L872–899）
- **P1.1 Context Build Plane**：source adapters → raw evidence → normalize → conflict detection → proposal → review → publish → rollback → index/eval；来源含 Ontology、Octane field catalog、内部文档、approved query、成功分析、人工反馈。
- **P1.2 Value/Schema Linking**：高价值维度维护代表值/别名/正反例；BM25/向量只做候选召回，最终选择受类型、scope、capability 校验；优先项目、OS、PU、模块、版本、phase、日期窗口。
- **P1.3 Verified Analysis Repository**：存 `question pattern → expected SemanticFrame → expected Plan invariants → approved analysis template → result assertions → verified_by/verified_at/ontology_version`；同时服务 runtime few-shot 与 evaluation，评测样例必须从 runtime retrieval 隔离防泄漏。
- **P1.4 结果解释与 UI**：展示业务可读 semantic tokens（指标/维度/时间/比较组/过滤/快照/质量/records 样本）；不展示隐藏 chain-of-thought，展示可验证的 plan summary 与 evidence。

### P2：有真实需求和指标后再做（L901–908）
Cube 风格预聚合（p95/并发数据证明需要时）；OpenMetadata/graph projection（lineage 用）；正式 auth/RLS/multi-tenant；sandbox Python/SQL；CHASE 式多候选 ensemble（仅低置信度复杂问题且 eval 证明收益>时延）；写操作与 testcase 生成走 Palantir 风格 typed action + preview + approval + audit。

### 项目采用红线（§10，L912–927 摘要）
- **WrenAI**：能力对齐不直接做主依赖（避免 Ontology 与 MDL 双事实源）；**Cube**：暂不引入，留 SQL warehouse adapter 选项；**MetricFlow**：借鉴 QueryPlan 结构；**ktx**：强借鉴 Context Build Plane，优先原生实现；**Datus**：借鉴 node/eval/trace 不用默认多 subagent；**SLayer**：未来 SQL 域 PoC；**DB-GPT**：不迁移主架构；**Vanna**：只借鉴接口（已归档）；**OpenMetadata**：借鉴 provenance/quality schema 暂不部署；**CHESS/CHASE/XiYan**：算法按需吸收，在线保持单 Agent；**Snowflake/Genie/Fabric/Palantir/Spotter**：产品与治理设计标杆。
- 内网小规模团队前提：正式用户体系、RLS、多租户**保留接口但不入当前 P0/P1**（L55）。

### 最该做 / 最不该做（§11，L932–946）
最该对齐五件事：①Wren/MetricFlow 式可 explain Semantic QueryPlan；②ktx/OpenMetadata 式带来源/版本/质量/冲突/审核的知识；③Snowflake 式 verified analysis + 执行结果 regression eval；④Genie 式 value/entity matching 与反馈审核；⑤Palantir/Spotter 式 Ontology binding 与业务可读 semantic tokens。
最不该做五件事：①整体嵌入 WrenAI/DB-GPT/Datus；②Router/Planner/Verifier/Supervisor 多 Agent 堆叠；③继续加 dashboard/page 级工具；④把 vector RAG 当语义层、让用户反馈自动改 Ontology；⑤records/snapshot/analysis_ref/evidence gate 未完成前先做炫酷图表或任意 Python 分析。

**一句话架构判断**（L950）：Data-Agent 最好的形态 = 「一个懂汽车测试业务的主 Agent，调用一个确定性、可版本化、可追问、证据优先的 Semantic Kernel」。

## 操作要点
- 每项 P0 都带可执行验收问题（见上表 P0.2 验收文本），直接可作为 golden 用例来源。
- 与既有任务的衔接：评测数据面依赖 [[60 Knowledge/Solutions/octane数据下载与入库链路|Octane 数据下载与入库链路]] 的 DB/快照现状；架构演进判断另见 [[50 Syntheses/AI-Agent能力盘点与演进|AI Agent 能力盘点与演进]]。

## 相关页面
- [[60 Knowledge/Concepts/Data-Agent目标架构三合同|目标架构三合同]] · [[60 Knowledge/Concepts/Data-Agent架构基线与代码断点|架构基线与断点]] · [[60 Knowledge/Concepts/智能问数行业收敛方向-2026|行业收敛方向]]
- [[60 Knowledge/Concepts/ktx与Context-Build-Plane|ktx]] · [[60 Knowledge/Concepts/学术Text-to-SQL-CHESS-CHASE-XiYan|学术系统]] · [[60 Knowledge/Concepts/商业问数产品架构对标|商业产品]]
