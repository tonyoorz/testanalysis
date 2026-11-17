#!/usr/bin/env python3
"""
Q-Gate Phase Transition效率分析HTML报告生成器
格式参照: 高级KPI分析报告_2024_2025.html
"""

import json
import os
import pandas as pd
from collections import Counter
from datetime import datetime
import re
import longrunner_analysis as lra

# 配置
DEFAULT_TEAMS = [
    "DTSV_China",
    "Spotlight_DTSV_China",
    "Spotlight_FIT",
    "[AT]BBA_Basis-FIT",
    "[AT]FIT_LAENDER_CHINA",
    "[AT]W71-FIT",
    "[AT]W72-FIT",
]

CHINA_SPECIFIC_FIF = {
    "Connected Music China [01.04.01.06.04]",
    "DELETED_BMW Points (Mobile App) [01.04.03.02.01.01.01]",
    "Festival Mode [01.04.02.01.02.01.04]",
    "Itinerary (Mobile App) [01.04.03.01.01.07.09]",
    "Play audio via Online Services (Connected Music) [01.04.01.01.02]",
    "Provide 3rd party gaming enablement [01.04.01.02.03]",
    "Provide 3rd Party Gaming App [01.04.01.02.03.05]",
    "Provide App Center China [01.04.01.06.09]",
    "Provide Festival Mode [01.04.02.01.04.08]",
    "Provide Karaoke Service [01.04.01.06.10]",
    "Provide Projected Modes China [01.04.01.06.13]",
    "QQ Music [01.04.01.06.04.02]",
    "QQ Music [01.04.01.06.06.02]",
    "Smart Access / Digital Key (Plus) [01.03.03.03.04]",
    "Tencent MiniProgramPlatform (Tencent MPP) [01.04.01.06.01]",
    "Tencent WeChat [01.04.01.06.02]",
    "Use App Store China [01.04.01.06.07]",
    "Use Speech operation [01.04.02.01.01.05]",
    "Video streaming China [01.04.01.06.05]",
    "Voice Interface [01.04.02.01.01.02]",
    "WeChat VoiP Call [01.04.01.06.02.02]",
    "Ximalaya [01.04.01.06.04.01]",
    "Ximalaya [01.04.01.06.06.03]",
}

def slugify_team_name(team_name: str) -> str:
    if not team_name:
        return "UNKNOWN_TEAM"
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", team_name.strip())
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "UNKNOWN_TEAM"

def load_defect_ids_for_team(defect_dir: str, team: str):
    team_slug = slugify_team_name(team)
    ids = set()
    if not os.path.isdir(defect_dir):
        return ids
    for filename in os.listdir(defect_dir):
        if not filename.endswith("_defect.json"):
            continue
        if f"_{team_slug}_defect.json" not in filename:
            continue
        path = os.path.join(defect_dir, filename)
        try:
            df = pd.read_json(path)
        except ValueError:
            continue
        if "id" not in df.columns:
            continue
        ids.update({str(x) for x in df["id"].dropna().tolist()})
    return ids

def load_defect_info_for_team(defect_dir: str, team: str):
    team_slug = slugify_team_name(team)
    info = {}
    if not os.path.isdir(defect_dir):
        return info
    for filename in os.listdir(defect_dir):
        if not filename.endswith("_defect.json"):
            continue
        if f"_{team_slug}_defect.json" not in filename:
            continue
        path = os.path.join(defect_dir, filename)
        try:
            df = pd.read_json(path)
        except ValueError:
            continue
        if df.empty or "id" not in df.columns:
            continue
        for _, row in df.iterrows():
            tid = str(row.get("id") or "").strip()
            if not tid:
                continue
            name = str(row.get("name") or "").strip()
            detected_by = row.get("detected_by")
            tester = ""
            if isinstance(detected_by, dict):
                tester = str(detected_by.get("full_name") or "").strip()
            info[tid] = {"name": name, "tester": tester}
    return info

