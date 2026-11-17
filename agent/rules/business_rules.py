"""
业务规则引擎 - 可执行的业务规则定义和计算

核心功能：
1. 规则定义 - 声明式业务规则（风险评分、Matrix计算、SLA等）
2. 规则执行 - 在数据上执行规则计算
3. 规则链 - 组合多个规则进行复杂分析
4. 动态规则 - 支持运行时动态添加规则

作者: AI Assistant
日期: 2026-03-18
"""

import json
import re
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class RuleType(Enum):
    """规则类型"""
    RISK_SCORE = "risk_score"           # 风险评分
    MATRIX_LEVEL = "matrix_level"       # Matrix级别
    SLA_CHECK = "sla_check"             # SLA检查
    QUALITY_CHECK = "quality_check"     # 质量检查
    BUSINESS_LOGIC = "business_logic"   # 业务逻辑
    CUSTOM = "custom"                   # 自定义规则


class RulePriority(Enum):
    """规则优先级"""
    CRITICAL = 1    # 关键
    HIGH = 2        # 高
    MEDIUM = 3      # 中
    LOW = 4         # 低


@dataclass
class RuleResult:
    """规则执行结果"""
    rule_name: str
    passed: bool
    score: Optional[float] = None
    level: Optional[str] = None
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class BusinessRule:
    """业务规则定义"""
    name: str
    rule_type: RuleType
    description: str
    condition: str  # 条件表达式或逻辑
    action: str     # 执行动作
    priority: RulePriority = RulePriority.MEDIUM
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class RuleExecutor(ABC):
    """规则执行器基类"""

    @abstractmethod
    def execute(self, data: Dict[str, Any]) -> RuleResult:
        """执行规则"""
        pass


class RiskScoreRule(RuleExecutor):
    """
    风险评分规则

    基于多个维度计算缺陷风险分数：
    - 严重级别 (30%)
    - Matrix级别 (25%)
    - 年龄 (20%)
    - TopIssue标记 (15%)
    - 状态 (10%)
    """

    # 严重级别权重
    SEVERITY_WEIGHTS = {
        'Critical': 1.0,
        'Major': 0.7,
        'Minor': 0.3,
    }

    # Matrix级别权重映射
    MATRIX_WEIGHTS = {
        '1A': 1.0, '1B': 0.95, '1C': 0.9, '1D': 0.85,
        '2A': 0.8, '2B': 0.75, '2C': 0.7,
        '3A': 0.5, '3B': 0.45, '3C': 0.4,
        '4A': 0.2, '4B': 0.15, '4C': 0.1, '4D': 0.05,
    }

    # 年龄风险阈值
    AGE_THRESHOLDS = {
        7: 0.2,    # 1周内
        14: 0.4,   # 2周内
        30: 0.6,   # 1月内
        60: 0.8,   # 2月内
        float('inf'): 1.0,  # 超过2月
    }

    def execute(self, data: Dict[str, Any]) -> RuleResult:
        """计算风险评分"""
        scores = []
        details = {}

        # 1. 严重级别评分 (30%)
        severity = data.get('severity', 'Minor')
        severity_score = self.SEVERITY_WEIGHTS.get(severity, 0.3)
        scores.append(severity_score * 0.30)
        details['severity_score'] = severity_score * 0.30

        # 2. Matrix级别评分 (25%)
        matrix = data.get('matrix_display', '4D')
        matrix_score = self.MATRIX_WEIGHTS.get(matrix, 0.05)
        scores.append(matrix_score * 0.25)
        details['matrix_score'] = matrix_score * 0.25

        # 3. 年龄评分 (20%)
        age_days = data.get('defect_age_days', 0) or 0
        age_score = self._calculate_age_score(age_days)
        scores.append(age_score * 0.20)
        details['age_score'] = age_score * 0.20
        details['age_days'] = age_days

        # 4. TopIssue评分 (15%)
        is_topissue = data.get('is_topissue', False)
        topissue_score = 1.0 if is_topissue else 0.3
        scores.append(topissue_score * 0.15)
        details['topissue_score'] = topissue_score * 0.15

        # 5. 状态评分 (10%)
        status = data.get('status_phase', 'New')
        status_score = self._calculate_status_score(status)
        scores.append(status_score * 0.10)
        details['status_score'] = status_score * 0.10

        # 计算总分 (0-100)
        total_score = sum(scores) * 100
        total_score = min(100, max(0, total_score))

        # 确定风险等级
        risk_level = self._determine_risk_level(total_score)

        # 生成建议
        recommendations = self._generate_recommendations(
            total_score, severity, matrix, is_topissue, age_days
        )

        return RuleResult(
            rule_name="RiskScore",
            passed=total_score < 60,
            score=round(total_score, 1),
            level=risk_level,
            message=f"风险评分: {total_score:.1f}/100，等级: {risk_level}",
            details=details,
            recommendations=recommendations
        )

    def _calculate_age_score(self, age_days: int) -> float:
        """计算年龄风险分数"""
        for threshold, score in sorted(self.AGE_THRESHOLDS.items()):
            if age_days <= threshold:
                return score
        return 1.0

    def _calculate_status_score(self, status: str) -> float:
        """根据状态计算分数"""
        status_scores = {
            'New': 0.8,
            'Assigned': 0.6,
            'In Progress': 0.4,
            'Fixed': 0.2,
            'Closed': 0.0,
            'Rejected': 0.0,
        }
        return status_scores.get(status, 0.5)

    def _determine_risk_level(self, score: float) -> str:
        """确定风险等级"""
        if score >= 80:
            return "🔴 极高风险"
        elif score >= 60:
            return "🟠 高风险"
        elif score >= 40:
            return "🟡 中风险"
        else:
            return "🟢 低风险"

    def _generate_recommendations(self, score: float, severity: str,
                                   matrix: str, is_topissue: bool,
                                   age_days: int) -> List[str]:
        """生成风险建议"""
        recommendations = []

        if score >= 80:
            recommendations.append("立即组织技术评审，制定解决方案")
        elif score >= 60:
            recommendations.append("优先安排资源处理")

        if severity == 'Critical':
            recommendations.append("Critical级别缺陷需要立即修复")

        if matrix in ['1A', '1B']:
            recommendations.append(f"Matrix {matrix} 级别需要高层关注")

        if is_topissue:
            recommendations.append("TopIssue已标记，需要专项跟进")

        if age_days > 30:
            recommendations.append(f"已存在 {age_days} 天，建议推动解决")

        return recommendations


