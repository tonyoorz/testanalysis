"""
智能SQL数据分析Agent

一个深度理解业务数据的自然语言SQL查询Agent

核心模块:
- knowledge: Schema业务语义目录
- query: NL→SQL转换和结果解释
- rules: 业务规则引擎
- core: 对话状态管理

使用示例:
    from agent import get_agent, quick_query

    # 方式1: 使用全局Agent实例
    agent = get_agent("database/local_data.db")
    session_id = agent.create_session()
    response = agent.query(session_id, "最近7天的Critical缺陷")

    # 方式2: 快速单次查询
    response = quick_query("按项目统计缺陷分布")
"""

from agent.intelligent_sql_agent import (
    IntelligentSQLAgent,
    AgentResponse,
    get_agent,
    quick_query,
)

from agent.knowledge.schema_catalog import SchemaCatalog, get_schema_catalog
from agent.query.nl_to_sql import NLToSQLConverter, nl_to_sql
from agent.query.result_explainer import QueryResultExplainer, explain_results
from agent.rules.business_rules import BusinessRuleEngine, run_all_checks
from agent.core.dialogue_state import DialogueStateManager, get_state_manager

__version__ = "1.0.0"
__author__ = "AI Assistant"

__all__ = [
    # Main Agent
    "IntelligentSQLAgent",
    "AgentResponse",
    "get_agent",
    "quick_query",

    # Core Modules
    "SchemaCatalog",
    "get_schema_catalog",
    "NLToSQLConverter",
    "nl_to_sql",
    "QueryResultExplainer",
    "explain_results",
    "BusinessRuleEngine",
    "run_all_checks",
    "DialogueStateManager",
    "get_state_manager",
]
