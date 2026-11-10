---
title: "Successfully changed chat title to Casua"
type: knowledge
source: "Claude-Code"
source_file: "10 Sources/raw/conversations/Claude-Code/Successfully-changed-chat-title-to-Casual-conversa.md"
compiled_at: 2026-07-15
compiler: claude-sonnet-5
tags:
  - compiled-knowledge
---

# Successfully changed chat title to Casua

> 编译自 [[10 Sources/raw/conversations/Claude-Code/Successfully-changed-chat-title-to-Casual-conversa.md]] 的完整对话。

## 核心问题

针对 **Data-Agent** 项目（一个面向汽车测试缺陷/Octane数据的 text-to-SQL 对话式 Agent，Python FastAPI 后端 + React/TypeScript 前端）完成三项任务：
1. 全面分析项目架构（模块、数据流、设计模式）
2. 生成 Mermaid 架构图
3. 加固 `agent/interpret/code_interpreter.py` 中的 Python 代码执行沙箱（因原有基于字符串黑名单的方案存在安全隐患）

## 关键结论

- **技术栈**：FastAPI 后端（`api/main.py`，默认端口 8100）+ Vite/React/TS 前端；规则模式为默认，设置 API Key 后可切换为 LLM 增强模式（智谱 GLM / DeepSeek）。
- **架构灵感来源**：WrenAI MDL（Ontology）、CHASE-SQL（多路径生成+执行引导选择）、MARS-SQL（结果校验+自修正）、BIRD-Interact（多轮对话上下文）、Palantir Ontology（本体建模）。
- **核心处理流水线**：`理解（term_resolver→entity_extractor→intent_detector）→ SQL生成（3条候选路径）→ 多路径执行比对 → 自修正（QueryFixer）→ 结果校验（ResultValidator）→ 叙事生成（Storyteller）`。
- **Ontology 是全局单一事实来源**：`agent/ontology/objects/*.yaml`（defect/project/testcase/defect_history/manual_run/team）驱动 schema、别名解析、类别分组、业务规则、治理约束，贯穿理解层、生成层、prompt构建、校验层。
- **NL2SQL 本质是模板填充而非 LLM 直接生成**：`NL2SQLEngine.query()`（`agent/sql_engine/generator.py:590`）通过 `DirectGenerator`/`DecomposedGenerator`/`PlanBasedGenerator` 生成3个候选SQL，由 `MultiPathExecutor` 执行并比较 `data_signature`，判定 UNANIMOUS(0.95)/MAJORITY(0.80)/DISAGREE（LLM仲裁或路径优先级回退：plan_based > decomposed > direct）。
- **降级设计彻底**：所有依赖LLM的路径都有规则回退（意图/实体提取纯正则、SQL模板化、code interpreter有 `_fallback_code`），可完全离线运行。
- **代码沙箱原方案存在弱点**：`FORBIDDEN_PATTERNS` 基于子串黑名单（如禁止 `"open("`, `"__import__"`, `"exec("` 等），易被绕过（如 `__builtins__`、`getattr` 等手法），仅适用于可信单用户场景。

## 操作要点

