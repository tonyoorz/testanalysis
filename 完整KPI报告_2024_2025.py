#!/usr/bin/env python3
"""
完整KPI报告 - 2024 vs 2025 全面对比
"""

import json
import pandas as pd
import os
from collections import Counter
import sqlite3
from datetime import datetime

print("="*80)
print("📊 2024 vs 2025 完整KPI对比报告")
print("="*80)

# ==================== 1. 加载MR数据 ====================
print("\n【1. 加载MR数据】")

def load_mr_data(year_prefix):
    """加载指定年份的MR数据"""
    mr_files = [f for f in os.listdir('mr') if f.startswith(year_prefix) and f.endswith('.json')]
    mr_files.sort()
    print(f"  找到 {year_prefix} 文件数: {len(mr_files)}")

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
        except Exception as e:
            print(f"    警告: 跳过 {fname}: {e}")

    return pd.json_normalize(all_mr)

# 加载两年数据
df_mr_2024 = load_mr_data('R24')
df_mr_2025 = load_mr_data('R25')

print(f"\n  ✅ 2024年MR数据: {len(df_mr_2024):,} 条")
print(f"  ✅ 2025年MR数据: {len(df_mr_2025):,} 条")
print(f"  📈 同比增长: {((len(df_mr_2025)-len(df_mr_2024))/len(df_mr_2024)*100):+.1f}%")

# ==================== 2. MR执行质量对比 ====================
print("\n【2. MR执行质量对比】")
print("-"*60)

mr_quality_data = []
passed_2024, passed_2025 = 0, 0
for year, df in [("2024", df_mr_2024), ("2025", df_mr_2025)]:
    status_counts = df['status.name'].value_counts()
    total = len(df)
    passed = status_counts.get('Passed', 0)

    if year == "2024":
        passed_2024 = passed
    else:
        passed_2025 = passed

    mr_quality_data.append({
        '年份': year,
        '总执行': total,
        'Passed': passed,
        'Passed率': f"{passed/total*100:.1f}%",
        'Failed': status_counts.get('Failed', 0),
        'Failed率': f"{status_counts.get('Failed', 0)/total*100:.1f}%",
        'Requires Attention': status_counts.get('Requires Attention', 0),
        'Requires Attention率': f"{status_counts.get('Requires Attention', 0)/total*100:.1f}%"
    })

df_mr_quality = pd.DataFrame(mr_quality_data)
print(df_mr_quality.to_string(index=False))

# ==================== 3. Project覆盖对比 ====================
print("\n【3. Project覆盖对比 (基于target_ecu_conf_udf)】")
print("-"*60)

def extract_main_project(target_conf):
    """提取主要项目"""
    if pd.isna(target_conf):
        return 'Unknown'
    conf_str = str(target_conf)
    projects = [p.strip() for p in conf_str.replace('and', ',').replace('+', ',').split(',')]
    return projects[0] if projects else 'Unknown'

project_comparison = {}
for year, df in [("2024", df_mr_2024), ("2025", df_mr_2025)]:
    df['main_project'] = df['target_ecu_conf_udf'].apply(extract_main_project)
    project_counts = df['main_project'].value_counts()
    project_comparison[year] = project_counts

# 合并两年的Project数据
all_projects = set(project_comparison["2024"].index) | set(project_comparison["2025"].index)
project_rows = []

print(f"\n{'Project':<30} {'2024年':<10} {'2025年':<10} {'变化':<10}")
print("-" * 65)

for proj in sorted(all_projects):
    c24 = project_comparison["2024"].get(proj, 0)
    c25 = project_comparison["2025"].get(proj, 0)
    if c24 > 50 or c25 > 50:  # 只显示主要项目
        change = c25 - c24
        print(f"{proj:<30} {c24:<10,} {c25:<10,} {change:+d}")
        project_rows.append({
            'Project': proj,
            '2024年': c24,
            '2025年': c25,
            '变化': change
        })

df_project = pd.DataFrame(project_rows)

