#!/usr/bin/env python3
"""
2024 vs 2025 综合KPI对比报告 - 完整版
包含7大类测试度量指标
"""

import json
import pandas as pd
import os
from collections import Counter, defaultdict
import sqlite3
from datetime import datetime, timedelta
import re
import numpy as np

print("="*80)
print("📊 2024 vs 2025 综合KPI对比报告 - 完整版")
print("="*80)

# ==================== 1. 加载数据 ====================
print("\n【1. 加载数据】")

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

def load_defect_data(year):
    """从数据库加载defect数据 - 返回原始字典列表保持嵌套结构"""
    conn = sqlite3.connect('database/local_data.db')
    df = pd.read_sql_query(f"SELECT raw_json FROM octane_defects WHERE year={year}", conn)
    conn.close()

    defects = []
    for row in df.itertuples():
        try:
            data = json.loads(row.raw_json)
            data['_year'] = year
            defects.append(data)
        except:
            pass
    # 返回原始字典列表而不是json_normalize，以保持嵌套结构
    return defects

def load_history_data(year):
    """加载history数据用于处理周期分析"""
    history_files = [f for f in os.listdir('history') if f.startswith(f'{year}_') and f.endswith('.json')]
    all_history = {}
    for fname in history_files[:500]:  # 限制数量避免内存问题
        try:
            with open(f'history/{fname}', 'r', encoding='utf-8') as f:
                data = json.load(f)
            ticket_id = fname.replace(f'{year}_', '').replace('.json', '')
            all_history[ticket_id] = data
        except:
            pass
    return all_history

# 加载所有数据
print("  加载MR数据...")
df_mr_2024 = load_mr_data('R24')
df_mr_2025 = load_mr_data('R25')

print("  加载Defect数据...")
df_def_2024_raw = load_defect_data(2024)
df_def_2025_raw = load_defect_data(2025)

print("  加载History数据...")
history_2024 = load_history_data(2024)
history_2025 = load_history_data(2025)

print(f"\n  ✅ 2024年: MR={len(df_mr_2024):,}, Defect={len(df_def_2024_raw):,}, History={len(history_2024)}")
print(f"  ✅ 2025年: MR={len(df_mr_2025):,}, Defect={len(df_def_2025_raw):,}, History={len(history_2025)}")

# ==================== 2. 项目提取逻辑 ====================
print("\n【2. 应用项目提取逻辑】")

def extract_project_from_row(row):
    """使用data_processor.py的逻辑提取项目"""
    target_ecu = str(row.get('target_ecu_conf_udf', '')) if pd.notna(row.get('target_ecu_conf_udf')) else ''
    name = str(row.get('name', '')) if pd.notna(row.get('name')) else ''

    project = ''
    if 'DTSV_CHINA-RSU' in name or 'RSU' in name:
        project = 'RSU'
    if project == '':
        if 'My BMW' in target_ecu:
            project = 'App'
        elif 'IDCEVO' in target_ecu:
            project = 'IDCevo'
        elif 'HU-MGU_02_L' in target_ecu:
            project = 'MGU'
        elif 'HU-MGU_02_A' in target_ecu:
            project = 'IDC'
    if project == '':
        if any(x in name for x in ['IOS', 'Android', 'HarmonyOS']):
            project = 'App'
        elif any(x in name for x in ['IDC23_MINI', 'IDC23_BMW', 'HU-MGU_02_A', 'IDC23']):
            project = 'IDC'
        elif 'IDCEVO' in name:
            project = 'IDCevo'
        elif any(x in name for x in ['MGU22', 'HU-MGU_02_L', 'HU-MGU_01']):
            project = 'MGU'
        elif 'MGU21' in name:
            project = 'MGU'
        elif 'MGU18' in name:
            project = 'MGU'
    if project.startswith('MGU'):
        project = 'MGU'
    return project if project else 'Unknown'

for df in [df_mr_2024, df_mr_2025]:
    if len(df) > 0:
        df['project'] = df.apply(extract_project_from_row, axis=1)

# ==================== 3. 计算7大类度量指标 ====================
print("\n【3. 计算7大类度量指标】")

metrics = {'2024': {}, '2025': {}}

# ------------------ 类别1: 基础MR执行质量 ------------------
print("  计算基础MR执行质量...")
for year, df in [("2024", df_mr_2024), ("2025", df_mr_2025)]:
    status_counts = df['status.name'].value_counts() if len(df) > 0 else pd.Series()
    total = len(df)
    passed = status_counts.get('Passed', 0)
    failed = status_counts.get('Failed', 0)

    df['defect_count'] = df['defect.total_count'].fillna(0)
    df['has_defect'] = df['defect_count'] > 0
    with_defect = df['has_defect'].sum() if len(df) > 0 else 0
    failed_with_defect = df[(df['has_defect']) & (df['status.name'] == 'Failed')].shape[0] if len(df) > 0 else 0

    metrics[year]['mr_total'] = total
    metrics[year]['mr_passed'] = passed
    metrics[year]['mr_passed_rate'] = passed/total*100 if total > 0 else 0
    metrics[year]['mr_failed'] = failed
    metrics[year]['mr_failed_rate'] = failed/total*100 if total > 0 else 0
    metrics[year]['mr_with_defect'] = with_defect
    metrics[year]['mr_defect_link_rate'] = with_defect/total*100 if total > 0 else 0
    metrics[year]['mr_failed_with_defect'] = failed_with_defect

# ------------------ 类别2: Project/车型分布 ------------------
print("  计算Project/车型分布...")
for year, df in [("2024", df_mr_2024), ("2025", df_mr_2025)]:
    metrics[year]['project_dist'] = df['project'].value_counts().to_dict() if len(df) > 0 else {}
    metrics[year]['model_dist'] = df['exec_model_series_udf.name'].value_counts().to_dict() if len(df) > 0 else {}

