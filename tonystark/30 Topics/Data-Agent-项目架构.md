---
title: "Data-Agent 项目架构"
type: topic
description: "Data-Agent（汽车测试缺陷/Octane 数据的 text-to-SQL Agent）的整体架构、能力分析与演进"
page_count: 10
compiled_at: 2026-07-15
compiler: claude-sonnet-5
tags:
  - topic
  - compiled
---

# Data-Agent 项目架构

> Data-Agent（汽车测试缺陷/Octane 数据的 text-to-SQL Agent）的整体架构、能力分析与演进。综合 10 篇知识页。

## 主题概述

Data-Agent 是一个面向汽车测试缺陷/Octane 数据的 text-to-SQL 对话式智能问数 Agent 项目（`/Users/tonyorz/Data-Agent`），采用 Python FastAPI 后端 + React/TypeScript 前端架构。本主题综合了该项目的核心处理流水线、Ontology 本体驱动设计、数据层从 SQLite 向 PostgreSQL 的迁移演进、代码执行沙箱的安全加固过程，以及面向 Codex/Pi Agent 级智能的下一代 Agent Runtime 选型决策，同时涉及与之相关的周边产出（Duplicate Search Agent 技术分享、姊妹项目 vizion-lab 前端）。

## 核心知识

### 整体架构与技术栈

Data-Agent 服务入口为 `api/main.py`（FastAPI，title="Data-Agent API", version="1.0.0"），启动方式 `python3 -m api.main` 或 `uvicorn api.main:app --host 0.0.0.0 --port 8100 --reload`，前端为 Vite/React/TS。核心模块位于 `agent/` 下，分为 `agent_loop`、`context`、`conversation`、`data`、`interpret`、`learning`、`llm`、`ontology`、`sql_engine`、`understand`，配合根目录 `api/`、`data/`、`frontend/`、`tests/`。项目文档 `AGENT_DESIGN_REVIEW.md`、`DUPLICATE_DEFECT_SEARCH_DESIGN.md`、`PHASE1_REPORT.md`~`PHASE6_REPORT.md` 表明项目按 Phase 1–6 迭代推进（Phase 1–4 已在 `api/main.py` 文档字符串中确认集成）。

REST/SSE 接口以 `/api/agent/` 为前缀：
- `POST /query`（`:320`）—同步查询
- `GET /stream`（`:444`）—SSE 流式查询（start/thought/action/observation/final/done）
- `POST /feedback`（`:485`）—用户反馈（up/down + note/correction）
- `GET /history`、`GET /stats`、`GET /health`

默认为规则模式，设置 API Key 后可切换为 LLM 增强模式（智谱 GLM / DeepSeek）。架构灵感来源明确列出：WrenAI MDL（Ontology）、CHASE-SQL（多路径生成+执行引导选择）、MARS-SQL（结果校验+自修正）、BIRD-Interact（多轮对话上下文）、Palantir Ontology（本体建模）。

### 处理流水线：理解 → 生成 → 执行 → 校验 → 解释

核心链路为：**理解（`term_resolver` → `entity_extractor` → `intent_detector`）→ SQL 生成（3 条候选路径）→ 多路径执行比对 → 自修正（QueryFixer）→ 结果校验（ResultValidator）→ 叙事生成（Storyteller）**。

NL2SQL 的本质是**模板填充而非 LLM 直接生成**：`NL2SQLEngine.query()`（`agent/sql_engine/generator.py:590`）通过 `DirectGenerator`/`DecomposedGenerator`/`PlanBasedGenerator` 生成 3 个候选 SQL，由 `MultiPathExecutor` 执行并比较 `data_signature`，判定：
- UNANIMOUS（置信度 0.95）
- MAJORITY（置信度 0.80）
- DISAGREE（触发 LLM 仲裁，或按路径优先级回退：plan_based > decomposed > direct）

**降级设计彻底**：所有依赖 LLM 的路径都有规则回退（意图/实体提取纯正则、SQL 模板化、code interpreter 有 `_fallback_code`），系统可完全离线运行。

### Ontology 是全局单一事实来源

`agent/ontology/objects/*.yaml`（defect/project/testcase/defect_history/manual_run/team）驱动 schema、别名解析、类别分组、业务规则、治理约束，贯穿理解层、生成层、prompt 构建、校验层——是整个系统的"单一事实来源"（Single Source of Truth）。