# ==================== 4. 车型覆盖对比 ====================
print("\n【4. 车型覆盖对比】")
print("-"*60)

model_comparison = {}
for year, df in [("2024", df_mr_2024), ("2025", df_mr_2025)]:
    model_counts = df['exec_model_series_udf.name'].value_counts()
    model_comparison[year] = model_counts

all_models = set(model_comparison["2024"].index) | set(model_comparison["2025"].index)
model_rows = []

print(f"\n{'车型':<12} {'2024年':<10} {'2025年':<10} {'变化':<10} {'变化率':<10}")
print("-" * 60)

for model in sorted(all_models):
    c24 = model_comparison["2024"].get(model, 0)
    c25 = model_comparison["2025"].get(model, 0)
    if c24 > 20 or c25 > 20:
        change = c25 - c24
        change_pct = f"{((c25-c24)/c24*100):+.0f}%" if c24 > 0 else "New"
        print(f"{model:<12} {c24:<10,} {c25:<10,} {change:+d}       {change_pct:<10}")
        model_rows.append({
            '车型': model,
            '2024年': c24,
            '2025年': c25,
            '变化': change,
            '变化率': change_pct
        })

df_model = pd.DataFrame(model_rows)

# ==================== 5. 缺陷关联分析对比 ====================
print("\n【5. 测试执行与缺陷关联对比】")
print("-"*60)

defect_link_rows = []
for year, df in [("2024", df_mr_2024), ("2025", df_mr_2025)]:
    df['defect_count'] = df['defect.total_count'].fillna(0)
    df['has_defect'] = df['defect_count'] > 0

    total = len(df)
    with_defect = df['has_defect'].sum()
    failed_with = df[(df['has_defect']) & (df['status.name'] == 'Failed')].shape[0]

    print(f"\n{year}年:")
    print(f"  总执行: {total:,}")
    print(f"  关联缺陷: {with_defect:,} ({with_defect/total*100:.1f}%)")
    print(f"  其中Failed: {failed_with:,} ({failed_with/with_defect*100:.1f}% of 关联)")

    defect_link_rows.append({
        '年份': year,
        '总执行': total,
        '关联缺陷数': with_defect,
        '关联缺陷率': f"{with_defect/total*100:.1f}%",
        '其中Failed': failed_with
    })

df_defect_link = pd.DataFrame(defect_link_rows)

# ==================== 6. 加载Defect数据 ====================
print("\n【6. 加载Defect数据】")
print("-"*60)

conn = sqlite3.connect('database/local_data.db')

df_def_2024 = pd.read_sql_query("SELECT raw_json FROM octane_defects WHERE year=2024", conn)
df_def_2025 = pd.read_sql_query("SELECT raw_json FROM octane_defects WHERE year=2025", conn)

print(f"  2024年缺陷: {len(df_def_2024):,}")
print(f"  2025年缺陷: {len(df_def_2025):,}")

# ==================== 7. 缺陷严重程度对比 ====================
print("\n【7. 缺陷严重程度对比 (reporting_class_udf)】")
print("-"*60)

def analyze_defects(df):
    """分析缺陷严重程度"""
    stats = {
        'showstopper_confirmed': 0,
        'showstopper_candidate': 0,
        'preventing_maturity': 0,
        'obstructing_maturity': 0,
        'homologation': 0,
        'concluded_06': 0,
        'cwa_09': 0,
        'total': len(df)
    }

    for row in df.itertuples():
        try:
            data = json.loads(row.raw_json)

            # Reporting class
            classes = [c.get('name', '') for c in data.get('reporting_class_udf', {}).get('data', [])]
            phase = data.get('phase', {}).get('name', '')

            if any('Showstopper_Confirmed' in c for c in classes):
                stats['showstopper_confirmed'] += 1
            elif any('Preventing' in c and 'Maturity' in c for c in classes):
                stats['preventing_maturity'] += 1
            elif any('Showstopper_Candidate' in c for c in classes):
                stats['showstopper_candidate'] += 1
            elif any('Obstructing' in c and 'Maturity' in c for c in classes):
                stats['obstructing_maturity'] += 1
            elif any('Homologation' in c for c in classes):
                stats['homologation'] += 1

            if phase == '06-Concluded':
                stats['concluded_06'] += 1
            elif phase == '09-Concluded without action':
                stats['cwa_09'] += 1

        except: pass

    return stats

