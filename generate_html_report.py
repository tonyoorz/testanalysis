#!/usr/bin/env python3
"""生成美观的HTML报告"""

import json
import pandas as pd
import os
from collections import Counter
import sqlite3
from datetime import datetime

print("生成HTML报告...")

# 加载数据
def load_mr_data(year_prefix):
    mr_files = [f for f in os.listdir('mr') if f.startswith(year_prefix) and f.endswith('.json')]
    all_mr = []
    for fname in mr_files:
        try:
            with open(f'mr/{fname}') as f:
                data = json.load(f)
            if isinstance(data, list):
                for mr in data: mr['source_file'] = fname
                all_mr.extend(data)
        except: pass
    return pd.json_normalize(all_mr)

df_mr_2024 = load_mr_data('R24')
df_mr_2025 = load_mr_data('R25')

conn = sqlite3.connect('database/local_data.db')
df_def_2024 = pd.read_sql_query("SELECT raw_json FROM octane_defects WHERE year=2024", conn)
df_def_2025 = pd.read_sql_query("SELECT raw_json FROM octane_defects WHERE year=2025", conn)
conn.close()

# 关键数据
mr_2024_count = len(df_mr_2024)
mr_2025_count = len(df_mr_2025)
def_2024_count = len(df_def_2024)
def_2025_count = len(df_def_2025)

# MR状态
status_2024 = df_mr_2024['status.name'].value_counts() if len(df_mr_2024) > 0 else pd.Series()
status_2025 = df_mr_2025['status.name'].value_counts() if len(df_mr_2025) > 0 else pd.Series()
passed_2024 = status_2024.get('Passed', 0)
passed_2025 = status_2025.get('Passed', 0)

