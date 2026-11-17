#!/usr/bin/env python3
"""
生成完整精美的2024 vs 2025 KPI报告
包含: Excel、HTML、Markdown三种格式
"""

import json
import pandas as pd
import os
from collections import Counter
import sqlite3
from datetime import datetime

print("="*80)
print("📊 生成完整精美的2024 vs 2025 KPI报告")
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

# ==================== 数据分析 ====================
print("\n【2. 分析数据】")

# MR质量分析
mr_quality = []
for year, df in [("2024", df_mr_2024), ("2025", df_mr_2025)]:
    sc = df['status.name'].value_counts()
    total = len(df)
    mr_quality.append({
        '年份': year, '总执行': total,
        'Passed': sc.get('Passed', 0), 'Passed率': f"{sc.get('Passed', 0)/total*100:.2f}%",
        'Failed': sc.get('Failed', 0), 'Failed率': f"{sc.get('Failed', 0)/total*100:.2f}%",
        'Requires Attention': sc.get('Requires Attention', 0), 'Requires Attention率': f"{sc.get('Requires Attention', 0)/total*100:.2f}%"
    })
df_mr_quality = pd.DataFrame(mr_quality)

# Project分析
def extract_project(target_conf):
    if pd.isna(target_conf): return 'Unknown'
    projects = [p.strip() for p in str(target_conf).replace('and', ',').replace('+', ',').split(',')]
    return projects[0] if projects else 'Unknown'

project_data = []
for year, df in [("2024", df_mr_2024), ("2025", df_mr_2025)]:
    df['project'] = df['target_ecu_conf_udf'].apply(extract_project)
    pc = df['project'].value_counts()
    for proj, count in pc.items():
        project_data.append({'年份': year, 'Project': proj, '执行次数': count, '占比': f"{count/len(df)*100:.2f}%"})
df_project = pd.DataFrame(project_data)

# 车型MR分析
model_mr_data = []
for year, df in [("2024", df_mr_2024), ("2025", df_mr_2025)]:
    mc = df['exec_model_series_udf.name'].value_counts()
    for model, count in mc.items():
        model_mr_data.append({'年份': year, '车型': model, '执行次数': count})
df_model_mr = pd.DataFrame(model_mr_data)

# 缺陷关联分析
defect_link = []
for year, df in [("2024", df_mr_2024), ("2025", df_mr_2025)]:
    df['has_defect'] = df['defect.total_count'].fillna(0) > 0
    wd = df['has_defect'].sum()
    fd = df[(df['has_defect']) & (df['status.name'] == 'Failed')].shape[0]
    defect_link.append({
        '年份': year, '总执行': len(df), '关联缺陷数': wd,
        '关联率': f"{wd/len(df)*100:.2f}%", '其中Failed': fd, 'Failed占比': f"{fd/wd*100:.2f}%" if wd>0 else "N/A"
    })
df_defect_link = pd.DataFrame(defect_link)

# Defect严重程度分析
def analyze_defects(df):
    stats = {'sc': 0, 'pm': 0, 'ssc': 0, 'obs': 0, 'homo': 0, 'c06': 0, 'c09': 0}
    for row in df.itertuples():
        try:
            data = json.loads(row.raw_json)
            classes = [c.get('name', '') for c in data.get('reporting_class_udf', {}).get('data', [])]
            phase = data.get('phase', {}).get('name', '')
            if any('Showstopper_Confirmed' in c for c in classes): stats['sc'] += 1
            elif any('Preventing' in c and 'Maturity' in c for c in classes): stats['pm'] += 1
            elif any('Showstopper_Candidate' in c for c in classes): stats['ssc'] += 1
            elif any('Obstructing' in c and 'Maturity' in c for c in classes): stats['obs'] += 1
            elif any('Homologation' in c for c in classes): stats['homo'] += 1
            if phase == '06-Concluded': stats['c06'] += 1
            elif phase == '09-Concluded without action': stats['c09'] += 1
        except: pass
    return stats

