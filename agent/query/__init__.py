"""
查询模块 - NL到SQL转换和结果解释
"""

from agent.query.nl_to_sql import (
    NLToSQLConverter,
    SQLQuery,
    NLQuery,
    ExtractedEntity,
    QueryIntent,
    EntityExtractor,
    IntentClassifier,
    SQLGenerator,
    nl_to_sql,
    nl_query,
)

from agent.query.result_explainer import (
    QueryResultExplainer,
    ResultExplanation,
    DataInsight,
    InsightType,
    PatternDetector,
    ResultSummarizer,
    BusinessInterpreter,
    RecommendationEngine,
    explain_results,
    format_explanation,
)

__all__ = [
    # NL→SQL
    "NLToSQLConverter",
    "SQLQuery",
    "NLQuery",
    "ExtractedEntity",
    "QueryIntent",
    "EntityExtractor",
    "IntentClassifier",
    "SQLGenerator",
    "nl_to_sql",
    "nl_query",

    # Result Explainer
    "QueryResultExplainer",
    "ResultExplanation",
    "DataInsight",
    "InsightType",
    "PatternDetector",
    "ResultSummarizer",
    "BusinessInterpreter",
    "RecommendationEngine",
    "explain_results",
    "format_explanation",
]
