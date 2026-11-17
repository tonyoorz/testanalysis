"""
风险分析工具 - 集成 TopIssue 风险评分算法

功能：
1. 从 SQLite 数据库加载缺陷数据
2. 计算风险分数（规则 + 学习权重混合）
3. 返回分析结果供 Agent 调用

Author: tonyorz
Date: 2026-03-18
"""

import sqlite3
import json
import math
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import Counter
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class RiskScore:
    """风险评分结果"""
    defect_id: str
    defect_name: str
    final_score: int
    risk_level: str
    rule_score: int
    key_factors: List[str]
    team: str = ""
    phase: str = ""
    severity: str = ""


class RiskAnalysisTool:
    """风险分析工具 - 可被 Agent 调用"""
    
    # Phase 风险系数
    PHASE_RISK = {
        'new': 0.3,
        'in analysis': 0.4,
        'in progress': 0.5,
        'in verification': 0.6,
        'resolved': 0.2,
        'closed': 0.1,
    }
    
    # Severity 风险
    SEVERITY_RISK = {
        'critical': 1.0,
        'high': 0.8,
        'medium': 0.5,
        'low': 0.2,
        'none': 0.0,
    }
    
    # Problem Severity 风险
    PROBLEM_SEVERITY_RISK = {
        'showstopper': 1.0,
        'major': 0.7,
        'minor': 0.4,
        'cosmetic': 0.2,
    }
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(PROJECT_ROOT, 'database', 'local_data.db')
        self.db_path = db_path
    
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def load_defects(
        self, 
        year: int = 2025, 
        team: Optional[str] = None,
        program: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """从数据库加载缺陷数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                defect_id, name, creation_time, last_modified,
                team, problem_finder_team, program,
                phase, severity, problem_severity,
                ecu_no_of_changes, reprel_changes,
                parent_child_type, blocking_reason,
                user_tags, product_areas, risk_score
            FROM octane_defects
            WHERE year = ?
        """
        params = [year]
        
        if team:
            query += " AND team = ?"
            params.append(team)
        
        if program:
            query += " AND program = ?"
            params.append(program)
        
        query += " ORDER BY last_modified DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def calculate_risk_score(self, defect: Dict) -> RiskScore:
        """计算单个缺陷的风险分数"""
        score = 0
        factors = []
        
        # 1. Severity 风险 (25分)
        severity = str(defect.get('severity', '')).lower()
        sev_score = int(self.SEVERITY_RISK.get(severity, 0.3) * 25)
        score += sev_score
        if sev_score > 10:
            factors.append(f"严重度: {severity.upper()}")
        
        # 2. Problem severity (20分)
        prob_sev = str(defect.get('problem_severity', '')).lower()
        prob_score = 0
        for key, risk in self.PROBLEM_SEVERITY_RISK.items():
            if key in prob_sev:
                prob_score = max(prob_score, int(risk * 20))
        score += prob_score
        if prob_score > 10:
            factors.append(f"问题级别: {prob_sev[:20]}")
        
        # 3. ECU 变更 (20分)
        ecu_changes = int(defect.get('ecu_no_of_changes', 0) or 0)
        if ecu_changes >= 10:
            score += 20
            factors.append(f"ECU 变更 {ecu_changes}x")
        elif ecu_changes >= 5:
            score += 14
            factors.append(f"ECU 变更 {ecu_changes}x")
        elif ecu_changes >= 2:
            score += 8
            factors.append(f"ECU 变更 {ecu_changes}x")
        
        # 4. Release 变更 (15分)
        reprel = int(defect.get('reprel_changes', 0) or 0)
        if reprel >= 5:
            score += 15
            factors.append(f"Release 变更 {reprel}x")
        elif reprel >= 3:
            score += 10
            factors.append(f"Release 变更 {reprel}x")
        elif reprel >= 2:
            score += 5
        
        # 5. Blocked (20分)
        blocking = str(defect.get('blocking_reason', '')).lower()
        if blocking and blocking not in ['none', '', 'duplicate', 'nan']:
            score += 20
            factors.append(f"被阻塞: {blocking[:15]}")
        
        # 6. Phase 风险 (10分)
        phase = str(defect.get('phase', '')).lower()
        phase_score = int(self.PHASE_RISK.get(phase, 0.3) * 10)
        score += phase_score
        
        # 7. Parent/Child (10分)
        parent_child = str(defect.get('parent_child_type', '')).lower()
        if 'parent' in parent_child and 'child' not in parent_child:
            score += 10
            factors.append("父票")
        elif 'child' in parent_child:
            score += 5
            factors.append("子票")
        
        # 风险等级
        if score >= 80:
            risk_level = "极高风险"
        elif score >= 60:
            risk_level = "高风险"
        elif score >= 40:
            risk_level = "中等风险"
        elif score >= 20:
            risk_level = "低风险"
        else:
            risk_level = "极低风险"
        
        return RiskScore(
            defect_id=str(defect.get('defect_id', '')),
            defect_name=str(defect.get('name', ''))[:60],
            final_score=score,
            risk_level=risk_level,
            rule_score=score,
            key_factors=factors[:5] if factors else ["无明显高风险因素"],
            team=str(defect.get('team', '')),
            phase=str(defect.get('phase', '')),
            severity=str(defect.get('severity', '')),
        )
    
    def analyze_top_risks(
        self, 
        year: int = 2025, 
        top_n: int = 20,
        team: Optional[str] = None,
        program: Optional[str] = None
    ) -> Dict[str, Any]:
        """分析高风险缺陷"""
        defects = self.load_defects(year, team, program)
        
        if not defects:
            return {
                'success': False,
                'error': '没有找到符合条件的缺陷数据',
                'total_count': 0
            }
        
        # 计算所有缺陷的风险分数
        risk_scores = [self.calculate_risk_score(d) for d in defects]
        
        # 按分数排序
        risk_scores.sort(key=lambda x: -x.final_score)
        
        # 统计风险分布
        risk_dist = Counter(r.risk_level for r in risk_scores)
        
        # 统计团队分布
        team_dist = Counter(r.team for r in risk_scores[:top_n] if r.team)
        
        return {
            'success': True,
            'total_count': len(risk_scores),
            'risk_distribution': dict(risk_dist),
            'team_distribution': dict(team_dist.most_common(5)),
            'top_risks': [
                {
                    'rank': i + 1,
                    'defect_id': r.defect_id,
                    'defect_name': r.defect_name,
                    'score': r.final_score,
                    'level': r.risk_level,
                    'team': r.team,
                    'phase': r.phase,
                    'severity': r.severity,
                    'factors': r.key_factors
                }
                for i, r in enumerate(risk_scores[:top_n])
            ],
            'analyzed_at': datetime.now().isoformat()
        }
    
    def get_risk_summary(self, year: int = 2025) -> Dict[str, Any]:
        """获取风险概览"""
        defects = self.load_defects(year)
        
        if not defects:
            return {'success': False, 'error': '没有数据'}
        
        risk_scores = [self.calculate_risk_score(d) for d in defects]
        
        # 统计
        risk_dist = Counter(r.risk_level for r in risk_scores)
        high_risk_count = sum(1 for r in risk_scores if r.final_score >= 60)
        avg_score = sum(r.final_score for r in risk_scores) / len(risk_scores)
        
        # 按团队统计
        team_stats = {}
        for r in risk_scores:
            if r.team not in team_stats:
                team_stats[r.team] = {'total': 0, 'high_risk': 0, 'scores': []}
            team_stats[r.team]['total'] += 1
            team_stats[r.team]['scores'].append(r.final_score)
            if r.final_score >= 60:
                team_stats[r.team]['high_risk'] += 1
        
        # 排序团队
        team_summary = []
        for team, stats in sorted(team_stats.items(), key=lambda x: -x[1]['high_risk']):
            team_summary.append({
                'team': team,
                'total': stats['total'],
                'high_risk': stats['high_risk'],
                'high_risk_rate': round(stats['high_risk'] / stats['total'] * 100, 1),
                'avg_score': round(sum(stats['scores']) / len(stats['scores']), 1)
            })
        
        return {
            'success': True,
            'total_defects': len(risk_scores),
            'high_risk_count': high_risk_count,
            'high_risk_rate': round(high_risk_count / len(risk_scores) * 100, 1),
            'avg_score': round(avg_score, 1),
            'risk_distribution': dict(risk_dist),
            'team_summary': team_summary[:10]
        }
    
    def update_risk_scores_in_db(self, year: int = 2025) -> int:
        """更新数据库中的风险分数"""
        defects = self.load_defects(year)
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updated = 0
        for defect in defects:
            risk = self.calculate_risk_score(defect)
            try:
                cursor.execute(
                    "UPDATE octane_defects SET risk_score = ? WHERE defect_id = ?",
                    (risk.final_score, risk.defect_id)
                )
                updated += 1
            except Exception as e:
                print(f"更新失败 {risk.defect_id}: {e}")
        
        conn.commit()
        conn.close()
        return updated
    
    def create_risk_index(self):
        """创建风险分数索引"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 检查索引是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='idx_defects_risk_score'
        """)
        if cursor.fetchone():
            conn.close()
            return "索引已存在"
        
        # 创建索引
        cursor.execute("CREATE INDEX idx_defects_risk_score ON octane_defects(risk_score DESC)")
        conn.commit()
        conn.close()
        return "索引创建成功"


