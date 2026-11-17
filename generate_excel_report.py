#!/usr/bin/env python3
"""生成2024 vs 2025 KPI Excel报告"""

import json
import pandas as pd
import os
from collections import Counter
import sqlite3
from datetime import datetime

print("="*80)
print("📊 生成2024 vs 2025 KPI Excel报告")
print("="*80)

# 加载MR数据
def load_mr_data(year_prefix):
    mr_files = [f for f in os.listdir('mr') if f.startswith(year_prefix) and f.endswith('.json')]
    all_mr = []
    for fname in mr_files:
        try:
            with open(f'mr/{fname}') as f:
                data = json.load(f)
            if isinstance(data, list):
                for mr in data:
                    mr['source_file'] = fname
                    mr['year'] = year_prefix
                all_mr.extend(data)
        except: pass
    return pd.json_normalize(all_mr)

print("\n1. 加载MR数据...")
df_mr_2024 = load_mr_data('R24')
df_mr_2025 = load_mr_data('R25')
print(f"  2024年MR: {len(df_mr_2024):,} 条")
print(f"  2025年MR: {len(df_mr_2025):,} 条")

# MR执行质量
print("\n2. 分析MR执行质量...")
mr_summary = []
for year, df in [("2024", df_mr_2024), ("2025", df_mr_2025)]:
    if len(df) == 0: continue
    status_counts = df['status.name'].value_counts()
    total = len(df)
    mr_summary.append({
        '年份': year, '总执行': total,
        'Passed': status_counts.get('Passed', 0),
        'Passed率': f"{status_counts.get('Passed', 0)/total*100:.1f}%",
        'Failed': status_counts.get('Failed', 0),
        'Failed率': f"{status_counts.get('Failed', 0)/total*100:.1f}%",
        'Requires Attention': status_counts.get('Requires Attention', 0),
        'Requires Attention率': f"{status_counts.get('Requires Attention', 0)/total*100:.1f}%"
    })
df_mr_summary = pd.DataFrame(mr_summary)

# Project分析
def extract_main_project(target_conf):
    if pd.isna(target_conf): return 'Unknown'
    projects = [p.strip() for p in str(target_conf).replace('and', ',').replace('+', ',').split(',')]
    return projects[0] if projects else 'Unknown'

print("\n3. 分析Project覆盖...")
project_summary = []
for year, df in [("2024", df_mr_2024), ("2025", df_mr_2025)]:
    if len(df) == 0: continue
    df['main_project'] = df['target_ecu_conf_udf'].apply(extract_main_project)
    for proj, count in df['main_project'].value_counts().head(15).items():
        project_summary.append({'年份': year, 'Project': proj, '执行次数': count, '占比': f"{count/len(df)*100:.1f}%"})
df_project = pd.DataFrame(project_summary)

# 车型覆盖
print("\n4. 分析车型覆盖...")
model_comp = []
models_2024 = df_mr_2024['exec_model_series_udf.name'].value_counts() if len(df_mr_2024)>0 else pd.Series()
models_2025 = df_mr_2025['exec_model_series_udf.name'].value_counts() if len(df_mr_2025)>0 else pd.Series()
for model in sorted(set(models_2024.index) | set(models_2025.index)):
    c24, c25 = models_2024.get(model, 0), models_2025.get(model, 0)
    if c24>10 or c25>10:
        model_comp.append({'车型': model, '2024年': c24, '2025年': c25, '变化': c25-c24})
df_model = pd.DataFrame(model_comp)

# 缺陷关联分析
print("\n5. 分析缺陷关联...")
defect_link = []
for year, df in [("2024", df_mr_2024), ("2025", df_mr_2025)]:
    if len(df) == 0: continue
    df['defect_count'] = df['defect.total_count'].fillna(0)
    df['has_defect'] = df['defect_count'] > 0
    total_with = df['has_defect'].sum()
    failed_with = df[(df['has_defect']) & (df['status.name'] == 'Failed')].shape[0]
    defect_link.append({
        '年份': year, '总执行': len(df), '关联缺陷数': total_with,
        '关联缺陷率': f"{total_with/len(df)*100:.1f}%", '其中Failed': failed_with
    })
df_defect_link = pd.DataFrame(defect_link)

# Defect数据
print("\n6. 加载Defect数据...")
conn = sqlite3.connect('database/local_data.db')
df_def_2024 = pd.read_sql_query("SELECT raw_json FROM octane_defects WHERE year=2024", conn)
df_def_2025 = pd.read_sql_query("SELECT raw_json FROM octane_defects WHERE year=2025", conn)
print(f"  2024年缺陷: {len(df_def_2024):,}")
print(f"  2025年缺陷: {len(df_def_2025):,}")

# 严重程度
print("\n7. 分析严重程度...")
severity_data = []
cwa_data = []