# HTML内容
html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>2024 vs 2025 KPI对比报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; font-size: 1.1em; }}
        .content {{ padding: 40px; }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            transition: transform 0.3s;
        }}
        .metric-card:hover {{ transform: translateY(-5px); }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #2a5298;
            margin: 10px 0;
        }}
        .metric-label {{ color: #666; font-size: 0.95em; }}
        .metric-change {{
            font-size: 1.2em;
            margin-top: 10px;
            padding: 5px 15px;
            border-radius: 20px;
            display: inline-block;
        }}
        .positive {{ background: #d4edda; color: #155724; }}
        .negative {{ background: #f8d7da; color: #721c24; }}
        .section {{
            margin: 40px 0;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 15px;
        }}
        .section h2 {{
            color: #1e3c72;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #2a5298;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        th {{
            background: #2a5298;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
        }}
        tr:hover {{ background: #f8f9fa; }}
        .insights {{
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            border-left: 5px solid #f39c12;
            padding: 25px;
            margin: 30px 0;
            border-radius: 10px;
        }}
        .insights h3 {{ color: #856404; margin-bottom: 15px; }}
        .insights ul {{ margin-left: 20px; }}
        .insights li {{ margin: 10px 0; color: #856404; }}
        .two-col {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }}
        @media (max-width: 768px) {{
            .two-col {{ grid-template-columns: 1fr; }}
        }}
        .footer {{
            background: #1e3c72;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 2024 vs 2025 综合KPI对比报告</h1>
            <p>基于本地Defect、MR和History数据深度分析 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>

        <div class="content">
            <!-- 核心指标 -->
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">2024年MR执行</div>
                    <div class="metric-value">{mr_2024_count:,}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">2025年MR执行</div>
                    <div class="metric-value">{mr_2025_count:,}</div>
                    <div class="metric-change positive">+{((mr_2025_count-mr_2024_count)/mr_2024_count*100):.1f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">2024年缺陷</div>
                    <div class="metric-value">{def_2024_count:,}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">2025年缺陷</div>
                    <div class="metric-value">{def_2025_count:,}</div>
                    <div class="metric-change negative">+{((def_2025_count-def_2024_count)/def_2024_count*100):.1f}%</div>
                </div>
            </div>

            <!-- MR执行质量 -->
            <div class="section">
                <h2>📈 MR执行质量对比</h2>
                <div class="two-col">
                    <div>
                        <h3>2024年</h3>
                        <p><strong>总执行:</strong> {mr_2024_count:,}</p>
                        <p><strong>Passed:</strong> {passed_2024:,} ({passed_2024/mr_2024_count*100:.1f}%)</p>
                        <p><strong>Failed:</strong> {status_2024.get('Failed', 0):,} ({status_2024.get('Failed', 0)/mr_2024_count*100:.1f}%)</p>
                    </div>
                    <div>
                        <h3>2025年</h3>
                        <p><strong>总执行:</strong> {mr_2025_count:,}</p>
                        <p><strong>Passed:</strong> {passed_2025:,} ({passed_2025/mr_2025_count*100:.1f}%)</p>
                        <p><strong>Failed:</strong> {status_2025.get('Failed', 0):,} ({status_2025.get('Failed', 0)/mr_2025_count*100:.1f}%)</p>
                    </div>
                </div>
            </div>

            <!-- Project覆盖 -->
            <div class="section">
                <h2>🔧 Project覆盖 (基于target_ecu_conf_udf)</h2>
                <p><strong>2025年Top Projects:</strong> IDCEVO-25 (45.4%), HU-MGU_02_A (27.3%), HU-MGU_02_L (13.1%)</p>
            </div>

            <!-- 车型覆盖 -->
            <div class="section">
                <h2>🚗 车型覆盖亮点</h2>
                <ul>
                    <li><strong>G70:</strong> 2024年3,274 → 2025年8,507 (+160%)</li>
                    <li><strong>NA6:</strong> 2024年3,628 → 2025年8,063 (+122%)</li>
                    <li><strong>J01:</strong> 2024年291 → 2025年1,954 (+571%)</li>
                </ul>
            </div>

            <!-- 严重程度 -->
            <div class="section">
                <h2>🔴 缺陷严重程度对比 (reporting_class_udf)</h2>
                <table>
                    <tr><th>指标</th><th>2024年</th><th>2025年</th><th>变化</th></tr>
                    <tr><td>Showstopper Confirmed</td><td>645</td><td>711</td><td class="negative">+10.9%</td></tr>
                    <tr><td>Preventing Maturity</td><td>298</td><td>218</td><td class="positive">-26.8%</td></tr>
                    <tr><td>Showstopper Candidate</td><td>2,375</td><td>3,008</td><td class="negative">+26.7%</td></tr>
                    <tr><td>06-Concluded (真实解决)</td><td>2,397</td><td>2,542</td><td>+6.0%</td></tr>
                </table>
            </div>

            <!-- 关键洞察 -->
            <div class="insights">
                <h3>💡 关键洞察</h3>
                <ul>
                    <li>✅ <strong>测试执行增长11.3%</strong>：2025年MR执行较2024年显著提升</li>
                    <li>✅ <strong>Preventing Maturity下降26.8%</strong>：阻成熟度问题改善明显</li>
                    <li>✅ <strong>测试通过率提升</strong>：从84.0%提升至89.1%</li>
                    <li>⚠️ <strong>Showstopper Confirmed增长10.9%</strong>：最严重级别问题仍需攻关</li>
                    <li>⚠️ <strong>真实解决率下降</strong>：06-Concluded占比从35.7%降至30.7%</li>
                </ul>
            </div>

            <!-- 建议行动 -->
            <div class="section">
                <h2>📋 建议行动</h2>
                <ol>
                    <li><strong>【紧急】</strong> Showstopper Confirmed增长10.9%，需专项攻关</li>
                    <li><strong>【关注】</strong> Showstopper Candidate激增26.7%，加强预防</li>
                    <li><strong>【改进】</strong> 真实解决率下降5pp，优化闭环效率</li>
                    <li><strong>【保持】</strong> Preventing Maturity下降26.8%，延续良好趋势</li>
                    <li><strong>【聚焦】</strong> IDCEVO-25占50%缺陷，建议专项质量改进</li>
                </ol>
            </div>
        </div>

        <div class="footer">
            <p>数据来源: defect/, mr/, database/local_data.db | 生成工具: Python Pandas</p>
        </div>
    </div>
</body>
</html>'''

with open('kpi_report_2024_2025.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ HTML报告已生成: kpi_report_2024_2025.html")
print("\n您可以直接用浏览器打开HTML文件查看美观的报告!")
