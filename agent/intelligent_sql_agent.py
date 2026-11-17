"""
智能SQL数据分析Agent - 集成所有模块的主Agent

核心功能：
1. 自然语言理解 - 将业务查询转换为SQL
2. 数据查询执行 - 执行SQL并获取结果
3. 业务规则应用 - 计算风险评分、检查SLA等
4. 结果解释生成 - 用业务语言解释结果
5. 多轮对话管理 - 维护对话上下文

使用示例：
    agent = IntelligentSQLAgent(db_path="database/local_data.db")

    # 创建会话
    session_id = agent.create_session()

    # 第一轮查询
    response1 = agent.query(session_id, "昨天音频模块的Critical缺陷")
    print(response1['summary'])
    print(response1['explanation'])

    # 跟进查询（自动继承上下文）
    response2 = agent.query(session_id, "其中有多少是TopIssue？")
    print(response2['summary'])

作者: AI Assistant
日期: 2026-03-18
"""

import json
import sqlite3
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from agent.core.dialogue_state import (
    DialogueStateManager, IntentType, get_state_manager
)
from agent.knowledge.schema_catalog import SchemaCatalog, get_schema_catalog
from agent.query.nl_to_sql import (
    NLToSQLConverter, SQLQuery, QueryIntent, nl_to_sql
)
from agent.query.result_explainer import (
    QueryResultExplainer, ResultExplanation, explain_results
)
from agent.rules.business_rules import (
    BusinessRuleEngine, RuleResult, run_all_checks
)

logger = logging.getLogger(__name__)


@dataclass
class AgentResponse:
    """Agent响应"""
    session_id: str
    query_id: str
    original_query: str
    enhanced_query: str
    sql: Optional[str]
    sql_explanation: Optional[str]
    success: bool
    summary: str
    explanation: str
    key_findings: List[str]
    insights: List[Dict[str, Any]]
    recommendations: List[str]
    rule_results: List[Dict[str, Any]]
    data: List[Dict[str, Any]]
    row_count: int
    execution_time_ms: float
    context_info: Dict[str, Any]
    suggestions: List[str]
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