### 架构分析产出的核心文件/函数索引
- 入口：`api/main.py` — `POST /api/agent/query`(`:320`)、`GET /api/agent/stream`(`:444`)、`/api/agent/feedback`(`:485`)、`/api/agent/history`(`:515`)、`/api/agent/stats`(`:526`)；会话管理 `get_agent_for_session()`(`:162`)，字典 `_session_agents[session_id] -> ReActAgent`。
- 配置：`DB_PATH=data/agent_memory.db`（记忆/反馈）、`DATA_DB_PATH=resolve_data_db_path()`（业务数据）；`AGENT_MODE` env（默认 `llm`）。
- Agent Loop：`agent/agent_loop/loop.py` — `ReActAgent`，`_process_rule_based`(`:211`)、`_process_with_llm`(`:367`)，`MAX_STEPS=8`(`:73`)；`streaming.py` 的 `SSEEventStream` 转换 `StepType`→SSE事件。
- 工具集（7个，注册于 `registry.py:82`）：`query_defects`(`tools.py:81`)、`query_trend`(`:147`)、`get_distribution`/`get_ranking`(`:259,366`)、`search_similar`(`:459`)、`get_dashboard`(`:552`)、`analyze_data`(CodeInterpreterTool,`:635`)。
- 理解层：`term_resolver.py`（别名索引+longest-match+CJK感知+`category_groups`展开，`:101,164,229`）；`entity_extractor.py`（`:96,224,307`）；`intent_detector.py`（11种意图，`INTENT_RULES`表`:53`，`detect()`:`165`）。
- Ontology：`agent/ontology/engine.py`（`OntologyEngine`，`ObjectType`/`PropertyDef`/`LinkDef`/`MetricDef`/`CalibrationRule`/`Governance`），Defect对象含7条 `calibration_rules`（如 `cal_severity_not_matrix`、`cal_trend_uses_creation_time`、`cal_active_excludes_closed`）。
- SQL引擎：`agent/sql_engine/generator.py`（`NL2SQLEngine`）、`fixer.py`（`QueryFixer`，CHASE-SQL Algorithm 4，β=3重试，`_sql_looks_valid`阻止DROP/DELETE，`:75,305`）、`validator.py`（`ResultValidator`，MARS-SQL风格规则+LLM PASS/FAIL）、`selector.py`（`SQLSelector`，已废弃未使用）。
- 数据层：`agent/data/adapter.py`（仅SQLite实现，`resolve_data_db_path()`:`245`，`execute_query()`:`272`）；`value_retriever.py`（分层匹配：精确100→别名95→部分别名85+→rapidfuzz模糊≥65，`retrieve()`:`244`；`get_hints_for_question()`:`391`）。
- 学习/记忆：`query_memory.py`（`QueryMemory`，md5去重，`record()`:`222`，`retrieve_similar()`:`312`）；`semantic_matcher.py`（三层：embedding→TF-IDF(CJK bigram，从零实现)→Jaccard回退）；`feedback_store.py`（`get_weight_adjustments()`:`174`）。
- 对话上下文：`agent/conversation/context.py`（`TurnClassifier.classify()`:`127`，`ContextResolver.resolve()`:`231`，`SessionManager`:`493`，30分钟过期，仅内存不持久化）。
- 解读层：`agent/interpret/code_interpreter.py`（`CodeInterpreter`）、`storyteller.py`（`DataStoryteller`，`tell_count/tell_trend/tell_distribution/tell_ranking/tell_summary`）。
- LLM：`agent/llm/client.py`（`LLMClient`，`PROVIDER_CONFIG`:`58`，ZhiPu GLM `glm-4-flash`/DeepSeek `deepseek-chat`，均 `temperature=0.1, max_tokens=4096`；适配器 `as_agent_fn()`:`291`、`as_fixer_fn()`:`320`）。

### 代码沙箱加固任务（截断前状态）
- 已展示原始 `code_interpreter.py` 全文（第1-151行左右），准备针对其安全弱点进行加固：
  - `SAFE_IMPORTS`: `pandas, numpy, math, re, json, statistics, collections, itertools`
  - `FORBIDDEN_PATTERNS`: 子串黑名单形式，含 `import os/sys/subprocess/socket/urllib/requests/http/shutil/pickle/marshal/ctypes`、`__import__`、`open(`、`exec(`、`eval(`、`compile(`、`globals(`、`locals(`
  - `timeout=5`（构造函数默认参数）
  - 加固的具体实现方案在对话记录中被截断，**未给出**。

## 踩过的坑

1. **Schema/Ontology 漂移**：`agent/ontology/objects/defect.yaml` 中字段名（`assigned_ecu`, `name`, `problem_finder_team`）与 `agent/data/adapter.py` 实际生成的示例库列名（`ecu`, `summary`, `detected_by`）不一致，导致部分查询在示例DB上静默返回空结果。
2. **僵尸代码**：`SQLSelector`（`selector.py`）虽被 `__init__` 导入但实际未被 `NL2SQLEngine.query()` 使用（已被 `select_best()` + `MultiPathExecutor` 取代）；`PlanBasedGenerator` 与 `DecomposedGenerator` 的分解逻辑存在重叠。
3. **弱沙箱**：`code_interpreter.py` 的 `FORBIDDEN_PATTERNS` 是纯子串匹配黑名单，容易被 `__builtins__`、`getattr` 等手法绕过，不适合处理不可信输入。
4. **`_fallback_code`（`code_interpreter.py:233`）存在 f-string 隐患**：模板中嵌入 `{{`/`}}` 转义方式脆弱，自动生成代码将数据硬编码内联。
5. **CORS 配置不安全**：`main.py:262` 同时设置 `allow_origins=["*"]` 和 `allow_credentials=True`，属危险组合。
6. **对 Agent 步骤的正则解析脆弱**：`main.py:344-352` 通过正则解析中文格式的步骤内容（如"类型:"、"→ '...'"），属于脆弱的字符串刮取（string-scraping）。
7. **SQL 注入面**：`get_distribution`/`get_ranking`/`get_dashboard` 等工具通过 f-string 拼接 `filters` 字符串构建SQL（`tools.py:303-331, 417-422`），无参数化查询，依赖上游LLM/规则层不产生引号等特殊字符。
8. **会话不持久化**：`SessionManager` 仅内存存储，进程重启会丢失所有对话状态。
9. **无成本护栏**：`MAX_STEPS=8` 但没有 token 预算控制，每轮LLM迭代都是完整的 function-calling 往返。

## 待解决问题

- 代码沙箱加固的具体实现方案（对话在展示原文件源码后被截断，未给出加固后的完整代码/设计）。
- Schema/Ontology 字段名不一致问题尚未修复（对话中仅指出问题，未给出修复方案）。
- `
