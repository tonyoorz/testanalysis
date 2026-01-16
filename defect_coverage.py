import dash
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output, State
import numpy as np
from dash import callback_context
import traceback
import dash_bootstrap_components as dbc

# --- 1. 加载数据 ---
from data_processor import load_defect_data # 从 data_processor 导入函数
ddf = load_defect_data() # 调用函数加载缺陷数据

# --- 配置 ---
px.defaults.template = "simple_white"

# 为缺陷状态定义颜色映射 (可以根据实际状态值调整)
# defect_status_color_map = {
#     "01 Open": "#1f77b4",  # 蓝色
#     "02 Clarification": "#ff7f0e",  # 橙色
#     "03 In Progress": "#2ca02c",  # 绿色
#     "04 Solved": "#d62728",  # 红色 (在原始代码中，此状态用于 'Failed'，这里用作一个解决状态)
#     "05 Test Pending": "#9467bd",  # 紫色
#     # "06 Solved" is often a key resolved state, ensure it's distinct or map to "04 Solved" if synonymous
#     "06 Solved": "#8c564b",  # 棕色 (如果 '06 Solved' 是主要解决状态，可使用更鲜明的颜色如绿色)
#     "07 Verified": "#e377c2",  # 粉色
#     "08 Closed": "#7f7f7f",  # 灰色
#     "09 Rejected": "#bcbd22",  # 黄绿色
#     "10 Deferred": "#17becf",   # 青色
#     "Unknown": "lightgrey" # 未知状态
# }
# 获取 ddf 中实际存在的所有 status_phase 值并更新映射
# if 'status_phase' in ddf.columns:
#     actual_statuses = ddf['status_phase'].unique()
#     for status in actual_statuses:
#         if status not in defect_status_color_map:
#             defect_status_color_map[status] = 'lightgrey' # 为未在映射中定义的状态设置默认颜色
# else:
#     print("警告: 'status_phase' 列在 ddf 中不存在，图表颜色可能不正确。")

# --- 新增: 为 Matrix 定义颜色映射 ---
matrix_color_map = {
    "matrix-1a": "#FF0000",  # 鲜红
    "matrix-1b": "#FF4500",  # 橙红
    "matrix-1c": "#FF8C00",  # 暗橙
    "matrix-1d": "#FFA500",  # 橙色
    "matrix-1e": "#FFD700",  # 金色
    "matrix-2a": "#ADFF2F",  # 绿黄色
    "matrix-2b": "#7FFF00",  # 草坪绿
    "matrix-2c": "#32CD32",  # 酸橙绿
    "matrix-3a": "#00FA9A",  # 中春绿色
    "matrix-3b": "#00FF7F",  # 春绿色
    "matrix-3c": "#48D1CC",  # 中绿松石
    "matrix-4a": "#40E0D0",  # 绿松石
    "matrix-4b": "#00CED1",  # 暗绿松石
    "matrix-5a": "#1E90FF",  # 道奇蓝
    "matrix-5b": "#00BFFF",  # 深天蓝
    "UnknownMatrix": "#D3D3D3",  # 浅灰色 (用于未知或空 Matrix 值)
    "": "#D3D3D3" # 浅灰色 (用于空字符串 Matrix 值)
}

