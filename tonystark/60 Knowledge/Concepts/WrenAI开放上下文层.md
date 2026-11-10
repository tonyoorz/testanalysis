---
title: "WrenAI 开放上下文层"
type: knowledge
source: "research-doc"
source_file: "智能问数Agent全网深度调研-2026-08-03.md"
compiled_at: 2026-11-11
compiler: zcode-night
tags:
  - compiled-knowledge
---

# WrenAI 开放上下文层

> 编译自 [[智能问数Agent全网深度调研-2026-08-03]] §3.1（L161–229）。证据等级 A/B（源码 + 官方文档）。

## 核心问题
WrenAI 2026-05 重构后的真实定位是什么？Data-Agent 该借鉴什么、为何不直接集成？

## 关键结论

**定位变化**（L168–170）：WrenAI 已不是 Docker Chat BI 应用。2026-05-07 旧 `wren-engine` 并入主仓库 `core/`，旧 chat-first 产品移入 `legacy/v1`（不再获得新功能与安全修复）。主线变成：**让外部 Agent 通过 CLI、SDK、skills 使用一个开放、可版本化的上下文和语义执行层**。

**四层架构**（L172–177）：Agent Workflow（Markdown skills）→ Project Context（MDL、instructions、profile、memory）→ Planning Engine（modeled SQL 展开为目标数据源 SQL）→ Execution Layer（连接器执行、Arrow 结果）。

**`WrenEngine.dry_plan()` 执行路径**（L181–193）：
```text
目标方言 SQL → sqlglot parse → 找模型/视图引用
→ 从完整 MDL 抽取最小 effective manifest
→ strict mode / denied functions policy 校验
→ wren-core SessionContext → CTERewriter 展开 modeled object
→ 生成目标方言 SQL → connector dry-run / query
```

**仓库结构**（L195–202）：`core/wren-core/`（Rust + DataFusion 语义计划）、`wren-core-base/`（MDL manifest）、`wren-core-py/`、`core/wren/`（CLI/SDK、连接器、memory、policy）、`sdk/wren-langchain/`、`skills/`。

**正确性机制**（L204–206）：拆成 schema linking、value profiling、ambiguity detection、generation trace、retry/repair、eval 六个 primitive；`wren dry-plan` 暴露模型/join/CTE/expanded SQL；structured errors 支持 Agent 自修复。

**不能误写的部分**（L208–210）：golden NL-SQL eval 仍在 development；audit log、rate limit、approval workflow、data-flow inspector 仍在 roadmap——**不能写成已拥有全部生产治理能力**。

## 操作要点（对 Data-Agent）
**应借鉴**（L214–220）：可审查版本化 Context Artifacts；`dry-plan → validate → execute` 分离；strict manifest scope + structured errors；记忆只存经确认样例；SDK/tool adapter 边界。

**不直接集成 `wren-core` 的理由**（L222–227）：
- Wren 核心执行对象是 SQL warehouse 上的 modeled SQL；Data-Agent 数据源含 Python read models、缺陷快照、traceability、duplicate search 等非统一 SQL 服务；
- JSON Ontology 转 MDL 会制造**两个语义事实源**和同步风险；
- 主要缺口是契约统一、records/snapshot/evidence 闭环，不是缺 SQL AST 重写器。

**结论**（L228）：采用 **Wren-aligned native architecture**，不把 Wren 当主运行时。

## 相关页面
- [[60 Knowledge/Concepts/智能问数行业收敛方向-2026|行业收敛方向]] · [[60 Knowledge/Concepts/语义层引擎对标-Cube-MetricFlow-SLayer|Cube/MetricFlow/SLayer]] · [[60 Knowledge/Concepts/ktx与Context-Build-Plane|ktx Context Build Plane]]
- [[60 Knowledge/Concepts/Data-Agent目标架构三合同|目标架构三合同]] · [[60 Knowledge/Concepts/Data-Agent工程路线P0-P1-P2|工程路线 P0/P1/P2]]