class MatrixLevelRule(RuleExecutor):
    """
    Matrix级别计算规则

    根据严重级别和影响范围计算Matrix位置
    """

    # 严重级别到行映射
    SEVERITY_TO_ROW = {
        'Critical': 1,
        'Major': 2,
        'Minor': 3,
    }

    def execute(self, data: Dict[str, Any]) -> RuleResult:
        """计算Matrix级别"""
        severity = data.get('severity', 'Minor')

        # 简化的Matrix计算（实际业务可能更复杂）
        row = self.SEVERITY_TO_ROW.get(severity, 3)

        # 根据额外因素确定列 (A-D)
        col = self._determine_column(data)

        matrix_display = f"{row}{col}"

        # 计算业务影响
        impact = self._calculate_impact(matrix_display)

        return RuleResult(
            rule_name="MatrixLevel",
            passed=True,
            level=matrix_display,
            message=f"Matrix级别: {matrix_display}，业务影响: {impact}",
            details={
                'matrix_display': matrix_display,
                'severity': severity,
                'impact_level': impact,
            },
            recommendations=self._generate_matrix_recommendations(matrix_display)
        )

    def _determine_column(self, data: Dict[str, Any]) -> str:
        """确定Matrix列 (A-D)"""
        # 基于多个因素综合判断
        score = 0

        # TopIssue增加权重
        if data.get('is_topissue'):
            score += 2

        # 年龄因素
        age = data.get('defect_age_days', 0) or 0
        if age > 30:
            score += 2
        elif age > 14:
            score += 1

        # 状态因素
        if data.get('status_phase') == 'New':
            score += 1

        # 映射到列
        if score >= 3:
            return 'A'
        elif score >= 2:
            return 'B'
        elif score >= 1:
            return 'C'
        else:
            return 'D'

    def _calculate_impact(self, matrix_display: str) -> str:
        """计算业务影响"""
        if matrix_display in ['1A', '1B']:
            return "阻断级 - 车辆无法交付"
        elif matrix_display in ['1C', '2A', '2B']:
            return "严重 - 主要功能受影响"
        elif matrix_display in ['2C', '3A', '3B']:
            return "中等 - 次要功能受影响"
        else:
            return "轻微 - 影响有限"

    def _generate_matrix_recommendations(self, matrix_display: str) -> List[str]:
        """生成Matrix相关建议"""
        recommendations = []

        if matrix_display.startswith('1'):
            recommendations.append("Matrix 1x 级别需要立即处理")
        elif matrix_display.startswith('2'):
            recommendations.append("Matrix 2x 级别需要优先处理")

        if matrix_display.endswith('A'):
            recommendations.append("Matrix xA 级别需要高层关注")

        return recommendations


