import json
import pandas as pd
from datetime import timedelta, datetime
import glob
import os
import plotly.graph_objects as go
import dash
# Import Input, Output for callbacks
from dash import dcc, html, Input, Output, State, dash_table
import numpy as np # Import numpy for potential NaN handling
import pickle # 用于序列化缓存数据
import hashlib # 用于生成缓存键
import time # 用于测量性能

try:
    # Ensure 'aidas' column is loaded if available
    from data_processor import load_defect_data, apply_chart_style, extract_english
except ImportError:
    print("警告：无法导入 data_processor 模块。请确保 data_processor.py 在PYTHONPATH中。")
    def load_defect_data(pattern): return pd.DataFrame()
    def apply_chart_style(fig, title, x_title, y_title, height): return fig

def calculate_defect_metrics(history_file_path):
    """
    计算缺陷的指标：各阶段耗时、ECU变更最大值、Solution Cluster PingPong次数。
    增强版本：按周计算历史变化并存储

    Args:
        history_file_path (str): 缺陷历史 JSON 文件的路径。

    Returns:
        dict: 包含指标的字典:
            {
                'phase_times': pd.Series, # 各阶段耗时
                'max_ecu_changes': int,   # ecu_no_of_changes_udf 的最大值
                'solution_cluster_pings': int, # solution_cluster_udf 的变更次数
                'processed_df': pd.DataFrame # 处理后的变更记录 (可选)
                'weekly_metrics': dict # 按周计算的指标变化历史
            }
            如果数据不足或出错则返回包含默认值的字典。
    """
    default_return = {
        'phase_times': pd.Series(dtype='timedelta64[ns]'),
        'max_ecu_changes': 0,
        'solution_cluster_pings': 0,
        'processed_df': pd.DataFrame(),
        'weekly_metrics': {}
    }
    try:
        with open(history_file_path, 'r', encoding='utf-8') as f:
            history_data = json.load(f)
    except FileNotFoundError:
        return default_return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {history_file_path}")
        return default_return
    except Exception as e:
        print(f"An unexpected error occurred processing {history_file_path}: {e}")
        return default_return

    if not history_data or 'data' not in history_data or not history_data['data']:
        return default_return

    processed_changes = []
    max_ecu_val = 0
    # 追踪字段值的变化
    field_values = {
        'phase': [],
        'solution_cluster_udf': [],
        'ecu_no_of_changes_udf': []
    }
    
    # 按周追踪的指标
    weekly_metrics = {}

    # 逆序迭代历史记录（通常最新在前），或者正序迭代后排序
    history_entries = sorted(history_data['data'], key=lambda x: x.get('timestamp', ''))

    for entry in history_entries: # 确保按时间顺序处理
        timestamp_str = entry.get('timestamp')
        if not timestamp_str: continue
        try:
            timestamp = pd.to_datetime(timestamp_str)
            # 计算周号，格式为 YYYY-WXX
            week_str = timestamp.strftime('%G-W%V')
        except (ValueError, TypeError):
            continue

        change_set = entry.get('change_set', [])
        action = entry.get('action')

        current_entry_changes = {} # 存储此时间戳的字段值

        # 处理创建事件
        if action == 'create':
            for change in change_set:
                field_name = change.get('field_name')
                value = change.get('valueName') or change.get('value_text') or change.get('value') # 尝试获取各种值
                if field_name in field_values:
                    current_entry_changes[field_name] = value
                    processed_changes.append({ # 也记录到 processed_changes 供后续使用
                         'timestamp': timestamp,
                         'field_name': field_name,
                         'value': value,
                         'action': 'create',
                         'week': week_str
                     })

        # 处理更新事件
        elif action == 'update':
            for change in change_set:
                field_name = change.get('field_name')
                if field_name in field_values:
                    value = change.get('valueName') or change.get('value_text') or change.get('value')
                    if value is not None: # 仅当有值时记录
                        current_entry_changes[field_name] = value
                        processed_changes.append({
                             'timestamp': timestamp,
                             'field_name': field_name,
                             'value': value,
                             'action': 'update',
                             'week': week_str
                         })

        # 更新追踪列表和最大 ECU 值
        for field, value in current_entry_changes.items():
            field_values[field].append({'timestamp': timestamp, 'value': value, 'week': week_str})
            if field == 'ecu_no_of_changes_udf':
                try:
                    # 尝试将值转为数字，忽略无法转换的
                    numeric_value = pd.to_numeric(value, errors='coerce')
                    if pd.notna(numeric_value):
                        max_ecu_val = max(max_ecu_val, int(numeric_value))
                        
                        # 更新周度指标
                        if week_str not in weekly_metrics:
                            weekly_metrics[week_str] = {'max_ecu_changes': 0, 'solution_cluster_pings': 0}
                        weekly_metrics[week_str]['max_ecu_changes'] = int(numeric_value)
                except (ValueError, TypeError):
                    pass # 忽略无法转换为数字的值

    if not processed_changes:
        return default_return

    # --- 计算 Solution Cluster PingPong ---
    solution_cluster_changes = sorted([
        item for item in field_values['solution_cluster_udf']
        if item.get('value') is not None # 过滤掉 None 值
    ], key=lambda x: x['timestamp'])

    # 周度 Ping-Pong 计算 (不重置计数，保持累计)
    current_pings = 0
    last_value = None
    
    for change in solution_cluster_changes:
        current_value = change['value']
        week_str = change['week']
        
        if last_value is not None and current_value != last_value:
            current_pings += 1
            
            # 更新周度指标
            if week_str not in weekly_metrics:
                weekly_metrics[week_str] = {'max_ecu_changes': 0, 'solution_cluster_pings': 0}
            weekly_metrics[week_str]['solution_cluster_pings'] = current_pings
            
        last_value = current_value

    solution_cluster_pings = current_pings
    
    # 确保每周的指标都是当周之前的累积值
    sorted_weeks = sorted(weekly_metrics.keys())
    for i in range(1, len(sorted_weeks)):
        prev_week = sorted_weeks[i-1]
        curr_week = sorted_weeks[i]
        
        # ECU变更取最大值
        weekly_metrics[curr_week]['max_ecu_changes'] = max(
            weekly_metrics[curr_week]['max_ecu_changes'],
            weekly_metrics[prev_week]['max_ecu_changes']
        )
        
        # Ping-Pong确保是递增的
        if weekly_metrics[curr_week]['solution_cluster_pings'] < weekly_metrics[prev_week]['solution_cluster_pings']:
            weekly_metrics[curr_week]['solution_cluster_pings'] = weekly_metrics[prev_week]['solution_cluster_pings']

    # --- 计算 Phase Durations (逻辑保持不变，但基于 processed_changes) ---
    df_processed = pd.DataFrame(processed_changes)
    if df_processed.empty:
         # 如果没有处理任何变更，返回默认值
         return {
            'phase_times': pd.Series(dtype='timedelta64[ns]'),
            'max_ecu_changes': max_ecu_val, # 仍然返回计算出的 max_ecu
            'solution_cluster_pings': solution_cluster_pings, # 和 pings
            'processed_df': pd.DataFrame(),
            'weekly_metrics': weekly_metrics
         }

    df_processed = df_processed.sort_values(by='timestamp').reset_index(drop=True)
    # 保留相同时间戳和字段的最后一个更改 (如果需要)
    # df_processed = df_processed.drop_duplicates(subset=['timestamp', 'field_name'], keep='last')

    phase_df = df_processed[df_processed['field_name'] == 'phase'].copy()
    phase_durations = pd.Series(dtype='timedelta64[ns]')

    if not phase_df.empty:
        # 确保按时间排序
        phase_df = phase_df.sort_values(by='timestamp')
        # 移除连续相同的值，只保留状态变化的时刻
        phase_df = phase_df.loc[phase_df['value'].shift() != phase_df['value']]

        if not phase_df.empty:
            phase_df['next_timestamp'] = phase_df['timestamp'].shift(-1)
            # 使用整个历史记录的最后一个时间戳作为最后一个阶段的结束时间
            last_overall_timestamp = df_processed['timestamp'].iloc[-1]
            phase_df['next_timestamp'] = phase_df['next_timestamp'].fillna(last_overall_timestamp)
            # 确保 next_timestamp 不早于 timestamp
            phase_df['next_timestamp'] = phase_df[['timestamp', 'next_timestamp']].max(axis=1)

            phase_df['duration'] = phase_df['next_timestamp'] - phase_df['timestamp']
            phase_df['duration'] = pd.to_timedelta(phase_df['duration'])
            # 过滤掉可能的负持续时间（虽然理论上不应发生）
            phase_df = phase_df[phase_df['duration'] >= pd.Timedelta(0)]
            phase_durations = phase_df.groupby('value')['duration'].sum()


    return {
        'phase_times': phase_durations if not phase_durations.empty else pd.Series(dtype='timedelta64[ns]'),
        'max_ecu_changes': int(max_ecu_val), # 确保是整数
        'solution_cluster_pings': solution_cluster_pings,
        'processed_df': df_processed, # 返回处理后的 DataFrame
        'weekly_metrics': weekly_metrics # 返回按周计算的指标
    }

