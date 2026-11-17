"""
查询结果解释器 - 将SQL查询结果转换为业务语言

核心功能：
1. 结果摘要 - 生成查询结果的概要描述
2. 洞察发现 - 从数据中识别关键模式和异常
3. 业务解读 - 将技术数据转换为业务语言
4. 建议生成 - 基于数据提供可执行的建议

作者: AI Assistant
日期: 2026-03-18
"""

import json
import re
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import statistics
import logging

from agent.knowledge.schema_catalog import SchemaCatalog

logger = logging.getLogger(__name__)


class InsightType(Enum):
    """洞察类型"""
    TREND_UP = "trend_up"              # 上升趋势
    TREND_DOWN = "trend_down"          # 下降趋势
    HIGH_VOLUME = "high_volume"        # 高数量
    LOW_VOLUME = "low_volume"          # 低数量
    ANOMALY = "anomaly"                # 异常值
    CONCENTRATION = "concentration"    # 集中度
    RISK = "risk"                      # 风险点
    OPPORTUNITY = "opportunity"        # 机会点
    PATTERN = "pattern"                # 模式发现


@dataclass
class DataInsight:
    """数据洞察"""
    insight_type: InsightType
    title: str
    description: str
    severity: str  # high, medium, low
    data_evidence: Dict[str, Any]
    recommendation: Optional[str] = None


@dataclass
class ResultExplanation:
    """结果解释"""
    summary: str                           # 一句话摘要
    detailed_description: str              # 详细描述
    key_findings: List[str]                # 关键发现
    insights: List[DataInsight]            # 深度洞察
    recommendations: List[str]             # 建议
    data_quality_notes: List[str]          # 数据质量说明
    confidence: float = 1.0                # 置信度


