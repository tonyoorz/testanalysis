---
title: "Data-Agent 架构基线与代码断点"
type: knowledge
source: "research-doc"
source_file: "智能问数Agent全网深度调研-2026-08-03.md"
compiled_at: 2026-11-11
compiler: zcode-night
tags:
  - compiled-knowledge
---

# Data-Agent 架构基线与代码断点

> 编译自 [[智能问数Agent全网深度调研-2026-08-03]] §2（L89–156），基线分支 `feature/2026-07-30-main-agent-recovery-sync`，基线提交 `e764175c`。

## 核心问题
2026-08-03 时点 Data-Agent 的真实架构现状：哪些是对的底子？哪些是代码级断点？

## 关键结论

### 已具备的正确基础（§2.1，L91–98）
1. **一个主 Agent + 有界循环**：默认运行时已是 `langgraph`，单次最多 4 个工具步骤（`server/agentRuntime/langGraphChatRuntime.mjs` L234/L271）。
2. **显式状态机**：`initialize → resolve_context → route_tools → plan_tool_calls ⇄ execute_tool_calls → finalize` 六节点（同文件 L534）。
3. **领域 Ontology 有规模**：28 实体、50 维度、30 指标、27 关系、12 业务规则、5 约束、3 动作。
4. **受治理语义工具入口已存在**：`query_semantic_metrics`、`query_semantic_records`、`query_traceability`（`server/mainAgentTools.mjs` L160）。
5. **领域工具资产**：`search_duplicates`（重复缺陷检索）、`get_test_case_context` 已适配（L487/L700）。
6. **快照基础设施**：缺陷数据已有快照能力，语义结果可携带 `sourceRevision`/质量元数据。

### 代码级断点 A–H（§2.2，L100–156）
| 断点 | 问题 | 关键证据 |
|---|---|---|
| A | 工具面「新语义 + 旧页面」双轨，同一意图暴露多个重叠工具 | `mainAgentToolRegistry.mjs` |
| B | `query_semantic_records` 不是真 records，最终仍调 `_aggregate_rows()` 分组计数 | `queryPlanner.mjs` L99、`semantic_query.py` L499/L575 |
| C | 缺失维度被物化为 `(missing)`，数据源不提供的维度应 fail closed | `semantic_query.py` L491 |
| D | 关系/业务规则/候选消歧未接入执行链：`getRelationship()` 无生产调用、`semanticCandidate.mjs` 无调用者、`business_rules.json` 未加载 | `registry.mjs` L73、`queryPlanner.mjs` L77 |
| E | 没有一等公民 `analysis_ref`，快照信息分散、追问无法恢复原分析上下文 | — |
| F | evidence 被收集但最终答案无程序化 Claim→Evidence 门禁 | `langGraphChatRuntime.mjs` L258 |
| G | 韧性不足：`companyChat.mjs` 裸 fetch 无 timeout/retry；异常 run 无终态持久化；`MemorySaver` 仅进程内 | `companyChat.mjs` L397/L459 |
| H | 评测是组件级（10 条路由 golden + 113 条 frame golden）不验证执行结果/同快照 compare/真 records/证据一致/追问复用 | — |

**总判断**（§2.2 断点 D 后注）：Ontology 的「定义完整度」领先于「运行时兑现度」——更像 catalog 而非完整 executable semantic kernel（§7.2，L674）。

> [!contradiction] Ontology 是否已接入主对话？
> - [[60 Knowledge/Solutions/goal-全网深度分析我的项目里的agent-分析一下我这个智能问数agent如|2026-07-14 Codex 全网分析]]：Python Ontology「有实体对齐、规则、治理、记忆，但**未接入主对话**」。
> - [[智能问数Agent全网深度调研-2026-08-03|2026-08-03 代码级调研]]（§2.1 L96）：已存在受治理语义工具入口 `query_semantic_metrics` / `query_semantic_records` / `query_traceability`。
> 两次结论相差约 3 周，大概率是期间演进而非事实冲突；但注意断点 B/D——records 并非真行、规则与关系仍未接线，即「入口已接、兑现不全」。

## 操作要点
- 断点 A 的收敛方向（L106）：停止加页面级工具，工具面收敛为 `semantic_aggregate / semantic_compare / semantic_records / semantic_trace / duplicate_search / testcase_context·generate / ask_clarification`。
- 断点 B 的破坏场景（L113–118）：聚合发现高增长模块 → 想取 ticket 样本解释 → "records" 又返回分组计数表，闭环断裂。
- 对应修复全部编入 [[60 Knowledge/Concepts/Data-Agent工程路线P0-P1-P2|工程路线 P0]]。

## 踩过的坑
- 断点 C 的隐性风险：Agent 会把「不存在的数据能力」叙述成有效分组——`(missing)` 只该用于「字段存在但某行为空」。

## 相关页面
- [[60 Knowledge/Concepts/智能问数行业收敛方向-2026|行业收敛方向]] · [[60 Knowledge/Concepts/Data-Agent目标架构三合同|目标架构三合同]] · [[60 Knowledge/Concepts/Data-Agent工程路线P0-P1-P2|工程路线 P0/P1/P2]]
- [[60 Knowledge/Decisions/研究任务-ontology本体在-data-agent-AI-数据智能中的应用|Ontology 应用研究]] · [[50 Syntheses/AI-Agent能力盘点与演进|AI Agent 能力盘点与演进]] · [[30 Topics/Data-Agent-项目架构|Data-Agent 项目架构]]