# 获取 ddf 中实际存在的所有 matrix 值并更新映射
if 'matrix' in ddf.columns:
    # 确保在填充之前，将 ddf['matrix'] 中的 NaN 值替换为一个特定字符串，如 'UnknownMatrix'
    # 这样可以为它们在 color map 中分配一个颜色
    ddf['matrix'] = ddf['matrix'].fillna('UnknownMatrix')
    actual_matrices = ddf['matrix'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique()
    for mat_val in actual_matrices:
        if mat_val not in matrix_color_map:
            matrix_color_map[mat_val] = '#D3D3D3' # 默认为浅灰色
else:
    print("警告: 'matrix' 列在 ddf 中不存在，图表颜色将基于默认设置。")
# --- 结束新增 ---


# --- 2. 初始化 Dash 应用 ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "缺陷覆盖率看板"

# --- 3. 定义应用布局 ---

# === 准备下拉菜单选项 ===
def get_sorted_options(column_name, df, is_test_week=False):
    if column_name not in df.columns or df[column_name].isnull().all():
        print(f"警告: 列 '{column_name}' 不存在或全为空，无法生成下拉选项。")
        return []
    try:
        # 转换为字符串以处理混合类型，然后取唯一值并排序
        unique_values = sorted(df[column_name].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().astype(str).unique())
        unique_values = [val for val in unique_values if val] # 过滤空字符串
        if is_test_week:
            # 假设 test_week 格式为 'CWXX'
            unique_values = sorted(unique_values, key=lambda x: int(x[2:]) if x.startswith('CW') and len(x) > 2 and x[2:].isdigit() else 999)
        return unique_values
    except Exception as e:
        print(f"处理列 '{column_name}' 时出错: {e}. 使用空列表代替.")
        return []

project_options = get_sorted_options('project', ddf)
testweek_options = get_sorted_options('test_week', ddf, is_test_week=True)
pu_options = get_sorted_options('pu', ddf)
top_aida_options = get_sorted_options('top_aida', ddf)
fvp_options = get_sorted_options('fvp', ddf)
fv_options = get_sorted_options('fv', ddf)

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("缺陷覆盖率看板", className="text-center my-4"))),

    dbc.Card([
        dbc.CardHeader("筛选器"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Project:", html_for='project-dropdown-defect', style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='project-dropdown-defect',
                        options=[{'label': '全部', 'value': 'all'}] + [{'label': i, 'value': i} for i in project_options],
                        value=['all'], multi=True, placeholder="选择 Project..."
                    )
                ], md=4),
                dbc.Col([
                    dbc.Label("发现周 (Test Week):", html_for='testweek-dropdown-defect', style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='testweek-dropdown-defect',
                        options=[{'label': '全部', 'value': 'all'}] + [{'label': i, 'value': i} for i in testweek_options],
                        value=['all'], multi=True, placeholder="选择发现周..."
                    )
                ], md=4),
                dbc.Col([
                    dbc.Label("PU:", html_for='pu-dropdown-defect', style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='pu-dropdown-defect',
                        options=[{'label': '全部', 'value': 'all'}] + [{'label': i, 'value': i} for i in pu_options],
                        value=['all'], multi=True, placeholder="选择 PU..."
                    )
                ], md=4),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Top AIDA:", html_for='aida-dropdown-defect', style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='aida-dropdown-defect',
                        options=[{'label': '全部', 'value': 'all'}] + [{'label': i, 'value': i} for i in top_aida_options],
                        value=['all'], multi=True, placeholder="选择 Top AIDA..."
                    )
                ], md=4),
                dbc.Col([
                    dbc.Label("FVP:", html_for='fvp-dropdown-defect', style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='fvp-dropdown-defect',
                        options=[{'label': '全部', 'value': 'all'}] + [{'label': i, 'value': i} for i in fvp_options],
                        value=['all'], multi=True, placeholder="选择 FVP..."
                    )
                ], md=4),
                dbc.Col([
                    dbc.Label("FV:", html_for='fv-dropdown-defect', style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='fv-dropdown-defect',
                        options=[{'label': '全部', 'value': 'all'}] + [{'label': i, 'value': i} for i in fv_options],
                        value=['all'], multi=True, placeholder="选择 FV..."
                    )
                ], md=4),
            ])
        ])
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("图表 1: 按周和功能分类的缺陷Matrix"),
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-graph-1-defect", type="circle",
                        children=dcc.Graph(id='defect-fv-week-chart', clear_on_unhover=True)
                    )
                ])
            ])
        ], md=12, className="mb-4")
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("图表 2: 按 Top AIDA 和测试周分类的缺陷Matrix"),
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-graph-2-defect", type="circle",
                        children=dcc.Graph(id='defect-aida-week-chart', clear_on_unhover=True)
                    )
                ])
            ])
        ], md=12, className="mb-4")
    ]),
], fluid=True)

