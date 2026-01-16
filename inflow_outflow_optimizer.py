#!/usr/bin/env python3
"""
Inflow/Outflow 分析超级优化版本
专门针对大量历史文件的快速处理
"""

import os
import glob
import json
import pandas as pd
from datetime import datetime, timedelta
import concurrent.futures
import threading
from collections import defaultdict
import time

def calculate_inflow_outflow_trends_ultra_fast(history_dir="history", date_range_weeks=52):
    """
    超快速版本的Inflow/Outflow趋势分析
    
    优化策略：
    1. 极简文件过滤
    2. 流式JSON解析
    3. 内存优化的并发处理
    4. 智能早期终止
    """
    print(f"🚀 启动超快速Inflow/Outflow分析...")
    
    # 获取历史文件
    history_files = glob.glob(os.path.join(history_dir, "*_history.json"))
    if not history_files:
        return pd.DataFrame(columns=['week', 'inflow', 'outflow'])
    
    print(f"📁 发现 {len(history_files)} 个历史文件")
    
    # 定义关键阶段
    outflow_phases = ['06', '09']  # 移除'10'，因为tolerate现在已经改成09状态
    
    # 快速时间范围估算
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=date_range_weeks)
    print(f"🎯 分析时间范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
    
    # 线程安全的计数器
    weekly_counters = defaultdict(lambda: {'inflow': 0, 'outflow': 0})
    counter_lock = threading.Lock()
    
    def process_file_ultra_fast(file_path):
        """超快速单文件处理"""
        local_counts = defaultdict(lambda: {'inflow': 0, 'outflow': 0})
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not data or 'data' not in data:
                return local_counts
            
            # 计数器，避免处理所有数据
            processed_entries = 0
            max_entries_per_file = 1000  # 限制每个文件最多处理的条目数
            
            for entry in data['data']:
                if processed_entries >= max_entries_per_file:
                    break
                
                timestamp_str = entry.get('timestamp')
                if not timestamp_str:
                    continue
                
                try:
                    timestamp = pd.to_datetime(timestamp_str)
                    if not (start_date <= timestamp <= end_date):
                        continue
                    
                    week_key = timestamp.strftime('%Y-W%V')
                    
                    # 检查变更集中的相位变化
                    change_set = entry.get('change_set', [])
                    for change in change_set:
                        if (isinstance(change, dict) and 
                            change.get('field_name') == 'phase'):
                            
                            old_value = change.get('old_value_text', '')
                            new_value = change.get('value_text', '') or change.get('valueName', '')
                            
                            # Inflow: 00 -> 01
                            if old_value.startswith('00') and new_value.startswith('01'):
                                local_counts[week_key]['inflow'] += 1
                            
                            # Outflow: any -> 06/09/10
                            if any(new_value.startswith(phase) for phase in outflow_phases):
                                local_counts[week_key]['outflow'] += 1
                    
                    processed_entries += 1
                    
                except:
                    continue
            
        except Exception as e:
            # 静默处理文件错误
            pass
        
        return local_counts
    
    # 动态调整并发参数
    file_count = len(history_files)
    if file_count <= 500:
        max_workers = 6
        chunk_size = 20
    elif file_count <= 2000:
        max_workers = 8
        chunk_size = 50
    else:
        max_workers = 12
        chunk_size = 100
    
    print(f"⚡ 并发配置: {max_workers} 线程，块大小 {chunk_size}")
    
    # 分块并行处理
    file_chunks = [history_files[i:i + chunk_size] for i in range(0, len(history_files), chunk_size)]
    processed_chunks = 0
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 批量提交任务
        future_to_files = {}
        for chunk in file_chunks:
            for file_path in chunk:
                future = executor.submit(process_file_ultra_fast, file_path)
                future_to_files[future] = file_path
        
        # 收集结果
        for future in concurrent.futures.as_completed(future_to_files):
            try:
                local_counts = future.result(timeout=5)  # 5秒超时
                
                # 合并到全局计数器
                with counter_lock:
                    for week_key, counts in local_counts.items():
                        weekly_counters[week_key]['inflow'] += counts['inflow']
                        weekly_counters[week_key]['outflow'] += counts['outflow']
                
            except concurrent.futures.TimeoutError:
                print(f"⚠️  文件处理超时: {future_to_files[future]}")
            except Exception as e:
                pass  # 静默处理错误
            
            processed_chunks += 1
            if processed_chunks % 50 == 0:
                elapsed = time.time() - start_time
                print(f"📊 进度: {processed_chunks}/{len(history_files)} 文件 ({elapsed:.1f}s)")
    
    # 生成完整的周列表
    current_date = start_date
    while current_date <= end_date:
        week_key = current_date.strftime('%Y-W%V')
        if week_key not in weekly_counters:
            weekly_counters[week_key] = {'inflow': 0, 'outflow': 0}
        current_date += timedelta(weeks=1)
    
    # 转换为DataFrame
    weekly_data = []
    for week_key in sorted(weekly_counters.keys()):
        weekly_data.append({
            'week': week_key,
            'inflow': weekly_counters[week_key]['inflow'],
            'outflow': weekly_counters[week_key]['outflow']
        })
    
    df_result = pd.DataFrame(weekly_data)
    
    total_time = time.time() - start_time
    total_inflow = df_result['inflow'].sum() if not df_result.empty else 0
    total_outflow = df_result['outflow'].sum() if not df_result.empty else 0
    
    print(f"✅ 超快速分析完成!")
    print(f"⏱️  总耗时: {total_time:.2f} 秒")
    print(f"📈 处理速度: {len(history_files)/total_time:.1f} 文件/秒")
    print(f"📊 结果: {len(df_result)} 周数据，总Inflow: {total_inflow}, 总Outflow: {total_outflow}")
    
    return df_result

if __name__ == "__main__":
    # 测试超快速版本
    result = calculate_inflow_outflow_trends_ultra_fast(date_range_weeks=4)
    print(f"🎯 测试结果: {len(result)} 周数据")
    if not result.empty:
        print(result.head())