---
title: "Data-Agent 目标架构三合同（SemanticFrame / QueryPlan / AnalysisResult）"
type: knowledge
source: "research-doc"
source_file: "智能问数Agent全网深度调研-2026-08-03.md"
compiled_at: 2026-11-11
compiler: zcode-night
tags:
  - compiled-knowledge
---

# Data-Agent 目标架构三合同（SemanticFrame / QueryPlan / AnalysisResult）

> 编译自 [[智能问数Agent全网深度调研-2026-08-03]] §8（L688–794）。

## 核心问题
推荐目标架构的骨架是什么？三个核心类型合同与 `analysis_ref` 必须保存什么？

## 关键结论

### 架构总图（§8，L690–732）
```text
UI(Chat/SSE/Analysis UI) → 一个主 Agent(bounded model-tool loop) + ask_clarification
→ Deterministic Semantic Kernel:
    Context Retriever(ontology subset+values+verified examples)
    → Resolver(NL→SemanticFrame)
    → Typed Query Planner(SemanticFrame→QueryPlan)
    → Plan Validator(rules·relationships·availability·limits)
    → Analysis Primitives(aggregate·compare·records·trace)
→ Domain Execution Plane: Defect Snapshot / Testing Coverage / Traceability
  / Duplicate Search / Testcase Context 五个 Adapter
→ Analysis Store(analysis_ref·frame·plan·snapshot·evidence)
→ Claim→Evidence Gate → Agent → UI
Context Build Plane: 来源(Ontology·field catalog·docs·approved queries·feedback)
  → Normalize/Reconcile/冲突检测 → 人工审核·版本发布·回滚 → 端到端 eval(与审核互馈)
```

### 三合同（§8.1，L734–782）
```ts
type SemanticFrame = {
  intent: "aggregate" | "compare" | "trend" | "rank" | "records" | "trace";
  metricIds: string[]; dimensionIds: string[]; filters: SemanticFilter[];
  timeScopes: TimeScope[]; comparison?: ComparisonSpec; requestedFields?: string[];
  assumptions: string[]; ambiguities: Ambiguity[];
  ontologyVersion: string; schemaFingerprint: string;
};
type QueryPlan = {
  planId: string; frame: SemanticFrame;
  snapshotPolicy: "required" | "best_effort";
  steps: PlanStep[]; invariants: string[]; deniedReasons: string[];
};
type AnalysisResult = {
  analysisRef: string;
  resultKind: "aggregate" | "comparison" | "records" | "trace";
  snapshotSet: SourceRevision[]; data: unknown;
  claims: Claim[]; evidence: EvidenceRef[]; quality: QualityEnvelope;
  continuation: { allowedOperations: ("drilldown"|"compare"|"explain"|"trace")[] };
};
```

### `analysis_ref` 必须保存什么（§8.2，L784–794）
原始问题与已确认澄清；SemanticFrame 与 QueryPlan；每个数据源的 `sourceRevision/snapshotVersion/asOf`；聚合结果与选中异常 group；records query 的 filter/字段 allowlist/分页 cursor；证据哈希、质量 warning、Ontology version；允许的下一步操作。
**效果**：「为什么这个模块增长最快？」不需要重新解析、重新取最新数据，而是从原 `analysis_ref` 继续执行**同快照** records/explain。

## 操作要点
- 三合同直接对应 [[60 Knowledge/Concepts/Data-Agent架构基线与代码断点|基线断点]] E/B/F 的根治：统一语义运行路径（断点 A）、真 records（断点 B）、发布门禁（断点 F）。
- 计划节点风格参考 [[60 Knowledge/Concepts/语义层引擎对标-Cube-MetricFlow-SLayer|MetricFlow dataflow plan]]：ResolveScope → SelectSnapshot → Aggregate → Compare → SelectAnomaly → FetchRecords → ComputeEvidence → PublishAnalysis（L302）。
- provenance 字段（source_id/version/as_of/quality/owner/evidence）参考 [[60 Knowledge/Concepts/ktx与Context-Build-Plane|OpenMetadata provenance schema]]；verified 语义参考 [[60 Knowledge/Concepts/商业问数产品架构对标|Snowflake VQR]]。
- 实施顺序见 [[60 Knowledge/Concepts/Data-Agent工程路线P0-P1-P2|工程路线]]：P0.1 统一契约 → P0.2 records → P0.4 analysis_ref + 门禁。

## 踩过的坑
- 原文强调（§0.3 L47）：`snapshot_version + analysis_ref + evidence_ref` 要做成**一等公民**，否则多轮追问漂移、结论不可复现——这是对标 Snowflake multi-turn/VQR、Wren dry-plan、Palantir Ontology 的共同结论。

## 相关页面
- [[60 Knowledge/Concepts/智能问数行业收敛方向-2026|行业收敛方向]] · [[60 Knowledge/Decisions/研究任务-ontology本体在-data-agent-AI-数据智能中的应用|Ontology 应用研究]] · [[30 Topics/Data-Agent-项目架构|Data-Agent 项目架构]]
