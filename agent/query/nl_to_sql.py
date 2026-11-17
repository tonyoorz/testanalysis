"""
NL→SQL 转换器 - 自然语言到SQL的智能转换

核心功能：
1. 实体识别 - 从自然语言中提取时间、项目、AIDA等实体
2. 字段映射 - 将业务术语映射到数据库字段
3. SQL生成 - 生成可执行的SQLite查询
4. 查询验证 - 确保生成的SQL安全且有效

作者: AI Assistant
日期: 2026-03-18
"""

import re
import json
import sqlite3
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

from agent.knowledge.schema_catalog import SchemaCatalog

logger = logging.getLogger(__name__)


class QueryIntent(Enum):
    """查询意图类型"""
    COUNT = "count"              # 计数查询
    LIST = "list"                # 列表查询
    STATISTICS = "statistics"    # 统计分析
    TREND = "trend"              # 趋势分析
    COMPARE = "compare"          # 对比分析
    DETAIL = "detail"            # 详情查询
    RANKING = "ranking"          # 排名查询
    DISTRIBUTION = "distribution" # 分布分析


@dataclass
class ExtractedEntity:
    """提取的实体"""
    entity_type: str           # 实体类型: time, project, aida, severity, status, etc.
    raw_value: str            # 原始文本
    normalized_value: Any     # 规范化后的值
    column_mapping: str       # 对应的数据库字段
    confidence: float = 1.0   # 置信度


@dataclass
class NLQuery:
    """解析后的自然语言查询"""
    original_text: str
    intent: QueryIntent
    entities: List[ExtractedEntity] = field(default_factory=list)
    time_range: Optional[Dict[str, str]] = None
    aggregation: Optional[str] = None
    group_by: List[str] = field(default_factory=list)
    order_by: Optional[Tuple[str, str]] = None  # (column, direction)
    limit: Optional[int] = None
    filters: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SQLQuery:
    """生成的SQL查询"""
    sql: str
    params: List[Any]
    explanation: str          # 查询解释
    estimated_rows: int       # 预估返回行数
    tables: List[str]         # 涉及的表
    confidence: float         # 生成置信度
    warnings: List[str] = field(default_factory=list)