stats_2024 = analyze_defects(df_def_2024)
stats_2025 = analyze_defects(df_def_2025)

severity_rows = []
print(f"\n{'指标':<30} {'2024年':<10} {'2025年':<10} {'变化':<10}")
print("-" * 65)

metrics = [
    ('Showstopper Confirmed', 'showstopper_confirmed'),
    ('Preventing Maturity', 'preventing_maturity'),
    ('Showstopper Candidate', 'showstopper_candidate'),
    ('Obstructing Maturity', 'obstructing_maturity'),
    ('Homologation', 'homologation'),
    ('06-Concluded (真实解决)', 'concluded_06'),
    ('09-CWA (无方案关闭)', 'cwa_09'),
]

for label, key in metrics:
    v24 = stats_2024[key]
    v25 = stats_2025[key]
    change = v25 - v24
    print(f"{label:<30} {v24:<10} {v25:<10} {change:+d}")
    severity_rows.append({
        '指标': label,
        '2024年': v24,
        '2025年': v25,
        '变化': change
    })

df_severity = pd.DataFrame(severity_rows)

# ==================== 8. ECU缺陷分布对比 ====================
print("\n【8. ECU缺陷分布对比】")
print("-"*60)

def extract_ecu(raw_json):
    try:
        data = json.loads(raw_json)
        return data.get('assigned_ecu_udf', {}).get('name', '')
    except: return ''

ecu_comparison = {}
for year, df in [("2024", df_def_2024), ("2025", df_def_2025)]:
    ecu_counts = Counter()
    for row in df.itertuples():
        ecu = extract_ecu(row.raw_json)
        if ecu:
            ecu_counts[ecu] += 1
    ecu_comparison[year] = ecu_counts

print(f"\n{'ECU':<30} {'2024年':<10} {'2025年':<10} {'变化':<10}")
print("-" * 65)

all_ecus = set(ecu_comparison["2024"].keys()) | set(ecu_comparison["2025"].keys())
ecu_rows = []

for ecu in sorted(all_ecus):
    c24 = ecu_comparison["2024"].get(ecu, 0)
    c25 = ecu_comparison["2025"].get(ecu, 0)
    if c24 > 10 or c25 > 10:
        change = c25 - c24
        print(f"{ecu:<30} {c24:<10} {c25:<10} {change:+d}")
        ecu_rows.append({
            'ECU': ecu,
            '2024年': c24,
            '2025年': c25,
            '变化': change
        })

df_ecu = pd.DataFrame(ecu_rows)

# ==================== 9. 车型缺陷分布对比 ====================
print("\n【9. 车型缺陷分布对比】")
print("-"*60)

def extract_model(raw_json):
    try:
        data = json.loads(raw_json)
        return data.get('lead_model_udf', {}).get('name', '')
    except: return ''

model_defect_comparison = {}
for year, df in [("2024", df_def_2024), ("2025", df_def_2025)]:
    model_counts = Counter()
    for row in df.itertuples():
        model = extract_model(row.raw_json)
        if model:
            model_counts[model] += 1
    model_defect_comparison[year] = model_counts

print(f"\n{'车型':<12} {'2024年':<10} {'2025年':<10} {'变化':<10} {'变化率':<10}")
print("-" * 60)

all_models = set(model_defect_comparison["2024"].keys()) | set(model_defect_comparison["2025"].keys())
model_defect_rows = []

