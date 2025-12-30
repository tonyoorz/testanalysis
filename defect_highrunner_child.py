import pandas as pd
import plotly.express as px
import numpy as np
from dash_common_styles import (
    create_theme_switcher, get_theme_css, theme_manager, 
    MAIN_CONTAINER_STYLE, LIGHT_MAIN_CONTAINER_STYLE,
    TEXT_COLOR, LIGHT_TEXT_COLOR,
    TITLE_STYLE, LIGHT_TITLE_STYLE,
    SUBTITLE_STYLE, LIGHT_SUBTITLE_STYLE,
    CHART_CONTAINER_STYLE, LIGHT_CHART_CONTAINER_STYLE,
    CONTENT_CONTAINER_STYLE, LIGHT_CONTENT_CONTAINER_STYLE,
    get_datatable_styles, create_empty_figure
)
import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import argparse

try:
    from data_processor import load_defect_data, enrich_ddf_with_master_info, apply_chart_style
except ImportError:
    print("错误：无法导入 data_processor.py。请确保它在正确的路径下。")
    exit()

# --- Global Helper Functions ---
def categorize_defect_level(count):
    """Categorizes defect level based on child_count_of_master. Aligned with TopIssue risk scoring thresholds."""
    if pd.isna(count) or count < 3:
        return 'Low'      # <3个子票
    elif 3 <= count < 5:
        return 'Medium'   # 3-4个子票
    elif count >= 5:
        return 'High'     # ≥5个子票
    return 'Unknown'

def count_linked_defects(relation_str):
    """Counts linked defects from a comma-separated string in relation_to_udf."""
    if pd.isna(relation_str) or not isinstance(relation_str, str) or relation_str.strip() == '':
        return 0
    return len([item for item in relation_str.split(',') if item.strip()])

def categorize_master_linked_level(count):
    """Categorizes master ticket linked defect level based on relation_to_udf count."""
    if count == 1:
        return 'Low'
    elif 2 <= count <= 3: 
        return 'Medium'
    elif count > 3: 
        return 'High'
    return 'None'

def get_current_theme_styles():
    """根据当前主题返回相应的样式"""
    current_theme = theme_manager.get_theme()
    
    if current_theme == 'light':
        return {
            'main_container': LIGHT_MAIN_CONTAINER_STYLE,
            'title': LIGHT_TITLE_STYLE,
            'subtitle': LIGHT_SUBTITLE_STYLE,
            'chart_container': LIGHT_CHART_CONTAINER_STYLE,
            'content_container': LIGHT_CONTENT_CONTAINER_STYLE,
            'table_styles': get_datatable_styles('light')
        }
    else:
        return {
            'main_container': MAIN_CONTAINER_STYLE,
            'title': TITLE_STYLE,
            'subtitle': SUBTITLE_STYLE,
            'chart_container': CHART_CONTAINER_STYLE,
            'content_container': CONTENT_CONTAINER_STYLE,
            'table_styles': get_datatable_styles('dark')
        }
# --- End Global Helper Functions ---

print("[App 8058 - 全局] 开始执行数据加载和预处理...")
ddf_loaded_orig = load_defect_data(file_pattern="defect/2025_defect*.json")
ddf_processed = pd.DataFrame()
relevant_weeks_global = []

if ddf_loaded_orig.empty:
    print("[App 8058 - 全局] 未能加载缺陷数据，无法启动Dash应用。")
