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
    from data_processor import load_defect_data, apply_chart_style # No enrich_ddf_with_master_info here
except ImportError:
    print("错误：无法导入 data_processor.py。请确保它在正确的路径下。")
    exit()

# --- Global Helper Functions ---
def count_linked_defects(relation_str):
    """Counts linked defects from a comma-separated string in relation_to_udf."""
    if pd.isna(relation_str) or not isinstance(relation_str, str) or relation_str.strip() == '':
        return 0
    return len([item for item in relation_str.split(',') if item.strip()])

def categorize_master_linked_level(count):
    """Categorizes master ticket linked defect level based on relation_to_udf count. Aligned with TopIssue risk scoring thresholds."""
    if count < 3:
        return 'Low'      # <3个链接缺陷
    elif 3 <= count < 5:
        return 'Medium'   # 3-4个链接缺陷
    elif count >= 5:
        return 'High'     # ≥5个链接缺陷
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

print("[App 8059 - 全局] 开始执行数据加载和预处理 (原始数据)...")
ddf_loaded_raw = load_defect_data(file_pattern="defect/2025_defect*.json")
ddf_processed_parents = pd.DataFrame()
relevant_weeks_global_raw = []

if ddf_loaded_raw.empty:
    print("[App 8059 - 全局] 未能加载缺陷数据，无法启动Dash应用。")