# --- 4. 定义回调函数 ---
@app.callback(
    [Output('defect-fv-week-chart', 'figure'),
     Output('defect-aida-week-chart', 'figure'),
     Output('fv-dropdown-defect', 'value'),       # Output to update FV dropdown
     Output('aida-dropdown-defect', 'value')],    # Output to update AIDA dropdown
    [Input('project-dropdown-defect', 'value'),
     Input('testweek-dropdown-defect', 'value'),
     Input('pu-dropdown-defect', 'value'),
     Input('aida-dropdown-defect', 'value'),      # Input from AIDA dropdown
     Input('fvp-dropdown-defect', 'value'),
     Input('fv-dropdown-defect', 'value'),        # Input from FV dropdown
     Input('defect-fv-week-chart', 'clickData'),  # Click data from chart 1
     Input('defect-aida-week-chart', 'clickData')],# Click data from chart 2
    [State('fv-dropdown-defect', 'value'),        # State of FV dropdown
     State('aida-dropdown-defect', 'value')]      # State of AIDA dropdown
)
def update_defect_graphs(selected_projects, selected_testweeks, selected_pus,
                         selected_aidas_input, selected_fvps, selected_fvs_input,
                         click_data_fv_chart, click_data_aida_chart, # Renamed for clarity
                         fv_dropdown_state, aida_dropdown_state):   # Renamed for clarity
    
    print("--- Defect Callback triggered ---")
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'No trigger'
    print(f"Triggered by: {triggered_id}")

    # Helper to create an empty figure with a message
    def create_empty_figure(message="没有符合筛选条件的数据"):
        fig = go.Figure()
        fig.update_layout(
            xaxis={"visible": False}, yaxis={"visible": False},
            annotations=[{"text": message, "xref": "paper", "yref": "paper", "showarrow": False, "font": {"size": 20}}],
            plot_bgcolor='rgba(248, 248, 250, 0.5)' # Light background for empty chart
        )
        return fig

    # Helper to check if a filter is active (i.e., not 'all' and not empty)
    def is_filter_active(selected_values):
        return isinstance(selected_values, list) and selected_values and 'all' not in selected_values

    # Initialize filter lists from state, defaulting to ['all'] if empty or None
    output_fvs = list(fv_dropdown_state) if isinstance(fv_dropdown_state, list) and fv_dropdown_state else ['all']
    output_aidas = list(aida_dropdown_state) if isinstance(aida_dropdown_state, list) and aida_dropdown_state else ['all']
    print(f"Initial state from dropdowns: fvs={output_fvs}, aidas={output_aidas}")

    clicked_value = None
    filter_type_clicked = None # To distinguish which chart click triggered

    # Process click data from the FV chart (Chart 1)
    if triggered_id == 'defect-fv-week-chart' and click_data_fv_chart:
        clicked_value = click_data_fv_chart['points'][0]['y'] # FV is on y-axis
        filter_type_clicked = 'fv'
        print(f"Defect Chart 1 (FV vs Week) clicked. FV value: {clicked_value}")
        if 'all' in output_fvs: output_fvs = [] # Clear 'all' if a specific FV is clicked
        if clicked_value in output_fvs:
            output_fvs.remove(clicked_value)
        else:
            output_fvs.append(clicked_value)
        if not output_fvs: output_fvs = ['all'] # Reset to 'all' if list becomes empty
        print(f"FV list updated by chart click: {output_fvs}")

    # Process click data from the AIDA chart (Chart 2)
    elif triggered_id == 'defect-aida-week-chart' and click_data_aida_chart:
        clicked_value = click_data_aida_chart['points'][0]['y'] # Top AIDA is on y-axis
        filter_type_clicked = 'aida'
        print(f"Defect Chart 2 (AIDA vs Week) clicked. AIDA value: {clicked_value}")
        if 'all' in output_aidas: output_aidas = [] # Clear 'all' if a specific AIDA is clicked
        if clicked_value in output_aidas:
            output_aidas.remove(clicked_value)
        else:
            output_aidas.append(clicked_value)
        if not output_aidas: output_aidas = ['all'] # Reset to 'all' if list becomes empty
        print(f"AIDA list updated by chart click: {output_aidas}")
    
    # If triggered by dropdowns themselves, update the output lists from inputs
    elif triggered_id == 'fv-dropdown-defect':
        output_fvs = list(selected_fvs_input) if isinstance(selected_fvs_input, list) and selected_fvs_input else ['all']
        print(f"FV dropdown changed. New FV selection: {output_fvs}")
    elif triggered_id == 'aida-dropdown-defect':
        output_aidas = list(selected_aidas_input) if isinstance(selected_aidas_input, list) and selected_aidas_input else ['all']
        print(f"AIDA dropdown changed. New AIDA selection: {output_aidas}")
    # Handle other dropdowns by ensuring the stateful fv/aida lists are used if not directly changed
    # This covers cases where project, week, pu, fvp dropdowns change
    else:
        # If no click and not FV/AIDA dropdown, ensure current input values for FV/AIDA are used
        # only if they are the source of the trigger. Otherwise, stick to state.
        # This logic is complex. Simpler: if not a click, fv/aida dropdowns reflect their direct input.
        if triggered_id not in ['defect-fv-week-chart', 'defect-aida-week-chart']:
             output_fvs = list(selected_fvs_input) if isinstance(selected_fvs_input, list) and selected_fvs_input else ['all']
             output_aidas = list(selected_aidas_input) if isinstance(selected_aidas_input, list) and selected_aidas_input else ['all']
        print(f"Trigger from other dropdown or initial load. Using fvs={output_fvs}, aidas={output_aidas}")


    # --- Filter Data ---
    filtered_ddf = ddf.copy()
    if is_filter_active(selected_projects):
        filtered_ddf = filtered_ddf[filtered_ddf['project'].isin(selected_projects)]
    if is_filter_active(selected_testweeks):
        filtered_ddf = filtered_ddf[filtered_ddf['test_week'].isin(selected_testweeks)]
    if is_filter_active(selected_pus):
        filtered_ddf = filtered_ddf[filtered_ddf['pu'].isin(selected_pus)]
    if is_filter_active(selected_fvps):
        filtered_ddf = filtered_ddf[filtered_ddf['fvp'].isin(selected_fvps)]
    
    # Apply AIDA and FV filters using the potentially updated output_aidas/output_fvs
    if is_filter_active(output_aidas): # Use the determined output_aidas
        if 'top_aida' in filtered_ddf.columns:
            filtered_ddf = filtered_ddf[filtered_ddf['top_aida'].isin(output_aidas)]
        else:
            print("警告: Top AIDA 筛选已选择但 'top_aida' 列缺失。")
            empty_fig = create_empty_figure("错误: 'top_aida' 列不存在")
            return empty_fig, empty_fig, output_fvs, output_aidas
            
    if is_filter_active(output_fvs): # Use the determined output_fvs
        if 'fv' in filtered_ddf.columns:
            filtered_ddf = filtered_ddf[filtered_ddf['fv'].isin(output_fvs)]
        else:
            print("警告: FV 筛选已选择但 'fv' 列缺失。")
            empty_fig = create_empty_figure("错误: 'fv' 列不存在")
            return empty_fig, empty_fig, output_fvs, output_aidas

    if filtered_ddf.empty:
        print("Filtered defect data is empty.")
        empty_fig = create_empty_figure()
        return empty_fig, empty_fig, output_fvs, output_aidas

    # Ensure necessary columns for charts exist
    chart_cols = ['id', 'test_week', 'matrix', 'fv', 'fvp', 'top_aida']
    missing_cols = [col for col in chart_cols if col not in filtered_ddf.columns]
    if missing_cols:
        print(f"警告: 必需列 {missing_cols} 在筛选后的缺陷数据中缺失。")
        error_fig = create_empty_figure(f"错误: 缺失列 {', '.join(missing_cols)}")
        return error_fig, error_fig, output_fvs, output_aidas
            
    def sort_key_cw(week_str): # Sorting for 'CWXX'
        if isinstance(week_str, str) and week_str.startswith('CW') and week_str[2:].isdigit():
            return int(week_str[2:])
        return 9999 # Fallback

    # --- Chart 1: FV vs Week for Defects ---
    fig1 = create_empty_figure("缺陷图表1加载中...")
    try:
        # Group by test_week, fvp, fv, and matrix, then count unique defect IDs
        grouped_data1 = filtered_ddf.groupby(
            ["test_week", "fvp", "fv", "matrix"], as_index=False
        )['id'].nunique().rename(columns={'id': 'count'})

        if grouped_data1.empty:
            fig1 = create_empty_figure("无数据显示 (图表1)")
        else:
            grouped_data1['test_week_sort'] = grouped_data1['test_week'].apply(sort_key_cw)
            # Sort by FVP then FV for y-axis ordering
            grouped_data1['fvp_sort_str'] = grouped_data1['fvp'].fillna('ZZZ').astype(str) # Handle NaN in FVP for sorting
            grouped_data1['fv_sort_str'] = grouped_data1['fv'].fillna('ZZZ').astype(str)   # Handle NaN in FV
            grouped_data1 = grouped_data1.sort_values(["test_week_sort", "fvp_sort_str", "fv_sort_str"])
            
            sorted_weeks1 = grouped_data1['test_week'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique()
            # Get unique FVs sorted by FVP then FV
            sorted_fvs1 = grouped_data1.drop_duplicates(subset=['fvp_sort_str', 'fv_sort_str']).sort_values(
                by=['fvp_sort_str', 'fv_sort_str']
            )['fv'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique()


            fig1 = px.scatter(
                grouped_data1, x="test_week", y="fv", color="matrix", size="count",
                size_max=30, opacity=0.8,
                hover_data={"test_week": True, "fvp": True, "fv": True, "matrix": True, "count": True, 
                              "test_week_sort":False, "fvp_sort_str":False, "fv_sort_str":False}, # Hide sort keys from hover
                labels={"test_week": "发现周", "fv": "功能 (FV)", "matrix": "Matrix", "count": "缺陷数量", "fvp":"FVP"},
                color_discrete_map=matrix_color_map,
                category_orders={
                    "test_week": list(sorted_weeks1), 
                    "fv": list(sorted_fvs1), # Use the custom sorted FV list
                    "matrix": list(matrix_color_map.keys())
                }
            )
            fig1.update_layout(
                height=700, xaxis={'tickangle': -45},
                xaxis_title="发现周", yaxis_title="功能 (FV)",
                title="按周和功能分类的缺陷Matrix (气泡大小: 缺陷数)", 
                showlegend=True, legend_title_text="Matrix",
                xaxis_showgrid=True, yaxis_showgrid=True, plot_bgcolor='rgba(248, 248, 250, 0.5)',
                hoverlabel=dict(bgcolor="white", font_size=12)
            )
            fig1.update_traces(marker=dict(sizemode='area', line_width=1, line_color='black'))
    except Exception as e:
        print(f"创建缺陷图表1时出错: {e}")
        traceback.print_exc()
        fig1 = create_empty_figure(f"图表1出错: {str(e)[:100]}")

    # --- Chart 2: Top AIDA vs Week for Defects ---
    fig2 = create_empty_figure("缺陷图表2加载中...")
    try:
        grouped_data2 = filtered_ddf.groupby(
            ["test_week", "top_aida", "matrix"], as_index=False
        )['id'].nunique().rename(columns={'id': 'count'})

        if grouped_data2.empty:
            fig2 = create_empty_figure("无数据显示 (图表2)")
        else:
            grouped_data2['test_week_sort'] = grouped_data2['test_week'].apply(sort_key_cw)
            grouped_data2['top_aida_sort_str'] = grouped_data2['top_aida'].fillna('ZZZ').astype(str)
            grouped_data2 = grouped_data2.sort_values(["test_week_sort", "top_aida_sort_str"])
            
            sorted_weeks2 = grouped_data2['test_week'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique()
            sorted_aidas2 = grouped_data2['top_aida'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique() # Already sorted by top_aida_sort_str

            fig2 = px.scatter(
                grouped_data2, x='test_week', y='top_aida', color='matrix', size='count',
                size_max=30, opacity=0.8,
                title="按 Top AIDA 和发现周分类的缺陷Matrix (气泡大小: 缺陷数)",
                labels={'count': '缺陷数量', 'top_aida': 'Top AIDA', 'test_week': '发现周', 'matrix': 'Matrix'},
                color_discrete_map=matrix_color_map,
                category_orders={
                    'test_week': list(sorted_weeks2), 
                    'top_aida': list(sorted_aidas2), 
                    'matrix': list(matrix_color_map.keys())
                },
                hover_data={"test_week": True, "top_aida": True, "matrix": True, "count": True,
                              "test_week_sort":False, "top_aida_sort_str":False} # Hide sort keys
            )
            fig2.update_layout(
                height=max(600, len(sorted_aidas2) * 25 + 150), # Dynamic height
                xaxis={'tickangle': -45},
                xaxis_title="发现周", yaxis_title="Top AIDA", 
                legend_title_text="Matrix",
                xaxis_showgrid=True, yaxis_showgrid=True, plot_bgcolor='rgba(248, 248, 250, 0.5)',
                hoverlabel=dict(bgcolor="white", font_size=12)
            )
            fig2.update_traces(marker=dict(sizemode='area', line_width=1, line_color='black'))
    except Exception as e:
        print(f"创建缺陷图表2时出错: {e}")
        traceback.print_exc()
        fig2 = create_empty_figure(f"图表2出错: {str(e)[:100]}")

    print("--- Defect Callback finished ---")
    # Return figures and the updated dropdown values
    return fig1, fig2, output_fvs, output_aidas

# --- 5. 运行应用 ---
if __name__ == '__main__':
    # Make sure debug=True is used for development to see errors and auto-reload
    app.run_server(debug=True, port=8056, host='0.0.0.0')