for year, df in [("2024", df_def_2024), ("2025", df_def_2025)]:
    sc, pm, ssc, obs, homo, c06, c09 = 0, 0, 0, 0, 0, 0, 0
    cwa_reasons = Counter()

    for row in df.itertuples():
        try:
            data = json.loads(row.raw_json)
            classes = [c.get('name','') for c in data.get('reporting_class_udf',{}).get('data',[])]
            phase = data.get('phase',{}).get('name','')
            br = data.get('blocking_reason_udf',{}).get('name','') if isinstance(data.get('blocking_reason_udf'), dict) else ''

            if any('Showstopper_Confirmed' in c for c in classes): sc += 1
            elif any('Preventing' in c and 'Maturity' in c for c in classes): pm += 1
            elif any('Showstopper_Candidate' in c for c in classes): ssc += 1
            elif any('Obstructing' in c and 'Maturity' in c for c in classes): obs += 1
            elif any('Homologation' in c for c in classes): homo += 1

            if phase == '06-Concluded': c06 += 1
            if phase == '09-Concluded without action':
                c09 += 1
                cwa_reasons[br or 'Unknown/Empty'] += 1
        except: pass

    severity_data.append({
        '年份': year, '缺陷总数': len(df),
        'Showstopper Confirmed': sc,
        'Preventing Maturity': pm,
        'Showstopper Candidate': ssc,
        'Obstructing Maturity': obs,
        'Homologation': homo,
        '06-Concluded': c06,
        '09-CWA': c09
    })

    for reason, count in cwa_reasons.most_common(10):
        cwa_data.append({'年份': year, 'Blocking Reason': reason, '数量': count, '占CWA比': f"{count/c09*100:.1f}%"})

df_severity = pd.DataFrame(severity_data)
df_cwa = pd.DataFrame(cwa_data)

# ECU缺陷分布
print("\n8. 分析ECU分布...")
ecu_data = []
for year, df in [("2024", df_def_2024), ("2025", df_def_2025)]:
    ecu_counts = Counter()
    for row in df.itertuples():
        try:
            data = json.loads(row.raw_json)
            ecu = data.get('assigned_ecu_udf',{}).get('name','')
            if ecu: ecu_counts[ecu] += 1
        except: pass
    for ecu, count in ecu_counts.most_common(15):
        ecu_data.append({'年份': year, 'ECU': ecu, '缺陷数': count})
df_ecu = pd.DataFrame(ecu_data)

# 车型缺陷分布
print("\n9. 分析车型缺陷...")
model_defect_data = []
for year, df in [("2024", df_def_2024), ("2025", df_def_2025)]:
    model_counts = Counter()
    for row in df.itertuples():
        try:
            data = json.loads(row.raw_json)
            model = data.get('lead_model_udf',{}).get('name','')
            if model: model_counts[model] += 1
        except: pass
    for model, count in model_counts.items():
        if count > 5:
            model_defect_data.append({'年份': year, '车型': model, '缺陷数': count})
df_model_defect = pd.DataFrame(model_defect_data)

conn.close()

# 生成Excel
print("\n10. 生成Excel报告...")
output_file = 'kpi_report_2024_2025.xlsx'

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # Sheet 1: 概览
    overview = pd.DataFrame({
        '指标': ['MR测试执行总数', '测试通过率', '缺陷总数', 'Showstopper Confirmed', 'Preventing Maturity', '06-Concluded(真实解决)'],
        '2024年': [
            len(df_mr_2024),
            f"{df_mr_summary[df_mr_summary['年份']=='2024']['Passed率'].values[0] if len(df_mr_summary)>0 else 'N/A'}",
            len(df_def_2024),
            df_severity[df_severity['年份']=='2024']['Showstopper Confirmed'].values[0] if len(df_severity)>0 else 0,
            df_severity[df_severity['年份']=='2024']['Preventing Maturity'].values[0] if len(df_severity)>0 else 0,
            df_severity[df_severity['年份']=='2024']['06-Concluded'].values[0] if len(df_severity)>0 else 0
        ],
        '2025年': [
            len(df_mr_2025),
            f"{df_mr_summary[df_mr_summary['年份']=='2025']['Passed率'].values[0] if len(df_mr_summary)>0 else 'N/A'}",
            len(df_def_2025),
            df_severity[df_severity['年份']=='2025']['Showstopper Confirmed'].values[0] if len(df_severity)>0 else 0,
            df_severity[df_severity['年份']=='2025']['Preventing Maturity'].values[0] if len(df_severity)>0 else 0,
            df_severity[df_severity['年份']=='2025']['06-Concluded'].values[0] if len(df_severity)>0 else 0
        ]
    })
    overview.to_excel(writer, sheet_name='1-概览', index=False)

    df_mr_summary.to_excel(writer, sheet_name='2-MR执行质量', index=False)
    df_project.to_excel(writer, sheet_name='3-Project覆盖', index=False)
    df_model.to_excel(writer, sheet_name='4-车型覆盖对比', index=False)
    df_defect_link.to_excel(writer, sheet_name='5-缺陷关联分析', index=False)
    df_severity.to_excel(writer, sheet_name='6-缺陷严重程度', index=False)
    df_cwa.to_excel(writer, sheet_name='7-CWA分析', index=False)
    df_ecu.to_excel(writer, sheet_name='8-ECU缺陷分布', index=False)
    df_model_defect.to_excel(writer, sheet_name='9-车型缺陷分布', index=False)

print(f"\n✅ Excel报告已生成: {output_file}")
print("="*80)
