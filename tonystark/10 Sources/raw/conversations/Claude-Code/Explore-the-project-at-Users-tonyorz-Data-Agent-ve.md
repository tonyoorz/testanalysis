---
title: "Explore the project at /Users/tonyorz/Data-Agent very thorou…"
tool: Claude Code
session_id: agent-aea1f1bb0741c04cc
source_path: "/Users/tonyorz/.claude/projects/-Users-tonyorz-Data-Agent/49c2695b-d10e-4f75-8fbb-61181128fc96/subagents/agent-aea1f1bb0741c04cc.jsonl"
started_at: "2026-06-30T14:22:44.243Z"
user_turns: 38
assistant_turns: 12
tags:
  - ai-session
  - claude-code
---

# Explore the project at /Users/tonyorz/Data-Agent very thorou…

> 完整对话提取自 `/Users/tonyorz/.claude/projects/-Users-tonyorz-Data-Agent/49c2695b-d10e-4f75-8fbb-61181128fc96/subagents/agent-aea1f1bb0741c04cc.jsonl`
> 工具: Claude Code | 用户消息: 38 | 助手回答: 12

## 用户提问（完整）

### Q1

Explore the project at /Users/tonyorz/Data-Agent very thoroughly. I need a comprehensive architecture analysis.

This appears to be a text-to-SQL agent for defect/test data ("Data-Agent"). Please investigate and report:

1. **Entry points & runtime**: How does the app run? (api/main.py — FastAPI? endpoints, session API). How does the frontend (frontend/) talk to it?

2. **Agent loop & pipeline**: Read agent/agent_loop/loop.py, registry.py, tools.py. What is the agent's reasoning loop? What tools does it have? How does streaming work?

3. **Understanding stage**: agent/understand/ (intent_detector, entity_extractor, term_resolver) — what do these do, what's their output?

4. **Ontology**: agent/ontology/engine.py and objects/*.yaml — what's the data model (defect, project, testcase, etc.)? How is the ontology used?

5. **SQL engine**: agent/sql_engine/ (generator, validator, fixer, selector, multi_executor) — how does SQL generation, validation, fixing, multi-path execution work?

6. **Data layer**: agent/data/ (adapter, value_retriever) — what DB? schema? how does value retrieval work?

7. **Learning/memory**: agent/learning/ (feedback_store, query_memory, semantic_matcher) — how does memory persist, what's TF-IDF + embedding?

8. **Conversation context**: agent/conversation/context.py — multi-turn context.

9. **Interpretation**: agent/interpret/ (code_interpreter, storyteller) — Python code interpreter, result storytelling.

10. **LLM**: agent/llm/client.py — which providers (GLM, DeepSeek, etc.)?

11. **Cross-cutting**: How do these modules flow together end-to-end for a user query? What are the key abstractions, design patterns, and any notable strengths/weaknesses/tech-debt you observe?

Report findings as a structured architecture map with module responsibilities, key data flows, and design observations. Include file:line references for important pieces. Be thorough — read actual code, don't just guess from filenames.

### Q2

./tests/test_conversation_context.py
./tests/test_sql_engine.py
./tests/test_query_fixer.py
./tests/test_entity_extractor.py
./tests/test_intent_detector.py
./tests/test_multi_executor.py
./tests/test_value_retriever.py
./tests/test_llm_client.py
./tests/test_context_engine.py
./tests/test_agent_loop.py
./tests/test_phase4.py
./tests/test_agent_tools.py
./tests/test_validator.py
./tests/test_term_resolver.py
./tests/test_api.py
./tests/test_ontology_engine.py
./tests/test_semantic_memory.py
./tests/test_code_interpreter.py
./api/__init__.py
./api/main.py
./agent/llm/client.py
./agent/llm/__init__.py
./agent/context/__init__.py
./agent/context/engine.py
./agent/learning/__init__.py
./agent/learning/feedback_store.py
./agent/learning/query_memory.py
./agent/learning/semantic_matcher.py
./agent/understand/__init__.py
./agent/understand/term_resolver.py
./agent/understand/entity_extractor.py
./agent/understand/intent_detector.py
./agent/ontology/__init__.py
./agent/ontology/engine.py
./agent/agent_loop/registry.py
./agent/agent_loop/tools.py
./agent/agent_loop/__init__.py
./agent/agent_loop/loop.py
./agent/agent_loop/streaming.py
./agent/sql_engine/validator.py
./agent/sql_engine/fixer.py
./agent/sql_engine/selector.py
./agent/sql_engine/__init__.py
./agent/sql_engine/generator.py
./agent/sql_engine/examples.py
./agent/sql_engine/multi_executor.py
./agent/interpret/code_interpreter.py
./agent/interpret/storyteller.py
./agent/interpret/__init__.py
./agent/data/adapter.py
./agent/data/__init__.py
./agent/data/value_retriever.py
./agent/conversation/__init__.py
./agent/conversation/context.py
---FRONTEND---
frontend/vite.config.ts
frontend/src/App.tsx
frontend/src/main.tsx
frontend/src/vite-env.d.ts
frontend/dist/assets/index-BNzI80Jp.js
frontend/src/types/index.ts
frontend/src/components/FeedbackButtons.tsx
frontend/src/components/ChartRenderer.tsx
frontend/src/components/AgentStepDisplay.tsx
frontend/src/components/StoryCard.tsx
frontend/src/api/client.ts
frontend/src/pages/StatsPanel.tsx
frontend/src/pages/AIChatPage.tsx

### Q3

total 200
drwxr-xr-x   19 tonyorz  staff    608  6 30 20:21 .
drwxr-x---+ 177 tonyorz  staff   5664  6 30 22:22 ..
drwxr-xr-x   13 tonyorz  staff    416  6 30 22:22 .git
-rw-r--r--    1 tonyorz  staff    282  6 22 17:18 .gitignore
-rw-r--r--@   1 tonyorz  staff  24648  6 24 08:55 AGENT_DESIGN_REVIEW.md
-rw-r--r--    1 tonyorz  staff   2357  6 22 17:18 CLAUDE.md
-rw-r--r--    1 tonyorz  staff  12775  6 30 20:21 DUPLICATE_DEFECT_SEARCH_DESIGN.md
-rw-r--r--    1 tonyorz  staff   5933  6 22 17:18 PHASE1_REPORT.md
-rw-r--r--    1 tonyorz  staff   9036  6 22 17:18 PHASE2_REPORT.md
-rw-r--r--    1 tonyorz  staff   6976  6 22 17:18 PHASE3_REPORT.md
-rw-r--r--    1 tonyorz  staff   6193  6 22 17:18 PHASE4_REPORT.md
-rw-r--r--    1 tonyorz  staff   2894  6 22 17:18 PHASE5_REPORT.md
-rw-r--r--    1 tonyorz  staff   3378  6 22 17:18 PHASE6_REPORT.md
drwxr-xr-x   12 tonyorz  staff    384  6 22 17:18 agent
drwxr-xr-x    4 tonyorz  staff    128  6 22 17:18 api
drwxr-xr-x    4 tonyorz  staff    128  6 22 17:18 data
drwxr-xr-x   10 tonyorz  staff    320  6 22 17:18 frontend
-rw-r--r--@   1 tonyorz  staff     23  6 22 17:18 requirements-agent.txt
drwxr-xr-x   21 tonyorz  staff    672  6 22 17:18 tests
===
.
./.git
./agent
./agent/agent_loop
./agent/context
./agent/conversation
./agent/data
./agent/interpret
./agent/learning
./agent/llm
./agent/ontology
./agent/sql_engine
./agent/understand
./api
./data
./frontend
./frontend/dist
./frontend/node_modules
./frontend/src
./tests

### Q4

1	# CLAUDE.md
2	
3	Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.
4	
5	**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.
6	
7	## 1. Think Before Coding
8	
9	**Don't assume. Don't hide confusion. Surface tradeoffs.**
10	
11	Before implementing:
12	- State your assumptions explicitly. If uncertain, ask.
13	- If multiple interpretations exist, present them - don't pick silently.
14	- If a simpler approach exists, say so. Push back when warranted.
15	- If something is unclear, stop. Name what's confusing. Ask.
16	
17	## 2. Simplicity First
18	
19	**Minimum code that solves the problem. Nothing speculative.**
20	
21	- No features beyond what was asked.
22	- No abstractions for single-use code.
23	- No "flexibility" or "configurability" that wasn't requested.
24	- No error handling for impossible scenarios.
25	- If you write 200 lines and it could be 50, rewrite it.
26	
27	Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.
28	
29	## 3. Surgical Changes
30	
31	**Touch only what you must. Clean up only your own mess.**
32	
33	When editing existing code:
34	- Don't "improve" adjacent code, comments, or formatting.
35	- Don't refactor things that aren't broken.
36	- Match existing style, even if you'd do it differently.
37	- If you notice unrelated dead code, mention it - don't delete it.
38	
39	When your changes create orphans:
40	- Remove imports/variables/functions that YOUR changes made unused.
41	- Don't remove pre-existing dead code unless asked.
42	
43	The test: Every changed line should trace directly to the user's request.
44	
45	## 4. Goal-Driven Execution
46	
47	**Define success criteria. Loop until verified.**
48	
49	Transform tasks into verifiable goals:
50	- "Add validation" → "Write tests for invalid inputs, then make them pass"
51	- "Fix the bug" → "Write a test that reproduces it, then make it pass"
52	- "Refactor X" → "Ensure tests pass before and after"
53	
54	For multi-step tasks, state a brief plan:
55	```
56	1. [Step] → verify: [check]
57	2. [Step] → verify: [check]
58	3. [Step] → verify: [check]
59	```
60	
61	Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.
62	
63	---
64	
65	**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
66

### Q5

1	"""
2	Data-Agent API Server
3	
4	FastAPI 服务，集成 Phase 1-4 全部能力。
5	
6	启动:
7	    cd Data-Agent
8	    python3 -m api.main
9	
10	    或:
11	    uvicorn api.main:app --host 0.0.0.0 --port 8100 --reload
12	
13	接口:
14	    POST   /api/agent/query       — 同步查询
15	    GET    /api/agent/stream      — SSE 流式查询
16	    POST   /api/agent/feedback    — 用户反馈
17	    GET    /api/agent/history     — 查询历史
18	    GET    /api/agent/stats       — 记忆统计
19	    GET    /api/agent/health      — 健康检查
20	    GET    /api/agent/tools       — 工具列表
21	"""
22	
23	from __future__ import annotations
24	
25	import os
26	import sys
27	import json
28	import time
29	import asyncio
30	import logging
31	from pathlib import Path
32	from typing import Optional, Dict, Any, List
33	
34	from fastapi import FastAPI, HTTPException, Query as QueryParam
35	from fastapi.middleware.cors import CORSMiddleware
36	from fastapi.responses import StreamingResponse, JSONResponse
37	from pydantic import BaseModel, Field
38	
39	logger = logging.getLogger("data-agent")
40	logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
41	
42	# Ensure project root is importable
43	PROJECT_ROOT = Path(__file__).resolve().parent.parent
44	if str(PROJECT_ROOT) not in sys.path:
45	    sys.path.insert(0, str(PROJECT_ROOT))
46	
47	# Agent imports
48	from agent.ontology import get_ontology_engine
49	from agent.agent_loop.loop import get_agent, StepType
50	from agent.agent_loop.registry import build_default_registry
51	from agent.agent_loop.streaming import SSEEventStream
52	from agent.learning import QueryMemory, FeedbackStore
53	from agent.interpret.storyteller import DataStoryteller, StoryType
54	from agent.data.adapter import resolve_data_db_path, execute_query
55	from agent.llm import get_llm_client
56	
57	
58	# ============================================================================
59	# Config
60	# ============================================================================
61	
62	DB_PATH = os.environ.get("DATA_AGENT_DB_PATH", str(PROJECT_ROOT / "data" / "agent_memory.db"))
63	
64	# Resolve data source DB (sample or production)
65	# Production: set DATA_DB_PATH to point to local_data_rebuilt.db
66	# Development: auto-creates sample DB with 500 mock defects
67	DATA_DB_PATH = resolve_data_db_path()
68	
69	# Ensure data directory exists
70	os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
71	
72	# ============================================================================
73	# Singletons (lazy init)
74	# ============================================================================
75	
76	_ontology = None
77	_agent = None
78	_query_memory = None
79	_feedback_store = None
80	_storyteller = None
81	_llm_client = None
82	
83	
84	def get_ontology():
85	    global _ontology
86	    if _ontology is None:
87	        ontology_dir = PROJECT_ROOT / "agent" / "ontology"
88	        _ontology = get_ontology_engine(ontology_dir)
89	    return _ontology
90	
91	
92	def get_query_memory() -> QueryMemory:
93	    global _query_memory
94	    if _query_memory is None:
95	        _query_memory = QueryMemory(db_path=DB_PATH)
96	    return _query_memory
97	
98	
99	def get_feedback_store() -> FeedbackStore:
100	    global _feedback_store
101	    if _feedback_store is None:
102	        _feedback_store = FeedbackStore(db_path=DB_PATH)
103	    return _feedback_store
104	
105	
106	def get_storyteller() -> DataStoryteller:
107	    global _storyteller
108	    if _storyteller is None:
109	        _storyteller = DataStoryteller()
110	    return _storyteller
111	
112	
113	def get_llm():
114	    """Get or create the LLM client singleton"""
115	    global _llm_client
116	    if _llm_client is None:
117	        _llm_client = get_llm_client()
118	    return _llm_client
119	
120	
121	def get_data_agent():
122	    global _agent
123	    if _agent is None:
124	        ont = get_ontology()
125	
126	        # Determine mode from env
127	        agent_mode = os.environ.get("AGENT_MODE", "llm")
128	        llm = get_llm()
129	
130	        if agent_mode == "llm" and llm:
131	            # LLM-powered mode
132	            agent_fn = llm.as_agent_fn()
133	            logger.info("Agent starting in LLM mode")
134	        else:
135	            agent_fn = None
136	            logger.info("Agent starting in rule-based mode")
137	
138	        _agent = get_agent(
139	            ontology=ont,
140	            db_path=DATA_DB_PATH or None,
141	            llm_call_fn=agent_fn,
142	        )
143	    return _agent
144	
145	
146	# ============================================================================
147	# Session Manager Singleton
148	# ============================================================================
149	
150	_session_manager = None
151	_session_agents: Dict[str, Any] = {}  # session_id -> agent instance
152	
153	
154	def get_session_manager():
155	    global _session_manager
156	    if _session_manager is None:
157	        from agent.conversation import SessionManager
158	        _session_manager = SessionManager()
159	    return _session_manager
160	
161	
162	def get_agent_for_session(session_id: Optional[str]):
163	    """
164	    Get or create agent for a session.
165	    
166	    Each session needs its own agent instance with independent
167	    ConversationContext for multi-turn dialogue.
168	    """
169	    global _session_agents
170	    
171	    # If no session_id, use default agent (stateless, single-turn)
172	    if not session_id:
173	        return get_data_agent()
174	    
175	    # Check if we have an agent for this session
176	    if session_id in _session_agents:
177	        return _session_agents[session_id]
178	    
179	    # Create new agent for this session
180	    ont = get_ontology()
181	    agent_mode = os.environ.get("AGENT_MODE", "llm")
182	    llm = get_llm()
183	    
184	    agent_fn = None
185	    if agent_mode == "llm" and llm:
186	        agent_fn = llm.as_agent_fn()
187	    
188	    # Create agent
189	    agent = get_agent(
190	        ontology=ont,
191	        db_path=DATA_DB_PATH or None,
192	        llm_call_fn=agent_fn,
193	    )
194	    
195	    # Replace agent's conversation context with session-specific one
196	    sess_mgr = get_session_manager()
197	    agent.conversation = sess_mgr.get_session(session_id)
198	    
199	    _session_agents[session_id] = agent
200	    return agent
201	
202	
203	# ============================================================================
204	# Request / Response Models
205	# ============================================================================
206	
207	class QueryRequest(BaseModel):
208	    question: str = Field(..., description="用户自然语言问题", min_length=1, max_length=500)
209	    use_memory: bool = Field(True, description="是否使用查询记忆")
210	    stream: bool = Field(False, description="是否流式返回")
211	    session_id: Optional[str] = Field(None, description="会话 ID (多轮对话时传此值)")
212	
213	
214	class QueryResponse(BaseModel):
215	    success: bool
216	    answer: str
217	    steps: List[Dict[str, Any]] = []
218	    tools_used: List[str] = []
219	    sql_executed: List[str] = []
220	    story: Optional[Dict[str, Any]] = None
221	    memory_record_id: Optional[str] = None
222	    session_id: Optional[str] = None
223	    turn_type: Optional[str] = None
224	    resolved_question: Optional[str] = None
225	    total_time_ms: float = 0
226	
227	
228	class FeedbackRequest(BaseModel):
229	    query_memory_id: str = Field(..., description="查询记忆 ID")
230	    feedback: str = Field(..., description="'up' or 'down'")
231	    note: str = Field("", description="用户备注")
232	    correction: str = Field("", description="用户认为正确的方向")
233	
234	
235	class SessionCreateRequest(BaseModel):
236	    user_id: Optional[str] = Field(None, description="用户 ID")
237	    session_id: Optional[str] = Field(None, description="指定会话 ID（可选，不指定则自动生成）")
238	
239	
240	class SessionCreateResponse(BaseModel):
241	    session_id: str
242	    message: str
243	
244	
245	class FeedbackResponse(BaseModel):
246	    success: bool
247	    feedback_id: str
248	    message: str
249	
250	
251	# ============================================================================
252	# FastAPI App
253	# ============================================================================
254	
255	app = FastAPI(
256	    title="Data-Agent API",
257	    description="Ontology-driven intelligent data analysis agent",
258	    version="1.0.0",
259	)
260	
261	# CORS — allow frontend
262	app.add_middleware(
263	    CORSMiddleware,
264	    allow_origins=["*"],  # production: restrict to known origins
265	    allow_credentials=True,
266	    allow_methods=["*"],
267	    allow_headers=["*"],
268	)
269	
270	
271	# ============================================================================
272	# Routes
273	# ============================================================================
274	
275	@app.get("/api/agent/health")
276	async def health():
277	    """健康检查"""
278	    # Check LLM status
279	    llm = get_llm()
280	    llm_status = "disabled"
281	    if llm:
282	        llm_status = f"{llm.provider}/{llm.model}"
283	
284	    return {
285	        "status": "ok",
286	        "service": "data-agent",
287	        "version": "1.0.0",
288	        "phases": {
289	            "ontology": True,
290	            "nl2sql": True,
291	            "agent_loop": True,
292	            "learning": True,
293	            "storyteller": True,
294	            "llm": llm is not None,
295	        },
296	        "llm": {
297	            "provider": llm.provider if llm else "none",
298	            "model": llm.model if llm else "none",
299	            "status": llm_status,
300	        },
301	        "mode": os.environ.get("AGENT_MODE", "llm"),
302	    }
303	
304	
305	@app.get("/api/agent/tools")
306	async def list_tools():
307	    """列出可用工具"""
308	    ont = get_ontology()
309	    registry = build_default_registry(ontology=ont, db_path=DATA_DB_PATH or None)
310	    schemas = registry.get_schemas()
311	    descriptions = registry.get_descriptions()  # returns markdown string
312	    tool_names = [s.get("function", {}).get("name", "") if isinstance(s, dict) else "" for s in schemas]
313	    return {
314	        "tools": tool_names,
315	        "count": len(tool_names),
316	        "descriptions": descriptions,
317	    }
318	
319	
320	@app.post("/api/agent/query", response_model=QueryResponse)
321	async def query(req: QueryRequest):
322	    """
323	    同步查询接口
324	
325	    完整流程:
326	    1. (可选) 从 QueryMemory 检索相似历史
327	    2. Agent ReAct Loop 执行
328	    3. DataStoryteller 解读结果
329	    4. 存入 QueryMemory
330	    """
331	    t0 = time.time()
332	
333	    # Get or create session-specific agent
334	    agent = get_agent_for_session(req.session_id)
335	
336	    try:
337	        response = agent.process(req.question)
338	        
339	        # Extract turn type and resolved question from the agent
340	        turn_type = None
341	        resolved_question = None
342	        if response.steps:
343	            for step in response.steps:
344	                if step.content and "上下文解析" in step.content:
345	                    import re
346	                    m = re.search(r"类型: (\w+)", step.content)
347	                    if m:
348	                        turn_type = m.group(1)
349	                    m2 = re.search(r"→ '([^']+)'", step.content)
350	                    if m2:
351	                        resolved_question = m2.group(1)
352	                    break
353	
354	        # Build story if we have data
355	        story = None
356	        teller = get_storyteller()
357	
358	        # Determine story type from response
359	        tools_used = response.tools_used
360	        if response.success and response.steps:
361	            last_tool = tools_used[-1] if tools_used else ""
362	            if "query_defects" in last_tool:
363	                count = _extract_count(response.answer)
364	                if count is not None:
365	                    story = teller.tell_count(count).to_dict()
366	            elif "query_trend" in last_tool:
367	                for step in response.steps:
368	                    if step.step_type == StepType.OBSERVATION and step.tool_output and step.tool_output.data:
369	                        rows = extract_rows(step.tool_output.data)
370	                        if rows:
371	                            story = teller.tell_trend(rows).to_dict()
372	                            break
373	            elif "get_distribution" in last_tool:
374	                for step in response.steps:
375	                    if step.step_type == StepType.OBSERVATION and step.tool_output and step.tool_output.data:
376	                        rows = extract_rows(step.tool_output.data)
377	                        if rows:
378	                            story = teller.tell_distribution(rows, dimension="结果").to_dict()
379	                            break
380	            elif "get_ranking" in last_tool:
381	                for step in response.steps:
382	                    if step.step_type == StepType.OBSERVATION and step.tool_output and step.tool_output.data:
383	                        rows = extract_rows(step.tool_output.data)
384	                        if rows:
385	                            story = teller.tell_ranking(rows, rank_by="排名维度").to_dict()
386	                            break
387	            elif "get_dashboard" in last_tool:
388	                stats = {"total": 0, "active": 0, "critical": 0, "resolved": 0}
389	                for step in response.steps:
390	                    if step.step_type == StepType.OBSERVATION and step.tool_output and step.tool_output.data:
391	                        rows = extract_rows(step.tool_output.data)
392	                        for row in rows:
393	                            if isinstance(row, dict):
394	                                stats["total"] += row.get("count", 0)
395	                story = teller.tell_summary(stats).to_dict()
396	
397	        # Record to memory
398	        memory_id = None
399	        if req.use_memory and response.success:
400	            mem = get_query_memory()
401	            sql_list = response.sql_executed
402	            memory_id = mem.record(
403	                question=req.question,
404	                sql=sql_list[0] if sql_list else "",
405	                intent=response.steps[0].tool_name if response.steps else "",
406	                result_summary=response.answer[:200],
407	                result_count=_extract_count(response.answer) or 0,
408	                success=response.success,
409	            )
410	
411	        elapsed = (time.time() - t0) * 1000
412	
413	        return QueryResponse(
414	            success=response.success,
415	            answer=response.answer,
416	            steps=[{
417	                "type": s.step_type.value,
418	                "content": s.content,
419	                "tool": s.tool_name,
420	                "tool_input": s.tool_input,
421	                "tool_output": s.tool_output.data if s.tool_output else None,
422	            } for s in response.steps],
423	            tools_used=tools_used,
424	            sql_executed=response.sql_executed,
425	            story=story,
426	            memory_record_id=memory_id,
427	            session_id=req.session_id,
428	            turn_type=turn_type,
429	            resolved_question=resolved_question,
430	            total_time_ms=round(elapsed, 1),
431	        )
432	
433	    except Exception as e:
434	        elapsed = (time.time() - t0) * 1000
435	        import traceback
436	        traceback.print_exc()
437	        return QueryResponse(
438	            success=False,
439	            answer=f"查询失败: {str(e)}",
440	            total_time_ms=round(elapsed, 1),
441	        )
442	
443	
444	@app.get("/api/agent/stream")
445	async def stream_query(
446	    question: str = QueryParam(..., description="用户问题"),
447	):
448	    """
449	    SSE 流式查询接口
450	
451	    事件类型:
452	    - start: 查询开始
453	    - thought: Agent 思考
454	    - action: 工具调用
455	    - observation: 结果观察
456	    - final: 最终回答
457	    - done: 结束
458	    """
459	    async def event_generator():
460	        agent = get_data_agent()
461	
462	        # start event
463	        yield f"event: start\ndata: {json.dumps({'question': question, 'timestamp': time.time()})}\n\n"
464	
465	        try:
466	            for event in agent.process_stream(question):
467	                yield f"event: {event.event_type}\ndata: {json.dumps(event.data, ensure_ascii=False, default=str)}\n\n"
468	        except Exception as e:
469	            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
470	
471	        # done event
472	        yield f"event: done\ndata: {json.dumps({'timestamp': time.time()})}\n\n"
473	
474	    return StreamingResponse(
475	        event_generator(),
476	        media_type="text/event-stream",
477	        headers={
478	            "Cache-Control": "no-cache",
479	            "Connection": "keep-alive",
480	            "X-Accel-Buffering": "no",
481	        },
482	    )
483	
484	
485	@app.post("/api/agent/feedback", response_model=FeedbackResponse)
486	async def feedback(req: FeedbackRequest):
487	    """用户反馈接口"""
488	    if req.feedback not in ("up", "down"):
489	        raise HTTPException(status_code=400, detail="feedback must be 'up' or 'down'")
490	
491	    mem = get_query_memory()
492	    fb = get_feedback_store()
493	
494	    # Verify the query memory exists
495	    record = mem.get_by_id(req.query_memory_id)
496	    if not record:
497	        raise HTTPException(status_code=404, detail="Query memory record not found")
498	
499	    fid = fb.record(
500	        query_memory_id=req.query_memory_id,
501	        feedback_type=req.feedback,
502	        note=req.note,
503	        question=record.question,
504	        sql=record.sql,
505	        correction=req.correction,
506	    )
507	
508	    return FeedbackResponse(
509	        success=True,
510	        feedback_id=fid,
511	        message=f"Feedback '{req.feedback}' recorded",
512	    )
513	
514	
515	@app.get("/api/agent/history")
516	async def history(limit: int = QueryParam(20, ge=1, le=100)):
517	    """查询历史记录"""
518	    mem = get_query_memory()
519	    records = mem.get_recent(limit=limit)
520	    return {
521	        "records": [r.to_dict() for r in records],
522	        "count": len(records),
523	    }
524	
525	
526	@app.get("/api/agent/stats")
527	async def stats():
528	    """记忆和反馈统计"""
529	    mem = get_query_memory()
530	    fb = get_feedback_store()
531	
532	    mem_stats = mem.get_statistics()
533	    fb_stats = fb.get_statistics()
534	
535	    return {
536	        "memory": mem_stats,
537	        "feedback": fb_stats,
538	        "weight_adjustments": fb.get_weight_adjustments(),
539	    }
540	
541	
542	@app.post("/api/agent/session", response_model=SessionCreateResponse)
543	async def create_session(req: SessionCreateRequest):
544	    """创建新会话（多轮对话）"""
545	    import uuid
546	    session_id = req.session_id or str(uuid.uuid4())
547	    
548	    # Get or create session
549	    sess_mgr = get_session_manager()
550	    ctx = sess_mgr.get_session(session_id)
551	    
552	    return SessionCreateResponse(
553	        session_id=session_id,
554	        message=f"会话 {session_id} 已创建",
555	    )
556	
557	
558	@app.delete("/api/agent/session/{session_id}")
559	async def delete_session(session_id: str):
560	    """删除会话"""
561	    sess_mgr = get_session_manager()
562	    sess_mgr.remove_session(session_id)
563	    
564	    # Remove cached agent
565	    global _session_agents
566	    _session_agents.pop(session_id, None)
567	    
568	    return {"message": f"会话 {session_id} 已删除"}
569	
570	
571	@app.get("/api/agent/sessions")
572	async def list_sessions():
573	    """列出活跃会话"""
574	    sess_mgr = get_session_manager()
575	    active = sess_mgr.get_active_sessions()
576	    
577	    # Get turn counts for each session
578	    result = []
579	    for sid in active:
580	        ctx = sess_mgr.get_session(sid)
581	        result.append({
582	            "session_id": sid,
583	            "turn_count": len(ctx.history),
584	            "last_turn": ctx.history[-1]["question"] if ctx.history else None,
585	        })
586	    
587	    return {"sessions": result, "count": len(result)}
588	
589	
590	@app.get("/api/agent/session/{session_id}")
591	async def get_session(session_id: str):
592	    """获取会话详情"""
593	    sess_mgr = get_session_manager()
594	    try:
595	        ctx = sess_mgr.get_session(session_id)
596	        return {
597	            "session_id": session_id,
598	            "turn_count": len(ctx.history),
599	            "history": ctx.history,
600	        }
601	    except Exception:
602	        raise HTTPException(status_code=404, detail="会话不存在")
603	
604	
605	@app.get("/api/agent/examples")
606	async def examples(limit: int = QueryParam(30, ge=1, le=100)):
607	    """导出高分查询为 few-shot 示例"""
608	    mem = get_query_memory()
609	    data = mem.export_examples(limit=limit)
610	    return {
611	        "examples": data,
612	        "count": len(data),
613	    }
614	
615	
616	# ============================================================================
617	# LLM Management
618	# ============================================================================
619	
620	@app.get("/api/agent/llm/status")
621	async def llm_status():
622	    """查看 LLM 状态"""
623	    llm = get_llm()
624	    if llm is None:
625	        return {
626	            "enabled": False,
627	            "provider": "none",
628	            "model": "none",
629	            "message": "LLM 未配置。设置 AGENT_LLM_PROVIDER 和 API key 启用。",
630	        }
631	    return {
632	        "enabled": True,
633	        "provider": llm.provider,
634	        "model": llm.model,
635	        "base_url": llm.base_url,
636	        "agent_mode": os.environ.get("AGENT_MODE", "llm"),
637	    }
638	
639	
640	@app.post("/api/agent/llm/test")
641	async def llm_test():
642	    """测试 LLM 连通性"""
643	    llm = get_llm()
644	    if llm is None:
645	        return {"success": False, "error": "LLM not configured"}
646	
647	    ok = llm.health_check()
648	    return {
649	        "success": ok,
650	        "provider": llm.provider,
651	        "model": llm.model,
652	        "message": "LLM 响应正常" if ok else "LLM 无响应",
653	    }
654	
655	
656	@app.get("/api/agent/values/stats")
657	async def value_stats():
658	    """查看值索引统计"""
659	    from agent.data.value_retriever import get_value_retriever
660	    vr = get_value_retriever(db_path=DATA_DB_PATH or None, ontology=get_ontology())
661	    return vr.stats()
662	
663	
664	@app.get("/api/agent/values/search")
665	async def value_search(
666	    q: str = QueryParam(..., description="搜索文本"),
667	    field: Optional[str] = QueryParam(None, description="限定字段"),
668	):
669	    """搜索数据库值 (Value Retrieval)"""
670	    from agent.data.value_retriever import get_value_retriever
671	    vr = get_value_retriever(db_path=DATA_DB_PATH or None, ontology=get_ontology())
672	    r = vr.retrieve(q, field=field)
673	    return {
674	        "query": q,
675	        "matches": [
676	            {"value": m.value, "field": m.field, "score": m.score, "source": m.source}
677	            for m in r.matches
678	        ],
679	    }
680	
681	
682	# ============================================================================
683	# Helpers
684	# ============================================================================
685	
686	def _extract_count(text: str) -> Optional[int]:
687	    """从回答文本中提取数字"""
688	    import re
689	    # Match patterns like "共有 42 个" or "= 42" or "总计 42"
690	    patterns = [
691	        r'(\d+)\s*个',
692	        r'共\s*(\d+)',
693	        r'总计\s*(\d+)',
694	        r'[:：]\s*(\d+)',
695	        r'=\s*(\d+)',
696	        r'\b(\d+)\b',
697	    ]
698	    for pattern in patterns:
699	        match = re.search(pattern, text)
700	        if match:
701	            try:
702	                return int(match.group(1))
703	            except ValueError:
704	                continue
705	    return None
706	
707	
708	def extract_rows(data) -> list:
709	    """从 tool_output.data 提取 rows，兼容 list 和 dict 格式"""
710	    if isinstance(data, list):
711	        return data
712	    if isinstance(data, dict):
713	        if "rows" in data:
714	            return data["rows"]
715	        if "data" in data:
716	            return data["data"]
717	        return [data]
718	    return []
719	
720	
721	# ============================================================================
722	# Main entry
723	# ============================================================================
724	
725	if __name__ == "__main__":
726	    import uvicorn
727	    uvicorn.run(
728	        "api.main:app",
729	        host="0.0.0.0",
730	        port=int(os.environ.get("PORT", 8100)),
731	        reload=True,
732	    )
733

### Q6

1	"""ReAct Agent Loop - Thought/Action/Observation reasoning cycle
2	
3	Implements the ReAct pattern:
4	1. Thought: reason about what to do next
5	2. Action: call a tool
6	3. Observation: process the result
7	4. Repeat until final answer can be given
8	
9	The loop supports both:
10	- Rule-based mode (deterministic tool selection)
11	- LLM-based mode (dynamic reasoning via function calling)
12	"""
13	
14	import time
15	import json
16	from typing import Dict, List, Optional, Any, Callable, Generator
17	from dataclasses import dataclass, field
18	from enum import Enum
19	
20	from agent.agent_loop.tools import AgentTool, ToolResult
21	from agent.agent_loop.registry import ToolRegistry, build_default_registry
22	from agent.ontology import OntologyEngine, get_ontology_engine
23	from agent.sql_engine.generator import NL2SQLEngine
24	from agent.understand.intent_detector import QueryIntent
25	
26	
27	class StepType(Enum):
28	    """Types of steps in the agent loop"""
29	    THOUGHT = "thought"
30	    ACTION = "action"
31	    OBSERVATION = "observation"
32	    FINAL = "final"
33	    ERROR = "error"
34	
35	
36	@dataclass
37	class AgentStep:
38	    """A single step in the agent loop"""
39	    step_type: StepType
40	    content: str                 # Human-readable content
41	    tool_name: str = ""          # Which tool was called (for ACTION)
42	    tool_input: Dict = field(default_factory=dict)  # Tool parameters
43	    tool_output: Optional[ToolResult] = None         # Tool result
44	    timestamp: float = field(default_factory=time.time)
45	
46	
47	@dataclass
48	class AgentResponse:
49	    """Final response from the agent"""
50	    answer: str                        # Final answer text
51	    steps: List[AgentStep] = field(default_factory=list)  # All steps taken
52	    tools_used: List[str] = field(default_factory=list)   # Tool names used
53	    sql_executed: List[str] = field(default_factory=list) # SQL queries run
54	    total_time_ms: float = 0.0
55	    success: bool = True
56	    error: str = ""
57	
58	
59	class ReActAgent:
60	    """
61	    ReAct Agent - reasons and acts in a loop.
62	
63	    In rule-based mode, the agent uses deterministic logic to:
64	    1. Understand the question (intent + entities)
65	    2. Select the right tool
66	    3. Execute and collect results
67	    4. Format the final answer
68	
69	    In LLM mode (when llm_call_fn is provided), the agent uses
70	    LLM reasoning for tool selection and answer generation.
71	    """
72	
73	    MAX_STEPS = 8  # Safety limit
74	
75	    def __init__(
76	        self,
77	        registry: Optional[ToolRegistry] = None,
78	        ontology: Optional[OntologyEngine] = None,
79	        db_path: Optional[str] = None,
80	        llm_call_fn: Optional[Callable] = None,
81	    ):
82	        self.ontology = ontology or get_ontology_engine()
83	        self.db_path = db_path
84	        self.llm_call_fn = llm_call_fn  # Optional: fn(messages, tools) -> response
85	
86	        if registry:
87	            self.registry = registry
88	        else:
89	            # Get fixer_fn for NL2SQL self-correction
90	            fixer_fn = None
91	            if llm_call_fn:
92	                # Adapt agent_fn to fixer_fn format (str -> str)
93	                from agent.llm import get_llm_client
94	                llm = get_llm_client()
95	                if llm:
96	                    fixer_fn = llm.as_fixer_fn()
97	
98	            self.registry = build_default_registry(
99	                ontology=self.ontology,
100	                db_path=db_path,
101	                llm_call_fn=fixer_fn,
102	            )
103	
104	        self.nl2sql = NL2SQLEngine(ontology=ontology, db_path=db_path)
105	
106	        # Conversation context for multi-turn dialogue
107	        from agent.conversation import ConversationContext
108	        resolve_fn = None
109	        if llm_call_fn:
110	            from agent.llm import get_llm_client
111	            llm_for_ctx = get_llm_client()
112	            if llm_for_ctx:
113	                # Adapt chat_text to ContextResolver's expected signature
114	                # ContextResolver calls: fn(messages=[...], tools=[])
115	                # chat_text expects: fn(prompt, system)
116	                def resolve_adapter(messages, tools):
117	                    prompt = ""
118	                    system = ""
119	                    for msg in messages:
120	                        if msg.get("role") == "system":
121	                            system = msg.get("content", "")
122	                        elif msg.get("role") == "user":
123	                            prompt = msg.get("content", "")
124	                    try:
125	                        return llm_for_ctx.chat_text(prompt=prompt, system=system)
126	                    except Exception:
127	                        return None
128	                resolve_fn = resolve_adapter
129	        self.conversation = ConversationContext(llm_call_fn=resolve_fn)
130	
131	    def process(self, question: str) -> AgentResponse:
132	        """
133	        Process a user question through the ReAct loop.
134	
135	        Args:
136	            question: User's natural language question
137	
138	        Returns:
139	            AgentResponse with answer, steps, and metadata
140	        """
141	        start_time = time.time()
142	        steps: List[AgentStep] = []
143	        tools_used: List[str] = []
144	        sql_executed: List[str] = []
145	
146	        # Resolve multi-turn context
147	        turn_type = self.conversation.classify(question)
148	        resolved_question = self.conversation.resolve(question)
149	        if resolved_question != question:
150	            steps.append(AgentStep(
151	                step_type=StepType.THOUGHT,
152	                content=f"上下文解析: '{question}' → '{resolved_question}' (类型: {turn_type.value})"
153	            ))
154	
155	        try:
156	            if self.llm_call_fn:
157	                # LLM-based mode
158	                response = self._process_with_llm(resolved_question, steps, tools_used, sql_executed)
159	            else:
160	                # Rule-based mode
161	                response = self._process_rule_based(resolved_question, steps, tools_used, sql_executed)
162	        except Exception as e:
163	            response = AgentResponse(
164	                answer=f"处理问题时发生错误: {str(e)}",
165	                steps=steps,
166	                tools_used=tools_used,
167	                sql_executed=sql_executed,
168	                success=False,
169	                error=str(e),
170	            )
171	
172	        elapsed = (time.time() - start_time) * 1000
173	        response.steps = steps
174	        response.tools_used = tools_used
175	        response.sql_executed = sql_executed
176	        response.total_time_ms = elapsed
177	
178	        # Record turn in conversation history
179	        result_summary = response.answer[:200] if response.success else ""
180	        self.conversation.add_turn(
181	            question=question,
182	            resolved_question=resolved_question,
183	            sql=sql_executed[0] if sql_executed else "",
184	            result_summary=result_summary,
185	        )
186	
187	        return response
188	
189	    def process_stream(self, question: str) -> Generator[AgentStep, None, None]:
190	        """
191	        Process question and yield steps as they happen (for SSE streaming).
192	
193	        Yields AgentStep objects that can be converted to SSE events.
194	        """
195	        try:
196	            if self.llm_call_fn:
197	                steps_gen = self._stream_with_llm(question)
198	            else:
199	                steps_gen = self._stream_rule_based(question)
200	
201	            for step in steps_gen:
202	                yield step
203	        except Exception as e:
204	            yield AgentStep(
205	                step_type=StepType.ERROR,
206	                content=f"错误: {str(e)}"
207	            )
208	
209	    # ==================== Rule-Based Mode ====================
210	
211	    def _process_rule_based(
212	        self,
213	        question: str,
214	        steps: List[AgentStep],
215	        tools_used: List[str],
216	        sql_executed: List[str],
217	    ) -> AgentResponse:
218	        """Rule-based processing: deterministic tool selection"""
219	        from agent.understand.entity_extractor import get_entity_extractor
220	        from agent.understand.intent_detector import get_intent_detector, QueryIntent
221	
222	        # Step 1: Analyze question
223	        extractor = get_entity_extractor(self.ontology)
224	        entities = extractor.extract(question)
225	        intent = get_intent_detector().detect(question, entities)
226	
227	        steps.append(AgentStep(
228	            step_type=StepType.THOUGHT,
229	            content=(
230	                f"分析问题: 意图={intent.primary.value}, 置信度={intent.confidence:.1%}\n"
231	                f"提取实体: {self._format_entities(entities)}\n"
232	                f"选择工具: {self._select_tool_name(intent.primary)}"
233	            )
234	        ))
235	
236	        # Step 2: Select and execute tool
237	        tool_name = self._select_tool_name(intent.primary)
238	        tool = self.registry.get(tool_name)
239	
240	        if not tool:
241	            steps.append(AgentStep(
242	                step_type=StepType.ERROR,
243	                content=f"工具未找到: {tool_name}"
244	            ))
245	            return AgentResponse(
246	                answer=f"无法处理意图类型: {intent.primary.value}",
247	                success=False,
248	            )
249	
250	        # Execute tool
251	        result = self._execute_tool_for_intent(
252	            tool_name, tool, question, intent, entities
253	        )
254	
255	        tools_used.append(tool_name)
256	        if result.sql:
257	            sql_executed.append(result.sql)
258	
259	        steps.append(AgentStep(
260	            step_type=StepType.ACTION,
261	            content=f"调用工具: {tool_name}",
262	            tool_name=tool_name,
263	            tool_input={"question": question},
264	        ))
265	
266	        steps.append(AgentStep(
267	            step_type=StepType.OBSERVATION,
268	            content=result.summary,
269	            tool_output=result,
270	        ))
271	
272	        # Step 3: Determine if we need a follow-up tool
273	        if intent.primary == QueryIntent.SUMMARY:
274	            # For summaries, also get distribution
275	            dist_result = self.registry.execute(
276	                "get_distribution", group_by="severity"
277	            )
278	            if dist_result.success:
279	                tools_used.append("get_distribution")
280	                steps.append(AgentStep(
281	                    step_type=StepType.OBSERVATION,
282	                    content=f"补充数据 - 严重度分布: {dist_result.summary}",
283	                    tool_output=dist_result,
284	                ))
285	
286	        # Step 4: Generate final answer
287	        answer = self._format_answer(question, intent, result, steps)
288	
289	        steps.append(AgentStep(
290	            step_type=StepType.FINAL,
291	            content=answer
292	        ))
293	
294	        return AgentResponse(answer=answer, success=True)
295	
296	    def _select_tool_name(self, intent) -> str:
297	        """Map intent to tool name"""
298	        mapping = {
299	            QueryIntent.COUNT: "query_defects",
300	            QueryIntent.TREND: "query_trend",
301	            QueryIntent.RANKING: "get_ranking",
302	            QueryIntent.DISTRIBUTION: "get_distribution",
303	            QueryIntent.COMPARISON: "get_distribution",
304	            QueryIntent.DETAIL_LIST: "query_defects",
305	            QueryIntent.SEARCH_SIMILAR: "search_similar",
306	            QueryIntent.RISK_ANALYSIS: "query_defects",
307	            QueryIntent.SUMMARY: "get_dashboard",
308	            QueryIntent.ROOT_CAUSE: "query_defects",
309	            QueryIntent.STATUS_CHECK: "query_defects",
310	        }
311	        return mapping.get(intent, "query_defects")
312	
313	    def _execute_tool_for_intent(self, tool_name: str, tool: AgentTool,
314	                                  question: str, intent, entities) -> ToolResult:
315	        """Execute the selected tool with appropriate parameters"""
316	        if tool_name == "query_defects":
317	            return self.registry.execute("query_defects", question=question)
318	
319	        elif tool_name == "query_trend":
320	            return self.registry.execute("query_trend", question=question)
321	
322	        elif tool_name == "get_ranking":
323	            rank_by = "assigned_ecu"
324	            for e in entities.entities:
325	                if e.entity_type in ("project", "ecu", "team", "severity"):
326	                    rank_by = e.field
327	                    break
328	            limit = 10
329	            limit_entity = entities.get_first("limit")
330	            if limit_entity:
331	                limit = int(limit_entity.value)
332	            return self.registry.execute("get_ranking", rank_by=rank_by, limit=limit)
333	
334	        elif tool_name == "get_distribution":
335	            group_by = "project"
336	            for e in entities.entities:
337	                if e.entity_type in ("project", "ecu", "severity", "status",
338	                                     "team", "test_phase", "aida"):
339	                    group_by = e.field
340	                    break
341	            # Check question for dimension hints
342	            dim_hints = {
343	                "项目": "project", "ECU": "assigned_ecu", "严重": "severity",
344	                "状态": "status_phase", "团队": "team", "阶段": "phase",
345	            }
346	            for keyword, field_name in dim_hints.items():
347	                if keyword in question:
348	                    group_by = field_name
349	                    break
350	            return self.registry.execute("get_distribution", group_by=group_by)
351	
352	        elif tool_name == "search_similar":
353	            return self.registry.execute("search_similar", query=question)
354	
355	        elif tool_name == "get_dashboard":
356	            project = ""
357	            for e in entities.entities:
358	                if e.entity_type == "project":
359	                    project = e.value
360	                    break
361	            return self.registry.execute("get_dashboard", project=project)
362	
363	        return self.registry.execute("query_defects", question=question)
364	
365	    # ==================== LLM-Based Mode ====================
366	
367	    def _process_with_llm(
368	        self,
369	        question: str,
370	        steps: List[AgentStep],
371	        tools_used: List[str],
372	        sql_executed: List[str],
373	    ) -> AgentResponse:
374	        """LLM-based processing: dynamic tool selection via function calling"""
375	        messages = [
376	            {
377	                "role": "system",
378	                "content": self._build_system_prompt()
379	            },
380	            {
381	                "role": "user",
382	                "content": question
383	            }
384	        ]
385	
386	        tool_schemas = self.registry.get_schemas()
387	
388	        for _ in range(self.MAX_STEPS):
389	            # Call LLM
390	            llm_response = self.llm_call_fn(messages, tool_schemas)
391	
392	            if llm_response.get("tool_calls"):
393	                # LLM wants to call tools
394	                for tool_call in llm_response["tool_calls"]:
395	                    tool_name = tool_call["name"]
396	                    tool_args = tool_call["arguments"]
397	
398	                    steps.append(AgentStep(
399	                        step_type=StepType.THOUGHT,
400	                        content=tool_call.get("thought", f"使用 {tool_name}")
401	                    ))
402	                    steps.append(AgentStep(
403	                        step_type=StepType.ACTION,
404	                        content=f"调用 {tool_name}({tool_args})",
405	                        tool_name=tool_name,
406	                        tool_input=tool_args,
407	                    ))
408	
409	                    result = self.registry.execute(tool_name, **tool_args)
410	                    tools_used.append(tool_name)
411	                    if result.sql:
412	                        sql_executed.append(result.sql)
413	
414	                    steps.append(AgentStep(
415	                        step_type=StepType.OBSERVATION,
416	                        content=result.summary,
417	                        tool_output=result,
418	                    ))
419	
420	                    # Add to conversation
421	                    messages.append({
422	                        "role": "tool",
423	                        "name": tool_name,
424	                        "content": json.dumps({
425	                            "success": result.success,
426	                            "summary": result.summary,
427	                            "data": result.data[:10] if isinstance(result.data, list) else result.data,
428	                        }, ensure_ascii=False, default=str)
429	                    })
430	            else:
431	                # LLM gives final answer
432	                answer = llm_response.get("content", "")
433	                steps.append(AgentStep(
434	                    step_type=StepType.FINAL,
435	                    content=answer
436	                ))
437	                return AgentResponse(answer=answer, success=True)
438	
439	        # Max steps reached
440	        steps.append(AgentStep(
441	            step_type=StepType.FINAL,
442	            content="达到最大步数限制，基于已有信息生成回答"
443	        ))
444	        return AgentResponse(
445	            answer="基于已有信息: " + steps[-2].content if len(steps) >= 2 else "无法回答",
446	            success=True,
447	        )
448	
449	    # ==================== Streaming ====================
450	
451	    def _stream_rule_based(self, question: str) -> Generator[AgentStep, None, None]:
452	        """Stream rule-based processing"""
453	        from agent.understand.entity_extractor import get_entity_extractor
454	        from agent.understand.intent_detector import get_intent_detector
455	
456	        entities = get_entity_extractor(self.ontology).extract(question)
457	        intent = get_intent_detector().detect(question, entities)
458	
459	        yield AgentStep(
460	            step_type=StepType.THOUGHT,
461	            content=f"🤔 意图: {intent.primary.value} | 实体: {self._format_entities(entities)}"
462	        )
463	
464	        tool_name = self._select_tool_name(intent.primary)
465	        result = self._execute_tool_for_intent(
466	            tool_name, self.registry.get(tool_name), question, intent, entities
467	        )
468	
469	        yield AgentStep(
470	            step_type=StepType.ACTION,
471	            content=f"🔧 调用 {tool_name}",
472	            tool_name=tool_name,
473	        )
474	
475	        yield AgentStep(
476	            step_type=StepType.OBSERVATION,
477	            content=f"📊 {result.summary}",
478	            tool_output=result,
479	        )
480	
481	        answer = self._format_answer(question, intent, result, [])
482	        yield AgentStep(
483	            step_type=StepType.FINAL,
484	            content=answer
485	        )
486	
487	    def _stream_with_llm(self, question: str) -> Generator[AgentStep, None, None]:
488	        """Stream LLM-based processing"""
489	        # Similar to _process_with_llm but yields steps
490	        messages = [
491	            {"role": "system", "content": self._build_system_prompt()},
492	            {"role": "user", "content": question}
493	        ]
494	        tool_schemas = self.registry.get_schemas()
495	
496	        for _ in range(self.MAX_STEPS):
497	            llm_response = self.llm_call_fn(messages, tool_schemas)
498	
499	            if llm_response.get("tool_calls"):
500	                for tool_call in llm_response["tool_calls"]:
501	                    tool_name = tool_call["name"]
502	                    tool_args = tool_call["arguments"]
503	
504	                    yield AgentStep(
505	                        step_type=StepType.THOUGHT,
506	                        content=tool_call.get("thought", f"使用 {tool_name}")
507	                    )
508	
509	                    result = self.registry.execute(tool_name, **tool_args)
510	
511	                    yield AgentStep(
512	                        step_type=StepType.ACTION,
513	                        content=f"🔧 {tool_name}({json.dumps(tool_args, ensure_ascii=False)})",
514	                        tool_name=tool_name,
515	                        tool_input=tool_args,
516	                        tool_output=result,
517	                    )
518	
519	                    messages.append({
520	                        "role": "tool",
521	                        "name": tool_name,
522	                        "content": json.dumps({
523	                            "success": result.success,
524	                            "summary": result.summary,
525	                            "data": result.data[:10] if isinstance(result.data, list) else result.data,
526	                        }, ensure_ascii=False, default=str)
527	                    })
528	            else:
529	                answer = llm_response.get("content", "")
530	                yield AgentStep(
531	                    step_type=StepType.FINAL,
532	                    content=answer
533	                )
534	                return
535	
536	    # ==================== Helpers ====================
537	
538	    def _build_system_prompt(self) -> str:
539	        """Build system prompt for LLM mode"""
540	        tool_desc = self.registry.get_descriptions()
541	        schema_context = self.ontology.to_schema_context()[:2000]
542	
543	        # Inject conversation history if available
544	        history_text = self.conversation.get_history_text(max_turns=3)
545	        history_section = f"\n\n对话历史（用户可能参考之前的结果）:\n{history_text}" if history_text else ""
546	
547	        return f"""你是一个汽车测试缺陷数据分析 Agent。
548	
549	你可以使用以下工具来回答用户的问题:
550	{tool_desc}
551	
552	数据库语义:
553	{schema_context}
554	{history_section}
555	
556	规则:
557	1. 先理解用户意图，选择最合适的工具
558	2. 一个问题可能需要多步: 先查总数，再查分布，最后总结
559	3. 用中文回答，数据要精确
560	4. 对于趋势问题，说明上升/下降趋势
561	5. 对于分布问题，说明TOP3
562	6. 如果用户问的是跟进问题（如"按ECU分布呢"），参考对话历史
563	"""
564	
565	    def _format_entities(self, entities) -> str:
566	        """Format entities for display"""
567	        parts = []
568	        for e in entities.entities:
569	            if e.values:
570	                parts.append(f"{e.entity_type}={e.original}({e.value})→IN")
571	            else:
572	                parts.append(f"{e.entity_type}={e.original}({e.value})")
573	        return ", ".join(parts) if parts else "(无)"
574	
575	    def _format_answer(self, question: str, intent, result: ToolResult,
576	                       steps: List[AgentStep]) -> str:
577	        """Format the final answer based on intent and results"""
578	        if not result.success:
579	            return f"查询失败: {result.error}"
580	
581	        data = result.data
582	        intent_val = intent.primary.value
583	
584	        if intent_val == "count":
585	            if isinstance(data, list) and len(data) == 1 and len(data[0]) == 1:
586	                val = list(data[0].values())[0]
587	                return f"根据查询结果，{question}的答案是: **{val}**"
588	            elif isinstance(data, list) and len(data) == 1:
589	                # Single row
590	                parts = [f"  - {k}: {v}" for k, v in data[0].items()]
591	                return f"查询结果:\n" + "\n".join(parts)
592	            elif isinstance(data, list):
593	                return f"共找到 **{len(data)}** 条记录"
594	            else:
595	                return result.summary
596	
597	        elif intent_val == "trend":
598	            if isinstance(data, list) and len(data) >= 2:
599	                last = data[-1]
600	                prev = data[-2]
601	                count_key = "count"
602	                label_key = list(last.keys())[0]
603	                direction = "上升" if last[count_key] > prev[count_key] else "下降"
604	                return (
605	                    f"趋势分析结果（共{len(data)}期）:\n"
606	                    f"- 最近一期: {last[label_key]} = {last[count_key]}\n"
607	                    f"- 上一期: {prev[label_key]} = {prev[count_key]}\n"
608	                    f"- 趋势: **{direction}**\n"
609	                    f"- 变化量: {last[count_key] - prev[count_key]}"
610	                )
611	            return result.summary
612	
613	        elif intent_val in ("distribution", "comparison"):
614	            if isinstance(data, list) and data:
615	                lines = [f"分布分析（共{len(data)}个分组）:"]
616	                for i, row in enumerate(data[:5]):
617	                    group_val = row.get(list(row.keys())[0], "?")
618	                    count = row.get("count", 0)
619	                    pct = row.get("pct", "")
620	                    pct_str = f" ({pct}%)" if pct else ""
621	                    lines.append(f"  {i+1}. {group_val}: {count}{pct_str}")
622	                if len(data) > 5:
623	                    lines.append(f"  ... 共{len(data)}个分组")
624	                return "\n".join(lines)
625	            return result.summary
626	
627	        elif intent_val == "ranking":
628	            if isinstance(data, list) and data:
629	                lines = [f"排名结果（TOP {len(data)}）:"]
630	                for i, row in enumerate(data):
631	                    rank_val = row.get(list(row.keys())[0], "?")
632	                    count = row.get("count", 0)
633	                    lines.append(f"  {i+1}. {rank_val}: {count}")
634	                return "\n".join(lines)
635	            return result.summary
636	
637	        elif intent_val == "summary":
638	            if isinstance(data, dict):
639	                lines = ["📊 仪表盘概览:"]
640	                lines.append(f"- 总缺陷数: {data.get('total', 'N/A')}")
641	                lines.append(f"- 活跃缺陷: {data.get('active', 'N/A')}")
642	                lines.append(f"- Critical: {data.get('critical', 'N/A')}")
643	                lines.append(f"- 已解决: {data.get('resolved', 'N/A')}")
644	                return "\n".join(lines)
645	            return result.summary
646	
647	        elif intent_val == "detail_list" or intent_val == "status_check":
648	            if isinstance(data, list) and data:
649	                lines = [f"共 {len(data)} 条记录，前5条:"]
650	                for row in data[:5]:
651	                    defect_id = row.get("defect_id", "")
652	                    name = row.get("name", "")[:40]
653	                    severity = row.get("severity", "")
654	                    lines.append(f"  - [{defect_id}] {severity}: {name}")
655	                return "\n".join(lines)
656	            return result.summary
657	
658	        elif intent_val == "search_similar":
659	            if isinstance(data, list):
660	                return f"找到 {len(data)} 个相似缺陷"
661	            return result.summary
662	
663	        return result.summary or "查询完成"
664	
665	
666	# Singleton
667	_agent: Optional[ReActAgent] = None
668	
669	
670	def get_agent(
671	    ontology: Optional[OntologyEngine] = None,
672	    db_path: Optional[str] = None,
673	    llm_call_fn: Optional[Callable] = None,
674	) -> ReActAgent:
675	    global _agent
676	    if _agent is None:
677	        _agent = ReActAgent(
678	            ontology=ontology,
679	            db_path=db_path,
680	            llm_call_fn=llm_call_fn,
681	        )
682	    return _agent
683

### Q7

1	"""Tool Registry - Central tool registration and discovery
2	
3	Manages all available agent tools, their schemas, and execution.
4	"""
5	
6	from typing import Dict, List, Optional, Any
7	from dataclasses import dataclass
8	
9	from agent.agent_loop.tools import AgentTool, ToolResult
10	from agent.ontology import OntologyEngine, get_ontology_engine
11	
12	
13	class ToolRegistry:
14	    """
15	    Central registry for all agent tools.
16	
17	    Tools are registered here and can be discovered by name,
18	    listed for LLM function calling, and executed on demand.
19	    """
20	
21	    def __init__(self):
22	        self._tools: Dict[str, AgentTool] = {}
23	
24	    def register(self, tool: AgentTool):
25	        """Register a tool"""
26	        if tool.name in self._tools:
27	            raise ValueError(f"Tool '{tool.name}' already registered")
28	        self._tools[tool.name] = tool
29	
30	    def unregister(self, name: str):
31	        """Unregister a tool"""
32	        self._tools.pop(name, None)
33	
34	    def get(self, name: str) -> Optional[AgentTool]:
35	        """Get a tool by name"""
36	        return self._tools.get(name)
37	
38	    def list_tools(self) -> List[str]:
39	        """List all registered tool names"""
40	        return list(self._tools.keys())
41	
42	    def get_schemas(self) -> List[Dict]:
43	        """Get JSON schemas for all tools (for LLM function calling)"""
44	        return [tool.to_schema() for tool in self._tools.values()]
45	
46	    def execute(self, name: str, **kwargs) -> ToolResult:
47	        """Execute a tool by name"""
48	        tool = self.get(name)
49	        if not tool:
50	            return ToolResult(
51	                success=False,
52	                error=f"Unknown tool: {name}. Available: {self.list_tools()}"
53	            )
54	
55	        # Validate required parameters
56	        for param in tool.parameters:
57	            if param.required and param.name not in kwargs:
58	                return ToolResult(
59	                    success=False,
60	                    error=f"Missing required parameter '{param.name}' for tool '{name}'"
61	                )
62	
63	        # Fill defaults
64	        for param in tool.parameters:
65	            if param.name not in kwargs and param.default is not None:
66	                kwargs[param.name] = param.default
67	
68	        return tool.execute(**kwargs)
69	
70	    def get_descriptions(self) -> str:
71	        """Get human-readable description of all tools"""
72	        lines = []
73	        for name, tool in self._tools.items():
74	            params = ", ".join(
75	                f"{p.name}{'*' if p.required else ''}: {p.type}"
76	                for p in tool.parameters
77	            )
78	            lines.append(f"- **{name}**({params}): {tool.description}")
79	        return "\n".join(lines)
80	
81	
82	def build_default_registry(
83	    ontology: Optional[OntologyEngine] = None,
84	    db_path: Optional[str] = None,
85	    embedding_search_fn=None,
86	    llm_call_fn=None,
87	) -> ToolRegistry:
88	    """
89	    Build the default tool registry with all 6 core tools.
90	
91	    Args:
92	        ontology: Ontology engine instance
93	        db_path: Path to SQLite database
94	        embedding_search_fn: Optional BGE embedding search function
95	        llm_call_fn: Optional LLM callable for SQL fix/validate
96	
97	    Returns:
98	        Configured ToolRegistry with all tools registered
99	    """
100	    from agent.agent_loop.tools import (
101	        QueryDefectsTool, QueryTrendTool, DistributionTool,
102	        RankingTool, SearchSimilarTool, DashboardTool,
103	        CodeInterpreterTool,
104	    )
105	
106	    ont = ontology or get_ontology_engine()
107	
108	    registry = ToolRegistry()
109	    registry.register(QueryDefectsTool(ontology=ont, db_path=db_path, llm_call_fn=llm_call_fn))
110	    registry.register(QueryTrendTool(ontology=ont, db_path=db_path))
111	    registry.register(DistributionTool(ontology=ont, db_path=db_path))
112	    registry.register(RankingTool(ontology=ont, db_path=db_path))
113	    registry.register(SearchSimilarTool(
114	        ontology=ont, db_path=db_path, embedding_search_fn=embedding_search_fn
115	    ))
116	    registry.register(DashboardTool(ontology=ont, db_path=db_path))
117	    registry.register(CodeInterpreterTool(ontology=ont, db_path=db_path, llm_call_fn=llm_call_fn))
118	
119	    return registry
120

### Q8

1	"""Agent Tools - Core tool definitions for the ReAct loop
2	
3	Each tool wraps a specific capability:
4	- QueryDefectsTool: NL→SQL defect querying
5	- QueryTrendTool: Time series trend analysis
6	- DistributionTool: Group-by distribution analysis
7	- RankingTool: TOP-N ranking queries
8	- SearchSimilarTool: BGE semantic search for similar defects
9	- DashboardTool: Summary metrics/KPIs
10	- CodeInterpreterTool: Python code execution for complex analysis
11	"""
12	
13	import sqlite3
14	import json
15	from typing import Dict, List, Optional, Any, Tuple, Callable
16	from dataclasses import dataclass, field
17	from pathlib import Path
18	from abc import ABC, abstractmethod
19	
20	from agent.ontology import OntologyEngine, get_ontology_engine
21	from agent.sql_engine.generator import NL2SQLEngine, get_nl2sql_engine
22	from agent.understand.entity_extractor import ExtractionResult
23	from agent.understand.intent_detector import QueryIntent
24	
25	
26	@dataclass
27	class ToolParameter:
28	    """Parameter definition for a tool"""
29	    name: str
30	    type: str           # string, integer, boolean, array
31	    description: str
32	    required: bool = False
33	    default: Any = None
34	    enum: Optional[List[str]] = None
35	
36	
37	@dataclass
38	class ToolResult:
39	    """Result from tool execution"""
40	    success: bool
41	    data: Any = None           # The actual result data
42	    sql: str = ""              # SQL that was executed (if applicable)
43	    summary: str = ""          # Human-readable summary
44	    error: str = ""
45	    metadata: Dict = field(default_factory=dict)  # Extra info (row count, timing, etc.)
46	
47	
48	@dataclass
49	class AgentTool(ABC):
50	    """Base class for all agent tools"""
51	    name: str
52	    description: str
53	    parameters: List[ToolParameter] = field(default_factory=list)
54	
55	    @abstractmethod
56	    def execute(self, **kwargs) -> ToolResult:
57	        """Execute the tool with given parameters"""
58	        pass
59	
60	    def to_schema(self) -> Dict:
61	        """Convert to JSON schema for LLM function calling"""
62	        return {
63	            "name": self.name,
64	            "description": self.description,
65	            "parameters": {
66	                "type": "object",
67	                "properties": {
68	                    p.name: {
69	                        "type": p.type,
70	                        "description": p.description,
71	                        **({"enum": p.enum} if p.enum else {}),
72	                        **({"default": p.default} if p.default is not None else {}),
73	                    }
74	                    for p in self.parameters
75	                },
76	                "required": [p.name for p in self.parameters if p.required],
77	            }
78	        }
79	
80	
81	class QueryDefectsTool(AgentTool):
82	    """
83	    Query defect data using natural language.
84	    Uses the NL→SQL engine to translate questions to SQL and execute.
85	    """
86	
87	    def __init__(self, ontology: Optional[OntologyEngine] = None,
88	                 db_path: Optional[str] = None,
89	                 llm_call_fn=None):
90	        self.name = "query_defects"
91	        self.description = (
92	            "查询缺陷数据。支持自然语言提问，自动生成SQL并执行。"
93	            "例如: 'IDCEVO 本月 Critical 缺陷有多少'"
94	        )
95	        self.parameters = [
96	            ToolParameter(
97	                name="question",
98	                type="string",
99	                description="自然语言查询问题",
100	                required=True
101	            ),
102	            ToolParameter(
103	                name="limit",
104	                type="integer",
105	                description="返回结果最大行数",
106	                default=50
107	            ),
108	        ]
109	        self.engine = NL2SQLEngine(ontology=ontology, db_path=db_path, llm_call_fn=llm_call_fn)
110	
111	    def execute(self, question: str, limit: int = 50, **kwargs) -> ToolResult:
112	        """Execute NL→SQL query"""
113	        result = self.engine.query(question)
114	
115	        if result.error:
116	            return ToolResult(
117	                success=False,
118	                error=result.error,
119	                sql=result.sql,
120	                summary=f"查询失败: {result.error}"
121	            )
122	
123	        row_count = len(result.data)
124	        # Build summary
125	        if row_count == 0:
126	            summary = "查询结果为空"
127	        elif row_count == 1 and len(result.data[0]) == 1:
128	            # Single scalar value (like COUNT)
129	            val = list(result.data[0].values())[0]
130	            summary = f"结果: {val}"
131	        else:
132	            summary = f"返回 {row_count} 行数据"
133	
134	        return ToolResult(
135	            success=True,
136	            data=result.data[:limit],
137	            sql=result.sql,
138	            summary=summary,
139	            metadata={
140	                "intent": result.intent,
141	                "row_count": row_count,
142	                "candidates_count": len(result.candidates),
143	            }
144	        )
145	
146	
147	class QueryTrendTool(AgentTool):
148	    """
149	    Time series trend analysis tool.
150	    Generates day/week/month trend data.
151	    """
152	
153	    def __init__(self, ontology: Optional[OntologyEngine] = None,
154	                 db_path: Optional[str] = None):
155	        self.name = "query_trend"
156	        self.description = (
157	            "趋势分析工具。按天/周/月统计缺陷数量变化。"
158	            "例如: 'IDCEVO 近3个月缺陷趋势'"
159	        )
160	        self.parameters = [
161	            ToolParameter(
162	                name="question",
163	                type="string",
164	                description="趋势分析问题",
165	                required=True
166	            ),
167	            ToolParameter(
168	                name="granularity",
169	                type="string",
170	                description="时间粒度",
171	                enum=["day", "week", "month"],
172	                default="month"
173	            ),
174	        ]
175	        self.engine = NL2SQLEngine(ontology=ontology, db_path=db_path)
176	        self.ontology = ontology or get_ontology_engine()
177	        self.db_path = db_path
178	
179	    def execute(self, question: str, granularity: str = "month", **kwargs) -> ToolResult:
180	        """Execute trend query with specified granularity"""
181	        table = self.ontology.get_object("Defect").source_table
182	        time_field = "creation_time"
183	
184	        # Build granularity SQL
185	        if granularity == "day":
186	            date_expr = f"date({time_field})"
187	            date_label = "date"
188	        elif granularity == "week":
189	            date_expr = f"strftime('%Y-W%W', {time_field})"
190	            date_label = "week"
191	        else:  # month
192	            date_expr = f"strftime('%Y-%m', {time_field})"
193	            date_label = "month"
194	
195	        # Use NL2SQL to get WHERE clause
196	        result = self.engine.query(question)
197	
198	        # Extract WHERE from generated SQL
199	        where_match = result.sql.upper().find("WHERE")
200	        if where_match != -1:
201	            # Extract everything after WHERE up to GROUP BY/ORDER/LIMIT
202	            where_part = result.sql[where_match + 5:]
203	            for stopper in ["GROUP BY", "ORDER BY", "LIMIT"]:
204	                stop_pos = where_part.upper().find(stopper)
205	                if stop_pos != -1:
206	                    where_part = where_part[:stop_pos]
207	            where_clause = where_part.strip()
208	        else:
209	            where_clause = "1=1"
210	
211	        sql = (
212	            f"SELECT {date_expr} as {date_label}, COUNT(*) as count "
213	            f"FROM {table} WHERE {where_clause} "
214	            f"GROUP BY {date_expr} ORDER BY {date_label}"
215	        )
216	
217	        # Execute
218	        data = []
219	        error = None
220	        if self.db_path:
221	            try:
222	                conn = sqlite3.connect(self.db_path)
223	                conn.row_factory = sqlite3.Row
224	                cursor = conn.cursor()
225	                cursor.execute(sql)
226	                data = [dict(row) for row in cursor.fetchall()]
227	                conn.close()
228	            except Exception as e:
229	                error = str(e)
230	
231	        if error:
232	            return ToolResult(success=False, error=error, sql=sql)
233	
234	        # Compute trend direction
235	        if len(data) >= 2:
236	            last_val = data[-1]["count"]
237	            prev_val = data[-2]["count"]
238	            if last_val > prev_val:
239	                direction = "上升 ↑"
240	            elif last_val < prev_val:
241	                direction = "下降 ↓"
242	            else:
243	                direction = "持平 →"
244	            summary = f"趋势: {direction} (最近: {last_val}, 上一期: {prev_val})"
245	        elif len(data) == 1:
246	            summary = f"仅1期数据: {data[0]['count']}"
247	        else:
248	            summary = "无趋势数据"
249	
250	        return ToolResult(
251	            success=True,
252	            data=data,
253	            sql=sql,
254	            summary=summary,
255	            metadata={"granularity": granularity, "periods": len(data)}
256	        )
257	
258	
259	class DistributionTool(AgentTool):
260	    """
261	    Distribution/breakdown analysis tool.
262	    Groups defects by a dimension and shows counts/percentages.
263	    """
264	
265	    def __init__(self, ontology: Optional[OntologyEngine] = None,
266	                 db_path: Optional[str] = None):
267	        self.name = "get_distribution"
268	        self.description = (
269	            "分布分析工具。按指定维度分组统计缺陷数量和占比。"
270	            "例如: 按项目/严重度/ECU/团队分布"
271	        )
272	        self.parameters = [
273	            ToolParameter(
274	                name="group_by",
275	                type="string",
276	                description="分组维度: project, severity, assigned_ecu, team, status_phase, phase, top_aida",
277	                required=True,
278	                enum=["project", "severity", "assigned_ecu", "team",
279	                      "status_phase", "phase", "top_aida", "market"]
280	            ),
281	            ToolParameter(
282	                name="filters",
283	                type="string",
284	                description="过滤条件 (如: project=IDCEVO)",
285	                default=""
286	            ),
287	            ToolParameter(
288	                name="top_n",
289	                type="integer",
290	                description="只返回前N个分组",
291	                default=20
292	            ),
293	        ]
294	        self.ontology = ontology or get_ontology_engine()
295	        self.db_path = db_path
296	
297	    def execute(self, group_by: str, filters: str = "",
298	                top_n: int = 20, **kwargs) -> ToolResult:
299	        """Execute distribution query"""
300	        table = self.ontology.get_object("Defect").source_table
301	
302	        # Build WHERE from filters string
303	        where_clause = "1=1"
304	        if filters:
305	            # Simple key=value parsing
306	            parts = filters.split(",")
307	            conditions = []
308	            for part in parts:
309	                if "=" in part:
310	                    key, val = part.split("=", 1)
311	                    key = key.strip()
312	                    val = val.strip().strip("'\"")
313	                    conditions.append(f"{key} = '{val}'")
314	            if conditions:
315	                where_clause = " AND ".join(conditions)
316	
317	        # Check for category group
318	        prop = self.ontology.get_property("Defect", group_by)
319	        if prop and prop.category_groups:
320	            # Check if filters contains a category name for this field
321	            for group_name, group_values in prop.category_groups.items():
322	                if group_name.lower() in filters.lower():
323	                    values_str = ", ".join(f"'{v}'" for v in group_values)
324	                    where_clause += f" AND {group_by} IN ({values_str})"
325	                    break
326	
327	        sql = (
328	            f"SELECT {group_by}, COUNT(*) as count, "
329	            f"ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM {table} WHERE {where_clause}), 1) as pct "
330	            f"FROM {table} WHERE {where_clause} "
331	            f"GROUP BY {group_by} ORDER BY count DESC LIMIT {top_n}"
332	        )
333	
334	        data = []
335	        error = None
336	        if self.db_path:
337	            try:
338	                conn = sqlite3.connect(self.db_path)
339	                conn.row_factory = sqlite3.Row
340	                cursor = conn.cursor()
341	                cursor.execute(sql)
342	                data = [dict(row) for row in cursor.fetchall()]
343	                conn.close()
344	            except Exception as e:
345	                error = str(e)
346	
347	        if error:
348	            return ToolResult(success=False, error=error, sql=sql)
349	
350	        # Build summary
351	        if data:
352	            top_item = data[0]
353	            summary = f"共{len(data)}个分组, 最多: {top_item[group_by]} ({top_item['count']}个, {top_item['pct']}%)"
354	        else:
355	            summary = "无分布数据"
356	
357	        return ToolResult(
358	            success=True,
359	            data=data,
360	            sql=sql,
361	            summary=summary,
362	            metadata={"group_by": group_by, "groups": len(data)}
363	        )
364	
365	
366	class RankingTool(AgentTool):
367	    """
368	    Ranking tool for TOP-N queries.
369	    """
370	
371	    def __init__(self, ontology: Optional[OntologyEngine] = None,
372	                 db_path: Optional[str] = None):
373	        self.name = "get_ranking"
374	        self.description = (
375	            "排名查询工具。按指定维度排序，返回TOP N。"
376	            "例如: 缺陷最多的10个ECU"
377	        )
378	        self.parameters = [
379	            ToolParameter(
380	                name="rank_by",
381	                type="string",
382	                description="排名维度: project, severity, assigned_ecu, team, status_phase, phase, top_aida",
383	                required=True,
384	                enum=["project", "severity", "assigned_ecu", "team",
385	                      "status_phase", "phase", "top_aida"]
386	            ),
387	            ToolParameter(
388	                name="order",
389	                type="string",
390	                description="排序方向",
391	                enum=["desc", "asc"],
392	                default="desc"
393	            ),
394	            ToolParameter(
395	                name="limit",
396	                type="integer",
397	                description="返回行数",
398	                default=10
399	            ),
400	            ToolParameter(
401	                name="filters",
402	                type="string",
403	                description="过滤条件",
404	                default=""
405	            ),
406	        ]
407	        self.ontology = ontology or get_ontology_engine()
408	        self.db_path = db_path
409	
410	    def execute(self, rank_by: str, order: str = "desc", limit: int = 10,
411	                filters: str = "", **kwargs) -> ToolResult:
412	        """Execute ranking query"""
413	        table = self.ontology.get_object("Defect").source_table
414	
415	        where_clause = "1=1"
416	        if filters:
417	            parts = filters.split(",")
418	            conditions = []
419	            for part in parts:
420	                if "=" in part:
421	                    key, val = part.split("=", 1)
422	                    conditions.append(f"{key.strip()} = '{val.strip().strip(chr(39) + chr(34))}'")
423	            if conditions:
424	                where_clause = " AND ".join(conditions)
425	
426	        sql_direction = "DESC" if order.lower() == "desc" else "ASC"
427	        sql = (
428	            f"SELECT {rank_by}, COUNT(*) as count "
429	            f"FROM {table} WHERE {where_clause} AND {rank_by} IS NOT NULL "
430	            f"GROUP BY {rank_by} ORDER BY count {sql_direction} LIMIT {limit}"
431	        )
432	
433	        data = []
434	        if self.db_path:
435	            try:
436	                conn = sqlite3.connect(self.db_path)
437	                conn.row_factory = sqlite3.Row
438	                cursor = conn.cursor()
439	                cursor.execute(sql)
440	                data = [dict(row) for row in cursor.fetchall()]
441	                conn.close()
442	            except Exception as e:
443	                return ToolResult(success=False, error=str(e), sql=sql)
444	
445	        if data:
446	            summary = f"TOP {len(data)}: 第1名 {data[0][rank_by]} ({data[0]['count']}个)"
447	        else:
448	            summary = "无排名数据"
449	
450	        return ToolResult(
451	            success=True,
452	            data=data,
453	            sql=sql,
454	            summary=summary,
455	            metadata={"rank_by": rank_by, "limit": limit}
456	        )
457	
458	
459	class SearchSimilarTool(AgentTool):
460	    """
461	    Semantic search for similar defects using BGE embeddings.
462	    Wraps the existing duplicate_issue_finder.py if available.
463	    """
464	
465	    def __init__(self, ontology: Optional[OntologyEngine] = None,
466	                 db_path: Optional[str] = None,
467	                 embedding_search_fn=None):
468	        self.name = "search_similar"
469	        self.description = (
470	            "语义搜索相似缺陷。使用BGE embedding向量检索。"
471	            "输入缺陷描述或关键词，返回最相似的缺陷列表。"
472	        )
473	        self.parameters = [
474	            ToolParameter(
475	                name="query",
476	                type="string",
477	                description="搜索文本（缺陷描述、关键词等）",
478	                required=True
479	            ),
480	            ToolParameter(
481	                name="top_k",
482	                type="integer",
483	                description="返回结果数量",
484	                default=10
485	            ),
486	            ToolParameter(
487	                name="threshold",
488	                type="number",  # float
489	                description="相似度阈值 (0-1)",
490	                default=0.5
491	            ),
492	        ]
493	        self.ontology = ontology or get_ontology_engine()
494	        self.db_path = db_path
495	        self._search_fn = embedding_search_fn  # Injected dependency
496	
497	    def execute(self, query: str, top_k: int = 10,
498	                threshold: float = 0.5, **kwargs) -> ToolResult:
499	        """Execute semantic search"""
500	        if self._search_fn:
501	            # Use injected search function (production)
502	            try:
503	                results = self._search_fn(query, top_k=top_k, threshold=threshold)
504	                summary = f"找到 {len(results)} 个相似缺陷"
505	                return ToolResult(
506	                    success=True,
507	                    data=results,
508	                    summary=summary,
509	                    metadata={"top_k": top_k, "threshold": threshold}
510	                )
511	            except Exception as e:
512	                return ToolResult(success=False, error=str(e))
513	
514	        # Fallback: keyword-based search using SQL LIKE
515	        if self.db_path:
516	            table = self.ontology.get_object("Defect").source_table
517	            # Simple keyword search
518	            keywords = query.split()
519	            like_conditions = " OR ".join(
520	                f"name LIKE '%{kw}%' OR assigned_ecu LIKE '%{kw}%'"
521	                for kw in keywords[:3]  # Limit to 3 keywords
522	            )
523	            sql = (
524	                f"SELECT defect_id, name, project, severity, status_phase, "
525	                f"assigned_ecu, creation_time FROM {table} "
526	                f"WHERE {like_conditions} LIMIT {top_k}"
527	            )
528	            try:
529	                conn = sqlite3.connect(self.db_path)
530	                conn.row_factory = sqlite3.Row
531	                cursor = conn.cursor()
532	                cursor.execute(sql)
533	                data = [dict(row) for row in cursor.fetchall()]
534	                conn.close()
535	                summary = f"关键词搜索找到 {len(data)} 个相关缺陷"
536	                return ToolResult(
537	                    success=True,
538	                    data=data,
539	                    sql=sql,
540	                    summary=summary,
541	                    metadata={"mode": "keyword_fallback"}
542	                )
543	            except Exception as e:
544	                return ToolResult(success=False, error=str(e), sql=sql)
545	
546	        return ToolResult(
547	            success=False,
548	            error="No search function or database available"
549	        )
550	
551	
552	class DashboardTool(AgentTool):
553	    """
554	    Dashboard summary tool - returns key metrics at a glance.
555	    """
556	
557	    def __init__(self, ontology: Optional[OntologyEngine] = None,
558	                 db_path: Optional[str] = None):
559	        self.name = "get_dashboard"
560	        self.description = (
561	            "获取仪表盘汇总指标。一键返回: 总缺陷数、活跃缺陷数、"
562	            "Critical缺陷数、各项目分布等核心KPI。"
563	        )
564	        self.parameters = [
565	            ToolParameter(
566	                name="project",
567	                type="string",
568	                description="指定项目 (留空=全部项目)",
569	                default=""
570	            ),
571	        ]
572	        self.ontology = ontology or get_ontology_engine()
573	        self.db_path = db_path
574	
575	    def execute(self, project: str = "", **kwargs) -> ToolResult:
576	        """Execute dashboard query"""
577	        if not self.db_path:
578	            return ToolResult(success=False, error="No database configured")
579	
580	        table = self.ontology.get_object("Defect").source_table
581	        project_filter = f" AND project = '{project}'" if project else ""
582	
583	        queries = {
584	            "total": f"SELECT COUNT(*) as val FROM {table} WHERE 1=1{project_filter}",
585	            "active": f"SELECT COUNT(*) as val FROM {table} WHERE status_phase IN ('New', 'Open', 'In Progress'){project_filter}",
586	            "critical": f"SELECT COUNT(*) as val FROM {table} WHERE severity = 'Critical' AND status_phase IN ('New', 'Open', 'In Progress'){project_filter}",
587	            "resolved": f"SELECT COUNT(*) as val FROM {table} WHERE status_phase IN ('Fixed', 'Closed'){project_filter}",
588	        }
589	
590	        results = {}
591	        try:
592	            conn = sqlite3.connect(self.db_path)
593	            cursor = conn.cursor()
594	            for key, sql in queries.items():
595	                cursor.execute(sql)
596	                results[key] = cursor.fetchone()[0]
597	
598	            # Project distribution
599	            cursor.execute(
600	                f"SELECT project, COUNT(*) as count FROM {table} "
601	                f"WHERE 1=1{project_filter} GROUP BY project ORDER BY count DESC LIMIT 10"
602	            )
603	            results["by_project"] = [dict(zip(["project", "count"], row))
604	                                    for row in cursor.fetchall()]
605	
606	            # Severity distribution
607	            cursor.execute(
608	                f"SELECT severity, COUNT(*) as count FROM {table} "
609	                f"WHERE 1=1{project_filter} GROUP BY severity ORDER BY count DESC"
610	            )
611	            results["by_severity"] = [dict(zip(["severity", "count"], row))
612	                                      for row in cursor.fetchall()]
613	
614	            conn.close()
615	        except Exception as e:
616	            return ToolResult(success=False, error=str(e))
617	
618	        # Build summary
619	        summary_parts = [
620	            f"总缺陷: {results['total']}",
621	            f"活跃: {results['active']}",
622	            f"Critical: {results['critical']}",
623	            f"已解决: {results['resolved']}",
624	        ]
625	        summary = " | ".join(summary_parts)
626	
627	        return ToolResult(
628	            success=True,
629	            data=results,
630	            summary=summary,
631	            metadata={"project": project or "ALL"}
632	        )
633	
634	
635	class CodeInterpreterTool(AgentTool):
636	    """
637	    Python Code Interpreter Tool - generates and executes Python code
638	    for complex analysis that SQL can't express.
639	
640	    Use cases: statistical tests, custom aggregations, anomaly detection,
641	    data transformations, comparative analysis.
642	    """
643	
644	    def __init__(
645	        self,
646	        ontology: Optional[OntologyEngine] = None,
647	        db_path: Optional[str] = None,
648	        llm_call_fn: Optional[Callable] = None,
649	    ):
650	        self.name = "analyze_data"
651	        self.description = (
652	            "用Python代码分析查询结果。适用于复杂统计、自定义计算、"
653	            "异常检测、趋势对比等SQL无法表达的分析。"
654	            "传入analysis描述和data（查询结果），返回分析结论。"
655	        )
656	        self.parameters = [
657	            ToolParameter(
658	                name="analysis",
659	                type="string",
660	                description="分析描述，如'计算各ECU的缺陷密度并排序'",
661	                required=True,
662	            ),
663	            ToolParameter(
664	                name="data",
665	                type="array",
666	                description="要分析的数据（查询结果，JSON数组）",
667	                required=True,
668	            ),
669	        ]
670	        self.ontology = ontology or get_ontology_engine()
671	        self.db_path = db_path
672	
673	        from agent.interpret.code_interpreter import CodeInterpreter
674	        self.interpreter = CodeInterpreter(
675	            llm_call_fn=llm_call_fn,
676	            timeout=5,
677	        )
678	
679	    def execute(
680	        self,
681	        analysis: str = "",
682	        data: Optional[list] = None,
683	        **kwargs,
684	    ) -> ToolResult:
685	        """Execute Python code analysis"""
686	        if not data:
687	            return ToolResult(
688	                success=False,
689	                error="data参数为空，需要提供要分析的数据",
690	            )
691	
692	        if not analysis:
693	            return ToolResult(
694	                success=False,
695	                error="analysis参数为空，需要描述分析目标",
696	            )
697	
698	        result = self.interpreter.execute(analysis, data)
699	
700	        return ToolResult(
701	            success=result["success"],
702	            data={"result": result["output"], "code": result["code"]},
703	            summary=result["output"] if result["success"] else f"分析失败: {result.get('output', '')}",
704	            error=result.get("error", ""),
705	            metadata={"time_ms": result["time_ms"]},
706	        )
707

### Q9

1	"""SSE Event Stream - Stream agent steps as Server-Sent Events
2	
3	Converts AgentStep events into SSE-formatted messages
4	compatible with the existing Data-Agent Node gateway.
5	
6	Event types:
7	- thought: Agent reasoning step
8	- action: Tool call
9	- observation: Tool result
10	- final: Final answer
11	- error: Error occurred
12	"""
13	
14	import json
15	import time
16	from typing import Generator, Dict, Any
17	
18	from agent.agent_loop.loop import ReActAgent, AgentStep, StepType
19	
20	
21	class SSEEventStream:
22	    """
23	    Convert agent execution into SSE events.
24	
25	    Usage in FastAPI:
26	        @app.get("/api/agent/stream")
27	        def stream_agent(question: str):
28	            stream = SSEEventStream(agent)
29	            return StreamingResponse(
30	                stream.process(question),
31	                media_type="text/event-stream"
32	            )
33	    """
34	
35	    # Event type mapping
36	    EVENT_TYPES = {
37	        StepType.THOUGHT: "thought",
38	        StepType.ACTION: "action",
39	        StepType.OBSERVATION: "observation",
40	        StepType.FINAL: "final",
41	        StepType.ERROR: "error",
42	    }
43	
44	    def __init__(self, agent: ReActAgent):
45	        self.agent = agent
46	
47	    def process(self, question: str) -> Generator[str, None, None]:
48	        """
49	        Process question and yield SSE-formatted events.
50	
51	        Yields strings in SSE format: "data: {json}\\n\\n"
52	        """
53	        # Send start event
54	        yield self._format_event("start", {
55	            "question": question,
56	            "timestamp": time.time()
57	        })
58	
59	        # Process and stream steps
60	        for step in self.agent.process_stream(question):
61	            event_type = self.EVENT_TYPES.get(step.step_type, "step")
62	            data = self._step_to_dict(step)
63	            yield self._format_event(event_type, data)
64	
65	        # Send end event
66	        yield self._format_event("done", {
67	            "timestamp": time.time()
68	        })
69	
70	    def _step_to_dict(self, step: AgentStep) -> Dict[str, Any]:
71	        """Convert AgentStep to dict for SSE"""
72	        data = {
73	            "content": step.content,
74	            "timestamp": step.timestamp,
75	        }
76	
77	        if step.tool_name:
78	            data["tool"] = step.tool_name
79	
80	        if step.tool_input:
81	            data["input"] = step.tool_input
82	
83	        if step.tool_output:
84	            data["output"] = {
85	                "success": step.tool_output.success,
86	                "summary": step.tool_output.summary,
87	            }
88	            # Include data if reasonable size
89	            if step.tool_output.data:
90	                if isinstance(step.tool_output.data, list):
91	                    data["rows"] = len(step.tool_output.data)
92	                    data["preview"] = step.tool_output.data[:5]
93	                elif isinstance(step.tool_output.data, dict):
94	                    data["preview"] = {k: v for k, v in
95	                                      list(step.tool_output.data.items())[:10]}
96	
97	        return data
98	
99	    def _format_event(self, event_type: str, data: Dict) -> str:
100	        """Format as SSE event"""
101	        payload = json.dumps(data, ensure_ascii=False, default=str)
102	        return f"event: {event_type}\ndata: {payload}\n\n"
103	
104	    @staticmethod
105	    def parse_event(sse_string: str) -> Dict[str, Any]:
106	        """Parse an SSE event string back to dict (for client-side debugging)"""
107	        lines = sse_string.strip().split("\n")
108	        event_type = ""
109	        data = ""
110	        for line in lines:
111	            if line.startswith("event: "):
112	                event_type = line[7:]
113	            elif line.startswith("data: "):
114	                data = line[6:]
115	        return {
116	            "event": event_type,
117	            "data": json.loads(data) if data else {}
118	        }
119

### Q10

1	"""Ontology Engine - Core Semantic Modeling
2	
3	Inspired by Palantir Ontology and WrenAI MDL
4	
5	This engine loads and queries object type definitions from YAML files,
6	providing semantic context for NL→SQL generation and agent reasoning.
7	"""
8	
9	import yaml
10	from pathlib import Path
11	from dataclasses import dataclass, field
12	from typing import Any, Optional, Dict, List, Set
13	from enum import Enum
14	
15	
16	class PropertyType(Enum):
17	    STRING = "string"
18	    INTEGER = "integer"
19	    FLOAT = "float"
20	    ENUM = "enum"
21	    DATETIME = "datetime"
22	    JSON = "json"
23	    ARRAY = "array"
24	
25	
26	@dataclass
27	class PropertyDef:
28	    """Property definition for an object type"""
29	    name: str
30	    type: PropertyType
31	    meaning: str
32	    values: Optional[List[str]] = None
33	    examples: Optional[List[str]] = None
34	    foreign_key: Optional[str] = None
35	    category_groups: Optional[Dict[str, List[str]]] = None
36	    semantics: Optional[Dict[str, str]] = None
37	    business_rules: Optional[List[str]] = None
38	    aliases: Optional[Dict[str, List[str]]] = None
39	    mapping: Optional[Dict[str, Any]] = None
40	    item_type: Optional[PropertyType] = None  # For array types
41	
42	
43	@dataclass
44	class LinkDef:
45	    """Relationship definition between object types"""
46	    name: str
47	    target: str
48	    type: str  # one-to-one, one-to-many, many-to-one, many-to-many
49	    join: Optional[str] = None  # Optional - JSON-based relationships use "via"
50	    meaning: str = ""
51	    via: Optional[str] = None  # For many-to-many via junction table
52	
53	
54	@dataclass
55	class MetricDef:
56	    """Calculated metric definition"""
57	    name: str
58	    definition: str  # SQL-like definition
59	    meaning: str
60	
61	
62	@dataclass
63	class CalibrationRule:
64	    """Business calibration rule"""
65	    id: str
66	    trigger: List[str]  # Keywords that trigger this rule
67	    rule: str  # The rule text
68	
69	
70	@dataclass
71	class Governance:
72	    """Governance rules for object operations"""
73	    allow_operations: List[str]
74	    forbid_operations: List[str]
75	    sensitive_fields: List[str]
76	    default_time_range: str
77	
78	
79	@dataclass
80	class ObjectType:
81	    """Object type definition"""
82	    object_type: str
83	    description: str
84	    source_table: str
85	    primary_key: str
86	    properties: Dict[str, PropertyDef] = field(default_factory=dict)
87	    links: List[LinkDef] = field(default_factory=list)
88	    metrics: Dict[str, MetricDef] = field(default_factory=dict)
89	    calibration_rules: List[CalibrationRule] = field(default_factory=list)
90	    governance: Optional[Governance] = None
91	
92	
93	class OntologyEngine:
94	    """
95	    Ontology Engine - loads and queries semantic object definitions
96	
97	    Provides semantic context for:
98	    - Understanding what each field means
99	    - Knowing relationships between objects
100	    - Applying business rules
101	    - Generating proper SQL with semantics
102	    """
103	
104	    def __init__(self, ontology_dir: Path):
105	        self.ontology_dir = Path(ontology_dir)
106	        self._objects: Dict[str, ObjectType] = {}
107	        self._load_objects()
108	
109	    def _load_objects(self):
110	        """Load all object type definitions from YAML files"""
111	        objects_dir = self.ontology_dir / "objects"
112	        if not objects_dir.exists():
113	            raise FileNotFoundError(f"Objects directory not found: {objects_dir}")
114	
115	        for yaml_file in objects_dir.glob("*.yaml"):
116	            with open(yaml_file, encoding="utf-8") as f:
117	                data = yaml.safe_load(f)
118	
119	            obj_type = self._parse_object_type(data)
120	            self._objects[obj_type.object_type] = obj_type
121	
122	    def _parse_object_type(self, data: dict) -> ObjectType:
123	        """Parse YAML data into ObjectType"""
124	        # Parse properties
125	        properties = {}
126	        for prop_name, prop_data in data.get("properties", {}).items():
127	            if isinstance(prop_data, str):
128	                # Simple string meaning
129	                properties[prop_name] = PropertyDef(
130	                    name=prop_name,
131	                    type=PropertyType.STRING,
132	                    meaning=prop_data
133	                )
134	            elif isinstance(prop_data, dict):
135	                prop_type_str = prop_data.get("type", "string")
136	                prop_type = PropertyType(prop_type_str)
137	
138	                # Parse item_type for arrays
139	                item_type_str = prop_data.get("item_type")
140	                item_type = PropertyType(item_type_str) if item_type_str else None
141	
142	                properties[prop_name] = PropertyDef(
143	                    name=prop_name,
144	                    type=prop_type,
145	                    meaning=prop_data.get("meaning", ""),
146	                    values=prop_data.get("values"),
147	                    examples=prop_data.get("examples"),
148	                    foreign_key=prop_data.get("foreign_key"),
149	                    category_groups=prop_data.get("category_groups"),
150	                    semantics=prop_data.get("semantics"),
151	                    business_rules=prop_data.get("business_rules"),
152	                    aliases=prop_data.get("aliases"),
153	                    mapping=prop_data.get("mapping"),
154	                    item_type=item_type
155	                )
156	
157	        # Parse links
158	        links = []
159	        for link_data in data.get("links", []):
160	            # Some relationships use "via" for JSON-based joins, not SQL join
161	            join_clause = link_data.get("join")
162	            if not join_clause and link_data.get("via"):
163	                join_clause = f"via {link_data['via']}"  # JSON-based relationship
164	            
165	            links.append(LinkDef(
166	                name=link_data["name"],
167	                target=link_data["target"],
168	                type=link_data["type"],
169	                join=join_clause,
170	                meaning=link_data.get("meaning", ""),
171	                via=link_data.get("via")
172	            ))
173	
174	        # Parse metrics
175	        metrics = {}
176	        for metric_name, metric_data in data.get("metrics", {}).items():
177	            if isinstance(metric_data, dict):
178	                metrics[metric_name] = MetricDef(
179	                    name=metric_name,
180	                    definition=metric_data["definition"],
181	                    meaning=metric_data["meaning"]
182	                )
183	
184	        # Parse calibration rules
185	        calibration_rules = []
186	        for rule_data in data.get("calibration_rules", []):
187	            calibration_rules.append(CalibrationRule(
188	                id=rule_data["id"],
189	                trigger=rule_data["trigger"],
190	                rule=rule_data["rule"]
191	            ))
192	
193	        # Parse governance
194	        governance = None
195	        governance_data = data.get("governance")
196	        if governance_data:
197	            governance = Governance(
198	                allow_operations=governance_data.get("allow_operations", []),
199	                forbid_operations=governance_data.get("forbid_operations", []),
200	                sensitive_fields=governance_data.get("sensitive_fields", []),
201	                default_time_range=governance_data.get("default_time_range", "90 days")
202	            )
203	
204	        return ObjectType(
205	            object_type=data["object_type"],
206	            description=data["description"],
207	            source_table=data["source_table"],
208	            primary_key=data["primary_key"],
209	            properties=properties,
210	            links=links,
211	            metrics=metrics,
212	            calibration_rules=calibration_rules,
213	            governance=governance
214	        )
215	
216	    def get_object(self, object_type: str) -> Optional[ObjectType]:
217	        """Get object type definition"""
218	        return self._objects.get(object_type)
219	
220	    def get_all_objects(self) -> Dict[str, ObjectType]:
221	        """Get all object type definitions"""
222	        return self._objects
223	
224	    def get_property(self, object_type: str, property_name: str) -> Optional[PropertyDef]:
225	        """Get property definition"""
226	        obj = self.get_object(object_type)
227	        if obj:
228	            return obj.properties.get(property_name)
229	        return None
230	
231	    def get_links(self, object_type: str) -> List[LinkDef]:
232	        """Get all links for an object type"""
233	        obj = self.get_object(object_type)
234	        if obj:
235	            return obj.links
236	        return []
237	
238	    def get_link(self, object_type: str, link_name: str) -> Optional[LinkDef]:
239	        """Get specific link by name"""
240	        for link in self.get_links(object_type):
241	            if link.name == link_name:
242	                return link
243	        return None
244	
245	    def get_metrics(self, object_type: str) -> Dict[str, MetricDef]:
246	        """Get all metrics for an object type"""
247	        obj = self.get_object(object_type)
248	        if obj:
249	            return obj.metrics
250	        return {}
251	
252	    def get_calibration_rules(self, object_type: str) -> List[CalibrationRule]:
253	        """Get calibration rules for an object type"""
254	        obj = self.get_object(object_type)
255	        if obj:
256	            return obj.calibration_rules
257	        return []
258	
259	    def get_all_calibration_rules(self) -> List[CalibrationRule]:
260	        """Get calibration rules from all object types"""
261	        all_rules = []
262	        for obj in self._objects.values():
263	            all_rules.extend(obj.calibration_rules)
264	        return all_rules
265	
266	    def find_relevant_rules(self, keywords: List[str]) -> List[CalibrationRule]:
267	        """Find calibration rules that match given keywords"""
268	        relevant_rules = []
269	        for rule in self.get_all_calibration_rules():
270	            for trigger in rule.trigger:
271	                for keyword in keywords:
272	                    if keyword.lower() in trigger.lower():
273	                        relevant_rules.append(rule)
274	                        break
275	        return relevant_rules
276	
277	    def resolve_alias(self, object_type: str, property_name: str, alias: str) -> Optional[str]:
278	        """
279	        Resolve an alias to its canonical value
280	
281	        Example:
282	            resolve_alias("Defect", "project", "idcevo") -> "IDCEVO"
283	            resolve_alias("Defect", "assigned_ecu", "车身控制器") -> "BCM"
284	        """
285	        prop = self.get_property(object_type, property_name)
286	        if not prop or not prop.aliases:
287	            return None
288	
289	        alias_lower = alias.lower().strip()
290	        for canonical, aliases in prop.aliases.items():
291	            if alias_lower in [a.lower() for a in aliases]:
292	                return canonical
293	        return None
294	
295	    def get_category_group(self, object_type: str, property_name: str, category: str) -> Optional[List[str]]:
296	        """Get values for a specific category group"""
297	        prop = self.get_property(object_type, property_name)
298	        if not prop or not prop.category_groups:
299	            return None
300	        return prop.category_groups.get(category)
301	
302	    def traverse(self, start_type: str, start_id: str, path: List[str]) -> List[Dict[str, Any]]:
303	        """
304	        Traverse the ontology graph following a path of link names
305	
306	        Example:
307	            traverse("Defect", "DEF-001", ["has_history"]) -> history records
308	            traverse("Defect", "DEF-001", ["belongs_to_project"]) -> project info
309	
310	        Returns a list of dict results with traversed object data
311	        """
312	        # This is a placeholder - actual implementation requires database access
313	        # The ontology engine defines the traversal plan, but execution happens in SQL engine
314	        return []
315	
316	    def to_schema_context(self) -> str:
317	        """
318	        Convert ontology to schema context for LLM prompts
319	
320	        Generates a human-readable description of all objects, properties, and relationships
321	        """
322	        lines = ["# 数据库语义模型\n"]
323	
324	        for obj_type, obj in sorted(self._objects.items()):
325	            lines.append(f"\n## {obj_type}\n")
326	            lines.append(f"**含义**: {obj.description}\n")
327	            lines.append(f"**数据表**: {obj.source_table}\n")
328	            lines.append(f"**主键**: {obj.primary_key}\n")
329	
330	            if obj.properties:
331	                lines.append("\n### 字段\n")
332	                for prop_name, prop in obj.properties.items():
333	                    type_str = prop.type.value
334	                    values_str = f" (取值: {', '.join(prop.values)})" if prop.values else ""
335	                    meaning_str = prop.meaning or ""
336	                    lines.append(f"- **{prop_name}** ({type_str}{values_str}): {meaning_str}")
337	
338	                    if prop.aliases:
339	                        aliases_str = ", ".join([f"{k}({', '.join(v)})" for k, v in prop.aliases.items()])
340	                        lines.append(f"  - 别名: {aliases_str}")
341	
342	                    if prop.business_rules:
343	                        for rule in prop.business_rules:
344	                            lines.append(f"  - 规则: {rule}")
345	
346	            if obj.links:
347	                lines.append("\n### 关系\n")
348	                for link in obj.links:
349	                    lines.append(f"- **{link.name}** → {link.target} ({link.type}): {link.meaning}")
350	                    lines.append(f"  - 关联条件: {link.join}")
351	
352	            if obj.metrics:
353	                lines.append("\n### 计算指标\n")
354	                for metric_name, metric in obj.metrics.items():
355	                    lines.append(f"- **{metric_name}**: {metric.meaning}")
356	                    lines.append(f"  - 计算: {metric.definition}")
357	
358	            if obj.calibration_rules:
359	                lines.append("\n### 业务规则提醒\n")
360	                for rule in obj.calibration_rules:
361	                    trigger_str = ", ".join(f'"{t}"' for t in rule.trigger)
362	                    lines.append(f"- 当提到 {trigger_str} 时: {rule.rule}")
363	
364	        return "\n".join(lines)
365	
366	    def get_sql_table_mapping(self) -> Dict[str, str]:
367	        """Get mapping from object type to SQL table"""
368	        return {obj_type: obj.source_table for obj_type, obj in self._objects.items()}
369	
370	    def get_primary_keys(self) -> Dict[str, str]:
371	        """Get primary key for each object type"""
372	        return {obj_type: obj.primary_key for obj_type, obj in self._objects.items()}
373	
374	
375	# Singleton instance for easy access
376	_engine: Optional[OntologyEngine] = None
377	
378	
379	def get_ontology_engine(ontology_dir: Optional[Path] = None) -> OntologyEngine:
380	    """Get or create the singleton OntologyEngine"""
381	    global _engine
382	    if _engine is None:
383	        if ontology_dir is None:
384	            # Default to agent/ontology/
385	            ontology_dir = Path(__file__).parent.parent / "agent" / "ontology"
386	        _engine = OntologyEngine(ontology_dir)
387	    return _engine

### Q11

total 40
drwxr-xr-x   5 tonyorz  staff    160  6 22 17:18 .
drwxr-xr-x  12 tonyorz  staff    384  6 22 17:18 ..
-rw-r--r--   1 tonyorz  staff    704  6 22 17:18 __init__.py
-rw-r--r--   1 tonyorz  staff  14348  6 22 17:18 engine.py
drwxr-xr-x   8 tonyorz  staff    256  6 22 17:18 objects
===
/Users/tonyorz/Data-Agent/agent/ontology/objects/defect.yaml
/Users/tonyorz/Data-Agent/agent/ontology/objects/defect_history.yaml
/Users/tonyorz/Data-Agent/agent/ontology/objects/manual_run.yaml
/Users/tonyorz/Data-Agent/agent/ontology/objects/project.yaml
/Users/tonyorz/Data-Agent/agent/ontology/objects/team.yaml
/Users/tonyorz/Data-Agent/agent/ontology/objects/testcase.yaml

### Q12

1	# Defect Object Type
2	# Semantic definition of Octane defects
3	
4	object_type: Defect
5	description: "测试缺陷/问题记录"
6	source_table: octane_defects
7	primary_key: defect_id
8	
9	# Column definitions with semantic meaning
10	properties:
11	  defect_id:
12	    type: string
13	    meaning: "Octane 缺陷唯一ID"
14	    examples: ["DEF-2026-0001", "DEF-2026-0002"]
15	
16	  name:
17	    type: string
18	    meaning: "缺陷标题/描述"
19	
20	  project:
21	    type: enum
22	    meaning: "项目代号"
23	    values: [IDCEVO, IDC, MGU, RSU, App]
24	    aliases:
25	      IDCEVO: ["idcevo", "IDCEVO*", "CDE", "ENTRYEVO", "NBTEVO"]
26	      IDC: ["idc", "IDC23", "HU-MGU_02_A"]
27	      MGU: ["mgu", "MGU22", "BMWMGU"]
28	      RSU: ["rsu", "Remote_Software_Update"]
29	      App: ["app", "Application", "Phone_App"]
30	    category_groups:
31	      china: ["IDCEVO", "IDC", "MGU"]
32	      global: ["RSU", "App"]
33	
34	  market:
35	    type: string
36	    meaning: "市场区域"
37	    values: [CN, GLOBAL, APAC, EU, NA]
38	    aliases:
39	      CN: ["china", "中国", "cn"]
40	      GLOBAL: ["global", "全球", "intl"]
41	      APAC: ["apac", "亚太"]
42	      EU: ["eu", "欧洲"]
43	      NA: ["na", "北美"]
44	
45	  pu:
46	    type: string
47	    meaning: "产品单元"
48	    examples: ["PU-A", "PU-B", "PU-Infotainment"]
49	
50	  fv:
51	    type: string
52	    meaning: "功能版本"
53	    examples: ["FV-001", "FV-002"]
54	
55	  fvp:
56	    type: string
57	    meaning: "功能版本计划"
58	    examples: ["FVP-001", "FVP-002"]
59	
60	  team:
61	    type: string
62	    meaning: "负责团队"
63	    examples: ["CN Core UI", "CN Media", "CN Navigation"]
64	
65	  lead_model:
66	    type: string
67	    meaning: "主导车型"
68	    examples: ["BMW iX", "BMW 5 Series", "MINI Countryman"]
69	
70	  # From raw_json fields
71	  status_phase:
72	    type: enum
73	    meaning: "缺陷处理阶段"
74	    values: [New, Open, "In Progress", Fixed, Closed, Rejected, Deferred]
75	    lifecycle: "New → Open → In Progress → Fixed → Closed"
76	    category_groups:
77	      active: ["New", "Open", "In Progress"]
78	      resolved: ["Fixed", "Closed"]
79	      excluded: ["Rejected", "Deferred"]
80	    semantics:
81	      New: "新建缺陷，未开始处理"
82	      Open: "已指派处理人，正在分析"
83	      "In Progress": "正在修复或解决方案验证中"
84	      Fixed: "已修复，等待验证"
85	      Closed: "已验证通过，问题解决"
86	      Rejected: "不符合缺陷定义，拒绝处理"
87	      Deferred: "计划性延后处理"
88	
89	  severity:
90	    type: enum
91	    meaning: "严重程度"
92	    values: [Critical, Major, Minor, Cosmetic]
93	    semantics:
94	      Critical: "安全相关/法规不满足/功能完全丧失，必须立即处理"
95	      Major: "功能降级，影响用户使用体验"
96	      Minor: "功能异常但可绕过，或体验问题"
97	      Cosmetic: "外观/文案问题，不影响功能"
98	    business_rules:
99	      - "severity = Critical 且 status IN (New, Open, In Progress) 需要立即处理"
100	      - "severity 不等于 matrix，matrix 是从 tags 提取的标签"
101	
102	  assigned_ecu:
103	    type: string
104	    meaning: "指派的电子控制单元"
105	    examples: [BCM, VCU, MCU, BMS, ADAS, IHU]
106	    aliases:
107	      BCM: ["Body_Control_Module", "车身控制器", "车身模块"]
108	      VCU: ["Vehicle_Control_Unit", "整车控制器"]
109	      MCU: ["Motor_Control_Unit", "电机控制器"]
110	      BMS: ["Battery_Management_System", "电池管理系统"]
111	      ADAS: ["Advanced_Driver_Assistance_Systems", "高级驾驶辅助"]
112	      IHU: ["In-Vehicle_Human_Machine_Interface", "车载人机交互"]
113	
114	  problem_finder_team:
115	    type: string
116	    meaning: "问题发现团队"
117	
118	  top_aida:
119	    type: string
120	    meaning: "AIDA 功能域（一级）"
121	    examples: ["ent_and_con_cn", "cn_navigation", "cn_speech", "cn_media"]
122	    aliases:
123	      ent_and_con_cn: ["content", "内容", "娱乐"]
124	      cn_navigation: ["navigation", "导航", "nav"]
125	      cn_speech: ["speech", "语音"]
126	      cn_media: ["media", "媒体"]
127	
128	  aida_english:
129	    type: string
130	    meaning: "AIDA 功能域英文名称"
131	
132	  aida_businesskey:
133	    type: string
134	    meaning: "AIDA 业务键"
135	
136	  phase:
137	    type: string
138	    meaning: "测试阶段"
139	    category_groups:
140	      q_gate: ["02", "07"]
141	      integration: ["00", "01", "06", "08", "09"]
142	      coc: ["03", "04", "05"]
143	    semantics:
144	      "00": "Development phase"
145	      "01": "Early Integration"
146	      "02": "Q-Gate 1"
147	      "03": "CoC 1"
148	      "04": "CoC 2"
149	      "05": "CoC 3"
150	      "06": "Q-Gate 2"
151	      "07": "Q-Gate 3"
152	      "08": "Pre-production"
153	      "09": "Production"
154	
155	  solution_cluster:
156	    type: string
157	    meaning: "解决方案聚类"
158	    examples: ["solution cluster:china product", "ipa cn", "speech cn", "navigation cn"]
159	    category_groups:
160	      china: ["solution cluster:china product", "ipa cn", "speech cn", "navigation cn",
161	              "ent_and_con cn", "navigation twn", "etc jp"]
162	
163	  year:
164	    type: string
165	    meaning: "年份"
166	    examples: ["2026", "2025", "2024"]
167	
168	  # JSON fields (from requirements_json)
169	  requirement:
170	    type: array
171	    meaning: "关联的需求"
172	    item_type: string
173	
174	  raw_json:
175	    type: json
176	    meaning: "Octane 原始 JSON 数据"
177	
178	  creation_time:
179	    type: datetime
180	    meaning: "缺陷创建时间（用于趋势分析）"
181	
182	  last_modified:
183	    type: datetime
184	    meaning: "最后修改时间"
185	
186	  fetched_at:
187	    type: datetime
188	    meaning: "数据抓取时间"
189	
190	# Relationships to other objects
191	links:
192	  - name: has_history
193	    target: DefectHistory
194	    type: one-to-many
195	    join: defect.defect_id = history.defect_id
196	    meaning: "缺陷历史变更记录"
197	
198	  - name: tested_in_manual_run
199	    target: ManualRun
200	    type: one-to-many
201	    join: defect.defect_id = manual_run.defect_id
202	    meaning: "在手动测试中被发现的缺陷"
203	
204	  - name: related_to_testcases
205	    target: TestCase
206	    type: many-to-many
207	    via: octane_testcase_relations
208	    join: defect.defect_id = relations.related_id AND relations.relation_type = 'defect'
209	    meaning: "关联的测试用例"
210	
211	  - name: belongs_to_project
212	    target: Project
213	    type: many-to-one
214	    join: defect.project = project.name
215	    meaning: "所属项目"
216	
217	  - name: found_by_team
218	    target: Team
219	    type: many-to-one
220	    join: defect.problem_finder_team = team.name
221	    meaning: "发现问题的团队"
222	
223	# Pre-calculated metrics for frequent queries
224	metrics:
225	  active_defect_count:
226	    definition: "COUNT(*) WHERE status_phase IN ('New', 'Open', 'In Progress')"
227	    meaning: "活跃缺陷数（未关闭）"
228	
229	  critical_defect_count:
230	    definition: "COUNT(*) WHERE severity = 'Critical' AND status_phase IN ('New', 'Open', 'In Progress')"
231	    meaning: "未关闭的 Critical 缺陷数"
232	
233	  defect_density:
234	    definition: "defect_count / test_case_count * 100"
235	    meaning: "缺陷密度（每百用例缺陷数）"
236	
237	  china_defect_count:
238	    definition: "COUNT(*) WHERE top_aida IN CHINA_SOLUTION_CLUSTERS OR market = 'CN'"
239	    meaning: "中国区域缺陷数"
240	
241	  q_gate_defect_count:
242	    definition: "COUNT(*) WHERE phase IN ('02', '07')"
243	    meaning: "Q-Gate 阶段缺陷数"
244	
245	  coc_defect_count:
246	    definition: "COUNT(*) WHERE phase IN ('03', '04', '05')"
247	    meaning: "CoC 阶段缺陷数"
248	
249	# Business calibration rules - common misunderstandings
250	calibration_rules:
251	  - id: "cal_severity_not_matrix"
252	    trigger: ["severity", "严重度", "critical", "严重"]
253	    rule: "severity 是 Octane 原生字段（Critical/Major/Minor），matrix 是从 tags 提取的标签，不要混淆"
254	
255	  - id: "cal_trend_uses_creation_time"
256	    trigger: ["趋势", "trend", "新增", "走势", "变化"]
257	    rule: "趋势分析的时间维度用 creation_time（缺陷创建时间），不要用 last_modified"
258	
259	  - id: "cal_active_excludes_closed"
260	    trigger: ["活跃", "active", "未关闭", "待处理"]
261	    rule: "活跃缺陷 = status_phase IN ('New', 'Open', 'In Progress')，排除 Fixed/Closed/Rejected/Deferred"
262	
263	  - id: "cal_project_aliases"
264	    trigger: ["项目", "project", "车型", "车系"]
265	    rule: |
266	      IDCEVO 包含: IDCEVO, ENTRYEVO, NBTEVO, CDE
267	      IDC 包含: IDC, IDC23, HU-MGU_02_A
268	      MGU 包含: MGU, MGU22, BMWMGU
269	      China 项目: IDCEVO, IDC, MGU
270	      Global 项目: RSU, App"
271	
272	  - id: "cal_ecu_aliases"
273	    trigger: ["ecu", "电子控制", "模块", "控制器"]
274	    rule: |
275	      常见 ECU: BCM(车身), VCU(整车), MCU(电机), BMS(电池), ADAS(辅助驾驶), IHU(人机交互)
276	      assigned_ecu 字段可能有多个 ECU，逗号分隔"
277	
278	  - id: "cal_china_scope"
279	    trigger: ["china", "中国", "cn", "国产"]
280	    rule: |
281	      中国区域判断: market='CN' OR top_aida IN CHINA_SOLUTION_CLUSTERS
282	      CHINA_SOLUTION_CLUSTERS = {ent_and_con_cn, ipa cn, speech cn, navigation cn, navigation twn, etc jp}"
283	
284	  - id: "cal_phase_classification"
285	    trigger: ["phase", "阶段", "测试阶段"]
286	    rule: |
287	      Q-Gate: 02, 07
288	      Integration: 00, 01, 06, 08, 09
289	      CoC: 03, 04, 05
290	      Other: 其他值"
291	
292	# Governance - what operations are allowed/disallowed
293	governance:
294	  allow_operations:
295	    - read
296	    - filter
297	    - aggregate
298	    - join
299	  forbid_operations:
300	    - update
301	    - delete
302	    - insert
303	
304	  sensitive_fields:
305	    - raw_json
306	
307	  default_time_range: "90 days"

### Q13

1	# Project Object Type
2	# Project metadata
3	
4	object_type: Project
5	description: "项目/车型"
6	source_table: "derived"  # Derived from project values in other tables
7	primary_key: name
8	
9	properties:
10	  name:
11	    type: string
12	    meaning: "项目代号"
13	    values: [IDCEVO, IDC, MGU, RSU, App]
14	
15	  category:
16	    type: enum
17	    values: [china, global]
18	    meaning: "项目分类"
19	    mapping:
20	      IDCEVO: china
21	      IDC: china
22	      MGU: china
23	      RSU: global
24	      App: global
25	
26	  description:
27	    type: string
28	    meaning: "项目描述"
29	    values:
30	      IDCEVO: "中国专属信息娱乐系统"
31	      IDC: "智联座舱 2.0"
32	      MGU: "22 款 MGU 车型"
33	      RSU: "远程软件更新"
34	      App: "手机应用"
35	
36	links:
37	  - name: has_defects
38	    target: Defect
39	    type: one-to-many
40	    join: project.name = defect.project
41	    meaning: "项目关联的缺陷"
42	
43	  - name: has_manual_runs
44	    target: ManualRun
45	    type: one-to-many
46	    join: project.name = manual_run.project
47	    meaning: "项目关联的手动测试"
48	
49	calibration_rules:
50	  - id: "cal_china_projects"
51	    trigger: ["china", "中国", "cn", "国产项目"]
52	    rule: "China 项目: IDCEVO, IDC, MGU"
53	
54	  - id: "cal_global_projects"
55	    trigger: ["global", "全球", "intl", "国际项目"]
56	    rule: "Global 项目: RSU, App"

### Q14

1	# TestCase Object Type
2	# Test case definitions
3	
4	object_type: TestCase
5	description: "测试用例定义"
6	source_table: octane_testcases
7	primary_key: (test_id, scope_team, scope_release, source)
8	
9	properties:
10	  test_id:
11	    type: string
12	    meaning: "测试用例ID"
13	    examples: ["TC-2026-0001"]
14	
15	  scope_team:
16	    type: string
17	    meaning: "范围团队"
18	
19	  scope_release:
20	    type: string
21	    meaning: "范围发布版本"
22	
23	  source:
24	    type: string
25	    meaning: "数据来源"
26	    examples: ["Octane", "Manual"]
27	
28	  test_name:
29	    type: string
30	    meaning: "测试用例名称"
31	
32	  run_count:
33	    type: integer
34	    meaning: "执行次数"
35	
36	  defect_ids_json:
37	    type: array
38	    meaning: "关联的缺陷ID列表（JSON）"
39	    item_type: string
40	
41	  feature_ids_json:
42	    type: array
43	    meaning: "关联的功能ID列表（JSON）"
44	    item_type: string
45	
46	  story_ids_json:
47	    type: array
48	    meaning: "关联的需求故事ID列表（JSON）"
49	    item_type: string
50	
51	  raw_json:
52	    type: json
53	    meaning: "Octane 原始 JSON 数据"
54	
55	  fetched_at:
56	    type: datetime
57	    meaning: "数据抓取时间"
58	
59	links:
60	  - name: finds_defects
61	    target: Defect
62	    type: many-to-many
63	    via: defect_ids_json
64	    meaning: "测试用例发现的缺陷"
65	
66	  - name: has_relations
67	    target: TestCaseRelation
68	    type: one-to-many
69	    join: testcase.test_id = relations.test_id AND testcase.scope_team = relations.scope_team
70	    meaning: "测试用例关联关系"
71	
72	metrics:
73	  defect_detection_efficiency:
74	    definition: "COUNT(DISTINCT defect_ids_json) / run_count"
75	    meaning: "缺陷检测效率（每百次执行发现的缺陷数）"
76	
77	calibration_rules:
78	  - id: "cal_json_arrays"
79	    trigger: ["json", "array", "ids"]
80	    rule: "defect_ids_json, feature_ids_json, story_ids_json 是 JSON 数组字符串，需要 JSON.parse() 解析"

### Q15

1	"""Result Validator - MARS-SQL style independent verification
2	
3	Inspired by MARS-SQL (arXiv 2511.01008, 2026):
4	    Instead of just checking SQL syntax, an independent Validation Agent
5	    reviews the *execution result* against the user's question.
6	
7	    Two validation modes:
8	    1. Rule-based (always on): heuristic sanity checks
9	    2. LLM-based (when available): semantic consistency check
10	
11	Rule-based checks (fast, no API call):
12	    - Empty result for data-expecting queries
13	    - Suspiciously large result (>10K rows = likely missing WHERE)
14	    - All values identical (possible bug)
15	    - Type mismatch (expecting number, got string)
16	    - Count mismatch (SUM of distribution != total)
17	
18	LLM-based checks (when result passes rules but might be semantically wrong):
19	    - "Does this result answer the user's question?"
20	    - "Are the column names consistent with what was asked?"
21	    - "Is the magnitude reasonable?"
22	
23	Usage:
24	    from agent.sql_engine.validator import ResultValidator
25	
26	    validator = ResultValidator(llm_call_fn=client.as_fixer_fn())
27	    verdict = validator.validate(
28	        question="IDCEVO有多少Critical缺陷?",
29	        sql="SELECT COUNT(*) FROM ... WHERE project='IDCEVO' AND severity='Critical'",
30	        rows=[{"COUNT(*)": 23}],
31	        intent="count"
32	    )
33	    if not verdict.passed:
34	        print(verdict.reason)  # "Result is empty but question expects data"
35	"""
36	
37	from __future__ import annotations
38	
39	import re
40	import logging
41	from typing import List, Dict, Optional, Callable
42	from dataclasses import dataclass, field
43	from enum import Enum
44	
45	logger = logging.getLogger(__name__)
46	
47	
48	class ValidationLevel(Enum):
49	    """Severity of validation failure"""
50	    INFO = "info"         # Something noted, but OK to proceed
51	    WARNING = "warning"   # Suspicious, may want to retry
52	    ERROR = "error"       # Clearly wrong, must retry or report
53	
54	
55	@dataclass
56	class ValidationIssue:
57	    """A single validation finding"""
58	    level: ValidationLevel
59	    check: str            # Which check found this
60	    message: str
61	    suggestion: str = ""  # How to fix
62	
63	
64	@dataclass
65	class ValidationVerdict:
66	    """Overall validation result"""
67	    passed: bool                          # True if no ERROR-level issues
68	    issues: List[ValidationIssue] = field(default_factory=list)
69	    llm_verified: bool = False           # Whether LLM validation ran
70	    llm_reasoning: str = ""               # LLM's reasoning (if ran)
71	
72	    @property
73	    def primary_reason(self) -> str:
74	        """Main reason for failure (first ERROR issue)"""
75	        for issue in self.issues:
76	            if issue.level == ValidationLevel.ERROR:
77	                return issue.message
78	        for issue in self.issues:
79	            if issue.level == ValidationLevel.WARNING:
80	                return issue.message
81	        return ""
82	
83	
84	class ResultValidator:
85	    """
86	    Independent result validation (MARS-SQL style).
87	
88	    Validates that execution results actually answer the user's question.
89	    Works as a post-execution check, complementing the pre-execution SQL Fixer.
90	    """
91	
92	    # Questions that expect data (non-empty results)
93	    DATA_EXPECTING_PATTERNS = [
94	        "多少", "数量", "有几个", "几个", "count", "how many",
95	        "top", "排名", "ranking", "最", "most",
96	        "分布", "distribution", "breakdown",
97	        "列表", "列出", "list", "show",
98	        "趋势", "trend",
99	        "哪些", "which",
100	    ]
101	
102	    # Max rows before flagging as suspicious (likely missing WHERE)
103	    MAX_REASONABLE_ROWS = 10000
104	
105	    # Numeric intent types where result should be a number
106	    NUMERIC_INTENTS = {"count", "summary"}
107	
108	    def __init__(
109	        self,
110	        llm_call_fn: Optional[Callable[[str], str]] = None,
111	        enable_llm_validation: bool = True,
112	    ):
113	        """
114	        Args:
115	            llm_call_fn: Optional LLM callable for semantic validation.
116	                        Signature: fn(prompt: str) -> str
117	            enable_llm_validation: Whether to use LLM validation (can disable for speed)
118	        """
119	        self.llm_call_fn = llm_call_fn
120	        self.enable_llm = enable_llm_validation and llm_call_fn is not None
121	
122	    def validate(
123	        self,
124	        question: str,
125	        sql: str,
126	        rows: List[Dict],
127	        intent: str = "",
128	        columns: Optional[List[str]] = None,
129	    ) -> ValidationVerdict:
130	        """
131	        Validate execution result against the question.
132	
133	        Args:
134	            question: Original user question
135	            sql: SQL that was executed
136	            rows: Result rows
137	            intent: Detected intent type
138	            columns: Column names (inferred from rows if not provided)
139	
140	        Returns:
141	            ValidationVerdict with pass/fail and any issues
142	        """
143	        verdict = ValidationVerdict(passed=True)
144	
145	        if not columns:
146	            columns = list(rows[0].keys()) if rows else []
147	
148	        # --- Rule-based checks ---
149	
150	        # 1. Empty result check
151	        issue = self._check_empty_result(question, rows, intent)
152	        if issue:
153	            verdict.issues.append(issue)
154	
155	        # 2. Large result check
156	        issue = self._check_large_result(rows, sql, intent)
157	        if issue:
158	            verdict.issues.append(issue)
159	
160	        # 3. Uniform values check
161	        issue = self._check_uniform_values(rows, columns)
162	        if issue:
163	            verdict.issues.append(issue)
164	
165	        # 4. Count consistency check (for distribution queries)
166	        issue = self._check_distribution_consistency(rows, sql, intent)
167	        if issue:
168	            verdict.issues.append(issue)
169	
170	        # 5. SQL structure check (did SQL match intent?)
171	        issue = self._check_sql_intent_alignment(sql, intent, question)
172	        if issue:
173	            verdict.issues.append(issue)
174	
175	        # Determine if passed
176	        verdict.passed = not any(
177	            i.level == ValidationLevel.ERROR for i in verdict.issues
178	        )
179	
180	        # --- LLM-based validation (only if rule-based passed and LLM available) ---
181	        if verdict.passed and self.enable_llm and rows:
182	            llm_issue = self._llm_validate(question, sql, rows, intent)
183	            if llm_issue:
184	                verdict.issues.append(llm_issue)
185	                if llm_issue.level == ValidationLevel.ERROR:
186	                    verdict.passed = False
187	                verdict.llm_verified = True
188	                verdict.llm_reasoning = llm_issue.message
189	            else:
190	                verdict.llm_verified = True
191	                verdict.llm_reasoning = "LLM validation passed"
192	
193	        return verdict
194	
195	    # ==================== Rule-Based Checks ====================
196	
197	    def _check_empty_result(
198	        self, question: str, rows: List[Dict], intent: str
199	    ) -> Optional[ValidationIssue]:
200	        """Check: empty result for data-expecting questions"""
201	        if rows:
202	            return None
203	
204	        q_lower = question.lower()
205	        expects_data = any(p in q_lower for p in self.DATA_EXPECTING_PATTERNS)
206	
207	        if expects_data and intent != "count":
208	            return ValidationIssue(
209	                level=ValidationLevel.ERROR,
210	                check="empty_result",
211	                message="查询结果为空，但问题期望有数据。可能是过滤条件太严格或字段值不匹配。",
212	                suggestion="检查 WHERE 条件中的值是否正确，或放宽过滤条件。"
213	            )
214	
215	        return None
216	
217	    def _check_large_result(
218	        self, rows: List[Dict], sql: str, intent: str
219	    ) -> Optional[ValidationIssue]:
220	        """Check: suspiciously large result set"""
221	        row_count = len(rows)
222	        if row_count <= self.MAX_REASONABLE_ROWS:
223	            return None
224	
225	        sql_lower = sql.lower()
226	
227	        # If no WHERE clause and lots of rows, likely missing filter
228	        if "where" not in sql_lower:
229	            return ValidationIssue(
230	                level=ValidationLevel.ERROR,
231	                check="large_result_no_filter",
232	                message=f"返回 {row_count} 行且无 WHERE 条件，可能缺少过滤。",
233	                suggestion="添加 WHERE 条件限制结果范围。"
234	            )
235	
236	        return ValidationIssue(
237	            level=ValidationLevel.WARNING,
238	            check="large_result",
239	            message=f"返回 {row_count} 行，可能需要 LIMIT。",
240	            suggestion=f"添加 LIMIT 限制返回行数。"
241	        )
242	
243	    def _check_uniform_values(
244	        self, rows: List[Dict], columns: List[str]
245	    ) -> Optional[ValidationIssue]:
246	        """Check: all values in first column are identical (possible bug)"""
247	        if len(rows) < 3 or not columns:
248	            return None
249	
250	        first_col = columns[0]
251	        first_val = rows[0].get(first_col)
252	
253	        if first_val is None:
254	            return None
255	
256	        # Skip count columns (they're supposed to vary)
257	        if first_col.lower() in ("count", "cnt", "total"):
258	            return None
259	
260	        all_same = all(r.get(first_col) == first_val for r in rows[:20])
261	        if all_same:
262	            return ValidationIssue(
263	                level=ValidationLevel.WARNING,
264	                check="uniform_values",
265	                message=f"第一列 '{first_col}' 的所有值都是 '{first_val}'，可能是 GROUP BY 错误。",
266	                suggestion="检查 GROUP BY 字段是否正确。"
267	            )
268	
269	        return None
270	
271	    def _check_distribution_consistency(
272	        self, rows: List[Dict], sql: str, intent: str
273	    ) -> Optional[ValidationIssue]:
274	        """Check: distribution percentages sum to ~100%"""
275	        if intent != "distribution" or not rows:
276	            return None
277	
278	        # Look for pct column
279	        pct_values = []
280	        for row in rows:
281	            if "pct" in row and row["pct"] is not None:
282	                try:
283	                    pct_values.append(float(row["pct"]))
284	                except (ValueError, TypeError):
285	                    pass
286	
287	        if not pct_values:
288	            return None
289	
290	        total_pct = sum(pct_values)
291	        # Allow some tolerance for rounding
292	        if total_pct < 90 or total_pct > 110:
293	            return ValidationIssue(
294	                level=ValidationLevel.WARNING,
295	                check="pct_sum",
296	                message=f"分布百分比总和为 {total_pct:.1f}%，偏离 100% 较多。",
297	                suggestion="检查 SQL 中的百分比计算逻辑。"
298	            )
299	
300	        return None
301	
302	    def _check_sql_intent_alignment(
303	        self, sql: str, intent: str, question: str
304	    ) -> Optional[ValidationIssue]:
305	        """Check: SQL structure aligns with detected intent"""
306	        sql_lower = sql.lower()
307	
308	        # Count intent should have COUNT
309	        if intent == "count" and "count" not in sql_lower:
310	            return ValidationIssue(
311	                level=ValidationLevel.WARNING,
312	                check="intent_alignment",
313	                message="意图为'计数'，但SQL中无 COUNT 函数。",
314	                suggestion="添加 COUNT(*) 聚合。"
315	            )
316	
317	        # Trend intent should have time grouping
318	        if intent == "trend":
319	            has_time = any(x in sql_lower for x in ["strftime", "date(", "group by"])
320	            if not has_time:
321	                return ValidationIssue(
322	                    level=ValidationLevel.WARNING,
323	                    check="intent_alignment",
324	                    message="意图为'趋势'，但SQL中无时间分组。",
325	                    suggestion="添加按月份/日期的 GROUP BY。"
326	                )
327	
328	        # Ranking intent should have ORDER BY
329	        if intent == "ranking" and "order by" not in sql_lower:
330	            return ValidationIssue(
331	                level=ValidationLevel.WARNING,
332	                check="intent_alignment",
333	                message="意图为'排名'，但SQL中无 ORDER BY。",
334	                suggestion="添加 ORDER BY count DESC。"
335	            )
336	
337	        return None
338	
339	    # ==================== LLM-Based Validation ====================
340	
341	    def _llm_validate(
342	        self,
343	        question: str,
344	        sql: str,
345	        rows: List[Dict],
346	        intent: str,
347	    ) -> Optional[ValidationIssue]:
348	        """
349	        Use LLM to semantically validate the result.
350	
351	        Asks the LLM:
352	        - Does this result answer the question?
353	        - Is the magnitude reasonable?
354	        - Are there obvious errors?
355	        """
356	        # Prepare a sample of the data for the LLM
357	        sample = rows[:5]
358	        row_count = len(rows)
359	
360	        # Format columns
361	        columns = list(rows[0].keys()) if rows else []
362	
363	        prompt = f"""你是一个数据验证专家。请检查以下 SQL 查询结果是否正确回答了用户问题。
364	
365	## 用户问题
366	{question}
367	
368	## 执行的 SQL
369	```sql
370	{sql}
371	```
372	
373	## 查询结果
374	- 总行数: {row_count}
375	- 列: {columns}
376	- 前5行数据:
377	{sample}
378	
379	## 检查项
380	1. 结果是否回答了用户的问题？
381	2. 数据量是否合理？（不是0，也不是异常大）
382	3. 列名是否与问题相关？
383	4. 数值范围是否合理？
384	
385	## 输出格式
386	如果结果正确，只回复：PASS
387	如果有问题，回复：
388	FAIL: <问题描述>
389	
390	只回复 PASS 或 FAIL: ...，不要其他内容。"""
391	
392	        try:
393	            response = self.llm_call_fn(prompt).strip()
394	
395	            if response.upper().startswith("PASS"):
396	                return None  # Validation passed
397	
398	            if response.upper().startswith("FAIL"):
399	                reason = response[5:].strip().split("\n")[0]  # First line after FAIL:
400	                return ValidationIssue(
401	                    level=ValidationLevel.WARNING,
402	                    check="llm_semantic",
403	                    message=f"LLM 验证未通过: {reason}",
404	                    suggestion="考虑重新生成 SQL 或调整查询条件。"
405	                )
406	
407	            # Unparseable response → assume pass
408	            logger.debug(f"LLM validation unclear response: {response[:100]}")
409	            return None
410	
411	        except Exception as e:
412	            logger.warning(f"LLM validation failed: {e}")
413	            return None  # Don't fail on LLM errors
414	
415	
416	# ============================================================================
417	# Singleton
418	# ============================================================================
419	
420	_validator: Optional[ResultValidator] = None
421	
422	
423	def get_result_validator(
424	    llm_call_fn: Optional[Callable] = None,
425	    enable_llm: bool = True,
426	) -> ResultValidator:
427	    """Get or create singleton ResultValidator"""
428	    global _validator
429	    if _validator is None:
430	        _validator = ResultValidator(
431	            llm_call_fn=llm_call_fn,
432	            enable_llm_validation=enable_llm,
433	        )
434	    return _validator
435

### Q16

1	"""CHASE-SQL Multi-Path SQL Generator
2	
3	Inspired by CHASE-SQL (ICLR 2025): generates multiple SQL candidates
4	via different reasoning paths, then selects the best.
5	
6	Three generation paths:
7	- Path A: Direct generation (NL → SQL with full context)
8	- Path B: Divide & Conquer (decompose into sub-queries, combine)
9	- Path C: Execution plan reasoning (step-by-step plan → SQL)
10	
11	A selection LLM (or heuristic) then compares candidate results pairwise
12	and picks the best answer.
13	"""
14	
15	import re
16	import json
17	from typing import List, Optional, Dict, Tuple
18	from dataclasses import dataclass, field
19	from pathlib import Path
20	
21	from agent.ontology import OntologyEngine, get_ontology_engine
22	from agent.context.engine import ContextEngine
23	from agent.understand.term_resolver import get_term_resolver
24	from agent.understand.entity_extractor import EntityExtractor, get_entity_extractor, ExtractionResult
25	from agent.understand.intent_detector import IntentDetector, get_intent_detector, QueryIntent, IntentResult
26	from agent.sql_engine.examples import get_examples_by_intent, get_similar_examples
27	from agent.sql_engine.validator import ResultValidator, get_result_validator
28	
29	
30	@dataclass
31	class SQLCandidate:
32	    """A generated SQL candidate"""
33	    sql: str
34	    path: str           # "direct", "decomposed", "plan_based"
35	    explanation: str    # Reasoning behind this SQL
36	    confidence: float = 0.5
37	
38	
39	@dataclass
40	class QueryResult:
41	    """Final result of NL→SQL query"""
42	    question: str
43	    sql: str                        # Best SQL
44	    data: List[Dict] = field(default_factory=list)  # Query results
45	    answer: str = ""                # Natural language answer
46	    intent: str = ""
47	    candidates: List[SQLCandidate] = field(default_factory=list)
48	    entities: ExtractionResult = None
49	    error: Optional[str] = None
50	    validation_issues: List[Dict] = field(default_factory=list)   # MARS validation findings
51	    validation_llm_verified: bool = False
52	    multi_path_agreement: str = ""    # unanimous/majority/disagree/single
53	    multi_path_confidence: float = 0.0
54	
55	
56	class SQLGenerator:
57	    """
58	    Base SQL generator using Ontology context + entity extraction.
59	    Provides shared logic for all generation paths.
60	    """
61	
62	    def __init__(self, ontology: Optional[OntologyEngine] = None,
63	                 db_path: Optional[str] = None):
64	        self.ontology = ontology or get_ontology_engine()
65	        self.term_resolver = get_term_resolver(ontology)
66	        self.entity_extractor = get_entity_extractor(ontology)
67	        self.intent_detector = get_intent_detector()
68	        self.context_engine = ContextEngine(ontology=self.ontology, db_path=db_path)
69	        self.db_path = db_path
70	
71	        # Value Retriever (lazy init)
72	        self._value_retriever = None
73	
74	    @property
75	    def value_retriever(self):
76	        if self._value_retriever is None and self.db_path:
77	            try:
78	                from agent.data.value_retriever import ValueRetriever
79	                self._value_retriever = ValueRetriever(
80	                    db_path=self.db_path,
81	                    ontology=self.ontology,
82	                )
83	            except Exception as e:
84	                import logging
85	                logging.getLogger(__name__).warning(f"ValueRetriever init failed: {e}")
86	                self._value_retriever = False  # Mark as failed
87	        return self._value_retriever if self._value_retriever is not False else None
88	
89	    def analyze_question(self, question: str) -> Tuple[ExtractionResult, IntentResult, str]:
90	        """
91	        Full analysis: entity extraction + intent detection + context building.
92	        Shared across all generation paths.
93	        """
94	        # Extract entities
95	        entities = self.entity_extractor.extract(question)
96	
97	        # Detect intent
98	        intent = self.intent_detector.detect(question, entities)
99	
100	        # Build context
101	        context = self.context_engine.build_context(
102	            object_type="Defect",
103	            question=question,
104	            include_layers=[1, 2, 3, 4]  # Skip behavioral for now
105	        )
106	
107	        return entities, intent, context
108	
109	    def build_where_clause(self, entities: ExtractionResult,
110	                           object_type: str = "Defect",
111	                           question: str = "") -> str:
112	        """
113	        Build WHERE clause from extracted entities.
114	        Enhanced with ValueRetriever for dynamic value matching.
115	        """
116	        filters = self.entity_extractor.to_sql_filters(entities, object_type)
117	
118	        # Enhance with ValueRetriever if question provided
119	        if question and self.value_retriever:
120	            vr_hints = self.value_retriever.get_hints_for_question(question)
121	
122	            # Get fields already covered by entity extraction
123	            covered_fields = set()
124	            for e in entities.entities:
125	                if e.field and not e.field.startswith("__"):
126	                    covered_fields.add(e.field)
127	
128	            # Add VR hints for fields not yet covered
129	            for field_name, hint in vr_hints.items():
130	                if field_name not in covered_fields:
131	                    values = hint["matches"]
132	                    if len(values) == 1:
133	                        filters.append(f"{field_name} = '{values[0]}'")
134	                    elif len(values) > 1:
135	                        in_clause = ", ".join(f"'{v}'" for v in values)
136	                        filters.append(f"{field_name} IN ({in_clause})")
137	
138	        if not filters:
139	            return "1=1"
140	        return " AND ".join(filters)
141	
142	    def resolve_group_field(self, question: str, entities: ExtractionResult) -> str:
143	        """Determine the GROUP BY field from question/entities"""
144	        # Check entities for grouping hints
145	        for entity in entities.entities:
146	            if entity.entity_type in ("project", "ecu", "severity", "status",
147	                                       "team", "test_phase", "aida", "market"):
148	                return entity.field
149	
150	        # Check question text
151	        field_hints = {
152	            "项目": "project",
153	            "ECU": "assigned_ecu",
154	            "严重": "severity",
155	            "状态": "status_phase",
156	            "团队": "team",
157	            "阶段": "phase",
158	            "域": "top_aida",
159	        }
160	        for keyword, field_name in field_hints.items():
161	            if keyword in question:
162	                return field_name
163	
164	        return "project"  # Default
165	
166	    def resolve_time_field(self, question: str) -> str:
167	        """Determine time field for trend queries"""
168	        return "creation_time"  # Always use creation_time for trends
169	
170	    def resolve_limit(self, entities: ExtractionResult, default: int = 20) -> int:
171	        """Extract LIMIT from entities or return default"""
172	        limit_entity = entities.get_first("limit")
173	        if limit_entity:
174	            return int(limit_entity.value)
175	        return default
176	
177	
178	class DirectGenerator(SQLGenerator):
179	    """
180	    Path A: Direct NL→SQL generation.
181	
182	    Uses full context + few-shot examples to generate SQL directly.
183	    Best for straightforward queries.
184	    """
185	
186	    def generate(self, question: str) -> SQLCandidate:
187	        entities, intent, context = self.analyze_question(question)
188	
189	        # Get relevant few-shot examples
190	        examples = get_examples_by_intent(intent.primary.value, top_k=3)
191	        examples_text = "\n".join(
192	            f"问: {ex['question']}\nSQL: {ex['sql']}" for ex in examples
193	        )
194	
195	        # Build SQL from template
196	        where_clause = self.build_where_clause(entities, question=question)
197	        table = self.ontology.get_object("Defect").source_table
198	        group_field = self.resolve_group_field(question, entities)
199	        time_field = self.resolve_time_field(question)
200	        limit = self.resolve_limit(entities)
201	        id_field = self.ontology.get_object("Defect").primary_key
202	
203	        sql = self._fill_template(
204	            intent.sql_template,
205	            table=table,
206	            filters=where_clause,
207	            group_field=group_field,
208	            time_field=time_field,
209	            limit=limit,
210	            id_field=id_field
211	        )
212	
213	        return SQLCandidate(
214	            sql=sql,
215	            path="direct",
216	            explanation=f"直接生成: intent={intent.primary.value}, "
217	                       f"filters={where_clause[:80]}...",
218	            confidence=0.6
219	        )
220	
221	    def _fill_template(self, template: str, **kwargs) -> str:
222	        """Fill in SQL template placeholders"""
223	        sql = template
224	        for key, value in kwargs.items():
225	            sql = sql.replace("{" + key + "}", str(value))
226	
227	        # Clean up: if no LIMIT in template, don't add
228	        sql = sql.replace(" LIMIT {limit}", f" LIMIT {kwargs.get('limit', 20)}")
229	        sql = sql.rstrip()
230	
231	        return sql
232	
233	
234	class DecomposedGenerator(SQLGenerator):
235	    """
236	    Path B: Divide & Conquer.
237	
238	    Decomposes complex questions into sub-questions, generates SQL for each,
239	    then combines results.
240	
241	    Best for: "IDCEVO 各ECU的Critical缺陷，按团队分布"
242	    → Sub-1: WHERE project=IDCEVO AND severity=Critical GROUP BY assigned_ecu
243	    → Sub-2: WHERE project=IDCEVO AND severity=Critical GROUP BY team
244	    → Combine: GROUP BY assigned_ecu, team
245	    """
246	
247	    def generate(self, question: str) -> SQLCandidate:
248	        entities, intent, context = self.analyze_question(question)
249	
250	        table = self.ontology.get_object("Defect").source_table
251	        where_clause = self.build_where_clause(entities, question=question)
252	
253	        # Identify multiple dimensions in the question
254	        dimensions = self._find_dimensions(question, entities)
255	
256	        if len(dimensions) >= 2 and intent.needs_grouping:
257	            # Multi-dimensional grouping
258	            group_fields = ", ".join(dimensions)
259	            sql = f"SELECT {group_fields}, COUNT(*) as count FROM {table} WHERE {where_clause} GROUP BY {group_fields} ORDER BY count DESC"
260	        elif intent.needs_timeseries and dimensions:
261	            # Time series + dimension
262	            time_field = self.resolve_time_field(question)
263	            dim = dimensions[0]
264	            sql = (f"SELECT strftime('%Y-%m', {time_field}) as month, {dim}, "
265	                   f"COUNT(*) as count FROM {table} WHERE {where_clause} "
266	                   f"GROUP BY strftime('%Y-%m', {time_field}), {dim} "
267	                   f"ORDER BY month, {dim}")
268	        elif intent.primary == QueryIntent.COUNT and entities.has("numeric_constraint"):
269	            # Numeric constraint: HAVING COUNT > N
270	            nc_entity = entities.get_first("numeric_constraint")
271	            if nc_entity:
272	                group_field = self.resolve_group_field(question, entities)
273	                op = nc_entity.operator if nc_entity.operator != "=" else ">"
274	                sql = (f"SELECT {group_field}, COUNT(*) as count FROM {table} "
275	                       f"WHERE {where_clause} GROUP BY {group_field} "
276	                       f"HAVING COUNT(*) {op} {nc_entity.value} ORDER BY count DESC")
277	            else:
278	                sql = f"SELECT COUNT(*) FROM {table} WHERE {where_clause}"
279	        else:
280	            # Fall back to simple query
281	            if intent.needs_grouping:
282	                group_field = self.resolve_group_field(question, entities)
283	                sql = f"SELECT {group_field}, COUNT(*) as count FROM {table} WHERE {where_clause} GROUP BY {group_field} ORDER BY count DESC"
284	            elif intent.needs_aggregation:
285	                sql = f"SELECT COUNT(*) FROM {table} WHERE {where_clause}"
286	            else:
287	                limit = self.resolve_limit(entities)
288	                sql = f"SELECT * FROM {table} WHERE {where_clause} LIMIT {limit}"
289	
290	        return SQLCandidate(
291	            sql=sql,
292	            path="decomposed",
293	            explanation=f"分治策略: dimensions={dimensions}, intent={intent.primary.value}",
294	            confidence=0.65
295	        )
296	
297	    def _find_dimensions(self, question: str, entities: ExtractionResult) -> List[str]:
298	        """Find grouping dimensions from question and entities"""
299	        dims = []
300	        seen = set()
301	
302	        # From entities
303	        dim_types = ["project", "ecu", "severity", "status", "team",
304	                     "test_phase", "aida", "market", "solution_cluster"]
305	        for entity in entities.entities:
306	            if entity.entity_type in dim_types and entity.field not in seen:
307	                dims.append(entity.field)
308	                seen.add(entity.field)
309	
310	        # From question text
311	        text_dims = {
312	            "项目": "project", "ECU": "assigned_ecu", "严重": "severity",
313	            "状态": "status_phase", "团队": "team", "阶段": "phase",
314	            "域": "top_aida", "市场": "market",
315	        }
316	        for keyword, field_name in text_dims.items():
317	            if keyword in question and field_name not in seen:
318	                # Only add if it's a grouping dimension (not a filter)
319	                has_filter = any(e.field == field_name for e in entities.entities
320	                                if e.entity_type in dim_types)
321	                if not has_filter:
322	                    dims.append(field_name)
323	                    seen.add(field_name)
324	
325	        return dims
326	
327	
328	class PlanBasedGenerator(SQLGenerator):
329	    """
330	    Path C: Execution plan reasoning.
331	
332	    Creates a step-by-step execution plan, then generates SQL.
333	    Best for complex analytical queries.
334	
335	    Example:
336	        "IDCEVO 风险最高的3个缺陷"
337	        → Plan:
338	          1. Filter: project = 'IDCEVO'
339	          2. Order by: risk_score DESC
340	          3. Limit: 3
341	        → SQL: SELECT defect_id, name, severity, ... FROM octane_defects
342	               WHERE project = 'IDCEVO' ORDER BY severity DESC, creation_time DESC LIMIT 3
343	    """
344	
345	    def generate(self, question: str) -> SQLCandidate:
346	        entities, intent, context = self.analyze_question(question)
347	
348	        table = self.ontology.get_object("Defect").source_table
349	        pk = self.ontology.get_object("Defect").primary_key
350	        where_clause = self.build_where_clause(entities, question=question)
351	
352	        # Build execution plan
353	        plan_steps = []
354	
355	        # Step 1: Base filter
356	        plan_steps.append(f"1. 过滤: WHERE {where_clause}")
357	
358	        # Step 2: Determine SELECT columns
359	        if intent.primary in (QueryIntent.COUNT, QueryIntent.SUMMARY):
360	            select_cols = "COUNT(*)"
361	            if intent.needs_grouping:
362	                group_field = self.resolve_group_field(question, entities)
363	                select_cols = f"{group_field}, COUNT(*) as count"
364	        elif intent.primary == QueryIntent.DETAIL_LIST:
365	            # Select meaningful columns
366	            obj = self.ontology.get_object("Defect")
367	            detail_cols = ["defect_id", "name", "project", "severity",
368	                          "status_phase", "assigned_ecu", "creation_time"]
369	            select_cols = ", ".join(detail_cols)
370	        elif intent.primary == QueryIntent.STATUS_CHECK:
371	            select_cols = "defect_id, name, status_phase, severity, last_modified"
372	        elif intent.primary == QueryIntent.RANKING:
373	            group_field = self.resolve_group_field(question, entities)
374	            select_cols = f"{group_field}, COUNT(*) as count"
375	        else:
376	            select_cols = "*"
377	
378	        # Step 3: Grouping
379	        group_clause = ""
380	        if intent.needs_grouping:
381	            group_field = self.resolve_group_field(question, entities)
382	            group_clause = f" GROUP BY {group_field}"
383	            plan_steps.append(f"2. 分组: GROUP BY {group_field}")
384	
385	        # Step 4: Ordering
386	        order_clause = ""
387	        if intent.primary == QueryIntent.RANKING:
388	            order_clause = " ORDER BY count DESC"
389	            plan_steps.append("3. 排序: ORDER BY count DESC")
390	        elif intent.primary == QueryIntent.DETAIL_LIST:
391	            order_clause = " ORDER BY creation_time DESC"
392	            plan_steps.append("3. 排序: ORDER BY creation_time DESC")
393	        elif intent.primary == QueryIntent.STATUS_CHECK:
394	            order_clause = " ORDER BY last_modified DESC"
395	            plan_steps.append("3. 排序: ORDER BY last_modified DESC")
396	        elif intent.needs_grouping:
397	            order_clause = " ORDER BY count DESC"
398	            plan_steps.append("3. 排序: ORDER BY count DESC")
399	
400	        # Step 5: Limit
401	        limit_clause = ""
402	        if intent.primary in (QueryIntent.RANKING, QueryIntent.DETAIL_LIST,
403	                              QueryIntent.STATUS_CHECK):
404	            limit = self.resolve_limit(entities, default=20)
405	            limit_clause = f" LIMIT {limit}"
406	            plan_steps.append(f"4. 限制: LIMIT {limit}")
407	        elif intent.primary == QueryIntent.TREND:
408	            limit_clause = ""  # Trends usually don't need limits
409	
410	        # Build final SQL
411	        sql = f"SELECT {select_cols} FROM {table} WHERE {where_clause}{group_clause}{order_clause}{limit_clause}"
412	
413	        # Special handling for trend
414	        if intent.primary == QueryIntent.TREND:
415	            time_field = self.resolve_time_field(question)
416	            sql = (f"SELECT strftime('%Y-%m', {time_field}) as month, COUNT(*) as count "
417	                   f"FROM {table} WHERE {where_clause} "
418	                   f"GROUP BY strftime('%Y-%m', {time_field}) ORDER BY month")
419	
420	        # Special handling for distribution with percentage
421	        if intent.primary == QueryIntent.DISTRIBUTION and "占比" in question:
422	            group_field = self.resolve_group_field(question, entities)
423	            sql = (f"SELECT {group_field}, COUNT(*) as count, "
424	                   f"ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM {table} WHERE {where_clause}), 1) as pct "
425	                   f"FROM {table} WHERE {where_clause} "
426	                   f"GROUP BY {group_field} ORDER BY count DESC")
427	
428	        plan_text = "\n".join(plan_steps)
429	        return SQLCandidate(
430	            sql=sql,
431	            path="plan_based",
432	            explanation=f"执行计划:\n{plan_text}",
433	            confidence=0.7
434	        )
435	
436	
437	class NL2SQLEngine:
438	    """
439	    Main NL→SQL Engine: CHASE-SQL multi-path generation + selection.
440	
441	    Flow:
442	    1. Analyze question (entities + intent + context)
443	    2. Generate 3 SQL candidates via different paths
444	    3. (Optionally execute and) Select best candidate
445	    4. Return result
446	
447	    Usage:
448	        engine = NL2SQLEngine()
449	        result = engine.query("IDCEVO 本月 Critical 缺陷有多少")
450	        print(result.sql)  # SELECT COUNT(*) FROM octane_defects WHERE ...
451	    """
452	
453	    def __init__(self, ontology: Optional[OntologyEngine] = None,
454	                 db_path: Optional[str] = None,
455	                 llm_call_fn: Optional = None,
456	                 use_query_fixer: bool = True,
457	                 use_validator: bool = True):
458	        self.direct_gen = DirectGenerator(ontology, db_path)
459	        self.decomposed_gen = DecomposedGenerator(ontology, db_path)
460	        self.plan_gen = PlanBasedGenerator(ontology, db_path)
461	        self.db_path = db_path
462	        self.llm_call_fn = llm_call_fn
463	
464	        # Query Fixer (self-correction)
465	        self.use_query_fixer = use_query_fixer
466	        if use_query_fixer:
467	            from agent.sql_engine.fixer import QueryFixer
468	            self.query_fixer = QueryFixer(
469	                db_path=self.db_path,
470	                llm_call_fn=llm_call_fn
471	            )
472	        else:
473	            self.query_fixer = None
474	
475	        # Result Validator (MARS-style verification)
476	        self.use_validator = use_validator
477	        if use_validator:
478	            self.validator = ResultValidator(
479	                llm_call_fn=llm_call_fn,
480	                enable_llm_validation=llm_call_fn is not None,
481	            )
482	        else:
483	            self.validator = None
484	
485	        # Multi-Path Executor (execution-guided selection)
486	        self.multi_executor = None
487	        if db_path:
488	            from agent.sql_engine.multi_executor import MultiPathExecutor
489	            self.multi_executor = MultiPathExecutor(
490	                db_path=db_path,
491	                llm_call_fn=llm_call_fn,
492	            )
493	
494	    def generate_candidates(self, question: str) -> List[SQLCandidate]:
495	        """Generate all SQL candidates via 3 paths"""
496	        candidates = []
497	
498	        try:
499	            candidates.append(self.direct_gen.generate(question))
500	        except Exception as e:
501	            pass  # One path failing shouldn't block others
502	
503	        try:
504	            candidates.append(self.decomposed_gen.generate(question))
505	        except Exception as e:
506	            pass
507	
508	        try:
509	            candidates.append(self.plan_gen.generate(question))
510	        except Exception as e:
511	            pass
512	
513	        return candidates
514	
515	    def select_best(self, question: str,
516	                    candidates: List[SQLCandidate],
517	                    entities: ExtractionResult,
518	                    intent: IntentResult) -> SQLCandidate:
519	        """
520	        Select the best SQL candidate using heuristics.
521	
522	        In production, this would use an LLM to compare candidates pairwise.
523	        For now, we use rule-based scoring.
524	        """
525	        if not candidates:
526	            # Fallback: simple count query
527	            table = "octane_defects"
528	            return SQLCandidate(
529	                sql=f"SELECT COUNT(*) FROM {table}",
530	                path="fallback",
531	                explanation="Fallback: no candidate succeeded",
532	                confidence=0.3
533	            )
534	
535	        if len(candidates) == 1:
536	            return candidates[0]
537	
538	        # Score each candidate
539	        scored = [(c, self._score_candidate(c, question, entities, intent))
540	                  for c in candidates]
541	        scored.sort(key=lambda x: x[1], reverse=True)
542	
543	        return scored[0][0]
544	
545	    def _score_candidate(self, candidate: SQLCandidate, question: str,
546	                         entities: ExtractionResult,
547	                         intent: IntentResult) -> float:
548	        """Score a SQL candidate (higher is better)"""
549	        score = candidate.confidence
550	
551	        sql_lower = candidate.sql.lower()
552	
553	        # Bonus: covers all filter entities
554	        for entity in entities.entities:
555	            if entity.field and not entity.field.startswith("__"):
556	                if entity.field in sql_lower:
557	                    score += 0.1
558	
559	        # Bonus: correct aggregation
560	        if intent.needs_aggregation and "count" in sql_lower:
561	            score += 0.1
562	        if intent.needs_grouping and "group by" in sql_lower:
563	            score += 0.15
564	        if intent.needs_timeseries and ("strftime" in sql_lower or "date(" in sql_lower):
565	            score += 0.15
566	
567	        # Penalty: missing WHERE when entities exist
568	        filter_entities = [e for e in entities.entities
569	                          if e.field and not e.field.startswith("__")
570	                          and e.entity_type not in ("aggregation", "sort", "metric")]
571	        if filter_entities and "where" not in sql_lower:
572	            score -= 0.3
573	
574	        # Penalty: SELECT * for count queries
575	        if intent.primary == QueryIntent.COUNT and "select *" in sql_lower:
576	            score -= 0.2
577	
578	        # Bonus: plan-based path for complex queries
579	        if candidate.path == "plan_based" and intent.confidence > 0.5:
580	            score += 0.05
581	
582	        # Bonus: decomposed path for multi-dimensional queries
583	        if candidate.path == "decomposed":
584	            dim_count = sql_lower.count(",") - sql_lower.count("count")
585	            if dim_count > 0:
586	                score += 0.05
587	
588	        return score
589	
590	    def query(self, question: str) -> QueryResult:
591	        """
592	        Full NL→SQL pipeline:
593	        1. Analyze
594	        2. Generate candidates (3 paths)
595	        3. Multi-Path Execution: run all candidates, compare results
596	        4. Self-Correction: fix best SQL if needed (Query Fixer)
597	        5. Validate result (MARS-style Result Validator)
598	        """
599	        # 1. Analyze
600	        entities, intent, context = self.direct_gen.analyze_question(question)
601	
602	        # 2. Generate candidates
603	        candidates = self.generate_candidates(question)
604	
605	        # 3. Select best (static scoring)
606	        best = self.select_best(question, candidates, entities, intent)
607	
608	        result = QueryResult(
609	            question=question,
610	            sql=best.sql,
611	            intent=intent.primary.value,
612	            candidates=candidates,
613	            entities=entities
614	        )
615	
616	        # Execute if database available
617	        if self.db_path:
618	            # === Multi-Path Execution (new) ===
619	            if self.multi_executor and len(candidates) >= 2:
620	                multi_result = self.multi_executor.execute_and_compare(
621	                    candidates=candidates,
622	                    question=question,
623	                    intent=intent.primary.value,
624	                )
625	
626	                # Use the multi-path winner
627	                result.sql = multi_result.best_sql
628	                result.data = multi_result.best_data
629	
630	                # If agreement is high, skip fixer (high confidence)
631	                if multi_result.agreement.value in ("unanimous", "majority"):
632	                    # Still run validator, but skip fixer
633	                    if self.validator:
634	                        verdict = self.validator.validate(
635	                            question=question,
636	                            sql=multi_result.best_sql,
637	                            rows=multi_result.best_data,
638	                            intent=intent.primary.value,
639	                        )
640	                        if not verdict.passed:
641	                            result.error = f"Validation: {verdict.primary_reason}"
642	                        result.validation_issues = [
643	                            {"level": i.level.value, "check": i.check, "message": i.message}
644	                            for i in verdict.issues
645	                        ]
646	                        result.validation_llm_verified = verdict.llm_verified
647	
648	                    result.multi_path_agreement = multi_result.agreement.value
649	                    result.multi_path_confidence = multi_result.confidence
650	                    return result
651	
652	                # If disagreement or single candidate, fall through to fixer
653	                # for the multi-path winner
654	                best_sql = multi_result.best_sql
655	                best_data = multi_result.best_data
656	            else:
657	                best_sql = best.sql
658	                best_data = None
659	
660	            # === Self-Correction (Query Fixer) ===
661	            if self.query_fixer:
662	                schema_ctx = self._get_schema_context()
663	                exec_result = self.query_fixer.execute(
664	                    best_sql,
665	                    question=question,
666	                    schema_context=schema_ctx
667	                )
668	                if exec_result.success:
669	                    result.data = exec_result.rows if not best_data else best_data
670	
671	                    # MARS-style validation
672	                    if self.validator:
673	                        verdict = self.validator.validate(
674	                            question=question,
675	                            sql=best_sql,
676	                            rows=exec_result.rows,
677	                            intent=intent.primary.value,
678	                            columns=exec_result.columns,
679	                        )
680	                        if not verdict.passed:
681	                            result.error = f"Validation: {verdict.primary_reason}"
682	                        result.validation_issues = [
683	                            {"level": i.level.value, "check": i.check, "message": i.message}
684	                            for i in verdict.issues
685	                        ]
686	                        result.validation_llm_verified = verdict.llm_verified
687	                else:
688	                    result.error = exec_result.error
689	            else:
690	                # Legacy execution
691	                data, error = self._execute_sql(best_sql)
692	                if error:
693	                    result.error = error
694	                else:
695	                    result.data = data
696	
697	        return result
698	
699	    def _execute_sql(self, sql: str) -> Tuple[List[Dict], Optional[str]]:
700	        """Execute SQL and return results (legacy path, used if no fixer)"""
701	        import sqlite3
702	        try:
703	            conn = sqlite3.connect(self.db_path)
704	            conn.row_factory = sqlite3.Row
705	            cursor = conn.cursor()
706	            cursor.execute(sql)
707	            rows = cursor.fetchall()
708	            conn.close()
709	            return [dict(row) for row in rows], None
710	        except Exception as e:
711	            return [], str(e)
712	
713	    def _get_schema_context(self) -> str:
714	        """Get database schema context for LLM fixing"""
715	        # Get main table info from ontology
716	        defect_obj = self.direct_gen.ontology.get_object("Defect")
717	        test_obj = self.direct_gen.ontology.get_object("ManualRun")
718	
719	        lines = []
720	        lines.append(f"Table: {defect_obj.source_table}")
721	        for prop_name, prop_def in defect_obj.properties.items():
722	            mapping = getattr(prop_def, 'mapping', None)
723	            source_col = mapping.get('column', prop_name) if mapping else prop_name
724	            lines.append(f"  - {source_col} ({prop_def.type.value}): {prop_def.meaning}")
725	
726	        if test_obj:
727	            lines.append(f"\nTable: {test_obj.source_table}")
728	            for prop_name, prop_def in test_obj.properties.items():
729	                mapping = getattr(prop_def, 'mapping', None)
730	                source_col = mapping.get('column', prop_name) if mapping else prop_name
731	                lines.append(f"  - {source_col} ({prop_def.type.value}): {prop_def.meaning}")
732	
733	        return "\n".join(lines)
734	
735	    def to_prompt_context(self, question: str) -> str:
736	        """
737	        Generate a prompt context for LLM-based SQL generation.
738	        Combines context + entities + intent + few-shot examples.
739	        """
740	        entities, intent, context = self.direct_gen.analyze_question(question)
741	
742	        # Few-shot examples
743	        similar = get_similar_examples(question, top_k=3)
744	        examples_text = "\n".join(
745	            f"示例:\n  问: {ex['question']}\n  SQL: {ex['sql']}\n  说明: {ex['explanation']}"
746	            for ex in similar
747	        )
748	
749	        # Entity summary
750	        entity_lines = []
751	        for e in entities.entities:
752	            if e.values:
753	                entity_lines.append(f"  - {e.entity_type}: {e.original} → {e.field} IN {e.values}")
754	            else:
755	                entity_lines.append(f"  - {e.entity_type}: {e.original} → {e.field} {e.operator} '{e.value}'")
756	
757	        entities_text = "\n".join(entity_lines) if entity_lines else "  (无特定实体)"
758	
759	        # Value Retrieval hints
760	        value_hints_text = "  (无额外值匹配)"
761	        vr = self.direct_gen.value_retriever
762	        if vr:
763	            vr_hints = vr.get_hints_for_question(question)
764	            if vr_hints:
765	                hint_lines = []
766	                for field_name, hint in vr_hints.items():
767	                    hint_lines.append(f"  - {field_name}: 匹配值 = {hint['matches']} (用户原文: '{hint['query']}')")
768	                value_hints_text = "\n".join(hint_lines)
769	
770	        return f"""# 查询分析
771	
772	## 用户问题
773	{question}
774	
775	## 意图
776	- 主意图: {intent.primary.value} ({intent.description})
777	- SQL模板: {intent.sql_template}
778	- 需要聚合: {intent.needs_aggregation}
779	- 需要分组: {intent.needs_grouping}
780	- 需要时序: {intent.needs_timeseries}
781	
782	## 提取的实体
783	{entities_text}
784	
785	## 数据库值匹配 (Value Retrieval)
786	{value_hints}
787	
788	## 数据库语义上下文
789	{context[:2000]}...
790	
791	## 参考示例
792	{examples_text}
793	"""
794	
795	
796	# Singleton
797	_engine: Optional[NL2SQLEngine] = None
798	
799	
800	def get_nl2sql_engine(ontology: Optional[OntologyEngine] = None,
801	                      db_path: Optional[str] = None,
802	                      llm_call_fn: Optional = None,
803	                      use_query_fixer: bool = True,
804	                      use_validator: bool = True) -> NL2SQLEngine:
805	    global _engine
806	    if _engine is None:
807	        _engine = NL2SQLEngine(ontology, db_path, llm_call_fn, use_query_fixer, use_validator)
808	    return _engine
809

### Q17

1	"""
2	Query Fixer - Self-Correction for SQL
3	
4	Based on CHASE-SQL ICLR 2025 Algorithm 4 (Query Fixer):
5	  - Execute SQL → catch error
6	  - Feed error + original SQL + question to LLM
7	  - Generate fixed SQL
8	  - Retry up to β times (β=3)
9	  - Drop unfixable candidates
10	
11	This handles:
12	  - Syntax errors
13	  - Missing tables/columns
14	  - Type mismatches
15	  - Logical errors (detected via result sanity checks)
16	"""
17	
18	from __future__ import annotations
19	
20	import sqlite3
21	import re
22	from dataclasses import dataclass
23	from typing import Optional, Dict, List, Callable
24	from datetime import datetime
25	
26	
27	@dataclass
28	class FixResult:
29	    """Result of query fixing attempt"""
30	    fixed_sql: Optional[str]
31	    success: bool
32	    iterations: int
33	    error_message: Optional[str] = None
34	    reasoning: str = ""
35	
36	
37	@dataclass
38	class ExecutionResult:
39	    """Result of SQL execution"""
40	    success: bool
41	    rows: List[Dict]
42	    error: Optional[str]
43	    columns: List[str]
44	    rowcount: int
45	
46	
47	class QueryFixer:
48	    """
49	    Self-correcting SQL executor.
50	
51	    Workflow:
52	      1. Try executing SQL
53	      2. On error, call LLM to fix
54	      3. Retry with fixed SQL (max β=3 attempts)
55	      4. If no fix after β attempts, mark as unfixable
56	
57	    LLM prompt template:
58	        Error executing SQL: {error_message}
59	        Original SQL: {original_sql}
60	        Question we're trying to answer: {question}
61	        Database schema (relevant tables/columns): {schema_context}
62	        Please provide a corrected SQL query that fixes the error.
63	        Explain your reasoning briefly.
64	    """
65	
66	    def __init__(self, db_path: str, llm_call_fn: Optional[Callable] = None):
67	        """
68	        Args:
69	            db_path: Path to SQLite database
70	            llm_call_fn: Optional LLM callable for fixing queries.
71	                        If None, use rule-based fallback.
72	        """
73	        self.db_path = db_path
74	        self.llm_call_fn = llm_call_fn
75	        self.max_attempts = 3  # CHASE-SQL uses β=3
76	
77	    def execute(
78	        self,
79	        sql: str,
80	        question: str = "",
81	        schema_context: str = ""
82	    ) -> ExecutionResult:
83	        """
84	        Execute SQL with self-correction.
85	
86	        Args:
87	            sql: SQL query to execute
88	            question: Original natural language question (for LLM context)
89	            schema_context: Database schema info (for LLM context)
90	
91	        Returns:
92	            ExecutionResult with rows or error
93	        """
94	        current_sql = sql
95	
96	        for attempt in range(1, self.max_attempts + 1):
97	            # Try execution
98	            try:
99	                result = self._try_execute(current_sql)
100	
101	                # Sanity check the result
102	                if result.success:
103	                    if not self._is_result_sane(result, question):
104	                        # Result looks wrong (empty/abnormal), try to fix
105	                        if self.llm_call_fn:
106	                            fix = self._llm_fix(
107	                                current_sql,
108	                                f"Query succeeded but result looks abnormal:\n{self._format_result(result)}",
109	                                question,
110	                                schema_context
111	                            )
112	                            if fix.success and fix.fixed_sql:
113	                                current_sql = fix.fixed_sql
114	                                continue
115	                        else:
116	                            # Rule-based fallback: mark as failed
117	                            result.success = False
118	                            result.error = "Result sanity check failed"
119	
120	                if result.success:
121	                    return result
122	
123	                # Execution failed (syntax/table error)
124	                # If no LLM, return error immediately on first attempt
125	                if not self.llm_call_fn:
126	                    return result
127	
128	                # With LLM, try to fix
129	                if result.error:
130	                    fix = self._llm_fix(
131	                        current_sql,
132	                        result.error,
133	                        question,
134	                        schema_context
135	                    )
136	                    if fix.success and fix.fixed_sql:
137	                        current_sql = fix.fixed_sql
138	                        continue
139	                    else:
140	                        return result
141	
142	            except sqlite3.Error as e:
143	                # SQL execution error (shouldn't reach here, _try_execute catches)
144	                if not self.llm_call_fn:
145	                    return ExecutionResult(
146	                        success=False,
147	                        rows=[],
148	                        error=str(e),
149	                        columns=[],
150	                        rowcount=0
151	                    )
152	
153	                fix = self._llm_fix(
154	                    current_sql,
155	                    str(e),
156	                    question,
157	                    schema_context
158	                )
159	
160	                if fix.success and fix.fixed_sql:
161	                    current_sql = fix.fixed_sql
162	                    continue
163	                else:
164	                    return ExecutionResult(
165	                        success=False,
166	                        rows=[],
167	                        error=f"{e} (unfixable after {attempt} attempts)",
168	                        columns=[],
169	                        rowcount=0
170	                    )
171	
172	        # Max attempts exhausted
173	        return ExecutionResult(
174	            success=False,
175	            rows=[],
176	            error="Max fix attempts exhausted",
177	            columns=[],
178	            rowcount=0
179	        )
180	
181	    def _try_execute(self, sql: str) -> ExecutionResult:
182	        """Attempt single SQL execution"""
183	        try:
184	            conn = sqlite3.connect(self.db_path)
185	            conn.row_factory = sqlite3.Row
186	            cursor = conn.execute(sql)
187	            rows = cursor.fetchall()
188	
189	            columns = [d[0] for d in cursor.description] if cursor.description else []
190	            result_rows = [dict(r) for r in rows]
191	
192	            conn.close()
193	
194	            return ExecutionResult(
195	                success=True,
196	                rows=result_rows,
197	                error=None,
198	                columns=columns,
199	                rowcount=len(result_rows)
200	            )
201	
202	        except sqlite3.Error as e:
203	            return ExecutionResult(
204	                success=False,
205	                rows=[],
206	                error=str(e),
207	                columns=[],
208	                rowcount=0
209	            )
210	
211	    def _llm_fix(
212	        self,
213	        original_sql: str,
214	        error_message: str,
215	        question: str,
216	        schema_context: str
217	    ) -> FixResult:
218	        """
219	        Use LLM to fix SQL query.
220	
221	        Returns:
222	            FixResult with fixed SQL and reasoning
223	        """
224	        if not self.llm_call_fn:
225	            return FixResult(
226	                fixed_sql=None,
227	                success=False,
228	                iterations=0,
229	                error_message="No LLM available for fixing"
230	            )
231	
232	        prompt = f"""
233	You are a SQL expert. Fix the following SQL query.
234	
235	## Error
236	{error_message}
237	
238	## Original SQL
239	```sql
240	{original_sql}
241	```
242	
243	## Question
244	{question}
245	
246	## Database Schema
247	{schema_context}
248	
249	## Instructions
250	1. Analyze the error and identify what's wrong
251	2. Provide a corrected SQL query
252	3. Explain briefly what you fixed
253	
254	## Output Format
255	```
256	REASONING:
257	Your explanation here...
258	
259	FIXED_SQL:
260	SELECT ...
261	```
262	"""
263	
264	        try:
265	            response = self.llm_call_fn(prompt)
266	
267	            # Parse response
268	            reasoning = ""
269	            fixed_sql = None
270	
271	            # Extract reasoning
272	            reasoning_match = re.search(r"REASONING:\s*(.+?)(?=\nFIXED_SQL:|\n\n|$)", response, re.DOTALL)
273	            if reasoning_match:
274	                reasoning = reasoning_match.group(1).strip()
275	
276	            # Extract SQL
277	            sql_match = re.search(r"FIXED_SQL:\s*(.+?)(?=\n\n|$)", response, re.DOTALL)
278	            if sql_match:
279	                fixed_sql = sql_match.group(1).strip()
280	
281	            # Validate extracted SQL
282	            if fixed_sql and self._sql_looks_valid(fixed_sql):
283	                return FixResult(
284	                    fixed_sql=fixed_sql,
285	                    success=True,
286	                    iterations=1,
287	                    reasoning=reasoning
288	                )
289	            else:
290	                return FixResult(
291	                    fixed_sql=None,
292	                    success=False,
293	                    iterations=1,
294	                    error_message="Failed to parse valid SQL from LLM response"
295	                )
296	
297	        except Exception as e:
298	            return FixResult(
299	                fixed_sql=None,
300	                success=False,
301	                iterations=1,
302	                error_message=f"LLM fix failed: {str(e)}"
303	            )
304	
305	    def _sql_looks_valid(self, sql: str) -> bool:
306	        """Basic validation that extracted text looks like SQL"""
307	        sql = sql.strip()
308	
309	        # Must start with SELECT or other DML (not DROP/DELETE/UPDATE for safety)
310	        if not re.match(r"^\s*(SELECT|WITH|SELECT\s+)", sql, re.IGNORECASE):
311	            return False
312	
313	        # Check for forbidden operations
314	        forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
315	        for op in forbidden:
316	            if re.search(rf"\b{op}\b", sql, re.IGNORECASE):
317	                return False
318	
319	        return True
320	
321	    def _is_result_sane(self, result: ExecutionResult, question: str) -> bool:
322	        """
323	        Check if execution result looks reasonable.
324	
325	        Heuristics:
326	        - For count queries: result should be a single number, not empty
327	        - For ranking/distribution: result should have > 0 rows
328	        - For all queries: result shouldn't be suspiciously large (>10K rows)
329	        - Values shouldn't all be the same (possible bug)
330	        """
331	        # Empty result might be OK for count (should be 0), but check
332	        if result.rowcount == 0:
333	            # For queries expecting data, empty is suspicious
334	            # Check if question words suggest expecting data
335	            data_words = ["多少", "数量", "有几个", "top", "排名", "分布"]
336	            if any(word in question.lower() for word in data_words):
337	                return False
338	
339	        # Too many rows (likely a bug or unintended full scan)
340	        if result.rowcount > 10000:
341	            return False
342	
343	        # All values identical (possible bug)
344	        if len(result.rows) > 1:
345	            first_value = result.rows[0].get(result.columns[0]) if result.columns else None
346	            if first_value is not None:
347	                all_same = all(r.get(result.columns[0]) == first_value for r in result.rows)
348	                if all_same:
349	                    return False
350	
351	        return True
352	
353	    def _format_result(self, result: ExecutionResult) -> str:
354	        """Format result for LLM error message"""
355	        if not result.rows:
356	            return f"Empty result (0 rows), columns: {result.columns}"
357	
358	        if result.rowcount <= 3:
359	            sample = result.rows
360	        else:
361	            sample = result.rows[:3]
362	
363	        return f"""
364	Result stats:
365	  - Rows: {result.rowcount}
366	  - Columns: {result.columns}
367	
368	Sample rows:
369	{sample}
370	""".strip()

### Q18

1	"""Multi-Path SQL Executor — Execute and compare all candidate SQLs
2	
3	Inspired by CHASE-SQL (ICLR 2025) + PV-SQL (2026):
4	    Instead of picking one SQL based on static scoring, EXECUTE all candidates
5	    and compare their results. This catches subtle SQL bugs that pass
6	    syntax validation but produce wrong answers.
7	
8	Pipeline:
9	    1. Execute each valid candidate SQL
10	    2. Compare results:
11	       a. All agree → high confidence, return best
12	       b. 2 of 3 agree → medium confidence, return majority
13	       c. All disagree → low confidence, use LLM to pick (or fallback to scoring)
14	
15	    3. If LLM available: pairwise comparison of top-2 results vs question
16	
17	Usage:
18	    from agent.sql_engine.multi_executor import MultiPathExecutor
19	
20	    executor = MultiPathExecutor(db_path="...")
21	    result = executor.execute_and_compare(
22	        candidates=[sql1, sql2, sql3],
23	        question="IDCEVO有多少Critical缺陷",
24	        question="...",
25	    )
26	    # result.best_sql, result.best_data, result.confidence, result.agreement
27	"""
28	
29	from __future__ import annotations
30	
31	import sqlite3
32	import logging
33	from typing import List, Optional, Dict, Any, Tuple
34	from dataclasses import dataclass, field
35	from enum import Enum
36	import json
37	
38	logger = logging.getLogger(__name__)
39	
40	
41	class AgreementLevel(Enum):
42	    """How well candidates agree"""
43	    UNANIMOUS = "unanimous"     # All candidates produce same result
44	    MAJORITY = "majority"       # 2/3 agree
45	    DISAGREE = "disagree"       # All different
46	    SINGLE = "single"           # Only one valid candidate
47	
48	
49	@dataclass
50	class CandidateResult:
51	    """Result of executing one candidate SQL"""
52	    sql: str
53	    path: str               # direct / decomposed / plan_based
54	    success: bool
55	    data: List[Dict] = field(default_factory=list)
56	    row_count: int = 0
57	    error: str = ""
58	    execution_ms: float = 0.0
59	
60	    @property
61	    def data_signature(self) -> str:
62	        """
63	        A normalized signature of the result data for comparison.
64	        Two results with the same signature are considered equivalent.
65	        """
66	        if not self.success or not self.data:
67	            return f"empty:{self.success}"
68	
69	        # For count queries (1 row, 1 col), signature is the value
70	        if len(self.data) == 1 and len(self.data[0]) == 1:
71	            val = list(self.data[0].values())[0]
72	            return f"scalar:{val}"
73	
74	        # For multi-row results, compare row count + first col values
75	        first_col = list(self.data[0].keys())[0] if self.data[0] else ""
76	        values = [str(row.get(first_col, "")) for row in self.data[:20]]
77	        return f"rows:{self.row_count}:{first_col}:{','.join(values)}"
78	
79	
80	@dataclass
81	class MultiPathResult:
82	    """Result of multi-path execution and comparison"""
83	    best_sql: str
84	    best_data: List[Dict]
85	    best_path: str
86	    agreement: AgreementLevel
87	    confidence: float                    # 0-1
88	    all_results: List[CandidateResult] = field(default_factory=list)
89	    llm_verdict: str = ""               # LLM reasoning if used
90	    reasoning: str = ""
91	
92	    @property
93	    def row_count(self) -> int:
94	        return len(self.best_data)
95	
96	
97	class MultiPathExecutor:
98	    """
99	    Execute all candidate SQLs and pick the best based on result comparison.
100	
101	    This is the execution-guided selection layer that complements
102	    the static SQLSelector scoring.
103	    """
104	
105	    def __init__(
106	        self,
107	        db_path: str,
108	        llm_call_fn: Optional = None,
109	        max_candidates: int = 3,
110	    ):
111	        self.db_path = db_path
112	        self.llm_call_fn = llm_call_fn
113	        self.max_candidates = max_candidates
114	
115	    def execute_and_compare(
116	        self,
117	        candidates: List,  # List[SQLCandidate]
118	        question: str = "",
119	        intent: str = "",
120	    ) -> MultiPathResult:
121	        """
122	        Execute all candidates, compare results, and select the best.
123	
124	        Args:
125	            candidates: List of SQLCandidate objects
126	            question: Original user question (for LLM comparison)
127	            intent: Detected intent type
128	
129	        Returns:
130	            MultiPathResult with best SQL and comparison metadata
131	        """
132	        if not candidates:
133	            return MultiPathResult(
134	                best_sql="SELECT COUNT(*) FROM octane_defects",
135	                best_data=[],
136	                best_path="fallback",
137	                agreement=AgreementLevel.SINGLE,
138	                confidence=0.1,
139	                reasoning="No candidates provided",
140	            )
141	
142	        # Step 1: Execute all candidates
143	        results = []
144	        for cand in candidates[:self.max_candidates]:
145	            r = self._execute_one(cand.sql, cand.path)
146	            results.append(r)
147	
148	        # Step 2: Filter successful
149	        successful = [r for r in results if r.success]
150	        failed = [r for r in results if not r.success]
151	
152	        if len(successful) == 0:
153	            # All failed — return first with error
154	            return MultiPathResult(
155	                best_sql=candidates[0].sql,
156	                best_data=[],
157	                best_path=candidates[0].path,
158	                agreement=AgreementLevel.DISAGREE,
159	                confidence=0.0,
160	                all_results=results,
161	                reasoning=f"All {len(results)} candidates failed: {failed[0].error if failed else 'unknown'}",
162	            )
163	
164	        if len(successful) == 1:
165	            # Only one succeeded
166	            return MultiPathResult(
167	                best_sql=successful[0].sql,
168	                best_data=successful[0].data,
169	                best_path=successful[0].path,
170	                agreement=AgreementLevel.SINGLE,
171	                confidence=0.7,
172	                all_results=results,
173	                reasoning=f"Only '{successful[0].path}' succeeded ({successful[0].row_count} rows)",
174	            )
175	
176	        # Step 3: Compare results
177	        agreement = self._check_agreement(successful)
178	
179	        if agreement == AgreementLevel.UNANIMOUS:
180	            # All agree! High confidence
181	            best = successful[0]
182	            return MultiPathResult(
183	                best_sql=best.sql,
184	                best_data=best.data,
185	                best_path=best.path,
186	                agreement=agreement,
187	                confidence=0.95,
188	                all_results=results,
189	                reasoning=f"All {len(successful)} candidates agree ({best.row_count} rows)",
190	            )
191	
192	        if agreement == AgreementLevel.MAJORITY and len(successful) >= 3:
193	            # 2 of 3 agree — return majority
194	            majority_result = self._find_majority(successful)
195	            return MultiPathResult(
196	                best_sql=majority_result.sql,
197	                best_data=majority_result.data,
198	                best_path=majority_result.path,
199	                agreement=agreement,
200	                confidence=0.80,
201	                all_results=results,
202	                reasoning=f"Majority agreement (2/3), selecting '{majority_result.path}'",
203	            )
204	
205	        # Step 4: Disagreement — try LLM arbitration
206	        if self.llm_call_fn and question:
207	            return self._llm_arbitrate(successful, question, intent, results)
208	
209	        # No LLM — fallback to highest scoring path preference
210	        # Preference order: plan_based > decomposed > direct
211	        preference = {"plan_based": 3, "decomposed": 2, "direct": 1}
212	        successful.sort(
213	            key=lambda r: preference.get(r.path, 0),
214	            reverse=True
215	        )
216	        best = successful[0]
217	        return MultiPathResult(
218	            best_sql=best.sql,
219	            best_data=best.data,
220	            best_path=best.path,
221	            agreement=agreement,
222	            confidence=0.5,
223	            all_results=results,
224	            reasoning=f"Candidates disagree; selected '{best.path}' (path preference fallback)",
225	        )
226	
227	    # ==================== Execution ====================
228	
229	    def _execute_one(self, sql: str, path: str) -> CandidateResult:
230	        """Execute a single SQL and return result"""
231	        import time
232	        t0 = time.time()
233	
234	        try:
235	            conn = sqlite3.connect(self.db_path)
236	            conn.row_factory = sqlite3.Row
237	            cursor = conn.cursor()
238	            cursor.execute(sql)
239	            rows = [dict(row) for row in cursor.fetchall()]
240	            conn.close()
241	
242	            latency = (time.time() - t0) * 1000
243	            return CandidateResult(
244	                sql=sql,
245	                path=path,
246	                success=True,
247	                data=rows,
248	                row_count=len(rows),
249	                execution_ms=latency,
250	            )
251	        except Exception as e:
252	            latency = (time.time() - t0) * 1000
253	            return CandidateResult(
254	                sql=sql,
255	                path=path,
256	                success=False,
257	                error=str(e),
258	                execution_ms=latency,
259	            )
260	
261	    # ==================== Agreement Checking ====================
262	
263	    def _check_agreement(self, results: List[CandidateResult]) -> AgreementLevel:
264	        """Check how well results agree"""
265	        if len(results) <= 1:
266	            return AgreementLevel.SINGLE
267	
268	        signatures = [r.data_signature for r in results]
269	        unique_sigs = set(signatures)
270	
271	        if len(unique_sigs) == 1:
272	            return AgreementLevel.UNANIMOUS
273	        elif len(results) >= 3 and len(unique_sigs) == 2:
274	            return AgreementLevel.MAJORITY
275	        else:
276	            return AgreementLevel.DISAGREE
277	
278	    def _find_majority(self, results: List[CandidateResult]) -> CandidateResult:
279	        """Find the majority result (shared by 2+ candidates)"""
280	        sig_groups: Dict[str, List[CandidateResult]] = {}
281	        for r in results:
282	            sig = r.data_signature
283	            if sig not in sig_groups:
284	                sig_groups[sig] = []
285	            sig_groups[sig].append(r)
286	
287	        # Find the group with most members
288	        majority_group = max(sig_groups.values(), key=len)
289	        return majority_group[0]
290	
291	    # ==================== LLM Arbitration ====================
292	
293	    def _llm_arbitrate(
294	        self,
295	        results: List[CandidateResult],
296	        question: str,
297	        intent: str,
298	        all_results: List[CandidateResult],
299	    ) -> MultiPathResult:
300	        """Use LLM to pick the best result when candidates disagree"""
301	
302	        # Prepare comparison prompt
303	        candidates_text = []
304	        for i, r in enumerate(results):
305	            sample = r.data[:5]
306	            candidates_text.append(
307	                f"候选 {i+1} (路径: {r.path}):\n"
308	                f"  SQL: {r.sql}\n"
309	                f"  行数: {r.row_count}\n"
310	                f"  样本: {json.dumps(sample, ensure_ascii=False, default=str)[:300]}\n"
311	            )
312	
313	        prompt = f"""你是SQL结果评审专家。多个SQL候选对同一问题产生了不同结果，请判断哪个最正确。
314	
315	## 用户问题
316	{question}
317	
318	## 意图
319	{intent}
320	
321	## 候选结果
322	{chr(10).join(candidates_text)}
323	
324	## 评审标准
325	1. SQL逻辑是否正确（JOIN/WHERE/GROUP BY）
326	2. 结果是否回答了用户问题
327	3. 数据量是否合理
328	
329	## 输出格式
330	回复 JSON:
331	{{"best": <候选编号1-3>, "reason": "<简要原因>"}}
332	只回复 JSON，不要其他内容。"""
333	
334	        try:
335	            response = self.llm_call_fn(prompt).strip()
336	
337	            # Parse JSON response
338	            # Handle cases where LLM wraps in markdown
339	            if "```" in response:
340	                response = response.split("```")[1]
341	                if response.startswith("json"):
342	                    response = response[4:]
343	            response = response.strip("` \n")
344	
345	            verdict = json.loads(response)
346	            best_idx = int(verdict["best"]) - 1  # 1-indexed → 0-indexed
347	
348	            if 0 <= best_idx < len(results):
349	                chosen = results[best_idx]
350	                return MultiPathResult(
351	                    best_sql=chosen.sql,
352	                    best_data=chosen.data,
353	                    best_path=chosen.path,
354	                    agreement=AgreementLevel.DISAGREE,
355	                    confidence=0.75,
356	                    all_results=all_results,
357	                    llm_verdict=verdict.get("reason", ""),
358	                    reasoning=f"LLM selected '{chosen.path}' (候选{best_idx+1}): {verdict.get('reason', '')}",
359	                )
360	
361	        except (json.JSONDecodeError, ValueError, IndexError) as e:
362	            logger.warning(f"LLM arbitration parse error: {e}")
363	        except Exception as e:
364	            logger.warning(f"LLM arbitration failed: {e}")
365	
366	        # Fallback: prefer plan_based
367	        preference = {"plan_based": 3, "decomposed": 2, "direct": 1}
368	        results.sort(key=lambda r: preference.get(r.path, 0), reverse=True)
369	        best = results[0]
370	        return MultiPathResult(
371	            best_sql=best.sql,
372	            best_data=best.data,
373	            best_path=best.path,
374	            agreement=AgreementLevel.DISAGREE,
375	            confidence=0.5,
376	            all_results=all_results,
377	            reasoning="LLM arbitration failed; path preference fallback",
378	        )
379

### Q19

1	"""Intent Detector - Classify user query intent
2	
3	Identifies what kind of analysis the user wants:
4	- count_query: "有多少缺陷"
5	- trend_analysis: "趋势怎样"
6	- ranking: "TOP 10"
7	- distribution: "按项目分布"
8	- comparison: "IDCEVO vs IDC"
9	- detail_list: "列出所有Critical"
10	- search_similar: "有没有类似的"
11	- risk_analysis: "风险评估"
12	- summary: "概况"
13	"""
14	
15	import re
16	from typing import List, Optional, Tuple
17	from dataclasses import dataclass
18	from enum import Enum
19	
20	from agent.understand.entity_extractor import ExtractionResult
21	
22	
23	class QueryIntent(Enum):
24	    """Primary query intents"""
25	    COUNT = "count"                    # 多少/数量
26	    TREND = "trend"                    # 趋势/走势/变化
27	    RANKING = "ranking"                # TOP N / 排名
28	    DISTRIBUTION = "distribution"      # 分布/占比/分组
29	    COMPARISON = "comparison"          # 对比/比较
30	    DETAIL_LIST = "detail_list"        # 列表/明细
31	    SEARCH_SIMILAR = "search_similar"  # 相似/重复
32	    RISK_ANALYSIS = "risk_analysis"    # 风险
33	    SUMMARY = "summary"               # 概况/总览
34	    ROOT_CAUSE = "root_cause"          # 为什么/根因
35	    STATUS_CHECK = "status_check"      # 状态查询
36	
37	
38	@dataclass
39	class IntentResult:
40	    """Intent detection result"""
41	    primary: QueryIntent
42	    secondary: List[QueryIntent]
43	    confidence: float
44	    sql_template: str        # Hint for SQL generation
45	    needs_aggregation: bool
46	    needs_grouping: bool
47	    needs_timeseries: bool
48	    needs_join: bool
49	    description: str
50	
51	
52	# Intent detection rules: (intent, patterns, sql_hint, flags)
53	INTENT_RULES = [
54	    (
55	        QueryIntent.COUNT, [
56	            r"多少|数量|总数|几个|count",
57	            r"统计.*?(?:缺陷|问题|bug)",
58	        ],
59	        "SELECT COUNT(*) FROM {table} WHERE {filters}",
60	        True, False, False, False, "计数查询"
61	    ),
62	    (
63	        QueryIntent.TREND, [
64	            r"趋势|走势|变化|增长|下降|trend|时间线",
65	            r"近.*?(?:天|月|周).*?(?:变化|趋势)",
66	            r"按.*?(?:月|周|天).*?(?:统计|分组)",
67	        ],
68	        "SELECT date({time_field}) as date, COUNT(*) as count FROM {table} WHERE {filters} GROUP BY date({time_field}) ORDER BY date",
69	        True, False, True, False, "趋势分析"
70	    ),
71	    (
72	        QueryIntent.RANKING, [
73	            r"top\s*\d+|前\s*\d+|排名|最高|最多|最大|最低|最少",
74	            r"排.*?第",
75	            r"最.*?(?:多|少|高|低|严重)",
76	        ],
77	        "SELECT {group_field}, COUNT(*) as count FROM {table} WHERE {filters} GROUP BY {group_field} ORDER BY count DESC LIMIT {limit}",
78	        True, True, False, False, "排名查询"
79	    ),
80	    (
81	        QueryIntent.DISTRIBUTION, [
82	            r"分布|占比|比例|百分比|构成|breakdown",
83	            r"按.*?(?:项目|团队|ECU|严重度|阶段).*?(?:统计|分布|分组)",
84	            r"哪个.*?(?:最多|最高)",
85	            r"分别.*?(?:多少|几个)",
86	        ],
87	        "SELECT {group_field}, COUNT(*) as count FROM {table} WHERE {filters} GROUP BY {group_field} ORDER BY count DESC",
88	        True, True, False, False, "分布分析"
89	    ),
90	    (
91	        QueryIntent.COMPARISON, [
92	            r"对比|比较|vs|versus|同比|环比|差异",
93	            r"和.*?(?:相比|对比|哪个)",
94	        ],
95	        "SELECT {group_field}, COUNT(*) as count FROM {table} WHERE {filters} GROUP BY {group_field}",
96	        True, True, False, False, "对比分析"
97	    ),
98	    (
99	        QueryIntent.DETAIL_LIST, [
100	            r"列出|列表|明细|清单|详情|list|哪些",
101	            r"显示.*?(?:缺陷|问题|bug)",
102	            r"查看.*?(?:缺陷|问题)",
103	        ],
104	        "SELECT * FROM {table} WHERE {filters} LIMIT {limit}",
105	        False, False, False, False, "明细列表"
106	    ),
107	    (
108	        QueryIntent.SEARCH_SIMILAR, [
109	            r"类似|相似|重复|一样的|相同|duplicate|same",
110	            r"有没有.*?(?:同样|类似|一样)",
111	            r".*?是否.*?(?:出现过|遇到过)",
112	        ],
113	        "-- Uses BGE embedding search, not SQL",
114	        False, False, False, False, "相似搜索"
115	    ),
116	    (
117	        QueryIntent.RISK_ANALYSIS, [
118	            r"风险|risk|危险|严重.*?(?:程度|等级)",
119	            r"最.*?(?:严重|危险|高风险)",
120	        ],
121	        "SELECT * FROM {table} WHERE {filters} ORDER BY risk_score DESC LIMIT {limit}",
122	        False, False, False, False, "风险分析"
123	    ),
124	    (
125	        QueryIntent.SUMMARY, [
126	            r"概况|总览|概览|summary|dashboard|仪表",
127	            r"整体.*?(?:情况|状态)",
128	            r"汇总",
129	        ],
130	        "SELECT COUNT(*), COUNT(DISTINCT {group_field}) FROM {table} WHERE {filters}",
131	        True, False, False, False, "总览摘要"
132	    ),
133	    (
134	        QueryIntent.ROOT_CAUSE, [
135	            r"为什么|原因|根因|why|root cause",
136	            r"什么.*?(?:导致|引起|造成)",
137	        ],
138	        "-- Requires multi-step analysis",
139	        False, False, False, True, "根因分析"
140	    ),
141	    (
142	        QueryIntent.STATUS_CHECK, [
143	            r"状态|进度|怎么样了|什么状态|进展",
144	            r"还没.*?(?:解决|关闭|修复)",
145	            r"是否.*?(?:解决|关闭|修复)",
146	        ],
147	        "SELECT {id_field}, status_phase, severity, name FROM {table} WHERE {filters}",
148	        False, False, False, False, "状态查询"
149	    ),
150	]
151	
152	
153	class IntentDetector:
154	    """
155	    Detects primary and secondary intents from user questions.
156	    """
157	
158	    def __init__(self):
159	        self._compiled_rules = []
160	        for intent, patterns, sql_hint, agg, group, ts, join, desc in INTENT_RULES:
161	            compiled = [(intent, re.compile(p, re.IGNORECASE), sql_hint, agg, group, ts, join, desc)
162	                       for p in patterns]
163	            self._compiled_rules.extend(compiled)
164	
165	    def detect(self, question: str, extraction: Optional[ExtractionResult] = None) -> IntentResult:
166	        """
167	        Detect intent from question.
168	
169	        Args:
170	            question: User's question
171	            extraction: Pre-extracted entities (optional, helps disambiguate)
172	
173	        Returns:
174	            IntentResult with primary intent and metadata
175	        """
176	        scores = {}  # intent -> (score, sql_hint, flags)
177	
178	        for intent, pattern, sql_hint, agg, group, ts, join, desc in self._compiled_rules:
179	            match = pattern.search(question)
180	            if match:
181	                current = scores.get(intent, (0, sql_hint, agg, group, ts, join, desc))
182	                scores[intent] = (current[0] + 1, sql_hint, agg, group, ts, join, desc)
183	
184	        # Also use extraction hints
185	        if extraction:
186	            agg_entity = extraction.get_first("aggregation")
187	            if agg_entity:
188	                agg_map = {
189	                    "count": QueryIntent.COUNT,
190	                    "trend": QueryIntent.TREND,
191	                    "ranking": QueryIntent.RANKING,
192	                    "distribution": QueryIntent.DISTRIBUTION,
193	                    "comparison": QueryIntent.COMPARISON,
194	                    "list": QueryIntent.DETAIL_LIST,
195	                    "average": QueryIntent.DISTRIBUTION,
196	                }
197	                mapped = agg_map.get(agg_entity.value)
198	                if mapped:
199	                    current = scores.get(mapped, (0, "", False, False, False, False, ""))
200	                    scores[mapped] = (current[0] + 2, current[1], current[2], current[3],
201	                                      current[4], current[5], current[6])
202	
203	        if not scores:
204	            # Default to count
205	            return IntentResult(
206	                primary=QueryIntent.COUNT,
207	                secondary=[],
208	                confidence=0.5,
209	                sql_template="SELECT COUNT(*) FROM {table} WHERE {filters}",
210	                needs_aggregation=True,
211	                needs_grouping=False,
212	                needs_timeseries=False,
213	                needs_join=False,
214	                description="计数查询(默认)"
215	            )
216	
217	        # Sort by score
218	        sorted_intents = sorted(scores.items(), key=lambda x: x[1][0], reverse=True)
219	        primary_intent = sorted_intents[0][0]
220	        primary_data = sorted_intents[0][1]
221	
222	        secondary = [item[0] for item in sorted_intents[1:3]]
223	
224	        # Confidence: normalize score
225	        max_score = primary_data[0]
226	        confidence = min(max_score / 3.0, 1.0)  # Cap at 1.0
227	
228	        return IntentResult(
229	            primary=primary_intent,
230	            secondary=secondary,
231	            confidence=confidence,
232	            sql_template=primary_data[1],
233	            needs_aggregation=primary_data[2],
234	            needs_grouping=primary_data[3],
235	            needs_timeseries=primary_data[4],
236	            needs_join=primary_data[5],
237	            description=primary_data[6]
238	        )
239	
240	
241	# Singleton
242	_detector: Optional[IntentDetector] = None
243	
244	
245	def get_intent_detector() -> IntentDetector:
246	    global _detector
247	    if _detector is None:
248	        _detector = IntentDetector()
249	    return _detector
250

### Q20

1	"""Entity Extractor - Extract entities from natural language questions
2	
3	Identifies and extracts structured entities from user questions:
4	- Projects (IDCEVO, IDC, MGU, etc.)
5	- ECUs (BCM, VCU, ADAS, etc.)
6	- Time ranges (本月, 上周, 近30天)
7	- Severities (Critical, Major, Minor)
8	- Status phases (活跃, 已关闭)
9	- Teams / People
10	- Phases (Q-Gate, CoC, Integration)
11	- Metrics (缺陷密度, 活跃缺陷数)
12	- Numeric constraints (>5, 超过10个)
13	"""
14	
15	import re
16	from typing import Dict, List, Optional, Tuple
17	from dataclasses import dataclass, field
18	from datetime import datetime, timedelta
19	
20	from agent.ontology import OntologyEngine, get_ontology_engine
21	from agent.understand.term_resolver import TermResolver, get_term_resolver, ResolvedTerm
22	
23	
24	@dataclass
25	class Entity:
26	    """An extracted entity"""
27	    entity_type: str        # project, ecu, severity, status, time_range, phase, team, metric, limit
28	    value: str              # Canonical value
29	    original: str           # Original text from user
30	    field: str = ""         # Maps to which DB field
31	    operator: str = "="     # SQL operator
32	    values: Optional[List[str]] = None  # For IN clauses
33	    start: int = 0          # Position in original text
34	    end: int = 0            # End position
35	    confidence: float = 1.0
36	
37	
38	@dataclass
39	class ExtractionResult:
40	    """Result of entity extraction"""
41	    entities: List[Entity] = field(default_factory=list)
42	    unresolved: List[str] = field(default_factory=list)  # Terms we couldn't resolve
43	
44	    def get(self, entity_type: str) -> List[Entity]:
45	        """Get entities of a specific type"""
46	        return [e for e in self.entities if e.entity_type == entity_type]
47	
48	    def has(self, entity_type: str) -> bool:
49	        return any(e.entity_type == entity_type for e in self.entities)
50	
51	    def get_first(self, entity_type: str) -> Optional[Entity]:
52	        for e in self.entities:
53	            if e.entity_type == entity_type:
54	                return e
55	        return None
56	
57	
58	class EntityExtractor:
59	    """
60	    Extracts structured entities from user questions.
61	
62	    Uses TermResolver for canonical mapping and adds:
63	    - Pattern-based extraction (dates, numbers)
64	    - Context-aware disambiguation
65	    - Multi-entity extraction
66	    """
67	
68	    # Metric keywords → metric name
69	    METRIC_KEYWORDS: Dict[str, str] = {
70	        "活跃缺陷": "active_defect_count",
71	        "active": "active_defect_count",
72	        "critical缺陷": "critical_defect_count",
73	        "critical数": "critical_defect_count",
74	        "缺陷密度": "defect_density",
75	        "中国缺陷": "china_defect_count",
76	        "china缺陷": "china_defect_count",
77	        "q-gate缺陷": "q_gate_defect_count",
78	        "coc缺陷": "coc_defect_count",
79	    }
80	
81	    # Aggregation intent patterns
82	    AGG_PATTERNS = [
83	        (re.compile(r"多少|数量|总数|count", re.IGNORECASE), "count", "COUNT"),
84	        (re.compile(r"趋势|走势|变化|trend", re.IGNORECASE), "trend", "TIMESERIES"),
85	        (re.compile(r"排名|top|前\d|最高|最多|最低|最少", re.IGNORECASE), "ranking", "ORDER BY"),
86	        (re.compile(r"分布|占比|比例|百分比|breakdown|分组", re.IGNORECASE), "distribution", "GROUP BY"),
87	        (re.compile(r"对比|比较|vs|versus|同比|环比", re.IGNORECASE), "comparison", "COMPARE"),
88	        (re.compile(r"列表|明细|清单|list|详情", re.IGNORECASE), "list", "SELECT *"),
89	        (re.compile(r"平均|均值|avg|average", re.IGNORECASE), "average", "AVG"),
90	    ]
91	
92	    def __init__(self, ontology: Optional[OntologyEngine] = None):
93	        self.ontology = ontology or get_ontology_engine()
94	        self.term_resolver = get_term_resolver(ontology)
95	
96	    def extract(self, question: str, object_type: str = "Defect") -> ExtractionResult:
97	        """
98	        Extract all entities from a natural language question.
99	
100	        Args:
101	            question: User's question
102	            object_type: Which object type to extract against
103	
104	        Returns:
105	            ExtractionResult with all found entities
106	        """
107	        result = ExtractionResult()
108	
109	        # 1. Resolve terms via TermResolver
110	        resolved_terms = self.term_resolver.resolve(question, object_type)
111	
112	        for rt in resolved_terms:
113	            entity = self._resolved_to_entity(rt)
114	            if entity:
115	                result.entities.append(entity)
116	
117	        # 2. Extract metrics
118	        self._extract_metrics(question, result)
119	
120	        # 3. Extract aggregation intent
121	        self._extract_aggregation(question, result)
122	
123	        # 4. Extract time range entities more precisely
124	        self._extract_time_ranges(question, result)
125	
126	        # 5. Extract sort/limit
127	        self._extract_sort_limit(question, result)
128	
129	        # Sort by position
130	        result.entities.sort(key=lambda e: e.start)
131	
132	        return result
133	
134	    def _resolved_to_entity(self, rt: ResolvedTerm) -> Optional[Entity]:
135	        """Convert a ResolvedTerm to an Entity"""
136	        if rt.field == "__limit__":
137	            return Entity(
138	                entity_type="limit",
139	                value=rt.value,
140	                original=rt.original,
141	                field="limit",
142	                operator="LIMIT",
143	                confidence=rt.confidence
144	            )
145	        if rt.field == "__count__":
146	            return Entity(
147	                entity_type="numeric_constraint",
148	                value=rt.value,
149	                original=rt.original,
150	                field="count",
151	                operator=rt.operator,
152	                confidence=rt.confidence
153	            )
154	        if rt.operator == "time_range":
155	            return Entity(
156	                entity_type="time_range",
157	                value=rt.value,
158	                original=rt.original,
159	                field="creation_time",
160	                operator="time_range",
161	                confidence=rt.confidence
162	            )
163	
164	        # Map field to entity type
165	        field_to_type = {
166	            "project": "project",
167	            "assigned_ecu": "ecu",
168	            "severity": "severity",
169	            "status_phase": "status",
170	            "phase": "test_phase",
171	            "team": "team",
172	            "problem_finder_team": "team",
173	            "top_aida": "aida",
174	            "market": "market",
175	            "solution_cluster": "solution_cluster",
176	        }
177	
178	        etype = field_to_type.get(rt.field, rt.field)
179	
180	        return Entity(
181	            entity_type=etype,
182	            value=rt.value,
183	            original=rt.original,
184	            field=rt.field,
185	            operator=rt.operator if rt.operator != "=" else "=",
186	            values=rt.values,
187	            confidence=rt.confidence
188	        )
189	
190	    def _extract_metrics(self, question: str, result: ExtractionResult):
191	        """Extract metric references"""
192	        q_lower = question.lower()
193	        for keyword, metric_name in self.METRIC_KEYWORDS.items():
194	            if keyword.lower() in q_lower:
195	                # Check not already extracted
196	                if not any(e.entity_type == "metric" and e.value == metric_name for e in result.entities):
197	                    result.entities.append(Entity(
198	                        entity_type="metric",
199	                        value=metric_name,
200	                        original=keyword,
201	                        field="metric",
202	                        confidence=0.85
203	                    ))
204	
205	    def _extract_aggregation(self, question: str, result: ExtractionResult):
206	        """Extract aggregation intent"""
207	        for pattern, agg_type, sql_hint in self.AGG_PATTERNS:
208	            match = pattern.search(question)
209	            if match:
210	                # Only take the first matching aggregation
211	                if not any(e.entity_type == "aggregation" for e in result.entities):
212	                    result.entities.append(Entity(
213	                        entity_type="aggregation",
214	                        value=agg_type,
215	                        original=match.group(0),
216	                        field="__aggregation__",
217	                        operator=sql_hint,
218	                        start=match.start(),
219	                        end=match.end(),
220	                        confidence=0.9
221	                    ))
222	                    break
223	
224	    def _extract_time_ranges(self, question: str, result: ExtractionResult):
225	        """Extract precise time range with date computation"""
226	        now = datetime.now()
227	
228	        time_range_map = {
229	            "today": (now.replace(hour=0, minute=0, second=0), now),
230	            "yesterday": (now.replace(hour=0, minute=0, second=0) - timedelta(days=1),
231	                          now.replace(hour=0, minute=0, second=0)),
232	            "this_week": (now - timedelta(days=now.weekday()), now),
233	            "last_week": (now - timedelta(days=now.weekday() + 7),
234	                          now - timedelta(days=now.weekday())),
235	            "this_month": (now.replace(day=1, hour=0, minute=0, second=0), now),
236	            "last_month": (
237	                (now.replace(day=1) - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0),
238	                now.replace(day=1, hour=0, minute=0, second=0) - timedelta(seconds=1)
239	            ),
240	            "this_quarter": (
241	                now.replace(month=((now.month - 1) // 3) * 3 + 1, day=1, hour=0, minute=0, second=0),
242	                now
243	            ),
244	            "this_year": (now.replace(month=1, day=1, hour=0, minute=0, second=0), now),
245	            "last_year": (
246	                now.replace(year=now.year - 1, month=1, day=1, hour=0, minute=0, second=0),
247	                now.replace(month=1, day=1, hour=0, minute=0, second=0) - timedelta(seconds=1)
248	            ),
249	        }
250	
251	        # Find time range entities
252	        for entity in result.entities:
253	            if entity.entity_type != "time_range":
254	                continue
255	
256	            range_type = entity.value
257	
258	            # Handle "近N天/月/周"
259	            if range_type in ("recent_days", "recent_months", "recent_weeks"):
260	                match = re.search(r"近\s*(\d+)\s*(天|个月|周)", question)
261	                if match:
262	                    n = int(match.group(1))
263	                    unit = match.group(2)
264	                    if unit == "天":
265	                        start_date = now - timedelta(days=n)
266	                    elif unit == "个月":
267	                        start_date = now - timedelta(days=n * 30)
268	                    else:  # 周
269	                        start_date = now - timedelta(weeks=n)
270	                    entity.values = [start_date.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")]
271	            elif range_type in time_range_map:
272	                start, end = time_range_map[range_type]
273	                entity.values = [start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")]
274	
275	    def _extract_sort_limit(self, question: str, result: ExtractionResult):
276	        """Extract sort direction and limit"""
277	        # Sort direction
278	        sort_desc_patterns = [
279	            re.compile(r"最高|最多|最大|top|降序|倒序", re.IGNORECASE),
280	        ]
281	        sort_asc_patterns = [
282	            re.compile(r"最低|最少|最小|升序|bottom", re.IGNORECASE),
283	        ]
284	
285	        has_desc = any(p.search(question) for p in sort_desc_patterns)
286	        has_asc = any(p.search(question) for p in sort_asc_patterns)
287	
288	        if has_desc and not any(e.entity_type == "sort" for e in result.entities):
289	            result.entities.append(Entity(
290	                entity_type="sort",
291	                value="DESC",
292	                original="降序",
293	                field="__sort__",
294	                operator="ORDER BY ... DESC",
295	                confidence=0.8
296	            ))
297	        elif has_asc and not any(e.entity_type == "sort" for e in result.entities):
298	            result.entities.append(Entity(
299	                entity_type="sort",
300	                value="ASC",
301	                original="升序",
302	                field="__sort__",
303	                operator="ORDER BY ... ASC",
304	                confidence=0.8
305	            ))
306	
307	    def to_sql_filters(self, result: ExtractionResult,
308	                       object_type: str = "Defect") -> List[str]:
309	        """
310	        Convert extracted entities to SQL WHERE clause fragments.
311	
312	        Returns list of SQL conditions that can be AND-ed together.
313	        """
314	        filters = []
315	        obj = self.ontology.get_object(object_type)
316	        if not obj:
317	            return filters
318	
319	        for entity in result.entities:
320	            if entity.entity_type in ("aggregation", "sort", "limit", "metric",
321	                                      "numeric_constraint"):
322	                continue
323	
324	            field = entity.field
325	            if not field or field.startswith("__"):
326	                continue
327	
328	            if entity.operator == "IN" and entity.values:
329	                values_str = ", ".join(f"'{v}'" for v in entity.values)
330	                filters.append(f"{field} IN ({values_str})")
331	            elif entity.operator == "time_range" and entity.values:
332	                filters.append(f"{field} >= '{entity.values[0]}' AND {field} <= '{entity.values[1]}'")
333	            else:
334	                filters.append(f"{field} {entity.operator} '{entity.value}'")
335	
336	        return filters
337	
338	
339	# Singleton
340	_extractor: Optional[EntityExtractor] = None
341	
342	
343	def get_entity_extractor(ontology: Optional[OntologyEngine] = None) -> EntityExtractor:
344	    global _extractor
345	    if _extractor is None:
346	        _extractor = EntityExtractor(ontology)
347	    return _extractor
348

### Q21

1	"""Term Resolver - Business term disambiguation
2	
3	Resolves user-facing business terms to canonical field values,
4	using Ontology Engine's alias mappings and domain knowledge.
5	
6	Examples:
7	    "大灯" → assigned_ecu = 'IHU' (or relevant ECU)
8	    "Critical" → severity = 'Critical'
9	    "活跃" → status_phase IN ('New', 'Open', 'In Progress')
10	    "中国项目" → project IN ('IDCEVO', 'IDC', 'MGU')
11	"""
12	
13	import re
14	from typing import Dict, List, Optional, Tuple
15	from dataclasses import dataclass, field
16	from pathlib import Path
17	
18	from agent.ontology import OntologyEngine, get_ontology_engine
19	
20	
21	@dataclass
22	class ResolvedTerm:
23	    """A resolved business term"""
24	    original: str               # Original text from user
25	    canonical: str              # Canonical form
26	    field: str                  # Which field this maps to
27	    value: str                  # The canonical value
28	    operator: str = "="         # SQL operator (=, IN, etc.)
29	    values: Optional[List[str]] = None  # For IN clauses
30	    confidence: float = 1.0
31	    source: str = "ontology"    # ontology | pattern | synonym
32	
33	
34	class TermResolver:
35	    """
36	    Resolves business terms using:
37	    1. Ontology alias mappings (primary)
38	    2. Category group expansions (e.g., "活跃" → active statuses)
39	    3. Synonym dictionary (supplementary)
40	    4. Pattern matching (e.g., "超过N个" → >N)
41	    """
42	
43	    # Supplementary synonyms not in YAML
44	    SUPPLEMENT_SYNONYMS: Dict[str, Dict[str, List[str]]] = {
45	        "severity": {
46	            "Critical": ["严重", "致命", "高优", "P0", "S0"],
47	            "Major": ["主要", "重要", "P1", "S1"],
48	            "Minor": ["次要", "轻微", "P2", "S2"],
49	            "Cosmetic": ["外观", "表面", "P3", "S3"],
50	        },
51	        "status_phase": {
52	            "active": ["活跃", "未关闭", "待处理", "open状态", "处理中",
53	                       "未解决", "还没关", "open的"],
54	            "resolved": ["已解决", "已关闭", "已修复", "已完成"],
55	            "New": ["新建", "新提", "刚提"],
56	            "Open": ["打开", "已指派"],
57	            "In Progress": ["进行中", "开发中", "修复中", "处理中"],
58	            "Fixed": ["已修", "修好了", "已修复"],
59	            "Closed": ["已关", "关闭了", "验证通过"],
60	            "Rejected": ["已拒绝", "驳回"],
61	            "Deferred": ["延期", "延后", "推迟"],
62	        },
63	    }
64	
65	    # Numeric constraint patterns
66	    NUMERIC_PATTERNS = [
67	        # "超过N个", "大于N", ">N"
68	        (re.compile(r"超过\s*(\d+)\s*[个条项]?"), ">", "count"),
69	        (re.compile(r"大于\s*(\d+)\s*[个条项]?"), ">", "count"),
70	        (re.compile(r"多于\s*(\d+)\s*[个条项]?"), ">", "count"),
71	        (re.compile(r"至少\s*(\d+)\s*[个条项]?"), ">=", "count"),
72	        (re.compile(r"少于\s*(\d+)\s*[个条项]?"), "<", "count"),
73	        (re.compile(r"小于\s*(\d+)\s*[个条项]?"), "<", "count"),
74	        (re.compile(r"不到\s*(\d+)\s*[个条项]?"), "<", "count"),
75	        (re.compile(r"刚好\s*(\d+)\s*[个条项]?"), "=", "count"),
76	        (re.compile(r"前\s*(\d+)\s*[个条项]"), "TOP", "limit"),
77	        (re.compile(r"top\s*(\d+)", re.IGNORECASE), "TOP", "limit"),
78	    ]
79	
80	    # Time range patterns
81	    TIME_PATTERNS = [
82	        (re.compile(r"今天|今日"), "today"),
83	        (re.compile(r"昨天|昨日"), "yesterday"),
84	        (re.compile(r"本周|这周|这一周"), "this_week"),
85	        (re.compile(r"上周|上一周"), "last_week"),
86	        (re.compile(r"本月|这个月|当月"), "this_month"),
87	        (re.compile(r"上月|上个月|上个月"), "last_month"),
88	        (re.compile(r"本季度|这个季度"), "this_quarter"),
89	        (re.compile(r"上季度|上个季度"), "last_quarter"),
90	        (re.compile(r"今年|本年|年度"), "this_year"),
91	        (re.compile(r"去年|上一年"), "last_year"),
92	        (re.compile(r"近\s*(\d+)\s*天"), "recent_days"),
93	        (re.compile(r"近\s*(\d+)\s*个月"), "recent_months"),
94	        (re.compile(r"近\s*(\d+)\s*周"), "recent_weeks"),
95	    ]
96	
97	    def __init__(self, ontology: Optional[OntologyEngine] = None):
98	        self.ontology = ontology or get_ontology_engine()
99	        self._build_reverse_index()
100	
101	    def _build_reverse_index(self):
102	        """Build reverse alias index for fast lookup"""
103	        self._alias_index: Dict[str, List[Tuple[str, str, str]]] = {}
104	        # alias_index: lowercase_alias -> [(object_type, field, canonical_value), ...]
105	
106	        for obj_type_name, obj in self.ontology.get_all_objects().items():
107	            for prop_name, prop in obj.properties.items():
108	                if prop.aliases:
109	                    for canonical, aliases in prop.aliases.items():
110	                        # Index the canonical value itself as a key
111	                        canon_key = canonical.lower().strip()
112	                        self._alias_index.setdefault(canon_key, []).append(
113	                            (obj_type_name, prop_name, canonical)
114	                        )
115	                        # Index all aliases
116	                        for alias in aliases:
117	                            key = alias.lower().strip()
118	                            self._alias_index.setdefault(key, []).append(
119	                                (obj_type_name, prop_name, canonical)
120	                            )
121	
122	                # Also index the canonical value itself
123	                if prop.values:
124	                    for val in prop.values:
125	                        key = val.lower().strip()
126	                        self._alias_index.setdefault(key, []).append(
127	                            (obj_type_name, prop_name, val)
128	                        )
129	
130	                # Also index examples as known values
131	                if prop.examples:
132	                    for val in prop.examples:
133	                        key = val.lower().strip()
134	                        if key not in self._alias_index:
135	                            self._alias_index.setdefault(key, []).append(
136	                                (obj_type_name, prop_name, val)
137	                            )
138	
139	        # Add supplement synonyms
140	        for field_name, synonyms in self.SUPPLEMENT_SYNONYMS.items():
141	            for canonical, syns in synonyms.items():
142	                for syn in syns:
143	                    key = syn.lower().strip()
144	                    self._alias_index.setdefault(key, []).append(
145	                        ("Defect", field_name, canonical)
146	                    )
147	
148	    def resolve(self, text: str, object_type: str = "Defect") -> List[ResolvedTerm]:
149	        """
150	        Resolve all business terms in the given text.
151	
152	        Args:
153	            text: User's question or text segment
154	            object_type: Which object type to resolve against
155	
156	        Returns:
157	            List of resolved terms found in the text
158	        """
159	        results: List[ResolvedTerm] = []
160	        seen = set()  # Avoid duplicates
161	
162	        # 1. Resolve aliases and synonyms (longest-match-first to avoid partial overlaps)
163	        text_lower = text.lower()
164	        sorted_aliases = sorted(self._alias_index.keys(), key=len, reverse=True)
165	        consumed_positions: set = set()  # Track matched char positions
166	
167	        for alias in sorted_aliases:
168	            if len(alias) < 2:
169	                continue
170	            is_cjk = any(ord(c) > 0x3000 for c in alias)
171	            # Find all non-overlapping occurrences
172	            search_from = 0
173	            while search_from <= len(text_lower) - len(alias):
174	                pos = text_lower.find(alias, search_from)
175	                if pos == -1:
176	                    break
177	                search_from = pos + 1
178	                # Word boundary check (skip for CJK text)
179	                if not is_cjk:
180	                    before_ok = (pos == 0 or not text_lower[pos - 1].isalnum())
181	                    after_ok = (pos + len(alias) >= len(text_lower) or not text_lower[pos + len(alias)].isalnum())
182	                    if not (before_ok and after_ok):
183	                        continue
184	                positions = set(range(pos, pos + len(alias)))
185	                if positions & consumed_positions:
186	                    continue
187	                consumed_positions |= positions
188	
189	                for obj_type, field, canonical in self._alias_index[alias]:
190	                    if obj_type != object_type:
191	                        continue
192	                    key = (field, canonical)
193	                    if key in seen:
194	                        continue
195	                    seen.add(key)
196	
197	                    # Check if this is a category group
198	                    prop = self.ontology.get_property(object_type, field)
199	                    is_category = False
200	                    values = None
201	                    if prop and prop.category_groups:
202	                        for group_name, group_values in prop.category_groups.items():
203	                            if canonical == group_name:
204	                                is_category = True
205	                                values = group_values
206	                                break
207	
208	                    if is_category and values:
209	                        results.append(ResolvedTerm(
210	                            original=alias,
211	                            canonical=canonical,
212	                            field=field,
213	                            value=canonical,
214	                            operator="IN",
215	                            values=values,
216	                            confidence=0.95,
217	                            source="category"
218	                        ))
219	                    else:
220	                        results.append(ResolvedTerm(
221	                            original=alias,
222	                            canonical=canonical,
223	                            field=field,
224	                            value=canonical,
225	                            confidence=0.9,
226	                            source="alias"
227	                        ))
228	
229	        # 2. Resolve category group terms directly
230	        obj = self.ontology.get_object(object_type)
231	        if obj:
232	            for prop_name, prop in obj.properties.items():
233	                if not prop.category_groups:
234	                    continue
235	                for group_name, group_values in prop.category_groups.items():
236	                    # Check if user mentioned the group name
237	                    if group_name.lower() in text_lower:
238	                        key = (prop_name, group_name)
239	                        if key not in seen:
240	                            seen.add(key)
241	                            results.append(ResolvedTerm(
242	                                original=group_name,
243	                                canonical=group_name,
244	                                field=prop_name,
245	                                value=group_name,
246	                                operator="IN",
247	                                values=group_values,
248	                                confidence=0.95,
249	                                source="category"
250	                            ))
251	
252	        # 3. Resolve numeric constraints
253	        for pattern, operator, kind in self.NUMERIC_PATTERNS:
254	            match = pattern.search(text)
255	            if match:
256	                num = int(match.group(1))
257	                if kind == "limit":
258	                    results.append(ResolvedTerm(
259	                        original=match.group(0),
260	                        canonical=f"LIMIT {num}",
261	                        field="__limit__",
262	                        value=str(num),
263	                        operator="LIMIT",
264	                        confidence=1.0,
265	                        source="pattern"
266	                    ))
267	                else:
268	                    results.append(ResolvedTerm(
269	                        original=match.group(0),
270	                        canonical=f"{operator}{num}",
271	                        field="__count__",
272	                        value=str(num),
273	                        operator=operator,
274	                        confidence=1.0,
275	                        source="pattern"
276	                    ))
277	
278	        # 4. Resolve time ranges
279	        for pattern, range_type in self.TIME_PATTERNS:
280	            match = pattern.search(text)
281	            if match:
282	                results.append(ResolvedTerm(
283	                    original=match.group(0),
284	                    canonical=range_type,
285	                    field="creation_time",
286	                    value=range_type,
287	                    operator="time_range",
288	                    confidence=1.0,
289	                    source="pattern"
290	                ))
291	
292	        return results
293	
294	    def resolve_field(self, text: str, object_type: str = "Defect") -> Optional[Tuple[str, str]]:
295	        """
296	        Try to resolve a single term to a field+value.
297	
298	        Returns (field_name, canonical_value) or None
299	        """
300	        terms = self.resolve(text, object_type)
301	        for t in terms:
302	            if t.field and not t.field.startswith("__"):
303	                return (t.field, t.value)
304	        return None
305	
306	    def expand_category(self, field: str, category: str,
307	                        object_type: str = "Defect") -> Optional[List[str]]:
308	        """Expand a category name to its member values"""
309	        prop = self.ontology.get_property(object_type, field)
310	        if prop and prop.category_groups:
311	            return prop.category_groups.get(category)
312	        return None
313	
314	    def get_all_known_terms(self, object_type: str = "Defect") -> Dict[str, List[str]]:
315	        """
316	        Get all known terms for an object type.
317	        Useful for debugging and visualization.
318	        """
319	        result: Dict[str, List[str]] = {}
320	        obj = self.ontology.get_object(object_type)
321	        if not obj:
322	            return result
323	
324	        for prop_name, prop in obj.properties.items():
325	            terms = []
326	            if prop.values:
327	                terms.extend(prop.values)
328	            if prop.aliases:
329	                for canonical, aliases in prop.aliases.items():
330	                    terms.append(canonical)
331	                    terms.extend(aliases)
332	            if prop.category_groups:
333	                terms.extend(prop.category_groups.keys())
334	
335	            # Add supplement synonyms
336	            if prop_name in self.SUPPLEMENT_SYNONYMS:
337	                for canonical, syns in self.SUPPLEMENT_SYNONYMS[prop_name].items():
338	                    terms.append(canonical)
339	                    terms.extend(syns)
340	
341	            if terms:
342	                result[prop_name] = terms
343	
344	        return result
345	
346	
347	# Singleton
348	_resolver: Optional[TermResolver] = None
349	
350	
351	def get_term_resolver(ontology: Optional[OntologyEngine] = None) -> TermResolver:
352	    global _resolver
353	    if _resolver is None:
354	        _resolver = TermResolver(ontology)
355	    return _resolver
356

### Q22

1	"""
2	Data Adapter Layer — 数据源适配器
3	
4	负责连接不同的数据源：
5	1. 本地 sample 数据（开发测试用）
6	2. 生产 Octane SQLite 数据库（另一台电脑）
7	3. PostgreSQL（生产可选）
8	
9	设计原则：
10	- 上层 Agent 只管调用 SQL，不关心数据源在哪
11	- 通过环境变量 DATA_DB_PATH 切换数据源
12	- Schema 保持与生产库一致（octane_defects 表结构）
13	"""
14	
15	from __future__ import annotations
16	
17	import os
18	import json
19	import sqlite3
20	import random
21	from datetime import datetime, timedelta
22	from pathlib import Path
23	from typing import Optional, List, Dict, Any
24	
25	
26	# ============================================================================
27	# Schema — 与生产库 db_storage.py 保持一致
28	# ============================================================================
29	
30	DEFECTS_SCHEMA = """
31	CREATE TABLE IF NOT EXISTS octane_defects (
32	    defect_id TEXT PRIMARY KEY,
33	    year INTEGER,
34	    creation_time TEXT,
35	    summary TEXT,
36	    description TEXT,
37	    status_phase TEXT,
38	    severity TEXT,
39	    project TEXT,
40	    detected_by TEXT,
41	    detected_in_release TEXT,
42	    domain TEXT,
43	    aidas TEXT,
44	    top_aida TEXT,
45	    tags TEXT,
46	    classification TEXT,
47	    pingpong INTEGER DEFAULT 0,
48	    vin TEXT,
49	    ecu TEXT,
50	    source_file TEXT
51	)
52	"""
53	
54	MANUAL_RUNS_SCHEMA = """
55	CREATE TABLE IF NOT EXISTS octane_manual_runs (
56	    run_id TEXT,
57	    report_period TEXT,
58	    test_id TEXT,
59	    test_name TEXT,
60	    run_status TEXT,
61	    tester TEXT,
62	    finished_time TEXT,
63	    test_week TEXT,
64	    project TEXT,
65	    model TEXT,
66	    aidas TEXT,
67	    top_aida TEXT,
68	    PRIMARY KEY (report_period, run_id)
69	)
70	"""
71	
72	DEFECT_HISTORY_SCHEMA = """
73	CREATE TABLE IF NOT EXISTS octane_defect_history_events (
74	    id INTEGER PRIMARY KEY AUTOINCREMENT,
75	    defect_id TEXT,
76	    event_time TEXT,
77	    user TEXT,
78	    event_type TEXT,
79	    from_phase TEXT,
80	    to_phase TEXT,
81	    details TEXT
82	)
83	"""
84	
85	
86	# ============================================================================
87	# Sample Data Generator — 生成模拟缺陷数据
88	# ============================================================================
89	
90	PROJECTS = ['IDCEVO', 'IDC', 'MGU', 'APA', 'ICM']
91	SEVERITIES = ['Critical', 'Major', 'Minor']
92	STATUSES = ['New', 'Open', 'In Progress', 'Fixed', 'Closed', 'Rejected', 'Deferred']
93	ECUS = ['BCM', 'IDC', 'IDCEVO', 'APA', 'ICM', 'ADAS', 'Cluster', 'Gateway', 'V2X', 'DMS']
94	RELEASES = ['R026', 'R027', 'R028', 'R029', 'R030', 'R031']
95	DOMAINS = ['Software', 'Hardware', 'System', 'Mechanical', 'Integration']
96	TESTERS = [
97	    '张伟', '李明', '王强', '陈杰', '刘洋',
98	    '赵磊', '黄涛', '周鹏', '吴昊', '徐辉',
99	]
100	
101	
102	def generate_sample_defects(n: int = 500, year: int = 2026) -> List[Dict[str, Any]]:
103	    """生成模拟缺陷数据"""
104	    random.seed(42)
105	    defects = []
106	    base_time = datetime(year, 1, 1)
107	
108	    for i in range(1, n + 1):
109	        created = base_time + timedelta(
110	            days=random.randint(0, 170),
111	            hours=random.randint(0, 23),
112	        )
113	
114	        ecu = random.choice(ECUS)
115	        project = random.choice(PROJECTS)
116	        severity = random.choices(SEVERITIES, weights=[15, 50, 35])[0]
117	        status = random.choices(STATUSES, weights=[10, 20, 15, 25, 20, 5, 5])[0]
118	
119	        # Critical 倾向于更多在 Open/In Progress
120	        if severity == 'Critical' and random.random() < 0.4:
121	            status = random.choice(['New', 'Open', 'In Progress'])
122	
123	        defect = {
124	            'defect_id': f'DEF-{year}-{i:05d}',
125	            'year': year,
126	            'creation_time': created.strftime('%Y-%m-%dT%H:%M:%SZ'),
127	            'summary': f'{ecu} {severity} 级别问题 #{i}: {random.choice(["功能异常", "通信超时", "信号错误", "显示异常", "性能不达标"])}',
128	            'description': f'在 {project} 项目 {ecu} 模块测试中发现的 {severity} 级别缺陷',
129	            'status_phase': status,
130	            'severity': severity,
131	            'project': project,
132	            'detected_by': random.choice(TESTERS),
133	            'detected_in_release': random.choice(RELEASES),
134	            'domain': random.choice(DOMAINS),
135	            'aidas': json.dumps(random.sample(['SA1', 'SA2', 'SA3', 'BR1', 'BR2', 'AD1'], k=random.randint(1, 3))),
136	            'top_aida': random.choice(['SA1', 'SA2', 'BR1', 'AD1']),
137	            'tags': json.dumps(random.sample(['回归', '新增', '偶发', '必现', '环境相关'], k=random.randint(0, 2))),
138	            'classification': json.dumps([random.choice(['Functional', 'Performance', 'Interface', 'Crash'])]),
139	            'pingpong': random.randint(0, 5) if random.random() > 0.7 else 0,
140	            'vin': f'LSG{random.randint(100000, 999999)}' if random.random() > 0.6 else '',
141	            'ecu': ecu,
142	            'source_file': f'{year}_defect.json',
143	        }
144	        defects.append(defect)
145	
146	    return defects
147	
148	
149	def generate_sample_runs(n: int = 300) -> List[Dict[str, Any]]:
150	    """生成模拟测试执行数据"""
151	    random.seed(43)
152	    runs = []
153	    periods = [f'R{p}' for p in range(26, 32)]
154	
155	    for i in range(1, n + 1):
156	        run = {
157	            'run_id': f'RUN-{i:06d}',
158	            'report_period': random.choice(periods),
159	            'test_id': f'TC-{random.randint(1, 200):04d}',
160	            'test_name': f'测试用例 {random.choice(["通信", "功能", "性能", "安全", "兼容"])} #{i}',
161	            'run_status': random.choices(['Passed', 'Failed', 'N/A', 'Blocked'], weights=[60, 25, 10, 5])[0],
162	            'tester': random.choice(TESTERS),
163	            'finished_time': datetime(2026, random.randint(1, 6), random.randint(1, 28)).strftime('%Y-%m-%dT%H:%M:%SZ'),
164	            'test_week': f'2026-CW{random.randint(1, 25):02d}',
165	            'project': random.choice(PROJECTS),
166	            'model': random.choice(['ModelA', 'ModelB', 'ModelC']),
167	            'aidas': json.dumps(random.sample(['SA1', 'SA2', 'BR1'], k=1)),
168	            'top_aida': random.choice(['SA1', 'SA2', 'BR1']),
169	        }
170	        runs.append(run)
171	
172	    return runs
173	
174	
175	# ============================================================================
176	# Database Initializer
177	# ============================================================================
178	
179	def init_sample_database(db_path: str, n_defects: int = 500, n_runs: int = 300):
180	    """
181	    初始化样本数据库
182	    
183	    如果数据库已存在且有数据，不会覆盖。
184	    """
185	    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
186	    
187	    conn = sqlite3.connect(db_path)
188	    conn.execute(DEFECTS_SCHEMA)
189	    conn.execute(MANUAL_RUNS_SCHEMA)
190	    conn.execute(DEFECT_HISTORY_SCHEMA)
191	
192	    # Check if already has data
193	    count = conn.execute("SELECT COUNT(*) FROM octane_defects").fetchone()[0]
194	    if count > 0:
195	        conn.close()
196	        return False  # already initialized
197	
198	    # Generate and insert sample data
199	    defects = generate_sample_defects(n_defects)
200	    for d in defects:
201	        conn.execute("""
202	            INSERT OR REPLACE INTO octane_defects
203	            (defect_id, year, creation_time, summary, description, status_phase,
204	             severity, project, detected_by, detected_in_release, domain,
205	             aidas, top_aida, tags, classification, pingpong, vin, ecu, source_file)
206	            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
207	        """, (
208	            d['defect_id'], d['year'], d['creation_time'], d['summary'],
209	            d['description'], d['status_phase'], d['severity'], d['project'],
210	            d['detected_by'], d['detected_in_release'], d['domain'],
211	            d['aidas'], d['top_aida'], d['tags'], d['classification'],
212	            d['pingpong'], d['vin'], d['ecu'], d['source_file'],
213	        ))
214	
215	    runs = generate_sample_runs(n_runs)
216	    for r in runs:
217	        conn.execute("""
218	            INSERT OR REPLACE INTO octane_manual_runs
219	            (run_id, report_period, test_id, test_name, run_status, tester,
220	             finished_time, test_week, project, model, aidas, top_aida)
221	            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
222	        """, (
223	            r['run_id'], r['report_period'], r['test_id'], r['test_name'],
224	            r['run_status'], r['tester'], r['finished_time'], r['test_week'],
225	            r['project'], r['model'], r['aidas'], r['top_aida'],
226	        ))
227	
228	    # Create indexes
229	    conn.execute("CREATE INDEX IF NOT EXISTS idx_defects_project ON octane_defects(project)")
230	    conn.execute("CREATE INDEX IF NOT EXISTS idx_defects_severity ON octane_defects(severity)")
231	    conn.execute("CREATE INDEX IF NOT EXISTS idx_defects_status ON octane_defects(status_phase)")
232	    conn.execute("CREATE INDEX IF NOT EXISTS idx_defects_ecu ON octane_defects(ecu)")
233	    conn.execute("CREATE INDEX IF NOT EXISTS idx_defects_creation ON octane_defects(creation_time)")
234	    conn.execute("CREATE INDEX IF NOT EXISTS idx_defects_year ON octane_defects(year)")
235	
236	    conn.commit()
237	    conn.close()
238	    return True
239	
240	
241	# ============================================================================
242	# Data source resolver
243	# ============================================================================
244	
245	def resolve_data_db_path() -> str:
246	    """
247	    解析数据源 DB 路径
248	
249	    优先级:
250	    1. 环境变量 DATA_DB_PATH（生产环境用）
251	    2. 本地 sample 数据库
252	
253	    生产环境部署时:
254	        export DATA_DB_PATH=/path/to/local_data_rebuilt.db
255	    """
256	    env_path = os.environ.get("DATA_DB_PATH", "")
257	    if env_path and os.path.exists(env_path):
258	        return env_path
259	
260	    # Default: sample DB in data/
261	    sample_path = str(Path(__file__).resolve().parent.parent.parent / "data" / "sample_defects.db")
262	    if not os.path.exists(sample_path):
263	        print(f"[DataAdapter] Initializing sample database at {sample_path} ...")
264	        init_sample_database(sample_path)
265	    return sample_path
266	
267	
268	# ============================================================================
269	# Query helper
270	# ============================================================================
271	
272	def execute_query(db_path: str, sql: str) -> Dict[str, Any]:
273	    """
274	    执行 SQL 查询，返回标准化结果
275	    
276	    Returns:
277	        { "columns": [...], "rows": [...], "rowcount": N }
278	    """
279	    conn = sqlite3.connect(db_path)
280	    conn.row_factory = sqlite3.Row
281	    try:
282	        cursor = conn.execute(sql)
283	        rows = cursor.fetchall()
284	        columns = [d[0] for d in cursor.description] if cursor.description else []
285	        return {
286	            "columns": columns,
287	            "rows": [dict(r) for r in rows],
288	            "rowcount": len(rows),
289	        }
290	    finally:
291	        conn.close()
292

### Q23

1	"""Value Retriever — Dynamic database value lookup
2	
3	Solves the "vocabulary gap": user says "车身控制器" but DB has "BCM".
4	Instead of relying on manual aliases, we:
5	
6	1. Build a fuzzy index from actual DB distinct values at startup
7	2. Use rapidfuzz (Levenshtein-based) for fast candidate retrieval
8	3. Optionally use BGE embeddings for semantic matching
9	4. Inject matched values into SQL generation context
10	
11	Two-tier matching:
12	- Tier 1 (fast): rapidfuzz token_set_ratio, threshold ≥ 70
13	- Tier 2 (semantic, optional): BGE cosine similarity, threshold ≥ 0.7
14	
15	Usage:
16	    from agent.data.value_retriever import get_value_retriever
17	
18	    vr = get_value_retriever(db_path="...")
19	    matches = vr.retrieve("车身控制器", field="assigned_ecu")
20	    # → [{"value": "BCM", "score": 92, "source": "fuzzy"}]
21	
22	    # Auto-detect field from question
23	    matches = vr.retrieve("IDCEVO")  # → [{"value": "IDCEVO", "field": "project", ...}]
24	
25	    # Inject into SQL generation
26	    hints = vr.get_hints_for_question("车身控制器有多少Critical缺陷")
27	    # → {"assigned_ecu": {"query": "车身控制器", "matches": ["BCM"]}}
28	"""
29	
30	from __future__ import annotations
31	
32	import os
33	import re
34	import sqlite3
35	import logging
36	from typing import Dict, List, Optional, Any, Tuple
37	from dataclasses import dataclass, field
38	from pathlib import Path
39	from collections import defaultdict
40	
41	logger = logging.getLogger(__name__)
42	
43	# Try importing rapidfuzz (fast Levenshtein)
44	try:
45	    from rapidfuzz import fuzz, process as rf_process
46	    HAS_RAPIDFUZZ = True
47	except ImportError:
48	    HAS_RAPIDFUZZ = False
49	    logger.warning("rapidfuzz not installed, falling back to difflib")
50	
51	    import difflib
52	
53	    class _FuzzFallback:
54	        @staticmethod
55	        def token_set_ratio(s1, s2):
56	            return int(difflib.SequenceMatcher(None, s1.lower(), s2.lower()).ratio() * 100)
57	
58	    class _ProcessFallback:
59	        @staticmethod
60	        def extract(query, choices, limit=5):
61	            results = []
62	            for choice in choices:
63	                score = _FuzzFallback.token_set_ratio(query, choice)
64	                results.append((choice, score, 0))
65	            results.sort(key=lambda x: x[1], reverse=True)
66	            return results[:limit]
67	
68	    fuzz = _FuzzFallback()
69	    rf_process = _ProcessFallback()
70	
71	
72	# ============================================================================
73	# Data Structures
74	# ============================================================================
75	
76	@dataclass
77	class ValueMatch:
78	    """A single value match result"""
79	    value: str              # Actual DB value
80	    field: str              # Which column
81	    score: float            # Match score (0-100)
82	    source: str             # "exact", "fuzzy", "semantic", "alias"
83	    original_query: str     # What the user typed
84	
85	
86	@dataclass
87	class FieldIndex:
88	    """Index for a single field's values"""
89	    field_name: str
90	    values: List[str]
91	    value_lower: List[str]  # Lowercase for case-insensitive matching
92	    aliases: Dict[str, str] = field(default_factory=dict)  # alias → canonical value
93	
94	    def add_alias(self, alias: str, canonical: str):
95	        self.aliases[alias.lower()] = canonical
96	
97	
98	@dataclass
99	class RetrievalResult:
100	    """Result of a value retrieval request"""
101	    query: str
102	    matches: List[ValueMatch] = field(default_factory=list)
103	    field_detected: Optional[str] = None
104	
105	    @property
106	    def best_match(self) -> Optional[ValueMatch]:
107	        return self.matches[0] if self.matches else None
108	
109	    @property
110	    def values(self) -> List[str]:
111	        """Just the matched values"""
112	        return [m.value for m in self.matches]
113	
114	    def to_sql_values(self) -> str:
115	        """Format as SQL IN clause values"""
116	        if not self.matches:
117	            return ""
118	        if len(self.matches) == 1:
119	            return f"'{self.matches[0].value}'"
120	        return ", ".join(f"'{m.value}'" for m in self.matches)
121	
122	
123	# ============================================================================
124	# Value Retriever
125	# ============================================================================
126	
127	# Fields to index (high-cardinality, commonly filtered)
128	DEFAULT_INDEXED_FIELDS = [
129	    "project",
130	    "assigned_ecu",
131	    "severity",
132	    "status_phase",
133	    "domain",
134	    "top_aida",
135	    "problem_finder_team",
136	    "market",
137	    "phase",
138	    "solution_cluster",
139	    "detected_by",
140	]
141	
142	# Minimum value length to index (skip very short values)
143	MIN_VALUE_LENGTH = 1
144	
145	# Fuzzy match threshold (0-100, higher = stricter)
146	FUZZY_THRESHOLD = 65
147	
148	
149	class ValueRetriever:
150	    """
151	    Dynamic value retrieval from database.
152	
153	    Builds an in-memory index of distinct values for key fields,
154	    then provides fuzzy + alias-based lookup.
155	    """
156	
157	    def __init__(
158	        self,
159	        db_path: Optional[str] = None,
160	        table: str = "octane_defects",
161	        indexed_fields: Optional[List[str]] = None,
162	        ontology=None,
163	    ):
164	        self.db_path = db_path
165	        self.table = table
166	        self.indexed_fields = indexed_fields or DEFAULT_INDEXED_FIELDS
167	        self.ontology = ontology
168	
169	        # Build index
170	        self._indexes: Dict[str, FieldIndex] = {}
171	        self._all_values: List[Tuple[str, str]] = []  # (value, field) for global search
172	
173	        if db_path:
174	            self._build_index()
175	
176	    def _build_index(self):
177	        """Build value indexes from database"""
178	        if not self.db_path:
179	            logger.warning("No DB path, ValueRetriever is empty")
180	            return
181	
182	        try:
183	            conn = sqlite3.connect(self.db_path)
184	            cursor = conn.cursor()
185	
186	            for field_name in self.indexed_fields:
187	                try:
188	                    cursor.execute(
189	                        f"SELECT DISTINCT {field_name} FROM {self.table} "
190	                        f"WHERE {field_name} IS NOT NULL AND TRIM({field_name}) != ''"
191	                    )
192	                    values = [str(r[0]).strip() for r in cursor.fetchall()]
193	                    values = [v for v in values if len(v) >= MIN_VALUE_LENGTH]
194	
195	                    if values:
196	                        idx = FieldIndex(
197	                            field_name=field_name,
198	                            values=values,
199	                            value_lower=[v.lower() for v in values],
200	                        )
201	
202	                        # Load aliases from ontology if available
203	                        if self.ontology:
204	                            self._load_ontology_aliases(idx)
205	
206	                        self._indexes[field_name] = idx
207	
208	                        for v in values:
209	                            self._all_values.append((v, field_name))
210	
211	                except sqlite3.OperationalError:
212	                    # Field doesn't exist in table
213	                    pass
214	
215	            conn.close()
216	
217	            total = sum(len(idx.values) for idx in self._indexes.values())
218	            logger.info(
219	                f"ValueRetriever indexed {total} values across "
220	                f"{len(self._indexes)} fields"
221	            )
222	
223	        except Exception as e:
224	            logger.error(f"Failed to build value index: {e}")
225	
226	    def _load_ontology_aliases(self, idx: FieldIndex):
227	        """Load aliases from ontology YAML for a field"""
228	        if not self.ontology:
229	            return
230	
231	        prop = self.ontology.get_property("Defect", idx.field_name)
232	        if not prop or not prop.aliases:
233	            return
234	
235	        # aliases format: {canonical_value: [alias1, alias2, ...]}
236	        for canonical, aliases in prop.aliases.items():
237	            for alias in aliases:
238	                idx.add_alias(alias, canonical)
239	            # Also add the canonical itself
240	            idx.add_alias(canonical, canonical)
241	
242	    # ==================== Retrieval ====================
243	
244	    def retrieve(
245	        self,
246	        query: str,
247	        field: Optional[str] = None,
248	        top_k: int = 3,
249	    ) -> RetrievalResult:
250	        """
251	        Retrieve matching values for a query string.
252	
253	        Args:
254	            query: User's input (e.g., "车身控制器", "IDCEVO", "critical")
255	            field: Restrict search to a specific field (None = search all)
256	            top_k: Max results
257	
258	        Returns:
259	            RetrievalResult with matches sorted by score
260	        """
261	        result = RetrievalResult(query=query, field_detected=field)
262	        query_lower = query.lower().strip()
263	
264	        if not query_lower:
265	            return result
266	
267	        fields_to_search = [field] if field and field in self._indexes else list(self._indexes.keys())
268	
269	        for field_name in fields_to_search:
270	            idx = self._indexes[field_name]
271	
272	            # Tier 0: Exact match (case-insensitive)
273	            for i, v_lower in enumerate(idx.value_lower):
274	                if v_lower == query_lower:
275	                    result.matches.append(ValueMatch(
276	                        value=idx.values[i],
277	                        field=field_name,
278	                        score=100.0,
279	                        source="exact",
280	                        original_query=query,
281	                    ))
282	                    break
283	
284	            if result.matches and result.matches[-1].source == "exact":
285	                continue  # Exact match found for this field
286	
287	            # Tier 1: Alias match
288	            if query_lower in idx.aliases:
289	                canonical = idx.aliases[query_lower]
290	                result.matches.append(ValueMatch(
291	                    value=canonical,
292	                    field=field_name,
293	                    score=95.0,
294	                    source="alias",
295	                    original_query=query,
296	                ))
297	                continue
298	
299	            # Partial alias match (query contains alias or vice versa)
300	            for alias, canonical in idx.aliases.items():
301	                if len(alias) < 2:
302	                    continue
303	                if alias in query_lower or query_lower in alias:
304	                    score = 85 + (10 * min(len(query_lower), len(alias)) / max(len(query_lower), len(alias)))
305	                    result.matches.append(ValueMatch(
306	                        value=canonical,
307	                        field=field_name,
308	                        score=score,
309	                        source="alias_partial",
310	                        original_query=query,
311	                    ))
312	                    break
313	
314	        # Tier 2: Fuzzy match (only if no exact/alias match)
315	        if not result.matches or all(m.score < 90 for m in result.matches):
316	            for field_name in fields_to_search:
317	                idx = self._indexes[field_name]
318	
319	                # Use rapidfuzz for batch scoring
320	                fuzzy_results = rf_process.extract(
321	                    query_lower,
322	                    idx.value_lower,
323	                    scorer=fuzz.token_set_ratio,
324	                    limit=top_k,
325	                )
326	
327	                for match_value, score, _ in fuzzy_results:
328	                    if score >= FUZZY_THRESHOLD:
329	                        # Find original (non-lowercase) value
330	                        orig_idx = idx.value_lower.index(match_value)
331	                        orig_value = idx.values[orig_idx]
332	
333	                        # Avoid duplicates
334	                        already = any(
335	                            m.value == orig_value and m.field == field_name
336	                            for m in result.matches
337	                        )
338	                        if not already:
339	                            result.matches.append(ValueMatch(
340	                                value=orig_value,
341	                                field=field_name,
342	                                score=float(score),
343	                                source="fuzzy",
344	                                original_query=query,
345	                            ))
346	
347	        # Sort by score and limit
348	        result.matches.sort(key=lambda m: m.score, reverse=True)
349	        result.matches = result.matches[:top_k]
350	
351	        # Auto-detect field if not specified
352	        if not field and result.matches:
353	            result.field_detected = result.matches[0].field
354	
355	        return result
356	
357	    def retrieve_for_fields(
358	        self,
359	        query: str,
360	        top_k_per_field: int = 2,
361	    ) -> Dict[str, RetrievalResult]:
362	        """
363	        Retrieve matches for ALL indexed fields.
364	
365	        Returns a dict: {field_name: RetrievalResult}
366	        Useful for building complete query context.
367	        """
368	        results = {}
369	        for field_name in self._indexes:
370	            r = self.retrieve(query, field=field_name, top_k=top_k_per_field)
371	            if r.matches:
372	                results[field_name] = r
373	        return results
374	
375	    # ==================== Question-Level Helpers ====================
376	
377	    # Field detection keywords
378	    FIELD_KEYWORDS = {
379	        "project": ["项目", "project", "车型", "平台"],
380	        "assigned_ecu": ["ECU", "控制器", "模块", "单元"],
381	        "severity": ["严重", "级别", "severity", "critical", "major", "minor"],
382	        "status_phase": ["状态", "status", "open", "closed", "fixed"],
383	        "domain": ["域", "领域", "domain"],
384	        "problem_finder_team": ["团队", "team", "测试组"],
385	        "market": ["市场", "market", "地区", "区域"],
386	        "top_aida": ["AIDA", "功能域"],
387	        "detected_by": ["测试人员", "发现者", "tester"],
388	        "phase": ["阶段", "phase"],
389	    }
390	
391	    def get_hints_for_question(self, question: str) -> Dict[str, Any]:
392	        """
393	        Analyze a natural language question and return value hints for SQL generation.
394	
395	        Returns:
396	            {
397	                "field_name": {
398	                    "query": "original_text",
399	                    "matches": ["DB_VALUE_1", "DB_VALUE_2"],
400	                    "best": "DB_VALUE_1",
401	                    "sql_in": "'DB_VALUE_1', 'DB_VALUE_2'"
402	                },
403	                ...
404	            }
405	        """
406	        hints = {}
407	
408	        # Strategy 1: Try matching each known value against the question
409	        for field_name, idx in self._indexes.items():
410	            best_match = None
411	            best_score = 0
412	
413	            for value in idx.values:
414	                if len(value) < 2:
415	                    continue
416	                # Check if value appears in question (case-insensitive)
417	                if value.lower() in question.lower():
418	                    score = len(value) * 10  # Longer matches are better
419	                    if score > best_score:
420	                        best_score = score
421	                        best_match = value
422	
423	            # Also check aliases
424	            if not best_match:
425	                for alias, canonical in idx.aliases.items():
426	                    if len(alias) < 2:
427	                        continue
428	                    if alias.lower() in question.lower():
429	                        score = len(alias) * 10
430	                        if score > best_score:
431	                            best_score = score
432	                            best_match = canonical
433	
434	            if best_match:
435	                hints[field_name] = {
436	                    "query": question,
437	                    "matches": [best_match],
438	                    "best": best_match,
439	                    "sql_in": f"'{best_match}'",
440	                }
441	
442	        # Strategy 2: Extract unknown tokens and fuzzy-match them
443	        # Tokenize question
444	        tokens = self._extract_tokens(question)
445	        known_values = set()
446	        for idx in self._indexes.values():
447	            known_values.update(v.lower() for v in idx.values)
448	
449	        for token in tokens:
450	            if token.lower() in known_values:
451	                continue  # Already matched
452	            if len(token) < 2:
453	                continue
454	
455	            r = self.retrieve(token, top_k=1)
456	            if r.best_match and r.best_match.score >= 75 and r.best_match.field not in hints:
457	                field_name = r.best_match.field
458	                hints[field_name] = {
459	                    "query": token,
460	                    "matches": r.values,
461	                    "best": r.best_match.value,
462	                    "sql_in": r.to_sql_values(),
463	                }
464	
465	        return hints
466	
467	    def _extract_tokens(self, question: str) -> List[str]:
468	        """Extract meaningful tokens from question"""
469	        # Split on non-alphanumeric (keeps CJK chars)
470	        tokens = re.findall(r'[\w\u4e00-\u9fff]+', question)
471	        # Filter common stop words
472	        stop_words = {
473	            "的", "了", "在", "是", "有", "多少", "几个", "请", "问",
474	            "the", "a", "an", "how", "many", "what", "which", "show",
475	            "给我", "帮我", "查看", "查询", "统计",
476	        }
477	        return [t for t in tokens if t.lower() not in stop_words and len(t) >= 2]
478	
479	    # ==================== SQL Enhancement ====================
480	
481	    def enhance_sql_conditions(
482	        self,
483	        question: str,
484	        base_where: str = "1=1",
485	    ) -> Tuple[str, Dict[str, Any]]:
486	        """
487	        Generate enhanced WHERE conditions using value retrieval.
488	
489	        Returns:
490	            (enhanced_where_clause, hints_dict)
491	        """
492	        hints = self.get_hints_for_question(question)
493	
494	        conditions = [base_where]
495	        for field_name, hint in hints.items():
496	            values = hint["matches"]
497	            if len(values) == 1:
498	                conditions.append(f"{field_name} = '{values[0]}'")
499	            elif len(values) > 1:
500	                in_clause = ", ".join(f"'{v}'" for v in values)
501	                conditions.append(f"{field_name} IN ({in_clause})")
502	
503	        enhanced = " AND ".join(conditions)
504	        return enhanced, hints
505	
506	    # ==================== Stats & Refresh ====================
507	
508	    def stats(self) -> Dict[str, Any]:
509	        """Return index statistics"""
510	        return {
511	            "total_fields": len(self._indexes),
512	            "total_values": sum(len(idx.values) for idx in self._indexes.values()),
513	            "total_aliases": sum(len(idx.aliases) for idx in self._indexes.values()),
514	            "fields": {
515	                name: {
516	                    "values": len(idx.values),
517	                    "aliases": len(idx.aliases),
518	                }
519	                for name, idx in self._indexes.items()
520	            },
521	        }
522	
523	    def refresh(self):
524	        """Rebuild index from database"""
525	        self._indexes.clear()
526	        self._all_values.clear()
527	        if self.db_path:
528	            self._build_index()
529	
530	
531	# ============================================================================
532	# Singleton
533	# ============================================================================
534	
535	_retriever: Optional[ValueRetriever] = None
536	
537	
538	def get_value_retriever(
539	    db_path: Optional[str] = None,
540	    ontology=None,
541	) -> ValueRetriever:
542	    """Get or create singleton ValueRetriever"""
543	    global _retriever
544	    if _retriever is None:
545	        if db_path is None:
546	            from agent.data.adapter import resolve_data_db_path
547	            db_path = resolve_data_db_path()
548	        _retriever = ValueRetriever(db_path=db_path, ontology=ontology)
549	    return _retriever
550

### Q24

1	"""
2	QueryMemory — 查询记忆引擎
3	
4	存储成功的 NL→SQL 对，支持：
5	1. 相似问题检索（embedding + 关键词混合）
6	2. SQL 复用（高相似度直接复用）
7	3. 结果摘要缓存
8	
9	灵感: WrenAI Memory Layer + 人类工作经验积累
10	"""
11	
12	from __future__ import annotations
13	
14	import json
15	import sqlite3
16	import hashlib
17	import os
18	import re
19	from dataclasses import dataclass, field
20	from datetime import datetime, timedelta
21	from pathlib import Path
22	from typing import Optional, List, Dict, Any, Tuple
23	
24	from agent.learning.semantic_matcher import SemanticMatcher
25	
26	
27	@dataclass
28	class QueryRecord:
29	    """一条查询记忆"""
30	    id: str = ""
31	    question: str = ""
32	    normalized_question: str = ""
33	    sql: str = ""
34	    intent: str = ""
35	    entities: Dict[str, Any] = field(default_factory=dict)
36	    result_summary: str = ""
37	    result_count: int = 0
38	    success: bool = True
39	    feedback: Optional[str] = None  # "up" | "down" | None
40	    feedback_note: str = ""
41	    created_at: str = ""
42	    usage_count: int = 0  # 被检索复用次数
43	    score: float = 1.0  # 综合评分（feedback + usage + recency）
44	
45	    def to_dict(self) -> dict:
46	        return {
47	            "id": self.id,
48	            "question": self.question,
49	            "normalized_question": self.normalized_question,
50	            "sql": self.sql,
51	            "intent": self.intent,
52	            "entities": json.dumps(self.entities, ensure_ascii=False),
53	            "result_summary": self.result_summary,
54	            "result_count": self.result_count,
55	            "success": self.success,
56	            "feedback": self.feedback,
57	            "feedback_note": self.feedback_note,
58	            "created_at": self.created_at,
59	            "usage_count": self.usage_count,
60	            "score": self.score,
61	        }
62	
63	    @classmethod
64	    def from_row(cls, row: sqlite3.Row) -> "QueryRecord":
65	        entities = json.loads(row["entities"]) if row["entities"] else {}
66	        return cls(
67	            id=row["id"],
68	            question=row["question"],
69	            normalized_question=row["normalized_question"],
70	            sql=row["sql"],
71	            intent=row["intent"],
72	            entities=entities,
73	            result_summary=row["result_summary"],
74	            result_count=row["result_count"],
75	            success=bool(row["success"]),
76	            feedback=row["feedback"],
77	            feedback_note=row["feedback_note"],
78	            created_at=row["created_at"],
79	            usage_count=row["usage_count"],
80	            score=row["score"],
81	        )
82	
83	
84	def _normalize_question(q: str) -> str:
85	    """归一化问题文本，用于相似度比较"""
86	    s = q.strip().lower()
87	    s = re.sub(r'\s+', ' ', s)
88	    s = re.sub(r'[，。？！,.?!;；]', '', s)
89	    return s
90	
91	
92	def _extract_keywords(q: str) -> set:
93	    """提取关键词用于快速检索"""
94	    s = _normalize_question(q)
95	    cjk_chars = set()
96	    eng_words = set()
97	    
98	    cjk_pattern = re.compile(r'[\u4e00-\u9fff]+')
99	    for match in cjk_pattern.finditer(s):
100	        text = match.group()
101	        if len(text) >= 2:
102	            for i in range(len(text) - 1):
103	                cjk_chars.add(text[i:i+2])
104	        cjk_chars.add(text)
105	    
106	    eng_pattern = re.compile(r'[a-z0-9_]+')
107	    for match in eng_pattern.finditer(s):
108	        word = match.group()
109	        if len(word) >= 2:
110	            eng_words.add(word)
111	    
112	    return cjk_chars | eng_words
113	
114	
115	def _jaccard_similarity(set_a: set, set_b: set) -> float:
116	    """Jaccard 相似度"""
117	    if not set_a or not set_b:
118	        return 0.0
119	    intersection = set_a & set_b
120	    union = set_a | set_b
121	    return len(intersection) / len(union)
122	
123	
124	def _edit_distance_ratio(a: str, b: str) -> float:
125	    """编辑距离相似度 (0-1, 1=完全相同)"""
126	    if a == b:
127	        return 1.0
128	    if not a or not b:
129	        return 0.0
130	    
131	    m, n = len(a), len(b)
132	    if m > 200 or n > 200:
133	        return _jaccard_similarity(_extract_keywords(a), _extract_keywords(b))
134	    
135	    prev = list(range(n + 1))
136	    for i in range(1, m + 1):
137	        curr = [i] + [0] * n
138	        for j in range(1, n + 1):
139	            cost = 0 if a[i-1] == b[j-1] else 1
140	            curr[j] = min(
141	                curr[j-1] + 1,
142	                prev[j] + 1,
143	                prev[j-1] + cost
144	            )
145	        prev = curr
146	    
147	    distance = prev[n]
148	    return 1.0 - distance / max(m, n)
149	
150	
151	class QueryMemory:
152	    """
153	    查询记忆引擎
154	    
155	    - SQLite 存储（轻量、无外部依赖）
156	    - 关键词索引 + Jaccard/编辑距离混合相似度
157	    - 支持注入 BGE embedding 搜索函数
158	    - 评分 = recency + usage + feedback + similarity
159	    """
160	
161	    def __init__(
162	        self,
163	        db_path: Optional[str] = None,
164	        embedding_search_fn: Optional[Any] = None,
165	        embedding_fn: Optional[Any] = None,
166	    ):
167	        self.db_path = db_path or ":memory:"
168	        self.embedding_search_fn = embedding_search_fn
169	        self._persistent_conn: Optional[sqlite3.Connection] = None
170	        if self.db_path == ":memory:":
171	            self._persistent_conn = sqlite3.connect(":memory:")
172	            self._persistent_conn.row_factory = sqlite3.Row
173	
174	        # Semantic matcher (TF-IDF + optional embedding)
175	        self.semantic_matcher = SemanticMatcher(embedding_fn=embedding_fn)
176	
177	        self._init_db()
178	        self._fit_semantic_matcher()
179	
180	    def _get_conn(self) -> sqlite3.Connection:
181	        if self._persistent_conn is not None:
182	            return self._persistent_conn
183	        conn = sqlite3.connect(self.db_path)
184	        conn.row_factory = sqlite3.Row
185	        return conn
186	
187	    def _close_if_file(self, conn: sqlite3.Connection):
188	        """Close connection only if using file-based DB (not persistent in-memory)"""
189	        if self._persistent_conn is None:
190	            conn.close()
191	
192	    def _init_db(self):
193	        conn = self._get_conn()
194	        conn.execute("""
195	            CREATE TABLE IF NOT EXISTS query_memory (
196	                id TEXT PRIMARY KEY,
197	                question TEXT NOT NULL,
198	                normalized_question TEXT NOT NULL,
199	                sql TEXT NOT NULL,
200	                intent TEXT DEFAULT '',
201	                entities TEXT DEFAULT '{}',
202	                result_summary TEXT DEFAULT '',
203	                result_count INTEGER DEFAULT 0,
204	                success INTEGER DEFAULT 1,
205	                feedback TEXT,
206	                feedback_note TEXT DEFAULT '',
207	                created_at TEXT NOT NULL,
208	                usage_count INTEGER DEFAULT 0,
209	                score REAL DEFAULT 1.0
210	            )
211	        """)
212	        conn.execute("CREATE INDEX IF NOT EXISTS idx_normalized ON query_memory(normalized_question)")
213	        conn.execute("CREATE INDEX IF NOT EXISTS idx_intent ON query_memory(intent)")
214	        conn.execute("CREATE INDEX IF NOT EXISTS idx_score ON query_memory(score DESC)")
215	        conn.commit()
216	        self._close_if_file(conn)
217	
218	    def _make_id(self, question: str, sql: str) -> str:
219	        raw = f"{question}::{sql}"
220	        return hashlib.md5(raw.encode()).hexdigest()[:16]
221	
222	    def record(
223	        self,
224	        question: str,
225	        sql: str,
226	        intent: str = "",
227	        entities: Optional[dict] = None,
228	        result_summary: str = "",
229	        result_count: int = 0,
230	        success: bool = True,
231	    ) -> str:
232	        record_id = self._make_id(question, sql)
233	        now = datetime.now().isoformat()
234	        normalized = _normalize_question(question)
235	        
236	        conn = self._get_conn()
237	        existing = conn.execute(
238	            "SELECT id, usage_count FROM query_memory WHERE id = ?",
239	            (record_id,)
240	        ).fetchone()
241	        
242	        if existing:
243	            conn.execute(
244	                "UPDATE query_memory SET usage_count = usage_count + 1, score = score + 0.1 WHERE id = ?",
245	                (record_id,)
246	            )
247	            conn.commit()
248	            self._close_if_file(conn)
249	            return record_id
250	        
251	        conn.execute("""
252	            INSERT INTO query_memory 
253	            (id, question, normalized_question, sql, intent, entities,
254	             result_summary, result_count, success, feedback, feedback_note,
255	             created_at, usage_count, score)
256	            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, '', ?, 0, ?)
257	        """, (
258	            record_id, question, normalized, sql, intent,
259	            json.dumps(entities or {}, ensure_ascii=False),
260	            result_summary, result_count, 1 if success else 0,
261	            now, 1.0 if success else 0.5
262	        ))
263	        conn.commit()
264	        self._close_if_file(conn)
265	        
266	        # Refit semantic matcher with new data
267	        self._fit_semantic_matcher()
268	        
269	        return record_id
270	
271	    def record_feedback(
272	        self,
273	        record_id: str,
274	        feedback: str,
275	        note: str = "",
276	    ):
277	        if feedback not in ("up", "down"):
278	            raise ValueError(f"feedback must be 'up' or 'down', got: {feedback}")
279	        
280	        conn = self._get_conn()
281	        row = conn.execute(
282	            "SELECT score FROM query_memory WHERE id = ?", (record_id,)
283	        ).fetchone()
284	        
285	        if not row:
286	            self._close_if_file(conn)
287	            return False
288	        
289	        new_score = row["score"]
290	        if feedback == "up":
291	            new_score += 1.0
292	        else:
293	            new_score -= 0.5
294	        
295	        conn.execute(
296	            "UPDATE query_memory SET feedback = ?, feedback_note = ?, score = ? WHERE id = ?",
297	            (feedback, note, new_score, record_id)
298	        )
299	        conn.commit()
300	        self._close_if_file(conn)
301	        return True
302	
303	    def _fit_semantic_matcher(self):
304	        """Fit TF-IDF on existing stored questions"""
305	        conn = self._get_conn()
306	        rows = conn.execute("SELECT normalized_question FROM query_memory WHERE success = 1").fetchall()
307	        self._close_if_file(conn)
308	        documents = [row["normalized_question"] for row in rows]
309	        if documents:
310	            self.semantic_matcher.fit_corpus(documents)
311	
312	    def retrieve_similar(
313	        self,
314	        question: str,
315	        top_k: int = 3,
316	        min_similarity: float = 0.3,
317	    ) -> List[QueryRecord]:
318	        normalized = _normalize_question(question)
319	        query_keywords = _extract_keywords(question)
320	        
321	        conn = self._get_conn()
322	        rows = conn.execute(
323	            "SELECT * FROM query_memory WHERE success = 1 ORDER BY score DESC LIMIT 500"
324	        ).fetchall()
325	        self._close_if_file(conn)
326	        
327	        if not rows:
328	            return []
329	        
330	        scored: List[Tuple[float, QueryRecord]] = []
331	        
332	        for row in rows:
333	            record = QueryRecord.from_row(row)
334	            
335	            # Semantic similarity (TF-IDF or embedding)
336	            semantic_sim = self.semantic_matcher.similarity(question, record.question)
337	            
338	            # Legacy similarity (fallback)
339	            rec_keywords = _extract_keywords(record.normalized_question)
340	            kw_sim = _jaccard_similarity(query_keywords, rec_keywords)
341	            ed_sim = _edit_distance_ratio(normalized, record.normalized_question)
342	            legacy_sim = kw_sim * 0.6 + ed_sim * 0.4
343	            
344	            # Hybrid: prefer semantic, fall back to legacy
345	            hybrid_sim = max(semantic_sim, legacy_sim)
346	            
347	            if normalized in record.normalized_question or record.normalized_question in normalized:
348	                hybrid_sim = max(hybrid_sim, 0.7)
349	            
350	            if record.feedback == "up":
351	                hybrid_sim += 0.05
352	            elif record.feedback == "down":
353	                hybrid_sim -= 0.1
354	            
355	            if hybrid_sim >= min_similarity:
356	                scored.append((hybrid_sim, record))
357	        
358	        scored.sort(key=lambda x: x[0], reverse=True)
359	        return [r for _, r in scored[:top_k]]
360	
361	    def get_by_id(self, record_id: str) -> Optional[QueryRecord]:
362	        conn = self._get_conn()
363	        row = conn.execute(
364	            "SELECT * FROM query_memory WHERE id = ?", (record_id,)
365	        ).fetchone()
366	        self._close_if_file(conn)
367	        return QueryRecord.from_row(row) if row else None
368	
369	    def get_recent(self, limit: int = 10) -> List[QueryRecord]:
370	        conn = self._get_conn()
371	        rows = conn.execute(
372	            "SELECT * FROM query_memory ORDER BY created_at DESC LIMIT ?",
373	            (limit,)
374	        ).fetchall()
375	        self._close_if_file(conn)
376	        return [QueryRecord.from_row(r) for r in rows]
377	
378	    def get_statistics(self) -> Dict[str, Any]:
379	        conn = self._get_conn()
380	        total = conn.execute("SELECT COUNT(*) as c FROM query_memory").fetchone()["c"]
381	        success = conn.execute("SELECT COUNT(*) as c FROM query_memory WHERE success = 1").fetchone()["c"]
382	        up = conn.execute("SELECT COUNT(*) as c FROM query_memory WHERE feedback = 'up'").fetchone()["c"]
383	        down = conn.execute("SELECT COUNT(*) as c FROM query_memory WHERE feedback = 'down'").fetchone()["c"]
384	        avg_score = conn.execute("SELECT AVG(score) as s FROM query_memory").fetchone()["s"]
385	        self._close_if_file(conn)
386	        
387	        return {
388	            "total_records": total,
389	            "successful": success,
390	            "success_rate": success / total if total > 0 else 0,
391	            "thumbs_up": up,
392	            "thumbs_down": down,
393	            "avg_score": avg_score or 0,
394	        }
395	
396	    def clear(self):
397	        conn = self._get_conn()
398	        conn.execute("DELETE FROM query_memory")
399	        conn.commit()
400	        self._close_if_file(conn)
401	
402	    def export_examples(self, limit: int = 50) -> List[dict]:
403	        conn = self._get_conn()
404	        rows = conn.execute(
405	            "SELECT * FROM query_memory WHERE success = 1 AND score >= 1.0 ORDER BY score DESC, usage_count DESC LIMIT ?",
406	            (limit,)
407	        ).fetchall()
408	        self._close_if_file(conn)
409	        
410	        examples = []
411	        for row in rows:
412	            record = QueryRecord.from_row(row)
413	            examples.append({
414	                "question": record.question,
415	                "sql": record.sql,
416	                "intent": record.intent,
417	                "entities": record.entities,
418	            })
419	        return examples
420

### Q25

1	"""Semantic Memory — Embedding-enhanced query matching for QueryMemory
2	
3	Upgrades QueryMemory's Jaccard(60%) + Levenshtein(40%) matching to:
4	1. TF-IDF cosine similarity (always available, no external dependency)
5	2. Pluggable embedding function (BGE, ZhiPu embedding API, etc.)
6	
7	The key insight from Vanna 2.0 and WrenAI: query memory with semantic
8	matching dramatically improves SQL reuse for paraphrased questions.
9	
10	Example:
11	    # Without semantic matching:
12	    "IDCEVO有多少严重缺陷" vs "IDCEVO的Critical缺陷数量" → 0.42 (Jaccard)
13	    
14	    # With TF-IDF + cosine:
15	    Same pair → 0.78 (shares key terms: IDCEVO, 缺陷)
16	    
17	    # With BGE embedding:
18	    Same pair → 0.89 (semantic similarity)
19	
20	Usage:
21	    from agent.learning.semantic_matcher import SemanticMatcher
22	
23	    matcher = SemanticMatcher(embedding_fn=my_embed_fn)
24	    score = matcher.similarity("query1", "query2")
25	    # → 0.89
26	
27	    matches = matcher.find_similar("IDCEVO有多少缺陷", database_of_records)
28	"""
29	
30	from __future__ import annotations
31	
32	import re
33	import math
34	import logging
35	from typing import List, Dict, Optional, Callable, Tuple
36	from dataclasses import dataclass
37	from collections import Counter
38	
39	logger = logging.getLogger(__name__)
40	
41	
42	# ============================================================================
43	# Tokenization
44	# ============================================================================
45	
46	def tokenize(text: str) -> List[str]:
47	    """
48	    CJK-aware tokenization.
49	
50	    For CJK text: 2-character sliding window (bigrams)
51	    For Latin text: word-level tokens
52	    """
53	    text = text.lower().strip()
54	    tokens = []
55	
56	    # CJK bigrams
57	    cjk_pattern = re.compile(r'[\u4e00-\u9fff]+')
58	    cjk_spans = []
59	    pos = 0
60	    for match in cjk_pattern.finditer(text):
61	        cjk_text = match.group()
62	        if len(cjk_text) >= 2:
63	            for i in range(len(cjk_text) - 1):
64	                tokens.append(cjk_text[i:i + 2])
65	            # Also add the full CJK span as a token
66	            if len(cjk_text) <= 6:
67	                tokens.append(cjk_text)
68	        elif len(cjk_text) == 1:
69	            tokens.append(cjk_text)
70	        cjk_spans.append(match.span())
71	
72	    # Latin words (outside CJK spans)
73	    last_end = 0
74	    for start, end in cjk_spans:
75	        between = text[last_end:start]
76	        tokens.extend(_tokenize_latin(between))
77	        last_end = end
78	    tokens.extend(_tokenize_latin(text[last_end:]))
79	
80	    return tokens
81	
82	
83	def _tokenize_latin(text: str) -> List[str]:
84	    """Word-level tokenization for Latin text"""
85	    words = re.findall(r'[a-z0-9_]+', text.lower())
86	    return [w for w in words if len(w) >= 2]
87	
88	
89	# ============================================================================
90	# TF-IDF Vectorizer
91	# ============================================================================
92	
93	class TfidfVectorizer:
94	    """
95	    Lightweight TF-IDF vectorizer.
96	
97	    Builds IDF from a corpus of stored questions.
98	    Computes TF-IDF vectors for similarity comparison.
99	    """
100	
101	    def __init__(self):
102	        self._idf: Dict[str, float] = {}
103	        self._vocabulary: set = set()
104	        self._doc_count: int = 0
105	
106	    def fit(self, documents: List[str]):
107	        """Compute IDF from a corpus"""
108	        self._doc_count = len(documents)
109	        if self._doc_count == 0:
110	            return
111	
112	        df = Counter()  # document frequency
113	        for doc in documents:
114	            tokens = set(tokenize(doc))
115	            for token in tokens:
116	                df[token] += 1
117	                self._vocabulary.add(token)
118	
119	        # IDF = ln(N / df), smoothed
120	        for token, freq in df.items():
121	            self._idf[token] = math.log((self._doc_count + 1) / (freq + 1)) + 1
122	
123	    def vectorize(self, text: str) -> Dict[str, float]:
124	        """Compute TF-IDF vector for a single document"""
125	        tokens = tokenize(text)
126	        if not tokens:
127	            return {}
128	
129	        tf = Counter(tokens)
130	        total = len(tokens)
131	
132	        vector = {}
133	        for token, count in tf.items():
134	            tf_val = count / total
135	            idf_val = self._idf.get(token, math.log(self._doc_count + 1) + 1)
136	            vector[token] = tf_val * idf_val
137	
138	        return vector
139	
140	    @property
141	    def vocabulary_size(self) -> int:
142	        return len(self._vocabulary)
143	
144	
145	def cosine_similarity(v1: Dict[str, float], v2: Dict[str, float]) -> float:
146	    """Cosine similarity between two sparse vectors"""
147	    if not v1 or not v2:
148	        return 0.0
149	
150	    # Dot product
151	    common_keys = set(v1.keys()) & set(v2.keys())
152	    dot = sum(v1[k] * v2[k] for k in common_keys)
153	
154	    # Magnitudes
155	    mag1 = math.sqrt(sum(v * v for v in v1.values()))
156	    mag2 = math.sqrt(sum(v * v for v in v2.values()))
157	
158	    if mag1 == 0 or mag2 == 0:
159	        return 0.0
160	
161	    return dot / (mag1 * mag2)
162	
163	
164	# ============================================================================
165	# Semantic Matcher
166	# ============================================================================
167	
168	# Type for embedding function: fn(text: str) -> List[float]
169	EmbeddingFn = Callable[[str], List[float]]
170	
171	
172	class SemanticMatcher:
173	    """
174	    Semantic similarity matcher.
175	
176	    Three tiers:
177	    1. Embedding cosine (if embedding_fn available) — best quality
178	    2. TF-IDF cosine — always available, good for keyword overlap
179	    3. Fallback to Jaccard (from original QueryMemory)
180	
181	    Usage:
182	        # With BGE/ZhiPu embedding
183	        matcher = SemanticMatcher(embedding_fn=my_embed_fn)
184	
185	        # TF-IDF only
186	        matcher = SemanticMatcher()
187	
188	        # Build corpus
189	        matcher.fit_corpus(["question1", "question2", ...])
190	
191	        # Compare
192	        score = matcher.similarity("new question", "stored question")
193	    """
194	
195	    def __init__(
196	        self,
197	        embedding_fn: Optional[EmbeddingFn] = None,
198	        use_tfidf: bool = True,
199	    ):
200	        self.embedding_fn = embedding_fn
201	        self.use_tfidf = use_tfidf
202	        self._vectorizer = TfidfVectorizer() if use_tfidf else None
203	        self._corpus_fitted = False
204	
205	        # Cache for embeddings (avoid re-computing)
206	        self._embedding_cache: Dict[str, List[float]] = {}
207	
208	    def fit_corpus(self, documents: List[str]):
209	        """Fit TF-IDF on stored questions"""
210	        if self.use_tfidf and documents:
211	            self._vectorizer.fit(documents)
212	            self._corpus_fitted = True
213	
214	    def similarity(self, text1: str, text2: str) -> float:
215	        """
216	        Compute semantic similarity between two texts.
217	        Returns 0-1 score.
218	        """
219	        # Tier 1: Embedding
220	        if self.embedding_fn:
221	            score = self._embedding_similarity(text1, text2)
222	            if score is not None:
223	                return score
224	
225	        # Tier 2: TF-IDF
226	        if self.use_tfidf and self._corpus_fitted:
227	            v1 = self._vectorizer.vectorize(text1)
228	            v2 = self._vectorizer.vectorize(text2)
229	            return cosine_similarity(v1, v2)
230	
231	        # Tier 3: Jaccard fallback
232	        return self._jaccard(text1, text2)
233	
234	    def find_similar(
235	        self,
236	        query: str,
237	        candidates: List[str],
238	        top_k: int = 3,
239	        min_score: float = 0.3,
240	    ) -> List[Tuple[float, str]]:
241	        """
242	        Find similar texts from a list of candidates.
243	
244	        Returns: [(score, candidate_text), ...] sorted by score descending.
245	        """
246	        scored = []
247	        for candidate in candidates:
248	            score = self.similarity(query, candidate)
249	            if score >= min_score:
250	                scored.append((score, candidate))
251	
252	        scored.sort(key=lambda x: x[0], reverse=True)
253	        return scored[:top_k]
254	
255	    # ==================== Internal ====================
256	
257	    def _embedding_similarity(self, text1: str, text2: str) -> Optional[float]:
258	        """Compute embedding cosine similarity"""
259	        try:
260	            v1 = self._get_embedding(text1)
261	            v2 = self._get_embedding(text2)
262	
263	            if v1 is None or v2 is None:
264	                return None
265	
266	            # Dense cosine similarity
267	            dot = sum(a * b for a, b in zip(v1, v2))
268	            mag1 = math.sqrt(sum(a * a for a in v1))
269	            mag2 = math.sqrt(sum(b * b for b in v2))
270	
271	            if mag1 == 0 or mag2 == 0:
272	                return 0.0
273	
274	            return dot / (mag1 * mag2)
275	
276	        except Exception as e:
277	            logger.warning(f"Embedding similarity failed: {e}")
278	            return None
279	
280	    def _get_embedding(self, text: str) -> Optional[List[float]]:
281	        """Get embedding from cache or compute"""
282	        if text in self._embedding_cache:
283	            return self._embedding_cache[text]
284	
285	        try:
286	            embedding = self.embedding_fn(text)
287	            self._embedding_cache[text] = embedding
288	            return embedding
289	        except Exception as e:
290	            logger.warning(f"Embedding failed for '{text[:30]}': {e}")
291	            return None
292	
293	    @staticmethod
294	    def _jaccard(a: str, b: str) -> float:
295	        """Jaccard similarity fallback"""
296	        tokens_a = set(tokenize(a))
297	        tokens_b = set(tokenize(b))
298	        if not tokens_a or not tokens_b:
299	            return 0.0
300	        return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)
301

### Q26

1	"""
2	FeedbackStore — 用户反馈存储与权重管理
3	
4	功能：
5	1. 存储用户对查询结果的 👍/👎 反馈
6	2. 基于反馈调整 SQL 候选排序权重
7	3. 反馈笔记存储（用户给出的具体修正意见）
8	4. 反馈统计与报告
9	"""
10	
11	from __future__ import annotations
12	
13	import json
14	import sqlite3
15	import hashlib
16	from dataclasses import dataclass, field
17	from datetime import datetime
18	from typing import Optional, List, Dict, Any
19	
20	
21	@dataclass
22	class FeedbackRecord:
23	    """一条用户反馈"""
24	    id: str = ""
25	    query_memory_id: str = ""
26	    feedback_type: str = ""  # "up" | "down"
27	    note: str = ""
28	    question: str = ""
29	    sql: str = ""
30	    correction: str = ""
31	    created_at: str = ""
32	
33	    def to_dict(self) -> dict:
34	        return {
35	            "id": self.id,
36	            "query_memory_id": self.query_memory_id,
37	            "feedback_type": self.feedback_type,
38	            "note": self.note,
39	            "question": self.question,
40	            "sql": self.sql,
41	            "correction": self.correction,
42	            "created_at": self.created_at,
43	        }
44	
45	
46	class FeedbackStore:
47	    """
48	    反馈存储引擎
49	    
50	    - SQLite 存储
51	    - 与 QueryMemory 通过 record_id 关联
52	    - 提供权重调整建议
53	    """
54	
55	    def __init__(self, db_path: Optional[str] = None):
56	        self.db_path = db_path or ":memory:"
57	        self._persistent_conn: Optional[sqlite3.Connection] = None
58	        if self.db_path == ":memory:":
59	            self._persistent_conn = sqlite3.connect(":memory:")
60	            self._persistent_conn.row_factory = sqlite3.Row
61	        self._init_db()
62	
63	    def _get_conn(self) -> sqlite3.Connection:
64	        if self._persistent_conn is not None:
65	            return self._persistent_conn
66	        conn = sqlite3.connect(self.db_path)
67	        conn.row_factory = sqlite3.Row
68	        return conn
69	
70	    def _close_if_file(self, conn: sqlite3.Connection):
71	        if self._persistent_conn is None:
72	            conn.close()
73	
74	    def _init_db(self):
75	        conn = self._get_conn()
76	        conn.execute("""
77	            CREATE TABLE IF NOT EXISTS feedback (
78	                id TEXT PRIMARY KEY,
79	                query_memory_id TEXT NOT NULL,
80	                feedback_type TEXT NOT NULL,
81	                note TEXT DEFAULT '',
82	                question TEXT DEFAULT '',
83	                sql TEXT DEFAULT '',
84	                correction TEXT DEFAULT '',
85	                created_at TEXT NOT NULL,
86	                FOREIGN KEY (query_memory_id) REFERENCES query_memory(id)
87	            )
88	        """)
89	        conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_memory ON feedback(query_memory_id)")
90	        conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback(feedback_type)")
91	        conn.commit()
92	        self._close_if_file(conn)
93	
94	    def record(
95	        self,
96	        query_memory_id: str,
97	        feedback_type: str,
98	        note: str = "",
99	        question: str = "",
100	        sql: str = "",
101	        correction: str = "",
102	    ) -> str:
103	        if feedback_type not in ("up", "down"):
104	            raise ValueError(f"feedback_type must be 'up' or 'down'")
105	
106	        fid = hashlib.md5(
107	            f"{query_memory_id}::{feedback_type}::{datetime.now().isoformat()}".encode()
108	        ).hexdigest()[:16]
109	        
110	        now = datetime.now().isoformat()
111	        
112	        conn = self._get_conn()
113	        conn.execute("""
114	            INSERT INTO feedback (id, query_memory_id, feedback_type, note, question, sql, correction, created_at)
115	            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
116	        """, (fid, query_memory_id, feedback_type, note, question, sql, correction, now))
117	        
118	        # Also update QueryMemory table
119	        if feedback_type == "up":
120	            conn.execute(
121	                "UPDATE query_memory SET feedback = 'up', score = score + 1.0 WHERE id = ?",
122	                (query_memory_id,)
123	            )
124	        else:
125	            conn.execute(
126	                "UPDATE query_memory SET feedback = 'down', score = score - 0.5 WHERE id = ?",
127	                (query_memory_id,)
128	            )
129	        
130	        conn.commit()
131	        self._close_if_file(conn)
132	        return fid
133	
134	    def get_by_query(self, query_memory_id: str) -> List[FeedbackRecord]:
135	        conn = self._get_conn()
136	        rows = conn.execute(
137	            "SELECT * FROM feedback WHERE query_memory_id = ? ORDER BY created_at DESC",
138	            (query_memory_id,)
139	        ).fetchall()
140	        self._close_if_file(conn)
141	        return [self._row_to_record(r) for r in rows]
142	
143	    def get_recent(self, limit: int = 20) -> List[FeedbackRecord]:
144	        conn = self._get_conn()
145	        rows = conn.execute(
146	            "SELECT * FROM feedback ORDER BY created_at DESC LIMIT ?",
147	            (limit,)
148	        ).fetchall()
149	        self._close_if_file(conn)
150	        return [self._row_to_record(r) for r in rows]
151	
152	    def get_statistics(self) -> Dict[str, Any]:
153	        conn = self._get_conn()
154	        total = conn.execute("SELECT COUNT(*) as c FROM feedback").fetchone()["c"]
155	        up = conn.execute("SELECT COUNT(*) as c FROM feedback WHERE feedback_type = 'up'").fetchone()["c"]
156	        down = conn.execute("SELECT COUNT(*) as c FROM feedback WHERE feedback_type = 'down'").fetchone()["c"]
157	        
158	        negative_notes = conn.execute(
159	            "SELECT question, note, correction FROM feedback WHERE feedback_type = 'down' AND note != '' ORDER BY created_at DESC LIMIT 10"
160	        ).fetchall()
161	        self._close_if_file(conn)
162	        
163	        return {
164	            "total": total,
165	            "thumbs_up": up,
166	            "thumbs_down": down,
167	            "satisfaction_rate": up / total if total > 0 else 0,
168	            "negative_notes": [
169	                {"question": r["question"], "note": r["note"], "correction": r["correction"]}
170	                for r in negative_notes
171	            ],
172	        }
173	
174	    def get_weight_adjustments(self) -> Dict[str, float]:
175	        conn = self._get_conn()
176	        rows = conn.execute("""
177	            SELECT qm.intent, 
178	                   SUM(CASE WHEN f.feedback_type = 'up' THEN 1 ELSE 0 END) as up_count,
179	                   SUM(CASE WHEN f.feedback_type = 'down' THEN 1 ELSE 0 END) as down_count
180	            FROM feedback f
181	            JOIN query_memory qm ON f.query_memory_id = qm.id
182	            GROUP BY qm.intent
183	        """).fetchall()
184	        self._close_if_file(conn)
185	        
186	        adjustments = {}
187	        for row in rows:
188	            intent = row["intent"] or "unknown"
189	            up, down = row["up_count"], row["down_count"]
190	            total = up + down
191	            
192	            if total < 2:
193	                continue
194	            
195	            satisfaction = up / total
196	            if satisfaction >= 0.8:
197	                adjustments[intent] = 0.1
198	            elif satisfaction <= 0.4:
199	                adjustments[intent] = -0.2
200	        
201	        return adjustments
202	
203	    def _row_to_record(self, row: sqlite3.Row) -> FeedbackRecord:
204	        return FeedbackRecord(
205	            id=row["id"],
206	            query_memory_id=row["query_memory_id"],
207	            feedback_type=row["feedback_type"],
208	            note=row["note"],
209	            question=row["question"],
210	            sql=row["sql"],
211	            correction=row["correction"],
212	            created_at=row["created_at"],
213	        )
214

### Q27

1	"""Conversation Context — Multi-turn dialogue management
2	
3	Inspired by BIRD-Interact (ICLR 2026 Oral):
4	- Multi-turn interactions where users refine queries
5	- Coreference resolution ("其中", "这些", "上面提到的")
6	- Implicit constraint inheritance (previous filters carry forward)
7	- Turn type detection (refine, follow-up, new_topic, clarify)
8	
9	Key design:
10	1. TurnHistory: stores all prior turns (question + SQL + result summary)
11	2. ContextResolver: merges prior context into current question
12	3. The resolver produces a "resolved question" that can be processed
13	   as if the user asked it fresh, but with all necessary context.
14	
15	Example:
16	    Turn 1: "IDCEVO有多少Critical缺陷" → 23个
17	    Turn 2: "按ECU分布呢" → "IDCEVO项目中Critical缺陷按ECU分布"
18	    Turn 3: "IHU的有多少" → "IDCEVO项目中Critical缺陷中IHU有多少"
19	
20	Usage:
21	    from agent.conversation.context import ConversationContext
22	
23	    ctx = ConversationContext(llm_call_fn=my_fn)
24	    ctx.add_turn("IDCEVO有多少Critical缺陷", sql, "23个")
25	    resolved = ctx.resolve("按ECU分布呢")
26	    # → "IDCEVO项目中Critical缺陷按ECU分布呢"
27	"""
28	
29	from __future__ import annotations
30	
31	import logging
32	import time
33	import json
34	from typing import List, Dict, Optional, Any, Callable
35	from dataclasses import dataclass, field
36	from enum import Enum
37	
38	logger = logging.getLogger(__name__)
39	
40	
41	# ============================================================================
42	# Data Models
43	# ============================================================================
44	
45	class TurnType(Enum):
46	    """Type of user turn in multi-turn dialogue"""
47	    INITIAL = "initial"        # First question or topic change
48	    REFINE = "refine"          # Refine previous query ("按ECU分布呢")
49	    FOLLOW_UP = "follow_up"    # Follow-up question ("IHU的有多少")
50	    CLARIFY = "clarify"        # Clarification ("我说的是IDCEVO不是IDC")
51	    COMPARE = "compare"        # Compare with previous result
52	
53	
54	@dataclass
55	class TurnRecord:
56	    """A single conversation turn"""
57	    turn_index: int = 0
58	    question: str = ""
59	    resolved_question: str = ""    # After context resolution
60	    sql: str = ""
61	    intent: str = ""
62	    result_summary: str = ""
63	    result_count: int = 0
64	    entities: Dict[str, Any] = field(default_factory=dict)
65	    turn_type: TurnType = TurnType.INITIAL
66	    timestamp: float = field(default_factory=time.time)
67	
68	    def to_dict(self) -> dict:
69	        return {
70	            "turn_index": self.turn_index,
71	            "question": self.question,
72	            "resolved_question": self.resolved_question,
73	            "sql": self.sql,
74	            "intent": self.intent,
75	            "result_summary": self.result_summary,
76	            "result_count": self.result_count,
77	            "entities": self.entities,
78	            "turn_type": self.turn_type.value,
79	            "timestamp": self.timestamp,
80	        }
81	
82	
83	# ============================================================================
84	# Turn Classifier
85	# ============================================================================
86	
87	class TurnClassifier:
88	    """
89	    Classify user turn type based on question characteristics.
90	
91	    Heuristics:
92	    - Contains pronouns/demonstratives → REFINE or FOLLOW_UP
93	    - Very short (< 8 chars) → likely FOLLOW_UP
94	    - Contains comparison keywords → COMPARE
95	    - Contains correction keywords → CLARIFY
96	    - Otherwise → INITIAL (new topic)
97	    """
98	
99	    # Pronouns and demonstratives (Chinese + English)
100	    REFERENCE_KEYWORDS = {
101	        "其中", "这些", "上面", "刚才", "那个", "这", "那",
102	        "其中", "里面的", "它们的", "其",
103	        "them", "those", "these", "that", "this", "above",
104	        "it", "their", "previous",
105	    }
106	
107	    # Refinement keywords
108	    REFINE_KEYWORDS = {
109	        "按", "根据", "分组", "分布", "排名", "排序", "统计",
110	        "呢", "怎么样", "如何",
111	        "group", "by", "distribution", "rank", "sort", "breakdown",
112	    }
113	
114	    # Correction keywords
115	    CLARIFY_KEYWORDS = {
116	        "不是", "我说的是", "应该是", "错了", "不对",
117	        "不是那个", "更正", "纠正",
118	        "not", "I meant", "correction", "actually",
119	    }
120	
121	    # Comparison keywords
122	    COMPARE_KEYWORDS = {
123	        "对比", "比较", "vs", "和...比", "差异", "区别",
124	        "compare", "comparison", "vs", "difference", "versus",
125	    }
126	
127	    def classify(
128	        self,
129	        question: str,
130	        history: List[TurnRecord],
131	    ) -> TurnType:
132	        """Classify the turn type"""
133	        if not history:
134	            return TurnType.INITIAL
135	
136	        q_lower = question.lower().strip()
137	
138	        # Check correction first (highest priority)
139	        for kw in self.CLARIFY_KEYWORDS:
140	            if kw in q_lower:
141	                return TurnType.CLARIFY
142	
143	        # Check comparison
144	        for kw in self.COMPARE_KEYWORDS:
145	            if kw in q_lower:
146	                return TurnType.COMPARE
147	
148	        # Check reference words → REFINE or FOLLOW_UP
149	        has_reference = any(kw in q_lower for kw in self.REFERENCE_KEYWORDS)
150	        has_refine = any(kw in q_lower for kw in self.REFINE_KEYWORDS)
151	
152	        # Check if question shares tokens with previous
153	        shares_tokens = False
154	        if history:
155	            last_turn = history[-1]
156	            # CJK-aware token overlap: use 2-gram characters
157	            q_tokens = set()
158	            for i in range(len(q_lower) - 1):
159	                q_tokens.add(q_lower[i:i+2])
160	            last_lower = last_turn.question.lower()
161	            last_tokens = set()
162	            for i in range(len(last_lower) - 1):
163	                last_tokens.add(last_lower[i:i+2])
164	            common = q_tokens & last_tokens
165	            shares_tokens = len(common) >= 3  # At least 3 bigrams overlap
166	
167	        is_short = len(question.strip()) < 8
168	
169	        # REFINE keywords (按, 分布, 排名...) are strong signals on their own
170	        if has_refine and history:
171	            return TurnType.REFINE
172	        if has_reference:
173	            return TurnType.FOLLOW_UP
174	        if is_short and shares_tokens:
175	            return TurnType.FOLLOW_UP
176	
177	        # No overlap with previous turns → INITIAL
178	        return TurnType.INITIAL
179	
180	
181	# ============================================================================
182	# Context Resolver
183	# ============================================================================
184	
185	class ContextResolver:
186	    """
187	    Resolve a user question with conversation context.
188	
189	    Two approaches:
190	    1. Rule-based: merge entities and filters from previous turns
191	    2. LLM-based: ask LLM to rewrite the question with full context
192	
193	    The LLM approach is more accurate but requires an API call.
194	    """
195	
196	    # Context resolution prompt
197	    RESOLUTION_PROMPT = """你是一个多轮对话上下文解析器。
198	
199	对话历史：
200	{history}
201	
202	用户当前问题：{question}
203	
204	请根据对话历史，将用户的当前问题重写为一个完整的、独立的问题。
205	要求：
206	1. 补全省略的主语、宾语、条件
207	2. 继承之前查询的筛选条件（项目、严重程度等）
208	3. 不要改变用户的原始意图
209	4. 如果当前问题已经是完整的，直接返回原文
210	
211	只输出重写后的问题，不要解释。
212	
213	示例：
214	历史：Q: IDCEVO有多少Critical缺陷 → A: 23个
215	当前：按ECU分布呢
216	重写：IDCEVO项目中Critical缺陷按ECU分布
217	
218	历史：Q: 各项目缺陷数量 → A: IDCEVO 111, MGU 105...
219	当前：第一名的是哪些ECU
220	重写：缺陷数量最多的项目(IDCEVO)中，各ECU的缺陷分布
221	"""
222	
223	    def __init__(
224	        self,
225	        llm_call_fn: Optional[Callable] = None,
226	        max_history_turns: int = 5,
227	    ):
228	        self.llm_call_fn = llm_call_fn
229	        self.max_history_turns = max_history_turns
230	
231	    def resolve(
232	        self,
233	        question: str,
234	        history: List[TurnRecord],
235	        turn_type: TurnType,
236	    ) -> str:
237	        """
238	        Resolve a question using conversation history.
239	
240	        Returns the resolved (context-complete) question.
241	        """
242	        if turn_type == TurnType.INITIAL or not history:
243	            return question
244	
245	        # Try LLM-based resolution first
246	        if self.llm_call_fn:
247	            resolved = self._llm_resolve(question, history)
248	            if resolved:
249	                return resolved
250	
251	        # Fall back to rule-based resolution
252	        return self._rule_resolve(question, history, turn_type)
253	
254	    def _llm_resolve(
255	        self,
256	        question: str,
257	        history: List[TurnRecord],
258	    ) -> Optional[str]:
259	        """Use LLM to rewrite question with context"""
260	        try:
261	            # Build history text
262	            history_text = self._format_history(history)
263	
264	            prompt = self.RESOLUTION_PROMPT.format(
265	                history=history_text,
266	                question=question,
267	            )
268	
269	            # Call LLM (text mode)
270	            response = self.llm_call_fn(
271	                messages=[
272	                    {"role": "system", "content": "你是一个问题重写助手。"},
273	                    {"role": "user", "content": prompt},
274	                ],
275	                tools=[],  # No tools, just text
276	            )
277	
278	            # Extract text from response
279	            if isinstance(response, str):
280	                return response.strip()
281	            if isinstance(response, dict):
282	                return response.get("content", "").strip()
283	            if isinstance(response, list) and response:
284	                # Might be a list of choices
285	                return str(response[0]).strip()
286	
287	            return None
288	
289	        except Exception as e:
290	            logger.warning(f"LLM context resolution failed: {e}")
291	            return None
292	
293	    def _rule_resolve(
294	        self,
295	        question: str,
296	        history: List[TurnRecord],
297	        turn_type: TurnType,
298	    ) -> str:
299	        """Rule-based context resolution (no LLM)"""
300	        if not history:
301	            return question
302	
303	        last_turn = history[-1]
304	        resolved = question
305	
306	        # For REFINE: prepend the previous query context
307	        if turn_type == TurnType.REFINE:
308	            # If question starts with refinement keyword, prepend context
309	            context_parts = []
310	
311	            # Extract key entities from previous turn
312	            prev_entities = last_turn.entities
313	            if prev_entities:
314	                project = prev_entities.get("project")
315	                if project:
316	                    context_parts.append(f"{project}项目中")
317	                severity = prev_entities.get("severity")
318	                if severity:
319	                    context_parts.append(f"{severity}级别的")
320	                ecu = prev_entities.get("assigned_ecu")
321	                if ecu:
322	                    context_parts.append(f"{ecu}的")
323	
324	            if context_parts:
325	                prefix = "".join(context_parts)
326	                resolved = f"{prefix}{question}"
327	
328	        elif turn_type == TurnType.FOLLOW_UP:
329	            # For FOLLOW_UP: if question is short, inherit previous subject
330	            if len(question.strip()) < 15:
331	                # Use previous question's subject
332	                prev_q = last_turn.resolved_question or last_turn.question
333	                resolved = f"关于「{prev_q}」的结果，{question}"
334	
335	        elif turn_type == TurnType.CLARIFY:
336	            # For CLARIFY: just use the question as-is (user is correcting)
337	            resolved = question
338	
339	        return resolved
340	
341	    def _format_history(self, history: List[TurnRecord]) -> str:
342	        """Format conversation history for LLM prompt"""
343	        lines = []
344	        # Use last N turns
345	        for turn in history[-self.max_history_turns:]:
346	            lines.append(
347	                f"Q: {turn.question}\n"
348	                f"A: {turn.result_summary or '(SQL: ' + turn.sql[:60] + ')'}"
349	            )
350	        return "\n\n".join(lines)
351	
352	
353	# ============================================================================
354	# Conversation Context
355	# ============================================================================
356	
357	class ConversationContext:
358	    """
359	    Manages multi-turn conversation context.
360	
361	    Usage:
362	        ctx = ConversationContext(llm_call_fn=my_fn)
363	
364	        # Turn 1
365	        resolved = ctx.resolve("IDCEVO有多少Critical缺陷")
366	        # → "IDCEVO有多少Critical缺陷" (initial, no change)
367	        ctx.add_turn(question="IDCEVO有多少Critical缺陷",
368	                     resolved_question=resolved,
369	                     sql="SELECT COUNT(*)...",
370	                     result_summary="23个")
371	
372	        # Turn 2
373	        resolved = ctx.resolve("按ECU分布呢")
374	        # → "IDCEVO项目中Critical缺陷按ECU分布" (refined)
375	
376	        # Turn 3
377	        resolved = ctx.resolve("IHU的有多少")
378	        # → "IDCEVO项目中Critical缺陷中IHU有多少" (follow-up)
379	
380	        # Get full history
381	        history = ctx.get_history()
382	    """
383	
384	    def __init__(
385	        self,
386	        llm_call_fn: Optional[Callable] = None,
387	        max_history: int = 10,
388	        session_id: str = "",
389	    ):
390	        self.session_id = session_id
391	        self.max_history = max_history
392	        self.classifier = TurnClassifier()
393	        self.resolver = ContextResolver(
394	            llm_call_fn=llm_call_fn,
395	            max_history_turns=max_history,
396	        )
397	        self._turns: List[TurnRecord] = []
398	
399	    @property
400	    def turn_count(self) -> int:
401	        return len(self._turns)
402	
403	    @property
404	    def turns(self) -> List[TurnRecord]:
405	        return list(self._turns)
406	
407	    def resolve(self, question: str) -> str:
408	        """
409	        Resolve the current question using conversation context.
410	
411	        Returns the resolved question (may be same as input if initial).
412	        Does NOT add the turn to history (call add_turn after execution).
413	        """
414	        turn_type = self.classifier.classify(question, self._turns)
415	        return self.resolver.resolve(question, self._turns, turn_type)
416	
417	    def classify(self, question: str) -> TurnType:
418	        """Classify the turn type without resolving"""
419	        return self.classifier.classify(question, self._turns)
420	
421	    def add_turn(
422	        self,
423	        question: str,
424	        resolved_question: str = "",
425	        sql: str = "",
426	        intent: str = "",
427	        result_summary: str = "",
428	        result_count: int = 0,
429	        entities: Optional[Dict[str, Any]] = None,
430	    ):
431	        """Record a completed turn"""
432	        turn_type = self.classifier.classify(question, self._turns)
433	
434	        turn = TurnRecord(
435	            turn_index=len(self._turns),
436	            question=question,
437	            resolved_question=resolved_question or question,
438	            sql=sql,
439	            intent=intent,
440	            result_summary=result_summary,
441	            result_count=result_count,
442	            entities=entities or {},
443	            turn_type=turn_type,
444	        )
445	        self._turns.append(turn)
446	
447	        # Trim history
448	        if len(self._turns) > self.max_history:
449	            self._turns = self._turns[-self.max_history:]
450	
451	    def get_history(self) -> List[TurnRecord]:
452	        """Get conversation history"""
453	        return list(self._turns)
454	
455	    def get_history_text(self, max_turns: int = 3) -> str:
456	        """Get formatted history text for prompt injection"""
457	        turns = self._turns[-max_turns:]
458	        if not turns:
459	            return ""
460	
461	        lines = []
462	        for t in turns:
463	            lines.append(
464	                f"之前问过: {t.question}\n"
465	                f"结果: {t.result_summary or '已查询'}"
466	            )
467	        return "\n\n".join(lines)
468	
469	    def clear(self):
470	        """Clear conversation history"""
471	        self._turns.clear()
472	
473	    def get_context_summary(self) -> Dict[str, Any]:
474	        """Get a summary of current conversation state"""
475	        if not self._turns:
476	            return {"turn_count": 0, "active_context": False}
477	
478	        last = self._turns[-1]
479	        return {
480	            "turn_count": len(self._turns),
481	            "active_context": True,
482	            "last_question": last.question,
483	            "last_intent": last.intent,
484	            "last_entities": last.entities,
485	            "last_turn_type": last.turn_type.value,
486	        }
487	
488	
489	# ============================================================================
490	# Session Manager (multi-session support)
491	# ============================================================================
492	
493	class SessionManager:
494	    """
495	    Manage conversation contexts for multiple sessions.
496	
497	    Each session (identified by session_id) has its own ConversationContext.
498	    Sessions expire after a period of inactivity.
499	    """
500	
501	    def __init__(
502	        self,
503	        llm_call_fn: Optional[Callable] = None,
504	        session_timeout: float = 1800,  # 30 minutes
505	    ):
506	        self.llm_call_fn = llm_call_fn
507	        self.session_timeout = session_timeout
508	        self._sessions: Dict[str, ConversationContext] = {}
509	        self._last_active: Dict[str, float] = {}
510	
511	    def get_session(self, session_id: str) -> ConversationContext:
512	        """Get or create a conversation context for a session"""
513	        self._cleanup_expired()
514	
515	        if session_id not in self._sessions:
516	            self._sessions[session_id] = ConversationContext(
517	                llm_call_fn=self.llm_call_fn,
518	                session_id=session_id,
519	            )
520	
521	        self._last_active[session_id] = time.time()
522	        return self._sessions[session_id]
523	
524	    def remove_session(self, session_id: str):
525	        """Remove a session"""
526	        self._sessions.pop(session_id, None)
527	        self._last_active.pop(session_id, None)
528	
529	    def _cleanup_expired(self):
530	        """Remove expired sessions"""
531	        now = time.time()
532	        expired = [
533	            sid for sid, last in self._last_active.items()
534	            if now - last > self.session_timeout
535	        ]
536	        for sid in expired:
537	            self._sessions.pop(sid, None)
538	            self._last_active.pop(sid, None)
539	
540	    def get_active_sessions(self) -> List[str]:
541	        """Get list of active session IDs"""
542	        self._cleanup_expired()
543	        return list(self._sessions.keys())
544

### Q28

1	"""Python Code Interpreter — Safe sandboxed execution for data analysis
2	
3	When SQL can't express complex logic (statistical tests, custom
4	transformations, anomaly detection), the LLM generates Python code
5	that operates on query results.
6	
7	Design:
8	1. CodeGen: LLM generates Python code from NL + data context
9	2. Sandbox: Restricted exec with timeout, no network, no file write
10	3. Formatter: Convert execution result to natural language
11	
12	Safety:
13	- subprocess with timeout
14	- Restricted globals (no __import__, no open, no os/system)
15	- Memory limit via input data size cap
16	- Only pandas/numpy/math/re available
17	
18	Usage:
19	    from agent.interpret.code_interpreter import CodeInterpreter
20	
21	    ci = CodeInterpreter(llm_call_fn=my_fn, db_path='/path/to/db')
22	    result = ci.execute(
23	        question='哪个ECU的缺陷增长率最高',
24	        data=[{'ecu': 'IHU', 'count': 100}, ...],
25	    )
26	    # → {'success': True, 'output': 'IHU has highest growth...', 'code': '...'}
27	"""
28	
29	from __future__ import annotations
30	
31	import json
32	import logging
33	import subprocess
34	import sys
35	import tempfile
36	import time
37	import textwrap
38	from pathlib import Path
39	from typing import List, Dict, Optional, Any, Callable
40	
41	logger = logging.getLogger(__name__)
42	
43	
44	# ============================================================================
45	# Code Generation Prompt
46	# ============================================================================
47	
48	CODE_GEN_PROMPT = """你是一个 Python 数据分析代码生成器。
49	
50	用户问题：{question}
51	
52	查询结果数据（JSON 格式）：
53	{data}
54	
55	请生成 Python 代码来分析上述数据，回答用户问题。
56	
57	可用库：pandas, numpy, math, re, json, statistics
58	限制：
59	- 不要 import 其它库
60	- 不要读写文件
61	- 不要访问网络
62	- 代码必须在 3 秒内完成
63	
64	数据已加载为变量 `data`（list of dict）。
65	请将最终分析结果赋值给变量 `result`（字符串或数字）。
66	
67	只输出 Python 代码，不要解释。
68	"""
69	
70	
71	# ============================================================================
72	# Code Interpreter
73	# ============================================================================
74	
75	class CodeInterpreter:
76	    """
77	    Generate and execute Python code for complex data analysis.
78	
79	    Flow:
80	    1. LLM generates Python code from question + data
81	    2. Code is executed in a subprocess sandbox
82	    3. Result is extracted and returned
83	
84	    When LLM is not available, falls back to basic statistical functions.
85	    """
86	
87	    # Safe imports allowed in generated code
88	    SAFE_IMPORTS = {
89	        "pandas", "numpy", "math", "re", "json",
90	        "statistics", "collections", "itertools",
91	    }
92	
93	    # Forbidden patterns in code
94	    FORBIDDEN_PATTERNS = [
95	        "import os",
96	        "import sys",
97	        "import subprocess",
98	        "import socket",
99	        "import urllib",
100	        "import requests",
101	        "import http",
102	        "import shutil",
103	        "import pickle",
104	        "import marshal",
105	        "import ctypes",
106	        "__import__",
107	        "open(",
108	        "exec(",
109	        "eval(",
110	        "compile(",
111	        "globals(",
112	        "locals(",
113	    ]
114	
115	    def __init__(
116	        self,
117	        llm_call_fn: Optional[Callable] = None,
118	        timeout: int = 5,
119	    ):
120	        self.llm_call_fn = llm_call_fn
121	        self.timeout = timeout
122	
123	    def execute(
124	        self,
125	        question: str,
126	        data: List[Dict[str, Any]],
127	    ) -> Dict[str, Any]:
128	        """
129	        Generate and execute Python code to analyze data.
130	
131	        Returns:
132	            {
133	                'success': bool,
134	                'output': str,      # result or error
135	                'code': str,        # generated code
136	                'time_ms': float,
137	            }
138	        """
139	        start = time.time()
140	
141	        # Generate code
142	        code = self._generate_code(question, data)
143	        if not code:
144	            return {
145	                'success': False,
146	                'output': '无法生成分析代码',
147	                'code': '',
148	                'time_ms': (time.time() - start) * 1000,
149	            }
150	
151	        # Safety check
152	        safety = self._check_safety(code)
153	        if not safety['safe']:
154	            return {
155	                'success': False,
156	                'output': f'安全检查失败: {safety["reason"]}',
157	                'code': code,
158	                'time_ms': (time.time() - start) * 1000,
159	            }
160	
161	        # Execute
162	        result = self._execute_sandbox(code, data)
163	
164	        return {
165	            'success': result['success'],
166	            'output': result['output'],
167	            'code': code,
168	            'time_ms': (time.time() - start) * 1000,
169	            'error': result.get('error', ''),
170	        }
171	
172	    def _generate_code(
173	        self,
174	        question: str,
175	        data: List[Dict[str, Any]],
176	    ) -> Optional[str]:
177	        """Generate Python code via LLM"""
178	        if not self.llm_call_fn:
179	            return self._fallback_code(question, data)
180	
181	        try:
182	            # Truncate data for prompt
183	            data_sample = data[:50] if len(data) > 50 else data
184	            data_json = json.dumps(data_sample, ensure_ascii=False, default=str)
185	
186	            prompt = CODE_GEN_PROMPT.format(
187	                question=question,
188	                data=data_json[:3000],  # Cap at 3K chars
189	            )
190	
191	            response = self.llm_call_fn(
192	                messages=[
193	                    {"role": "system", "content": "你是 Python 代码生成助手。"},
194	                    {"role": "user", "content": prompt},
195	                ],
196	                tools=[],
197	            )
198	
199	            if isinstance(response, str):
200	                code = response.strip()
201	            elif isinstance(response, dict):
202	                code = response.get("content", "").strip()
203	            else:
204	                code = str(response).strip()
205	
206	            # Extract code from markdown fences
207	            if "```python" in code:
208	                start = code.index("```python") + 10
209	                end = code.index("```", start) if "```" in code[start:] else len(code)
210	                code = code[start:end].strip()
211	            elif "```" in code:
212	                start = code.index("```") + 3
213	                end = code.index("```", start) if "```" in code[start:] else len(code)
214	                code = code[start:end].strip()
215	
216	            return code if code else None
217	
218	        except Exception as e:
219	            logger.warning(f"Code generation failed: {e}")
220	            return self._fallback_code(question, data)
221	
222	    def _fallback_code(
223	        self,
224	        question: str,
225	        data: List[Dict[str, Any]],
226	    ) -> Optional[str]:
227	        """Generate basic code without LLM (template-based)"""
228	        if not data:
229	            return None
230	
231	        # Basic: just return summary statistics
232	        cols = list(data[0].keys()) if data else []
233	        code = f"""# Auto-generated analysis (no LLM)
234	import json
235	from collections import Counter
236	
237	data = {json.dumps(data[:100], ensure_ascii=False, default=str)}
238	
239	# Basic statistics
240	row_count = len(data)
241	columns = {cols}
242	
243	# Value distribution for first column
244	if data:
245	    first_col = "{cols[0] if cols else ''}"
246	    values = [row.get(first_col) for row in data if row.get(first_col) is not None]
247	    dist = Counter(values)
248	    top = dist.most_common(5)
249	    result = f"共{{row_count}}行，{{first_col}}分布: " + ", ".join(f"{{k}}({{v}})" for k, v in top)
250	else:
251	    result = "无数据"
252	"""
253	        return code
254	
255	    def _check_safety(self, code: str) -> Dict[str, Any]:
256	        """Check code for forbidden patterns"""
257	        code_lower = code.lower()
258	
259	        for pattern in self.FORBIDDEN_PATTERNS:
260	            if pattern.lower() in code_lower:
261	                return {
262	                    'safe': False,
263	                    'reason': f'禁止使用: {pattern}',
264	                }
265	
266	        # Check imports
267	        for line in code.split('\n'):
268	            line = line.strip()
269	            if line.startswith('import ') or line.startswith('from '):
270	                module = line.replace('import ', '').replace('from ', '').split('.')[0].split(' ')[0]
271	                if module not in self.SAFE_IMPORTS:
272	                    return {
273	                        'safe': False,
274	                        'reason': f'不支持的库: {module}',
275	                    }
276	
277	        return {'safe': True, 'reason': ''}
278	
279	    def _execute_sandbox(
280	        self,
281	        code: str,
282	        data: List[Dict[str, Any]],
283	    ) -> Dict[str, Any]:
284	        """Execute code in a subprocess sandbox"""
285	        data_json = json.dumps(data, ensure_ascii=False, default=str)
286	
287	        # Build the script with no f-string escaping issues
288	        # Data is passed via stdin, code is embedded directly
289	        script_lines = [
290	            "import json, sys",
291	            "",
292	            "# Load data from stdin",
293	            "data = json.loads(sys.stdin.read())",
294	            "",
295	            "# User code",
296	            "try:",
297	        ]
298	        # Indent user code
299	        for line in code.split('\n'):
300	            script_lines.append("    " + line if line.strip() else "")
301	        script_lines.extend([
302	            "except Exception as e:",
303	            "    result = f'代码执行错误: {e}'",
304	            "",
305	            "# Output result",
306	            "if 'result' in dir():",
307	            "    print(json.dumps({'success': True, 'result': str(result)}))",
308	            "else:",
309	            "    print(json.dumps({'success': True, 'result': '代码执行完成（无result变量）'}))",
310	        ])
311	
312	        full_script = "\n".join(script_lines)
313	
314	        try:
315	            # Write to temp file and execute
316	            with tempfile.NamedTemporaryFile(
317	                mode='w', suffix='.py', delete=False, prefix='sandbox_'
318	            ) as f:
319	                f.write(full_script)
320	                script_path = f.name
321	
322	            result = subprocess.run(
323	                [sys.executable, script_path],
324	                input=data_json[:50000],
325	                capture_output=True,
326	                text=True,
327	                timeout=self.timeout,
328	            )
329	
330	            # Cleanup
331	            Path(script_path).unlink(missing_ok=True)
332	
333	            if result.returncode == 0:
334	                try:
335	                    output = json.loads(result.stdout.strip().split('\n')[-1])
336	                    return {
337	                        'success': output['success'],
338	                        'output': output['result'],
339	                    }
340	                except (json.JSONDecodeError, IndexError):
341	                    return {
342	                        'success': True,
343	                        'output': result.stdout[:500],
344	                    }
345	            else:
346	                return {
347	                    'success': False,
348	                    'output': result.stderr[:500],
349	                    'error': f'Exit code: {result.returncode}',
350	                }
351	
352	        except subprocess.TimeoutExpired:
353	            Path(script_path).unlink(missing_ok=True)
354	            return {
355	                'success': False,
356	                'output': f'代码执行超时 ({self.timeout}秒)',
357	                'error': 'timeout',
358	            }
359	        except Exception as e:
360	            Path(script_path).unlink(missing_ok=True)
361	            return {
362	                'success': False,
363	                'output': f'执行失败: {str(e)}',
364	                'error': str(e),
365	            }
366

### Q29

1	"""Unified LLM Client
2	
3	Supports ZhiPu GLM and DeepSeek via their OpenAI-compatible APIs.
4	Both providers support function calling, streaming, and system prompts.
5	
6	Provider endpoints:
7	- ZhiPu GLM: https://open.bigmodel.cn/api/paas/v4/chat/completions
8	- DeepSeek:  https://api.deepseek.com/v1/chat/completions
9	
10	Cost-effective defaults:
11	- ZhiPu: glm-4-flash (free tier, fast, good enough for SQL generation)
12	- DeepSeek: deepseek-chat (very cheap, strong code/SQL capability)
13	"""
14	
15	from __future__ import annotations
16	
17	import os
18	import json
19	import time
20	import logging
21	from typing import Dict, List, Optional, Callable, Any
22	from pathlib import Path
23	from dataclasses import dataclass, field
24	
25	import httpx
26	
27	logger = logging.getLogger(__name__)
28	
29	
30	# ============================================================================
31	# Config
32	# ============================================================================
33	
34	def load_env():
35	    """Load .env file into os.environ (lightweight, no python-dotenv dependency)"""
36	    env_path = Path(__file__).resolve().parents[2] / ".env"
37	    if not env_path.exists():
38	        return
39	    with open(env_path, "r", encoding="utf-8") as f:
40	        for line in f:
41	            line = line.strip()
42	            if not line or line.startswith("#"):
43	                continue
44	            if "=" not in line:
45	                continue
46	            key, _, value = line.partition("=")
47	            key = key.strip()
48	            value = value.strip().strip('"').strip("'")
49	            # Don't override existing env vars
50	            if key not in os.environ:
51	                os.environ[key] = value
52	
53	
54	# Load on import
55	load_env()
56	
57	
58	PROVIDER_CONFIG = {
59	    "zhipu": {
60	        "base_url": "https://open.bigmodel.cn/api/paas/v4",
61	        "default_model": "glm-4-flash",
62	        "api_key_env": "ZHIPU_API_KEY",
63	        "max_tokens": 4096,
64	        "temperature": 0.1,  # Low temperature for SQL generation
65	    },
66	    "deepseek": {
67	        "base_url": "https://api.deepseek.com/v1",
68	        "default_model": "deepseek-chat",
69	        "api_key_env": "DEEPSEEK_API_KEY",
70	        "max_tokens": 4096,
71	        "temperature": 0.1,
72	    },
73	}
74	
75	
76	@dataclass
77	class LLMMessage:
78	    """Unified message format"""
79	    role: str
80	    content: str
81	    tool_calls: Optional[List[Dict]] = None
82	    tool_call_id: Optional[str] = None
83	    name: Optional[str] = None
84	
85	    def to_dict(self) -> Dict:
86	        d = {"role": self.role, "content": self.content}
87	        if self.tool_calls:
88	            d["tool_calls"] = self.tool_calls
89	        if self.tool_call_id:
90	            d["tool_call_id"] = self.tool_call_id
91	        if self.name:
92	            d["name"] = self.name
93	        return d
94	
95	
96	@dataclass
97	class LLMResponse:
98	    """Unified LLM response"""
99	    content: str = ""
100	    tool_calls: List[Dict] = field(default_factory=list)
101	    raw: Optional[Dict] = None
102	    usage: Dict = field(default_factory=dict)
103	    latency_ms: float = 0.0
104	
105	    def to_agent_format(self) -> Dict:
106	        """Convert to format expected by ReActAgent._process_with_llm"""
107	        return {
108	            "content": self.content,
109	            "tool_calls": self.tool_calls if self.tool_calls else None,
110	        }
111	
112	
113	# ============================================================================
114	# LLM Client
115	# ============================================================================
116	
117	class LLMClient:
118	    """
119	    Unified LLM client.
120	
121	    Uses httpx for async-friendly HTTP calls.
122	    Supports function calling in OpenAI format.
123	
124	    Example:
125	        client = LLMClient(provider="zhipu")
126	
127	        # Chat with tools
128	        resp = client.chat(
129	            messages=[{"role": "user", "content": "IDCEVO有多少Critical缺陷?"}],
130	            tools=my_tool_schemas
131	        )
132	        if resp.tool_calls:
133	            for call in resp.tool_calls:
134	                print(call["name"], call["arguments"])
135	        else:
136	            print(resp.content)
137	    """
138	
139	    def __init__(
140	        self,
141	        provider: str = "zhipu",
142	        api_key: Optional[str] = None,
143	        model: Optional[str] = None,
144	        base_url: Optional[str] = None,
145	        timeout: float = 30.0,
146	    ):
147	        self.provider = provider
148	        config = PROVIDER_CONFIG.get(provider, PROVIDER_CONFIG["zhipu"])
149	
150	        self.api_key = api_key or os.environ.get(config["api_key_env"], "")
151	        self.model = model or os.environ.get(f"{provider.upper()}_MODEL", config["default_model"])
152	        self.base_url = base_url or config["base_url"]
153	        self.max_tokens = config["max_tokens"]
154	        self.temperature = config["temperature"]
155	        self.timeout = timeout
156	
157	        if not self.api_key:
158	            logger.warning(f"No API key for provider '{provider}'. LLM calls will fail.")
159	
160	        logger.info(f"LLMClient initialized: provider={provider}, model={self.model}")
161	
162	    # ==================== Core Chat ====================
163	
164	    def chat(
165	        self,
166	        messages: List[Dict[str, Any]],
167	        tools: Optional[List[Dict]] = None,
168	        temperature: Optional[float] = None,
169	        max_tokens: Optional[int] = None,
170	        stop: Optional[List[str]] = None,
171	    ) -> LLMResponse:
172	        """
173	        Chat completion with optional function calling.
174	
175	        Args:
176	            messages: OpenAI-format messages
177	            tools: OpenAI-format tool definitions [{"type": "function", "function": {...}}]
178	            temperature: Override default temperature
179	            max_tokens: Override default max_tokens
180	            stop: Stop sequences
181	
182	        Returns:
183	            LLMResponse with content and/or tool_calls
184	        """
185	        headers = {
186	            "Authorization": f"Bearer {self.api_key}",
187	            "Content-Type": "application/json",
188	        }
189	
190	        payload: Dict[str, Any] = {
191	            "model": self.model,
192	            "messages": messages,
193	            "temperature": temperature if temperature is not None else self.temperature,
194	            "max_tokens": max_tokens or self.max_tokens,
195	        }
196	
197	        if tools:
198	            payload["tools"] = tools
199	            payload["tool_choice"] = "auto"
200	
201	        if stop:
202	            payload["stop"] = stop
203	
204	        url = f"{self.base_url}/chat/completions"
205	        t0 = time.time()
206	
207	        try:
208	            with httpx.Client(timeout=self.timeout) as http_client:
209	                resp = http_client.post(url, json=payload, headers=headers)
210	                resp.raise_for_status()
211	                data = resp.json()
212	
213	            latency = (time.time() - t0) * 1000
214	
215	            # Parse response (OpenAI format, both providers compatible)
216	            choice = data.get("choices", [{}])[0]
217	            message = choice.get("message", {})
218	
219	            content = message.get("content", "") or ""
220	            raw_tool_calls = message.get("tool_calls", [])
221	
222	            # Normalize tool_calls to our format
223	            tool_calls = []
224	            for tc in raw_tool_calls:
225	                fn = tc.get("function", {})
226	                args_str = fn.get("arguments", "{}")
227	                try:
228	                    args = json.loads(args_str) if isinstance(args_str, str) else args_str
229	                except json.JSONDecodeError:
230	                    args = {"_raw": args_str}
231	
232	                tool_calls.append({
233	                    "id": tc.get("id", ""),
234	                    "name": fn.get("name", ""),
235	                    "arguments": args,
236	                    "thought": content,  # LLM reasoning before the call
237	                })
238	
239	            usage = data.get("usage", {})
240	
241	            logger.debug(
242	                f"LLM chat: {latency:.0f}ms, "
243	                f"tokens={usage.get('total_tokens', '?')}, "
244	                f"tool_calls={len(tool_calls)}"
245	            )
246	
247	            return LLMResponse(
248	                content=content,
249	                tool_calls=tool_calls,
250	                raw=data,
251	                usage=usage,
252	                latency_ms=latency,
253	            )
254	
255	        except httpx.HTTPStatusError as e:
256	            logger.error(f"LLM API error {e.response.status_code}: {e.response.text[:500]}")
257	            return LLMResponse(content=f"[LLM Error: {e.response.status_code}]")
258	        except Exception as e:
259	            logger.error(f"LLM call failed: {e}")
260	            return LLMResponse(content=f"[LLM Error: {str(e)}]")
261	
262	    def chat_text(
263	        self,
264	        prompt: str,
265	        system: str = "",
266	        temperature: float = 0.1,
267	    ) -> str:
268	        """
269	        Simple text completion. Returns just the text.
270	
271	        Used by QueryFixer and other components that just need text in/out.
272	
273	        Args:
274	            prompt: User prompt
275	            system: Optional system prompt
276	            temperature: Sampling temperature
277	
278	        Returns:
279	            LLM response text
280	        """
281	        messages = []
282	        if system:
283	            messages.append({"role": "system", "content": system})
284	        messages.append({"role": "user", "content": prompt})
285	
286	        resp = self.chat(messages, temperature=temperature, tools=None)
287	        return resp.content
288	
289	    # ==================== Adapters ====================
290	
291	    def as_agent_fn(self) -> Callable:
292	        """
293	        Return a callable compatible with ReActAgent.llm_call_fn.
294	
295	        Signature: fn(messages: List[Dict], tools: List[Dict]) -> Dict
296	        Returns: {"content": str, "tool_calls": [{"name", "arguments", "thought"}] | None}
297	        """
298	        def agent_fn(messages: List[Dict], tools: List[Dict]) -> Dict:
299	            # Convert tool schemas to OpenAI format if needed
300	            openai_tools = []
301	            for t in tools:
302	                if t.get("type") == "function":
303	                    openai_tools.append(t)
304	                else:
305	                    # Our schema format: {"name": ..., "description": ..., "parameters": {...}}
306	                    openai_tools.append({
307	                        "type": "function",
308	                        "function": {
309	                            "name": t.get("name", ""),
310	                            "description": t.get("description", ""),
311	                            "parameters": t.get("parameters", {"type": "object", "properties": {}}),
312	                        }
313	                    })
314	
315	            resp = self.chat(messages=messages, tools=openai_tools if openai_tools else None)
316	            return resp.to_agent_format()
317	
318	        return agent_fn
319	
320	    def as_fixer_fn(self) -> Callable:
321	        """
322	        Return a callable compatible with QueryFixer.llm_call_fn.
323	
324	        Signature: fn(prompt: str) -> str
325	        """
326	        def fixer_fn(prompt: str) -> str:
327	            return self.chat_text(prompt, temperature=0.0)
328	
329	        return fixer_fn
330	
331	    def as_generator_fn(self) -> Callable:
332	        """
333	        Return a callable for NL2SQLEngine.llm_call_fn.
334	
335	        Used for LLM-enhanced SQL generation.
336	        Signature: fn(prompt: str) -> str
337	        """
338	        return self.as_fixer_fn()
339	
340	    # ==================== Health ====================
341	
342	    def health_check(self) -> bool:
343	        """Quick health check - send a tiny prompt"""
344	        try:
345	            resp = self.chat(
346	                messages=[{"role": "user", "content": "ping"}],
347	                max_tokens=5,
348	                temperature=0.0,
349	            )
350	            return bool(resp.content)
351	        except Exception:
352	            return False
353	
354	
355	# ============================================================================
356	# Singleton
357	# ============================================================================
358	
359	_client: Optional[LLMClient] = None
360	
361	
362	def get_llm_client(
363	    provider: Optional[str] = None,
364	    **kwargs,
365	) -> Optional[LLMClient]:
366	    """
367	    Get or create the singleton LLM client.
368	
369	    Provider is determined by:
370	    1. Explicit argument
371	    2. AGENT_LLM_PROVIDER env var
372	    3. Default: "zhipu"
373	
374	    Returns None if provider is "none" or no API key available.
375	    """
376	    global _client
377	    if _client is not None:
378	        return _client
379	
380	    provider = provider or os.environ.get("AGENT_LLM_PROVIDER", "zhipu")
381	
382	    if provider == "none":
383	        logger.info("LLM disabled (AGENT_LLM_PROVIDER=none)")
384	        return None
385	
386	    try:
387	        _client = LLMClient(provider=provider, **kwargs)
388	        if not _client.api_key:
389	            logger.warning(f"No API key for provider '{provider}', LLM disabled")
390	            return None
391	        logger.info(f"LLM client ready: {_client.provider}/{_client.model}")
392	    except Exception as e:
393	        logger.error(f"Failed to init LLM client: {e}")
394	        return None
395	
396	    return _client
397

### Q30

1	"""
2	DataStoryteller — 数据故事化引擎
3	
4	把冰冷的数字变成有业务含义的故事。
5	
6	核心能力:
7	1. 数字解读 — "42 个 Critical" → "42 个安全相关缺陷，需要立即处理"
8	2. 趋势分析 — 数据走势 → 上升/下降/平稳 + 可能原因
9	3. 对比洞察 — 分布数据 → TOP1 vs 平均水平 / 集中度分析
10	4. 行动建议 — 基于数据特征给出推荐行动
11	
12	设计原则:
13	- 数据驱动，不做无依据推测
14	- 中文表达，符合汽车测试行业用语
15	- 简洁有力，不啰嗦
16	- 带数字引用，方便验证
17	"""
18	
19	from __future__ import annotations
20	
21	from dataclasses import dataclass
22	from typing import Optional, List, Dict, Any, Tuple
23	from enum import Enum
24	
25	
26	class StoryType(str, Enum):
27	    COUNT = "count"           # 计数结果解读
28	    TREND = "trend"           # 趋势解读
29	    DISTRIBUTION = "distribution"  # 分布解读
30	    RANKING = "ranking"       # 排名解读
31	    COMPARISON = "comparison"  # 对比解读
32	    SUMMARY = "summary"       # 汇总解读
33	
34	
35	@dataclass
36	class StoryResult:
37	    """数据故事结果"""
38	    headline: str = ""        # 核心结论（一句话）
39	    body: str = ""            # 详细解读
40	    insights: List[str] = None  # 关键洞察列表
41	    recommendation: str = ""  # 行动建议
42	    story_type: str = ""
43	
44	    def __post_init__(self):
45	        if self.insights is None:
46	            self.insights = []
47	
48	    def to_dict(self) -> dict:
49	        return {
50	            "headline": self.headline,
51	            "body": self.body,
52	            "insights": self.insights,
53	            "recommendation": self.recommendation,
54	            "story_type": self.story_type,
55	        }
56	
57	    def to_markdown(self) -> str:
58	        """渲染为 Markdown 格式"""
59	        parts = [f"### {self.headline}"]
60	        
61	        if self.body:
62	            parts.append(self.body)
63	        
64	        if self.insights:
65	            parts.append("**关键洞察：**")
66	            for i, insight in enumerate(self.insights, 1):
67	                parts.append(f"{i}. {insight}")
68	        
69	        if self.recommendation:
70	            parts.append(f"💡 **建议：** {self.recommendation}")
71	        
72	        return "\n\n".join(parts)
73	
74	
75	class DataStoryteller:
76	    """
77	    数据故事化引擎
78	    
79	    输入: 查询结果数据（行/列/统计量）
80	    输出: 有业务含义的故事化文本
81	    """
82	
83	    # 严重度业务含义
84	    SEVERITY_MEANING = {
85	        "Critical": "安全相关/法规不满足，需要立即处理",
86	        "Major": "功能降级，影响用户使用",
87	        "Minor": "外观/体验问题，不影响核心功能",
88	    }
89	
90	    # 状态业务含义
91	    STATUS_MEANING = {
92	        "New": "新建未分配",
93	        "Open": "已分配待处理",
94	        "In Progress": "正在修复中",
95	        "Fixed": "已修复待验证",
96	        "Closed": "已验证关闭",
97	        "Rejected": "已拒绝（非缺陷）",
98	        "Deferred": "延后处理",
99	    }
100	
101	    # 活跃状态
102	    ACTIVE_STATUSES = {"New", "Open", "In Progress"}
103	    RESOLVED_STATUSES = {"Fixed", "Closed"}
104	
105	    def tell_count(
106	        self,
107	        count: int,
108	        question: str = "",
109	        context: Optional[Dict[str, Any]] = None,
110	    ) -> StoryResult:
111	        """
112	        解读计数查询结果
113	        
114	        Args:
115	            count: 缺陷数量
116	            question: 原始问题
117	            context: 额外上下文（severity, project, ecu 等）
118	        """
119	        ctx = context or {}
120	        severity = ctx.get("severity", "")
121	        project = ctx.get("project", "")
122	        ecu = ctx.get("ecu", "")
123	        time_range = ctx.get("time_range", "")
124	        
125	        # 构建标题
126	        conditions = []
127	        if project:
128	            conditions.append(project)
129	        if severity:
130	            conditions.append(severity)
131	        if ecu:
132	            conditions.append(f"{ecu}相关")
133	        if time_range:
134	            conditions.append(time_range)
135	        
136	        prefix = "、".join(conditions) if conditions else "查询范围内"
137	        
138	        # 严重度解读
139	        severity_note = ""
140	        if severity and severity in self.SEVERITY_MEANING:
141	            severity_note = f"（{self.SEVERITY_MEANING[severity]}）"
142	        
143	        headline = f"{prefix}共有 **{count}** 个缺陷{severity_note}"
144	        
145	        # 正文
146	        body_parts = []
147	        body_parts.append(f"根据查询条件，符合条件的缺陷共 {count} 个。")
148	        
149	        insights = []
150	        
151	        # 数量级别解读
152	        if count == 0:
153	            insights.append("✅ 零缺陷 — 当前条件范围内表现良好")
154	        elif count <= 5:
155	            insights.append(f"数量较少（{count}个），处于可控范围")
156	        elif count <= 20:
157	            insights.append(f"数量中等（{count}个），建议关注")
158	        elif count <= 50:
159	            insights.append(f"数量偏多（{count}个），建议优先处理")
160	        else:
161	            insights.append(f"⚠️ 数量较多（{count}个），需要重点关注")
162	        
163	        # 行动建议
164	        recommendation = ""
165	        if severity == "Critical" and count > 0:
166	            recommendation = f"Critical 缺陷需立即分配责任人，建议 24h 内响应"
167	        elif count > 20:
168	            recommendation = "建议按优先级排序，集中处理 TOP 问题"
169	        elif count == 0:
170	            recommendation = "继续保持，定期复查"
171	        
172	        return StoryResult(
173	            headline=headline,
174	            body=" ".join(body_parts),
175	            insights=insights,
176	            recommendation=recommendation,
177	            story_type=StoryType.COUNT.value,
178	        )
179	
180	    def tell_trend(
181	        self,
182	        data: List[Dict[str, Any]],
183	        time_field: str = "period",
184	        value_field: str = "count",
185	        question: str = "",
186	    ) -> StoryResult:
187	        """
188	        解读趋势查询结果
189	        
190	        Args:
191	            data: 时间序列数据 [{period: "2026-01", count: 30}, ...]
192	        """
193	        if not data:
194	            return StoryResult(
195	                headline="暂无趋势数据",
196	                story_type=StoryType.TREND.value,
197	            )
198	        
199	        values = [row.get(value_field, 0) for row in data]
200	        periods = [row.get(time_field, "") for row in data]
201	        
202	        total = sum(values)
203	        avg = total / len(values) if values else 0
204	        latest = values[-1] if values else 0
205	        first = values[0] if values else 0
206	        
207	        # 趋势方向
208	        if len(values) >= 2:
209	            change_pct = ((latest - first) / first * 100) if first > 0 else 0
210	            if latest > first * 1.15:
211	                direction = "上升"
212	                arrow = "📈"
213	            elif latest < first * 0.85:
214	                direction = "下降"
215	                arrow = "📉"
216	            else:
217	                direction = "平稳"
218	                arrow = "➡️"
219	        else:
220	            change_pct = 0
221	            direction = "数据不足"
222	            arrow = ""
223	        
224	        headline = f"趋势分析：{arrow} {direction}趋势，共 {total} 个缺陷，月均 {avg:.1f} 个"
225	        
226	        insights = []
227	        
228	        # 趋势解读
229	        if direction == "上升":
230	            insights.append(f"⚠️ 缺陷数量呈上升趋势（{periods[0]}: {first} → {periods[-1]}: {latest}，增幅 {change_pct:+.1f}%）")
231	        elif direction == "下降":
232	            insights.append(f"✅ 缺陷数量呈下降趋势（{periods[0]}: {first} → {periods[-1]}: {latest}，降幅 {change_pct:+.1f}%）")
233	        else:
234	            insights.append(f"缺陷数量保持平稳，月均 {avg:.1f} 个")
235	        
236	        # 峰值
237	        if len(values) > 1:
238	            max_val = max(values)
239	            max_idx = values.index(max_val)
240	            min_val = min(values)
241	            min_idx = values.index(min_val)
242	            
243	            if max_val != min_val:
244	                insights.append(f"峰值出现在 {periods[max_idx]}（{max_val}个），低谷在 {periods[min_idx]}（{min_val}个）")
245	        
246	        # 波动
247	        if len(values) >= 3:
248	            import statistics
249	            stdev = statistics.stdev(values)
250	            cv = stdev / avg if avg > 0 else 0
251	            if cv > 0.5:
252	                insights.append(f"波动较大（标准差 {stdev:.1f}），建议分析异常月份的原因")
253	        
254	        recommendation = ""
255	        if direction == "上升" and latest > avg:
256	            recommendation = "趋势恶化，建议排查最近变更（新功能/新版本），加强测试覆盖"
257	        elif direction == "下降":
258	            recommendation = "趋势改善，总结当前做法经验，继续保持"
259	        elif avg > 30:
260	            recommendation = "月均数量偏高，建议从TOP问题入手进行根因分析"
261	        
262	        return StoryResult(
263	            headline=headline,
264	            insights=insights,
265	            recommendation=recommendation,
266	            story_type=StoryType.TREND.value,
267	        )
268	
269	    def tell_distribution(
270	        self,
271	        data: List[Dict[str, Any]],
272	        label_field: str = "label",
273	        value_field: str = "count",
274	        dimension: str = "",
275	        question: str = "",
276	    ) -> StoryResult:
277	        """
278	        解读分布查询结果
279	        
280	        Args:
281	            data: 分布数据 [{label: "Critical", count: 30}, ...]
282	            dimension: 分布维度名（severity/project/ecu 等）
283	        """
284	        if not data:
285	            return StoryResult(
286	                headline=f"按{dimension}分布分析：暂无数据",
287	                story_type=StoryType.DISTRIBUTION.value,
288	            )
289	        
290	        total = sum(row.get(value_field, 0) for row in data)
291	        sorted_data = sorted(data, key=lambda x: x.get(value_field, 0), reverse=True)
292	        
293	        top = sorted_data[0]
294	        top_label = top.get(label_field, "")
295	        top_count = top.get(value_field, 0)
296	        top_pct = top_count / total * 100 if total > 0 else 0
297	        
298	        headline = f"按{dimension}分布：共 {len(data)} 个分组，{top_label} 占比最高（{top_count}/{total}，{top_pct:.1f}%）"
299	        
300	        insights = []
301	        
302	        # TOP 3
303	        top3 = sorted_data[:3]
304	        top3_count = sum(r.get(value_field, 0) for r in top3)
305	        top3_pct = top3_count / total * 100 if total > 0 else 0
306	        insights.append(f"TOP3 占 {top3_pct:.1f}%（{top3_count}/{total}）")
307	        
308	        # 集中度
309	        if top_pct > 50:
310	            insights.append(f"📊 高度集中：{top_label} 超过总量一半（{top_pct:.1f}%），建议优先关注")
311	        elif top_pct < 25 and len(data) > 3:
312	            insights.append(f"📊 较为分散：最大分组仅 {top_pct:.1f}%，问题分布均匀")
313	        
314	        # 零值检测
315	        zero_groups = [r for r in data if r.get(value_field, 0) == 0]
316	        if zero_groups:
317	            zero_labels = [r.get(label_field, "") for r in zero_groups]
318	            insights.append(f"零缺陷分组：{', '.join(zero_labels)}")
319	        
320	        # 严重度特殊解读
321	        if dimension.lower() == "severity":
322	            critical = next((r for r in data if r.get(label_field) == "Critical"), None)
323	            if critical and critical.get(value_field, 0) > 0:
324	                insights.append(f"🔴 Critical {critical[value_field]}个 — 安全/法规风险，需立即处理")
325	        
326	        recommendation = ""
327	        if top_pct > 50:
328	            recommendation = f"集中解决 {top_label} 的问题可以大幅降低总量"
329	        elif len(data) > 5:
330	            recommendation = "问题分散在多个维度，建议按模块逐一排查"
331	        
332	        body = "分布明细：\n"
333	        for r in top3:
334	            label = r.get(label_field, "")
335	            count = r.get(value_field, 0)
336	            pct = count / total * 100 if total > 0 else 0
337	            body += f"  - {label}: {count} ({pct:.1f}%)\n"
338	        
339	        return StoryResult(
340	            headline=headline,
341	            body=body,
342	            insights=insights,
343	            recommendation=recommendation,
344	            story_type=StoryType.DISTRIBUTION.value,
345	        )
346	
347	    def tell_ranking(
348	        self,
349	        data: List[Dict[str, Any]],
350	        label_field: str = "label",
351	        value_field: str = "count",
352	        rank_by: str = "",
353	        question: str = "",
354	    ) -> StoryResult:
355	        """
356	        解读排名查询结果
357	        """
358	        if not data:
359	            return StoryResult(
360	                headline=f"按{rank_by}排名：暂无数据",
361	                story_type=StoryType.RANKING.value,
362	            )
363	        
364	        total = sum(row.get(value_field, 0) for row in data)
365	        top = data[0]
366	        top_label = top.get(label_field, "")
367	        top_count = top.get(value_field, 0)
368	        
369	        headline = f"TOP {len(data)} 排名：第一是 {top_label}（{top_count}个）"
370	        
371	        insights = []
372	        
373	        # TOP vs 平均
374	        avg = total / len(data) if data else 0
375	        if top_count > avg * 2:
376	            insights.append(f"🔴 {top_label} 远超平均水平（{top_count} vs 均值 {avg:.1f}），是突出热点")
377	        
378	        # 差距分析
379	        if len(data) >= 2:
380	            second = data[1]
381	            gap = top_count - second.get(value_field, 0)
382	            if gap > top_count * 0.3:
383	                insights.append(f"第一名与第二名差距明显（{gap}个），问题高度集中在 {top_label}")
384	        
385	        # 逐条列出
386	        body = "排名明细：\n"
387	        for i, r in enumerate(data, 1):
388	            label = r.get(label_field, "")
389	            count = r.get(value_field, 0)
390	            pct = count / total * 100 if total > 0 else 0
391	            body += f"  {i}. {label}: {count} ({pct:.1f}%)\n"
392	        
393	        recommendation = f"建议优先处理 {top_label} 的问题"
394	        
395	        return StoryResult(
396	            headline=headline,
397	            body=body,
398	            insights=insights,
399	            recommendation=recommendation,
400	            story_type=StoryType.RANKING.value,
401	        )
402	
403	    def tell_summary(
404	        self,
405	        stats: Dict[str, Any],
406	        question: str = "",
407	    ) -> StoryResult:
408	        """
409	        解读仪表盘汇总数据
410	        
411	        Args:
412	            stats: {total, active, critical, resolved, ...}
413	        """
414	        total = stats.get("total", 0)
415	        active = stats.get("active", 0)
416	        critical = stats.get("critical", 0)
417	        resolved = stats.get("resolved", 0)
418	        
419	        resolve_rate = resolved / total * 100 if total > 0 else 0
420	        active_rate = active / total * 100 if total > 0 else 0
421	        critical_rate = critical / total * 100 if total > 0 else 0
422	        
423	        headline = f"仪表盘：共 {total} 个缺陷，活跃 {active}（{active_rate:.1f}%），Critical {critical}，已解决 {resolved}（{resolve_rate:.1f}%）"
424	        
425	        insights = []
426	        
427	        if critical > 0:
428	            insights.append(f"🔴 {critical} 个未关闭 Critical 缺陷需立即关注")
429	        
430	        if resolve_rate >= 80:
431	            insights.append(f"✅ 解决率 {resolve_rate:.1f}%，整体进展良好")
432	        elif resolve_rate >= 50:
433	            insights.append(f"⏳ 解决率 {resolve_rate:.1f}%，仍有较多待处理")
434	        else:
435	            insights.append(f"⚠️ 解决率仅 {resolve_rate:.1f}%，积压较多")
436	        
437	        if active_rate > 50:
438	            insights.append(f"活跃缺陷占比 {active_rate:.1f}%，处理速度可能跟不上新增速度")
439	        
440	        recommendation = ""
441	        if critical > 0:
442	            recommendation = "优先关闭 Critical 缺陷，建议 24h 内分配责任人"
443	        elif active_rate > 60:
444	            recommendation = "增加人力投入或调整优先级，减少积压"
445	        elif resolve_rate >= 80:
446	            recommendation = "保持当前节奏，持续监控新增缺陷趋势"
447	        
448	        return StoryResult(
449	            headline=headline,
450	            insights=insights,
451	            recommendation=recommendation,
452	            story_type=StoryType.SUMMARY.value,
453	        )
454	
455	    def tell(
456	        self,
457	        story_type: str,
458	        data: Any,
459	        **kwargs,
460	    ) -> StoryResult:
461	        """
462	        统一入口，根据类型分发到对应方法
463	        """
464	        if story_type == StoryType.COUNT.value:
465	            return self.tell_count(data, **kwargs)
466	        elif story_type == StoryType.TREND.value:
467	            return self.tell_trend(data, **kwargs)
468	        elif story_type == StoryType.DISTRIBUTION.value:
469	            return self.tell_distribution(data, **kwargs)
470	        elif story_type == StoryType.RANKING.value:
471	            return self.tell_ranking(data, **kwargs)
472	        elif story_type == StoryType.SUMMARY.value:
473	            return self.tell_summary(data, **kwargs)
474	        else:
475	            return StoryResult(
476	                headline=str(data),
477	                story_type="unknown",
478	            )
479

### Q31

1	"""Context Engine - 5-Layer Context Building
2	
3	Inspired by WrenAI's context layer model:
4	
5	Layer 1 - Structural: Tables, columns, types, keys, relationships
6	Layer 2 - Semantic: Business names, descriptions, calculations, enums
7	Layer 3 - Business: Canonical tables, reusable metrics, relationship meaning
8	Layer 4 - Operational: Safe join paths, forbidden operations
9	Layer 5 - Behavioral: Historical successful queries, user feedback, frequent patterns
10	"""
11	
12	from typing import Optional, Dict, List
13	from pathlib import Path
14	from datetime import datetime
15	import sqlite3
16	
17	from agent.ontology import OntologyEngine, get_ontology_engine
18	
19	
20	class DataProfiler:
21	    """
22	    Automatic data profiling for Layer 1 context
23	
24	    Analyzes database to provide:
25	    - Row counts
26	    - Column distributions
27	    - Value frequencies
28	    - Data quality warnings
29	    """
30	
31	    def __init__(self, db_path: str):
32	        self.db_path = db_path
33	        self._cache: Dict[str, Dict] = {}
34	
35	    def profile_table(self, table_name: str) -> Dict:
36	        """Profile a single table"""
37	        if table_name in self._cache:
38	            return self._cache[table_name]
39	
40	        conn = sqlite3.connect(self.db_path)
41	        cursor = conn.cursor()
42	
43	        profile = {
44	            "row_count": 0,
45	            "columns": {},
46	            "created_at": datetime.now().isoformat()
47	        }
48	
49	        # Row count
50	        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
51	        profile["row_count"] = cursor.fetchone()[0]
52	
53	        # Column profiles
54	        cursor.execute(f"PRAGMA table_info({table_name})")
55	        columns_info = cursor.fetchall()
56	
57	        for col_info in columns_info:
58	            col_name = col_info[1]
59	            col_type = col_info[2]
60	
61	            col_profile = {
62	                "type": col_type,
63	                "nullable": col_info[3] == 0,  # 0 = NOT NULL
64	                "sample_values": [],
65	                "unique_count": 0,
66	                "null_count": 0
67	            }
68	
69	            # Sample values and statistics
70	            try:
71	                cursor.execute(f"SELECT DISTINCT {col_name} FROM {table_name} WHERE {col_name} IS NOT NULL LIMIT 5")
72	                sample_values = cursor.fetchall()
73	                col_profile["sample_values"] = [v[0] for v in sample_values if v[0] is not None]
74	
75	                # Unique count (for reasonable sized tables)
76	                if profile["row_count"] < 100000:
77	                    cursor.execute(f"SELECT COUNT(DISTINCT {col_name}) FROM {table_name}")
78	                    col_profile["unique_count"] = cursor.fetchone()[0]
79	
80	                # Null count
81	                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL")
82	                col_profile["null_count"] = cursor.fetchone()[0]
83	
84	                # Null percentage
85	                if profile["row_count"] > 0:
86	                    col_profile["null_percentage"] = (col_profile["null_count"] / profile["row_count"]) * 100
87	
88	            except sqlite3.OperationalError:
89	                # Column might not support these operations (e.g., BLOB)
90	                pass
91	
92	            profile["columns"][col_name] = col_profile
93	
94	        conn.close()
95	        self._cache[table_name] = profile
96	        return profile
97	
98	    def profile_all_tables(self) -> Dict[str, Dict]:
99	        """Profile all tables in the database"""
100	        conn = sqlite3.connect(self.db_path)
101	        cursor = conn.cursor()
102	
103	        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
104	        tables = [row[0] for row in cursor.fetchall()]
105	        conn.close()
106	
107	        profiles = {}
108	        for table in tables:
109	            if not table.startswith("sqlite_"):  # Skip SQLite system tables
110	                profiles[table] = self.profile_table(table)
111	
112	        return profiles
113	
114	    def get_summary_text(self) -> str:
115	        """Get a human-readable summary of database profile"""
116	        profiles = self.profile_all_tables()
117	
118	        lines = ["## 数据库概览\n"]
119	
120	        total_rows = sum(p["row_count"] for p in profiles.values())
121	        lines.append(f"**总表数**: {len(profiles)}")
122	        lines.append(f"**总行数**: {total_rows:,}\n")
123	
124	        for table_name, profile in sorted(profiles.items()):
125	            lines.append(f"### {table_name}")
126	            lines.append(f"- 行数: {profile['row_count']:,}")
127	            lines.append(f"- 列数: {len(profile['columns'])}")
128	
129	            # Highlight interesting columns
130	            interesting_cols = []
131	            for col_name, col_profile in profile["columns"].items():
132	                if col_profile["null_percentage"] and col_profile["null_percentage"] > 20:
133	                    interesting_cols.append(f"{col_name} (缺失率高 {col_profile['null_percentage']:.1f}%)")
134	
135	                if col_profile["unique_count"] == profile["row_count"] and profile["row_count"] > 0:
136	                    interesting_cols.append(f"{col_name} (唯一)")
137	
138	            if interesting_cols:
139	                lines.append(f"- 注意: {', '.join(interesting_cols)}")
140	
141	            lines.append("")
142	
143	        return "\n".join(lines)
144	
145	
146	class ContextEngine:
147	    """
148	    Context Engine - 5-Layer context builder for LLM prompts
149	
150	    Combines structural, semantic, business, operational, and behavioral context
151	    """
152	
153	    def __init__(
154	        self,
155	        ontology: Optional[OntologyEngine] = None,
156	        db_path: Optional[str] = None
157	    ):
158	        self.ontology = ontology or get_ontology_engine()
159	        self.profiler: Optional[DataProfiler] = None
160	
161	        if db_path:
162	            self.profiler = DataProfiler(db_path)
163	
164	        # Behavioral layer - query history and feedback
165	        self.query_history: List[Dict] = []
166	
167	    def structural_layer(self, object_type: str) -> str:
168	        """
169	        Layer 1: Structural Context
170	        Table schema, columns, types, primary keys, foreign keys
171	        """
172	        obj = self.ontology.get_object(object_type)
173	        if not obj:
174	            return f"## 未找到对象类型: {object_type}\n"
175	
176	        lines = [f"## 结构层 - {object_type}\n"]
177	        lines.append(f"**数据表**: {obj.source_table}\n")
178	        lines.append(f"**主键**: {obj.primary_key}\n")
179	
180	        if obj.properties:
181	            lines.append("### 字段结构\n")
182	            for prop_name, prop in obj.properties.items():
183	                type_str = prop.type.value
184	                if prop.item_type:
185	                    type_str = f"{prop.item_type.value}[]"
186	
187	                line = f"- **{prop_name}**: {type_str}"
188	                if prop.foreign_key:
189	                    line += f" → {prop.foreign_key}"
190	                lines.append(line)
191	
192	        return "\n".join(lines)
193	
194	    def semantic_layer(self, object_type: str, keywords: List[str] = None) -> str:
195	        """
196	        Layer 2: Semantic Context
197	        Business meanings, enum values, category groups, aliases
198	        """
199	        obj = self.ontology.get_object(object_type)
200	        if not obj:
201	            return ""
202	
203	        lines = [f"\n## 语义层 - {object_type}\n"]
204	
205	        if obj.properties:
206	            for prop_name, prop in obj.properties.items():
207	                if not prop.meaning and not prop.values and not prop.aliases:
208	                    continue
209	
210	                lines.append(f"### {prop_name}\n")
211	
212	                if prop.meaning:
213	                    lines.append(f"**含义**: {prop.meaning}\n")
214	
215	                if prop.values:
216	                    lines.append(f"**取值**: {', '.join(prop.values)}\n")
217	
218	                if prop.aliases:
219	                    lines.append("**别名**:\n")
220	                    for canonical, aliases in prop.aliases.items():
221	                        lines.append(f"- {canonical}: {', '.join(aliases)}\n")
222	
223	                if prop.category_groups:
224	                    lines.append("**分类**:\n")
225	                    for category, values in prop.category_groups.items():
226	                        lines.append(f"- {category}: {', '.join(values)}\n")
227	
228	                if prop.semantics:
229	                    lines.append("**语义说明**:\n")
230	                    for value, meaning in prop.semantics.items():
231	                        lines.append(f"- {value}: {meaning}\n")
232	
233	        return "\n".join(lines)
234	
235	    def business_layer(self, object_type: str, question: str = None) -> str:
236	        """
237	        Layer 3: Business Context
238	        Metrics, business rules, canonical definitions
239	        """
240	        obj = self.ontology.get_object(object_type)
241	        if not obj:
242	            return ""
243	
244	        lines = [f"\n## 业务层 - {object_type}\n"]
245	
246	        # Metrics
247	        if obj.metrics:
248	            lines.append("### 计算指标\n")
249	            for metric_name, metric in obj.metrics.items():
250	                lines.append(f"- **{metric_name}**: {metric.meaning}")
251	                lines.append(f"  - 计算: {metric.definition}\n")
252	
253	        # Calibration rules
254	        relevant_rules = []
255	        if question:
256	            keywords = question.lower().split()
257	            relevant_rules = self.ontology.find_relevant_rules(keywords)
258	
259	        if relevant_rules:
260	            lines.append("### 业务规则提醒\n")
261	            lines.append("根据你的问题，请注意以下业务规则:\n")
262	            for rule in relevant_rules[:5]:  # Top 5 most relevant
263	                lines.append(f"- {rule.rule}\n")
264	
265	        return "\n".join(lines)
266	
267	    def operational_layer(self, object_type: str) -> str:
268	        """
269	        Layer 4: Operational Context
270	        Safe join paths, forbidden operations, governance
271	        """
272	        obj = self.ontology.get_object(object_type)
273	        if not obj:
274	            return ""
275	
276	        lines = [f"\n## 操作层 - {object_type}\n"]
277	
278	        # Governance
279	        if obj.governance:
280	            if obj.governance.forbid_operations:
281	                lines.append("**禁止的操作**:\n")
282	                lines.append(f"{'、'.join(obj.governance.forbid_operations)}\n")
283	
284	            if obj.governance.default_time_range:
285	                lines.append(f"**默认时间范围**: {obj.governance.default_time_range}\n")
286	
287	        # Join paths
288	        if obj.links:
289	            lines.append("### 安全的 JOIN 路径\n")
290	            for link in obj.links:
291	                lines.append(f"- **{link.name}** → {link.target}")
292	                lines.append(f"  - 关联: {link.join}\n")
293	
294	        return "\n".join(lines)
295	
296	    def behavioral_layer(self, object_type: str, question: str = None) -> str:
297	        """
298	        Layer 5: Behavioral Context
299	        Historical queries, user feedback, frequent patterns
300	        """
301	        lines = [f"\n## 行为层 - {object_type}\n"]
302	
303	        # Similar successful queries from history
304	        if question and self.query_history:
305	            similar_queries = self._find_similar_queries(question, object_type)
306	            if similar_queries:
307	                lines.append("### 历史成功查询参考\n")
308	                for i, q in enumerate(similar_queries[:3], 1):
309	                    lines.append(f"{i}. **问题**: {q['question']}")
310	                    lines.append(f"   **SQL**: ```sql\n{q['sql']}\n```\n")
311	
312	        return "\n".join(lines)
313	
314	    def build_context(
315	        self,
316	        object_type: str,
317	        question: Optional[str] = None,
318	        include_layers: Optional[List[int]] = None
319	    ) -> str:
320	        """
321	        Build complete 5-layer context
322	
323	        Args:
324	            object_type: The object type to get context for
325	            question: The user's question (for relevance scoring)
326	            include_layers: Which layers to include (default: all)
327	
328	        Returns:
329	            Complete context string for LLM prompt
330	        """
331	        if include_layers is None:
332	            include_layers = [1, 2, 3, 4, 5]
333	
334	        context_parts = []
335	
336	        if 1 in include_layers:
337	            context_parts.append(self.structural_layer(object_type))
338	
339	        if 2 in include_layers:
340	            context_parts.append(self.semantic_layer(object_type))
341	
342	        if 3 in include_layers:
343	            context_parts.append(self.business_layer(object_type, question))
344	
345	        if 4 in include_layers:
346	            context_parts.append(self.operational_layer(object_type))
347	
348	        if 5 in include_layers and question:
349	            context_parts.append(self.behavioral_layer(object_type, question))
350	
351	        # Add data profile if available
352	        if self.profiler:
353	            context_parts.append("\n## 数据概览\n")
354	            context_parts.append(self.profiler.get_summary_text())
355	
356	        return "\n".join(context_parts)
357	
358	    def add_to_history(self, question: str, sql: str, object_type: str, success: bool = True):
359	        """Add a query to behavioral history"""
360	        self.query_history.append({
361	            "question": question,
362	            "sql": sql,
363	            "object_type": object_type,
364	            "success": success,
365	            "timestamp": datetime.now().isoformat()
366	        })
367	
368	    def _find_similar_queries(self, question: str, object_type: str, top_k: int = 3) -> List[Dict]:
369	        """
370	        Find similar historical queries
371	
372	        Simple keyword matching - production would use embeddings
373	        """
374	        question_words = set(question.lower().split())
375	        scored = []
376	
377	        for q in self.query_history:
378	            if q["object_type"] != object_type:
379	                continue
380	            if not q["success"]:
381	                continue
382	
383	            history_words = set(q["question"].lower().split())
384	            overlap = len(question_words & history_words)
385	            scored.append((overlap, q))
386	
387	        scored.sort(key=lambda x: x[0], reverse=True)
388	        return [q for _, q in scored[:top_k]]
389	
390	
391	def get_context_engine(
392	    ontology: Optional[OntologyEngine] = None,
393	    db_path: Optional[str] = None
394	) -> ContextEngine:
395	    """Factory function for ContextEngine"""
396	    return ContextEngine(ontology=ontology, db_path=db_path)

### Q32

1	"""SQL Selector - Candidate selection and validation
2	
3	Selects the best SQL candidate from multiple generated paths.
4	In production, this uses an LLM for pairwise comparison.
5	Currently uses rule-based scoring with optional LLM enhancement.
6	"""
7	
8	import re
9	from typing import List, Optional, Dict, Tuple
10	from dataclasses import dataclass
11	
12	from agent.sql_engine.generator import SQLCandidate, NL2SQLEngine
13	from agent.understand.entity_extractor import ExtractionResult
14	from agent.understand.intent_detector import IntentResult, QueryIntent
15	
16	
17	@dataclass
18	class SelectionResult:
19	    """Result of SQL selection"""
20	    best: SQLCandidate
21	    runner_up: Optional[SQLCandidate]
22	    scores: Dict[str, float]  # path -> score
23	    reasoning: str
24	
25	
26	class SQLSelector:
27	    """
28	    SQL Candidate Selector.
29	
30	    Validation checks:
31	    - SQL syntax
32	    - Table/column existence (via ontology)
33	    - Filter coverage (all entities represented?)
34	    - Intent alignment (aggregation/grouping correct?)
35	
36	    Selection strategy:
37	    1. Validate all candidates
38	    2. Score each
39	    3. If close scores, prefer plan_based (more structured reasoning)
40	    """
41	
42	    # Dangerous SQL patterns
43	    FORBIDDEN_PATTERNS = [
44	        r"\bDROP\b",
45	        r"\bDELETE\b",
46	        r"\bUPDATE\b",
47	        r"\bINSERT\b",
48	        r"\bALTER\b",
49	        r"\bATTACH\b",
50	        r"\bDETACH\b",
51	    ]
52	
53	    def __init__(self):
54	        self._forbidden_re = [re.compile(p, re.IGNORECASE) for p in self.FORBIDDEN_PATTERNS]
55	
56	    def validate(self, sql: str) -> Tuple[bool, Optional[str]]:
57	        """Validate SQL syntax and safety"""
58	        # Check forbidden patterns
59	        for pattern in self._forbidden_re:
60	            if pattern.search(sql):
61	                return False, f"Forbidden operation detected"
62	
63	        # Check basic structure
64	        if not re.search(r"SELECT\s+", sql, re.IGNORECASE):
65	            return False, "Missing SELECT"
66	
67	        if not re.search(r"FROM\s+\w+", sql, re.IGNORECASE):
68	            return False, "Missing FROM clause"
69	
70	        # Check balanced parentheses
71	        if sql.count("(") != sql.count(")"):
72	            return False, "Unbalanced parentheses"
73	
74	        return True, None
75	
76	    def score_candidate(self, candidate: SQLCandidate,
77	                        question: str,
78	                        entities: ExtractionResult,
79	                        intent: IntentResult) -> float:
80	        """
81	        Score a candidate. Higher is better.
82	
83	        Scoring criteria:
84	        - Base confidence from generator (0.3-0.7)
85	        - Filter coverage: are all extracted entities in SQL? (+0.1 each)
86	        - Intent alignment: correct aggregation/grouping? (+0.15)
87	        - SQL quality: proper columns, no SELECT * abuse (+0.1)
88	        - Path bonus: plan_based preferred for complex queries (+0.05)
89	        """
90	        score = candidate.confidence
91	        sql_lower = candidate.sql.lower()
92	
93	        # Filter coverage
94	        filter_entities = [e for e in entities.entities
95	                          if e.field and not e.field.startswith("__")
96	                          and e.entity_type not in ("aggregation", "sort", "metric")]
97	
98	        for entity in filter_entities:
99	            if entity.field.lower() in sql_lower:
100	                score += 0.1
101	            # Also check if entity value appears
102	            if entity.value.lower() in sql_lower:
103	                score += 0.05
104	
105	        # Intent alignment
106	        if intent.needs_aggregation and "count" in sql_lower:
107	            score += 0.1
108	        if intent.needs_grouping and "group by" in sql_lower:
109	            score += 0.15
110	        if intent.needs_timeseries:
111	            if "strftime" in sql_lower or "date(" in sql_lower:
112	                score += 0.15
113	            else:
114	                score -= 0.2  # Missing time dimension is bad
115	
116	        # SQL quality
117	        if intent.primary == QueryIntent.COUNT and "select *" in sql_lower:
118	            score -= 0.25
119	        if "limit" not in sql_lower and intent.primary in (QueryIntent.RANKING,
120	                                                            QueryIntent.DETAIL_LIST):
121	            score -= 0.1
122	
123	        # Path bonus
124	        if candidate.path == "plan_based" and intent.confidence > 0.5:
125	            score += 0.05
126	        if candidate.path == "decomposed" and len(filter_entities) >= 3:
127	            score += 0.05
128	
129	        # Penalty: WHERE clause missing
130	        filter_count = len(filter_entities)
131	        if filter_count > 0 and "where" not in sql_lower:
132	            score -= 0.4
133	
134	        return score
135	
136	    def select(self, candidates: List[SQLCandidate],
137	               question: str,
138	               entities: ExtractionResult,
139	               intent: IntentResult) -> SelectionResult:
140	        """
141	        Validate, score, and select the best candidate.
142	        """
143	        # Filter valid candidates
144	        valid = []
145	        for c in candidates:
146	            ok, err = self.validate(c.sql)
147	            if ok:
148	                valid.append(c)
149	
150	        if not valid:
151	            # Return the first candidate even if invalid
152	            return SelectionResult(
153	                best=candidates[0] if candidates else SQLCandidate(
154	                    sql="SELECT COUNT(*) FROM octane_defects",
155	                    path="emergency_fallback",
156	                    explanation="All candidates failed validation",
157	                    confidence=0.1
158	                ),
159	                runner_up=None,
160	                scores={c.path: 0.0 for c in candidates},
161	                reasoning="No valid candidates; using fallback"
162	            )
163	
164	        # Score all valid candidates
165	        scored = [(c, self.score_candidate(c, question, entities, intent))
166	                  for c in valid]
167	        scored.sort(key=lambda x: x[1], reverse=True)
168	
169	        best = scored[0][0]
170	        best_score = scored[0][1]
171	        runner_up = scored[1][0] if len(scored) > 1 else None
172	
173	        scores_map = {c.path: s for c, s in scored}
174	
175	        # Reasoning
176	        margin = best_score - (scored[1][1] if len(scored) > 1 else 0)
177	        if margin > 0.3:
178	            reasoning = f"'{best.path}' 路径显著领先(Δ={margin:.2f})"
179	        elif margin > 0.1:
180	            reasoning = f"'{best.path}' 路径略优(Δ={margin:.2f})"
181	        else:
182	            reasoning = f"候选分数接近，选择 '{best.path}' (plan_based优先)"
183	
184	        return SelectionResult(
185	            best=best,
186	            runner_up=runner_up,
187	            scores=scores_map,
188	            reasoning=reasoning
189	        )
190

### Q33

1	/** Data-Agent API client */
2	
3	import type { QueryResponse, MemoryStats, HistoryRecord } from '../types';
4	
5	const BASE = '/api/agent';
6	
7	export async function query(question: string, useMemory = true): Promise<QueryResponse> {
8	  const res = await fetch(`${BASE}/query`, {
9	    method: 'POST',
10	    headers: { 'Content-Type': 'application/json' },
11	    body: JSON.stringify({ question, use_memory: useMemory }),
12	  });
13	  if (!res.ok) throw new Error(`HTTP ${res.status}`);
14	  return res.json();
15	}
16	
17	export async function sendFeedback(
18	  memoryId: string,
19	  feedback: 'up' | 'down',
20	  note = '',
21	  correction = '',
22	): Promise<{ success: boolean; feedback_id: string }> {
23	  const res = await fetch(`${BASE}/feedback`, {
24	    method: 'POST',
25	    headers: { 'Content-Type': 'application/json' },
26	    body: JSON.stringify({
27	      query_memory_id: memoryId,
28	      feedback,
29	      note,
30	      correction,
31	    }),
32	  });
33	  if (!res.ok) throw new Error(`HTTP ${res.status}`);
34	  return res.json();
35	}
36	
37	export async function getStats(): Promise<MemoryStats> {
38	  const res = await fetch(`${BASE}/stats`);
39	  if (!res.ok) throw new Error(`HTTP ${res.status}`);
40	  return res.json();
41	}
42	
43	export async function getHistory(limit = 20): Promise<{ records: HistoryRecord[]; count: number }> {
44	  const res = await fetch(`${BASE}/history?limit=${limit}`);
45	  if (!res.ok) throw new Error(`HTTP ${res.status}`);
46	  return res.json();
47	}
48	
49	/**
50	 * SSE stream query — returns an async generator of events
51	 */
52	export async function* streamQuery(question: string): AsyncGenerator<{ event: string; data: unknown }> {
53	  const url = `${BASE}/stream?question=${encodeURIComponent(question)}`;
54	  const res = await fetch(url);
55	
56	  if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);
57	
58	  const reader = res.body.getReader();
59	  const decoder = new TextDecoder();
60	  let buffer = '';
61	  let currentEvent = '';
62	  let currentData = '';
63	
64	  while (true) {
65	    const { done, value } = await reader.read();
66	    if (done) break;
67	
68	    buffer += decoder.decode(value, { stream: true });
69	    const lines = buffer.split('\n');
70	    buffer = lines.pop() || '';
71	
72	    for (const line of lines) {
73	      if (line.startsWith('event:')) {
74	        currentEvent = line.slice(6).trim();
75	      } else if (line.startsWith('data:')) {
76	        currentData = line.slice(5).trim();
77	      } else if (line === '' && currentEvent) {
78	        let data: unknown = currentData;
79	        try {
80	          data = JSON.parse(currentData);
81	        } catch { /* keep as string */ }
82	        yield { event: currentEvent, data };
83	        currentEvent = '';
84	        currentData = '';
85	      }
86	    }
87	  }
88	}
89

### Q34

1	"""Few-shot examples for NL→SQL generation
2	
3	30+ business query examples covering:
4	- Count queries
5	- Trend analysis
6	- Distribution / breakdown
7	- Ranking
8	- Comparison
9	- Detail listing
10	- Status checks
11	- Multi-condition filtering
12	"""
13	
14	from typing import List, Dict, Optional
15	from dataclasses import dataclass
16	
17	
18	@dataclass
19	class FewShotExample:
20	    """A few-shot NL→SQL example"""
21	    question: str
22	    sql: str
23	    intent: str
24	    explanation: str  # Why this SQL is correct
25	
26	
27	# Note: Using plain dict for simplicity
28	EXAMPLES: List[Dict] = [
29	    # === Count Queries (6) ===
30	    {
31	        "question": "IDCEVO 本月 Critical 缺陷有多少",
32	        "sql": "SELECT COUNT(*) FROM octane_defects WHERE project = 'IDCEVO' AND severity = 'Critical' AND creation_time >= date('now', 'start of month')",
33	        "intent": "count",
34	        "explanation": "按项目+严重度+时间范围过滤计数"
35	    },
36	    {
37	        "question": "活跃缺陷总数",
38	        "sql": "SELECT COUNT(*) FROM octane_defects WHERE status_phase IN ('New', 'Open', 'In Progress')",
39	        "intent": "count",
40	        "explanation": "活跃=status_phase IN (New, Open, In Progress)"
41	    },
42	    {
43	        "question": "中国项目有多少未关闭的缺陷",
44	        "sql": "SELECT COUNT(*) FROM octane_defects WHERE project IN ('IDCEVO', 'IDC', 'MGU') AND status_phase IN ('New', 'Open', 'In Progress')",
45	        "intent": "count",
46	        "explanation": "中国项目=IDCEVO+IDC+MGU, 未关闭=active状态"
47	    },
48	    {
49	        "question": "BCM 相关的 Critical 缺陷有几个",
50	        "sql": "SELECT COUNT(*) FROM octane_defects WHERE assigned_ecu = 'BCM' AND severity = 'Critical'",
51	        "intent": "count",
52	        "explanation": "按ECU和严重度过滤"
53	    },
54	    {
55	        "question": "本周新增了多少缺陷",
56	        "sql": "SELECT COUNT(*) FROM octane_defects WHERE creation_time >= date('now', 'weekday 0', 'start of week')",
57	        "intent": "count",
58	        "explanation": "本周=从本周一开始"
59	    },
60	    {

### Q35

1	# DefectHistory Object Type
2	# Defect state change history
3	
4	object_type: DefectHistory
5	description: "缺陷状态变更历史事件"
6	source_table: octane_defect_history_events
7	primary_key: (defect_id, event_timestamp, field_name, entry_index, change_index)
8	
9	properties:
10	  defect_id:
11	    type: string
12	    meaning: "缺陷ID"
13	    foreign_key: Defect.defect_id
14	
15	  event_timestamp:
16	    type: datetime
17	    meaning: "变更发生时间"
18	
19	  field_name:
20	    type: string
21	    meaning: "变更的字段名"
22	    examples: [status_phase, severity, assigned_ecu, solution_cluster]
23	
24	  entry_index:
25	    type: integer
26	    meaning: "事件条目索引"
27	
28	  change_index:
29	    type: integer
30	    meaning: "变更索引"
31	
32	  old_value:
33	    type: string
34	    meaning: "变更前的值"
35	
36	  new_value:
37	    meaning: "变更后的值"
38	    type: string
39	
40	  old_value_text:
41	    type: string
42	    meaning: "旧值的文本描述"
43	
44	  new_value_text:
45	    type: string
46	    meaning: "新值的文本描述"
47	
48	  fetched_at:
49	    type: datetime
50	    meaning: "数据抓取时间"
51	
52	links:
53	  - name: belongs_to_defect
54	    target: Defect
55	    type: many-to-one
56	    join: history.defect_id = defect.defect_id
57	    meaning: "历史记录所属的缺陷"
58	
59	metrics:
60	  status_change_count:
61	    definition: "COUNT(*) WHERE field_name = 'status_phase'"
62	    meaning: "状态变更次数"
63	
64	  severity_change_count:
65	    definition: "COUNT(*) WHERE field_name = 'severity'"
66	    meaning: "严重度变更次数"
67	
68	  avg_resolution_time_hours:
69	    definition: "AVG(new_time - old_time) WHERE field_name = 'status_phase' AND new_value = 'Closed'"
70	    meaning: "平均解决时长（小时）"
71	
72	calibration_rules:
73	  - id: "cal_history_is_changes_not_defects"
74	    trigger: ["history", "历史", "变更"]
75	    rule: "history 表记录的是字段变更事件，不是独立的缺陷实体"
76	
77	  - id: "cal_timestamp_is_event_time"
78	    trigger: ["时间", "timestamp", "event"]
79	    rule: "event_timestamp 是变更发生时间，用于计算解决时长等指标"

### Q36

1	# ManualRun Object Type
2	# Manual test execution records
3	
4	object_type: ManualRun
5	description: "手动测试执行记录"
6	source_table: octane_manual_runs
7	primary_key: mr_id
8	
9	properties:
10	  mr_id:
11	    type: string
12	    meaning: "测试执行唯一ID"
13	    examples: ["MR-2026-0001"]
14	
15	  defect_id:
16	    type: string
17	    meaning: "关联的缺陷ID（如有）"
18	    foreign_key: Defect.defect_id
19	
20	  test_id:
21	    type: string
22	    meaning: "测试用例ID"
23	    foreign_key: TestCase.test_id
24	
25	  test_name:
26	    type: string
27	    meaning: "测试用例名称"
28	
29	  status:
30	    type: enum
31	    meaning: "执行状态"
32	    values: [Passed, Failed, Blocked, Not_Executed, "In Progress"]
33	    semantics:
34	      Passed: "测试通过"
35	      Failed: "测试失败，发现缺陷"
36	      Blocked: "被阻塞，无法执行"
37	      Not_Executed: "未执行"
38	      "In Progress": "执行中"
39	
40	  year:
41	    type: string
42	    meaning: "年份"
43	    examples: ["2026", "2025"]
44	
45	  test_week:
46	    type: string
47	    meaning: "测试周次"
48	    examples: ["2026-W20", "2026-W21"]
49	
50	  pu:
51	    type: string
52	    meaning: "产品单元"
53	
54	  top_aida:
55	    type: string
56	    meaning: "AIDA 功能域"
57	
58	  feature_region:
59	    type: string
60	    meaning: "特性区域"
61	
62	  tester:
63	    type: string
64	    meaning: "测试人员"
65	
66	  project:
67	    type: enum
68	    meaning: "项目代号"
69	    values: [IDCEVO, IDC, MGU, RSU, App]
70	    aliases:
71	      IDCEVO: ["idcevo", "IDCEVO*", "CDE"]
72	      IDC: ["idc", "IDC23"]
73	      MGU: ["mgu", "MGU22", "BMWMGU"]
74	
75	  fv:
76	    type: string
77	    meaning: "功能版本"
78	
79	  fvp:
80	    type: string
81	    meaning: "功能版本计划"
82	
83	  team:
84	    type: string
85	    meaning: "负责团队"
86	
87	  lead_model:
88	    type: string
89	    meaning: "主导车型"
90	
91	  raw_json:
92	    type: json
93	    meaning: "Octane 原始 JSON 数据"
94	
95	  fetched_at:
96	    type: datetime
97	    meaning: "数据抓取时间"
98	
99	links:
100	  - name: finds_defect
101	    target: Defect
102	    type: many-to-one
103	    join: manual_run.defect_id = defect.defect_id
104	    meaning: "测试执行发现的缺陷"
105	
106	  - name: executes_testcase
107	    target: TestCase
108	    type: many-to-one
109	    join: manual_run.test_id = testcase.test_id
110	    meaning: "执行的测试用例"
111	
112	  - name: belongs_to_project
113	    target: Project
114	    type: many-to-one
115	    join: manual_run.project = project.name
116	    meaning: "所属项目"
117	
118	metrics:
119	  pass_rate:
120	    definition: "COUNT(*) FILTER (WHERE status = 'Passed') / COUNT(*) * 100"
121	    meaning: "测试通过率"
122	
123	  fail_rate:
124	    definition: "COUNT(*) FILTER (WHERE status = 'Failed') / COUNT(*) * 100"
125	    meaning: "测试失败率"
126	
127	  defect_detection_rate:
128	    definition: "COUNT(*) FILTER (WHERE defect_id IS NOT NULL) / COUNT(*) * 100"
129	    meaning: "缺陷检出率"
130	
131	calibration_rules:
132	  - id: "cal_status_not_phase"
133	    trigger: ["status", "状态", "passed", "failed"]
134	    rule: "manual_run.status 是执行状态（Passed/Failed/Blocked），不是缺陷状态（status_phase）"
135	
136	  - id: "cal_defect_in_failed_runs"
137	    trigger: ["defect", "缺陷", "发现缺陷"]
138	    rule: "只有在 status = 'Failed' 的测试执行中才有 defect_id"

### Q37

1	"""Ontology Module - Semantic Object Modeling
2	
3	Inspired by Palantir Ontology and WrenAI MDL
4	
5	This module provides:
6	- Object type definitions (YAML-based)
7	- Semantic property and relationship modeling
8	- Business rule definitions
9	- Calibration rules for common misunderstandings
10	- Governance and access control definitions
11	"""
12	
13	from .engine import (
14	    OntologyEngine,
15	    ObjectType,
16	    PropertyDef,
17	    LinkDef,
18	    MetricDef,
19	    CalibrationRule,
20	    Governance,
21	    get_ontology_engine,
22	    PropertyType,
23	)
24	
25	__all__ = [
26	    "OntologyEngine",
27	    "ObjectType",
28	    "PropertyDef",
29	    "LinkDef",
30	    "MetricDef",
31	    "CalibrationRule",
32	    "Governance",
33	    "get_ontology_engine",
34	    "PropertyType",
35	]

### Q38

1	"""Agent Loop - ReAct Tool Calling + SSE Streaming
2	
3	Core modules:
4	- loop.py: ReAct reasoning loop (rule-based + LLM-based)
5	- tools.py: 6 core agent tools
6	- registry.py: Tool registration and discovery
7	- streaming.py: SSE event stream for real-time output
8	"""
9	
10	from agent.agent_loop.loop import (
11	    ReActAgent, AgentStep, AgentResponse, StepType, get_agent
12	)
13	from agent.agent_loop.tools import (
14	    AgentTool, ToolResult, ToolParameter,
15	    QueryDefectsTool, QueryTrendTool, DistributionTool,
16	    RankingTool, SearchSimilarTool, DashboardTool,
17	)
18	from agent.agent_loop.registry import ToolRegistry, build_default_registry
19	from agent.agent_loop.streaming import SSEEventStream
20	
21	__all__ = [
22	    "ReActAgent", "AgentStep", "AgentResponse", "StepType", "get_agent",
23	    "AgentTool", "ToolResult", "ToolParameter",
24	    "QueryDefectsTool", "QueryTrendTool", "DistributionTool",
25	    "RankingTool", "SearchSimilarTool", "DashboardTool",
26	    "ToolRegistry", "build_default_registry",
27	    "SSEEventStream",
28	]
29

## 助手回答（完整）

### A1

I'll explore this project thoroughly. Let me start by understanding the overall structure, then dive into each module.

### A2

Let me read the key documentation and the CLAUDE.md to get oriented, then start reading actual code.

### A3

Now let me read the agent loop registry, tools, streaming, and the ontology engine in parallel.

### A4

Now the ontology engine and YAML objects, plus the SQL engine.

### A5

Now the SQL engine. Let me read all SQL engine files in parallel.

### A6

Now let me read the multi_executor, selector, understanding modules, and data layer in parallel.

### A7

Now let me read the remaining modules: term_resolver, data layer, learning, conversation, interpret, LLM, context engine, selector.

### A8

Now the learning, conversation, interpret, LLM client, context engine, and selector.

### A9

Now the conversation context, interpret modules, LLM client, context engine, and selector.

### A10

Now let me read the context engine, selector, examples, frontend client, and the AIChatPage to understand the frontend.

### A11

I have read all the core modules thoroughly. Let me do a few final checks: the examples.py, the __init__ files for the public API, and a quick look at the frontend AIChatPage and the remaining ontology YAMLs to confirm the data model.

### A12

I have now read all the core modules thoroughly. I have a comprehensive understanding of the architecture. Let me compile the final report.

---

# Data-Agent — Architecture Analysis

A text-to-SQL conversational agent for **automotive test-defect / Octane data**. Python FastAPI backend + React/TypeScript frontend. Rule-based by default, LLM-enhanced (ZhiPu GLM / DeepSeek) when API keys are set. Inspired explicitly by several research systems (WrenAI MDL, CHASE-SQL, MARS-SQL, BIRD-Interact, Palantir Ontology).

---

## 1. Entry Points & Runtime

**`api/main.py`** — FastAPI app, run via `python3 -m api.main` or `uvicorn api.main:app` (port 8100, default).

Endpoints (`api/main.py`):
- `POST /api/agent/query` (sync) — main path (`main.py:320`)
- `GET /api/agent/stream` — SSE streaming (`main.py:444`)
- `POST /api/agent/feedback` (`main.py:485`), `GET /api/agent/history` (`:515`), `GET /api/agent/stats` (`:526`)
- Session lifecycle: `POST/DELETE /api/agent/session[/{id}]`, `GET /api/agent/sessions` (`:542-603`)
- LLM: `/api/agent/llm/status`, `/api/agent/llm/test`
- Value retrieval: `/api/agent/values/stats`, `/api/agent/values/search`

**Configuration** (`main.py:62-67`): two DBs — `DB_PATH` = `data/agent_memory.db` (memory/feedback), `DATA_DB_PATH` = `resolve_data_db_path()` (the data being queried). `AGENT_MODE` env (`llm` default vs rule-based). Lazy module-level singletons: `_ontology`, `_agent`, `_query_memory`, `_feedback_store`, `_storyteller`, `_llm_client`, `_session_manager` (`main.py:76-159`).

**Multi-turn sessions**: `get_agent_for_session(session_id)` (`main.py:162`) keeps a dict `_session_agents[session_id] -> ReActAgent`, each with its own `ConversationContext` from `SessionManager`. Without `session_id`, falls back to the shared stateless `_agent`.

**Frontend** (`frontend/`, Vite + React + TS):
- `src/api/client.ts` — calls `/api/agent/query`, `/feedback`, `/stats`, `/history`, and an SSE reader `streamQuery()` that parses `event:`/`data:` frames.
- `src/pages/AIChatPage.tsx`, `src/components/AgentStepDisplay.tsx` (renders ReAct steps), `ChartRenderer.tsx`, `StoryCard.tsx` (renders storyteller output), `FeedbackButtons.tsx`, `StatsPanel.tsx`. Vite dev proxy forwards `/api` to the backend.

---

## 2. Agent Loop & Pipeline (`agent/agent_loop/`)

**`loop.py` — `ReActAgent`** implements the ReAct pattern (Thought/Action/Observation/Final). Two execution modes (`loop.py:131-187`):
1. **Rule-based** (`_process_rule_based`, `:211`): deterministic — extract entities → detect intent → map intent→tool (`_select_tool_name`, `:296`) → execute → format answer (`_format_answer`, `:575`).
2. **LLM-based** (`_process_with_llm`, `:367`): standard function-calling loop — builds system prompt (`_build_system_prompt`, `:538`) with tool descriptions + ontology schema context + conversation history; loops up to `MAX_STEPS=8` (`:73`); each turn either the LLM emits `tool_calls` (executed via registry, results appended as `role:"tool"` messages) or a final answer.

**Streaming** (`process_stream`, `:189`): yields `AgentStep` objects; `streaming.py` (`SSEEventStream`) converts `StepType` → SSE event names (thought/action/observation/final/error). Note the `/api/agent/stream` endpoint (`main.py:444`) bypasses `SSEEventStream` and directly consumes `agent.process_stream`.

**Tools** (`tools.py`, 7 tools registered in `registry.py:82`):
- `query_defects` — wraps `NL2SQLEngine` (`tools.py:81`)
- `query_trend` — time-series; re-runs NL2SQL just to harvest the WHERE clause, then rewrites with `strftime` grouping (`tools.py:147`)
- `get_distribution`, `get_ranking` — direct SQL builders using ontology table + filter-string parsing (`tools.py:259, 366`)
- `search_similar` — BGE semantic search if `embedding_search_fn` injected, else SQL `LIKE` fallback (`tools.py:459`)
- `get_dashboard` — fixed KPI queries (`tools.py:552`)
- `analyze_data` (CodeInterpreterTool) — LLM-generated Python sandboxed (`tools.py:635`)

**Registry** (`registry.py`): `ToolRegistry` registers tools, exposes `get_schemas()` for OpenAI-style function-calling, validates required params, fills defaults. Each `AgentTool.to_schema()` (`tools.py:60`) produces `{name, description, parameters{type, properties, required}}`.

**Key data classes**: `AgentStep` (step_type, content, tool_name, tool_input, tool_output) `:36`; `AgentResponse` (answer, steps, tools_used, sql_executed, success) `:47`; `ToolResult` (success, data, sql, summary, error, metadata) `tools.py:37`.

---

## 3. Understanding Stage (`agent/understand/`)

Pipeline: `term_resolver` → `entity_extractor` → `intent_detector`.

**`term_resolver.py`** — `TermResolver.resolve()` maps user vocabulary → canonical `(field, value)`:
- Builds a reverse alias index from ontology YAML `aliases`/`values`/`examples` + a `SUPPLEMENT_SYNONYMS` dict (`:101`).
- Longest-match-first, non-overlapping, CJK-aware (skips word-boundary checks for CJK) (`:164`).
- Expands `category_groups` (e.g. "活跃" → `status_phase IN ('New','Open','In Progress')`; "中国项目" → `project IN (IDCEVO,IDC,MGU)`) (`:229`).
- Numeric constraints (`超过N`, `前N`, `top N`) and time ranges (`本月`, `近30天`) via regex (`:66-95`).
- Output: list of `ResolvedTerm(original, canonical, field, value, operator, values, source)`.

**`entity_extractor.py`** — `EntityExtractor.extract()` (`:96`) wraps `TermResolver`, adds metric extraction (`METRIC_KEYWORDS`), aggregation-intent extraction (`AGG_PATTERNS`), precise date computation (`_extract_time_ranges`, `:224` — converts `本月` etc. to concrete `[start,end]`), and sort/limit. Output: `ExtractionResult` (list of `Entity` + `unresolved`). `to_sql_filters()` (`:307`) renders entities into WHERE fragments (`field IN (...)`, `field BETWEEN`, `field = '...'`).

**`intent_detector.py`** — `IntentDetector.detect()` (`:165`) scores 11 intents (COUNT, TREND, RANKING, DISTRIBUTION, COMPARISON, DETAIL_LIST, SEARCH_SIMILAR, RISK_ANALYSIS, SUMMARY, ROOT_CAUSE, STATUS_CHECK) via `INTENT_RULES` regex table (`:53`), each carrying an `sql_template` + flags (`needs_aggregation/grouping/timeseries/join`). Aggregation entities from the extractor boost scores. Output: `IntentResult(primary, secondary, confidence, sql_template, …)`.

---

## 4. Ontology (`agent/ontology/`)

**`engine.py` — `OntologyEngine`** loads YAML from `objects/*.yaml` into `ObjectType` dataclasses (`:80`): `source_table`, `primary_key`, `properties` (dict of `PropertyDef`), `links` (`LinkDef`), `metrics` (`MetricDef`), `calibration_rules` (`CalibrationRule`), `governance` (`Governance`).

**`PropertyDef`** (`:27`) is rich: `type, meaning, values, examples, foreign_key, category_groups, semantics, business_rules, aliases, mapping, item_type`.

**Objects** (6 YAMLs):
- **Defect** → `octane_defects` (`defect.yaml`) — the central entity. Properties: defect_id, name, project (enum with aliases: IDCEVO↔[idcevo, ENTRYEVO, NBTEVO, CDE], etc.; category_groups: china/global), market, status_phase (enum with lifecycle `New→Open→…→Closed`; category_groups: active/resolved/excluded), severity (Critical/Major/Minor/Cosmetic with business meanings), assigned_ecu (BCM/VCU/MCU/... with Chinese aliases like 车身控制器→BCM), top_aida, phase (Q-Gate/CoC/Integration groups), creation_time, raw_json. 6 metrics (active_defect_count, defect_density, …). 7 calibration_rules (e.g. `cal_severity_not_matrix`, `cal_trend_uses_creation_time`, `cal_active_excludes_closed`). Governance forbids update/delete/insert.
- **Project** → `derived` (not a real table).
- **TestCase** → `octane_testcases` (composite PK; JSON-array fields like `defect_ids_json`; many-to-many to Defect `via octane_testcase_relations`).
- **ManualRun** → `octane_manual_runs` (test execution records; pass_rate/fail_rate metrics; calibration distinguishing run.status vs defect.status_phase).
- **DefectHistory** → `octane_defect_history_events` (field-change events, not separate defects; resolution-time metric).
- **Team**.

**How it's used everywhere**: source-table & PK lookup by tools; alias resolution + category expansion in `TermResolver`; schema-context generation `to_schema_context()` (`:316`) injected into LLM prompts; `find_relevant_rules()` feeds business-rule reminders into the ContextEngine; governance flags forbid dangerous ops in `SQLSelector`/`QueryFixer`.

---

## 5. SQL Engine (`agent/sql_engine/`)

**`generator.py` — `NL2SQLEngine`** is the orchestrator. Notably, despite the class names referencing LLMs, generation is **template-based, not LLM-based**. `query()` (`:590`) pipeline:
1. **Analyze** — entity extraction + intent + 5-layer context (`analyze_question`, `:89`).
2. **Generate 3 candidates** via CHASE-SQL-inspired paths (`generate_candidates`, `:494`):
   - `DirectGenerator` (`:178`) — fills the intent's `sql_template`.
   - `DecomposedGenerator` (`:234`) — detects multiple grouping dimensions / HAVING numeric constraints.
   - `PlanBasedGenerator` (`:328`) — builds an explicit execution plan, selects columns by intent, special-cases trend/distribution%.
3. **Static scoring/selection** (`select_best`, `:515`; `_score_candidate`, `:545`) — bonus for covering entity fields, correct aggregation/grouping/timeseries; penalties for missing WHERE / `SELECT *`.
4. **Multi-path execution** (`multi_executor.py`) — **execution-guided selection**: runs all candidates, computes a `data_signature` (`:62`) per result, and agreement level: UNANIMOUS (conf 0.95) / MAJORITY 2-of-3 (0.80) / DISAGREE → LLM arbitration (`_llm_arbitrate`, `:293`) or path-preference fallback (plan_based > decomposed > direct).
5. **Self-correction** (`fixer.py` — `QueryFixer`, CHASE-SQL Algorithm 4): executes; on error or sanity-check failure, prompts LLM with `REASONING:`/`FIXED_SQL:` format; retries up to β=3 (`:75`); `_sql_looks_valid` blocks DROP/DELETE/etc. (`:305`).
6. **Validation** (`validator.py` — `ResultValidator`, MARS-SQL style): rule checks (empty-result-for-data-questions, >10K rows, uniform values, distribution %sum, SQL↔intent alignment) then optional LLM semantic check returning PASS/`FAIL: reason`.

**`selector.py`** (`SQLSelector`) — older static validation+scoring layer (forbidden-pattern regex, paren balance, filter-coverage scoring). **Note**: it's imported by `__init__` but `NL2SQLEngine.query()` actually uses its own `select_best` + `MultiPathExecutor`, not `SQLSelector.select` — so `SQLSelector` is largely **dormant/duplicate** code (tech debt).

**`examples.py`** — 30+ hand-written few-shot `(question, sql, intent, explanation)` dicts used by `DirectGenerator` and `to_prompt_context`.

---

## 6. Data Layer (`agent/data/`)

**`adapter.py`** — SQLite is the only real backend (PostgreSQL mentioned in docstring but not implemented). Three schemas (`DEFECTS_SCHEMA`, `MANUAL_RUNS_SCHEMA`, `DEFECT_HISTORY_SCHEMA`), `:30-83`. **Important schema mismatch**: the adapter's `octane_defects` columns (`defect_id, summary, description, status_phase, severity, project, detected_by, ecu, aidas, top_aida, tags, …`) differ from the ontology's property names (`name`, `assigned_ecu`, `problem_finder_team`, …). Several tools/generators reference ontology field names (`assigned_ecu`, `name`) that don't exist in the generated sample schema (`ecu`, `summary`) — a latent inconsistency.

- `resolve_data_db_path()` (`:245`): `DATA_DB_PATH` env var → else auto-creates `data/sample_defects.db` with 500 mock defects + 300 runs (`generate_sample_defects`, seeded). Production = point `DATA_DB_PATH` at a real Octane-derived SQLite.
- `execute_query()` (`:272`) — standard row-factory helper.
- Sample generator biases Critical toward active statuses (`:120`).

**`value_retriever.py`** — closes the vocabulary gap (user says 车身控制器, DB has BCM):
- At construction, runs `SELECT DISTINCT <field>` for ~11 indexed fields, builds `FieldIndex` per field + a global `(value, field)` list (`_build_index`, `:176`); merges ontology aliases (`_load_ontology_aliases`).
- `retrieve()` (`:244`) — tiered: exact (100) → alias (95) → partial-alias (85+) → **rapidfuzz** `token_set_ratio` fuzzy (≥65); falls back to `difflib` if rapidfuzz missing (`:50`).
- `get_hints_for_question()` (`:391`) — strategy 1 matches known values/aliases as substrings; strategy 2 tokenizes the question and fuzzy-matches unknown tokens. Returns `{field: {matches, best, sql_in}}` consumed by `SQLGenerator.build_where_clause` (`generator.py:119`) to add filters for fields entity-extraction missed.

---

## 7. Learning / Memory (`agent/learning/`)

**`query_memory.py` — `QueryMemory`**: SQLite table `query_memory` storing successful (question, normalized_question, sql, intent, entities, result_summary, feedback, usage_count, score). `record()` (`:222`) deduplicates by md5(question::sql), bumps usage_count. `retrieve_similar()` (`:312`) loads top-500 by score and computes **hybrid** similarity = max(semantic, legacy Jaccard(0.6)+edit-distance(0.4)); feedback up/down nudges. Score = recency + usage + feedback.

**`semantic_matcher.py` — `SemanticMatcher`**: three tiers (`:214`):
1. Embedding cosine (if `embedding_fn` injected; cached)
2. **TF-IDF cosine** — a from-scratch `TfidfVectorizer` (`:93`) with **CJK bigram tokenization** (`tokenize`, `:46`) + IDF smoothing; always available, no deps.
3. Jaccard fallback.
Fit on the corpus after each record (`_fit_semantic_matcher`). Comment notes this beats Jaccard 0.42→0.78 for paraphrases.

**`feedback_store.py` — `FeedbackStore`**: SQLite `feedback` table linked by `query_memory_id`. `record()` (`:94`) adjusts `query_memory.score` (up +1.0 / down −0.5). `get_weight_adjustments()` (`:174`) aggregates satisfaction by intent → suggests per-intent scoring boosts/penalties (≥0.8 → +0.1, ≤0.4 → −0.2). API surfaces stats at `/api/agent/stats`.

---

## 8. Conversation Context (`agent/conversation/context.py`)

`ConversationContext` + `SessionManager` (BIRD-Interact-inspired).
- **`TurnClassifier.classify()`** (`:127`) → `TurnType` (INITIAL/REFINE/FOLLOW_UP/CLARIFY/COMPARE) using keyword sets + CJK-bigram token overlap with the last turn (≥3 shared bigrams → continuation).
- **`ContextResolver.resolve()`** (`:231`) — LLM rewrites the question with history (preferred) using a Chinese `RESOLUTION_PROMPT` (`:197`); falls back to `_rule_resolve` (`:293`) which prepends inherited project/severity/ecu entities for REFINE, or wraps the prior subject for short FOLLOW_UPs.
- `add_turn()` records (question, resolved_question, sql, result_summary, entities); trims to `max_history=10`.
- `SessionManager` (`:493`) — per-`session_id` contexts, 30-min expiry, in-memory only (not persisted). `loop.py:129` injects the conversation into the agent; `_build_system_prompt` injects `get_history_text(3)` into the LLM system prompt.

---

## 9. Interpretation (`agent/interpret/`)

**`code_interpreter.py` — `CodeInterpreter`**: LLM generates Python from `CODE_GEN_PROMPT` (data passed as `data` list-of-dict, must assign `result`); **sandbox** = writes script to a temp file, runs via `subprocess` with `timeout` (5s in the tool), data via stdin, `FORBIDDEN_PATTERNS` block (`import os/subprocess/socket`, `open(`, `__import__`, `exec/eval`, …) and a `SAFE_IMPORTS` allowlist (pandas/numpy/math/re/json/statistics/collections/itertools) (`:88-113`). `_check_safety` (`:255`). Template fallback when no LLM (`_fallback_code`). **Caveat**: the forbidden-pattern check is substring-based and easily bypassed (e.g. `__builtins__`, `getattr`), so it's a weak sandbox — acceptable for a trusted single-user tool, not multi-tenant.

**`storyteller.py` — `DataStoryteller`**: turns result data into business narratives (`StoryResult`: headline/body/insights/recommendation). Methods per type: `tell_count` (severity-aware urgency), `tell_trend` (direction with ±15% threshold, peaks, CV volatility), `tell_distribution` (TOP3 %, concentration analysis, severity-specific), `tell_ranking` (top-vs-average, gaps), `tell_summary` (resolve rate, active rate). The API layer (`main.py:354-396`) post-processes `response.steps` to pick the right `tell_*` by `tools_used[-1]`.

---

## 10. LLM (`agent/llm/client.py`)

`LLMClient` — unified client over OpenAI-compatible APIs via `httpx`. Providers in `PROVIDER_CONFIG` (`:58`):
- **ZhiPu GLM** — `glm-4-flash` default (free tier), base `open.bigmodel.cn/api/paas/v4`.
- **DeepSeek** — `deepseek-chat`, base `api.deepseek.com/v1`.
Both `temperature=0.1`, `max_tokens=4096`. Lightweight `.env` loader (`:34`, no python-dotenv dep). Selection: `AGENT_LLM_PROVIDER` env (default `zhipu`; `none` disables).

**Adapters** (clean separation of signatures):
- `as_agent_fn()` (`:291`) → `fn(messages, tools) -> {content, tool_calls}` for `ReActAgent`; converts internal schemas to OpenAI `tools` format.
- `as_fixer_fn()` (`:320`) → `fn(prompt)->str` for `QueryFixer`/`ResultValidator`/generator (temp 0.0).
- `chat_text` for simple completions.

---

## 11. End-to-End Flow & Cross-Cutting Observations

**End-to-end for a query** (e.g. "IDCEVO 本月 Critical 缺陷有多少"):
1. `POST /api/agent/query` → `get_agent_for_session` → `agent.process(question)`.
2. `ReActAgent.process` (`loop.py:131`): conversation `classify`+`resolve` (multi-turn rewrite).
3. LLM mode: system prompt (ontology schema + tools + history) → LLM function-calls `query_defects(question=...)`.
4. `QueryDefectsTool` → `NL2SQLEngine.query`:
   - `analyze_question`: `EntityExtractor.extract` (TermResolver → "IDCEVO"→project, "Critical"→severity, "本月"→creation_time range) + `IntentDetector.detect` → COUNT.
   - 3 candidate SQLs (direct/decomposed/plan) generated by template fill.
   - `MultiPathExecutor.execute_and_compare` — runs all 3; if unanimous, high-confidence return; else LLM-arbitrate.
   - `QueryFixer.execute` (LLM self-correction) → `ResultValidator.validate` (rule + LLM PASS/FAIL).
5. Observation appended; loop continues until LLM emits a final answer (≤8 steps).
6. `api/main.py` post-processing: parses `turn_type`/`resolved_question` from steps via regex, builds a `story` via `DataStoryteller`, records to `QueryMemory` (md5-deduped), returns `QueryResponse{answer, steps, tools_used, sql_executed, story, memory_record_id, ...}`.
7. Frontend renders steps (`AgentStepDisplay`), charts (`ChartRenderer`), story (`StoryCard`); `FeedbackButtons` POST to `/feedback` → `FeedbackStore` adjusts score.

**Key design patterns / abstractions**:
- **Singleton-everywhere** (`get_*` factories with module-level `_instance`) for ontology, agent, LLM, memory, validator, retriever — simple but means global mutable state and the session agent cache (`_session_agents`) leaks across requests.
- **Ontology-as-single-source-of-truth**: schema, aliases, categories, rules, governance all flow from YAML into understanding, generation, prompt-building, and validation. This is the project's strongest abstraction.
- **Multi-path generate → execute → agree → fix → validate** is a genuinely sophisticated NL2SQL pipeline (CHASE-SQL + MARS-SQL) unusual for a small codebase.
- **Graceful degradation**: every LLM-dependent path has a rule-based fallback (intent/entity extraction is pure regex; SQL is template-based; code interpreter has `_fallback_code`), so the agent runs fully offline.

**Strengths**: rich ontology with calibration rules that encode real domain gotchas (severity≠matrix, trend uses creation_time, active excludes closed); TF-IDF with CJK bigrams for zero-dep semantic memory; clean LLM adapter layering; multi-path execution agreement is a strong correctness signal.

**Weaknesses / tech debt**:
1. **Schema/ontology drift** — ontology property names (`assigned_ecu`, `name`, `problem_finder_team`) don't match `adapter.py` sample-schema columns (`ecu`, `summary`, `detected_by`); sample DB also uses `domain`/`top_aida=SA1/SA2` while ontology expects `top_aida=cn_navigation`-style values. Several queries will silently return empty on the sample DB.
2. **Dormant code** — `SQLSelector` is fully implemented but unused (superseded by `select_best`+`MultiPathExecutor`); `PlanBasedGenerator` decomposed logic overlaps `DecomposedGenerator`.
3. **Weak sandbox** — code interpreter uses substring denylisting, trivially bypassable; not safe for untrusted input.
4. **f-string bug** in `_fallback_code` (`code_interpreter.py:233`) — the template embeds `{{`/`}}` in a non-f-string so it emits literal braces correctly, but it's fragile; the auto-generated code hardcodes data inline.
5. **CORS `allow_origins=["*"]`** with `allow_credentials=True` (`main.py:262`) — insecure combo.
6. **Regex parsing of steps** in the API layer (`main.py:344-352`, parsing "类型:" / "→ '...'") is brittle string-scraping of localized step content.
7. **SQL injection surface**: distribution/ranking/dashboard tools build SQL via f-strings with `filters` string interpolation (`tools.py:303-331`, `:417-422`) — relies on the LLM/rule layer not emitting quotes; no parameterization.
8. **In-memory sessions** — `SessionManager` doesn't persist; restart loses all conversation state.
9. **`MAX_STEPS=8` with no cost guard** — each LLM iteration is a full function-calling round-trip; no token budgeting.

**Repo extras**: extensive phase reports (`PHASE1-6_REPORT.md`, `AGENT_DESIGN_REVIEW.md`, `DUPLICATE_DEFECT_SEARCH_DESIGN.md`) documenting the research-paper inspirations and incremental build; comprehensive `tests/` (one test per module: intent_detector, entity_extractor, term_resolver, sql_engine, multi_executor, validator, fixer, value_retriever, semantic_memory, code_interpreter, conversation_context, agent_loop, api, etc.).
