---
title: "Explore the project at UserstonyorzData-"
type: knowledge
source: "Claude-Code"
source_file: "10 Sources/raw/conversations/Claude-Code/Explore-the-project-at-Users-tonyorz-Data-Agent-ve.md"
compiled_at: 2026-07-15
compiler: claude-sonnet-5
tags:
  - compiled-knowledge
---

# Explore the project at UserstonyorzData-

> 编译自 [[10 Sources/raw/conversations/Claude-Code/Explore-the-project-at-Users-tonyorz-Data-Agent-ve.md]] 的完整对话。

## 核心问题
对 `/Users/tonyorz/Data-Agent` 项目（一个面向缺陷/测试数据的 text-to-SQL Agent，代号 "Data-Agent"）进行彻底的架构探查与分析，要求覆盖：入口与运行时（FastAPI/api/main.py）、Agent 推理循环（agent/agent_loop/）、理解阶段（agent/understand/）、Ontology 数据模型（agent/ontology/）、SQL 引擎（agent/sql_engine/）、数据层（agent/data/）、学习/记忆（agent/learning/）、多轮对话上下文（agent/conversation/）、结果解读（agent/interpret/）、LLM 客户端（agent/llm/），以及端到端数据流、设计模式与优缺点，需给出具体 file:line 引用。

## 关键结论
（对话被截断，未看到最终的完整架构分析报告；以下为从已读取的源码片段中确认的具体事实）

- **项目结构**：根目录含 `agent/`（子模块：agent_loop, context, conversation, data, interpret, learning, llm, ontology, sql_engine, understand）、`api/`、`data/`、`frontend/`、`tests/`；另有设计文档 `AGENT_DESIGN_REVIEW.md`、`DUPLICATE_DEFECT_SEARCH_DESIGN.md`、`PHASE1_REPORT.md`~`PHASE6_REPORT.md`，表明项目按 Phase 1–6 迭代开发，Phase 1–4 已在 `api/main.py` 文档字符串中确认集成。
- **服务入口**：`api/main.py` 是 FastAPI 应用（title="Data-Agent API", version="1.0.0"），启动方式为 `python3 -m api.main` 或 `uvicorn api.main:app --host 0.0.0.0 --port 8100 --reload`。
- **REST/SSE 接口**（均以 `/api/agent/` 为前缀）：
  - `POST /query` — 同步查询（`QueryRequest{question, use_memory, stream, session_id}` → `QueryResponse{success, answer, steps, tools_used, sql_executed, story, memory_record_id, session_id, turn_type, resolved_question, total_time_ms}`）
  - `GET /stream` — SSE 流式查询，事件类型：start/thought/action/observation/final/done
  - `POST /feedback` — 用户反馈（up/down + note/correction）
  - `GET /history` — 查询历史（分页 limit 1-100）
  - `GET /stats` — 记忆与反馈统计（含 `weight_adjustments`）
  - `GET /health` — 健康检查，返回各 phase 开关状态与 LLM provider/model
  - `GET /tools` — 工具 schema 列表 + markdown 描述
  - `POST /session`、`DELETE /session/{id}`、`GET /sessions`、`GET /session/{id}` — 会话管理
  - `GET /examples` — 导出高分查询作为 few-shot 示例
- **单例/依赖管理**：模块级全局单例（`_ontology`, `_agent`, `_query_memory`, `_feedback_store`, `_storyteller`, `_llm_client`）+ 懒初始化 getter 函数；`_session_agents: Dict[str, Any]` 缓存每个 session 的独立 agent 实例，用于多轮对话的独立 `ConversationContext`。
- **Agent 创建逻辑**（`get_data_agent()` / `get_agent_for_session()`）：通过环境变量 `AGENT_MODE`（默认 `"llm"`）决定是否使用 `llm.as_agent_fn()` 作为 `llm_call_fn` 传入 `get_agent(ontology, db_path, llm_call_fn)`；否则走 rule-based 模式（`agent_fn=None`）。
- **数据库路径**：`DB_PATH`（记忆库）默认 `data/agent_memory.db`，可用环境变量 `DATA_AGENT_DB_PATH` 覆盖；`DATA_DB_PATH`（业务数据库）通过 `agent.data.adapter.resolve_data_db_path()` 解析，支持生产库 `local_data_rebuilt.db` 或开发环境自动生成含 500 条 mock 缺陷的 sample DB。
- **Storyteller 集成**：`DataStoryteller`（`agent/interpret/storyteller.py`）根据最后调用的工具名分发到不同叙事方法：`query_defects→tell_count`、`query_trend→tell_trend`、`get_distribution→tell_distribution`、`get_ranking→tell_ranking`、`get_dashboard→tell_summary`。
- **记忆写入**：查询成功且 `use_memory=True` 时，`QueryMemory.record()` 记录 question/sql/intent/result_summary/result_count/success。
- **CORS**：`allow_origins=["*"]`，代码注释标注生产环境应限制为已知 origin。
- **CLAUDE.md 行为准则**（约束本次探索/编码风格）：
  1. Think Before Coding — 显式陈述假设，多种理解方式并列呈现，不擅自选择
  2. Simplicity First — 只写解决问题所需的最少代码，不做超范围抽象/配置化
  3. Surgical Changes — 只改动必须改的代码，不清理无关的既有死代码（发现了要提及而非删除）
  4. Goal-Driven Execution — 把任务转为可验证目标，多步任务需列出 `Step → verify` 计划

## 操作要点
- 探索路径：先用文件树/`ls`/`find` 列出全部 `agent/`、`api/`、`tests/`、`frontend/` 下的文件路径，再逐个读取核心模块源码（如 `api/main.py`）。
- 关键待读文件清单（已列出但对话中未展示读取结果）：
  - `agent/agent_loop/loop.py`, `registry.py`, `tools.py`, `streaming.py`
  - `agent/understand/intent_detector.py`, `entity_extractor.py`, `term_resolver.py`
  - `agent/ontology/engine.py` + `objects/*.yaml`
  - `agent/sql_engine/generator.py`, `validator.py`, `fixer.py`, `selector.py`, `multi_executor.py`, `examples.py`
  - `agent/data/adapter.py`, `value_retriever.py`
  - `agent/learning/feedback_store.py`, `query_memory.py`, `semantic_matcher.py`
  - `agent/conversation/context.py`
  - `agent/interpret/code_interpreter.py`, `storyteller.py`
  - `agent/llm/client.py`
  - 对应测试文件命名规范：`tests/test_<module_name>.py`（如 `test_agent_loop.py`, `test_sql_engine.py`, `test_ontology_engine.py` 等），可作为理解各模块预期行为的补充依据。
- 前端结构线索：`frontend/src/App.tsx`, `main.tsx`, `api/client.ts`, `pages/AIChatPage.tsx`, `pages/StatsPanel.tsx`, `components/{FeedbackButtons,ChartRenderer,AgentStepDisplay,StoryCard}.tsx`，表明前端通过 `api/client.ts` 调用上述 REST/SSE 接口，页面分为聊天页与统计面板。

## 踩过的坑
（对话中未涉及——日志未展示实际调试或报错过程，仅为架构探查阶段）

## 待解决问题
- 对话日志被截断，未能获取到该 sub