class PatternDetector:
    """模式检测器 - 从数据中识别模式"""

    def detect_trends(self, data: List[Dict], time_field: str = 'date',
                      value_field: str = 'count') -> Optional[DataInsight]:
        """检测趋势"""
        if len(data) < 3:
            return None

        values = [row.get(value_field, 0) for row in data if row.get(value_field)]
        if len(values) < 3:
            return None

        # 简单线性趋势检测
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]

        if not first_half or not second_half:
            return None

        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)

        if first_avg == 0:
            change_pct = 100 if second_avg > 0 else 0
        else:
            change_pct = ((second_avg - first_avg) / first_avg) * 100

        if abs(change_pct) < 10:
            return None

        if change_pct > 0:
            return DataInsight(
                insight_type=InsightType.TREND_UP,
                title="上升趋势",
                description=f"数据呈现上升趋势，后半段相比前半段增长 {change_pct:.1f}%",
                severity="medium",
                data_evidence={
                    'first_period_avg': first_avg,
                    'second_period_avg': second_avg,
                    'change_percentage': change_pct
                }
            )
        else:
            return DataInsight(
                insight_type=InsightType.TREND_DOWN,
                title="下降趋势",
                description=f"数据呈现下降趋势，后半段相比前半段下降 {abs(change_pct):.1f}%",
                severity="medium",
                data_evidence={
                    'first_period_avg': first_avg,
                    'second_period_avg': second_avg,
                    'change_percentage': change_pct
                }
            )

    def detect_anomalies(self, data: List[Dict], value_field: str = 'count',
                         threshold: float = 2.0) -> List[DataInsight]:
        """检测异常值"""
        insights = []

        values = [row.get(value_field, 0) for row in data if row.get(value_field) is not None]
        if len(values) < 5:
            return insights

        mean = statistics.mean(values)
        std = statistics.stdev(values) if len(values) > 1 else 0

        if std == 0:
            return insights

        for row in data:
            value = row.get(value_field)
            if value is None:
                continue

            z_score = abs(value - mean) / std
            if z_score > threshold:
                insights.append(DataInsight(
                    insight_type=InsightType.ANOMALY,
                    title="异常值检测",
                    description=f"发现异常值: {value} (偏离平均值 {z_score:.1f} 个标准差)",
                    severity="high" if z_score > 3 else "medium",
                    data_evidence={
                        'value': value,
                        'mean': mean,
                        'z_score': z_score,
                        'row': row
                    }
                ))

        return insights

    def detect_concentration(self, data: List[Dict], category_field: str,
                             value_field: str = 'count') -> Optional[DataInsight]:
        """检测数据集中度"""
        if len(data) < 3:
            return None

        values = [row.get(value_field, 0) for row in data if row.get(value_field)]
        if not values:
            return None

        total = sum(values)
        if total == 0:
            return None

        # 计算前3项占比
        sorted_values = sorted(values, reverse=True)
        top3_sum = sum(sorted_values[:3])
        top3_ratio = (top3_sum / total) * 100

        if top3_ratio > 70:
            top_items = sorted(data, key=lambda x: x.get(value_field, 0), reverse=True)[:3]
            item_names = [item.get(category_field, 'Unknown') for item in top_items]

            return DataInsight(
                insight_type=InsightType.CONCENTRATION,
                title="数据高度集中",
                description=f"前3项占总量的 {top3_ratio:.1f}%，存在明显集中趋势",
                severity="high" if top3_ratio > 80 else "medium",
                data_evidence={
                    'top3_ratio': top3_ratio,
                    'top_items': item_names,
                    'total_items': len(data)
                },
                recommendation=f"建议重点关注: {', '.join(item_names)}"
            )

        return None

    def detect_risks(self, data: List[Dict]) -> List[DataInsight]:
        """检测风险点"""
        insights = []

        for row in data:
            # 检测Critical级别缺陷
            if 'critical_count' in row and row['critical_count'] > 0:
                insights.append(DataInsight(
                    insight_type=InsightType.RISK,
                    title="Critical级别缺陷",
                    description=f"发现 {row['critical_count']} 个Critical级别缺陷",
                    severity="high",
                    data_evidence=row,
                    recommendation="建议立即处理Critical级别缺陷"
                ))

            # 检测TopIssue
            if 'topissue_count' in row and row.get('topissue_count', 0) > 0:
                insights.append(DataInsight(
                    insight_type=InsightType.RISK,
                    title="TopIssue热点问题",
                    description=f"包含 {row['topissue_count']} 个TopIssue",
                    severity="high",
                    data_evidence=row,
                    recommendation="TopIssue需要优先关注和处理"
                ))

            # 检测Long Runner
            if 'longrunner_count' in row and row.get('longrunner_count', 0) > 0:
                insights.append(DataInsight(
                    insight_type=InsightType.RISK,
                    title="长期未关闭缺陷",
                    description=f"存在 {row['longrunner_count']} 个超过30天未关闭的缺陷",
                    severity="medium",
                    data_evidence=row,
                    recommendation="建议分析长期未关闭原因，推动问题解决"
                ))

            # 检测高平均年龄
            if 'avg_age_days' in row and row.get('avg_age_days', 0) > 30:
                insights.append(DataInsight(
                    insight_type=InsightType.RISK,
                    title="缺陷处理周期长",
                    description=f"平均处理周期 {row['avg_age_days']:.1f} 天",
                    severity="medium",
                    data_evidence=row,
                    recommendation="建议优化缺陷处理流程，缩短解决周期"
                ))

        return insights


