---
title: "I need to understand the routing logic in agent core enhanced_ai_chat…"
tool: "Claude Code"
session_id: "agent-a8cf2e305050e22ee"
source_path: "/Users/tonyorz/.claude/projects/-Users-tonyorz-aianalysis/ff35778a-908b-4d63-87c6-c20eb439c8d7/subagents/agent-a8cf2e305050e22ee.jsonl"
started_at: "2026-03-17T03:05:38.807Z"
user_turns: "9"
assistant_turns: "5"
tags:
  - ai-session
  - claude-code
---

# I need to understand the routing logic in agent core enhanced_ai_chat…

## Snapshot
- Tool: [[40 Tools/Claude Code]]
- Source: `/Users/tonyorz/.claude/projects/-Users-tonyorz-aianalysis/ff35778a-908b-4d63-87c6-c20eb439c8d7/subagents/agent-a8cf2e305050e22ee.jsonl`
- Kind: `session`
- Started: `2026-03-17T03:05:38.807Z`
- Working directory: `/Users/tonyorz/aianalysis`
- User turns: `9`
- Assistant turns: `5`
- Tool usage: `Read x4, Grep x4`
- Keywords: `task_id, chat_messages, user_message, html, chat_id_prefix, dash, no_update, status_display, True, time, current_data, style`

## First Request
> I need to understand the routing logic in agent/core/enhanced_ai_chat_manager.py. Specifically: 1. Read around line 1290 - the _is_advanced_decision_query meth…

## Key User Asks
- I need to understand the routing logic in agent/core/enhanced_ai_chat_manager.py. Specifically: 1. Read around line 1290 - the _is_advanced_decision_query meth…
- 1375→ 'last_progress_update': time.time() 1376→ } 1377→ 1378→ has_db = bool( 1379→ getattr(self.intelligent_agent, "tool_executor", None) 1380→ and getattr(sel…
- 1270→ 'backgroundColor': '#f8f9fa', 1271→ 'borderRadius': '8px', 1272→ 'margin': '8px 0', 1273→ 'border': '1px solid #e9ecef' 1274→ }) 1275→ return [initial_me…
- 1540- 1541- def _format_agent_message(self, text: str, tools_used: List[str], insights: List[str]) -> str: 1542- parts = [] 1543- if text: 1544- parts.append(t…
- 1329→ try: 1330→ current_data = data_processor_func(filtered_data, user_message) 1331→ except TypeError: 1332→ current_data = data_processor_func(filtered_data…
- 947- ) 948- return chat_history_children 949- 950: def start_agent_streaming(task_id: str, question: str, current_data: Any, conversation_history: List[Dict[st…
- 531- question_lower = question.lower() 532- 533: if "总结" in question or "summary" in question_lower: 534- return f"基于当前数据分析：\n\n{data_context}\n\n建议关注关键指标和异常点。…
- 950→ def start_agent_streaming(task_id: str, question: str, current_data: Any, conversation_history: List[Dict[str, Any]]): 951→ def worker(): 952→ heartbeat_r…
- 1100- temperature=DEFAULT_TEMPERATURE, 1101- max_tokens=DEFAULT_MAX_TOKENS 1102- ) 1103- 1104: def start_duplicate_check_streaming(task_id: str, question: str,…

## Representative Assistant Responses
- I'll read the relevant sections of the file in parallel to give you exact code snippets.
- Good, now I need to read the `_has_data` method, the `prefer_agent_for_query` logic, and how `data_available` is computed. Let me get more context around those…
- Now let me also read a bit before line 1286 to understand `chat_mode` values, and around `start_agent_streaming` / `start_llm_streaming` definitions to complet…
- Now let me also read the `start_agent_streaming` worker to see how `data_available` is used inside it, and what the `start_duplicate_check_streaming` definitio…
- I now have all the relevant code. Here is a precise, annotated breakdown of every piece you asked about. --- ## 1. `_is_advanced_decision_query` — Lines 1286-1…

## Mentioned Files
- `/Users/tonyorz/aianalysis/agent/core/enhanced_ai_chat_manager.py`

## Raw Source
- `/Users/tonyorz/.claude/projects/-Users-tonyorz-aianalysis/ff35778a-908b-4d63-87c6-c20eb439c8d7/subagents/agent-a8cf2e305050e22ee.jsonl`