def classify_group(phase_transition: str) -> str:
    from_part, to_part = phase_transition, ""
    if "→" in phase_transition:
        from_part, to_part = phase_transition.split("→", 1)
    from_part = from_part.strip()
    to_part = to_part.strip()

    def get_prefix(phase_text: str):
        m = re.match(r"^(\d{2})-", (phase_text or "").strip())
        return m.group(1) if m else None

    from_prefix = get_prefix(from_part)
    to_prefix = get_prefix(to_part)

    if from_prefix == "09" and to_prefix == "01":
        return "Integration"
    if from_prefix == "06" and to_prefix == "05":
        return "Integration"

    if not from_prefix:
        return "Other"

    if from_prefix in {"02", "07"}:
        return "Q-Gate"
    if from_prefix in {"00", "01", "08"}:
        return "Integration"
    if from_prefix in {"03", "04", "05"}:
        return "CoC"
    return "Other"

def build_team_statistics(team: str, ticket_ids, history_dir: str, defect_info: dict):
    bulk = lra.bulk_analyze_phases(
        list(ticket_ids),
        history_folder=history_dir,
        show_progress=True,
        max_workers=min(24, max(4, (os.cpu_count() or 4) * 2)),
        cache_dir="qgate_cache",
        use_cache=True,
        return_all_results=False,
        return_duration_records=True,
        return_ticket_meta=True,
    )
    
    all_label = "(All)"
    duration_records = bulk.get("phase_duration_records") or {}
    ticket_meta = bulk.get("ticket_meta") or {}

    def ticket_fif_category(tid: str):
        items = ticket_meta.get(str(tid)) or []
        items_set = {str(x).strip() for x in items if str(x).strip()}
        if not items_set:
            return None
        if items_set.intersection(CHINA_SPECIFIC_FIF):
            return "China Specific"
        return "Global"

    rows = []

    hours_by_key = {}
    for transition, records in (duration_records or {}).items():
        group = classify_group(transition)
        for r in records or []:
            h = r.get("duration_hours")
            if h is None:
                continue
            try:
                h = float(h)
            except Exception:
                continue

            user = (str(r.get("changed_by") or "").strip()) or "Unknown"
            tid = r.get("ticket_id")
            fif = ticket_fif_category(str(tid)) if tid is not None else None

            if fif:
                dims = {(user, fif), (all_label, fif), (user, all_label), (all_label, all_label)}
            else:
                dims = {(user, all_label), (all_label, all_label)}

            for changed_by_val, fif_val in dims:
                key = (transition, group, changed_by_val, fif_val)
                hours_by_key.setdefault(key, []).append(h)

    for (transition, group, changed_by_val, fif_val), hours in hours_by_key.items():
        if not hours:
            continue
        hours_sorted = sorted(hours)
        count = len(hours_sorted)
        avg_hours = round(sum(hours_sorted) / count, 2)
        avg_days = round(avg_hours / 24, 2)
        min_hours = round(hours_sorted[0], 2)
        max_hours = round(hours_sorted[-1], 2)
        median_hours = round(hours_sorted[count // 2], 2)
        
        rows.append({
            "Team": team,
            "Phase_Transition": transition,
            "Group": group,
            "Changed_By": changed_by_val,
            "FiF": fif_val,
            "Count": count,
            "Avg_Hours": avg_hours,
            "Avg_Days": avg_days,
            "Min_Hours": min_hours,
            "Max_Hours": max_hours,
            "Median_Hours": median_hours,
        })

    df = pd.DataFrame(rows)
    return df, bulk.get("successful_count", 0), bulk.get("failed_count", 0)

def compute_all_teams_data(defect_dir: str, history_dir: str, teams):
    all_team_dfs = []
    per_team_meta = []

    print(f"开始按 team 统计：teams={len(teams)} | defect_dir={defect_dir} | history_dir={history_dir}")

    for idx, team in enumerate(teams, start=1):
        print(f"[{idx}/{len(teams)}] {team}...", end=" ", flush=True)
        ticket_ids = load_defect_ids_for_team(defect_dir, team)
        if not ticket_ids:
            per_team_meta.append({"Team": team, "Defects": 0, "History_OK": 0, "History_Missing_or_Error": 0})
            print("无数据")
            continue
        defect_info = load_defect_info_for_team(defect_dir, team)
        print(f"defects={len(ticket_ids)}", flush=True)
        df_stats, ok, bad = build_team_statistics(
            team,
            ticket_ids,
            history_dir,
            defect_info=defect_info,
        )
        all_team_dfs.append(df_stats)
        per_team_meta.append({"Team": team, "Defects": len(ticket_ids), "History_OK": ok, "History_Missing_or_Error": bad})

    meta_df = pd.DataFrame(per_team_meta)
    stats_df = pd.concat(all_team_dfs, ignore_index=True) if all_team_dfs else pd.DataFrame()
    return meta_df, stats_df

def build_summary_frames(stats_df: pd.DataFrame, min_transition_count: int):
    if stats_df.empty:
        return pd.DataFrame(), pd.DataFrame()
    filtered = stats_df[stats_df["Count"] >= int(min_transition_count)].copy()
    if filtered.empty:
        return filtered, pd.DataFrame()

    # 只保留 (All) 的数据
    if "Changed_By" in filtered.columns:
        filtered = filtered[filtered["Changed_By"] == "(All)"].copy()
    if "FiF" in filtered.columns:
        filtered = filtered[filtered["FiF"] == "(All)"].copy()

    summary_rows = []
    for (team, group), gdf in filtered.groupby(["Team", "Group"], dropna=False):
        # 计算加权平均天数
        total_count = gdf["Count"].sum()
        weighted_avg_days = (gdf["Avg_Days"] * gdf["Count"]).sum() / total_count if total_count > 0 else 0
        
        summary_rows.append({
            "Team": team,
            "Group": group,
            "Samples_Total": int(total_count),
            "Transitions_Total": int(gdf.shape[0]),
            "Weighted_Avg_Days": round(weighted_avg_days, 3),
        })
    
    summary_df = pd.DataFrame(summary_rows).sort_values(["Team", "Group"])
    return filtered, summary_df

def generate_html_report(meta_df, stats_df, summary_df):
    """生成HTML报告"""
    
    # 计算关键指标
    total_defects = meta_df['Defects'].sum()
    total_history_ok = meta_df['History_OK'].sum()
    total_history_bad = meta_df['History_Missing_or_Error'].sum()
    
    # 按Group统计
    group_stats = summary_df.groupby('Group').agg({
        'Samples_Total': 'sum',
        'Weighted_Avg_Days': 'mean'
    }).reset_index()
    
    # 按Team统计
    team_stats = summary_df.groupby('Team').agg({
        'Samples_Total': 'sum',
        'Weighted_Avg_Days': 'mean'
    }).reset_index()
    
    # 找出最慢的Phase Transition (Top 10)
    if not stats_df.empty:
        slowest_transitions = stats_df.nlargest(10, 'Avg_Days')[['Phase_Transition', 'Group', 'Count', 'Avg_Days', 'Median_Hours']].to_dict('records')
    else:
        slowest_transitions = []
    
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Q-Gate Phase Transition效率分析报告</title>
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

        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 50px 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 15px; }}
        .header p {{ font-size: 1.1em; opacity: 0.9; }}

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

        .content {{ padding: 40px; }}

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
        .kpi-value {{
            font-size: 2em;
            font-weight: bold;
            color: var(--primary);
            margin: 10px 0;
        }}
        .kpi-subtitle {{
            font-size: 0.85em;
            color: #95a5a6;
        }}

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

        .risk-item {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
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

        .footer {{
            background: var(--primary);
            color: white;
            text-align: center;
            padding: 25px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🚀 Q-Gate Phase Transition效率分析</h1>
            <p>深度洞察：Phase Transition效率 · Long Runner分析 · Team性能对比</p>
        </div>

        <!-- Executive Summary -->
        <div class="exec-summary">
            <h2>📊 执行摘要：关键指标一览</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="summary-year">总缺陷数</div>
                    <div class="summary-value">{total_defects:,}</div>
                    <div style="font-size:0.85em;color:#7f8c8d;margin-top:5px;">涵盖 {len(meta_df)} 个团队</div>
                </div>
                <div class="summary-item">
                    <div class="summary-year">成功分析历史</div>
                    <div class="summary-value">{total_history_ok:,}</div>
                    <div style="font-size:0.85em;color:#7f8c8d;margin-top:5px;">覆盖率: {total_history_ok/(total_history_ok+total_history_bad)*100:.1f}%</div>
                </div>
                <div class="summary-item">
                    <div class="summary-year">Phase Transitions</div>
                    <div class="summary-value">{len(stats_df):,}</div>
                    <div style="font-size:0.85em;color:#7f8c8d;margin-top:5px;">唯一转换路径</div>
                </div>
                <div class="summary-item">
                    <div class="summary-year">总样本数</div>
                    <div class="summary-value">{stats_df['Count'].sum():,}</div>
                    <div style="font-size:0.85em;color:#7f8c8d;margin-top:5px;">Phase Transition记录</div>
                </div>
            </div>
        </div>

        <div class="content">
            <!-- Section 1: Group Analysis -->
            <div class="section">
                <h2>🔍 一、Group效率分析</h2>

                <div class="kpi-row">
'''
    
    # 添加Group统计卡片
    for _, row in group_stats.iterrows():
        html_content += f'''                    <div class="kpi-card">
                        <div class="kpi-title">{row['Group']}</div>
                        <div class="kpi-value">{row['Weighted_Avg_Days']:.1f} 天</div>
                        <div class="kpi-subtitle">{row['Samples_Total']:,} 个样本</div>
                    </div>
'''
    
    html_content += '''                </div>

                <table class="simple-table">
                    <thead>
                        <tr>
                            <th>Group类型</th>
                            <th>样本总数</th>
                            <th>平均时长(天)</th>
                            <th>说明</th>
                        </tr>
                    </thead>
                    <tbody>
'''
    
    # 添加Group说明
    group_descriptions = {
        'Q-Gate': '质量门禁阶段转换',
        'Integration': '集成测试阶段转换',
        'CoC': 'CoC(Completion of Completion)阶段',
        'Other': '其他阶段转换'
    }
    
    for _, row in group_stats.iterrows():
        desc = group_descriptions.get(row['Group'], '未分类')
        html_content += f'''                        <tr>
                            <td>{row['Group']}</td>
                            <td>{row['Samples_Total']:,}</td>
                            <td>{row['Weighted_Avg_Days']:.2f}</td>
                            <td>{desc}</td>
                        </tr>
'''
    
    html_content += '''                    </tbody>
                </table>
            </div>

            <!-- Section 2: Team Analysis -->
            <div class="section">
                <h2>👥 二、Team效率对比</h2>

                <table class="simple-table">
                    <thead>
                        <tr>
                            <th>Team</th>
                            <th>缺陷数</th>
                            <th>成功分析</th>
                            <th>失败/缺失</th>
                            <th>覆盖率</th>
                        </tr>
                    </thead>
                    <tbody>
'''
    
    # 添加Team统计
    for _, row in meta_df.iterrows():
        coverage = row['History_OK'] / (row['History_OK'] + row['History_Missing_or_Error']) * 100 if (row['History_OK'] + row['History_Missing_or_Error']) > 0 else 0
        html_content += f'''                        <tr>
                            <td>{row['Team']}</td>
                            <td>{row['Defects']:,}</td>
                            <td>{row['History_OK']:,}</td>
                            <td>{row['History_Missing_or_Error']:,}</td>
                            <td>{coverage:.1f}%</td>
                        </tr>
'''
    
    html_content += '''                    </tbody>
                </table>
            </div>

            <!-- Section 3: Long Runner Analysis -->
            <div class="section">
                <h2>⚠️ 三、Long Runner分析 (Top 10最慢Phase Transition)</h2>

                <div class="insights">
                    <h3>💡 关键发现</h3>
                    <ul>
'''
    
    if slowest_transitions:
        avg_slow = sum([t['Avg_Days'] for t in slowest_transitions]) / len(slowest_transitions)
        html_content += f'''                        <li><strong>平均时长：</strong>Top 10最慢转换的平均时长为 <strong>{avg_slow:.1f}天</strong></li>
                        <li><strong>最长转换：</strong>{slowest_transitions[0]['Phase_Transition']} 需要 <strong>{slowest_transitions[0]['Avg_Days']:.1f}天</strong></li>
                        <li><strong>建议：</strong>重点关注这些Phase Transition，优化流程以缩短周期</li>
'''
    else:
        html_content += '''                        <li>暂无Long Runner数据</li>
'''
    
    html_content += '''                    </ul>
                </div>

                <table class="simple-table">
                    <thead>
                        <tr>
                            <th>Phase Transition</th>
                            <th>Group</th>
                            <th>样本数</th>
                            <th>平均时长(天)</th>
                            <th>中位数(小时)</th>
                        </tr>
                    </thead>
                    <tbody>
'''
    
    # 添加最慢转换
    for i, row in enumerate(slowest_transitions, 1):
        risk_class = 'risk-high' if row['Avg_Days'] > 30 else ('risk-medium' if row['Avg_Days'] > 15 else 'risk-low')
        html_content += f'''                        <tr>
                            <td>{row['Phase_Transition']}</td>
                            <td>{row['Group']}</td>
                            <td>{row['Count']}</td>
                            <td>{row['Avg_Days']:.2f}</td>
                            <td>{row['Median_Hours']:.1f}</td>
                        </tr>
'''
    
    html_content += '''                    </tbody>
                </table>
            </div>

            <!-- Section 4: Detailed Statistics -->
            <div class="section">
                <h2>📊 四、详细统计 (按Team & Group)</h2>

                <table class="simple-table">
                    <thead>
                        <tr>
                            <th>Team</th>
                            <th>Group</th>
                            <th>样本总数</th>
                            <th>转换路径数</th>
                            <th>加权平均时长(天)</th>
                        </tr>
                    </thead>
                    <tbody>
'''
    
    # 添加详细统计
    for _, row in summary_df.iterrows():
        html_content += f'''                        <tr>
                            <td>{row['Team']}</td>
                            <td>{row['Group']}</td>
                            <td>{row['Samples_Total']:,}</td>
                            <td>{row['Transitions_Total']}</td>
                            <td>{row['Weighted_Avg_Days']:.2f}</td>
                        </tr>
'''
    
    html_content += '''                    </tbody>
                </table>
            </div>

            <!-- Section 5: Recommendations -->
            <div class="section">
                <h2>🎯 五、战略建议</h2>

                <div class="insights">
                    <h3>📋 改进建议 (按优先级)</h3>
                    <ul>
                        <li><strong>【P0-紧急】</strong>针对Long Runner进行专项优化，缩短关键Phase Transition的时长</li>
                        <li><strong>【P1-高】</strong>提高历史数据覆盖率，当前覆盖率为{total_history_ok/(total_history_ok+total_history_bad)*100:.1f}%</li>
                        <li><strong>【P1-高】</strong>建立Phase Transition监控机制，实时预警超时转换</li>
                        <li><strong>【P2-中】</strong>针对Q-Gate阶段建立专项流程优化小组</li>
                        <li><strong>【P2-中】</strong>分析Integration阶段的瓶颈，提高集成效率</li>
                    </ul>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>Q-Gate Phase Transition效率分析报告 | 数据来源: qgate/defect, qgate/history | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
    </div>
</body>
</html>'''
    
    return html_content

def main():
    print("="*80)
    print("📊 Q-Gate Phase Transition效率分析报告生成器")
    print("="*80)
    
    defect_dir = "qgate/defect"
    history_dir = "qgate/history"
    
    # 加载并分析数据
    meta_df, stats_df = compute_all_teams_data(defect_dir, history_dir, DEFAULT_TEAMS)
    
    if stats_df.empty:
        print("❌ 未找到可分析的数据")
        return
    
    # 构建摘要
    stats_df_filtered, summary_df = build_summary_frames(stats_df, min_transition_count=5)
    
    if summary_df.empty:
        print("❌ 筛选后无数据")
        return
    
    # 生成HTML报告
    html_content = generate_html_report(meta_df, stats_df_filtered, summary_df)
    
    # 保存HTML文件
    output_file = "qgate_phase_transition_report.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ HTML报告已生成: {output_file}")
    
    # 保存CSV数据
    meta_df.to_csv("qgate_team_coverage.csv", index=False, encoding='utf-8')
    stats_df_filtered.to_csv("qgate_phase_statistics.csv", index=False, encoding='utf-8')
    summary_df.to_csv("qgate_team_group_summary.csv", index=False, encoding='utf-8')
    
    print(f"✅ CSV数据已生成:")
    print(f"   - qgate_team_coverage.csv")
    print(f"   - qgate_phase_statistics.csv")
    print(f"   - qgate_team_group_summary.csv")
    
    print("="*80)

if __name__ == "__main__":
    main()