else:
    print(f"[App 8058 - 全局] 原始缺陷数据加载完成，行数: {len(ddf_loaded_orig)}")
    ddf_processed = enrich_ddf_with_master_info(ddf_loaded_orig.copy(), master_file_path="defect/2025_defect_master.json")
    
    if ddf_processed.empty:
        print("[App 8058 - 全局] 数据丰富化步骤后数据为空。")
    else:
        print(f"[App 8058 - 全局] 数据丰富化完成，行数: {len(ddf_processed)}")
        if 'child_ids_of_master_display' in ddf_processed.columns:
            print("DEBUG: [child_ids_of_master_display] 数据类型:", ddf_processed['child_ids_of_master_display'].dtype)
            # 打印前5个非空且非空白字符串的值，以了解实际内容
            sample_values = ddf_processed[ddf_processed['child_ids_of_master_display'].notna() & ddf_processed['child_ids_of_master_display'].astype(str).str.strip().ne('')]['child_ids_of_master_display'].head()
            if not sample_values.empty:
                print("DEBUG: [child_ids_of_master_display] 前5个有效示例值:\n", sample_values)
            else:
                print("DEBUG: [child_ids_of_master_display] 未找到有效的示例值 (均为 NaN, None, 或空字符串)")
            print(f"DEBUG: [child_ids_of_master_display] 空值 (NaN/None) 数量: {ddf_processed['child_ids_of_master_display'].isnull().sum()}")
            print(f"DEBUG: [child_ids_of_master_display] 空字符串数量: {ddf_processed[ddf_processed['child_ids_of_master_display'] == ''].shape[0]}")
        else:
            print("DEBUG: [child_ids_of_master_display] 列不存在")

        if 'child_count_of_master' in ddf_processed.columns:
            print("DEBUG: [原始 child_count_of_master] 唯一值:", ddf_processed['child_count_of_master'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique())
            print("DEBUG: [原始 child_count_of_master] 数据类型:", ddf_processed['child_count_of_master'].dtype)
        else:
            print("DEBUG: [原始 child_count_of_master] 列不存在")
        try:
            unique_weeks = ddf_processed['test_week'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique()
            # 更新排序逻辑以支持新的格式 "2025-CW01"
            def sort_test_week(week_str):
                try:
                    if '-CW' in str(week_str):
                        year_part, week_part = str(week_str).split('-CW')
                        return (int(year_part), int(week_part))
                    elif str(week_str).startswith('CW'):
                        # 兼容旧格式
                        return (2025, int(str(week_str).replace('CW', '')))
                    else:
                        return (9999, 999)
                except:
                    return (9999, 999)
            
            ddf_processed['test_week_sortable'] = pd.Categorical(
                ddf_processed['test_week'],
                categories=sorted(unique_weeks, key=sort_test_week),
                ordered=True
            )
            print("    [App 8058 - 全局准备] test_week_sortable 创建成功")
        except Exception as e:
            print(f"    [App 8058 - 全局警告] 创建 test_week_sortable 时出错: {e}。")
            if 'test_week' in ddf_processed.columns:
                ddf_processed['test_week_sortable'] = ddf_processed['test_week']
            else:
                ddf_processed['test_week_sortable'] = pd.Series(dtype='object')

        if 'child_count_of_master' not in ddf_processed.columns:
            ddf_processed['child_count_of_master'] = 0
        ddf_processed['child_count_of_master'] = pd.to_numeric(ddf_processed['child_count_of_master'], errors='coerce').fillna(0)
        print("DEBUG: [转换后 child_count_of_master] 唯一值:", ddf_processed['child_count_of_master'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique())
        print("DEBUG: [转换后 child_count_of_master] 数据类型:", ddf_processed['child_count_of_master'].dtype)
        
        # 创建 child_ids_of_master_display 列
        if 'child_ids_of_master' in ddf_processed.columns:
            print("DEBUG: 使用现有的 child_ids_of_master 列创建 child_ids_of_master_display")
            ddf_processed['child_ids_of_master_display'] = ddf_processed['child_ids_of_master'].astype(str)
        else:
            print("DEBUG: 未找到 child_ids_of_master 列，尝试从主票据关系中创建")
            # 为每个主票据ID创建子票据ID列表
            if 'master_id' in ddf_processed.columns and 'id' in ddf_processed.columns:
                # 收集每个主票据的子票据
                master_to_children = {}
                for _, row in ddf_processed[ddf_processed['master_id'].notna()].iterrows():
                    master_id = row['master_id']
                    child_id = row['id']
                    if master_id not in master_to_children:
                        master_to_children[master_id] = []
                    master_to_children[master_id].append(child_id)
                
                # 将子票据ID列表分配给每个票据
                ddf_processed['child_ids_of_master_display'] = ddf_processed['id'].apply(
                    lambda x: ', '.join(map(str, master_to_children.get(x, []))) if x in master_to_children else ''
                )
                print(f"DEBUG: 已为 {len(master_to_children)} 个主票据创建子票据ID显示")
            else:
                print("DEBUG: 无法创建 child_ids_of_master_display，缺少必要的列")
                ddf_processed['child_ids_of_master_display'] = ''
        
        # 检查 classification_display 列是否存在
        if 'classification_display' in ddf_processed.columns:
            print("DEBUG: classification_display 列已存在")
            # 检查列是否为空
            if ddf_processed['classification_display'].isnull().all() or (ddf_processed['classification_display'] == '').all():
                print("DEBUG: classification_display 列全为空值，尝试从其他列创建")
                if 'classification' in ddf_processed.columns:
                    ddf_processed['classification_display'] = ddf_processed['classification'].fillna('未分类').astype(str)
                    print("DEBUG: 已从 classification 列创建 classification_display 列")
                else:
                    print("DEBUG: 找不到 classification 列，创建默认值")
                    ddf_processed['classification_display'] = '未分类'
        else:
            print("DEBUG: classification_display 列不存在，需要创建")
            if 'classification' in ddf_processed.columns:
                ddf_processed['classification_display'] = ddf_processed['classification'].fillna('未分类').astype(str)
                print("DEBUG: 已从 classification 列创建 classification_display 列")
            else:
                print("DEBUG: 找不到 classification 列，创建默认值")
                ddf_processed['classification_display'] = '未分类'
        
        # 基于 parent_child 字段调整 child_count_of_master 的值
        if 'parent_child' in ddf_processed.columns:
            # 计算筛选前有多少非零的 child_count_of_master
            non_zero_before = (ddf_processed['child_count_of_master'] > 0).sum()
            
            # 只为 'Child' 和 'Child (candidate)' 类型的票据保留 child_count_of_master
            valid_child_types = ['Child', 'Child (candidate)']
            child_mask = ddf_processed['parent_child'].isin(valid_child_types)
            
            # 对非Child类型的票据，将 child_count_of_master 设为0
            ddf_processed.loc[~child_mask, 'child_count_of_master'] = 0
            
            # 计算筛选后有多少非零的 child_count_of_master
            non_zero_after = (ddf_processed['child_count_of_master'] > 0).sum()
            print(f"DEBUG: 基于 parent_child 筛选后，非零 child_count_of_master 从 {non_zero_before} 减少到 {non_zero_after}")
        else:
            print("DEBUG: 缺少 parent_child 列，无法筛选Child类型票据")
        
        ddf_processed['defect_level'] = ddf_processed['child_count_of_master'].apply(categorize_defect_level)
        print("DEBUG: [defect_level] 值计数:\n", ddf_processed['defect_level'].value_counts())
        print("    [App 8058 - 全局准备] defect_level 列处理完成")
        
        if 'parent_child' in ddf_processed.columns and 'relation_to_udf' in ddf_processed.columns:
            master_tickets_df = ddf_processed[ddf_processed['parent_child'] == 'Parent'].copy()
            master_tickets_df['linked_defect_count'] = master_tickets_df['relation_to_udf'].apply(count_linked_defects)
            master_tickets_df['master_linked_defect_level'] = master_tickets_df['linked_defect_count'].apply(categorize_master_linked_level)
            ddf_processed = pd.merge(ddf_processed, master_tickets_df[['id', 'linked_defect_count', 'master_linked_defect_level']], on='id', how='left')
            ddf_processed['master_linked_defect_level'] = ddf_processed['master_linked_defect_level'].fillna('Not Master/Unknown')
            ddf_processed['linked_defect_count'] = ddf_processed['linked_defect_count'].fillna(0).astype(int)
        else:
            ddf_processed['master_linked_defect_level'] = 'Data Missing'
            ddf_processed['linked_defect_count'] = 0
        print("    [App 8058 - 全局准备] linked_defect_count 和 master_linked_defect_level 列处理完成 (供表格)")

        ddf_processed['tester'] = ddf_processed.get('tester', pd.Series(index=ddf_processed.index, name='tester')).fillna('Unknown Tester')
        print("    [App 8058 - 全局准备] tester 列处理完成")

        if 'test_week_sortable' in ddf_processed.columns and hasattr(ddf_processed['test_week_sortable'], 'cat') and ddf_processed['test_week_sortable'].cat.categories.size > 0:
            all_available_weeks_sorted = ddf_processed['test_week_sortable'].cat.categories.tolist()
            relevant_weeks_global = all_available_weeks_sorted
            if 'child_count_of_master' in ddf_processed.columns:
                ddf_meaningful_data = ddf_processed[ddf_processed['child_count_of_master'] > 0]
                if not ddf_meaningful_data.empty and 'test_week_sortable' in ddf_meaningful_data.columns:
                    last_meaningful_week = ddf_meaningful_data['test_week_sortable'].max()
                    if pd.notna(last_meaningful_week):
                        try:
                            if last_meaningful_week in all_available_weeks_sorted:
                                last_meaningful_week_idx = all_available_weeks_sorted.index(last_meaningful_week)
                                relevant_weeks_global = all_available_weeks_sorted[:last_meaningful_week_idx + 1]
                        except ValueError:
                             pass 
            print(f"    [App 8058 - 全局准备] relevant_weeks_global: {relevant_weeks_global}")

print("[App 8058 - 全局] 数据加载和预处理完毕。")

def create_child_complexity_line_chart(ddf_input, relevant_weeks_for_axis_display):
    print("    [App 8058 - 执行中] create_child_complexity_line_chart 开始")
    if ddf_input.empty:
        return create_empty_figure("Child Complexity (数据为空)", height=400, theme=theme_manager.get_theme())

    ddf = ddf_input.copy()
    if 'defect_level' not in ddf.columns or 'test_week_sortable' not in ddf.columns:
        return create_empty_figure("Child Complexity (缺少必要列)", height=400, theme=theme_manager.get_theme())
    
    # 筛选只包含 Child 和 Child (candidate) 类型的票据
    if 'parent_child' in ddf.columns:
        valid_child_types = ['Child', 'Child (candidate)']
        ddf_child_only = ddf[ddf['parent_child'].isin(valid_child_types)]
        if ddf_child_only.empty:
            print("    [App 8058 - 警告] 筛选后没有符合条件的 Child 类型票据")
            return create_empty_figure("Child Complexity (没有符合条件的 Child 类型票据)", height=400, theme=theme_manager.get_theme())
        print(f"    [App 8058 - 信息] 筛选后只保留 Child 类型票据，从 {len(ddf)} 行减少到 {len(ddf_child_only)} 行")
        ddf = ddf_child_only
    else:
        print("    [App 8058 - 警告] 数据中缺少 parent_child 列，无法筛选 Child 类型票据")
        
    if relevant_weeks_for_axis_display:
        ddf_filtered = ddf[ddf['test_week_sortable'].isin(relevant_weeks_for_axis_display)]
    else:
        ddf_filtered = ddf

    if ddf_filtered.empty:
        return create_empty_figure("Child Complexity (筛选周后数据为空)", height=400, theme=theme_manager.get_theme())

    line_data = ddf_filtered.groupby(['test_week_sortable', 'defect_level'], observed=True).size().reset_index(name='count')
    if line_data.empty:
        return create_empty_figure("Child Complexity (分组后数据为空)", height=400, theme=theme_manager.get_theme())

    fig = px.line(
        line_data, x='test_week_sortable', y='count', color='defect_level',
        labels={'count': '子缺陷数量', 'test_week_sortable': '测试周 (CW)', 'defect_level': '子缺陷等级'},
        markers=True, category_orders={'defect_level': ['High', 'Medium', 'Low', 'Unknown']},
        color_discrete_map={'Low': 'green', 'Medium': 'yellow', 'High': 'red', 'Unknown': 'grey'},
        custom_data=['defect_level', 'test_week_sortable', 'count']
    )
    fig = apply_chart_style(fig, title="Child Complexity (按子缺陷等级划分)", x_title="测试周 (CW)", y_title="子缺陷数量")
    if relevant_weeks_for_axis_display:
        fig.update_xaxes(type='category', categoryorder='array', categoryarray=relevant_weeks_for_axis_display)
    elif not line_data.empty:
        sorted_weeks = sorted(line_data['test_week_sortable'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique().tolist())
        fig.update_xaxes(type='category', categoryorder='array', categoryarray=sorted_weeks)
    print("    [App 8058 - 完成] create_child_complexity_line_chart 结束")
    return fig

app = dash.Dash(__name__, title="Child Complexity看板 (8058)")

# 添加主题CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            ''' + get_theme_css() + '''
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

line_chart_fig = create_child_complexity_line_chart(ddf_processed.copy() if not ddf_processed.empty else pd.DataFrame(), relevant_weeks_global)

def prepare_default_table_data_for_app1():
    if ddf_processed.empty or 'defect_level' not in ddf_processed.columns:
        return []
    
    # 筛选高缺陷等级的记录
    high_defects = ddf_processed[ddf_processed['defect_level'] == 'High']
    
    # 只保留 Child 和 Child (candidate) 类型的票据
    if 'parent_child' in high_defects.columns:
        valid_child_types = ['Child', 'Child (candidate)']
        child_count_before = len(high_defects)
        high_defects = high_defects[high_defects['parent_child'].isin(valid_child_types)]
        child_count_after = len(high_defects)
        print(f"[App 8058 - 默认表格] 基于 parent_child 筛选后，High 记录数从 {child_count_before} 减少到 {child_count_after}")
    else:
        print("[App 8058 - 默认表格警告] 缺少 parent_child 列，无法筛选 Child 类型票据")
    
    table_data = []
    for _, row in high_defects.iterrows():
        table_data.append({
            "id": str(row.get('id', '')), "name": str(row.get('name', '')),
            "master_id": str(row.get('master_id', '')),
            "child_ids_of_master_display": str(row.get('child_ids_of_master_display', '')),
            "child_count_of_master": row.get('child_count_of_master', 0),
            "matrix_display": str(row.get('matrix_display', '')),
            "classification_display": str(row.get('classification_display', '')),
            "pu": str(row.get('pu', '')), "status_phase": str(row.get('status_phase', '')),
            "linked_defect_count": row.get('linked_defect_count', 0),
            "master_linked_defect_level": str(row.get('master_linked_defect_level', '')),
            "parent_child": str(row.get('parent_child', '')),
            "tester": str(row.get('tester', 'Unknown Tester'))
        })
    return table_data

default_table_data_app1 = prepare_default_table_data_for_app1()

app.layout = html.Div([
        # 主题切换器
        create_theme_switcher(),
        
    html.H1("Child Complexity", id='main-title'),
    html.Div([
        dcc.Graph(id='child-complexity-chart', figure=line_chart_fig, style={'height': '400px'})
    ], id='chart-container'),
    html.Div([
        html.H3("缺陷详情数据", id='table-title'),
        html.Div(children="显示所有高级子缺陷(High)数据，点击图表数据点可以弹窗查看详细缺陷信息", id='click-data-info'),
        dash_table.DataTable(
            id='defect-detail-table',
            columns=[
                {"name": "缺陷ID", "id": "id"}, {"name": "名称", "id": "name"},
                {"name": "主票据ID", "id": "master_id"}, {"name": "子票据IDs", "id": "child_ids_of_master_display"},
                {"name": "子票据数量", "id": "child_count_of_master", "type": "numeric"},
                {"name": "Matrix显示", "id": "matrix_display"}, {"name": "分类", "id": "classification_display"},
                {"name": "PU", "id": "pu"}, {"name": "状态阶段", "id": "status_phase"},
                {"name": "主票关联缺陷数", "id": "linked_defect_count", "type": "numeric"},
                {"name": "主票关联等级", "id": "master_linked_defect_level"},
                {"name": "父/子票", "id": "parent_child"}, {"name": "测试员", "id": "tester"}
            ],
            data=default_table_data_app1,
            filter_action="native", sort_action="native", sort_mode="multi", page_action="native", page_size=10,
            style_as_list_view=False, filter_options={"case": "insensitive"},
            style_cell_conditional=[{'if': {'column_id': c}, 'width': w} for c, w in [('id', '80px'), ('name', '200px'), ('child_ids_of_master_display', '150px'), ('child_count_of_master', '80px'), ('linked_defect_count', '80px'), ('master_linked_defect_level', '100px'), ('parent_child', '80px'), ('tester', '100px')]],
            tooltip_data=[{col: {'value': str(val), 'type': 'markdown'} for col, val in row.items()} for row in default_table_data_app1],
            tooltip={'duration': None, 'type': 'markdown'},
            export_format="csv", export_headers="display"
        )
    ], id='defect-table-container'),
    
    # 缺陷详情Modal弹窗
    html.Div(
        id='defect-modal',
        children=[
            html.Div(
                id='modal-content',
                children=[
                    html.Div([
                        html.H3("缺陷详情", style={'margin': '0', 'display': 'inline-block', 'color': '#333'}),
                        html.Button(
                            "×", 
                            id='close-modal-btn',
                            style={
                                'float': 'right',
                                'border': 'none',
                                'background': 'transparent',
                                'fontSize': '24px',
                                'cursor': 'pointer',
                                'color': '#666',
                                'padding': '0',
                                'width': '30px',
                                'height': '30px'
                            }
                        )
                    ], style={'borderBottom': '1px solid #ddd', 'paddingBottom': '10px', 'marginBottom': '20px'}),
                    
                    html.Div(id='modal-info', style={'marginBottom': '15px', 'fontSize': '14px', 'color': '#666'}),
                    
                    dash_table.DataTable(
                        id='modal-defect-table',
                        columns=[
                            {'name': 'ID', 'id': 'id', 'presentation': 'markdown'},
                            {'name': '名称', 'id': 'name', 'type': 'text'},
                            {'name': '主票据ID', 'id': 'master_id', 'type': 'text'},
                            {'name': '子票据IDs', 'id': 'child_ids_of_master_display', 'type': 'text'},
                            {'name': '子票据数量', 'id': 'child_count_of_master', 'type': 'numeric'},
                            {'name': 'Matrix', 'id': 'matrix_display', 'type': 'text'},
                            {'name': '分类', 'id': 'classification_display', 'type': 'text'},
                            {'name': 'PU', 'id': 'pu', 'type': 'text'},
                            {'name': '状态', 'id': 'status_phase', 'type': 'text'},
                            {'name': '主票关联数', 'id': 'linked_defect_count', 'type': 'numeric'},
                            {'name': '主票关联等级', 'id': 'master_linked_defect_level', 'type': 'text'},
                            {'name': '父/子票', 'id': 'parent_child', 'type': 'text'},
                            {'name': '测试员', 'id': 'tester', 'type': 'text'}
                        ],
                        sort_action='native',
                        sort_mode='multi',
                        filter_action='native',
                        filter_options={'placeholder_text': 'Filter column...'},
                        page_action='native',
                        page_current=0,
                        page_size=15,
                        style_table={'overflowX': 'auto', 'maxHeight': '500px', 'overflowY': 'auto'},
                        style_cell={
                            'textAlign': 'left',
                            'padding': '8px 12px',
                            'whiteSpace': 'normal',
                            'height': 'auto',
                            'fontSize': '13px'
                        },
                        style_header={
                            'backgroundColor': '#f8fafc',
                            'fontWeight': 'bold',
                            'fontSize': '13px'
                        }
                    )
                ],
                style={
                    'backgroundColor': 'white',
                    'margin': '15% auto',
                    'padding': '20px',
                    'border': '1px solid #888',
                    'borderRadius': '8px',
                    'width': '90%',
                    'maxWidth': '1200px',
                    'maxHeight': '70vh',
                    'overflowY': 'auto',
                    'position': 'relative'
                }
            )
        ],
        style={
            'display': 'none',
            'position': 'fixed',
            'zIndex': '1000',
            'left': '0',
            'top': '0',
            'width': '100%',
            'height': '100%',
            'backgroundColor': 'rgba(0,0,0,0.5)',
            'justifyContent': 'center',
            'alignItems': 'center'
        }
    )
], id="main-container")

# Modal弹窗回调函数
@app.callback(
    [Output('defect-modal', 'style'),
     Output('modal-defect-table', 'data'),
     Output('modal-info', 'children')],
    [Input('child-complexity-chart', 'clickData'),
     Input('close-modal-btn', 'n_clicks')],
    prevent_initial_call=True
)
def update_modal(click_data, close_clicks):
    from dash import callback_context
    
    ctx = callback_context
    if not ctx.triggered:
        return {'display': 'none'}, [], ""
    
    triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # 如果点击了关闭按钮，隐藏Modal
    if triggered_input == 'close-modal-btn':
        return {
            'display': 'none',
            'position': 'fixed',
            'zIndex': '1000',
            'left': '0',
            'top': '0',
            'width': '100%',
            'height': '100%',
            'backgroundColor': 'rgba(0,0,0,0.5)',
            'justifyContent': 'center',
            'alignItems': 'center'
        }, [], ""
    
    # 处理图表点击事件
    if triggered_input == 'child-complexity-chart' and click_data:
        try:
            point_data = click_data['points'][0]
            if 'customdata' not in point_data or len(point_data['customdata']) < 2:
                return {'display': 'none'}, [], ""
            
            level_clicked, week_clicked = point_data['customdata'][0], point_data['customdata'][1]
            
            # 筛选对应的数据 - 只显示Child类型票据
            valid_child_types = ['Child', 'Child (candidate)']
            filtered_df = ddf_processed[
                (ddf_processed['parent_child'].isin(valid_child_types)) &
                (ddf_processed['test_week_sortable'] == week_clicked) &
                (ddf_processed['defect_level'] == level_clicked)
            ]
            
            # 准备Modal数据
            modal_data = []
            for _, row in filtered_df.iterrows():
                modal_data.append({
                    "id": str(row.get('id', '')),
                    "name": str(row.get('name', 'N/A')),
                    "master_id": str(row.get('master_id', 'N/A')),
                    "child_ids_of_master_display": str(row.get('child_ids_of_master_display', 'N/A')),
                    "child_count_of_master": row.get('child_count_of_master', 0),
                    "matrix_display": str(row.get('matrix_display', 'N/A')),
                    "classification_display": str(row.get('classification_display', 'N/A')),
                    "pu": str(row.get('pu', 'N/A')),
                    "status_phase": str(row.get('status_phase', 'N/A')),
                    "linked_defect_count": row.get('linked_defect_count', 0),
                    "master_linked_defect_level": str(row.get('master_linked_defect_level', '')),
                    "parent_child": str(row.get('parent_child', 'Child')),
                    "tester": str(row.get('tester', 'Unknown'))
                })
            
            info_text = f"测试周 {week_clicked} 的子缺陷等级为 {level_clicked} 的详细数据（共 {len(modal_data)} 条记录）"
            
            # 显示Modal
            modal_style = {
                'display': 'flex',
                'position': 'fixed',
                'zIndex': '1000',
                'left': '0',
                'top': '0',
                'width': '100%',
                'height': '100%',
                'backgroundColor': 'rgba(0,0,0,0.5)',
                'justifyContent': 'center',
                'alignItems': 'center'
            }
            
            return modal_style, modal_data, info_text
            
        except Exception as e:
            print(f"[Modal Error] {e}")
            return {'display': 'none'}, [], ""
    
    return {'display': 'none'}, [], ""

# 图表主题更新回调
@app.callback(
    Output('child-complexity-chart', 'figure'),
    [Input('global-theme-switcher', 'value')],
    prevent_initial_call=False
)
def update_chart_theme(selected_theme):
    if selected_theme:
        theme_manager.set_theme(selected_theme)
    
    # 重新生成图表以应用新主题
    return create_child_complexity_line_chart(
        ddf_processed.copy() if not ddf_processed.empty else pd.DataFrame(), 
        relevant_weeks_global
    )

@app.callback(
    [Output('defect-detail-table', 'data'),
     Output('defect-detail-table', 'tooltip_data'),
     Output('click-data-info', 'children')],
    [Input('child-complexity-chart', 'clickData')]
)
def display_click_data_app1(clickData):
    if clickData is None or ddf_processed.empty:
        tooltip = [{col: {'value': str(val), 'type': 'markdown'} for col, val in row.items()} for row in default_table_data_app1]
        return default_table_data_app1, tooltip, "显示所有高级子缺陷(High)数据，点击图表可查看特定周和子缺陷级别数据"
    
    try:
        point_data = clickData['points'][0]
        if 'customdata' not in point_data or len(point_data['customdata']) < 2:
            raise ValueError("Customdata 格式不正确")
            
        level_clicked, week_clicked = point_data['customdata'][0], point_data['customdata'][1]
        
        # 先根据测试周和缺陷等级筛选
        filtered_df = ddf_processed[
            (ddf_processed['test_week_sortable'] == week_clicked) &
            (ddf_processed['defect_level'] == level_clicked)
        ]
        
        # 再根据 parent_child 筛选，只保留 Child 和 Child (candidate) 类型的票据
        if 'parent_child' in filtered_df.columns:
            valid_child_types = ['Child', 'Child (candidate)']
            child_count_before = len(filtered_df)
            filtered_df = filtered_df[filtered_df['parent_child'].isin(valid_child_types)]
            child_count_after = len(filtered_df)
            print(f"[App 8058 - 回调] 基于 parent_child 筛选后，记录数从 {child_count_before} 减少到 {child_count_after}")
            info_text = f"显示测试周 {week_clicked} 的子缺陷等级为 {level_clicked} 且票据类型为 Child 的数据（共 {len(filtered_df)} 条记录）"
        else:
            print("[App 8058 - 回调警告] 回调中缺少 parent_child 列，无法筛选 Child 类型票据")
            info_text = f"显示测试周 {week_clicked} 的子缺陷等级为 {level_clicked} 的数据（共 {len(filtered_df)} 条记录）"
        
        if filtered_df.empty:
            return [], [], info_text + " (没有详细数据可显示)"
            
        table_data = []
        for _, row in filtered_df.iterrows():
            table_data.append({
                "id": str(row.get('id', '')), "name": str(row.get('name', '')),
                "master_id": str(row.get('master_id', '')),
                "child_ids_of_master_display": str(row.get('child_ids_of_master_display', '')),
                "child_count_of_master": row.get('child_count_of_master', 0),
                "matrix_display": str(row.get('matrix_display', '')),
                "classification_display": str(row.get('classification_display', '')),
                "pu": str(row.get('pu', '')), "status_phase": str(row.get('status_phase', '')),
                "linked_defect_count": row.get('linked_defect_count', 0),
                "master_linked_defect_level": str(row.get('master_linked_defect_level', '')),
                "parent_child": str(row.get('parent_child', '')),
                "tester": str(row.get('tester', 'Unknown Tester'))
            })
        tooltip_data = [{col: {'value': str(val), 'type': 'markdown'} for col, val in row.items()} for row in table_data]
        return table_data, tooltip_data, info_text
        
    except Exception as e:
        print(f"[App 8058 - Callback Error] {e}")
        import traceback
        traceback.print_exc()
        tooltip = [{col: {'value': str(val), 'type': 'markdown'} for col, val in row.items()} for row in default_table_data_app1]
        return default_table_data_app1, tooltip, f"处理点击数据时发生错误: {str(e)[:100]}"

# 主题切换回调
@app.callback(
    [Output('main-container', 'style'),
     Output('main-title', 'style'),
     Output('chart-container', 'style'),
     Output('table-title', 'style'),
     Output('click-data-info', 'style'),
     Output('defect-table-container', 'style'),
     Output('defect-detail-table', 'css'),
     Output('defect-detail-table', 'style_header'),
     Output('defect-detail-table', 'style_cell'),
     Output('defect-detail-table', 'style_data'),
     Output('defect-detail-table', 'style_filter'),
     Output('defect-detail-table', 'style_table'),
     Output('defect-detail-table', 'style_data_conditional')],
    [Input('global-theme-switcher', 'value')],
    prevent_initial_call=False
)
def update_theme(selected_theme):
    if selected_theme:
        theme_manager.set_theme(selected_theme)
    
    styles = get_current_theme_styles()
    table_styles = styles['table_styles']
    
    # 高亮条件样式（适应主题）
    if selected_theme == 'dark':
        highlight_style = [
            {'if': {'filter_query': '{child_count_of_master} > 2'}, 'backgroundColor': '#330000', 'color': 'white'},
            {'if': {'filter_query': '{master_linked_defect_level} = "High"'}, 'backgroundColor': 'rgba(102, 0, 0, 0.7)', 'color': 'white'},
            {'if': {'row_index': 'even'}, 'backgroundColor': '#000000', 'color': 'white'},
            {'if': {'row_index': 'odd'}, 'backgroundColor': '#000000', 'color': 'white'}
        ]
    else:
        highlight_style = [
            {'if': {'filter_query': '{child_count_of_master} > 2'}, 'backgroundColor': '#FFEBEE', 'color': '#B71C1C'},
            {'if': {'filter_query': '{master_linked_defect_level} = "High"'}, 'backgroundColor': '#FFCDD2', 'color': '#B71C1C'},
            {'if': {'row_index': 'even'}, 'backgroundColor': '#FFFFFF', 'color': '#212529'},
            {'if': {'row_index': 'odd'}, 'backgroundColor': '#F8F9FA', 'color': '#212529'}
        ]
    
    return (
        styles['main_container'],
        styles['title'],
        styles['chart_container'],
        styles['subtitle'],
        {'marginBottom': '10px', 'textAlign': 'center', 'color': styles['main_container']['color']},
        styles['content_container'],
        table_styles['css'],
        table_styles['style_header'],
        table_styles['style_cell'],
        table_styles['style_data'],
        table_styles['style_filter'],
        table_styles['style_table'],
        highlight_style
    )

# 主题切换器样式更新回调
@app.callback(
    Output('global-theme-switcher', 'labelStyle'),
    [Input('global-theme-switcher', 'value')],
    prevent_initial_call=False
)
def update_theme_switcher_style(selected_theme):
    text_color = LIGHT_TEXT_COLOR if selected_theme == 'light' else TEXT_COLOR
    return {'display': 'inline-block', 'marginRight': '15px', 'color': text_color}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='启动 Child Complexity 看板')
    parser.add_argument('--port', type=int, default=8058, help='服务器端口号')
    args = parser.parse_args()
    print(f"[App 8058 - Dash服务] 尝试在 http://0.0.0.0:{args.port}/ 启动Dash服务器...")
    try:
        app.run(debug=True, host='0.0.0.0', port=args.port)
    except Exception as e:
        print(f"[App 8058 - Dash服务错误] 启动Dash服务器失败: {e}")