def calculate_complexity(max_ecu_changes, solution_cluster_pings, weight_ecu=2, weight_pingpong=1):
    """
    根据 ECU 变更最大值和 Solution Cluster PingPong 次数计算加权复杂度得分。
    """
    # 确保输入是数值
    max_ecu_changes = pd.to_numeric(max_ecu_changes, errors='coerce')
    solution_cluster_pings = pd.to_numeric(solution_cluster_pings, errors='coerce')

    max_ecu_changes = max_ecu_changes if pd.notna(max_ecu_changes) else 0
    solution_cluster_pings = solution_cluster_pings if pd.notna(solution_cluster_pings) else 0

    score = weight_ecu * max_ecu_changes + weight_pingpong * solution_cluster_pings
    return score

def categorize_complexity(score):
    """
    根据复杂度得分进行分类。
    阈值可以根据数据分布调整。
    """
    if score <= 1:
        return '简单'
    elif score <= 4:
        return '中等'
    else:
        return '复杂'


# 修改 create_complexity_trend_figure_and_data
def create_complexity_trend_figure_and_data(defect_data_pattern="defect/2025*.json", history_folder="history", use_cache=True, cache_dir="cache"):
    """
    加载缺陷数据，计算基于历史的复杂度指标，并生成趋势图和完整数据。
    增强版：按周追踪缺陷的复杂度变化
    
    Args:
        defect_data_pattern (str): 缺陷数据文件的glob模式
        history_folder (str): 历史数据文件夹路径
        use_cache (bool): 是否使用缓存加速计算
        cache_dir (str): 缓存目录
    
    Returns:
        tuple: (plotly.graph_objects.Figure or None, pd.DataFrame or None)
               生成的图表对象和包含所有计算细节的 DataFrame。
               如果数据加载或处理失败则返回 (None, None)。
    """
    start_time = time.time()
    print("开始加载缺陷数据...")
    ddf = load_defect_data(defect_data_pattern)
    if ddf.empty:
        print(f"未能根据模式 '{defect_data_pattern}' 加载缺陷数据或数据为空。")
        return None, None

    print(f"成功加载 {len(ddf)} 条缺陷记录。")

    # 创建缓存目录（如果不存在）
    if use_cache and not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    
    # 检查缓存
    cache_valid = False
    cache_key = None
    if use_cache:
        # 使用固定的缓存键，不依赖文件修改时间
        cache_key = "defect_trend_fixed_cache"
        cache_file = os.path.join(cache_dir, f"trend_data_{cache_key}.pkl")
        
        # 检查缓存是否存在
        if os.path.exists(cache_file):
            print(f"发现缓存文件，尝试加载...")
            try:
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                    # 验证缓存的数据结构
                    if isinstance(cached_data, tuple) and len(cached_data) == 2:
                        cached_fig, cached_ddf = cached_data
                        if cached_ddf is not None and isinstance(cached_ddf, pd.DataFrame) and len(cached_ddf) > 0:
                            print(f"成功从缓存加载数据，节省了计算时间！")
                            end_time = time.time()
                            print(f"总处理时间: {end_time - start_time:.2f} 秒")
                            return cached_fig, cached_ddf
            except Exception as e:
                print(f"加载缓存失败: {e}，将重新计算数据。")

    # --- 时间和 ID 列检查 ---
    if 'creation_time' not in ddf.columns:
        print("错误：'creation_time' 列不存在。")
        return None, None
    if not pd.api.types.is_datetime64_any_dtype(ddf['creation_time']):
        try:
            ddf['creation_time'] = pd.to_datetime(ddf['creation_time'])
            print("已尝试将 'creation_time' 转换为 datetime 类型。")
        except Exception as e:
            print(f"转换 'creation_time' 失败: {e}")
            return None, None
    if 'id' not in ddf.columns:
        print("错误：缺陷数据中缺少 'id' 列。")
        return None, None

    # --- 筛选日期 ---
    start_date = pd.Timestamp("2025-01-01")
    ddf = ddf[ddf['creation_time'] >= start_date].copy()
    if ddf.empty:
        print("没有找到 2025年1月1日至今的缺陷数据。")
        return None, None
    print(f"筛选后剩余 {len(ddf)} 条 2025年至今的缺陷记录。")

    # --- 计算 Max ECU 和 Ping-Pong (基于历史) ---
    print("开始基于历史计算 Max ECU 和 Solution Cluster Ping-Pong 次数...")
    metrics_data = {} # 使用字典存储结果 {defect_id: {'max_ecu': val, 'pings': val}}
    weekly_data = {} # 存储周度指标数据 {defect_id: {'weekly_metrics': {...}}}
    weekly_status = {} # 存储每个缺陷每周的状态 {defect_id: {'weekly_status': {week: status}}}
    weekly_complexity = {} # 存储每个缺陷每周的复杂度 {defect_id: {'weekly_complexity': {week: category}}}
    processed_count = 0
    total_defects = len(ddf)
    
    # 定义结束状态
    concluded_statuses = ['09-Concluded without action', '06-Concluded']
    
    # 使用缓存加速每个缺陷的历史计算
    defect_metrics_cache = {}
    if use_cache:
        defect_cache_file = os.path.join(cache_dir, f"defect_metrics_{cache_key}.pkl")
        if os.path.exists(defect_cache_file):
            try:
                with open(defect_cache_file, 'rb') as f:
                    defect_metrics_cache = pickle.load(f)
                print(f"已加载 {len(defect_metrics_cache)} 条缺陷历史计算缓存。")
            except Exception as e:
                print(f"加载缺陷历史缓存失败: {e}")
                defect_metrics_cache = {}
    
    for index, row in ddf.iterrows():
        defect_id = row['id']
        history_file = os.path.join(history_folder, f"{defect_id}_history.json")
        
        # 检查是否有缓存的结果
        if use_cache and defect_id in defect_metrics_cache:
            metrics = defect_metrics_cache[defect_id]
        elif os.path.exists(history_file):
            # 如果没有缓存或缓存无效，则计算
            metrics = calculate_defect_metrics(history_file)
            # 保存到内存缓存
            if use_cache:
                defect_metrics_cache[defect_id] = metrics
        else:
            metrics = {
                'max_ecu_changes': 0,
                'solution_cluster_pings': 0,
                'weekly_metrics': {},
                'processed_df': pd.DataFrame(),
                'phase_times': pd.Series(dtype='timedelta64[ns]')
            }
        
        metrics_data[defect_id] = {
            'max_ecu_changes': metrics['max_ecu_changes'],
            'solution_cluster_pings': metrics['solution_cluster_pings']
        }
        weekly_data[defect_id] = {
            'weekly_metrics': metrics['weekly_metrics']
        }
        
        # 分析历史记录中的状态变化
        status_history = {}
        phase_changes = metrics['processed_df'][metrics['processed_df']['field_name'] == 'phase'].copy()
        if not phase_changes.empty:
            for _, change in phase_changes.iterrows():
                week_str = change['week']
                status_value = change['value']
                if isinstance(status_value, dict) and 'name' in status_value:
                    status_value = status_value['name']
                status_history[week_str] = status_value
            
            # 填充每周的状态（如果某周没有状态变化，使用上一周的状态）
            all_weeks = sorted(set(week for week in metrics['weekly_metrics'].keys()))
            if all_weeks:
                current_status = None
                weekly_status[defect_id] = {}
                
                for week in all_weeks:
                    if week in status_history:
                        current_status = status_history[week]
                    if current_status is not None:
                        weekly_status[defect_id][week] = current_status
        
        # 计算每周的复杂度
        weekly_complexity[defect_id] = {}
        weekly_metrics = metrics['weekly_metrics']
        
        for week, week_metrics in weekly_metrics.items():
            ecu = week_metrics.get('max_ecu_changes', 0)
            pings = week_metrics.get('solution_cluster_pings', 0)
            score = calculate_complexity(ecu, pings)
            category = categorize_complexity(score)
            weekly_complexity[defect_id][week] = {
                'score': score,
                'category': category,
                'ecu': ecu,
                'pings': pings
            }
        
        processed_count += 1
        if processed_count % 200 == 0 or processed_count == total_defects:
             print(f"  已处理 {processed_count}/{total_defects} 个缺陷的历史记录...")

    # 将计算结果合并回主 DataFrame
    metrics_df = pd.DataFrame.from_dict(metrics_data, orient='index')
    ddf = ddf.join(metrics_df, on='id')
    
    # 将周度数据存储到DataFrame中
    ddf['weekly_metrics'] = ddf['id'].map(lambda id: weekly_data.get(id, {}).get('weekly_metrics', {}))
    ddf['weekly_status'] = ddf['id'].map(lambda id: weekly_status.get(id, {}))
    ddf['weekly_complexity'] = ddf['id'].map(lambda id: weekly_complexity.get(id, {}))
    
    # 填充可能因 join 失败产生的 NaN (虽然理论上不应发生)
    ddf['max_ecu_changes'] = ddf['max_ecu_changes'].fillna(0).astype(int)
    ddf['solution_cluster_pings'] = ddf['solution_cluster_pings'].fillna(0).astype(int)

    print("Max ECU 和 Ping-Pong 次数计算完成。")

    # --- 计算和分类复杂度 (使用新指标) ---
    print("开始计算和分类复杂度...")
    ddf['complexity_score'] = ddf.apply(
        lambda row: calculate_complexity(row['max_ecu_changes'], row['solution_cluster_pings']),
        axis=1
    )
    ddf['complexity_category'] = ddf['complexity_score'].apply(categorize_complexity)
    print("复杂度计算和分类完成。")

    # 如果使用缓存，保存计算结果
    if use_cache and cache_key:
        # 保存单个缺陷的历史计算结果
        defect_cache_file = os.path.join(cache_dir, f"defect_metrics_{cache_key}.pkl")
        try:
            with open(defect_cache_file, 'wb') as f:
                pickle.dump(defect_metrics_cache, f)
            print(f"已缓存 {len(defect_metrics_cache)} 条缺陷的历史计算结果。")
        except Exception as e:
            print(f"保存缺陷历史缓存失败: {e}")

    # --- 准备绘图数据 ---
    print("开始聚合数据并准备主图表...")
    ddf['creation_week'] = ddf['creation_time'].dt.strftime('%G-W%V')
    # 确保 'aidas' 列存在且是列表
    if 'aidas' not in ddf.columns:
        print("警告: 'aidas' 列未在 load_defect_data 中生成。AIDA 分布图将不可用。")
        ddf['aidas'] = [[] for _ in range(len(ddf))] # 创建空列表列
    else:
        ddf['aidas'] = ddf['aidas'].apply(lambda x: x if isinstance(x, list) else [])

    # --- 按周计算开着的缺陷数量 ---
    # 获取所有周
    all_weeks = sorted(set(week for defect_id in weekly_status for week in weekly_status[defect_id].keys()))
    if not all_weeks:
        print("警告: 没有找到周数据。")
        return None, None
    
    # 创建周度开放缺陷计数的数据结构
    open_defects_by_week = {week: {'简单': 0, '中等': 0, '复杂': 0} for week in all_weeks}
    
    # 对每个缺陷，检查每周是否处于开放状态，并按当周的复杂度分类计数
    for _, row in ddf.iterrows():
        defect_id = row['id']
        defect_status = weekly_status.get(defect_id, {})
        defect_complexity = weekly_complexity.get(defect_id, {})
        
        # 确定缺陷创建的周
        creation_week = row['creation_week']
        
        # 从缺陷创建周开始，遍历所有周
        for week in [w for w in all_weeks if w >= creation_week]:
            # 检查该周的状态
            is_open = True
            
            # 如果该周或之前的周有状态记录
            weeks_before = [w for w in defect_status.keys() if w <= week]
            if weeks_before:
                latest_week = max(weeks_before)
                latest_status = defect_status[latest_week]
                is_open = latest_status not in concluded_statuses
            
            if is_open:
                # 使用该周的复杂度进行计数（如果该周有复杂度记录）
                if week in defect_complexity:
                    complexity_category = defect_complexity[week]['category']
                else:
                    # 找到最近的一个有复杂度记录的周
                    complexity_weeks = [w for w in defect_complexity.keys() if w <= week]
                    if complexity_weeks:
                        latest_complexity_week = max(complexity_weeks)
                        complexity_category = defect_complexity[latest_complexity_week]['category']
                    else:
                        # 如果没有复杂度记录，使用"简单"作为默认值
                        complexity_category = '简单'
                
                open_defects_by_week[week][complexity_category] += 1
    
    # 转换为DataFrame以便绘图
    open_defects_df = pd.DataFrame.from_dict(open_defects_by_week, orient='index')
    open_defects_df = open_defects_df.reset_index().rename(columns={'index': 'week'})
    open_defects_df = open_defects_df.sort_values('week')
    
    # --- 创建主图表 ---
    fig = go.Figure()
    colors = {'简单': '#2ca02c', '中等': '#ff7f0e', '复杂': '#d62728'}
    for category in ['简单', '中等', '复杂']:
         fig.add_trace(go.Scatter(
             x=open_defects_df['week'],
             y=open_defects_df[category],
             mode='lines+markers',
             name=category,
             line=dict(color=colors.get(category, 'grey')),
             marker=dict(size=6),
             customdata=[category] * len(open_defects_df),
             hovertemplate=f'<b>周</b>: %{{x}}<br><b>类别</b>: {category}<br><b>开放缺陷数</b>: %{{y}}<extra></extra>'
         ))

    fig = apply_chart_style(
        fig,
        title="缺陷复杂度趋势 (按周统计开放缺陷的当周复杂度)", # 更新标题
        x_title="周 (年-ISO周号)",
        y_title="开放缺陷数量",
        height=500
    )
    fig.update_layout(xaxis_tickangle=-60, hovermode='x unified')

    print("主图表对象生成完成。")
    
    # 如果使用缓存，保存整体计算结果
    if use_cache and cache_key:
        cache_file = os.path.join(cache_dir, f"trend_data_{cache_key}.pkl")
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump((fig, ddf), f)
            print(f"已缓存完整计算结果和图表数据。")
        except Exception as e:
            print(f"保存完整缓存失败: {e}")
    
    # 计算总处理时间
    end_time = time.time()
    print(f"总处理时间: {end_time - start_time:.2f} 秒")
    
    # 返回图表和完整数据
    return fig, ddf

