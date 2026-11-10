---
title: "ktx 与 Context Build Plane（含 OpenMetadata）"
type: knowledge
source: "research-doc"
source_file: "智能问数Agent全网深度调研-2026-08-03.md"
compiled_at: 2026-11-11
compiler: zcode-night
tags:
  - compiled-knowledge
---

# ktx 与 Context Build Plane（含 OpenMetadata）

> 编译自 [[智能问数Agent全网深度调研-2026-08-03]] §3.4（L310–357）、§3.9（L473–488）。证据等级 A。

## 核心问题
语义知识/上下文的「供应链」如何工程化？ktx 的 Context Build Plane 与 OpenMetadata 的 Context Graph 给出什么模板？

## 关键结论

### ktx：executable context layer（§3.4）
- 定位（L315–317）：不只建指标 YAML，而是把 warehouse introspection、dbt/MetricFlow/LookML/BI 元数据、历史 SQL、Notion/wiki 统一**采集、去重、标来源、检测矛盾**，输出可审查的 YAML/Markdown 资产。
- 代码结构（L319–339）：`packages/cli/src/context/`（ingestion/reconciliation/index）、`connectors/`（只读连接器）、`mcp/`、`python/ktx-sl/`（语义查询计划）、`ktx-daemon/`（计算 sidecar）；资产分层 `semantic-layer/<connection-id>/`、`wiki/global/`、`wiki/user/<user-id>/`、`raw-sources/`（采集证据）、`.ktx/`（本地状态不入 Git）。
- **连接器策略只有 `read-only-sql` 与 `semantic-layer-only` 两种——是否允许 raw SQL 是确定性配置，不由 Agent 临时决定**（L340–341）。
- 最值得复制的知识供应链（L344–356）：
```text
source evidence → normalize → propose semantic change → detect conflict
→ human review → publish version → rebuild index/eval
```
- 不作运行时依赖：Data-Agent 数据源与领域对象不是纯 warehouse；建议**原生实现一个较窄但完整的 Context Build Plane**。

### OpenMetadata：企业 Context Graph 上游参考（§3.9）
- 不是问数 Agent，而是统一技术元数据、质量、lineage、ownership、usage、policy、glossary、metrics、contracts、conversations/memory 的 Context + Memory Graph；130+ connectors、MCP、API/SDK、开放 schema（L477–478）。
- 价值在于定义「证据上下文」不止术语（L480–485）：指标定义与业务术语、来源/owner/质量/freshness/certification、column 与 data-product lineage、决策/假设/事故与修复记录。
- 不部署全平台（对内网小团队太重）；先借鉴 **provenance schema**，把 `source_id/version/as_of/quality/owner/evidence` 纳入 Ontology publication 与 `analysis_ref`（L487）。

## 操作要点
- 对应 [[60 Knowledge/Concepts/Data-Agent架构基线与代码断点|基线断点]]中的劣势「知识更新没有控制面：没有 source provenance、proposal、review、publication、rollback 全流程」（§7.2 L678）。
- 落地即 [[60 Knowledge/Concepts/Data-Agent工程路线P0-P1-P2|P1.1 Context Build Plane]]：source adapters → raw evidence → normalize → conflict detection → proposal → review → publish → rollback → index/eval（L874–876）。
- 与 [[60 Knowledge/Concepts/智能问数行业收敛方向-2026|行业收敛]]机制 2/4 呼应：知识进版本化资产、反馈经审核再沉淀。

## 踩过的坑
- ktx 是新项目（快照日 2026-07-19 最近推送，1.5k★），主要围绕 warehouse/BI 生态——借鉴流程，不押注运行时。

## 相关页面
- [[60 Knowledge/Concepts/WrenAI开放上下文层|WrenAI]]（memory 机制同为「经确认才沉淀」） · [[60 Knowledge/Concepts/语义层引擎对标-Cube-MetricFlow-SLayer|Cube/MetricFlow/SLayer]] · [[60 Knowledge/Concepts/Data-Agent目标架构三合同|目标架构三合同]]