class ResultSummarizer:
    """结果摘要生成器"""

    def __init__(self):
        self.schema = SchemaCatalog()

    def summarize(self, data: List[Dict], query_type: str = 'list') -> str:
        """生成结果摘要"""
        if not data:
            return "未找到匹配的数据"

        row_count = len(data)

        if query_type == 'count':
            return self._summarize_count(data)
        elif query_type == 'statistics':
            return self._summarize_statistics(data)
        elif query_type == 'trend':
            return self._summarize_trend(data)
        elif query_type == 'compare':
            return self._summarize_compare(data)
        elif query_type == 'ranking':
            return self._summarize_ranking(data)
        elif query_type == 'distribution':
            return self._summarize_distribution(data)
        else:
            return f"查询返回 {row_count} 条记录"

    def _summarize_count(self, data: List[Dict]) -> str:
        """摘要计数结果"""
        if len(data) == 1:
            count = data[0].get('count', 0)
            return f"总计 {count} 条记录"
        else:
            total = sum(row.get('count', 0) for row in data)
            return f"共 {len(data)} 个分组，总计 {total} 条记录"

    def _summarize_statistics(self, data: List[Dict]) -> str:
        """摘要统计结果"""
        if not data:
            return "无统计数据"

        stats = data[0]
        total = stats.get('total_count', 0)
        critical = stats.get('critical_count', 0)
        major = stats.get('major_count', 0)
        topissue = stats.get('topissue_count', 0)

        parts = [f"总缺陷数: {total}"]
        if critical > 0:
            parts.append(f"Critical级别: {critical} ({critical/total*100:.1f}%)")
        if major > 0:
            parts.append(f"Major级别: {major} ({major/total*100:.1f}%)")
        if topissue > 0:
            parts.append(f"TopIssue: {topissue}")

        return "；".join(parts)

    def _summarize_trend(self, data: List[Dict]) -> str:
        """摘要趋势结果"""
        if len(data) < 2:
            return "数据点不足，无法分析趋势"

        first = data[0].get('daily_count', 0)
        last = data[-1].get('daily_count', 0)
        total = sum(row.get('daily_count', 0) for row in data)

        if first == 0:
            change = "N/A"
        else:
            change = f"{((last - first) / first * 100):+.1f}%"

        return f"时间段内共 {total} 个缺陷，从 {first} 变化到 {last} ({change})"

    def _summarize_compare(self, data: List[Dict]) -> str:
        """摘要对比结果"""
        if not data:
            return "无对比数据"

        # 按项目分组统计
        projects = {}
        for row in data:
            project = row.get('tproject', 'Unknown')
            count = row.get('count', 0)
            projects[project] = projects.get(project, 0) + count

        if not projects:
            return "无项目数据"

        sorted_projects = sorted(projects.items(), key=lambda x: x[1], reverse=True)
        top_project = sorted_projects[0]

        return f"共 {len(projects)} 个项目，{top_project[0]} 数量最多 ({top_project[1]} 个)"

    def _summarize_ranking(self, data: List[Dict]) -> str:
        """摘要排名结果"""
        if not data:
            return "无排名数据"

        top = data[0] if data else {}
        name = top.get('tproject') or top.get('aida_english') or 'Unknown'
        count = top.get('count', 0)

        return f"排名第一: {name} ({count} 个)"

    def _summarize_distribution(self, data: List[Dict]) -> str:
        """摘要分布结果"""
        if not data:
            return "无分布数据"

        # 找最大占比
        max_item = max(data, key=lambda x: x.get('percentage', 0))
        category = max_item.get('category', 'Unknown')
        percentage = max_item.get('percentage', 0)

        return f"共 {len(data)} 个类别，{category} 占比最高 ({percentage}%)"


class BusinessInterpreter:
    """业务解释器 - 将技术数据转换为业务语言"""

    # 严重级别业务解读
    SEVERITY_INTERPRETATION = {
        'Critical': {'level': '阻断级', 'action': '必须立即处理'},
        'Major': {'level': '严重', 'action': '需要优先处理'},
        'Minor': {'level': '轻微', 'action': '按计划处理'},
    }

    # Matrix级别解读
    MATRIX_INTERPRETATION = {
        '1A': {'level': '极高风险', 'priority': 'P0'},
        '1B': {'level': '高风险', 'priority': 'P0'},
        '1C': {'level': '高风险', 'priority': 'P1'},
        '2A': {'level': '中高风险', 'priority': 'P1'},
        '2B': {'level': '中等风险', 'priority': 'P2'},
        '2C': {'level': '中等风险', 'priority': 'P2'},
    }

    def interpret(self, data: List[Dict], query_context: Dict[str, Any]) -> str:
        """将数据转换为业务语言描述"""
        if not data:
            return "当前数据范围内未发现问题记录"

        interpretations = []

        # 根据数据内容选择解读方式
        if 'severity' in str(data[0].keys()):
            interpretations.append(self._interpret_severity(data))

        if 'matrix_display' in str(data[0].keys()):
            interpretations.append(self._interpret_matrix(data))

        if 'is_topissue' in str(data[0].keys()):
            interpretations.append(self._interpret_topissue(data))

        if 'is_long_runner' in str(data[0].keys()):
            interpretations.append(self._interpret_longrunner(data))

        return "\n".join(filter(None, interpretations))

    def _interpret_severity(self, data: List[Dict]) -> str:
        """解读严重级别"""
        critical_count = sum(1 for row in data if row.get('severity') == 'Critical')
        major_count = sum(1 for row in data if row.get('severity') == 'Major')

        if critical_count > 0:
            return f"⚠️ 包含 {critical_count} 个阻断级缺陷，需要立即处理"
        elif major_count > 0:
            return f"⚡ 包含 {major_count} 个严重缺陷，建议优先处理"
        return ""

    def _interpret_matrix(self, data: List[Dict]) -> str:
        """解读Matrix级别"""
        high_risk = sum(1 for row in data
                       if row.get('matrix_display') in ['1A', '1B', '1C'])
        if high_risk > 0:
            return f"🔴 包含 {high_risk} 个Matrix高风险缺陷(1A-1C)"
        return ""

    def _interpret_topissue(self, data: List[Dict]) -> str:
        """解读TopIssue"""
        count = sum(1 for row in data if row.get('is_topissue'))
        if count > 0:
            return f"🔥 包含 {count} 个TopIssue热点问题，已标记为重点关注"
        return ""

    def _interpret_longrunner(self, data: List[Dict]) -> str:
        """解读Long Runner"""
        count = sum(1 for row in data if row.get('is_long_runner'))
        if count > 0:
            return f"⏰ 包含 {count} 个长期未关闭缺陷(>30天)，建议推动解决"
        return ""