# ===== Dash 应用设置 =====
app = dash.Dash(__name__)
app.title = "缺陷复杂度趋势 Dashboard"

# --- 全局数据加载 ---
print("--- 开始生成主图表和加载数据 ---")
# 调用更新后的函数，默认使用缓存
main_fig, all_defect_data = create_complexity_trend_figure_and_data(use_cache=True, cache_dir="cache")

# --- 应用布局 ---
app.layout = html.Div(children=[
    html.H1(children='缺陷复杂度趋势 Dashboard'),
    html.Div(children='''
        展示自2025年1月1日起，按周统计的不同复杂度（基于历史最大ECU和Solution Cluster变更次数）缺陷数量趋势。悬停可查看对应类别详情，点击可查看该周所有类别缺陷。
    '''), # 更新描述

    dcc.Graph(
        id='complexity-trend-graph',
        figure=main_fig if main_fig else go.Figure().update_layout(title_text="无法加载主图表数据")
    ),

    html.Hr(),
    
    # 添加选项卡组件 - 修改为不使用disabled属性
    dcc.Tabs(id='detail-tabs', value='简单', children=[
        dcc.Tab(label='简单', value='简单'),
        dcc.Tab(label='中等', value='中等'),
        dcc.Tab(label='复杂', value='复杂'),
        dcc.Tab(label='全部', value='全部') # 移除disabled属性
    ]),

    html.Div(id='hover-details-output', children=[
        html.H4("缺陷详细信息", style={'fontWeight': 'bold', 'fontSize': '1.2em'}),
        html.P("将鼠标悬停或点击上方图表以查看详细信息。")
    ]),

    dcc.Graph(id='aida-distribution-graph'),
    
    # 存储当前选中的周数据
    dcc.Store(id='selected-week-data'),
    
    # 存储选项卡状态
    dcc.Store(id='tab-state', data={'is_click': False})
])