class SLACheckRule(RuleExecutor):
    """
    SLA检查规则

    检查缺陷是否满足SLA要求
    """

    # SLA时限定义 (天)
    SLA_THRESHOLDS = {
        'Critical': 1,   # Critical: 1天
        'Major': 7,      # Major: 7天
        'Minor': 30,     # Minor: 30天
    }

    def execute(self, data: Dict[str, Any]) -> RuleResult:
        """执行SLA检查"""
        severity = data.get('severity', 'Minor')
        age_days = data.get('defect_age_days', 0) or 0
        status = data.get('status_phase', 'New')

        # 已关闭的缺陷不检查SLA
        if status in ['Closed', 'Rejected']:
            return RuleResult(
                rule_name="SLACheck",
                passed=True,
                message="缺陷已关闭，无需SLA检查",
                details={'status': status}
            )

        # 获取SLA阈值
        sla_days = self.SLA_THRESHOLDS.get(severity, 30)

        # 计算剩余时间
        remaining_days = sla_days - age_days

        # 检查是否超时
        is_violated = age_days > sla_days

        # 计算SLA达成率
        sla_achievement = max(0, min(100, (remaining_days / sla_days) * 100))

        details = {
            'severity': severity,
            'age_days': age_days,
            'sla_days': sla_days,
            'remaining_days': remaining_days,
            'is_violated': is_violated,
            'sla_achievement': round(sla_achievement, 1),
        }

        if is_violated:
            return RuleResult(
                rule_name="SLACheck",
                passed=False,
                message=f"⚠️ SLA已超时 {abs(remaining_days)} 天",
                details=details,
                recommendations=[
                    f"严重级别 {severity} 的SLA为 {sla_days} 天",
                    "建议升级处理并制定解决方案",
                    "考虑申请SLA豁免（如适用）"
                ]
            )
        elif remaining_days <= 2:
            return RuleResult(
                rule_name="SLACheck",
                passed=True,
                message=f"⏰ SLA即将到期，剩余 {remaining_days} 天",
                details=details,
                recommendations=[
                    f"SLA将在 {remaining_days} 天内到期",
                    "建议加快处理进度"
                ]
            )
        else:
            return RuleResult(
                rule_name="SLACheck",
                passed=True,
                message=f"✅ SLA正常，剩余 {remaining_days} 天",
                details=details
            )


class QualityCheckRule(RuleExecutor):
    """
    质量检查规则

    检查缺陷数据质量
    """

    def execute(self, data: Dict[str, Any]) -> RuleResult:
        """执行质量检查"""
        issues = []
        warnings = []

        # 1. 检查必填字段
        required_fields = ['name', 'severity', 'status_phase', 'tproject']
        for field in required_fields:
            if not data.get(field):
                issues.append(f"缺少必填字段: {field}")

        # 2. 检查AIDA字段
        if not data.get('aida_english') and not data.get('top_aida'):
            warnings.append("缺少AIDA信息，可能影响分类统计")

        # 3. 检查描述长度
        description = data.get('description', '')
        if len(str(description)) < 10:
            warnings.append("缺陷描述过短，建议补充详细信息")

        # 4. 检查ECU信息
        if not data.get('ecu'):
            warnings.append("缺少ECU信息")

        # 5. 检查重复可能性
        name = data.get('name', '')
        if name and len(name) < 5:
            warnings.append("缺陷名称过短，注意检查是否重复提交")

        # 生成结果
        passed = len(issues) == 0

        if issues:
            message = f"发现 {len(issues)} 个质量问题"
        elif warnings:
            message = f"数据质量良好，有 {len(warnings)} 个警告"
        else:
            message = "数据质量检查通过"

        return RuleResult(
            rule_name="QualityCheck",
            passed=passed,
            message=message,
            details={
                'issues': issues,
                'warnings': warnings,
                'issue_count': len(issues),
                'warning_count': len(warnings),
            },
            recommendations=issues + warnings
        )