外部研究（GraphRAG/知识图谱方向）为该本体演进提供了参照：Microsoft GraphRAG、LightRAG、HippoRAG、PathRAG 等是本体增强 RAG 的主要竞争/演进方案；LightRAG 主打轻量高效（成本较 GraphRAG 降低约 100 倍）；Neo4j `llm-graph-builder` 提供"5 分钟从零到 GraphRAG"的工程化路径。这些外部方案尚未落地进 Data-Agent，属于研究储备。

在最新的 Agent Runtime 规划中，Ontology 被重新定位为**"可执行语义内核"**，而非聊天机器人或整份塞入 Prompt 的静态知识——这是对早期"Ontology 驱动 schema/校验"定位的进一步收窄和明确化。

### 数据层：SQLite 现状与 PostgreSQL 迁移

**现状诊断**：项目存在两套下载器——`download/octane_downloader.py`（默认写数据库，除非加 `--skip-db`）和 `downloader7.py`（纯文件落地，无数据库写入）。两者字段定义一致（`DEFAULT_F_DEFECT_MAIN`/`DEFAULT_F_MANUALRUN` 均 40/30 字段），但 history 抓取存在潜在截断差异（`downloader7.py` limit=10000 vs `octane_downloader.py` limit=5000）。

当前 DB 数据量：`octane_defects=15298`、`octane_manual_runs=34333`、`octane_defect_histories=8493`，与本地文件数量一致。读取模式是**DB优先+文件回退**而非纯 DB only：默认 `db_first`（`db_migration_config.py:14`），写入默认 `both`（`db_migration_config.py:20`）；`data_processor.py` 的 `load_defect_data/load_test_data` 均有回退逻辑，主加载 `defect_explore6.py:669` 走 `use_db=True` 但底层仍可能回退文件。部分分析代码仍直接读 `history/*.json`（`data_processor.py:3298`、`:3810`、`longrunner_analysis.py:93/289`），**本地文件尚未完全变为纯备份**。

**PG 迁移字段兼容性核查**：SQLite 与 PostgreSQL 中 `octane_payloads`、`octane_defect_histories`、`octane_defects`、`octane_manual_runs` 四张表字段名、数量一一对应，但 PG 约束更严格：
- `octane_defects`：`defect_id/raw_json/fetched_at` 在 PG 为 NOT NULL（SQLite 可为空）
- `octane_manual_runs`：`mr_id/raw_json/fetched_at` 在 PG 为 NOT NULL
- `octane_payloads.year` 在 PG 为 NOT NULL（默认 -1）

真正支持 PG 读取的是 `UnifiedDataLoader`（`unified_data_loader.py:526`, `:773`），已做过 smoke test（PG 当前为空，查询返回 0 行）。项目已有 PG 支持基建（非从零搭建）：`requirements.txt:55`（`psycopg`）、`deploy/start_postgres.sh:1`、`init_postgres_db.py:1`。迁移状态对比：defects 15298 vs 0、manual_runs 34333 vs 0、histories 8493 vs 0——**字段兼容但数据尚未导入，读取链路尚未切换**。

**技术选型结论**：SQLite 在当前阶段完全可用，性能瓶颈真实来源通常是 JSON 反复读取解析、特征重复计算、history 文件级遍历，而非数据库本身本身，不需要因"要接入 AI"就立刻换 DuckDB 或向量库。最终锁定：**主库升级为 PostgreSQL 16 + pgvector**（结构化查询+语义检索统一在一套设施），**DuckDB 
## 知识页索引
- [[gitgithubcomtonyoorzData-Agentgit-我本地这个d|gitgithubcomtonyoorzData-Agentgit 我本地这个d]]
- [[skill-installerUserstonyorzcodexskillssy|skill-installerUserstonyorzcodexskillssy]]
- [[Conversation-info-untrusted-metadata-jso-Conversa|Conversation info untrusted metadata jso]]
- [[Explore-the-project-at-UserstonyorzData|Explore the project at UserstonyorzData-]]
- [[Successfully-changed-chat-title-to-Casua|Successfully changed chat title to Casua]]
- [[pgsql迁移与字段匹配|我现在pqsql 和sqlite一样看一下里边数据存储字段是匹配的么。 我想确保我之后迁移到pqsq]]
- [[研究任务-ontology本体在-data-agent-AI-数据智能中的应用|研究任务：ontology本体在 data agent AI 数据智能中的应用]]
- [[goal-全网深度分析我的项目里的agent-分析一下我这个智能问数agent如|goal 全网深度分析我的项目里的agent，分析一下我这个智能问数agent如]]
- [[octane数据下载与入库链路|你现在完整的查看一下我的项目，现在我是否是通过一键octane download把数据从octane]]
- [[前段设计还能更好么|前段设计还能更好么]]