# ===== Callback 函数 =====
@app.callback(
    Output('selected-week-data', 'data'),
    Output('detail-tabs', 'value'),
    Output('tab-state', 'data'),
    Input('complexity-trend-graph', 'hoverData'),
    Input('complexity-trend-graph', 'clickData')
)
def update_selected_data(hoverData, clickData):
    ctx = dash.callback_context
    if not ctx.triggered:
        # 没有触发，返回默认值
        return None, '简单', {'is_click': False}
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'complexity-trend-graph':
        # 确定是点击还是悬停
        is_click = 'clickData' in ctx.triggered[0]['prop_id']
        data_point = clickData if is_click else hoverData
        
        if data_point is None:
            return None, '简单', {'is_click': False}
            
        point = data_point['points'][0]
        hover_week = point['x']
        categories = ['简单', '中等', '复杂']
        selected_category = categories[point['curveNumber']]
        
        # 构建要存储的数据
        stored_data = {
            'week': hover_week,
            'category': selected_category,
            'is_click': is_click
        }
        
        # 如果是点击，选中"全部"选项卡，否则选中当前类别
        if is_click:
            return stored_data, '全部', {'is_click': True}
        else:
            return stored_data, selected_category, {'is_click': False}
    
    return None, '简单', {'is_click': False}