class RecommendationEngine:
    """建议生成引擎"""

    def generate(self, data: List[Dict], insights: List[DataInsight],
                 query_context: Dict[str, Any]) -> List[str]:
        """生成业务建议"""
        recommendations = []

        # 基于洞察生成建议
        for insight in insights:
            if insight.recommendation:
                recommendations.append(insight.recommendation)

        # 基于数据特征生成建议
        recommendations.extend(self._generate_data_based_recommendations(data))

        # 去重并返回
        return list(dict.fromkeys(recommendations))

    def _generate_data_based_recommendations(self, data: List[Dict]) -> List[str]:
        """基于数据特征生成建议"""
        recommendations = []

        if not data:
            return recommendations

        # 检查Critical缺陷比例
        if 'severity' in data[0]:
            critical_pct = sum(1 for row in data if row.get('severity') == 'Critical') / len(data) * 100
            if critical_pct > 10:
                recommendations.append("Critical缺陷比例较高，建议召开紧急评审会议")

        # 检查TopIssue
        if 'is_topissue' in data[0]:
            topissue_count = sum(1 for row in data if row.get('is_topissue'))
            if topissue_count > 5:
                recommendations.append(f"存在 {topissue_count} 个TopIssue，建议组织专项攻关")

        # 检查处理周期
        if 'defect_age_days' in data[0]:
            ages = [row.get('defect_age_days', 0) for row in data if row.get('defect_age_days')]
            if ages and sum(ages) / len(ages) > 30:
                recommendations.append("平均缺陷处理周期超过30天，建议优化处理流程")

        return recommendations