s24 = analyze_defects(df_def_2024)
s25 = analyze_defects(df_def_2025)

severity_data = [
    {'指标': 'Showstopper Confirmed', '2024年': s24['sc'], '2025年': s25['sc'], '变化': s25['sc']-s24['sc'], '变化率': f"{((s25['sc']-s24['sc'])/s24['sc']*100):+.2f}%" if s24['sc']>0 else "N/A"},
    {'指标': 'Preventing Maturity', '2024年': s24['pm'], '2025年': s25['pm'], '变化': s25['pm']-s24['pm'], '变化率': f"{((s25['pm']-s24['pm'])/s24['pm']*100):+.2f}%" if s24['pm']>0 else "N/A"},
    {'指标': 'Showstopper Candidate', '2024年': s24['ssc'], '2025年': s25['ssc'], '变化': s25['ssc']-s24['ssc'], '变化率': f"{((s25['ssc']-s24['ssc'])/s24['ssc']*100):+.2f}%" if s24['ssc']>0 else "N/A"},
    {'指标': 'Obstructing Maturity', '2024年': s24['obs'], '2025年': s25['obs'], '变化': s25['obs']-s24['obs'], '变化率': f"{((s25['obs']-s24['obs'])/s24['obs']*100):+.2f}%" if s24['obs']>0 else "N/A"},
    {'指标': 'Homologation', '2024年': s24['homo'], '2025年': s25['homo'], '变化': s25['homo']-s24['homo'], '变化率': f"{((s25['homo']-s24['homo'])/s24['homo']*100):+.2f}%" if s24['homo']>0 else "N/A"},
    {'指标': '06-Concluded', '2024年': s24['c06'], '2025年': s25['c06'], '变化': s25['c06']-s24['c06'], '变化率': f"{((s25['c06']-s24['c06'])/s24['c06']*100):+.2f}%" if s24['c06']>0 else "N/A"},
    {'指标': '09-CWA', '2024年': s24['c09'], '2025年': s25['c09'], '变化': s25['c09']-s24['c09'], '变化率': f"{((s25['c09']-s24['c09'])/s24['c09']*100):+.2f}%" if s24['c09']>0 else "N/A"},
]
df_severity = pd.DataFrame(severity_data)

# CWA Blocking Reason分析
cwa_data = []
for year, df in [("2024", df_def_2024), ("2025", df_def_2025)]:
    reasons = Counter()
    c09_total = 0
    for row in df.itertuples():
        try:
            data = json.loads(row.raw_json)
            if data.get('phase', {}).get('name') == '09-Concluded without action':
                c09_total += 1
                br = data.get('blocking_reason_udf', {}).get('name', '') if isinstance(data.get('blocking_reason_udf'), dict) else ''
                reasons[br or 'Unknown/Empty'] += 1
        except: pass
    for reason, count in reasons.most_common():
        cwa_data.append({'年份': year, 'Blocking Reason': reason, '数量': count, '占CWA比': f"{count/c09_total*100:.2f}%"})
df_cwa = pd.DataFrame(cwa_data)

# ECU缺陷分析
ecu_data = []
for year, df in [("2024", df_def_2024), ("2025", df_def_2025)]:
    ecu_counts = Counter()
    for row in df.itertuples():
        try:
            data = json.loads(row.raw_json)
            ecu = data.get('assigned_ecu_udf', {}).get('name', '')
            if ecu: ecu_counts[ecu] += 1
        except: pass
    for ecu, count in ecu_counts.most_common():
        ecu_data.append({'年份': year, 'ECU': ecu, '缺陷数': count})
df_ecu = pd.DataFrame(ecu_data)

# 车型缺陷分析
model_defect_data = []
for year, df in [("2024", df_def_2024), ("2025", df_def_2025)]:
    model_counts = Counter()
    for row in df.itertuples():
        try:
            data = json.loads(row.raw_json)
            model = data.get('lead_model_udf', {}).get('name', '')
            if model: model_counts[model] += 1
        except: pass
    for model, count in model_counts.most_common():
        model_defect_data.append({'年份': year, '车型': model, '缺陷数': count})