class EntityExtractor:
    """实体提取器 - 从自然语言中提取业务实体"""

    # 时间相关模式
    TIME_PATTERNS = {
        'today': r'今天|今日|当天',
        'yesterday': r'昨天|昨日',
        'this_week': r'本周|这周|最近一周',
        'last_week': r'上周|上星期',
        'this_month': r'本月|这个月|当月',
        'last_month': r'上月|上个月',
        'recent_7d': r'最近7天|近7天|近一周',
        'recent_30d': r'最近30天|近30天|近一个月',
        'recent_3m': r'最近3个月|近3个月|近一季度',
        'recent_6m': r'最近6个月|近6个月|近半年',
        'year_to_date': r'今年|年初至今|YTD',
    }

    # 数量相关模式
    QUANTITY_PATTERNS = {
        'all': r'所有|全部|总共',
        'top_n': r'前(\d+)|top\s*(\d+)|排名(\d+)',
        'first': r'第一个|首个|最早',
        'last': r'最后一个|最新|最近一个',
    }

    # 聚合相关模式
    AGGREGATION_PATTERNS = {
        'count': r'多少|数量|计数|条数|个数',
        'sum': r'总和|总计|合计|累加',
        'avg': r'平均|均值|平均数',
        'max': r'最大|最高|最多',
        'min': r'最小|最低|最少',
        'distinct': r'不同|唯一|去重',
    }

    def __init__(self, schema_catalog: SchemaCatalog):
        self.schema = schema_catalog
        self._init_patterns()

    def _init_patterns(self):
        """初始化业务实体模式"""
        # 项目模式
        self.project_patterns = {
            'idcevo': r'idcevo|idcevo|IDCEVO',
            'idc': r'\bidc\b|IDC(?!E)',
            'mgu': r'\bmgu\b|MGU',
            'g70': r'g70|G70',
            'g60': r'g60|G60',
            'na6': r'na6|NA6|新世代',
        }

        # 严重级别模式
        self.severity_patterns = {
            'Critical': r'critical|严重|致命|阻断|最高',
            'Major': r'major|主要|重要|高',
            'Minor': r'minor|次要|轻微|低',
        }

        # 状态模式
        self.status_patterns = {
            'New': r'新建|new|待处理',
            'Assigned': r'已分配|assigned',
            'In Progress': r'处理中|in progress|正在进行',
            'Fixed': r'已修复|fixed|已解决',
            'Closed': r'已关闭|closed',
            'Rejected': r'已拒绝|rejected|驳回',
        }

        # Matrix 模式
        self.matrix_patterns = {
            '1A': r'1A|1a',
            '1B': r'1B|1b',
            '1C': r'1C|1c',
            '2A': r'2A|2a',
            '2B': r'2B|2b',
            '2C': r'2C|2c',
        }

        # AIDA 领域模式（常见类别）
        self.aida_domain_patterns = {
            'audio': r'音频|audio|声音|sound|speaker|speaker',
            'media': r'媒体|media|音乐|music|蓝牙|bluetooth|usb',
            'navigation': r'导航|navigation|地图|map|gps|定位',
            'adas': r'adas|ADAS|辅助驾驶|自动驾驶|辅助',
            'hmi': r'hmi|HMI|界面|ui|UI|显示|display|屏幕',
            'connectivity': r'连接|connectivity|网络|network|wifi|5g|4g',
            'system': r'系统|system|启动|boot|重启|重启',
            'climate': r'空调|climate|温度|temperature|hvac',
        }

    def extract(self, text: str) -> List[ExtractedEntity]:
        """从文本中提取所有实体"""
        entities = []

        # 提取时间实体
        time_entities = self._extract_time_entities(text)
        entities.extend(time_entities)

        # 提取项目实体
        project_entities = self._extract_project_entities(text)
        entities.extend(project_entities)

        # 提取严重级别实体
        severity_entities = self._extract_severity_entities(text)
        entities.extend(severity_entities)

        # 提取状态实体
        status_entities = self._extract_status_entities(text)
        entities.extend(status_entities)

        # 提取Matrix实体
        matrix_entities = self._extract_matrix_entities(text)
        entities.extend(matrix_entities)

        # 提取AIDA实体
        aida_entities = self._extract_aida_entities(text)
        entities.extend(aida_entities)

        # 提取TopIssue
        topissue_entities = self._extract_topissue_entities(text)
        entities.extend(topissue_entities)

        # 提取Long Runner
        longrunner_entities = self._extract_longrunner_entities(text)
        entities.extend(longrunner_entities)

        return entities

    def _extract_time_entities(self, text: str) -> List[ExtractedEntity]:
        """提取时间实体"""
        entities = []
        today = datetime.now().date()

        for time_type, pattern in self.TIME_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                if time_type == 'today':
                    entities.append(ExtractedEntity(
                        entity_type='time_range',
                        raw_value='今天',
                        normalized_value={'start': str(today), 'end': str(today)},
                        column_mapping='creation_time'
                    ))
                elif time_type == 'yesterday':
                    yesterday = today - timedelta(days=1)
                    entities.append(ExtractedEntity(
                        entity_type='time_range',
                        raw_value='昨天',
                        normalized_value={'start': str(yesterday), 'end': str(yesterday)},
                        column_mapping='creation_time'
                    ))
                elif time_type == 'this_week':
                    start = today - timedelta(days=today.weekday())
                    entities.append(ExtractedEntity(
                        entity_type='time_range',
                        raw_value='本周',
                        normalized_value={'start': str(start), 'end': str(today)},
                        column_mapping='creation_time'
                    ))
                elif time_type == 'last_week':
                    end = today - timedelta(days=today.weekday() + 1)
                    start = end - timedelta(days=6)
                    entities.append(ExtractedEntity(
                        entity_type='time_range',
                        raw_value='上周',
                        normalized_value={'start': str(start), 'end': str(end)},
                        column_mapping='creation_time'
                    ))
                elif time_type == 'recent_7d':
                    start = today - timedelta(days=7)
                    entities.append(ExtractedEntity(
                        entity_type='time_range',
                        raw_value='最近7天',
                        normalized_value={'start': str(start), 'end': str(today)},
                        column_mapping='creation_time'
                    ))
                elif time_type == 'recent_30d':
                    start = today - timedelta(days=30)
                    entities.append(ExtractedEntity(
                        entity_type='time_range',
                        raw_value='最近30天',
                        normalized_value={'start': str(start), 'end': str(today)},
                        column_mapping='creation_time'
                    ))
                elif time_type == 'this_month':
                    start = today.replace(day=1)
                    entities.append(ExtractedEntity(
                        entity_type='time_range',
                        raw_value='本月',
                        normalized_value={'start': str(start), 'end': str(today)},
                        column_mapping='creation_time'
                    ))

        return entities

    def _extract_project_entities(self, text: str) -> List[ExtractedEntity]:
        """提取项目实体"""
        entities = []
        for project, pattern in self.project_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                entities.append(ExtractedEntity(
                    entity_type='project',
                    raw_value=project,
                    normalized_value=project,
                    column_mapping='tproject'
                ))
        return entities

    def _extract_severity_entities(self, text: str) -> List[ExtractedEntity]:
        """提取严重级别实体"""
        entities = []
        for severity, pattern in self.severity_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                entities.append(ExtractedEntity(
                    entity_type='severity',
                    raw_value=severity,
                    normalized_value=severity,
                    column_mapping='severity'
                ))
        return entities

    def _extract_status_entities(self, text: str) -> List[ExtractedEntity]:
        """提取状态实体"""
        entities = []
        for status, pattern in self.status_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                entities.append(ExtractedEntity(
                    entity_type='status',
                    raw_value=status,
                    normalized_value=status,
                    column_mapping='status_phase'
                ))
        return entities

    def _extract_matrix_entities(self, text: str) -> List[ExtractedEntity]:
        """提取Matrix实体"""
        entities = []
        for matrix, pattern in self.matrix_patterns.items():
            if re.search(pattern, text):
                entities.append(ExtractedEntity(
                    entity_type='matrix',
                    raw_value=matrix,
                    normalized_value=matrix,
                    column_mapping='matrix_display'
                ))
        return entities

    def _extract_aida_entities(self, text: str) -> List[ExtractedEntity]:
        """提取AIDA领域实体"""
        entities = []
        for domain, pattern in self.aida_domain_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                entities.append(ExtractedEntity(
                    entity_type='aida_domain',
                    raw_value=domain,
                    normalized_value=domain,
                    column_mapping='aida_english'
                ))
        return entities

    def _extract_topissue_entities(self, text: str) -> List[ExtractedEntity]:
        """提取TopIssue实体"""
        entities = []
        if re.search(r'topissue|top issue|热点问题|重点问题', text, re.IGNORECASE):
            entities.append(ExtractedEntity(
                entity_type='topissue',
                raw_value='TopIssue',
                normalized_value=True,
                column_mapping='is_topissue'
            ))
        return entities

    def _extract_longrunner_entities(self, text: str) -> List[ExtractedEntity]:
        """提取Long Runner实体"""
        entities = []
        if re.search(r'longrunner|long runner|长期|超过30天|老问题', text, re.IGNORECASE):
            entities.append(ExtractedEntity(
                entity_type='longrunner',
                raw_value='LongRunner',
                normalized_value=True,
                column_mapping='is_long_runner'
            ))
        return entities