class QueryResultExplainer:
    """
    查询结果解释器主类

    使用示例:
        explainer = QueryResultExplainer()

        # 解释查询结果
        result = explainer.explain(data, {
            'query': '昨天音频模块的高优先级缺陷',
            'sql': 'SELECT * FROM octane_defects WHERE...'
        })

        print(result.summary)
        print(result.key_findings)
        print(result.recommendations)
    """

    def __init__(self):
        self.schema = SchemaCatalog()
        self.pattern_detector = PatternDetector()
        self.summarizer = ResultSummarizer()
        self.interpreter = BusinessInterpreter()
        self.recommendation_engine = RecommendationEngine()

    def explain(self, data: List[Dict], query_context: Dict[str, Any]) -> ResultExplanation:
        """
        解释查询结果

        Args:
            data: 查询结果数据（字典列表）
            query_context: 查询上下文信息
                - query: 原始查询
                - sql: 执行的SQL
                - query_type: 查询类型

        Returns:
            ResultExplanation对象
        """
        logger.info(f"Explaining {len(data)} rows of data")

        query_type = query_context.get('query_type', 'list')

        # 1. 生成摘要
        summary = self.summarizer.summarize(data, query_type)

        # 2. 生成详细描述
        detailed_description = self.interpreter.interpret(data, query_context)

        # 3. 检测模式
        insights = self._detect_patterns(data, query_type)

        # 4. 提取关键发现
        key_findings = self._extract_key_findings(data, insights)

        # 5. 生成建议
        recommendations = self.recommendation_engine.generate(data, insights, query_context)

        # 6. 数据质量说明
        data_quality_notes = self._check_data_quality(data)

        return ResultExplanation(
            summary=summary,
            detailed_description=detailed_description,
            key_findings=key_findings,
            insights=insights,
            recommendations=recommendations,
            data_quality_notes=data_quality_notes,
            confidence=0.9 if data else 0.5
        )

    def _detect_patterns(self, data: List[Dict], query_type: str) -> List[DataInsight]:
        """检测数据模式"""
        insights = []

        if not data:
            return insights

        # 趋势检测
        if query_type == 'trend':
            trend = self.pattern_detector.detect_trends(data)
            if trend:
                insights.append(trend)

        # 异常检测
        value_field = 'count' if 'count' in data[0] else 'daily_count' if 'daily_count' in data[0] else None
        if value_field:
            anomalies = self.pattern_detector.detect_anomalies(data, value_field)
            insights.extend(anomalies)

        # 集中度检测
        if 'category' in data[0] or 'tproject' in data[0]:
            category_field = 'category' if 'category' in data[0] else 'tproject'
            concentration = self.pattern_detector.detect_concentration(data, category_field)
            if concentration:
                insights.append(concentration)

        # 风险检测
        risks = self.pattern_detector.detect_risks(data)
        insights.extend(risks)

        return insights

    def _extract_key_findings(self, data: List[Dict], insights: List[DataInsight]) -> List[str]:
        """提取关键发现"""
        findings = []

        if not data:
            findings.append("未查询到数据")
            return findings

        # 基础统计
        findings.append(f"数据总量: {len(data)} 条记录")

        # 从洞察中提取
        for insight in insights[:5]:  # 最多5个洞察
            findings.append(f"{insight.title}: {insight.description}")

        return findings

    def _check_data_quality(self, data: List[Dict]) -> List[str]:
        """检查数据质量"""
        notes = []

        if not data:
            notes.append("查询结果为空")
            return notes

        # 检查缺失值
        missing_counts = {}
        for row in data:
            for key, value in row.items():
                if value is None or value == '':
                    missing_counts[key] = missing_counts.get(key, 0) + 1

        if missing_counts:
            high_missing = [(k, v) for k, v in missing_counts.items() if v / len(data) > 0.5]
            if high_missing:
                notes.append(f"注意: {high_missing[0][0]} 等字段缺失率较高")

        return notes

    def format_for_display(self, explanation: ResultExplanation) -> str:
        """格式化为显示文本"""
        lines = []

        # 摘要
        lines.append(f"📊 {explanation.summary}")
        lines.append("")

        # 业务解读
        if explanation.detailed_description:
            lines.append("💡 业务解读:")
            for line in explanation.detailed_description.split('\n'):
                if line.strip():
                    lines.append(f"  {line}")
            lines.append("")

        # 关键发现
        if explanation.key_findings:
            lines.append("🔍 关键发现:")
            for finding in explanation.key_findings:
                lines.append(f"  • {finding}")
            lines.append("")

        # 建议
        if explanation.recommendations:
            lines.append("📋 建议:")
            for i, rec in enumerate(explanation.recommendations[:5], 1):
                lines.append(f"  {i}. {rec}")
            lines.append("")

        # 数据质量
        if explanation.data_quality_notes:
            lines.append("⚠️ 数据说明:")
            for note in explanation.data_quality_notes:
                lines.append(f"  • {note}")

        return '\n'.join(lines)


# 便捷函数
def explain_results(data: List[Dict], query: str = "", sql: str = "",
                    query_type: str = "list") -> ResultExplanation:
    """
    快速解释查询结果

    Args:
        data: 查询结果数据
        query: 原始查询
        sql: 执行的SQL
        query_type: 查询类型

    Returns:
        ResultExplanation对象
    """
    explainer = QueryResultExplainer()
    return explainer.explain(data, {
        'query': query,
        'sql': sql,
        'query_type': query_type
    })


def format_explanation(data: List[Dict], query: str = "", sql: str = "",
                       query_type: str = "list") -> str:
    """
    快速格式化解释结果

    Args:
        data: 查询结果数据
        query: 原始查询
        sql: 执行的SQL
        query_type: 查询类型

    Returns:
        格式化的解释文本
    """
    explainer = QueryResultExplainer()
    explanation = explainer.explain(data, {
        'query': query,
        'sql': sql,
        'query_type': query_type
    })
    return explainer.format_for_display(explanation)