# ------------------ 类别3: 测试周趋势 ------------------
print("  计算测试周趋势...")
for year, df in [("2024", df_mr_2024), ("2025", df_mr_2025)]:
    if 'test_week' in df.columns and len(df) > 0:
        # 清洗test_week数据
        df['test_week_clean'] = df['test_week'].astype(str).str.extract(r'(\d{4})[-_]?W?(\d{2})').apply(lambda x: f"{x[0]}-W{x[1]}" if pd.notna(x[0]) and pd.notna(x[1]) else None, axis=1)
        week_stats = df.groupby('test_week_clean').agg({
            'name': 'count',
            'status.name': lambda x: (x == 'Passed').sum()
        }).rename(columns={'name': 'total', 'status.name': 'passed'})
        week_stats['pass_rate'] = week_stats['passed'] / week_stats['total'] * 100
        metrics[year]['week_trend'] = week_stats.to_dict()
        metrics[year]['weeks_count'] = len(week_stats)
    else:
        metrics[year]['week_trend'] = {}
        metrics[year]['weeks_count'] = 0

# ------------------ 类别4: 缺陷严重程度 ------------------
print("  计算缺陷严重程度...")
for year, defects_list in [("2024", df_def_2024_raw), ("2025", df_def_2025_raw)]:
    stats = {
        'total': len(defects_list),
        'showstopper_confirmed': 0,
        'showstopper_candidate': 0,
        'preventing_maturity': 0,
        'obstructing_maturity': 0,
        'homologation': 0,
        'concluded_06': 0,
        'cwa_09': 0,
        'cwa_reasons': Counter()
    }

    for data in defects_list:
        try:
            # 处理reporting_class_udf
            reporting_class = data.get('reporting_class_udf', {})
            classes = []
            if isinstance(reporting_class, dict):
                class_data = reporting_class.get('data', [])
                if isinstance(class_data, list):
                    classes = [c.get('name', '') for c in class_data if isinstance(c, dict)]

            # 处理phase
            phase_data = data.get('phase', {})
            phase = phase_data.get('name', '') if isinstance(phase_data, dict) else str(phase_data)

            # 处理blocking_reason
            blocking_data = data.get('blocking_reason_udf', {})
            blocking_reason = blocking_data.get('name', '') if isinstance(blocking_data, dict) else str(blocking_data)

            # 统计严重级别
            if classes:
                class_names = ' '.join(classes)
                # 检查Showstopper Confirmed (注意实际值使用下划线)
                if 'Showstopper_Confirmed' in class_names or 'Showstopper Confirmed' in class_names:
                    stats['showstopper_confirmed'] += 1
                # 检查Preventing Maturity
                elif 'Preventing' in class_names:
                    stats['preventing_maturity'] += 1
                # 检查Showstopper Candidate
                elif 'Showstopper_Candidate' in class_names or 'Showstopper Candidate' in class_names:
                    stats['showstopper_candidate'] += 1
                # 检查Obstructing Maturity
                elif 'Obstructing' in class_names:
                    stats['obstructing_maturity'] += 1
                # 检查Homologation
                elif 'Homologation' in class_names:
                    stats['homologation'] += 1

            # 统计phase
            if phase == '06-Concluded':
                stats['concluded_06'] += 1
            elif phase == '09-Concluded without action':
                stats['cwa_09'] += 1
                stats['cwa_reasons'][blocking_reason or 'Unknown'] += 1
        except Exception as e:
            pass

    metrics[year]['defect_stats'] = stats

# ------------------ 类别5: 缺陷发现能力 ------------------
print("  计算缺陷发现能力...")
for year in ['2024', '2025']:
    mr_total = metrics[year]['mr_total']
    defect_total = metrics[year]['defect_stats']['total']
    failed_total = metrics[year]['mr_failed']
    failed_with_defect = metrics[year]['mr_failed_with_defect']

    # 缺陷密度 = 每1000次测试的缺陷数
    metrics[year]['defect_density'] = (defect_total / mr_total * 1000) if mr_total > 0 else 0

    # 发现问题效率 = Failed执行中关联缺陷的比例
    metrics[year]['discovery_efficiency'] = (failed_with_defect / failed_total * 100) if failed_total > 0 else 0

    # 真实解决率 = 06-Concluded / 总缺陷
    metrics[year]['real_resolution_rate'] = (metrics[year]['defect_stats']['concluded_06'] / defect_total * 100) if defect_total > 0 else 0

# ------------------ 类别6: ECU和车型缺陷分布 ------------------
print("  计算ECU和车型缺陷分布...")
for year, defects_list in [("2024", df_def_2024_raw), ("2025", df_def_2025_raw)]:
    ecu_counts = Counter()
    model_counts = Counter()

    for data in defects_list:
        ecu_data = data.get('assigned_ecu_udf', {})
        ecu = ecu_data.get('name', '') if isinstance(ecu_data, dict) else ''
        model_data = data.get('lead_model_udf', {})
        model = model_data.get('name', '') if isinstance(model_data, dict) else ''
        if ecu:
            ecu_counts[ecu] += 1
        if model:
            model_counts[model] += 1

    metrics[year]['ecu_dist'] = dict(ecu_counts.most_common(20))
    metrics[year]['model_defect_dist'] = dict(model_counts.most_common(20))