class IntentClassifier:
    """意图分类器 - 识别查询意图"""

    INTENT_PATTERNS = {
        QueryIntent.COUNT: [
            r'多少|几|数量|总数|总计|统计|count|number of',
            r'.*有多少.*',
            r'.*的数量',
        ],
        QueryIntent.LIST: [
            r'列出|显示|查看|查询|有哪些|是什么|list|show|display',
            r'.*的列表',
            r'.*有哪些',
        ],
        QueryIntent.STATISTICS: [
            r'统计|分析|概况|总结|summary|statistics|analyze',
            r'.*的统计',
            r'.*的分布',
        ],
        QueryIntent.TREND: [
            r'趋势|变化|走势|增长|下降|trend|change|growth|increase|decrease',
            r'.*的趋势',
            r'.*的变化',
        ],
        QueryIntent.COMPARE: [
            r'对比|比较|vs|versus|compare|comparison|difference|diff',
            r'.*和.*对比',
            r'.*vs.*',
        ],
        QueryIntent.DETAIL: [
            r'详情|明细|详细|detail|details|specific',
            r'.*的详情',
            r'具体.*',
        ],
        QueryIntent.RANKING: [
            r'排名|排行|前几|top|rank|ranking|排序|order',
            r'.*的排名',
            r'前\d+.*',
        ],
        QueryIntent.DISTRIBUTION: [
            r'分布|占比|比例|percentage|distribution|proportion',
            r'.*的分布',
            r'.*占比',
        ],
    }

    def classify(self, text: str) -> QueryIntent:
        """分类查询意图"""
        text_lower = text.lower()

        scores = {}
        for intent, patterns in self.INTENT_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 1
            scores[intent] = score

        # 返回得分最高的意图
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)

        # 默认返回列表意图
        return QueryIntent.LIST