# ============ Agent 工具接口 ============

def get_tool_definition():
    """返回工具定义，供 Agent 注册"""
    return {
        'name': 'risk_analysis',
        'description': '分析缺陷风险，返回高风险缺陷列表和风险分布统计',
        'parameters': {
            'type': 'object',
            'properties': {
                'year': {
                    'type': 'integer',
                    'description': '数据年份，默认 2025',
                    'default': 2025
                },
                'top_n': {
                    'type': 'integer',
                    'description': '返回 Top N 高风险缺陷，默认 20',
                    'default': 20
                },
                'team': {
                    'type': 'string',
                    'description': '按团队筛选（可选）',
                    'default': None
                },
                'program': {
                    'type': 'string',
                    'description': '按项目筛选（可选）',
                    'default': None
                },
                'action': {
                    'type': 'string',
                    'enum': ['analyze', 'summary', 'update_db', 'create_index'],
                    'description': '操作类型',
                    'default': 'analyze'
                }
            },
            'required': []
        },
        'handler': execute_risk_analysis
    }


def execute_risk_analysis(
    year: int = 2025, 
    top_n: int = 20,
    team: Optional[str] = None,
    program: Optional[str] = None,
    action: str = 'analyze'
) -> Dict[str, Any]:
    """执行风险分析 - Agent 调用入口"""
    
    tool = RiskAnalysisTool()
    
    try:
        if action == 'update_db':
            count = tool.update_risk_scores_in_db(year)
            return {
                'success': True,
                'message': f'已更新 {count} 条缺陷的风险分数',
                'updated_count': count
            }
        
        elif action == 'create_index':
            result = tool.create_risk_index()
            return {
                'success': True,
                'message': result
            }
        
        elif action == 'summary':
            result = tool.get_risk_summary(year)
            return result
        
        else:  # analyze
            result = tool.analyze_top_risks(year, top_n, team, program)
            return result
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def format_risk_report(result: Dict[str, Any]) -> str:
    """格式化风险报告为自然语言"""
    if not result.get('success'):
        return f"分析失败: {result.get('error', '未知错误')}"
    
    if 'risk_distribution' not in result:
        return result.get('message', '操作完成')
    
    # 分析报告
    lines = []
    lines.append("## 缺陷风险分析报告")
    lines.append("")
    lines.append(f"**总缺陷数**: {result['total_count']}")
    lines.append("")
    
    # 风险分布
    lines.append("**风险分布**:")
    for level in ["极高风险", "高风险", "中等风险", "低风险", "极低风险"]:
        count = result['risk_distribution'].get(level, 0)
        pct = round(count / result['total_count'] * 100, 1) if result['total_count'] > 0 else 0
        lines.append(f"  - {level}: {count} ({pct}%)")
    
    # Top 风险
    lines.append("")
    lines.append(f"**Top {len(result['top_risks'])} 高风险缺陷**:")
    for item in result['top_risks']:
        lines.append(f"  {item['rank']}. [{item['score']:3d}] {item['defect_name']}")
        if item['factors']:
            lines.append(f"     因素: {', '.join(item['factors'][:3])}")
    
    # 团队分布
    if result.get('team_distribution'):
        lines.append("")
        lines.append("**Top 团队分布**:")
        for team, count in result['team_distribution'].items():
            lines.append(f"  - {team}: {count}")
    
    return "\n".join(lines)


# ============ 命令行入口 ============

if __name__ == "__main__":
    import sys
    
    action = sys.argv[1] if len(sys.argv) > 1 else 'analyze'
    year = int(sys.argv[2]) if len(sys.argv) > 2 else 2025
    top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    
    print(f"执行: {action}, 年份: {year}")
    
    if action == 'summary':
        result = execute_risk_analysis(year=year, action='summary')
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif action == 'update':
        result = execute_risk_analysis(year=year, action='update_db')
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        result = execute_risk_analysis(year=year, top_n=top_n, action='analyze')
        print(format_risk_report(result))
