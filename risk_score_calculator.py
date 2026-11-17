"""
Risk Score 计算模块

从 data_processor.py 提取的独立风险评分算法
支持传入 defect 数据返回风险分数，可用于数据迁移时预计算入库

Author: AI Assistant
Date: 2026-02-17
"""

import math
from typing import Dict, List, Tuple, Optional, Any


def calculate_risk_score(defect: Dict[str, Any]) -> Tuple[float, List[str], str]:
    """
    计算单个 defect 的风险分数

    Args:
        defect: 包含 defect 字段的字典

    Returns:
        Tuple[分数, 原因列表, 风险等级]
    """
    score, reasons = _calculate_single_risk_score(defect)

    # 确定风险等级
    risk_level = _get_risk_level(score)

    return score, reasons, risk_level


def _calculate_single_risk_score(ticket_row: Dict[str, Any]) -> Tuple[float, List[str]]:
    """计算单个 ticket 的风险分数（内部实现）"""
    score = 0.0
    reasons = []

    # 保存各维度的原始分数
    dimension_scores = {
        'matrix': 0,
        'classification': 0,
        'ecu_transfer': 0,
        'domain_transfer': 0,
        'parent_complexity': 0,
        'child_complexity': 0,
        'processing_days': 0,
        'shift_pu': 0
    }

    # 保存原始数据用于非线性调整
    raw_data = {
        'matrix': '',
        'ecu_pingpong': 0,
        'domain_pingpong': 0,
        'parent_child': '',
        'child_count': 0,
        'processing_days': 0
    }

    # ========== 第一维度：Matrix Severity Level (30 points) ==========
    matrix = ticket_row.get('matrix', '')
    raw_data['matrix'] = matrix
    if isinstance(matrix, str) and matrix:
        matrix_lower = matrix.lower()

        matrix_order = {
            'matrix-1a': 0, 'matrix-1b': 1, 'matrix-1c': 2,
            'matrix-1d': 3, 'matrix-1e': 4, 'matrix-2a': 5,
            'matrix-2b': 6, 'matrix-3a': 7, 'matrix-2d': 8,
            'matrix-2e': 9, 'matrix-3b': 10, 'matrix-3c': 11,
            'matrix-3d': 12, 'matrix-4a': 13, 'matrix-3e': 14,
            'matrix-4b': 15, 'matrix-4c': 16, 'matrix-4d': 17, 'matrix-4e': 18
        }

        if matrix_lower in matrix_order:
            order = matrix_order[matrix_lower]
            matrix_score = round(30 * math.exp(-0.25 * order))
            matrix_score = max(2, matrix_score)

            score += matrix_score
            dimension_scores['matrix'] = matrix_score

            if matrix_lower in ['matrix-1a', 'matrix-1b', 'matrix-1c', 'matrix-1d', 'matrix-1e',
                               'matrix-2a', 'matrix-2b', 'matrix-3a']:
                severity_level = "High Severity"
            elif matrix_lower in ['matrix-2d', 'matrix-2e', 'matrix-3b', 'matrix-3c', 'matrix-3d', 'matrix-4a']:
                severity_level = "Medium Severity"
            else:
                severity_level = "Low Severity"

            reasons.append(f"Matrix {matrix} ({severity_level}, {matrix_score}pts)")

    # ========== 第二维度：Classification (30 points) ==========
    classification = ticket_row.get('classification', [])
    if isinstance(classification, list):
        if 'Showstopper_Confirmed' in classification:
            score += 30
            dimension_scores['classification'] = 30
            reasons.append("Showstopper Confirmed (30pts)")
        elif 'Preventing Maturity Grade ConDrive' in classification:
            score += 30
            dimension_scores['classification'] = 30
            reasons.append("Preventing Maturity ConDrive (30pts)")
        elif 'Showstopper_Candidate' in classification:
            score += 20
            dimension_scores['classification'] = 20
            reasons.append("Showstopper Candidate (20pts)")
        elif 'Obstructing Maturity Grade ConDrive' in classification:
            score += 10
            dimension_scores['classification'] = 10
            reasons.append("Obstructing Maturity ConDrive (10pts)")
        elif 'Homologation L-labelled' in classification:
            score += 10
            dimension_scores['classification'] = 10
            reasons.append("Homologation L-labelled (10pts)")

    # ========== 第三维度：ECU Transfer Count (30 points) ==========
    ecu_pingpong = ticket_row.get('ecu_no_of_changes_udf', 0) or ticket_row.get('pingpong', 0)
    raw_data['ecu_pingpong'] = ecu_pingpong
    if ecu_pingpong and ecu_pingpong > 0:
        if ecu_pingpong >= 5:
            score += 30
            dimension_scores['ecu_transfer'] = 30
            reasons.append(f"ECU Transfer {ecu_pingpong} times (30pts)")
        elif ecu_pingpong >= 3:
            score += 24
            dimension_scores['ecu_transfer'] = 24
            reasons.append(f"ECU Transfer {ecu_pingpong} times (24pts)")
        elif ecu_pingpong >= 1:
            score += 20
            dimension_scores['ecu_transfer'] = 20
            reasons.append(f"ECU Transfer {ecu_pingpong} times (20pts)")

    # ========== 第四维度：Domain Transfer Count (20 points) ==========
    domain_pingpong = ticket_row.get('domain_pingpong_display', 0) or ticket_row.get('domain_pingpong_count', 0)
    raw_data['domain_pingpong'] = domain_pingpong
    if domain_pingpong and domain_pingpong > 0:
        if domain_pingpong >= 5:
            score += 20
            dimension_scores['domain_transfer'] = 20
            reasons.append(f"Domain Transfer {domain_pingpong} times (20pts)")
        elif domain_pingpong >= 3:
            score += 14
            dimension_scores['domain_transfer'] = 14
            reasons.append(f"Domain Transfer {domain_pingpong} times (14pts)")
        elif domain_pingpong >= 1:
            score += 10
            dimension_scores['domain_transfer'] = 10
            reasons.append(f"Domain Transfer {domain_pingpong} times (10pts)")

    # ========== 第五维度：Parent Ticket Child Count (30 points) ==========
    parent_child = ticket_row.get('parent_child', '')
    raw_data['parent_child'] = parent_child
    if parent_child == 'Parent':
        parent_child_count = ticket_row.get('子票数量', 0) or ticket_row.get('child_count', 0)
        raw_data['child_count'] = parent_child_count
        if parent_child_count and parent_child_count > 0:
            parent_score = round(10 * math.log(parent_child_count + 1) * 2.5)
            parent_score = min(30, parent_score)
            score += parent_score
            dimension_scores['parent_complexity'] = parent_score
            reasons.append(f"Parent with {parent_child_count} children ({parent_score}pts)")

    # ========== 第六维度：Child Ticket Master Sub-ticket Count (30 points) ==========
    if parent_child == 'Child':
        child_count = ticket_row.get('子票数量', 0) or ticket_row.get('child_count', 0)
        raw_data['child_count'] = child_count
        if child_count and child_count > 0:
            child_score = round(10 * math.log(child_count + 1) * 2.5)
            child_score = min(30, child_score)
            score += child_score
            dimension_scores['child_complexity'] = child_score
            reasons.append(f"Master has {child_count} children ({child_score}pts)")

    # ========== 第七维度：Processing Cycle Days (20 points) ==========
    processing_days = ticket_row.get('processing_cycle_days', 0)
    raw_data['processing_days'] = processing_days
    if processing_days and processing_days > 0:
        if processing_days <= 3:
            processing_score = max(18, 24 - processing_days * 2)
            peak_type = "New Issue"
        elif processing_days <= 20:
            normalized_days = (processing_days - 12) / 12
            processing_score = round(5 + 10 * (1 - normalized_days ** 2))
            processing_score = max(5, min(15, processing_score))
            peak_type = "Normal Processing"
        elif processing_days <= 30:
            processing_score = round(15 + (processing_days - 21) * 0.5)
            peak_type = "Long Runner Rise"
        else:
            extra_days = processing_days - 30
            processing_score = min(25, 20 + (extra_days // 10) * 2)
            peak_type = "Long Runner Peak"

        score += processing_score
        dimension_scores['processing_days'] = processing_score
        reasons.append(f"Processing {processing_days} days ({processing_score}pts) [{peak_type}]")

    # ========== 第八维度：Shift PU Status (10 points) ==========
    shift_pu = ticket_row.get('Shift_PU', '') or ticket_row.get('shift_pu', '')
    if shift_pu and str(shift_pu).strip():
        score += 10
        dimension_scores['shift_pu'] = 10
        reasons.append(f"Shift PU assigned (10pts)")

    # ========== 智能组合算法 ==========
    dimension_values = [v for v in dimension_scores.values() if v > 0]

    if dimension_values:
        high_score_items = [v for v in dimension_values if v > 15]
        low_score_items = [v for v in dimension_values if v <= 15]

        combined_score = 0

        if high_score_items:
            high_score_avg = sum(high_score_items) / len(high_score_items)
            high_score_contribution = high_score_avg * 1.2 * len(high_score_items)
            combined_score += high_score_contribution

        if low_score_items:
            geometric_mean = math.pow(math.prod(low_score_items), 1/len(low_score_items))
            low_score_contribution = geometric_mean * 0.8 * len(low_score_items)
            combined_score += low_score_contribution

        score = round(combined_score)

    # ========== 非线性调整 ==========
    nonlinear_adjustment = 0

    # 严重问题长期未解决
    if dimension_scores['matrix'] >= 20 and raw_data['processing_days'] >= 30:
        nonlinear_adjustment += 15
        reasons.append("High severity issue with long processing time (+15pts)")

    # 跨ECU和跨领域的复杂问题
    if raw_data['ecu_pingpong'] >= 3 and raw_data['domain_pingpong'] >= 3:
        nonlinear_adjustment += 10
        reasons.append("Complex cross-ECU and cross-domain issue (+10pts)")

    # 严重的阻塞问题
    if dimension_scores['matrix'] >= 24 and dimension_scores['classification'] >= 20:
        nonlinear_adjustment += 15
        reasons.append("Critical blocking issue (+15pts)")

    # 时间衰减与加速
    if raw_data['processing_days'] > 30:
        time_factor = min(30, ((raw_data['processing_days'] - 30) / 10) * 5)
        nonlinear_adjustment += time_factor
        reasons.append(f"Extended processing time risk (+{time_factor:.1f}pts)")

    # 超大规模父票
    if raw_data['parent_child'] == 'Parent' and raw_data['child_count'] > 10:
        extra_score = min(25, (raw_data['child_count'] - 10) * 2.5)
        nonlinear_adjustment += extra_score
        reasons.append(f"Extremely large parent ticket (+{extra_score:.1f}pts)")

    # ECU频繁转移
    if raw_data['ecu_pingpong'] > 5:
        extra_score = min(20, 10 * math.log(1 + (raw_data['ecu_pingpong'] - 5) / 2))
        nonlinear_adjustment += extra_score
        reasons.append(f"Extreme ECU transfer complexity (+{extra_score:.1f}pts)")

    score += nonlinear_adjustment

    return score, reasons


def _get_risk_level(score: float) -> str:
    """根据分数确定风险等级"""
    if score >= 140:
        return "Extremely High Risk"
    elif score >= 100:
        return "High Risk"
    elif score >= 60:
        return "Medium Risk"
    elif score >= 30:
        return "Low Risk"
    else:
        return "Minimal Risk"


def batch_calculate_risk_scores(defects: List[Dict[str, Any]]) -> List[Tuple[float, List[str], str]]:
    """
    批量计算风险分数

    Args:
        defects: defect 字典列表

    Returns:
        每个 defect 的 (分数, 原因, 等级) 列表
    """
    return [calculate_risk_score(d) for d in defects]


def calculate_with_master(defect: Dict[str, Any], master_lookup: Optional[Dict[str, Dict]] = None) -> Tuple[float, List[str], str]:
    """
    计算风险分数，如果是 Child ticket 则考虑 Master ticket 的分数

    Args:
        defect: defect 数据
        master_lookup: master_id -> master_data 的查找字典

    Returns:
        (最终分数, 原因列表, 风险等级)
    """
    child_score, child_reasons = _calculate_single_risk_score(defect)
    final_score = child_score
    final_reasons = child_reasons.copy()

    # 检查是否为 Child ticket
    parent_child = defect.get('parent_child', '')
    parent_info = defect.get('parent', {})

    master_id = None
    if isinstance(parent_info, dict) and 'id' in parent_info:
        master_id = parent_info['id']

    if parent_child in ['Child', 'Child (candidate)'] and master_id and master_lookup:
        master_data = master_lookup.get(str(master_id))
        if master_data:
            master_score, master_reasons = _calculate_single_risk_score(master_data)
            if master_score > child_score:
                final_score = master_score
                final_reasons = master_reasons

    risk_level = _get_risk_level(final_score)
    return final_score, final_reasons, risk_level


# ========== 测试入口 ==========
if __name__ == "__main__":
    # 测试用例
    test_defect = {
        "matrix": "matrix-1a",
        "classification": ["Showstopper_Confirmed"],
        "ecu_no_of_changes_udf": 3,
        "parent_child": "Parent",
        "子票数量": 5,
        "processing_cycle_days": 35,
    }

    score, reasons, level = calculate_risk_score(test_defect)
    print(f"\n风险分数: {score}")
    print(f"风险等级: {level}")
    print("评分原因:")
    for r in reasons:
        print(f"  - {r}")