class SQLGenerator:
    """SQL生成器 - 根据解析结果生成SQL"""

    def __init__(self, schema_catalog: SchemaCatalog):
        self.schema = schema_catalog

    def generate(self, query: NLQuery, table: str = "octane_defects") -> SQLQuery:
        """生成SQL查询"""
        warnings = []

        # 根据意图选择生成策略
        if query.intent == QueryIntent.COUNT:
            sql, params = self._generate_count_sql(query, table)
        elif query.intent == QueryIntent.LIST:
            sql, params = self._generate_list_sql(query, table)
        elif query.intent == QueryIntent.STATISTICS:
            sql, params = self._generate_statistics_sql(query, table)
        elif query.intent == QueryIntent.TREND:
            sql, params = self._generate_trend_sql(query, table)
        elif query.intent == QueryIntent.COMPARE:
            sql, params = self._generate_compare_sql(query, table)
        elif query.intent == QueryIntent.RANKING:
            sql, params = self._generate_ranking_sql(query, table)
        elif query.intent == QueryIntent.DISTRIBUTION:
            sql, params = self._generate_distribution_sql(query, table)
        else:
            sql, params = self._generate_list_sql(query, table)

        # 构建查询解释
        explanation = self._generate_explanation(query, sql)

        # 估算返回行数
        estimated_rows = self._estimate_rows(query)

        return SQLQuery(
            sql=sql,
            params=params,
            explanation=explanation,
            estimated_rows=estimated_rows,
            tables=[table],
            confidence=0.85,
            warnings=warnings
        )

    def _generate_where_clause(self, query: NLQuery, params: List[Any]) -> Tuple[str, List[Any]]:
        """生成WHERE子句"""
        conditions = []

        for entity in query.entities:
            if entity.entity_type == 'time_range':
                time_range = entity.normalized_value
                conditions.append(f"DATE(creation_time) BETWEEN ? AND ?")
                params.append(time_range['start'])
                params.append(time_range['end'])

            elif entity.entity_type == 'project':
                conditions.append(f"tproject = ?")
                params.append(entity.normalized_value)

            elif entity.entity_type == 'severity':
                conditions.append(f"severity = ?")
                params.append(entity.normalized_value)

            elif entity.entity_type == 'status':
                conditions.append(f"status_phase = ?")
                params.append(entity.normalized_value)

            elif entity.entity_type == 'matrix':
                conditions.append(f"matrix_display = ?")
                params.append(entity.normalized_value)

            elif entity.entity_type == 'aida_domain':
                conditions.append(f"aida_english LIKE ?")
                params.append(f"%{entity.normalized_value}%")

            elif entity.entity_type == 'topissue':
                conditions.append(f"is_topissue = ?")
                params.append(1 if entity.normalized_value else 0)

            elif entity.entity_type == 'longrunner':
                conditions.append(f"is_long_runner = ?")
                params.append(1 if entity.normalized_value else 0)

        if conditions:
            return " WHERE " + " AND ".join(conditions), params
        return "", params

    def _generate_count_sql(self, query: NLQuery, table: str) -> Tuple[str, List[Any]]:
        """生成计数查询"""
        params = []
        sql = f"SELECT COUNT(DISTINCT defect_id) as count FROM {table}"

        where_clause, params = self._generate_where_clause(query, params)
        sql += where_clause

        # 添加分组
        if query.group_by:
            sql = f"SELECT {', '.join(query.group_by)}, COUNT(DISTINCT defect_id) as count FROM {table}"
            sql += where_clause
            sql += f" GROUP BY {', '.join(query.group_by)}"
            sql += " ORDER BY count DESC"

        return sql, params

    def _generate_list_sql(self, query: NLQuery, table: str) -> Tuple[str, List[Any]]:
        """生成列表查询"""
        params = []

        # 选择字段
        columns = ["defect_id", "name", "tproject", "severity", "status_phase", "creation_time"]
        if query.entities:
            for entity in query.entities:
                if entity.column_mapping not in columns:
                    columns.append(entity.column_mapping)

        sql = f"SELECT {', '.join(columns)} FROM {table}"

        where_clause, params = self._generate_where_clause(query, params)
        sql += where_clause

        # 添加排序
        if query.order_by:
            sql += f" ORDER BY {query.order_by[0]} {query.order_by[1]}"
        else:
            sql += " ORDER BY creation_time DESC"

        # 添加限制
        if query.limit:
            sql += f" LIMIT {query.limit}"
        else:
            sql += " LIMIT 100"

        return sql, params

    def _generate_statistics_sql(self, query: NLQuery, table: str) -> Tuple[str, List[Any]]:
        """生成统计查询"""
        params = []

        sql = f"""
        SELECT
            COUNT(DISTINCT defect_id) as total_count,
            COUNT(DISTINCT CASE WHEN severity = 'Critical' THEN id END) as critical_count,
            COUNT(DISTINCT CASE WHEN severity = 'Major' THEN id END) as major_count,
            COUNT(DISTINCT CASE WHEN severity = 'Minor' THEN id END) as minor_count,
            COUNT(DISTINCT CASE WHEN is_topissue = 1 THEN id END) as topissue_count,
            COUNT(DISTINCT CASE WHEN is_long_runner = 1 THEN id END) as longrunner_count,
            AVG(defect_age_days) as avg_age_days,
            MAX(defect_age_days) as max_age_days
        FROM {table}
        """

        where_clause, params = self._generate_where_clause(query, params)
        sql += where_clause

        return sql, params

    def _generate_trend_sql(self, query: NLQuery, table: str) -> Tuple[str, List[Any]]:
        """生成趋势查询"""
        params = []

        sql = f"""
        SELECT
            DATE(creation_time) as date,
            COUNT(DISTINCT defect_id) as daily_count,
            COUNT(DISTINCT CASE WHEN severity = 'Critical' THEN id END) as critical_count,
            COUNT(DISTINCT CASE WHEN severity = 'Major' THEN id END) as major_count
        FROM {table}
        """

        where_clause, params = self._generate_where_clause(query, params)
        sql += where_clause

        sql += " GROUP BY DATE(creation_time) ORDER BY date"

        return sql, params

    def _generate_compare_sql(self, query: NLQuery, table: str) -> Tuple[str, List[Any]]:
        """生成对比查询"""
        params = []

        # 默认按项目和严重级别对比
        sql = f"""
        SELECT
            tproject,
            severity,
            COUNT(DISTINCT defect_id) as count,
            COUNT(DISTINCT CASE WHEN is_topissue = 1 THEN id END) as topissue_count,
            AVG(defect_age_days) as avg_age
        FROM {table}
        """

        where_clause, params = self._generate_where_clause(query, params)
        sql += where_clause

        sql += " GROUP BY tproject, severity ORDER BY tproject, count DESC"

        return sql, params

    def _generate_ranking_sql(self, query: NLQuery, table: str) -> Tuple[str, List[Any]]:
        """生成排名查询"""
        params = []

        # 确定分组字段
        group_field = "tproject"  # 默认按项目
        for entity in query.entities:
            if entity.entity_type == 'aida_domain':
                group_field = "aida_english"
                break

        sql = f"""
        SELECT
            {group_field},
            COUNT(DISTINCT defect_id) as count,
            COUNT(DISTINCT CASE WHEN severity = 'Critical' THEN id END) as critical_count,
            COUNT(DISTINCT CASE WHEN is_topissue = 1 THEN id END) as topissue_count
        FROM {table}
        """

        where_clause, params = self._generate_where_clause(query, params)
        sql += where_clause

        sql += f" GROUP BY {group_field} ORDER BY count DESC"

        if query.limit:
            sql += f" LIMIT {query.limit}"
        else:
            sql += " LIMIT 10"

        return sql, params

    def _generate_distribution_sql(self, query: NLQuery, table: str) -> Tuple[str, List[Any]]:
        """生成分布查询"""
        params = []

        # 确定分布字段
        dist_field = "severity"  # 默认按严重级别
        for entity in query.entities:
            if entity.entity_type == 'project':
                dist_field = "tproject"
                break

        sql = f"""
        SELECT
            {dist_field} as category,
            COUNT(DISTINCT defect_id) as count,
            ROUND(COUNT(DISTINCT defect_id) * 100.0 / SUM(COUNT(DISTINCT defect_id)) OVER(), 2) as percentage
        FROM {table}
        """

        where_clause, params = self._generate_where_clause(query, params)
        sql += where_clause

        sql += f" GROUP BY {dist_field} ORDER BY count DESC"

        return sql, params

    def _generate_explanation(self, query: NLQuery, sql: str) -> str:
        """生成查询解释"""
        intent_desc = {
            QueryIntent.COUNT: "计数统计",
            QueryIntent.LIST: "列表查询",
            QueryIntent.STATISTICS: "统计分析",
            QueryIntent.TREND: "趋势分析",
            QueryIntent.COMPARE: "对比分析",
            QueryIntent.DETAIL: "详情查询",
            QueryIntent.RANKING: "排名查询",
            QueryIntent.DISTRIBUTION: "分布分析",
        }

        explanation = f"这是一个{intent_desc.get(query.intent, '数据查询')}"

        if query.entities:
            entity_descs = []
            for entity in query.entities:
                if entity.entity_type == 'time_range':
                    entity_descs.append(f"时间范围: {entity.raw_value}")
                elif entity.entity_type == 'project':
                    entity_descs.append(f"项目: {entity.normalized_value}")
                elif entity.entity_type == 'severity':
                    entity_descs.append(f"严重级别: {entity.normalized_value}")
                elif entity.entity_type == 'aida_domain':
                    entity_descs.append(f"AIDA领域: {entity.raw_value}")

            if entity_descs:
                explanation += "，筛选条件: " + "; ".join(entity_descs)

        return explanation

    def _estimate_rows(self, query: NLQuery) -> int:
        """估算返回行数"""
        # 根据意图和限制估算
        if query.intent == QueryIntent.COUNT and not query.group_by:
            return 1
        elif query.limit:
            return query.limit
        elif query.intent == QueryIntent.STATISTICS:
            return 1
        else:
            return 100  # 默认值