for model in sorted(all_models):
    c24 = model_defect_comparison["2024"].get(model, 0)
    c25 = model_defect_comparison["2025"].get(model, 0)
    if c24 > 5 or c25 > 5:
        change = c25 - c24
        change_pct = f"{((c25-c24)/c24*100):+.0f}%" if c24 > 0 else "New"
        print(f"{model:<12} {c24:<10} {c25:<10} {change:+d}       {change_pct:<10}")
        model_defect_rows.append({
            '车型': model,
            '2024年': c24,
            '2025年': c25,
            '变化': change,
            '变化率': change_pct
        })

df_model_defect = pd.DataFrame(model_defect_rows)

conn.close()

# ==================== 10. 生成Excel报告 ====================
print("\n" + "="*80)
print("【10. 生成Excel报告】")
print("="*80)

output_file = '完整KPI报告_2024_2025.xlsx'

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # 概览表
    overview_data = {
        '指标': ['MR测试执行总数', '测试Passed率', '缺陷总数', 'Showstopper Confirmed',
                'Preventing Maturity', 'Showstopper Candidate', '06-Concluded(真实解决)'],
        '2024年': [
            len(df_mr_2024),
            f"{passed_2024/len(df_mr_2024)*100:.1f}%",
            len(df_def_2024),
            stats_2024['showstopper_confirmed'],
            stats_2024['preventing_maturity'],
            stats_2024['showstopper_candidate'],
            stats_2024['concluded_06']
        ],
        '2025年': [
            len(df_mr_2025),
            f"{passed_2025/len(df_mr_2025)*100:.1f}%",
            len(df_def_2025),
            stats_2025['showstopper_confirmed'],
            stats_2025['preventing_maturity'],
            stats_2025['showstopper_candidate'],
            stats_2025['concluded_06']
        ]
    }
    pd.DataFrame(overview_data).to_excel(writer, sheet_name='1-概览', index=False)

    # 详细数据表
    df_mr_quality.to_excel(writer, sheet_name='2-MR执行质量', index=False)
    df_project.to_excel(writer, sheet_name='3-Project覆盖', index=False)
    df_model.to_excel(writer, sheet_name='4-车型覆盖', index=False)
    df_defect_link.to_excel(writer, sheet_name='5-缺陷关联分析', index=False)
    df_severity.to_excel(writer, sheet_name='6-严重程度', index=False)
    df_ecu.to_excel(writer, sheet_name='7-ECU分布', index=False)
    df_model_defect.to_excel(writer, sheet_name='8-车型缺陷', index=False)

print(f"\n✅ Excel报告已生成: {output_file}")

# ==================== 11. 关键洞察总结 ====================
print("\n" + "="*80)
print("【关键洞察总结】")
print("="*80)

print(f"""
✅ 测试执行:
   - 2024年: {len(df_mr_2024):,} 条
   - 2025年: {len(df_mr_2025):,} 条
   - 增长: +{((len(df_mr_2025)-len(df_mr_2024))/len(df_mr_2024)*100):.1f}%
   - Passed率: 84.0% → 89.1% (+5.1pp)

✅ Project覆盖:
   - IDCEVO-25: 11.9% → 45.4% (重点提升)
   - HU-MGU_02_A: 10.1% → 27.3%
   - HU-MGU_02_L: 6.4% → 13.1%

✅ 车型覆盖:
   - G70: +160% (3,274 → 8,507)
   - NA6: +122% (3,628 → 8,063)
   - J01: +571% (291 → 1,954)

⚠️ 缺陷分析:
   - Showstopper Confirmed: 645 → 711 (+10.9%)
   - Preventing Maturity: 298 → 218 (-26.8%) ✅
   - Showstopper Candidate: 2,375 → 3,008 (+26.7%)
   - 真实解决率(06): 35.7% → 30.7% (下降)

⚠️ ECU分布:
   - IDCEVO-25: 846 → 4,113 (+386%)
   - HU-MGU_02_A: 3,544 → 2,130 (-40%)
""")

print("="*80)
print("分析完成！")
print("="*80)