class BusinessRuleEngine:
    """
    业务规则引擎主类

    使用示例:
        engine = BusinessRuleEngine()

        # 注册规则
        engine.register_rule(RiskScoreRule())
        engine.register_rule(SLACheckRule())

        # 执行规则
        results = engine.execute_all(defect_data)

        for result in results:
            print(f"{result.rule_name}: {result.message}")
    """

    def __init__(self):
        self.rules: Dict[str, RuleExecutor] = {}
        self.rule_definitions: Dict[str, BusinessRule] = {}
        self._register_default_rules()

    def _register_default_rules(self):
        """注册默认规则"""
        self.register_rule("risk_score", RiskScoreRule())
        self.register_rule("matrix_level", MatrixLevelRule())
        self.register_rule("sla_check", SLACheckRule())
        self.register_rule("quality_check", QualityCheckRule())

    def register_rule(self, name: str, rule: RuleExecutor,
                      definition: Optional[BusinessRule] = None):
        """
        注册规则

        Args:
            name: 规则名称
            rule: 规则执行器
            definition: 规则定义（可选）
        """
        self.rules[name] = rule

        if definition:
            self.rule_definitions[name] = definition
        else:
            # 创建默认定义
            self.rule_definitions[name] = BusinessRule(
                name=name,
                rule_type=RuleType.CUSTOM,
                description=f"规则: {name}",
                condition="auto",
                action="execute"
            )

        logger.info(f"Registered rule: {name}")

    def unregister_rule(self, name: str):
        """注销规则"""
        if name in self.rules:
            del self.rules[name]
            del self.rule_definitions[name]
            logger.info(f"Unregistered rule: {name}")

    def execute(self, rule_name: str, data: Dict[str, Any]) -> Optional[RuleResult]:
        """
        执行单个规则

        Args:
            rule_name: 规则名称
            data: 缺陷数据

        Returns:
            规则执行结果
        """
        rule = self.rules.get(rule_name)
        if not rule:
            logger.warning(f"Rule not found: {rule_name}")
            return None

        try:
            return rule.execute(data)
        except Exception as e:
            logger.error(f"Rule execution failed: {e}")
            return RuleResult(
                rule_name=rule_name,
                passed=False,
                message=f"规则执行失败: {str(e)}"
            )

    def execute_all(self, data: Dict[str, Any],
                    rule_names: Optional[List[str]] = None) -> List[RuleResult]:
        """
        执行多个规则

        Args:
            data: 缺陷数据
            rule_names: 要执行的规则列表（None表示执行所有）

        Returns:
            规则执行结果列表
        """
        results = []

        names_to_execute = rule_names or list(self.rules.keys())

        for name in names_to_execute:
            result = self.execute(name, data)
            if result:
                results.append(result)

        return results

    def execute_by_type(self, data: Dict[str, Any],
                        rule_type: RuleType) -> List[RuleResult]:
        """
        按类型执行规则

        Args:
            data: 缺陷数据
            rule_type: 规则类型

        Returns:
            规则执行结果列表
        """
        matching_rules = [
            name for name, defn in self.rule_definitions.items()
            if defn.rule_type == rule_type
        ]
        return self.execute_all(data, matching_rules)

    def get_rule_summary(self, results: List[RuleResult]) -> Dict[str, Any]:
        """
        获取规则执行摘要

        Args:
            results: 规则执行结果列表

        Returns:
            摘要信息
        """
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed

        # 收集所有建议
        all_recommendations = []
        for result in results:
            all_recommendations.extend(result.recommendations)

        # 按风险等级统计
        risk_levels = {}
        for result in results:
            if result.level:
                risk_levels[result.level] = risk_levels.get(result.level, 0) + 1

        return {
            'total_rules': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': round(passed / total * 100, 1) if total > 0 else 0,
            'recommendations': list(dict.fromkeys(all_recommendations)),  # 去重
            'risk_level_distribution': risk_levels,
            'highest_risk': max(
                (r for r in results if r.score is not None),
                key=lambda x: x.score or 0,
                default=None
            )
        }


# 便捷函数
def calculate_risk_score(data: Dict[str, Any]) -> RuleResult:
    """快速计算风险评分"""
    rule = RiskScoreRule()
    return rule.execute(data)


def check_sla(data: Dict[str, Any]) -> RuleResult:
    """快速检查SLA"""
    rule = SLACheckRule()
    return rule.execute(data)


def run_all_checks(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    运行所有检查

    Args:
        data: 缺陷数据

    Returns:
        包含所有检查结果的摘要
    """
    engine = BusinessRuleEngine()
    results = engine.execute_all(data)
    summary = engine.get_rule_summary(results)

    return {
        'summary': summary,
        'details': [
            {
                'rule': r.rule_name,
                'passed': r.passed,
                'score': r.score,
                'level': r.level,
                'message': r.message,
            }
            for r in results
        ]
    }