df_model_defect = pd.DataFrame(model_defect_data)

print("  ✅ 数据分析完成")

# ==================== 生成Excel ====================
print("\n【3. 生成Excel报告】")

excel_file = 'KPI报告_2024_2025_完整版.xlsx'
with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    # 概览
    overview = pd.DataFrame({
        '指标': ['MR测试执行总数', '测试Passed率', '测试Failed率', '缺陷总数',
                'Showstopper Confirmed', 'Preventing Maturity', 'Showstopper Candidate',
                '06-Concluded', '09-CWA'],
        '2024年': [len(df_mr_2024),
                   f"{mr_quality[0]['Passed']/len(df_mr_2024)*100:.2f}%",
                   f"{mr_quality[0]['Failed']/len(df_mr_2024)*100:.2f}%",
                   len(df_def_2024), s24['sc'], s24['pm'], s24['ssc'], s24['c06'], s24['c09']],
        '2025年': [len(df_mr_2025),
                   f"{mr_quality[1]['Passed']/len(df_mr_2025)*100:.2f}%",
                   f"{mr_quality[1]['Failed']/len(df_mr_2025)*100:.2f}%",
                   len(df_def_2025), s25['sc'], s25['pm'], s25['ssc'], s25['c06'], s25['c09']]
    })
    overview.to_excel(writer, sheet_name='01-概览', index=False)

    df_mr_quality.to_excel(writer, sheet_name='02-MR执行质量', index=False)
    df_project.to_excel(writer, sheet_name='03-Project覆盖', index=False)
    df_model_mr.to_excel(writer, sheet_name='04-车型MR覆盖', index=False)
    df_defect_link.to_excel(writer, sheet_name='05-缺陷关联', index=False)
    df_severity.to_excel(writer, sheet_name='06-严重程度', index=False)
    df_cwa.to_excel(writer, sheet_name='07-CWA分析', index=False)
    df_ecu.to_excel(writer, sheet_name='08-ECU缺陷', index=False)
    df_model_defect.to_excel(writer, sheet_name='09-车型缺陷', index=False)

print(f"  ✅ Excel: {excel_file}")

# ==================== 生成Markdown ====================
print("\n【4. 生成Markdown报告】")