# ------------------ 类别7: 处理周期分析 ------------------
print("  计算处理周期...")
def analyze_processing_cycles(defects_list, history_data):
    """分析缺陷处理周期"""
    cycle_times = []
    phase_durations = defaultdict(list)
    resolved_count = 0

    for data in defects_list:
        defect_id = str(data.get('id', ''))
        phase_data = data.get('phase', {})
        phase = phase_data.get('name', '') if isinstance(phase_data, dict) else ''

        if phase in ['06-Concluded', '09-Concluded without action']:
            resolved_count += 1
            # 尝试从history计算处理时间
            if defect_id in history_data:
                try:
                    history = history_data[defect_id]
                    if isinstance(history, list) and len(history) >= 2:
                        # 简单计算：第一条到最后一条的时间差
                        first_time = history[0].get('timestamp', '')
                        last_time = history[-1].get('timestamp', '')
                        if first_time and last_time:
                            try:
                                from datetime import datetime
                                start = datetime.fromisoformat(first_time.replace('Z', '+00:00'))
                                end = datetime.fromisoformat(last_time.replace('Z', '+00:00'))
                                days = (end - start).days
                                if 0 < days < 365:  # 过滤异常值
                                    cycle_times.append(days)
                            except:
                                pass
                except:
                    pass

    avg_cycle = sum(cycle_times) / len(cycle_times) if cycle_times else 0
    return {
        'avg_cycle_days': round(avg_cycle, 1),
        'resolved_count': resolved_count,
        'cycle_samples': len(cycle_times)
    }

metrics['2024']['processing'] = analyze_processing_cycles(df_def_2024_raw, history_2024)
metrics['2025']['processing'] = analyze_processing_cycles(df_def_2025_raw, history_2025)

# ------------------ 类别8: Inflow/Outflow分析 ------------------
print("  计算Inflow/Outflow...")
def analyze_inflow_outflow(defects_list):
    """分析每周的流入流出"""
    inflow_by_week = Counter()
    outflow_by_week = Counter()

    for data in defects_list:
        # 创建时间
        created = data.get('creation_time', '')
        if created:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(str(created).replace('Z', '+00:00'))
                week_key = f"{dt.year}-W{dt.isocalendar()[1]:02d}"
                inflow_by_week[week_key] += 1
            except:
                pass

        # 解决时间
        phase_data = data.get('phase', {})
        phase = phase_data.get('name', '') if isinstance(phase_data, dict) else ''
        if phase in ['06-Concluded', '09-Concluded without action']:
            # 使用last_modified作为近似解决时间
            modified = data.get('last_modified', '')
            if modified:
                try:
                    dt = datetime.fromisoformat(str(modified).replace('Z', '+00:00'))
                    week_key = f"{dt.year}-W{dt.isocalendar()[1]:02d}"
                    outflow_by_week[week_key] += 1
                except:
                    pass

    return {
        'inflow': dict(inflow_by_week),
        'outflow': dict(outflow_by_week),
        'total_inflow': sum(inflow_by_week.values()),
        'total_outflow': sum(outflow_by_week.values())
    }

metrics['2024']['flow'] = analyze_inflow_outflow(df_def_2024_raw)
metrics['2025']['flow'] = analyze_inflow_outflow(df_def_2025_raw)

# ------------------ 类别9: 团队效能 ------------------
print("  计算团队效能...")
def analyze_team_effectiveness(defects_list):
    """分析测试人员效能"""
    # 尝试不同的字段名
    tester_counts = Counter()

    for data in defects_list:
        tester = None
        for field in ['found_by', 'author_name', 'tester', 'detected_by']:
            val = data.get(field)
            if val:
                if isinstance(val, dict):
                    tester = val.get('name', '')
                else:
                    tester = str(val)
                break

        # 尝试从owner字段
        if not tester:
            owner = data.get('owner', {})
            if isinstance(owner, dict):
                tester = owner.get('name', '')

        if tester and tester != 'nan':
            tester_counts[tester] += 1

    if not tester_counts:
        return {'total_testers': 0, 'avg_per_tester': 0, 'top_tester': 'N/A', 'top_count': 0}

    return {
        'total_testers': len(tester_counts),
        'avg_per_tester': round(sum(tester_counts.values()) / len(tester_counts), 1),
        'top_tester': tester_counts.most_common(1)[0][0] if tester_counts else 'N/A',
        'top_count': tester_counts.most_common(1)[0][1] if tester_counts else 0,
        'tester_dist': dict(tester_counts.most_common(10))
    }

metrics['2024']['team'] = analyze_team_effectiveness(df_def_2024_raw)
metrics['2025']['team'] = analyze_team_effectiveness(df_def_2025_raw)

# ------------------ 类别10: Feature Region分析 ------------------
print("  计算Feature Region覆盖...")
china_specific_aidas = [
    'Use App Store China', 'Traffic Info ASIA', 'Use Third Party App Store',
    'Route planning and management 2.0', 'Provide NetEase Cloud Music',
    'Provide Festival Mode', 'Positioning ASIA', 'Navigation Destination Input ASIA',
    'POI Functions ASIA', 'Parking Finder China', 'Itinerary (Mobile App)',
    'Use Speech operation', 'Connected Music China', 'Voice Interface',
    'Display map ASIA', 'Festival Mode', 'QQ Music', 'Tencent MiniProgramPlatform',
    'Guiding', 'Guiding 2.0', 'Guiding ASIA', 'Map', 'Map and Navigation Data update ASIA',
    'Tencent MPP - MainMenu', 'Tencent WeChat', 'Video streaming China',
    'WeChat Messaging', 'WeChat VoiP Call', 'Ximalaya', 'Provide Navigation 2.0',
    'Digital Keyring', 'PaDi', 'Display weather', 'Intelligent Reminder',
    'Provide IPA interactive Elements China', 'provide HUAWEI HiCar',
    'Provide Karaoke Service', 'Provisioning International Speller',
    'Provide App Center China', 'Telephony via customer device',
    'Provide 3rd party gaming enablement', 'Provide Child Seat App',
    'Provide Launcher', 'BT Child Seat App connection', 'My Modes',
    'Use Co-Driver Entertainment', 'Use Rear Seat Entertainment', 'Component Test'
]

