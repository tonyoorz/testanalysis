---
title: "Agent 平台工程参考：Datus / DB-GPT / Vanna 2"
type: knowledge
source: "research-doc"
source_file: "智能问数Agent全网深度调研-2026-08-03.md"
compiled_at: 2026-11-11
compiler: zcode-night
tags:
  - compiled-knowledge
---

# Agent 平台工程参考：Datus / DB-GPT / Vanna 2

> 编译自 [[智能问数Agent全网深度调研-2026-08-03]] §3.5（L360–398）、§3.7（L433–448）、§3.8（L451–469）。证据等级 A。

## 核心问题
三个「平台型」Data Agent 项目的工程能力哪些值得搬？为什么都不适合作为 Data-Agent 主架构？

## 关键结论

### Datus：完整 Agent Workflow + 评测工程（§3.5）
- 可配置 node workflow（L369–378）：`schema_linking → parallel(gen_sql, reasoning) → selection → execute_sql → output`。
- 节点分类（L380–385）：Core（schema linking、execute SQL、reasoning、reflect、output）、Agentic（gen SQL、chat、explore、gen semantic model、gen metrics、report）、Control flow（parallel、selection、subworkflow）、Utility（date parser、doc search、fix）。
- RAG Knowledge Base 用 **LanceDB 分层**存 schema metadata、reference SQL、Jinja 模板、semantic models、executable metrics、文档；支持 per-node model、**BIRD/Spider 2.0-Snow benchmark**、LLM trace、FastAPI/CLI/Web/MCP、多数据库 adapter（L387）。
- 2026 新增：permission profile、session resume/rewind、ask-user、scoped context、只读 SQL、deliverable validation hook、项目 memory、数据工程 subagents——正从 NL2SQL 扩张为通用 data-engineering agent 平台（L389–391）。
- 借鉴：node contract、workflow config、trace、benchmark runner、deliverable validation、context scope。不照搬：默认多节点/多模型/多 subagent 流程（L393–397）。

### DB-GPT：通用平台，不作主架构（§3.7）
- 覆盖 task planning、SQL/Python 执行、RAG、skills、AWEL workflow、多模型、多数据源、sandbox、报告图表；2026-03 发布 v0.8.0（L438）。
- 值得借鉴（L440–445）：**生成代码/SQL 必须进 sandbox**；输出是可复用 artifact/report 而非聊天片段；skill 封装重复分析流程；多源分析统一执行环境。
- 不迁移的理由（L447）：核心链路不需要任意 Python 执行与通用多 Agent 平台；迁入会弱化已有 Ontology 与领域 API，换来暂时不需要的部署与治理面。

### Vanna 2：接口漂亮，但已归档（§3.8）
- 架构（L456–464）：`vanna-chat → FastAPI ChatHandler → Agent → ToolRegistry/user-aware tools → row-level filtering → SSE table/chart/summary`；`UserResolver`、user/groups、tool access group、lifecycle hooks、middleware、conversation storage、observability、streaming UI component 都是明确扩展点。
- **仓库 2026-03-29 已归档只读**（L83、L469）：不能作为新的关键依赖，更不能再列为「活跃开源 SOTA 项目」。

## 操作要点
- 平台共同启示：trace/benchmark/validation 是工程资产，多 Agent 堆叠不是——呼应 [[60 Knowledge/Concepts/智能问数行业收敛方向-2026|行业收敛方向]]的「明确反对」清单。
- Datus benchmark 思路落到 [[60 Knowledge/Concepts/Data-Agent工程路线P0-P1-P2|P0.5 端到端 golden]]。

## 相关页面
- [[60 Knowledge/Concepts/学术Text-to-SQL-CHESS-CHASE-XiYan|学术系统（benchmark 对照）]] · [[60 Knowledge/Concepts/Data-Agent架构基线与代码断点|Data-Agent 基线]] · [[60 Knowledge/Concepts/WrenAI开放上下文层|WrenAI]]