class IntelligentSQLAgent:
    """
    智能SQL数据分析Agent

    这是整个系统的主入口，集成所有模块：
    - SchemaCatalog: 数据库业务语义
    - NLToSQLConverter: 自然语言转SQL
    - QueryResultExplainer: 结果解释
    - BusinessRuleEngine: 业务规则
    - DialogueStateManager: 对话状态管理
    """

    def __init__(self, db_path: str = "database/local_data.db"):
        """
        初始化Agent

        Args:
            db_path: SQLite数据库路径
        """
        self.db_path = db_path

        # 初始化各个模块
        self.schema = get_schema_catalog()
        self.nl_converter = NLToSQLConverter(db_path)
        self.result_explainer = QueryResultExplainer()
        self.rule_engine = BusinessRuleEngine()
        self.state_manager = get_state_manager()

        # 验证数据库连接
        self._verify_db_connection()

        logger.info(f"IntelligentSQLAgent initialized with db: {db_path}")

    def _verify_db_connection(self):
        """验证数据库连接"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()

            if 'octane_defects' not in tables:
                logger.warning(f"octane_defects table not found in {self.db_path}")

            logger.info(f"Database verified. Found {len(tables)} tables.")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")

    def create_session(self) -> str:
        """
        创建新的对话会话

        Returns:
            会话ID
        """
        state = self.state_manager.create_session()
        logger.info(f"Created new session: {state.session_id}")
        return state.session_id

    def close_session(self, session_id: str):
        """
        关闭对话会话

        Args:
            session_id: 会话ID
        """
        self.state_manager.close_session(session_id)
        logger.info(f"Closed session: {session_id}")

    def query(self, session_id: str, text: str, execute_rules: bool = True) -> AgentResponse:
        """
        执行自然语言查询

        Args:
            session_id: 会话ID
            text: 自然语言查询
            execute_rules: 是否执行业务规则

        Returns:
            AgentResponse对象
        """
        start_time = datetime.now()

        # 增强查询（继承上下文）
        enhanced_query = self.state_manager.enhance_query(session_id, text)

        # 获取上下文
        context = self.state_manager.get_context(session_id)

        try:
            # 1. 自然语言转SQL
            sql_query = self.nl_converter.convert(enhanced_query)

            # 2. 执行SQL查询
            data, execution_success = self._execute_sql(sql_query)

            # 3. 记录查询到对话状态
            query_context = self.state_manager.add_query(
                session_id,
                query=enhanced_query,
                sql=sql_query.sql,
                results_summary=f"{len(data)} rows" if data else "0 rows"
            )

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            if not execution_success:
                return self._error_response(
                    session_id, query_context.query_id, text, enhanced_query,
                    sql_query, "SQL执行失败", execution_time, context
                )

            # 4. 解释查询结果
            explanation = self.result_explainer.explain(data, {
                'query': text,
                'sql': sql_query.sql,
                'query_type': sql_query.explanation
            })

            # 5. 执行业务规则（如果启用）
            rule_results = []
            if execute_rules and data:
                rule_results = self._apply_business_rules(data)

            # 6. 获取后续建议
            suggestions = self.state_manager.get_suggestions(session_id)

            # 7. 构建响应
            return AgentResponse(
                session_id=session_id,
                query_id=query_context.query_id,
                original_query=text,
                enhanced_query=enhanced_query,
                sql=sql_query.sql,
                sql_explanation=sql_query.explanation,
                success=True,
                summary=explanation.summary,
                explanation=self.result_explainer.format_for_display(explanation),
                key_findings=explanation.key_findings,
                insights=[{
                    'type': i.insight_type.value,
                    'title': i.title,
                    'description': i.description,
                    'severity': i.severity,
                    'recommendation': i.recommendation
                } for i in explanation.insights],
                recommendations=explanation.recommendations,
                rule_results=rule_results,
                data=data[:50],  # 限制返回数据量
                row_count=len(data),
                execution_time_ms=execution_time,
                context_info=context,
                suggestions=suggestions,
                warnings=sql_query.warnings
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"Query failed: {e}", exc_info=True)
            return self._error_response(
                session_id, "", text, enhanced_query, None,
                str(e), execution_time, context
            )

    def _execute_sql(self, sql_query: SQLQuery) -> tuple[List[Dict], bool]:
        """
        执行SQL查询

        Args:
            sql_query: SQL查询对象

        Returns:
            (数据列表, 是否成功)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(sql_query.sql, sql_query.params)
            rows = cursor.fetchall()

            data = [dict(row) for row in rows]
            conn.close()

            return data, True

        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            return [], False

    def _apply_business_rules(self, data: List[Dict]) -> List[Dict[str, Any]]:
        """
        对数据应用业务规则

        Args:
            data: 查询结果数据

        Returns:
            规则执行结果列表
        """
        results = []

        # 对每行数据执行规则
        for row in data[:10]:  # 限制处理数量
            rule_results = self.rule_engine.execute_all(row)
            for rule_result in rule_results:
                results.append({
                    'rule': rule_result.rule_name,
                    'passed': rule_result.passed,
                    'score': rule_result.score,
                    'level': rule_result.level,
                    'message': rule_result.message,
                    'recommendations': rule_result.recommendations
                })

        return results

    def _error_response(self, session_id: str, query_id: str, original: str,
                        enhanced: str, sql_query: Optional[SQLQuery],
                        error: str, time_ms: float, context: Dict) -> AgentResponse:
        """构建错误响应"""
        return AgentResponse(
            session_id=session_id,
            query_id=query_id,
            original_query=original,
            enhanced_query=enhanced,
            sql=sql_query.sql if sql_query else None,
            sql_explanation=sql_query.explanation if sql_query else None,
            success=False,
            summary="查询执行失败",
            explanation=f"错误: {error}",
            key_findings=[],
            insights=[],
            recommendations=[],
            rule_results=[],
            data=[],
            row_count=0,
            execution_time_ms=time_ms,
            context_info=context,
            suggestions=[],
            error=error,
            warnings=[]
        )

    def get_schema_info(self, table_name: str = "octane_defects") -> str:
        """
        获取表的Schema信息

        Args:
            table_name: 表名

        Returns:
            Schema描述文本
        """
        return self.schema.get_table_schema_context(table_name)

    def explain_sql(self, sql: str) -> str:
        """
        解释SQL查询的业务含义

        Args:
            sql: SQL查询语句

        Returns:
            业务解释
        """
        # 简单的SQL解释（可以扩展）
        if "COUNT" in sql.upper():
            return "这是一个计数查询，用于统计符合条件的记录数量"
        elif "GROUP BY" in sql.upper():
            return "这是一个分组统计查询，用于按特定字段分组统计"
        elif "ORDER BY" in sql.upper():
            return "这是一个排序查询，结果会按指定字段排序"
        else:
            return "这是一个数据查询，用于获取符合条件的数据记录"

    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话信息

        Args:
            session_id: 会话ID

        Returns:
            会话信息字典
        """
        return self.state_manager.get_context(session_id)

    def get_stats(self) -> Dict[str, Any]:
        """
        获取Agent统计信息

        Returns:
            统计信息字典
        """
        session_stats = self.state_manager.get_session_stats()

        return {
            'sessions': session_stats,
            'database': self.db_path,
            'tables': list(self.schema.tables.keys()),
            'supported_intents': [i.value for i in QueryIntent],
        }


# 便捷函数
_global_agent: Optional[IntelligentSQLAgent] = None


def get_agent(db_path: str = "database/local_data.db") -> IntelligentSQLAgent:
    """
    获取全局Agent实例

    Args:
        db_path: 数据库路径

    Returns:
        IntelligentSQLAgent实例
    """
    global _global_agent
    if _global_agent is None:
        _global_agent = IntelligentSQLAgent(db_path)
    return _global_agent


def quick_query(text: str, db_path: str = "database/local_data.db") -> AgentResponse:
    """
    快速查询（自动创建临时会话）

    Args:
        text: 自然语言查询
        db_path: 数据库路径

    Returns:
        Agent响应
    """
    agent = get_agent(db_path)
    session_id = agent.create_session()
    response = agent.query(session_id, text)
    agent.close_session(session_id)
    return response


if __name__ == "__main__":
    # 测试代码
    import sys

    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 测试Agent
    print("=" * 60)
    print("智能SQL数据分析Agent测试")
    print("=" * 60)

    # 检查数据库路径
    db_path = "database/local_data.db"
    if not Path(db_path).exists():
        print(f"\n⚠️ 数据库文件不存在: {db_path}")
        print("请确保数据库文件存在后再运行测试")
        sys.exit(1)

    try:
        # 创建Agent
        agent = IntelligentSQLAgent(db_path)

        # 获取统计信息
        print("\n📊 Agent信息:")
        stats = agent.get_stats()
        print(f"  数据库: {stats['database']}")
        print(f"  表: {', '.join(stats['tables'])}")
        print(f"  支持的意图: {', '.join(stats['supported_intents'])}")

        # 创建会话
        session_id = agent.create_session()
        print(f"\n✅ 创建会话: {session_id}")

        # 测试查询
        test_queries = [
            "最近7天的缺陷数量",
            "按项目统计缺陷分布",
        ]

        for query in test_queries:
            print(f"\n🔍 查询: {query}")
            print("-" * 40)

            response = agent.query(session_id, query)

            print(f"✓ 成功: {response.success}")
            print(f"✓ 摘要: {response.summary}")
            print(f"✓ 行数: {response.row_count}")
            print(f"✓ 耗时: {response.execution_time_ms:.1f}ms")

            if response.error:
                print(f"✗ 错误: {response.error}")

            if response.recommendations:
                print(f"✓ 建议:")
                for rec in response.recommendations[:3]:
                    print(f"    - {rec}")

        # 关闭会话
        agent.close_session(session_id)
        print(f"\n✅ 关闭会话: {session_id}")

        print("\n✅ 测试完成!")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