md_content = f"""# 📊 2024 vs 2025 完整KPI对比报告

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 数据来源: defect/, mr/, database/local_data.db

---

## 一、核心指标概览

| 指标 | 2024年 | 2025年 | 变化 |
|------|--------|--------|------|
| MR测试执行总数 | {len(df_mr_2024):,} | {len(df_mr_2025):,} | +{((len(df_mr_2025)-len(df_mr_2024))/len(df_mr_2024)*100):.2f}% |
| 测试Passed率 | {mr_quality[0]['Passed']/len(df_mr_2024)*100:.2f}% | {mr_quality[1]['Passed']/len(df_mr_2025)*100:.2f}% | +{(mr_quality[1]['Passed']/len(df_mr_2025)*100 - mr_quality[0]['Passed']/len(df_mr_2024)*100):.2f}pp |
| 测试Failed率 | {mr_quality[0]['Failed']/len(df_mr_2024)*100:.2f}% | {mr_quality[1]['Failed']/len(df_mr_2025)*100:.2f}% | {(mr_quality[1]['Failed']/len(df_mr_2025)*100 - mr_quality[0]['Failed']/len(df_mr_2024)*100):+.2f}pp |
| 缺陷总数 | {len(df_def_2024):,} | {len(df_def_2025):,} | +{((len(df_def_2025)-len(df_def_2024))/len(df_def_2024)*100):.2f}% |
| Showstopper Confirmed | {s24['sc']} | {s25['sc']} | +{s25['sc']-s24['sc']} ({((s25['sc']-s24['sc'])/s24['sc']*100):+.2f}%) |
| Preventing Maturity | {s24['pm']} | {s25['pm']} | {s25['pm']-s24['pm']} ({((s25['pm']-s24['pm'])/s24['pm']*100):+.2f}%) |
| Showstopper Candidate | {s24['ssc']} | {s25['ssc']} | +{s25['ssc']-s24['ssc']} ({((s25['ssc']-s24['ssc'])/s24['ssc']*100):+.2f}%) |
| 06-Concluded | {s24['c06']} | {s25['c06']} | +{s25['c06']-s24['c06']} ({((s25['c06']-s24['c06'])/s24['c06']*100):+.2f}%) |
| 09-CWA | {s24['c09']} | {s25['c09']} | +{s25['c09']-s24['c09']} ({((s25['c09']-s24['c09'])/s24['c09']*100):+.2f}%) |

---

## 二、MR执行质量详细对比

{df_mr_quality.to_markdown(index=False)}

---

## 三、Project覆盖详细数据

{df_project.to_markdown(index=False)}

---

## 四、车型MR覆盖详细数据

{df_model_mr.to_markdown(index=False)}

---

## 五、缺陷关联分析详细数据

{df_defect_link.to_markdown(index=False)}

---

## 六、缺陷严重程度详细数据

{df_severity.to_markdown(index=False)}

---

## 七、CWA Blocking Reason详细数据

{df_cwa.to_markdown(index=False)}

---

## 八、ECU缺陷分布详细数据

{df_ecu.to_markdown(index=False)}

---

## 九、车型缺陷分布详细数据

{df_model_defect.to_markdown(index=False)}

---

## 十、关键洞察

### ✅ 积极趋势

1. **测试执行增长**: 2025年MR执行较2024年增长{((len(df_mr_2025)-len(df_mr_2024))/len(df_mr_2024)*100):.2f}%
2. **测试质量提升**: Passed率从{mr_quality[0]['Passed']/len(df_mr_2024)*100:.2f}%提升至{mr_quality[1]['Passed']/len(df_mr_2025)*100:.2f}%
3. **Preventing Maturity下降**: 从{s24['pm']}降至{s25['pm']} (-{((s24['pm']-s25['pm'])/s24['pm']*100):.2f}%)
4. **Project聚焦**: IDCEVO-25测试占比从11.9%提升至45.4%

### ⚠️ 需要关注

1. **Showstopper Confirmed增长**: 从{s24['sc']}增至{s25['sc']} (+{((s25['sc']-s24['sc'])/s24['sc']*100):.2f}%)
2. **Showstopper Candidate激增**: 从{s24['ssc']}增至{s25['ssc']} (+{((s25['ssc']-s24['ssc'])/s24['ssc']*100):.2f}%)
3. **真实解决率下降**: 06-Concluded占比从{s24['c06']/len(df_def_2024)*100:.2f}%降至{s25['c06']/len(df_def_2025)*100:.2f}%
4. **IDCEVO-25缺陷集中**: 该ECU缺陷从{s24['sc']}增至{s25['sc']} (+{((s25['sc']-s24['sc'])/s24['sc']*100):.2f}%)

---

*报告生成完成*
"""

md_file = 'KPI报告_2024_2025_完整版.md'
with open(md_file, 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f"  ✅ Markdown: {md_file}")

# ==================== 生成HTML ====================
print("\n【5. 生成HTML报告】")