else:
    print(f"[App 8059 - 全局] 原始缺陷数据加载完成，行数: {len(ddf_loaded_raw)}")
    ddf_processed_parents = ddf_loaded_raw.copy()
    
    # 处理嵌套的 problem_finder_team_udf 字段
    if 'problem_finder_team_udf' in ddf_processed_parents.columns:
        # 定义安全提取函数，处理嵌套字典结构
        def extract_problem_finder_team(x):
            if isinstance(x, dict) and "name" in x:
                return x["name"]
            return str(x)
        
        # 应用提取函数处理嵌套结构
        ddf_processed_parents['problem_finder_team'] = ddf_processed_parents['problem_finder_team_udf'].apply(extract_problem_finder_team)
        print(f"[App 8059 - 全局] 已处理 problem_finder_team_udf 字段，提取了 name 值")
    else:
        ddf_processed_parents['problem_finder_team'] = 'Unknown'
        print("[App 8059 - 全局警告] 数据中不包含 'problem_finder_team_udf' 字段，已创建默认的 'problem_finder_team' 列")
    
    # 添加过滤逻辑：只保留 problem_finder_team 为 "DTSV_China" 的票据
    dtsv_china_tickets = ddf_processed_parents[ddf_processed_parents['problem_finder_team'] == 'DTSV_China']
    if not dtsv_china_tickets.empty:
        ddf_processed_parents = dtsv_china_tickets
        print(f"[App 8059 - 全局] 已过滤为仅显示 problem_finder_team 为 'DTSV_China' 的票据，剩余行数: {len(ddf_processed_parents)}")
    else:
        print("[App 8059 - 全局警告] 未找到 problem_finder_team 为 'DTSV_China' 的票据，将使用所有数据。")

    try:
        unique_weeks_raw = ddf_processed_parents['test_week'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique()
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
        
        ddf_processed_parents['test_week_sortable'] = pd.Categorical(
            ddf_processed_parents['test_week'],
            categories=sorted(unique_weeks_raw, key=sort_test_week),
            ordered=True
        )
        print("    [App 8059 - 全局准备] test_week_sortable 创建成功")
    except Exception as e:
        print(f"    [App 8059 - 全局警告] 创建 test_week_sortable 时出错: {e}。")
        if 'test_week' in ddf_processed_parents.columns:
            ddf_processed_parents['test_week_sortable'] = ddf_processed_parents['test_week']
        else:
            ddf_processed_parents['test_week_sortable'] = pd.Series(dtype='object')

    if 'parent_child' in ddf_processed_parents.columns and 'relation_to_udf' in ddf_processed_parents.columns:
        # We only care about actual Parent tickets from the raw data for this app's chart
        parent_tickets_actual = ddf_processed_parents[ddf_processed_parents['parent_child'] == 'Parent'].copy()
        parent_tickets_actual['linked_defect_count'] = parent_tickets_actual['relation_to_udf'].apply(count_linked_defects)
        parent_tickets_actual['master_linked_defect_level'] = parent_tickets_actual['linked_defect_count'].apply(categorize_master_linked_level)
        
        # For the ddf_processed_parents, we want all tickets but ensure these new columns are present for Parent tickets
        ddf_processed_parents = pd.merge(
            ddf_processed_parents,
            parent_tickets_actual[['id', 'linked_defect_count', 'master_linked_defect_level']],
            on='id',
            how='left'
        )
        ddf_processed_parents['master_linked_defect_level'] = ddf_processed_parents['master_linked_defect_level'].fillna('Not Parent/Unknown')
        ddf_processed_parents['linked_defect_count'] = ddf_processed_parents['linked_defect_count'].fillna(0).astype(int)
        print("    [App 8059 - 全局准备] linked_defect_count 和 master_linked_defect_level 列处理完成 (基于原始数据)")
    else:
        print("    [App 8059 - 全局警告] 原始数据缺少 'parent_child' 或 'relation_to_udf'。")
        ddf_processed_parents['master_linked_defect_level'] = 'Data Missing'
        ddf_processed_parents['linked_defect_count'] = 0
        
    ddf_processed_parents['tester'] = ddf_processed_parents.get('tester', pd.Series(index=ddf_processed_parents.index, name='tester')).fillna('Unknown Tester')
    print("    [App 8059 - 全局准备] tester 列处理完成")

    # child_count_of_master would typically come from enrichment, so it might be missing or 0 here
    # For table consistency, ensure the column exists
    if 'child_count_of_master' not in ddf_processed_parents.columns:
        ddf_processed_parents['child_count_of_master'] = 'N/A (raw)'


    if 'test_week_sortable' in ddf_processed_parents.columns and hasattr(ddf_processed_parents['test_week_sortable'], 'cat') and ddf_processed_parents['test_week_sortable'].cat.categories.size > 0:
        relevant_weeks_global_raw = ddf_processed_parents['test_week_sortable'].cat.categories.tolist()
        # Simplified relevant weeks for this app
        print(f"    [App 8059 - 全局准备] relevant_weeks_global_raw: {relevant_weeks_global_raw}")

print("[App 8059 - 全局] 数据加载和预处理完毕。")

def create_parent_complexity_line_chart(ddf_input, relevant_weeks_for_axis_display):
    print("    [App 8059 - 执行中] create_parent_complexity_line_chart 开始")
    if ddf_input.empty:
        return create_empty_figure("Parent Complexity (数据为空)", height=400, theme=theme_manager.get_theme())

    # Filter for actual Parent tickets for the chart itself
    ddf_parents_for_chart = ddf_input[ddf_input['parent_child'] == 'Parent'].copy()
    if ddf_parents_for_chart.empty:
        return create_empty_figure("Parent Complexity (无Parent票据数据)", height=400, theme=theme_manager.get_theme())
        
    if 'master_linked_defect_level' not in ddf_parents_for_chart.columns or 'test_week_sortable' not in ddf_parents_for_chart.columns:
        return create_empty_figure("Parent Complexity (缺少必要列)", height=400, theme=theme_manager.get_theme())

    if relevant_weeks_for_axis_display:
        ddf_filtered = ddf_parents_for_chart[ddf_parents_for_chart['test_week_sortable'].isin(relevant_weeks_for_axis_display)]
    else:
        ddf_filtered = ddf_parents_for_chart
        
    if ddf_filtered.empty:
        return create_empty_figure("Parent Complexity (筛选周后数据为空)", height=400, theme=theme_manager.get_theme())

    valid_levels = ['High', 'Medium', 'Low']
    line_data = ddf_filtered[
        ddf_filtered['master_linked_defect_level'].isin(valid_levels)
    ].groupby(['test_week_sortable', 'master_linked_defect_level'], observed=True).size().reset_index(name='count')

    if line_data.empty:
        return create_empty_figure("Parent Complexity (分组后数据为空)", height=400, theme=theme_manager.get_theme())
        
    fig = px.line(
        line_data, x='test_week_sortable', y='count', color='master_linked_defect_level',
        labels={'count': '父票据数量', 'test_week_sortable': '测试周 (CW)', 'master_linked_defect_level': '父票据关联等级'},
        markers=True, category_orders={'master_linked_defect_level': valid_levels},
        color_discrete_map={'Low': 'green', 'Medium': 'orange', 'High': 'red'},
        custom_data=['master_linked_defect_level', 'test_week_sortable', 'count']
    )
    fig = apply_chart_style(fig, title="DTSV China Parent Complexity (按父票据关联等级)", x_title="测试周 (CW)", y_title="父票据数量")
    if relevant_weeks_for_axis_display:
        fig.update_xaxes(type='category', categoryorder='array', categoryarray=relevant_weeks_for_axis_display)
    elif not line_data.empty:
        sorted_weeks = sorted(line_data['test_week_sortable'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique().tolist())
        fig.update_xaxes(type='category', categoryorder='array', categoryarray=sorted_weeks)
    print("    [App 8059 - 完成] create_parent_complexity_line_chart 结束")
    return fig

app = dash.Dash(__name__, title="Parent Complexity看板 (8059)")

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

line_chart_fig_raw_parents = create_parent_complexity_line_chart(ddf_processed_parents.copy() if not ddf_processed_parents.empty else pd.DataFrame(), relevant_weeks_global_raw)

def prepare_default_table_data_for_app2():
    if ddf_processed_parents.empty:
        return []
    # Default: Show Parent tickets with High master_linked_defect_level
    high_linked_parents = ddf_processed_parents[
        (ddf_processed_parents['parent_child'] == 'Parent') &
        (ddf_processed_parents['master_linked_defect_level'] == 'High')
    ]
    table_data = []
    for _, row in high_linked_parents.iterrows():
        table_data.append({
            "id": str(row.get('id', '')), # Parent's own ID
            "name": str(row.get('name', 'N/A (raw)')),
            "master_id": str(row.get('master_id', 'N/A (raw)')), # Likely not applicable or different in raw
            "child_ids_of_master_display": str(row.get('relation_to_udf','N/A (raw)')), # Show its own relations
            "child_count_of_master": row.get('child_count_of_master', 'N/A (raw)'), # Not directly from enrichment
            "matrix_display": str(row.get('matrix_display', 'N/A (raw)')),
            "classification_display": str(row.get('classification_display', 'N/A (raw)')),
            "pu": str(row.get('pu', 'N/A (raw)')),
            "status_phase": str(row.get('status_phase', 'N/A (raw)')),
            "linked_defect_count": row.get('linked_defect_count', 0), # Count from its relation_to_udf
            "master_linked_defect_level": str(row.get('master_linked_defect_level', '')),
            "parent_child": str(row.get('parent_child', 'Parent')),
            "tester": str(row.get('tester', 'Unknown Tester')) # Parent's own tester
        })
    return table_data

default_table_data_app2 = prepare_default_table_data_for_app2()

app.layout = html.Div([
        # 主题切换器
        create_theme_switcher(),
        
    html.H1("DTSV China Parent Complexity 数据看板 (原始数据)", id='main-title'),
    html.Div([
        dcc.Graph(id='parent-complexity-chart', figure=line_chart_fig_raw_parents, style={'height': '400px'})
    ], id='chart-container'),
    html.Div([
        html.H3("DTSV China 父票据详情数据", id='table-title'),
        html.Div(children="显示DTSV China团队高关联度父票据数据，点击图表数据点可以弹窗查看详细缺陷信息", id='click-data-info-raw'),
        dash_table.DataTable(
            id='defect-detail-table-raw',
            columns=[ # Same column structure for consistency
                {"name": "缺陷ID", "id": "id"}, {"name": "名称", "id": "name"},
                {"name": "主票据ID", "id": "master_id"}, {"name": "关联缺陷IDs (子)", "id": "child_ids_of_master_display"}, # Renamed label for clarity
                {"name": "子票据数 (主视角)", "id": "child_count_of_master"}, {"name": "Matrix显示", "id": "matrix_display"},
                {"name": "分类", "id": "classification_display"}, {"name": "PU", "id": "pu"},
                {"name": "状态阶段", "id": "status_phase"}, {"name": "本票关联数", "id": "linked_defect_count", "type": "numeric"},
                {"name": "本票关联等级", "id": "master_linked_defect_level"},
                {"name": "父/子票", "id": "parent_child"}, {"name": "测试员", "id": "tester"}
            ],
            data=default_table_data_app2,
            filter_action="native", sort_action="native", sort_mode="multi", page_action="native", page_size=10,
            style_as_list_view=False, filter_options={"case": "insensitive"},
            style_cell_conditional=[{'if': {'column_id': c}, 'width': w} for c, w in [('id', '80px'), ('name', '200px'), ('child_ids_of_master_display', '150px'), ('child_count_of_master', '80px'), ('linked_defect_count', '80px'), ('master_linked_defect_level', '100px'), ('parent_child', '80px'), ('tester', '100px')]],
            tooltip_data=[{col: {'value': str(val), 'type': 'markdown'} for col, val in row.items()} for row in default_table_data_app2],
            tooltip={'duration': None, 'type': 'markdown'},
            export_format="csv", export_headers="display"
        )
    ], id='defect-table-container-raw'),
    
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
                            {'name': '关联缺陷IDs', 'id': 'child_ids_of_master_display', 'type': 'text'},
                            {'name': '子票据数', 'id': 'child_count_of_master', 'type': 'text'},
                            {'name': 'Matrix', 'id': 'matrix_display', 'type': 'text'},
                            {'name': '分类', 'id': 'classification_display', 'type': 'text'},
                            {'name': 'PU', 'id': 'pu', 'type': 'text'},
                            {'name': '状态', 'id': 'status_phase', 'type': 'text'},
                            {'name': '关联数', 'id': 'linked_defect_count', 'type': 'numeric'},
                            {'name': '关联等级', 'id': 'master_linked_defect_level', 'type': 'text'},
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
    [Input('parent-complexity-chart', 'clickData'),
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
    if triggered_input == 'parent-complexity-chart' and click_data:
        try:
            point_data = click_data['points'][0]
            if 'customdata' not in point_data or len(point_data['customdata']) < 2:
                return {'display': 'none'}, [], ""
            
            level_clicked, week_clicked = point_data['customdata'][0], point_data['customdata'][1]
            
            # 筛选对应的数据
            filtered_df = ddf_processed_parents[
                (ddf_processed_parents['parent_child'] == 'Parent') &
                (ddf_processed_parents['test_week_sortable'] == week_clicked) &
                (ddf_processed_parents['master_linked_defect_level'] == level_clicked)
            ]
            
            # 准备Modal数据
            modal_data = []
            for _, row in filtered_df.iterrows():
                modal_data.append({
                    "id": str(row.get('id', '')),
                    "name": str(row.get('name', 'N/A')),
                    "master_id": str(row.get('master_id', 'N/A')),
                    "child_ids_of_master_display": str(row.get('relation_to_udf', 'N/A')),
                    "child_count_of_master": str(row.get('child_count_of_master', 'N/A')),
                    "matrix_display": str(row.get('matrix_display', 'N/A')),
                    "classification_display": str(row.get('classification_display', 'N/A')),
                    "pu": str(row.get('pu', 'N/A')),
                    "status_phase": str(row.get('status_phase', 'N/A')),
                    "linked_defect_count": row.get('linked_defect_count', 0),
                    "master_linked_defect_level": str(row.get('master_linked_defect_level', '')),
                    "parent_child": str(row.get('parent_child', 'Parent')),
                    "tester": str(row.get('tester', 'Unknown'))
                })
            
            info_text = f"测试周 {week_clicked} 的父票据关联等级为 {level_clicked} 的详细数据（共 {len(modal_data)} 条记录）"
            
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

@app.callback(
    [Output('defect-detail-table-raw', 'data'),
     Output('defect-detail-table-raw', 'tooltip_data'),
     Output('click-data-info-raw', 'children')],
    [Input('parent-complexity-chart', 'clickData')]
)
def display_click_data_app2(clickData):
    if clickData is None or ddf_processed_parents.empty:
        tooltip = [{col: {'value': str(val), 'type': 'markdown'} for col, val in row.items()} for row in default_table_data_app2]
        return default_table_data_app2, tooltip, "显示DTSV China团队高关联度父票据数据，点击图表可查看特定周和关联等级的父票据"

    try:
        point_data = clickData['points'][0]
        if 'customdata' not in point_data or len(point_data['customdata']) < 2:
            raise ValueError("Customdata 格式不正确")

        level_clicked, week_clicked = point_data['customdata'][0], point_data['customdata'][1]
        
        # Filter for Parent tickets from the ddf_processed_parents
        filtered_df = ddf_processed_parents[
            (ddf_processed_parents['parent_child'] == 'Parent') &
            (ddf_processed_parents['test_week_sortable'] == week_clicked) &
            (ddf_processed_parents['master_linked_defect_level'] == level_clicked)
        ]
        info_text = f"显示测试周 {week_clicked} 的DTSV China团队父票据关联等级为 {level_clicked} 的数据（共 {len(filtered_df)} 条记录，源自原始数据）"
        
        if filtered_df.empty:
            return [], [], info_text + " (没有详细数据可显示)"
            
        table_data = []
        for _, row in filtered_df.iterrows():
            table_data.append({
                "id": str(row.get('id', '')), # Parent's own ID
                "name": str(row.get('name', 'N/A (raw)')),
                "master_id": str(row.get('master_id', 'N/A (raw)')), 
                "child_ids_of_master_display": str(row.get('relation_to_udf', 'N/A (raw)')), # Show its own relations
                "child_count_of_master": str(row.get('child_count_of_master', 'N/A (raw)')), 
                "matrix_display": str(row.get('matrix_display', 'N/A (raw)')),
                "classification_display": str(row.get('classification_display', 'N/A (raw)')),
                "pu": str(row.get('pu', 'N/A (raw)')),
                "status_phase": str(row.get('status_phase', 'N/A (raw)')),
                "linked_defect_count": row.get('linked_defect_count', 0), 
                "master_linked_defect_level": str(row.get('master_linked_defect_level', '')),
                "parent_child": str(row.get('parent_child', 'Parent')), # Should be 'Parent'
                "tester": str(row.get('tester', 'Unknown Tester')) # Parent's own tester
            })
        tooltip_data = [{col: {'value': str(val), 'type': 'markdown'} for col, val in row.items()} for row in table_data]
        return table_data, tooltip_data, info_text
        
    except Exception as e:
        print(f"[App 8059 - Callback Error] {e}")
        import traceback
        traceback.print_exc()
        tooltip = [{col: {'value': str(val), 'type': 'markdown'} for col, val in row.items()} for row in default_table_data_app2]
        return default_table_data_app2, tooltip, f"处理点击数据时发生错误: {str(e)[:100]}"

# 图表主题更新回调
@app.callback(
    Output('parent-complexity-chart', 'figure'),
    [Input('global-theme-switcher', 'value')],
    prevent_initial_call=False
)
def update_chart_theme(selected_theme):
    if selected_theme:
        theme_manager.set_theme(selected_theme)
    
    # 重新生成图表以应用新主题
    return create_parent_complexity_line_chart(
        ddf_processed_parents.copy() if not ddf_processed_parents.empty else pd.DataFrame(), 
        relevant_weeks_global_raw
    )

# 主题切换回调
@app.callback(
    [Output('main-container', 'style'),
     Output('main-title', 'style'),
     Output('chart-container', 'style'),
     Output('table-title', 'style'),
     Output('click-data-info-raw', 'style'),
     Output('defect-table-container-raw', 'style'),
     Output('defect-detail-table-raw', 'css'),
     Output('defect-detail-table-raw', 'style_header'),
     Output('defect-detail-table-raw', 'style_cell'),
     Output('defect-detail-table-raw', 'style_data'),
     Output('defect-detail-table-raw', 'style_filter'),
     Output('defect-detail-table-raw', 'style_table'),
     Output('defect-detail-table-raw', 'style_data_conditional')],
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
            {'if': {'filter_query': '{master_linked_defect_level} = "High"'}, 'backgroundColor': 'rgba(102, 0, 0, 0.7)', 'color': 'white'},
            {'if': {'row_index': 'even'}, 'backgroundColor': '#000000', 'color': 'white'},
            {'if': {'row_index': 'odd'}, 'backgroundColor': '#000000', 'color': 'white'}
        ]
    else:
        highlight_style = [
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
    parser = argparse.ArgumentParser(description='启动 Parent Complexity 看板')
    parser.add_argument('--port', type=int, default=8059, help='服务器端口号')
    args = parser.parse_args()
    print(f"[App 8059 - Dash服务] 尝试在 http://0.0.0.0:{args.port}/ 启动Dash服务器...")
    try:
        app.run(debug=True, host='0.0.0.0', port=args.port)
    except Exception as e:
        print(f"[App 8059 - Dash服务错误] 启动Dash服务器失败: {e}")