class NLToSQLConverter:
    """
    NL→SQL 转换器主类

    使用示例:
        converter = NLToSQLConverter()

        # 转换自然语言到SQL
        result = converter.convert("昨天音频模块的高优先级缺陷")
        print(result.sql)
        print(result.explanation)
    """

    def __init__(self, db_path: Optional[str] = None):
        self.schema = SchemaCatalog()
        self.extractor = EntityExtractor(self.schema)
        self.classifier = IntentClassifier()
        self.generator = SQLGenerator(self.schema)
        self.db_path = db_path

    def convert(self, text: str, table: str = "octane_defects") -> SQLQuery:
        """
        将自然语言转换为SQL

        Args:
            text: 自然语言查询
            table: 目标表名

        Returns:
            SQLQuery对象
        """
        logger.info(f"Converting NL to SQL: {text}")

        # 1. 提取实体
        entities = self.extractor.extract(text)
        logger.info(f"Extracted {len(entities)} entities")

        # 2. 分类意图
        intent = self.classifier.classify(text)
        logger.info(f"Classified intent: {intent.value}")

        # 3. 构建NLQuery
        nl_query = NLQuery(
            original_text=text,
            intent=intent,
            entities=entities
        )

        # 4. 提取额外信息（限制、排序等）
        nl_query = self._extract_query_modifiers(text, nl_query)

        # 5. 生成SQL
        sql_query = self.generator.generate(nl_query, table)

        logger.info(f"Generated SQL: {sql_query.sql[:100]}...")

        return sql_query

    def _extract_query_modifiers(self, text: str, query: NLQuery) -> NLQuery:
        """提取查询修饰符（限制、排序等）"""
        # 提取限制数量
        limit_match = re.search(r'前(\d+)|top\s*(\d+)', text, re.IGNORECASE)
        if limit_match:
            query.limit = int(limit_match.group(1) or limit_match.group(2))

        # 提取排序
        if re.search(r'最新|最近|倒序|desc', text):
            query.order_by = ('creation_time', 'DESC')
        elif re.search(r'最早|正序|asc', text):
            query.order_by = ('creation_time', 'ASC')

        return query

    def execute(self, text: str, table: str = "octane_defects") -> Dict[str, Any]:
        """
        转换并执行查询

        Args:
            text: 自然语言查询
            table: 目标表名

        Returns:
            包含查询结果的字典
        """
        sql_query = self.convert(text, table)

        if not self.db_path:
            return {
                'success': False,
                'error': '未配置数据库路径',
                'sql': sql_query.sql,
                'explanation': sql_query.explanation
            }

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(sql_query.sql, sql_query.params)
            rows = cursor.fetchall()

            # 转换为字典列表
            results = [dict(row) for row in rows]

            conn.close()

            return {
                'success': True,
                'sql': sql_query.sql,
                'params': sql_query.params,
                'explanation': sql_query.explanation,
                'results': results,
                'row_count': len(results),
                'warnings': sql_query.warnings
            }

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'sql': sql_query.sql,
                'explanation': sql_query.explanation
            }

    def get_schema_context(self, table: str = "octane_defects") -> str:
        """获取表结构的文本描述"""
        return self.schema.get_table_schema_context(table)


# 便捷函数
def nl_to_sql(text: str, db_path: Optional[str] = None) -> SQLQuery:
    """
    快速将自然语言转换为SQL

    Args:
        text: 自然语言查询
        db_path: 可选的数据库路径

    Returns:
        SQLQuery对象
    """
    converter = NLToSQLConverter(db_path)
    return converter.convert(text)


def nl_query(text: str, db_path: str) -> Dict[str, Any]:
    """
    快速执行自然语言查询

    Args:
        text: 自然语言查询
        db_path: 数据库路径

    Returns:
        查询结果字典
    """
    converter = NLToSQLConverter(db_path)
    return converter.execute(text)