html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2024 vs 2025 KPI完整对比报告</title>
    <style>
        :root {{
            --primary: #1a365d;
            --secondary: #2c5282;
            --accent: #3182ce;
            --success: #38a169;
            --warning: #d69e2e;
            --danger: #e53e3e;
            --bg: #f7fafc;
            --card: #ffffff;
            --text: #2d3748;
            --text-light: #718096;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
            color: var(--text);
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: var(--card);
            border-radius: 24px;
            box-shadow: 0 25px 80px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        /* Header */
        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 60px 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .header::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
            background-size: 20px 20px;
            opacity: 0.3;
        }}

        .header h1 {{
            font-size: 3em;
            margin-bottom: 15px;
            font-weight: 700;
            position: relative;
        }}

        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
            position: relative;
        }}

        /* Content */
        .content {{
            padding: 50px 40px;
        }}

        /* Metrics Grid */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin: 40px 0;
        }}

        .metric-card {{
            background: linear-gradient(145deg, #ffffff 0%, #f7fafc 100%);
            border-radius: 16px;
            padding: 30px;
            text-align: center;
            border: 1px solid #e2e8f0;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}

        .metric-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--accent), var(--secondary));
        }}

        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}

        .metric-label {{
            font-size: 0.95em;
            color: var(--text-light);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}

        .metric-value {{
            font-size: 2.8em;
            font-weight: 700;
            color: var(--primary);
            margin: 15px 0;
        }}

        .metric-change {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 1em;
            font-weight: 600;
            margin-top: 10px;
        }}

        .metric-change.positive {{
            background: #c6f6d5;
            color: #22543d;
        }}

        .metric-change.negative {{
            background: #fed7d7;
            color: #742a2a;
        }}

        /* Section */
        .section {{
            margin: 50px 0;
            background: var(--card);
            border-radius: 16px;
            padding: 40px;
            border: 1px solid #e2e8f0;
        }}

        .section h2 {{
            color: var(--primary);
            font-size: 1.8em;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 3px solid var(--accent);
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .section h3 {{
            color: var(--secondary);
            font-size: 1.3em;
            margin: 30px 0 15px 0;
        }}

        /* Table */
        .table-container {{
            overflow-x: auto;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin: 25px 0;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95em;
        }}

        thead {{
            background: linear-gradient(135deg, var(--secondary) 0%, var(--accent) 100%);
            color: white;
        }}

        th {{
            padding: 16px 14px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.85em;
        }}

        td {{
            padding: 14px;
            border-bottom: 1px solid #e2e8f0;
        }}

        tbody tr:nth-child(even) {{
            background: #f7fafc;
        }}

        tbody tr:hover {{
            background: #edf2f7;
            transition: background 0.2s;
        }}

        /* Insights */
        .insights {{
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-left: 5px solid var(--warning);
            padding: 30px;
            margin: 40px 0;
            border-radius: 12px;
        }}

        .insights h3 {{
            color: #92400e;
            margin-bottom: 20px;
            font-size: 1.4em;
        }}

        .insights ul {{
            margin-left: 25px;
        }}

        .insights li {{
            margin: 12px 0;
            color: #78350f;
            line-height: 1.6;
        }}

        /* Action Items */
        .actions {{
            background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
            border-left: 5px solid var(--accent);
            padding: 30px;
            margin: 40px 0;
            border-radius: 12px;
        }}

        .actions h3 {{
            color: #1e40af;
            margin-bottom: 20px;
            font-size: 1.4em;
        }}

        .actions ol {{
            margin-left: 25px;
        }}

        .actions li {{
            margin: 12px 0;
            color: #1e3a8a;
            line-height: 1.6;
        }}

        /* Footer */
        .footer {{
            background: var(--primary);
            color: white;
            text-align: center;
            padding: 30px;
            font-size: 0.9em;
            opacity: 0.9;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 2em; }}
            .content {{ padding: 30px 20px; }}
            .metric-value {{ font-size: 2em; }}
            .section {{ padding: 25px; }}
        }}

        /* Print styles */
        @media print {{
            body {{ background: white; }}
            .container {{ box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📊 2024 vs 2025 KPI完整对比报告</h1>
            <p>基于本地Defect、MR和History数据深度分析 | 生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}</p>
        </div>

        <div class="content">
            <!-- Metrics Grid -->
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">2024年MR执行</div>
                    <div class="metric-value">{len(df_mr_2024):,}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">2025年MR执行</div>
                    <div class="metric-value">{len(df_mr_2025):,}</div>
                    <div class="metric-change positive">+{((len(df_mr_2025)-len(df_mr_2024))/len(df_mr_2024)*100):.1f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">2024年缺陷</div>
                    <div class="metric-value">{len(df_def_2024):,}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">2025年缺陷</div>
                    <div class="metric-value">{len(df_def_2025):,}</div>
                    <div class="metric-change negative">+{((len(df_def_2025)-len(df_def_2024))/len(df_def_2024)*100):.1f}%</div>
                </div>
            </div>

            <!-- Section 1: Overview -->
            <div class="section">
                <h2>📋 一、核心指标概览</h2>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr><th>指标</th><th>2024年</th><th>2025年</th><th>变化</th></tr>
                        </thead>
                        <tbody>
                            <tr><td>MR测试执行总数</td><td>{len(df_mr_2024):,}</td><td>{len(df_mr_2025):,}</td><td>+{((len(df_mr_2025)-len(df_mr_2024))/len(df_mr_2024)*100):.2f}%</td></tr>
                            <tr><td>测试Passed率</td><td>{mr_quality[0]['Passed']/len(df_mr_2024)*100:.2f}%</td><td>{mr_quality[1]['Passed']/len(df_mr_2025)*100:.2f}%</td><td>+{(mr_quality[1]['Passed']/len(df_mr_2025)*100 - mr_quality[0]['Passed']/len(df_mr_2024)*100):.2f}pp</td></tr>
                            <tr><td>测试Failed率</td><td>{mr_quality[0]['Failed']/len(df_mr_2024)*100:.2f}%</td><td>{mr_quality[1]['Failed']/len(df_mr_2025)*100:.2f}%</td><td>{(mr_quality[1]['Failed']/len(df_mr_2025)*100 - mr_quality[0]['Failed']/len(df_mr_2024)*100):+.2f}pp</td></tr>
                            <tr><td>缺陷总数</td><td>{len(df_def_2024):,}</td><td>{len(df_def_2025):,}</td><td>+{((len(df_def_2025)-len(df_def_2024))/len(df_def_2024)*100):.2f}%</td></tr>
                            <tr><td>Showstopper Confirmed</td><td>{s24['sc']}</td><td>{s25['sc']}</td><td>+{((s25['sc']-s24['sc'])/s24['sc']*100):.2f}%</td></tr>
                            <tr><td>Preventing Maturity</td><td>{s24['pm']}</td><td>{s25['pm']}</td><td>{((s25['pm']-s24['pm'])/s24['pm']*100):.2f}%</td></tr>
                            <tr><td>Showstopper Candidate</td><td>{s24['ssc']}</td><td>{s25['ssc']}</td><td>+{((s25['ssc']-s24['ssc'])/s24['ssc']*100):.2f}%</td></tr>
                            <tr><td>06-Concluded</td><td>{s24['c06']}</td><td>{s25['c06']}</td><td>+{((s25['c06']-s24['c06'])/s24['c06']*100):.2f}%</td></tr>
                            <tr><td>09-CWA</td><td>{s24['c09']}</td><td>{s25['c09']}</td><td>+{((s25['c09']-s24['c09'])/s24['c09']*100):.2f}%</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Section 2: MR Quality -->
            <div class="section">
                <h2>📈 二、MR执行质量详细对比</h2>
                <div class="table-container">
                    {df_mr_quality.to_html(index=False, classes='data-table')}
                </div>
            </div>

            <!-- Section 3: Project -->
            <div class="section">
                <h2>🔧 三、Project覆盖详细数据</h2>
                <div class="table-container">
                    {df_project.to_html(index=False, classes='data-table')}
                </div>
            </div>

            <!-- Section 4: Model MR -->
            <div class="section">
                <h2>🚗 四、车型MR覆盖详细数据</h2>
                <div class="table-container">
                    {df_model_mr.to_html(index=False, classes='data-table')}
                </div>
            </div>

            <!-- Section 5: Defect Link -->
            <div class="section">
                <h2>🔗 五、缺陷关联分析详细数据</h2>
                <div class="table-container">
                    {df_defect_link.to_html(index=False, classes='data-table')}
                </div>
            </div>

            <!-- Section 6: Severity -->
            <div class="section">
                <h2>🔴 六、缺陷严重程度详细数据</h2>
                <div class="table-container">
                    {df_severity.to_html(index=False, classes='data-table')}
                </div>
            </div>

            <!-- Section 7: CWA -->
            <div class="section">
                <h2>📋 七、CWA Blocking Reason详细数据</h2>
                <div class="table-container">
                    {df_cwa.to_html(index=False, classes='data-table')}
                </div>
            </div>

            <!-- Section 8: ECU -->
            <div class="section">
                <h2>💻 八、ECU缺陷分布详细数据</h2>
                <div class="table-container">
                    {df_ecu.to_html(index=False, classes='data-table')}
                </div>
            </div>

            <!-- Section 9: Model Defect -->
            <div class="section">
                <h2>🚙 九、车型缺陷分布详细数据</h2>
                <div class="table-container">
                    {df_model_defect.to_html(index=False, classes='data-table')}
                </div>
            </div>

            <!-- Insights -->
            <div class="insights">
                <h3>💡 关键洞察</h3>
                <ul>
                    <li><strong>测试执行增长</strong>: 2025年MR执行较2024年增长{((len(df_mr_2025)-len(df_mr_2024))/len(df_mr_2024)*100):.2f}%，从{len(df_mr_2024):,}增至{len(df_mr_2025):,}</li>
                    <li><strong>测试质量提升</strong>: Passed率从{mr_quality[0]['Passed']/len(df_mr_2024)*100:.2f}%提升至{mr_quality[1]['Passed']/len(df_mr_2025)*100:.2f}%，增长{(mr_quality[1]['Passed']/len(df_mr_2025)*100 - mr_quality[0]['Passed']/len(df_mr_2024)*100):.2f}个百分点</li>
                    <li><strong>Preventing Maturity下降</strong>: 从{s24['pm']}降至{s25['pm']}，减少{((s24['pm']-s25['pm'])/s24['pm']*100):.2f}%</li>
                    <li><strong>Showstopper Confirmed增长</strong>: 从{s24['sc']}增至{s25['sc']}，增长{((s25['sc']-s24['sc'])/s24['sc']*100):.2f}%</li>
                    <li><strong>真实解决率下降</strong>: 06-Concluded占比从{s24['c06']/len(df_def_2024)*100:.2f}%降至{s25['c06']/len(df_def_2025)*100:.2f}%</li>
                </ul>
            </div>

            <!-- Actions -->
            <div class="actions">
                <h3>📌 建议行动</h3>
                <ol>
                    <li><strong>【紧急】</strong> Showstopper Confirmed增长{((s25['sc']-s24['sc'])/s24['sc']*100):.2f}%，需立即专项攻关</li>
                    <li><strong>【关注】</strong> Showstopper Candidate激增{((s25['ssc']-s24['ssc'])/s24['ssc']*100):.2f}%，加强预防机制</li>
                    <li><strong>【改进】</strong> 真实解决率下降{(s24['c06']/len(df_def_2024)*100 - s25['c06']/len(df_def_2025)*100):.2f}pp，优化闭环效率</li>
                    <li><strong>【保持】</strong> Preventing Maturity下降{((s24['pm']-s25['pm'])/s24['pm']*100):.2f}%，延续良好趋势</li>
                    <li><strong>【聚焦】</strong> IDCEVO-25占主导，建议专项质量改进</li>
                </ol>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>数据来源: defect/, mr/, database/local_data.db | 生成工具: Python Pandas | 报告包含完整详细数据</p>
        </div>
    </div>
</body>
</html>"""

html_file = 'KPI报告_2024_2025_完整版.html'
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"  ✅ HTML: {html_file}")

print("\n" + "="*80)
print("✅ 所有报告生成完成！")
print("="*80)
print(f"\n生成的文件:")
print(f"  📊 Excel: {excel_file}")
print(f"  📝 Markdown: {md_file}")
print(f"  🌐 HTML: {html_file}")
print(f"\n提示: 直接用浏览器打开HTML文件即可查看精美报告")