# 添加新的回调函数处理选项卡点击
@app.callback(
    Output('detail-tabs', 'value', allow_duplicate=True),
    Input('detail-tabs', 'value'),
    State('tab-state', 'data'),
    prevent_initial_call=True
)
def handle_tab_click(tab_value, tab_state):
    # 如果是点击图表后的"全部"选项卡，允许切换到其他选项卡
    # 或者是普通悬停模式下的选项卡切换
    return tab_value

@app.callback(
    Output('hover-details-output', 'children'),
    Output('aida-distribution-graph', 'figure'),
    Input('selected-week-data', 'data'),
    Input('detail-tabs', 'value')
)
def update_hover_details(selected_data, selected_tab):
    if selected_data is None or all_defect_data is None or all_defect_data.empty:
        default_title = html.H4("缺陷详细信息", style={'fontWeight': 'bold', 'fontSize': '1.2em'})
        default_text = html.P("将鼠标悬停或点击上方图表以查看详细信息。")
        empty_fig = go.Figure().update_layout(
            title=dict(text="AIDA 分布 (无数据)", font=dict(size=16, family="Arial, sans-serif")),
            xaxis={'visible': False},
            yaxis={'visible': False},
            annotations=[{"text": "无悬停/点击数据", "xref": "paper", "yref": "paper", "showarrow": False, "font": {"size": 16}}]
        )
        return [default_title, default_text], empty_fig

    try:
        hover_week = selected_data['week']
        is_click = selected_data.get('is_click', False)
        
        # 获取当前周和上一周
        all_weeks = [week for defect in all_defect_data['weekly_metrics'] for week in defect.keys()]
        weeks_list = sorted(set(all_weeks)) if all_weeks else []
        if not weeks_list:
            weeks_list = sorted(set(all_defect_data['creation_week'].tolist())) if 'creation_week' in all_defect_data.columns else []
        
        try:
            current_week_idx = weeks_list.index(hover_week)
            prev_week = weeks_list[current_week_idx - 1] if current_week_idx > 0 else None
        except (ValueError, IndexError):
            prev_week = None
        
        # 定义结束状态
        concluded_statuses = ['09-Concluded without action', '06-Concluded']
        
        # 收集所选周的开放缺陷及其当周复杂度
        open_defects_data = []
        for _, row in all_defect_data.iterrows():
            defect_id = row['id']
            creation_week = row['creation_week']
            
            # 如果创建时间晚于当前选择的周，则跳过
            if creation_week > hover_week:
                continue
            
            # 检查该缺陷在所选周是否处于开放状态
            weekly_status = row.get('weekly_status', {})
            is_open = True
            
            # 找到该缺陷截至所选周的最新状态
            weeks_before = [w for w in weekly_status.keys() if w <= hover_week]
            if weeks_before:
                latest_week = max(weeks_before)
                latest_status = weekly_status[latest_week]
                is_open = latest_status not in concluded_statuses
                current_phase = latest_status
            else:
                current_phase = "Unknown"
            
            if not is_open:
                continue
                
            # 获取该缺陷在所选周的复杂度
            weekly_complexity = row.get('weekly_complexity', {})
            complexity_data = {}
            
            # 如果该周有复杂度记录
            if hover_week in weekly_complexity:
                complexity_data = weekly_complexity[hover_week]
            else:
                # 找到最近的一个有复杂度记录的周
                complexity_weeks = [w for w in weekly_complexity.keys() if w <= hover_week]
                if complexity_weeks:
                    latest_complexity_week = max(complexity_weeks)
                    complexity_data = weekly_complexity[latest_complexity_week]
            
            current_category = complexity_data.get('category', '简单')
            current_score = complexity_data.get('score', 0)
            current_ecu = complexity_data.get('ecu', 0)
            current_pings = complexity_data.get('pings', 0)
            
            # 如果按选项卡筛选
            if selected_tab != '全部' and current_category != selected_tab:
                continue
                
            # 收集开放缺陷数据
            defect_detail = {
                'id': defect_id,
                'name': row.get('name', ''),
                'detected_by': row.get('detected_by', {}),
                'current_phase': current_phase,
                'matrix': row.get('matrix', ''),
                'current_ecu': current_ecu,
                'current_pings': current_pings,
                'current_score': current_score,
                'current_category': current_category,
                'creation_week': creation_week,
                'aidas': row.get('aidas', [])
            }
            
            # 检查指标变化
            if prev_week:
                # 获取上一周的复杂度数据
                prev_complexity_data = {}
                if prev_week in weekly_complexity:
                    prev_complexity_data = weekly_complexity[prev_week]
                else:
                    # 找到上一周之前最近的一个有复杂度记录的周
                    prev_complexity_weeks = [w for w in weekly_complexity.keys() if w <= prev_week]
                    if prev_complexity_weeks:
                        latest_prev_week = max(prev_complexity_weeks)
                        prev_complexity_data = weekly_complexity[latest_prev_week]
                
                prev_ecu = prev_complexity_data.get('ecu', 0)
                prev_pings = prev_complexity_data.get('pings', 0)
                
                # 计算变化
                ecu_increased = current_ecu > prev_ecu and prev_ecu > 0
                ping_increased = current_pings > prev_pings and prev_pings > 0
                
                defect_detail['has_increase'] = ecu_increased or ping_increased
                
                changes = []
                if ecu_increased:
                    changes.append(f"ECU: {prev_ecu}→{current_ecu}")
                if ping_increased:
                    changes.append(f"Ping: {prev_pings}→{current_pings}")
                
                defect_detail['change_text'] = ', '.join(changes)
            else:
                defect_detail['has_increase'] = False
                defect_detail['change_text'] = ''
            
            open_defects_data.append(defect_detail)
        
        # 转换为DataFrame
        if not open_defects_data:
            # 如果没有符合条件的缺陷
            no_data_title = html.H4(f"详细信息: {hover_week} - {selected_tab}", 
                                style={'fontWeight': 'bold', 'fontSize': '1.2em'})
            no_data_text = html.P("该选择没有对应的缺陷数据。")
            empty_fig = go.Figure().update_layout(
                title=dict(text=f"AIDA 分布: {hover_week} - {selected_tab} (无数据)", 
                        font=dict(size=16, family="Arial, sans-serif")),
                xaxis={'visible': False},
                yaxis={'visible': False},
                annotations=[{"text": "无数据", "xref": "paper", "yref": "paper", 
                            "showarrow": False, "font": {"size": 16}}]
            )
            return [no_data_title, no_data_text], empty_fig
        
        filtered_df = pd.DataFrame(open_defects_data)
        
        # --- 生成 DataTable ---
        data_for_table = []
        
        for _, row in filtered_df.iterrows():
            record = {
                'ID': row['id'],
                'Name': (str(row['name'])[:47] + '...') if isinstance(row['name'], str) and len(row['name']) > 50 else str(row['name']),
                'Phase': row['current_phase'],
                'Matrix': row['matrix'],
                'MaxECU': row['current_ecu'],
                'SCPing': row['current_pings'],
                'Score': row['current_score'],
                'Category': row['current_category'],
                '变更': row['change_text'],
                '_has_increase': row['has_increase']
            }
            
            # 处理 detected_by
            detected_by = row['detected_by']
            if isinstance(detected_by, dict) and 'full_name' in detected_by:
                record['Finder'] = detected_by['full_name']
            elif isinstance(detected_by, str):
                record['Finder'] = detected_by
            else:
                record['Finder'] = 'N/A'
            
            data_for_table.append(record)

        # 定义 DataTable 的列
        columns_for_table = [
            {"name": "ID", "id": "ID"},
            {"name": "Name", "id": "Name", "type": "text"},
            {"name": "Finder", "id": "Finder"},
            {"name": "Phase", "id": "Phase"},
            {"name": "Matrix", "id": "Matrix"},
            {"name": "MaxECU", "id": "MaxECU", "type": "numeric"},
            {"name": "SCPing", "id": "SCPing", "type": "numeric"},
            {"name": "Score", "id": "Score", "type": "numeric"},
            {"name": "当周类别", "id": "Category"},
            {"name": "本周变化", "id": "变更"},
        ]

        # 创建 DataTable 组件
        details_table = dash_table.DataTable(
            columns=columns_for_table,
            data=data_for_table,
            style_cell={'textAlign': 'left', 'padding': '5px', 'whiteSpace': 'normal', 'height': 'auto', 'fontSize': '13px'},
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_data={
                'backgroundColor': 'rgb(248, 248, 248)',
                'border': '1px solid grey'
            },
            style_data_conditional=[
                # 斑马条纹条件
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(255, 255, 255)',
                },
                # 指标有变化的行使用黄色背景
                {
                    'if': {'filter_query': '{_has_increase} = true'},
                    'backgroundColor': 'rgba(255, 235, 153, 0.7)',
                    'fontWeight': 'bold'
                }
            ],
            page_size=10,
            sort_action="native",
            filter_action="native",
            style_table={'overflowX': 'auto'}
        )

        # --- 计算有多少缺陷指标上升 ---
        increased_defects_count = filtered_df['has_increase'].sum()
        
        # 组合标题和 DataTable
        display_text = f"{hover_week} - {selected_tab}" if selected_tab != '全部' else f"{hover_week} - 所有类别"
        
        title_text = f"详细信息: {display_text} ({len(filtered_df)} 个缺陷)"
        if increased_defects_count > 0:
            title_text += f" 🔺{increased_defects_count}个指标上升"
            
        details_output_children = [
            html.H4(title_text, style={'fontWeight': 'bold', 'fontSize': '1.2em'}),
            html.P("每行显示的是缺陷在当周的状态和复杂度指标。🔺表示相比上周指标有所上升的缺陷", 
                  style={'fontSize': '0.9em', 'color': 'grey'}) if increased_defects_count > 0 else 
            html.P("每行显示的是缺陷在当周的状态和复杂度指标。", style={'fontSize': '0.9em', 'color': 'grey'}),
            details_table
        ]

        # --- 生成 AIDA 分布图 ---
        aida_fig = go.Figure()
        aida_title = f"AIDA 分布: {display_text}" # 先定义标题文本
        if 'aidas' in filtered_df.columns and not filtered_df['aidas'].isnull().all():
            # 先创建一个包含提取英文后aida的数据框
            try:
                from data_processor import extract_english
                # 应用extract_english到aidas列
                exploded_df = filtered_df[filtered_df['aidas'].apply(lambda x: isinstance(x, list) and len(x) > 0)].explode('aidas')
                exploded_df['aida_english'] = exploded_df['aidas'].apply(extract_english)
            except ImportError:
                # 如果无法导入，使用原始aidas值
                exploded_df = filtered_df[filtered_df['aidas'].apply(lambda x: isinstance(x, list) and len(x) > 0)].explode('aidas')
                exploded_df['aida_english'] = exploded_df['aidas']
                
            if not exploded_df.empty:
                # 如果是全部类别视图，按复杂度类别分组
                if selected_tab == '全部':
                    aida_summary = exploded_df.groupby(['aida_english', 'current_category'])[['current_ecu', 'current_pings']].sum().reset_index()
                    # 按AIDA和复杂度排序
                    aida_summary = aida_summary.sort_values(by=['aida_english', 'current_category'])
                    
                    # 为每个复杂度类别创建一组条形图
                    for category in ['简单', '中等', '复杂']:
                        category_data = aida_summary[aida_summary['current_category'] == category]
                        if not category_data.empty:
                            color = {'简单': '#2ca02c', '中等': '#ff7f0e', '复杂': '#d62728'}[category]
                            aida_fig.add_trace(go.Bar(
                                x=category_data['aida_english'], 
                                y=category_data['current_ecu'], 
                                name=f'{category} - 当前ECU', 
                                marker_color=color,
                                opacity=0.7
                            ))
                else:
                    # 使用aida_english列而不是aidas列
                    aida_summary = exploded_df.groupby('aida_english')[['current_ecu', 'current_pings']].sum().reset_index()
                    aida_summary = aida_summary.sort_values(by=['current_ecu', 'current_pings'], ascending=False)
                    aida_fig.add_trace(go.Bar(x=aida_summary['aida_english'], y=aida_summary['current_ecu'], name='ECU变更 (Sum)', marker_color='indianred'))
                    aida_fig.add_trace(go.Bar(x=aida_summary['aida_english'], y=aida_summary['current_pings'], name='Solution Cluster变更 (Sum)', marker_color='lightsalmon'))
                
                aida_fig.update_layout(
                    barmode='group',
                    # 使用 dict 更新标题以应用样式
                    title=dict(text=aida_title, font=dict(size=16, weight='bold', family="Arial, sans-serif")),
                    xaxis_title="AIDA (English)",
                    yaxis_title="当周指标总和",
                    xaxis_tickangle=-45,
                    height=400,
                    template="plotly_white"
                )
            else:
                aida_title += " (无 AIDA 数据)"
                aida_fig.update_layout(title=dict(text=aida_title, font=dict(size=16, weight='bold', family="Arial, sans-serif")), annotations=[{"text": "无 AIDA 数据", "xref": "paper", "yref": "paper", "showarrow": False, "font": {"size": 16}}])
        else:
            aida_title += " (无 AIDA 数据)"
            aida_fig.update_layout(title=dict(text=aida_title, font=dict(size=16, weight='bold', family="Arial, sans-serif")), annotations=[{"text": "无 AIDA 数据", "xref": "paper", "yref": "paper", "showarrow": False, "font": {"size": 16}}])

        # 返回包含标题和 DataTable 的列表，以及 AIDA 图
        return details_output_children, aida_fig
        
    except Exception as e:
        print(f"Error during hover update: {e}")
        error_title = html.H4("错误", style={'fontWeight': 'bold', 'fontSize': '1.2em', 'color': 'red'})
        error_text = html.P(f"处理数据时发生错误: {e}")
        empty_fig = go.Figure().update_layout(title=dict(text="AIDA 分布 (错误)", font=dict(size=16, weight='bold', family="Arial, sans-serif")), annotations=[{"text": "处理错误", "xref": "paper", "yref": "paper", "showarrow": False, "font": {"size": 16}}])
        return [error_title, error_text], empty_fig

# ===== 启动 Dash 服务器 =====
if __name__ == '__main__':
    # 创建缓存目录（如果不存在）
    cache_dir = "cache"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    # 运行Dash服务器
    app.run(debug=False, host='0.0.0.0', port=8052)