def analyze_feature_region(defects_list):
    """分析Feature Region分布"""
    china_count = 0
    global_count = 0

    for data in defects_list:
        top_aida = data.get('top_aida', '')
        if isinstance(top_aida, str):
            is_china = any(aida in top_aida for aida in china_specific_aidas)
            if is_china:
                china_count += 1
            else:
                global_count += 1

    total = china_count + global_count
    return {
        'china_specific': china_count,
        'global': global_count,
        'china_ratio': china_count/total*100 if total > 0 else 0
    }

metrics['2024']['feature_region'] = analyze_feature_region(df_def_2024_raw)
metrics['2025']['feature_region'] = analyze_feature_region(df_def_2025_raw)

print("\n  ✅ 所有指标计算完成")

# ==================== 4. 生成Excel报告 ====================
print("\n【4. 生成Excel报告】")

output_file = '综合KPI报告_2024_2025_完整版.xlsx'

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:

    # Sheet 1: 核心指标概览
    overview_data = {
        '指标类别': [
            '测试执行总数', '测试Passed率(%)', '测试Failed率(%)', '测试周数',
            '缺陷总数', 'Showstopper Confirmed', 'Preventing Maturity', 'Showstopper Candidate',
            '06-Concluded(真实解决)', '09-CWA(无方案关闭)', '真实解决率(%)',
            '缺陷密度(每1000测试)', '发现问题效率(%)', '平均处理周期(天)',
            'Feature Region-China Specific', 'Feature Region-Global'
        ],
        '2024年': [
            metrics['2024']['mr_total'],
            f"{metrics['2024']['mr_passed_rate']:.1f}%",
            f"{metrics['2024']['mr_failed_rate']:.1f}%",
            metrics['2024']['weeks_count'],
            metrics['2024']['defect_stats']['total'],
            metrics['2024']['defect_stats']['showstopper_confirmed'],
            metrics['2024']['defect_stats']['preventing_maturity'],
            metrics['2024']['defect_stats']['showstopper_candidate'],
            metrics['2024']['defect_stats']['concluded_06'],
            metrics['2024']['defect_stats']['cwa_09'],
            f"{metrics['2024']['real_resolution_rate']:.1f}%",
            f"{metrics['2024']['defect_density']:.1f}",
            f"{metrics['2024']['discovery_efficiency']:.1f}%",
            metrics['2024']['processing']['avg_cycle_days'],
            metrics['2024']['feature_region']['china_specific'],
            metrics['2024']['feature_region']['global']
        ],
        '2025年': [
            metrics['2025']['mr_total'],
            f"{metrics['2025']['mr_passed_rate']:.1f}%",
            f"{metrics['2025']['mr_failed_rate']:.1f}%",
            metrics['2025']['weeks_count'],
            metrics['2025']['defect_stats']['total'],
            metrics['2025']['defect_stats']['showstopper_confirmed'],
            metrics['2025']['defect_stats']['preventing_maturity'],
            metrics['2025']['defect_stats']['showstopper_candidate'],
            metrics['2025']['defect_stats']['concluded_06'],
            metrics['2025']['defect_stats']['cwa_09'],
            f"{metrics['2025']['real_resolution_rate']:.1f}%",
            f"{metrics['2025']['defect_density']:.1f}",
            f"{metrics['2025']['discovery_efficiency']:.1f}%",
            metrics['2025']['processing']['avg_cycle_days'],
            metrics['2025']['feature_region']['china_specific'],
            metrics['2025']['feature_region']['global']
        ]
    }
    pd.DataFrame(overview_data).to_excel(writer, sheet_name='1-核心指标概览', index=False)

    # Sheet 2: MR执行质量详情
    mr_quality_data = {
        '指标': ['总执行', 'Passed', 'Passed率', 'Failed', 'Failed率', 'Requires Attention',
                '关联缺陷数', '关联缺陷率', 'Failed且关联缺陷'],
        '2024年': [
            metrics['2024']['mr_total'],
            metrics['2024']['mr_passed'],
            f"{metrics['2024']['mr_passed_rate']:.1f}%",
            metrics['2024']['mr_failed'],
            f"{metrics['2024']['mr_failed_rate']:.1f}%",
            'N/A',
            metrics['2024']['mr_with_defect'],
            f"{metrics['2024']['mr_defect_link_rate']:.1f}%",
            metrics['2024']['mr_failed_with_defect']
        ],
        '2025年': [
            metrics['2025']['mr_total'],
            metrics['2025']['mr_passed'],
            f"{metrics['2025']['mr_passed_rate']:.1f}%",
            metrics['2025']['mr_failed'],
            f"{metrics['2025']['mr_failed_rate']:.1f}%",
            'N/A',
            metrics['2025']['mr_with_defect'],
            f"{metrics['2025']['mr_defect_link_rate']:.1f}%",
            metrics['2025']['mr_failed_with_defect']
        ]
    }
    pd.DataFrame(mr_quality_data).to_excel(writer, sheet_name='2-MR执行质量', index=False)

    # Sheet 3: Project覆盖
    all_projects = set(metrics['2024']['project_dist'].keys()) | set(metrics['2025']['project_dist'].keys())
    project_rows = []
    for proj in sorted(all_projects):
        c24 = metrics['2024']['project_dist'].get(proj, 0)
        c25 = metrics['2025']['project_dist'].get(proj, 0)
        p24 = f"{c24/metrics['2024']['mr_total']*100:.1f}%" if metrics['2024']['mr_total'] > 0 else '0%'
        p25 = f"{c25/metrics['2025']['mr_total']*100:.1f}%" if metrics['2025']['mr_total'] > 0 else '0%'
        project_rows.append({'Project': proj, '2024年': c24, '2024占比': p24, '2025年': c25, '2025占比': p25, '变化': c25-c24})
    pd.DataFrame(project_rows).to_excel(writer, sheet_name='3-Project覆盖', index=False)

    # Sheet 4: 车型覆盖
    all_models = set(metrics['2024']['model_dist'].keys()) | set(metrics['2025']['model_dist'].keys())
    model_rows = []
    for model in sorted(all_models):
        c24 = metrics['2024']['model_dist'].get(model, 0)
        c25 = metrics['2025']['model_dist'].get(model, 0)
        if c24 > 20 or c25 > 20:
            change_pct = f"{((c25-c24)/c24*100):+.0f}%" if c24 > 0 else "New"
            model_rows.append({'车型': model, '2024年': c24, '2025年': c25, '变化': c25-c24, '变化率': change_pct})
    pd.DataFrame(model_rows).to_excel(writer, sheet_name='4-车型覆盖', index=False)

    # Sheet 5: 缺陷严重程度对比
    severity_rows = []
    severity_metrics = [
        ('缺陷总数', 'total'), ('Showstopper Confirmed', 'showstopper_confirmed'),
        ('Preventing Maturity', 'preventing_maturity'), ('Showstopper Candidate', 'showstopper_candidate'),
        ('Obstructing Maturity', 'obstructing_maturity'), ('Homologation', 'homologation'),
        ('06-Concluded', 'concluded_06'), ('09-CWA', 'cwa_09')
    ]
    for label, key in severity_metrics:
        v24 = metrics['2024']['defect_stats'][key]
        v25 = metrics['2025']['defect_stats'][key]
        severity_rows.append({'指标': label, '2024年': v24, '2025年': v25, '变化': v25-v24})
    pd.DataFrame(severity_rows).to_excel(writer, sheet_name='5-缺陷严重程度', index=False)

    # Sheet 6: 严重级别 vs 真实解决
    resolution_comparison = {
        '严重级别': ['Showstopper Confirmed', 'Preventing Maturity', 'Showstopper Candidate'],
        '2024年数量': [metrics['2024']['defect_stats']['showstopper_confirmed'],
                      metrics['2024']['defect_stats']['preventing_maturity'],
                      metrics['2024']['defect_stats']['showstopper_candidate']],
        '2024年06-Concluded': [metrics['2024']['defect_stats']['concluded_06']] * 3,
        '2025年数量': [metrics['2025']['defect_stats']['showstopper_confirmed'],
                      metrics['2025']['defect_stats']['preventing_maturity'],
                      metrics['2025']['defect_stats']['showstopper_candidate']],
        '2025年06-Concluded': [metrics['2025']['defect_stats']['concluded_06']] * 3
    }
    pd.DataFrame(resolution_comparison).to_excel(writer, sheet_name='6-严重级别vs解决', index=False)

    # Sheet 7: CWA Blocking Reason
    all_reasons = set(metrics['2024']['defect_stats']['cwa_reasons'].keys()) | set(metrics['2025']['defect_stats']['cwa_reasons'].keys())
    cwa_rows = []
    for reason in sorted(all_reasons, key=lambda r: metrics['2025']['defect_stats']['cwa_reasons'].get(r, 0), reverse=True)[:15]:
        c24 = metrics['2024']['defect_stats']['cwa_reasons'].get(reason, 0)
        c25 = metrics['2025']['defect_stats']['cwa_reasons'].get(reason, 0)
        cwa_rows.append({'Blocking Reason': reason, '2024年': c24, '2025年': c25})
    pd.DataFrame(cwa_rows).to_excel(writer, sheet_name='7-CWA Blocking Reason', index=False)

    # Sheet 8: ECU缺陷分布
    all_ecus = set(metrics['2024']['ecu_dist'].keys()) | set(metrics['2025']['ecu_dist'].keys())
    ecu_rows = []
    for ecu in sorted(all_ecus):
        c24 = metrics['2024']['ecu_dist'].get(ecu, 0)
        c25 = metrics['2025']['ecu_dist'].get(ecu, 0)
        if c24 > 10 or c25 > 10:
            ecu_rows.append({'ECU': ecu, '2024年': c24, '2025年': c25, '变化': c25-c24})
    pd.DataFrame(ecu_rows).to_excel(writer, sheet_name='8-ECU缺陷分布', index=False)

    # Sheet 9: 车型缺陷分布
    all_models_def = set(metrics['2024']['model_defect_dist'].keys()) | set(metrics['2025']['model_defect_dist'].keys())
    model_def_rows = []
    for model in sorted(all_models_def):
        c24 = metrics['2024']['model_defect_dist'].get(model, 0)
        c25 = metrics['2025']['model_defect_dist'].get(model, 0)
        if c24 > 5 or c25 > 5:
            change_pct = f"{((c25-c24)/c24*100):+.0f}%" if c24 > 0 else "New"
            model_def_rows.append({'车型': model, '2024年': c24, '2025年': c25, '变化': c25-c24, '变化率': change_pct})
    pd.DataFrame(model_def_rows).to_excel(writer, sheet_name='9-车型缺陷分布', index=False)

    # Sheet 10: 缺陷发现能力
    discovery_data = {
        '指标': ['缺陷密度(每1000测试)', '发现问题效率(%)', '真实解决率(%)', '平均处理周期(天)'],
        '2024年': [
            f"{metrics['2024']['defect_density']:.1f}",
            f"{metrics['2024']['discovery_efficiency']:.1f}%",
            f"{metrics['2024']['real_resolution_rate']:.1f}%",
            metrics['2024']['processing']['avg_cycle_days']
        ],
        '2025年': [
            f"{metrics['2025']['defect_density']:.1f}",
            f"{metrics['2025']['discovery_efficiency']:.1f}%",
            f"{metrics['2025']['real_resolution_rate']:.1f}%",
            metrics['2025']['processing']['avg_cycle_days']
        ]
    }
    pd.DataFrame(discovery_data).to_excel(writer, sheet_name='10-缺陷发现能力', index=False)

    # Sheet 11: Inflow/Outflow
    flow_data = {
        '指标': ['总流入(Inflow)', '总流出(Outflow)', '净流量'],
        '2024年': [
            metrics['2024']['flow']['total_inflow'],
            metrics['2024']['flow']['total_outflow'],
            metrics['2024']['flow']['total_inflow'] - metrics['2024']['flow']['total_outflow']
        ],
        '2025年': [
            metrics['2025']['flow']['total_inflow'],
            metrics['2025']['flow']['total_outflow'],
            metrics['2025']['flow']['total_inflow'] - metrics['2025']['flow']['total_outflow']
        ]
    }
    pd.DataFrame(flow_data).to_excel(writer, sheet_name='11-Inflow Outflow', index=False)

    # Sheet 12: 团队效能
    team_data = {
        '指标': ['测试人员数量', '人均缺陷发现数', 'Top Tester', 'Top Tester发现数'],
        '2024年': [
            metrics['2024']['team']['total_testers'],
            metrics['2024']['team']['avg_per_tester'],
            metrics['2024']['team']['top_tester'],
            metrics['2024']['team']['top_count']
        ],
        '2025年': [
            metrics['2025']['team']['total_testers'],
            metrics['2025']['team']['avg_per_tester'],
            metrics['2025']['team']['top_tester'],
            metrics['2025']['team']['top_count']
        ]
    }
    pd.DataFrame(team_data).to_excel(writer, sheet_name='12-团队效能', index=False)

    # Sheet 13: Feature Region
    region_data = {
        'Feature Region': ['China Specific', 'Global', 'China占比(%)'],
        '2024年': [
            metrics['2024']['feature_region']['china_specific'],
            metrics['2024']['feature_region']['global'],
            f"{metrics['2024']['feature_region']['china_ratio']:.1f}%"
        ],
        '2025年': [
            metrics['2025']['feature_region']['china_specific'],
            metrics['2025']['feature_region']['global'],
            f"{metrics['2025']['feature_region']['china_ratio']:.1f}%"
        ]
    }
    pd.DataFrame(region_data).to_excel(writer, sheet_name='13-Feature Region', index=False)

