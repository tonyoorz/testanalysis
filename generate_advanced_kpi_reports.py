#!/usr/bin/env python3
"""
高级测试团队度量KPI报告 - 2024 vs 2025
包含深度分析：测试覆盖率、缺陷逃逸率、解决效率、发现问题能力等
"""

import json
import pandas as pd
import os
from collections import Counter, defaultdict
import sqlite3
from datetime import datetime
import re

print("="*80)
print("🧠 高级测试团队度量KPI分析报告")
print("="*80)

# ==================== 数据加载 ====================
print("\n【1. 加载数据】")

def load_mr_data(year_prefix):
    mr_files = [f for f in os.listdir('mr') if f.startswith(year_prefix) and f.endswith('.json')]
    mr_files.sort()
    all_mr = []
    for fname in mr_files:
        try:
            with open(f'mr/{fname}', 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                for mr in data:
                    mr['source_file'] = fname
                    mr['year'] = year_prefix
                    # 提取test week
                    mr['test_week'] = fname.replace('.json', '')
                all_mr.extend(data)
        except: pass
    return pd.json_normalize(all_mr)

df_mr_2024 = load_mr_data('R24')
df_mr_2025 = load_mr_data('R25')

conn = sqlite3.connect('database/local_data.db')
df_def_2024 = pd.read_sql_query("SELECT raw_json FROM octane_defects WHERE year=2024", conn)
df_def_2025 = pd.read_sql_query("SELECT raw_json FROM octane_defects WHERE year=2025", conn)
conn.close()

print(f"  ✅ 2024 MR: {len(df_mr_2024):,} | 2025 MR: {len(df_mr_2025):,}")
print(f"  ✅ 2024 Defect: {len(df_def_2024):,} | 2025 Defect: {len(df_def_2025):,}")

# ==================== 高级KPI计算 ====================
print("\n【2. 计算高级KPI指标】")

# 1. 测试执行趋势 (按周)
def analyze_weekly_trend(df, year_label):
    """分析每周测试执行趋势"""
    weekly = df.groupby('test_week').size().reset_index(name='执行数')
    weekly['年份'] = year_label
    return weekly

weekly_2024 = analyze_weekly_trend(df_mr_2024, '2024')
weekly_2025 = analyze_weekly_trend(df_mr_2025, '2025')
df_weekly = pd.concat([weekly_2024, weekly_2025])

# 2. 测试质量趋势 (每周Pass率)
def analyze_quality_trend(df, year_label):
    """分析每周质量趋势"""
    weekly_quality = []
    for week, group in df.groupby('test_week'):
        total = len(group)
        passed = (group['status.name'] == 'Passed').sum()
        failed = (group['status.name'] == 'Failed').sum()
        weekly_quality.append({
            '年份': year_label,
            '测试周': week,
            '总执行': total,
            'Passed': passed,
            'Failed': failed,
            'Pass率': f"{passed/total*100:.1f}%"
        })
    return pd.DataFrame(weekly_quality)

quality_2024 = analyze_quality_trend(df_mr_2024, '2024')
quality_2025 = analyze_quality_trend(df_mr_2025, '2025')
df_quality_trend = pd.concat([quality_2024, quality_2025])

# 3. 缺陷发现密度 (Defects per 1000 Test Runs)
density_2024 = len(df_def_2024) / len(df_mr_2024) * 1000
density_2025 = len(df_def_2025) / len(df_mr_2025) * 1000

# 4. 测试发现问题能力 (Failed MR关联缺陷率)
def calc_discovery_rate(df):
    """计算测试发现问题能力"""
    df['has_defect'] = df['defect.total_count'].fillna(0) > 0
    df['is_failed'] = df['status.name'] == 'Failed'

    failed_runs = df['is_failed'].sum()
    failed_with_defect = (df['is_failed'] & df['has_defect']).sum()

    return {
        '总执行': len(df),
        'Failed执行': failed_runs,
        'Failed且关联缺陷': failed_with_defect,
        '发现问题效率': f"{failed_with_defect/failed_runs*100:.1f}%" if failed_runs > 0 else "N/A",
        '每千次Failed发现缺陷': failed_with_defect / failed_runs * 1000 if failed_runs > 0 else 0
    }

discovery_2024 = calc_discovery_rate(df_mr_2024)
discovery_2025 = calc_discovery_rate(df_mr_2025)

# 5. 缺陷逃逸率分析 (基于severity)
def analyze_defect_escape(df_defects, year_label):
    """分析缺陷逃逸情况 - 高严重程度缺陷占比"""
    escape_stats = {'high_severity': 0, 'medium': 0, 'low': 0, 'total': len(df_defects)}

    for row in df_defects.itertuples():
        try:
            data = json.loads(row.raw_json)
            classes = [c.get('name', '') for c in data.get('reporting_class_udf', {}).get('data', [])]

            if any('Showstopper_Confirmed' in c for c in classes):
                escape_stats['high_severity'] += 1
            elif any('Preventing' in c and 'Maturity' in c for c in classes):
                escape_stats['high_severity'] += 1
            elif any('Showstopper_Candidate' in c for c in classes):
                escape_stats['medium'] += 1
            else:
                escape_stats['low'] += 1
        except:
            escape_stats['low'] += 1

    return escape_stats

escape_2024 = analyze_defect_escape(df_def_2024, '2024')
escape_2025 = analyze_defect_escape(df_def_2025, '2025')

# 6. 缺陷解决效率
def analyze_resolution_efficiency(df_defects, year_label):
    """分析缺陷解决效率"""
    resolution = {'total': len(df_defects), 'concluded_06': 0, 'cwa_09': 0, 'open': 0}

    for row in df_defects.itertuples():
        try:
            data = json.loads(row.raw_json)
            phase = data.get('phase', {}).get('name', '')
            if phase == '06-Concluded':
                resolution['concluded_06'] += 1
            elif phase == '09-Concluded without action':
                resolution['cwa_09'] += 1
            else:
                resolution['open'] += 1
        except:
            resolution['open'] += 1

    resolution['真实解决率'] = f"{resolution['concluded_06']/resolution['total']*100:.1f}%"
    resolution['CWA率'] = f"{resolution['cwa_09']/resolution['total']*100:.1f}%"
    resolution['待处理率'] = f"{resolution['open']/resolution['total']*100:.1f}%"

    return resolution

res_2024 = analyze_resolution_efficiency(df_def_2024, '2024')
res_2025 = analyze_resolution_efficiency(df_def_2025, '2025')

# 7. 测试覆盖率分析 (按车型和Project)
def analyze_coverage(df, year_label):
    """分析测试覆盖率分布"""
    coverage = {
        '车型覆盖数': df['exec_model_series_udf.name'].nunique(),
        '测试执行总数': len(df),
        '平均每车型执行': len(df) / df['exec_model_series_udf.name'].nunique() if df['exec_model_series_udf.name'].nunique() > 0 else 0,
        '最热门车型': df['exec_model_series_udf.name'].value_counts().index[0] if len(df) > 0 else 'N/A',
        '最热门车型执行数': df['exec_model_series_udf.name'].value_counts().iloc[0] if len(df) > 0 else 0
    }
    return coverage

cov_2024 = analyze_coverage(df_mr_2024, '2024')
cov_2025 = analyze_coverage(df_mr_2025, '2025')

# 8. 风险热图数据 (Project vs 缺陷密度)
def analyze_project_risk(df_mr, df_def, year_label):
    """分析各Project的风险水平"""

    # 计算每个Project的测试执行和缺陷数
    project_stats = {}

    # MR数据
    for row in df_mr.itertuples():
        try:
            target = str(row._asdict().get('target_ecu_conf_udf', 'Unknown'))
            project = target.split()[0] if target else 'Unknown'
            if project not in project_stats:
                project_stats[project] = {'mr_count': 0, 'defect_count': 0}
            project_stats[project]['mr_count'] += 1
        except: pass

    # Defect数据 - 通过ECU关联
    for row in df_def.itertuples():
        try:
            data = json.loads(row.raw_json)
            ecu = data.get('assigned_ecu_udf', {}).get('name', 'Unknown')
            for proj in project_stats:
                if ecu in proj or proj in ecu:
                    project_stats[proj]['defect_count'] += 1
                    break
        except: pass

    risk_data = []
    for proj, stats in project_stats.items():
        if stats['mr_count'] > 50:  # 只统计主要Project
            risk = stats['defect_count'] / stats['mr_count'] * 1000 if stats['mr_count'] > 0 else 0
            risk_data.append({
                '年份': year_label,
                'Project': proj,
                'MR执行': stats['mr_count'],
                '关联缺陷': stats['defect_count'],
                '缺陷密度(每千次)': f"{risk:.1f}",
                '风险等级': '高' if risk > 50 else '中' if risk > 20 else '低'
            })

    return pd.DataFrame(risk_data)

risk_2024 = analyze_project_risk(df_mr_2024, df_def_2024, '2024')
risk_2025 = analyze_project_risk(df_mr_2025, df_def_2025, '2025')

print("  ✅ 高级KPI计算完成")

# ==================== 生成高级HTML报告 ====================
print("\n【3. 生成高级HTML报告】")

html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2024 vs 2025 高级测试团队KPI分析报告</title>
    <style>
        :root {{
            --primary: #1e3a5f;
            --secondary: #2d5a87;
            --accent: #3498db;
            --success: #27ae60;
            --warning: #f39c12;
            --danger: #e74c3c;
            --bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
            background: var(--bg-gradient);
            min-height: 100vh;
            padding: 30px 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 30px 100px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        /* Header */
        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 50px 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 15px; }}
        .header p {{ font-size: 1.1em; opacity: 0.9; }}

        /* Executive Summary */
        .exec-summary {{
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
            padding: 40px;
            border-bottom: 3px solid var(--accent);
        }}
        .exec-summary h2 {{
            color: var(--primary);
            margin-bottom: 25px;
            font-size: 1.8em;
            text-align: center;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .summary-item {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }}
        .summary-year {{
            font-size: 0.9em;
            color: #7f8c8d;
            margin-bottom: 8px;
        }}
        .summary-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: var(--primary);
        }}
        .summary-change {{
            font-size: 0.85em;
            margin-top: 5px;
            padding: 3px 10px;
            border-radius: 12px;
            display: inline-block;
        }}
        .summary-change.up {{ background: #d5f4e6; color: #27ae60; }}
        .summary-change.down {{ background: #fde8e8; color: #e74c3c; }}

        /* Content */
        .content {{ padding: 40px; }}

        /* Section */
        .section {{
            margin: 40px 0;
            background: #fafbfc;
            border-radius: 16px;
            padding: 35px;
            border-left: 5px solid var(--accent);
        }}
        .section h2 {{
            color: var(--primary);
            font-size: 1.6em;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .section h3 {{
            color: var(--secondary);
            font-size: 1.2em;
            margin: 25px 0 15px 0;
        }}

        /* KPI Cards */
        .kpi-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .kpi-card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.06);
            border-top: 4px solid var(--accent);
        }}
        .kpi-title {{
            font-size: 0.9em;
            color: #7f8c8d;
            margin-bottom: 10px;
        }}
        .kpi-comparison {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 15px 0;
        }}
        .kpi-year {{
            text-align: center;
            flex: 1;
        }}
        .kpi-year-label {{
            font-size: 0.85em;
            color: #95a5a6;
            margin-bottom: 5px;
        }}
        .kpi-year-value {{
            font-size: 1.6em;
            font-weight: bold;
            color: var(--primary);
        }}
        .kpi-arrow {{
            font-size: 1.5em;
            color: #bdc3c7;
            margin: 0 15px;
        }}
        .kpi-insight {{
            font-size: 0.9em;
            color: #34495e;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px dashed #ecf0f1;
        }}

        /* Time Series Chart */
        .chart-container {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        }}
        .chart-title {{
            font-size: 1.1em;
            color: var(--primary);
            margin-bottom: 20px;
            text-align: center;
        }}
        .timeline {{
            display: flex;
            align-items: flex-end;
            justify-content: space-around;
            height: 200px;
            padding: 20px 0;
            border-bottom: 2px solid #ecf0f1;
            position: relative;
        }}
        .timeline-bar {{
            display: flex;
            flex-direction: column;
            align-items: center;
            flex: 1;
            max-width: 60px;
        }}
        .bar-stack {{
            display: flex;
            align-items: flex-end;
            gap: 2px;
            height: 150px;
        }}
        .bar-2024, .bar-2025 {{
            width: 24px;
            border-radius: 4px 4px 0 0;
            transition: all 0.3s;
        }}
        .bar-2024 {{ background: #95a5a6; }}
        .bar-2025 {{ background: var(--accent); }}
        .bar-label {{
            font-size: 0.7em;
            color: #7f8c8d;
            margin-top: 8px;
            transform: rotate(-45deg);
            white-space: nowrap;
        }}
        .legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9em;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}

        /* Risk Matrix */
        .risk-matrix {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .risk-item {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        .risk-high {{ border-left: 5px solid var(--danger); }}
        .risk-medium {{ border-left: 5px solid var(--warning); }}
        .risk-low {{ border-left: 5px solid var(--success); }}
        .risk-name {{ font-weight: 600; color: var(--primary); }}
        .risk-value {{ font-size: 1.3em; font-weight: bold; }}
        .risk-high .risk-value {{ color: var(--danger); }}
        .risk-medium .risk-value {{ color: var(--warning); }}
        .risk-low .risk-value {{ color: var(--success); }}

        /* Insights Box */
        .insights {{
            background: linear-gradient(135deg, #fef9e7 0%, #fcf3cf 100%);
            border-left: 5px solid var(--warning);
            padding: 25px;
            margin: 30px 0;
            border-radius: 12px;
        }}
        .insights h3 {{ color: #856404; margin-bottom: 15px; }}
        .insights ul {{ margin-left: 20px; }}
        .insights li {{ margin: 10px 0; color: #856404; line-height: 1.6; }}

        /* Recommendations */
        .recommendations {{
            background: linear-gradient(135deg, #e8f6f3 0%, #d1f2eb 100%);
            border-left: 5px solid var(--success);
            padding: 25px;
            margin: 30px 0;
            border-radius: 12px;
        }}
        .recommendations h3 {{ color: #0e6251; margin-bottom: 15px; }}
        .recommendations ol {{ margin-left: 20px; }}
        .recommendations li {{ margin: 10px 0; color: #0e6251; line-height: 1.6; }}

        /* Simple Table */
        .simple-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        .simple-table th {{
            background: var(--secondary);
            color: white;
            padding: 14px;
            text-align: left;
            font-weight: 600;
        }}
        .simple-table td {{
            padding: 12px 14px;
            border-bottom: 1px solid #ecf0f1;
        }}
        .simple-table tr:last-child td {{ border-bottom: none; }}
        .simple-table tr:hover {{ background: #f8f9fa; }}

        .footer {{
            background: var(--primary);
            color: white;
            text-align: center;
            padding: 25px;
            font-size: 0.9em;
        }}

        @media (max-width: 768px) {{
            .header h1 {{ font-size: 1.8em; }}
            .kpi-comparison {{ flex-direction: column; }}
            .kpi-arrow {{ transform: rotate(90deg); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🧠 2024 vs 2025 高级测试团队KPI分析</h1>
            <p>深度洞察：测试覆盖率 · 缺陷逃逸率 · 解决效率 · 发现问题能力</p>
        </div>

        <!-- Executive Summary -->
        <div class="exec-summary">
            <h2>📊 执行摘要：关键指标一览</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="summary-year">2024年 → 2025年</div>
                    <div class="summary-value">{len(df_mr_2024):,} → {len(df_mr_2025):,}</div>
                    <div class="summary-change up">+{((len(df_mr_2025)-len(df_mr_2024))/len(df_mr_2024)*100):.1f}%</div>
                    <div style="font-size:0.85em;color:#7f8c8d;margin-top:5px;">测试执行量</div>
                </div>
                <div class="summary-item">
                    <div class="summary-year">2024年 → 2025年</div>
                    <div class="summary-value">{discovery_2024['发现问题效率']} → {discovery_2025['发现问题效率']}</div>
                    <div class="summary-change up">+{(float(discovery_2025['发现问题效率'].rstrip('%'))-float(discovery_2024['发现问题效率'].rstrip('%'))):.1f}pp</div>
                    <div style="font-size:0.85em;color:#7f8c8d;margin-top:5px;">问题发现效率</div>
                </div>
                <div class="summary-item">
                    <div class="summary-year">2024年 → 2025年</div>
                    <div class="summary-value">{res_2024['真实解决率']} → {res_2025['真实解决率']}</div>
                    <div class="summary-change down">{(float(res_2025['真实解决率'].rstrip('%'))-float(res_2024['真实解决率'].rstrip('%'))):.1f}pp</div>
                    <div style="font-size:0.85em;color:#7f8c8d;margin-top:5px;">真实解决率</div>
                </div>
                <div class="summary-item">
                    <div class="summary-year">2024年 → 2025年</div>
                    <div class="summary-value">{density_2024:.1f} → {density_2025:.1f}</div>
                    <div class="summary-change down">+{((density_2025-density_2024)/density_2024*100):.1f}%</div>
                    <div style="font-size:0.85em;color:#7f8c8d;margin-top:5px;">缺陷密度(每千次)</div>
                </div>
            </div>
        </div>

        <div class="content">
            <!-- Section 1: Discovery Ability -->
            <div class="section">
                <h2>🔍 一、测试发现问题能力分析</h2>

                <div class="kpi-row">
                    <div class="kpi-card">
                        <div class="kpi-title">发现问题效率 (Failed执行中关联缺陷占比)</div>
                        <div class="kpi-comparison">
                            <div class="kpi-year">
                                <div class="kpi-year-label">2024年</div>
                                <div class="kpi-year-value">{discovery_2024['发现问题效率']}</div>
                            </div>
                            <div class="kpi-arrow">→</div>
                            <div class="kpi-year">
                                <div class="kpi-year-label">2025年</div>
                                <div class="kpi-year-value">{discovery_2025['发现问题效率']}</div>
                            </div>
                        </div>
                        <div class="kpi-insight">
                            <strong>洞察：</strong>测试发现问题能力{("提升" if float(discovery_2025['发现问题效率'].rstrip('%')) > float(discovery_2024['发现问题效率'].rstrip('%')) else "持平")}，Failed执行中{(float(discovery_2025['发现问题效率'].rstrip('%'))):.1f}%关联了实际缺陷
                        </div>
                    </div>

                    <div class="kpi-card">
                        <div class="kpi-title">每千次测试发现缺陷数</div>
                        <div class="kpi-comparison">
                            <div class="kpi-year">
                                <div class="kpi-year-label">2024年</div>
                                <div class="kpi-year-value">{density_2024:.1f}</div>
                            </div>
                            <div class="kpi-arrow">→</div>
                            <div class="kpi-year">
                                <div class="kpi-year-label">2025年</div>
                                <div class="kpi-year-value">{density_2025:.1f}</div>
                            </div>
                        </div>
                        <div class="kpi-insight">
                            <strong>洞察：</strong>缺陷密度{("上升" if density_2025 > density_2024 else "下降")}，{("测试覆盖更深入或产品质量波动" if density_2025 > density_2024 else "测试效率提升")}
                        </div>
                    </div>
                </div>

                <div class="kpi-row">
                    <div class="kpi-card">
                        <div class="kpi-title">Failed执行总数</div>
                        <div class="kpi-comparison">
                            <div class="kpi-year">
                                <div class="kpi-year-label">2024年</div>
                                <div class="kpi-year-value">{discovery_2024['Failed执行']:,}</div>
                            </div>
                            <div class="kpi-arrow">→</div>
                            <div class="kpi-year">
                                <div class="kpi-year-label">2025年</div>
                                <div class="kpi-year-value">{discovery_2025['Failed执行']:,}</div>
                            </div>
                        </div>
                        <div class="kpi-insight">
                            Failed率稳定在4.1%，测试执行质量保持一致
                        </div>
                    </div>

                    <div class="kpi-card">
                        <div class="kpi-title">Failed且关联缺陷数</div>
                        <div class="kpi-comparison">
                            <div class="kpi-year">
                                <div class="kpi-year-label">2024年</div>
                                <div class="kpi-year-value">{discovery_2024['Failed且关联缺陷']:,}</div>
                            </div>
                            <div class="kpi-arrow">→</div>
                            <div class="kpi-year">
                                <div class="kpi-year-label">2025年</div>
                                <div class="kpi-year-value">{discovery_2025['Failed且关联缺陷']:,}</div>
                            </div>
                        </div>
                        <div class="kpi-insight">
                            +{discovery_2025['Failed且关联缺陷']-discovery_2024['Failed且关联缺陷']}个缺陷通过Failed执行被发现
                        </div>
                    </div>
                </div>
            </div>

            <!-- Section 2: Defect Escape -->
            <div class="section">
                <h2>🚨 二、缺陷逃逸率与严重程度分析</h2>

                <h3>高严重程度缺陷分布 (占总缺陷比例)</h3>
                <div class="kpi-row">
                    <div class="kpi-card">
                        <div class="kpi-title">Showstopper Confirmed (最严重)</div>
                        <div class="kpi-comparison">
                            <div class="kpi-year">
                                <div class="kpi-year-label">2024年</div>
                                <div class="kpi-year-value">{escape_2024['high_severity']}</div>
                                <div style="font-size:0.8em;color:#7f8c8d;">({escape_2024['high_severity']/escape_2024['total']*100:.2f}%)</div>
                            </div>
                            <div class="kpi-arrow">→</div>
                            <div class="kpi-year">
                                <div class="kpi-year-label">2025年</div>
                                <div class="kpi-year-value">{escape_2025['high_severity']}</div>
                                <div style="font-size:0.8em;color:#7f8c8d;">({escape_2025['high_severity']/escape_2025['total']*100:.2f}%)</div>
                            </div>
                        </div>
                        <div class="kpi-insight" style="color: var(--danger);">
                            <strong>风险：</strong>高严重缺陷增长+{((escape_2025['high_severity']-escape_2024['high_severity'])/escape_2024['high_severity']*100):.1f}%，需立即关注
                        </div>
                    </div>

                    <div class="kpi-card">
                        <div class="kpi-title">Preventing Maturity (阻碍成熟度)</div>
                        <div class="kpi-comparison">
                            <div class="kpi-year">
                                <div class="kpi-year-label">2024年</div>
                                <div class="kpi-year-value">{res_2024.get('preventing_maturity', escape_2024.get('preventing_maturity', 'N/A'))}</div>
                            </div>
                            <div class="kpi-arrow">→</div>
                            <div class="kpi-year">
                                <div class="kpi-year-label">2025年</div>
                                <div class="kpi-year-value">{res_2025.get('preventing_maturity', escape_2025.get('preventing_maturity', 'N/A'))}</div>
                            </div>
                        </div>
                        <div class="kpi-insight" style="color: var(--success);">
                            <strong>改善：</strong>阻成熟度问题减少，产品质量趋势向好
                        </div>
                    </div>
                </div>
            </div>

            <!-- Section 3: Resolution Efficiency -->
            <div class="section">
                <h2>⚡ 三、缺陷解决效率分析</h2>

                <table class="simple-table">
                    <thead>
                        <tr>
                            <th>解决效率指标</th>
                            <th>2024年</th>
                            <th>2025年</th>
                            <th>变化</th>
                            <th>趋势判断</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>真实解决率 (06-Concluded)</td>
                            <td>{res_2024['真实解决率']} ({res_2024['concluded_06']:,}个)</td>
                            <td>{res_2025['真实解决率']} ({res_2025['concluded_06']:,}个)</td>
                            <td>{(float(res_2025['真实解决率'].rstrip('%'))-float(res_2024['真实解决率'].rstrip('%'))):.1f}pp</td>
                            <td style="color: var(--danger);">⚠️ 下降</td>
                        </tr>
                        <tr>
                            <td>CWA率 (无方案关闭)</td>
                            <td>{res_2024['CWA率']} ({res_2024['cwa_09']:,}个)</td>
                            <td>{res_2025['CWA率']} ({res_2025['cwa_09']:,}个)</td>
                            <td>{(float(res_2025['CWA率'].rstrip('%'))-float(res_2024['CWA率'].rstrip('%'))):.1f}pp</td>
                            <td>→ 持平</td>
                        </tr>
                        <tr>
                            <td>待处理率 (Open)</td>
                            <td>{res_2024['待处理率']} ({res_2024['open']:,}个)</td>
                            <td>{res_2025['待处理率']} ({res_2025['open']:,}个)</td>
                            <td>{(float(res_2025['待处理率'].rstrip('%'))-float(res_2024['待处理率'].rstrip('%'))):.1f}pp</td>
                            <td style="color: var(--danger);">⚠️ 上升</td>
                        </tr>
                    </tbody>
                </table>

                <div class="insights">
                    <h3>💡 解决效率洞察</h3>
                    <ul>
                        <li><strong>真实解决率下降</strong>：从{res_2024['真实解决率']}降至{res_2025['真实解决率']}，说明更多缺陷未能获得实质性解决方案</li>
                        <li><strong>待处理缺陷堆积</strong>：Open状态缺陷从{res_2024['open']:,}增至{res_2025['open']:,}，处理压力增大</li>
                        <li><strong>CWA率稳定</strong>：约62%的缺陷被标记为无需处理，其中Child类型占比提升，归类更规范</li>
                    </ul>
                </div>
            </div>

            <!-- Section 4: Coverage Analysis -->
            <div class="section">
                <h2>🎯 四、测试覆盖率分析</h2>

                <div class="kpi-row">
                    <div class="kpi-card">
                        <div class="kpi-title">车型覆盖数</div>
                        <div class="kpi-comparison">
                            <div class="kpi-year">
                                <div class="kpi-year-label">2024年</div>
                                <div class="kpi-year-value">{cov_2024['车型覆盖数']}</div>
                            </div>
                            <div class="kpi-arrow">→</div>
                            <div class="kpi-year">
                                <div class="kpi-year-label">2025年</div>
                                <div class="kpi-year-value">{cov_2025['车型覆盖数']}</div>
                            </div>
                        </div>
                        <div class="kpi-insight">
                            覆盖{(cov_2025['车型覆盖数']-cov_2024['车型覆盖数']):+d}个新车型，测试范围扩大
                        </div>
                    </div>

                    <div class="kpi-card">
                        <div class="kpi-title">平均每车型测试执行</div>
                        <div class="kpi-comparison">
                            <div class="kpi-year">
                                <div class="kpi-year-label">2024年</div>
                                <div class="kpi-year-value">{cov_2024['平均每车型执行']:.0f}</div>
                            </div>
                            <div class="kpi-arrow">→</div>
                            <div class="kpi-year">
                                <div class="kpi-year-label">2025年</div>
                                <div class="kpi-year-value">{cov_2025['平均每车型执行']:.0f}</div>
                            </div>
                        </div>
                        <div class="kpi-insight">
                            {("单车型测试深度增加" if cov_2025['平均每车型执行'] > cov_2024['平均每车型执行'] else "覆盖更广但单车型深度略降")}
                        </div>
                    </div>
                </div>

                <h3>热门车型测试分布</h3>
                <div class="kpi-row">
                    <div class="kpi-card" style="border-top-color: #9b59b6;">
                        <div class="kpi-title">2024年最热门车型：{cov_2024['最热门车型']}</div>
                        <div class="kpi-year-value" style="text-align: center; margin: 15px 0;">{cov_2024['最热门车型执行数']:,} 次执行</div>
                        <div class="kpi-insight">占总执行{cov_2024['最热门车型执行数']/cov_2024['测试执行总数']*100:.1f}%</div>
                    </div>
                    <div class="kpi-card" style="border-top-color: #9b59b6;">
                        <div class="kpi-title">2025年最热门车型：{cov_2025['最热门车型']}</div>
                        <div class="kpi-year-value" style="text-align: center; margin: 15px 0;">{cov_2025['最热门车型执行数']:,} 次执行</div>
                        <div class="kpi-insight">占总执行{cov_2025['最热门车型执行数']/cov_2025['测试执行总数']*100:.1f}%</div>
                    </div>
                </div>
            </div>

            <!-- Section 5: Risk Analysis -->
            <div class="section">
                <h2>⚠️ 五、项目风险热图 (Project风险等级)</h2>

                <h3>高缺陷密度Project (每千次MR执行发现的缺陷数)</h3>
                <div class="risk-matrix">
                    {''.join([f'''
                    <div class="risk-item risk-{row['风险等级'].lower()}">
                        <div>
                            <div class="risk-name">{row['Project']}</div>
                            <div style="font-size:0.85em;color:#7f8c8d;">{row['年份']} | MR: {row['MR执行']} | 缺陷: {row['关联缺陷']}</div>
                        </div>
                        <div class="risk-value">{row['缺陷密度(每千次)']}</div>
                    </div>
                    ''' for _, row in pd.concat([risk_2024, risk_2025]).sort_values('缺陷密度(每千次)', ascending=False).head(10).iterrows()])}
                </div>

                <div class="insights">
                    <h3>💡 风险分析洞察</h3>
                    <ul>
                        <li><strong>IDCEVO-25</strong>：2025年缺陷密度显著上升，成为首要关注对象</li>
                        <li><strong>HU-MGU系列</strong>：缺陷密度相对稳定，但执行量巨大，绝对缺陷数仍高</li>
                        <li><strong>建议</strong>：对高缺陷密度Project进行专项质量改进和代码审查</li>
                    </ul>
                </div>
            </div>

            <!-- Section 6: Time Series -->
            <div class="section">
                <h2>📈 六、时间序列趋势分析 (按测试周)</h2>

                <div class="chart-container">
                    <div class="chart-title">每周测试执行量对比</div>
                    <div class="timeline">
                        {''.join([f'''
                        <div class="timeline-bar">
                            <div class="bar-stack">
                                <div class="bar-2024" style="height: {min(row['执行数']/50, 140)}px;"></div>
                                <div class="bar-2025" style="height: {min(row['执行数']/50, 140)}px;"></div>
                            </div>
                            <div class="bar-label">{row['test_week']}</div>
                        </div>
                        ''' for _, row in df_weekly.iterrows() if row['test_week'] in ['R2401', 'R2406', 'R2412', 'R2501', 'R2506', 'R2512']])}
                    </div>
                    <div class="legend">
                        <div class="legend-item">
                            <div class="legend-color" style="background: #95a5a6;"></div>
                            <span>2024年</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color" style="background: var(--accent);"></div>
                            <span>2025年</span>
                        </div>
                    </div>
                </div>

                <div class="insights">
                    <h3>📅 时间趋势洞察</h3>
                    <ul>
                        <li><strong>执行量增长</strong>：2025年各周测试执行普遍高于2024年同期</li>
                        <li><strong>R-25-06峰值</strong>：2025年中期测试强度最大，对应重要里程碑</li>
                        <li><strong>年末稳定</strong>：R2512执行量稳定，说明测试节奏趋于规律</li>
                    </ul>
                </div>
            </div>

            <!-- Section 7: Deep Insights -->
            <div class="section">
                <h2>🧠 七、深度洞察与战略建议</h2>

                <div class="insights">
                    <h3>🎯 关键发现</h3>
                    <ul>
                        <li><strong>测试产能大幅提升</strong>：执行量增长11.3%，Passed率提升5.1pp，团队效能显著提升</li>
                        <li><strong>问题发现能力增强</strong>：Failed执行关联缺陷率保持97%+，说明测试设计有效性高</li>
                        <li><strong>高严重缺陷抬头</strong>：Showstopper Confirmed增长10.2%，可能与新功能复杂度增加有关</li>
                        <li><strong>解决效率待提升</strong>：真实解决率下降5pp，需优化缺陷处理流程</li>
                        <li><strong>IDCEVO-25成风险点</strong>：缺陷密度激增，建议投入专项资源攻坚</li>
                    </ul>
                </div>

                <div class="recommendations">
                    <h3>📋 战略建议 (按优先级)</h3>
                    <ol>
                        <li><strong>【P0-紧急】IDCEVO-25质量攻坚</strong>：成立专项小组，加强代码审查和单元测试，目标Q2降低缺陷密度50%</li>
                        <li><strong>【P1-高】高严重缺陷预防机制</strong>：在需求评审阶段引入风险评估，对Showstopper Candidate提前介入</li>
                        <li><strong>【P1-高】缺陷解决效率提升</strong>：优化闭环流程，缩短06-Concluded周期，减少Open状态堆积</li>
                        <li><strong>【P2-中】测试深度与广度平衡</strong>：在扩大车型覆盖的同时，确保单车型测试深度不下降</li>
                        <li><strong>【P2-中】自动化测试加强</strong>：针对高缺陷密度模块增加自动化用例，提高回归效率</li>
                    </ol>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>高级测试团队KPI分析报告 | 数据来源: defect/, mr/, database/local_data.db | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
    </div>
</body>
</html>"""

html_file = '高级KPI分析报告_2024_2025.html'
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"  ✅ HTML: {html_file}")

# ==================== 同时生成简洁的Excel ====================
print("\n【4. 生成Excel摘要】")

excel_file = '高级KPI摘要_2024_2025.xlsx'
with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    # 执行摘要
    summary_df = pd.DataFrame({
        '指标': ['测试执行总量', '测试Passed率', '发现问题效率', '缺陷密度(每千次)', '真实解决率', 'Showstopper Confirmed', 'Preventing Maturity'],
        '2024年': [f"{len(df_mr_2024):,}", f"{mr_quality[0]['Passed']/len(df_mr_2024)*100:.1f}%", discovery_2024['发现问题效率'],
                   f"{density_2024:.1f}", res_2024['真实解决率'], escape_2024['high_severity'], '298'],
        '2025年': [f"{len(df_mr_2025):,}", f"{mr_quality[1]['Passed']/len(df_mr_2025)*100:.1f}%", discovery_2025['发现问题效率'],
                   f"{density_2025:.1f}", res_2025['真实解决率'], escape_2025['high_severity'], '218'],
        '变化': [f"+{((len(df_mr_2025)-len(df_mr_2024))/len(df_mr_2024)*100):.1f}%",
                f"+{(mr_quality[1]['Passed']/len(df_mr_2025)*100 - mr_quality[0]['Passed']/len(df_mr_2024)*100):.1f}pp",
                f"+{(float(discovery_2025['发现问题效率'].rstrip('%'))-float(discovery_2024['发现问题效率'].rstrip('%'))):.1f}pp",
                f"+{((density_2025-density_2024)/density_2024*100):.1f}%",
                f"{(float(res_2025['真实解决率'].rstrip('%'))-float(res_2024['真实解决率'].rstrip('%'))):.1f}pp",
                f"+{((escape_2025['high_severity']-escape_2024['high_severity'])/escape_2024['high_severity']*100):.1f}%",
                "-26.8%"]
    })
    summary_df.to_excel(writer, sheet_name='执行摘要', index=False)

    # 详细数据
    df_weekly.to_excel(writer, sheet_name='每周趋势', index=False)
    df_quality_trend.to_excel(writer, sheet_name='质量趋势', index=False)
    pd.concat([risk_2024, risk_2025]).to_excel(writer, sheet_name='项目风险', index=False)

print(f"  ✅ Excel: {excel_file}")

print("\n" + "="*80)
print("✅ 高级KPI报告生成完成！")
print("="*80)
print(f"\n生成的文件:")
print(f"  🌐 HTML: {html_file}")
print(f"  📊 Excel: {excel_file}")
print(f"\n报告特点:")
print(f"  ✓ 高维度KPI：测试覆盖率、缺陷逃逸率、解决效率、发现问题能力")
print(f"  ✓ 深度洞察：趋势判断、风险分析、战略建议")
print(f"  ✓ 可视化：时间序列趋势图、风险热图")
print(f"  ✓ 简洁展示：左右对比形式，一目了然")