print(f"\n✅ Excel报告已生成: {output_file}")

# ==================== 5. 生成HTML报告 ====================
print("\n【5. 生成HTML报告】")

html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>2024 vs 2025 综合KPI对比报告 - 完整版</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
            background: #f5f7fa;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        h1 {{
            text-align: center;
            color: #1e3c72;
            margin-bottom: 10px;
            padding-bottom: 15px;
            border-bottom: 3px solid #2a5298;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #1e3c72;
            margin: 30px 0 15px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #e9ecef;
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 14px;
        }}
        th {{
            background: #2a5298;
            color: white;
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 10px 15px;
            border-bottom: 1px solid #e9ecef;
        }}
        tr:hover {{ background: #f8f9fa; }}
        .numeric {{ text-align: right; }}
        .positive {{ color: #28a745; font-weight: bold; }}
        .negative {{ color: #dc3545; font-weight: bold; }}
        .highlight {{ background: #fff3cd; }}
        .section {{ margin-bottom: 40px; }}
        .summary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .summary h3 {{ margin-bottom: 15px; }}
        .summary ul {{ margin-left: 20px; }}
        .summary li {{ margin: 8px 0; }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .kpi-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #2a5298;
        }}
        .kpi-card h4 {{
            color: #1e3c72;
            margin-bottom: 10px;
            font-size: 14px;
        }}
        .kpi-value {{
            font-size: 24px;
            font-weight: bold;
            color: #2a5298;
        }}
        .kpi-change {{
            font-size: 14px;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 2024 vs 2025 综合KPI对比报告 - 完整版</h1>
        <p class="subtitle">包含7大类测试度量指标 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>

        <!-- 核心指标概览 -->
        <div class="section">
            <h2>🎯 核心指标概览</h2>
            <table>
                <tr>
                    <th>指标类别</th>
                    <th class="numeric">2024年</th>
                    <th class="numeric">2025年</th>
                    <th class="numeric">变化</th>
                </tr>
                <tr>
                    <td>测试执行总数</td>
                    <td class="numeric">{metrics['2024']['mr_total']:,}</td>
                    <td class="numeric">{metrics['2025']['mr_total']:,}</td>
                    <td class="numeric {'positive' if metrics['2025']['mr_total'] > metrics['2024']['mr_total'] else 'negative'}">{metrics['2025']['mr_total'] - metrics['2024']['mr_total']:+d}</td>
                </tr>
                <tr>
                    <td>测试Passed率</td>
                    <td class="numeric">{metrics['2024']['mr_passed_rate']:.1f}%</td>
                    <td class="numeric">{metrics['2025']['mr_passed_rate']:.1f}%</td>
                    <td class="numeric {'positive' if metrics['2025']['mr_passed_rate'] > metrics['2024']['mr_passed_rate'] else 'negative'}">{metrics['2025']['mr_passed_rate'] - metrics['2024']['mr_passed_rate']:+.1f}pp</td>
                </tr>
                <tr>
                    <td>缺陷总数</td>
                    <td class="numeric">{metrics['2024']['defect_stats']['total']:,}</td>
                    <td class="numeric">{metrics['2025']['defect_stats']['total']:,}</td>
                    <td class="numeric {'negative' if metrics['2025']['defect_stats']['total'] > metrics['2024']['defect_stats']['total'] else 'positive'}">{metrics['2025']['defect_stats']['total'] - metrics['2024']['defect_stats']['total']:+d}</td>
                </tr>
                <tr>
                    <td>缺陷密度(每1000测试)</td>
                    <td class="numeric">{metrics['2024']['defect_density']:.1f}</td>
                    <td class="numeric">{metrics['2025']['defect_density']:.1f}</td>
                    <td class="numeric {'negative' if metrics['2025']['defect_density'] > metrics['2024']['defect_density'] else 'positive'}">{metrics['2025']['defect_density'] - metrics['2024']['defect_density']:+.1f}</td>
                </tr>
                <tr>
                    <td>发现问题效率(%)</td>
                    <td class="numeric">{metrics['2024']['discovery_efficiency']:.1f}%</td>
                    <td class="numeric">{metrics['2025']['discovery_efficiency']:.1f}%</td>
                    <td class="numeric {'positive' if metrics['2025']['discovery_efficiency'] > metrics['2024']['discovery_efficiency'] else 'negative'}">{metrics['2025']['discovery_efficiency'] - metrics['2024']['discovery_efficiency']:+.1f}pp</td>
                </tr>
                <tr>
                    <td>真实解决率</td>
                    <td class="numeric">{metrics['2024']['real_resolution_rate']:.1f}%</td>
                    <td class="numeric">{metrics['2025']['real_resolution_rate']:.1f}%</td>
                    <td class="numeric {'positive' if metrics['2025']['real_resolution_rate'] > metrics['2024']['real_resolution_rate'] else 'negative'}">{metrics['2025']['real_resolution_rate'] - metrics['2024']['real_resolution_rate']:+.1f}pp</td>
                </tr>
            </table>
        </div>

        <!-- Project覆盖 -->
        <div class="section">
            <h2>🔧 Project覆盖对比</h2>
            <table>
                <tr>
                    <th>Project</th>
                    <th class="numeric">2024年</th>
                    <th class="numeric">2024占比</th>
                    <th class="numeric">2025年</th>
                    <th class="numeric">2025占比</th>
                </tr>
'''

for proj in sorted(set(metrics['2024']['project_dist'].keys()) | set(metrics['2025']['project_dist'].keys())):
    c24 = metrics['2024']['project_dist'].get(proj, 0)
    c25 = metrics['2025']['project_dist'].get(proj, 0)
    p24 = f"{c24/metrics['2024']['mr_total']*100:.1f}%" if metrics['2024']['mr_total'] > 0 else '0%'
    p25 = f"{c25/metrics['2025']['mr_total']*100:.1f}%" if metrics['2025']['mr_total'] > 0 else '0%'
    html_content += f'''                <tr>
                    <td>{proj}</td>
                    <td class="numeric">{c24:,}</td>
                    <td class="numeric">{p24}</td>
                    <td class="numeric">{c25:,}</td>
                    <td class="numeric">{p25}</td>
                </tr>
'''

html_content += f'''            </table>
        </div>

        <!-- 缺陷严重程度 -->
        <div class="section">
            <h2>🔴 缺陷严重程度对比</h2>
            <table>
                <tr>
                    <th>指标</th>
                    <th class="numeric">2024年</th>
                    <th class="numeric">2025年</th>
                    <th class="numeric">变化</th>
                </tr>
'''

for label, key in [('Showstopper Confirmed', 'showstopper_confirmed'), ('Preventing Maturity', 'preventing_maturity'),
                   ('Showstopper Candidate', 'showstopper_candidate'), ('06-Concluded', 'concluded_06'), ('09-CWA', 'cwa_09')]:
    v24 = metrics['2024']['defect_stats'][key]
    v25 = metrics['2025']['defect_stats'][key]
    change_class = 'positive' if (v25 < v24 and key != 'concluded_06') or (key == 'concluded_06' and v25 > v24) else 'negative'
    html_content += f'''                <tr>
                    <td>{label}</td>
                    <td class="numeric">{v24:,}</td>
                    <td class="numeric">{v25:,}</td>
                    <td class="numeric {change_class}">{v25-v24:+d}</td>
                </tr>
'''

html_content += f'''            </table>
        </div>

        <!-- ECU缺陷分布 -->
        <div class="section">
            <h2>🔌 ECU缺陷分布对比 (Top 10)</h2>
            <table>
                <tr>
                    <th>ECU</th>
                    <th class="numeric">2024年</th>
                    <th class="numeric">2025年</th>
                    <th class="numeric">变化</th>
                </tr>
'''

for ecu in sorted(set(metrics['2024']['ecu_dist'].keys()) | set(metrics['2025']['ecu_dist'].keys()),
                  key=lambda x: metrics['2025']['ecu_dist'].get(x, 0), reverse=True)[:10]:
    c24 = metrics['2024']['ecu_dist'].get(ecu, 0)
    c25 = metrics['2025']['ecu_dist'].get(ecu, 0)
    change_class = 'positive' if c25 < c24 else 'negative'
    html_content += f'''                <tr>
                    <td>{ecu}</td>
                    <td class="numeric">{c24:,}</td>
                    <td class="numeric">{c25:,}</td>
                    <td class="numeric {change_class}">{c25-c24:+d}</td>
                </tr>
'''

html_content += f'''            </table>
        </div>

        <!-- Feature Region -->
        <div class="section">
            <h2>🌏 Feature Region覆盖</h2>
            <table>
                <tr>
                    <th>Region</th>
                    <th class="numeric">2024年</th>
                    <th class="numeric">2025年</th>
                </tr>
                <tr>
                    <td>China Specific</td>
                    <td class="numeric">{metrics['2024']['feature_region']['china_specific']:,} ({metrics['2024']['feature_region']['china_ratio']:.1f}%)</td>
                    <td class="numeric">{metrics['2025']['feature_region']['china_specific']:,} ({metrics['2025']['feature_region']['china_ratio']:.1f}%)</td>
                </tr>
                <tr>
                    <td>Global</td>
                    <td class="numeric">{metrics['2024']['feature_region']['global']:,}</td>
                    <td class="numeric">{metrics['2025']['feature_region']['global']:,}</td>
                </tr>
            </table>
        </div>

        <!-- 团队效能 -->
        <div class="section">
            <h2>👥 团队效能对比</h2>
            <table>
                <tr>
                    <th>指标</th>
                    <th class="numeric">2024年</th>
                    <th class="numeric">2025年</th>
                </tr>
                <tr>
                    <td>测试人员数量</td>
                    <td class="numeric">{metrics['2024']['team']['total_testers']}</td>
                    <td class="numeric">{metrics['2025']['team']['total_testers']}</td>
                </tr>
                <tr>
                    <td>人均缺陷发现数</td>
                    <td class="numeric">{metrics['2024']['team']['avg_per_tester']}</td>
                    <td class="numeric">{metrics['2025']['team']['avg_per_tester']}</td>
                </tr>
                <tr>
                    <td>Top Tester</td>
                    <td class="numeric">{metrics['2024']['team']['top_tester']} ({metrics['2024']['team']['top_count']})</td>
                    <td class="numeric">{metrics['2025']['team']['top_tester']} ({metrics['2025']['team']['top_count']})</td>
                </tr>
            </table>
        </div>

        <!-- 关键洞察 -->
        <div class="summary">
            <h3>💡 关键洞察</h3>
            <ul>
                <li>✅ <strong>测试执行增长 {((metrics['2025']['mr_total']-metrics['2024']['mr_total'])/metrics['2024']['mr_total']*100):.1f}%</strong>：从 {metrics['2024']['mr_total']:,} 提升至 {metrics['2025']['mr_total']:,}</li>
                <li>✅ <strong>Passed率提升 {metrics['2025']['mr_passed_rate']-metrics['2024']['mr_passed_rate']:.1f}pp</strong>：从 {metrics['2024']['mr_passed_rate']:.1f}% 提升至 {metrics['2025']['mr_passed_rate']:.1f}%</li>
                <li>✅ <strong>Preventing Maturity下降 {((metrics['2025']['defect_stats']['preventing_maturity']-metrics['2024']['defect_stats']['preventing_maturity'])/metrics['2024']['defect_stats']['preventing_maturity']*100):.1f}%</strong>：阻成熟度问题改善</li>
                <li>⚠️ <strong>Showstopper Confirmed增长 {((metrics['2025']['defect_stats']['showstopper_confirmed']-metrics['2024']['defect_stats']['showstopper_confirmed'])/metrics['2024']['defect_stats']['showstopper_confirmed']*100):.1f}%</strong>：最严重级别问题需攻关</li>
                <li>📊 <strong>缺陷密度{'上升' if metrics['2025']['defect_density'] > metrics['2024']['defect_density'] else '下降'}</strong>：从 {metrics['2024']['defect_density']:.1f} 到 {metrics['2025']['defect_density']:.1f} (每1000测试)</li>
            </ul>
        </div>

    </div>
</body>
</html>
'''

with open('综合KPI报告_2024_2025_完整版.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✅ HTML报告已生成: 综合KPI报告_2024_2025_完整版.html")

print("\n" + "="*80)
print("【分析完成】")
print("="*80)
print(f"""
生成的文件:
1. 综合KPI报告_2024_2025_完整版.xlsx - 包含13个工作表的详细数据
2. 综合KPI报告_2024_2025_完整版.html - HTML格式便于查看

报告包含的7大类度量指标:
┌─────────────────────────────────────────────────────────────┐
│ 1. 基础MR执行质量 - 通过率、缺陷关联率                        │
│ 2. Project/车型覆盖 - 按项目、车型的测试分布                  │
│ 3. 测试周趋势 - 按周统计执行量(Week trend)                   │
│ 4. 缺陷严重程度 - Showstopper/Preventing等                   │
│ 5. 缺陷发现能力 - 密度、发现问题效率、真实解决率              │
│ 6. ECU/车型缺陷分布 - 按ECU和车型的缺陷分布                   │
│ 7. 处理周期分析 - 平均处理时间                               │
│ 8. Inflow/Outflow - 缺陷流入流出分析                         │
│ 9. 团队效能 - 测试人员数量、人均发现数、Top Tester           │
│ 10. Feature Region - China Specific vs Global 覆盖          │
│ 11. CWA Blocking Reason - 关闭原因分析                       │
└─────────────────────────────────────────────────────────────┘

核心指标对比:
                    2024年              2025年              变化
测试执行总数        {metrics['2024']['mr_total']:,}            {metrics['2025']['mr_total']:,}            +{((metrics['2025']['mr_total']-metrics['2024']['mr_total'])/metrics['2024']['mr_total']*100):.1f}%
测试Passed率        {metrics['2024']['mr_passed_rate']:.1f}%              {metrics['2025']['mr_passed_rate']:.1f}%              +{metrics['2025']['mr_passed_rate']-metrics['2024']['mr_passed_rate']:.1f}pp
缺陷密度            {metrics['2024']['defect_density']:.1f}               {metrics['2025']['defect_density']:.1f}               {'+' if metrics['2025']['defect_density'] > metrics['2024']['defect_density'] else ''}{metrics['2025']['defect_density']-metrics['2024']['defect_density']:.1f}
发现问题效率        {metrics['2024']['discovery_efficiency']:.1f}%              {metrics['2025']['discovery_efficiency']:.1f}%              {'+' if metrics['2025']['discovery_efficiency'] > metrics['2024']['discovery_efficiency'] else ''}{metrics['2025']['discovery_efficiency']-metrics['2024']['discovery_efficiency']:.1f}pp
真实解决率          {metrics['2024']['real_resolution_rate']:.1f}%              {metrics['2025']['real_resolution_rate']:.1f}%              {'+' if metrics['2025']['real_resolution_rate'] > metrics['2024']['real_resolution_rate'] else ''}{metrics['2025']['real_resolution_rate']-metrics['2024']['real_resolution_rate']:.1f}pp
""")
