import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dash.exceptions import PreventUpdate
import base64
import io
import os
from PIL import Image

# 导入现有图表生成函数
try:
    # 导入缺陷状态分布图
    from defectEDA import filter_dataframe, update_defect_status_chart
    
    # 导入测试状态图
    from test_coverage import update_graph
    
    # 导入缺陷复杂度趋势图
    from defect_trend import create_complexity_trend_figure_and_data
    
    # 导入风险分布和缺陷矩阵分布图
    from risk_analysis import update_coverage_defect_dashboard
    from defect_matrix import create_matrix_figure
    
    # 导入常用数据处理函数
    from data_processor import load_defect_data, load_test_data, apply_chart_style
    print("成功从模块导入图表生成函数")
except ImportError as e:
    print(f"警告: 无法导入图表生成函数。使用空数据。错误: {e}")
    def load_defect_data(pattern=""): return pd.DataFrame()
    def load_test_data(): return pd.DataFrame()
    def apply_chart_style(fig, title, x_title=None, y_title=None, height=400): return fig

# 全局样式设置
CHART_BG_COLOR = 'rgba(255, 255, 255, 1)'  # 白色背景
FONT_COLOR = 'black'
GRID_COLOR = 'rgba(100, 100, 100, 0.5)'

# 创建空图表的函数
def create_empty_figure(message="加载中...", height=300):
    fig = go.Figure()
    fig.update_layout(
        height=height,
        xaxis={"visible": False}, yaxis={"visible": False},
        annotations=[{"text": message, "xref": "paper", "yref": "paper", "showarrow": False, "font": {"size": 16, "color": FONT_COLOR}}],
        plot_bgcolor=CHART_BG_COLOR,
        paper_bgcolor=CHART_BG_COLOR
    )
    return fig

# 初始化应用
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "数据看板"

# 加载数据
print("加载数据...")
try:
    ddf = load_defect_data("defect/2025*.json") 
    tdf = load_test_data()
    print(f"数据加载完成。缺陷: {len(ddf)}, 测试: {len(tdf)}")
except Exception as e:
    print(f"加载数据时出错: {e}")
    ddf = pd.DataFrame()
    tdf = pd.DataFrame()

# 准备筛选器选项
project_options = []
if not ddf.empty and 'project' in ddf.columns:
    try:
        project_options = [{'label': str(p), 'value': str(p)} for p in sorted(ddf['project'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique()) if pd.notna(p)]
    except Exception as e:
        print(f"处理project选项时出错: {e}")
        # 不排序，直接使用
        project_options = [{'label': str(p), 'value': str(p)} for p in ddf['project'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique() if pd.notna(p)]
elif not tdf.empty and 'project' in tdf.columns:
    try:
        project_options = [{'label': str(p), 'value': str(p)} for p in sorted(tdf['project'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique()) if pd.notna(p)]
    except Exception as e:
        print(f"处理project选项时出错: {e}")
        project_options = [{'label': str(p), 'value': str(p)} for p in tdf['project'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique() if pd.notna(p)]
else:
    # 示例选项
    project_options = [{'label': '所有项目', 'value': 'all'}]

pu_options = []
if not ddf.empty and 'pu' in ddf.columns:
    try:
        pu_options = [{'label': str(p), 'value': str(p)} for p in sorted(ddf['pu'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique()) if pd.notna(p)]
    except Exception as e:
        print(f"处理pu选项时出错: {e}")
        pu_options = [{'label': str(p), 'value': str(p)} for p in ddf['pu'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique() if pd.notna(p)]
else:
    # 示例选项
    pu_options = [{'label': '所有PU', 'value': 'all'}]

fv_options = []  
if not ddf.empty and 'fv' in ddf.columns:
    try:
        # 将所有值转为字符串后再排序
        fv_values = [str(fv) for fv in ddf['fv'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique() if pd.notna(fv)]
        fv_options = [{'label': fv, 'value': fv} for fv in sorted(fv_values)]
    except Exception as e:
        print(f"处理fv选项时出错: {e}")
        # 不排序，直接使用
        fv_options = [{'label': str(fv), 'value': str(fv)} for fv in ddf['fv'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique() if pd.notna(fv)]
else:
    # 示例选项
    fv_options = [{'label': '所有FV', 'value': 'all'}]

aida_options = []
if not ddf.empty and 'top_aida' in ddf.columns:
    try:
        aida_options = [{'label': str(a), 'value': str(a)} for a in sorted(ddf['top_aida'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique()) if pd.notna(a)]
    except Exception as e:
        print(f"处理aida选项时出错: {e}")
        aida_options = [{'label': str(a), 'value': str(a)} for a in ddf['top_aida'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique() if pd.notna(a)]
elif not tdf.empty and 'top_aida' in tdf.columns:
    try:
        aida_options = [{'label': str(a), 'value': str(a)} for a in sorted(tdf['top_aida'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique()) if pd.notna(a)]
    except Exception as e:
        print(f"处理aida选项时出错: {e}")
        aida_options = [{'label': str(a), 'value': str(a)} for a in tdf['top_aida'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique() if pd.notna(a)]
else:
    # 示例选项
    aida_options = [{'label': '所有AIDA', 'value': 'all'}]

# 布局定义
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("数据看板", className="text-center my-4"),
            html.Hr(),
        ], width=12)
    ]),
    
    # 筛选器行
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Project:"),
                            dcc.Dropdown(
                                id="project-filter",
                                options=project_options,
                                multi=True,
                                placeholder="选择Project"
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("PU:"),
                            dcc.Dropdown(
                                id="pu-filter",
                                options=pu_options,
                                multi=True,
                                placeholder="选择PU"
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("FV:"),
                            dcc.Dropdown(
                                id="fv-filter",
                                options=fv_options,
                                multi=True,
                                placeholder="选择FV"
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Top AIDA:"),
                            dcc.Dropdown(
                                id="topaida-filter",
                                options=aida_options,
                                multi=True,
                                placeholder="选择Top AIDA"
                            )
                        ], width=3)
                    ])
                ])
            ], className="mb-4")
        ], width=12)
    ]),
    
    # 图表行 - 第一行
    dbc.Row([
        # 左侧图表
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("缺陷状态分布"),
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-defect-distribution",
                        type="circle",
                        children=dcc.Graph(id="defect-distribution-graph")
                    )
                ])
            ])
        ], width=6),
        
        # 右侧图表
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("按周和功能分类的测试状态"),
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-test-status",
                        type="circle",
                        children=dcc.Graph(id="test-status-graph")
                    )
                ])
            ])
        ], width=6)
    ], className="mb-4"),
    
    # 图表行 - 第二行
    dbc.Row([
        # 左侧图表
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("缺陷复杂度趋势"),
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-defect-complexity",
                        type="circle",
                        children=dcc.Graph(id="defect-complexity-graph")
                    )
                ])
            ])
        ], width=6),
        
        # 右侧图表
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("缺陷矩阵分布"),
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-defect-matrix",
                        type="circle",
                        children=dcc.Graph(id="defect-matrix-graph")
                    )
                ])
            ])
        ], width=6)
    ], className="mb-4"),
    
    # 图表行 - 第三行
    dbc.Row([
        # 风险分布图表
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("风险分布"),
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-risk-distribution",
                        type="circle",
                        children=dcc.Graph(id="risk-distribution-graph")
                    )
                ])
            ])
        ], width=12)
    ])
], fluid=True)

# 回调：缺陷状态分布图
@app.callback(
    Output("defect-distribution-graph", "figure"),
    [
        Input("project-filter", "value"),
        Input("pu-filter", "value"),
        Input("fv-filter", "value"),
        Input("topaida-filter", "value")
    ]
)
def update_defect_distribution(projects, pus, fvs, aidas):
    try:
        # 使用来自defectEDA的图表生成函数
        if 'update_defect_status_chart' in globals():
            # 将数据筛选传递给defectEDA的函数
            return update_defect_status_chart(projects, [], aidas, [])
        else:
            return create_empty_figure("缺陷状态分布图加载失败")
    except Exception as e:
        print(f"缺陷状态分布图生成错误: {e}")
        return create_empty_figure(f"错误: {str(e)}")

# 回调：测试状态图
@app.callback(
    Output("test-status-graph", "figure"),
    [
        Input("project-filter", "value"),
        Input("pu-filter", "value"),
        Input("fv-filter", "value"),
        Input("topaida-filter", "value")
    ]
)
def update_test_status(projects, pus, fvs, aidas):
    try:
        # 使用来自test_coverage的图表生成函数
        if 'update_graph' in globals():
            # 注意：test_coverage.py需要特定的输入结构，这里可能需要适配
            if not projects:
                projects = ['all']
            if not pus:
                pus = ['all']
            if not fvs:
                fvs = ['all']
            if not aidas:
                aidas = ['all']
                
            # 修复返回值解包问题
            # 直接获取函数的第一个返回值（图表）
            try:
                result = update_graph(projects, ['all'], pus, aidas, ['all'], fvs, None, None, None, fvs, aidas)
                # 只取第一个返回值 (图表对象)
                if isinstance(result, tuple) and len(result) > 0:
                    fig = result[0]
                    # 仅隐藏图例，不修改图表其他内容
                    fig.update_layout(
                        showlegend=False
                    )
                    return fig
                return create_empty_figure("无法提取图表对象")
            except Exception as e:
                print(f"调用 update_graph 时出错: {e}")
                return create_empty_figure(f"调用图表生成函数时出错: {str(e)}")
        else:
            return create_empty_figure("测试状态图加载失败")
    except Exception as e:
        print(f"测试状态图生成错误: {e}")
        return create_empty_figure(f"错误: {str(e)}")

# 回调：缺陷复杂度趋势图
@app.callback(
    Output("defect-complexity-graph", "figure"),
    [
        Input("project-filter", "value"),
        Input("pu-filter", "value"),
        Input("fv-filter", "value"),
        Input("topaida-filter", "value")
    ]
)
def update_defect_complexity(projects, pus, fvs, aidas):
    try:
        # 使用来自defect_trend的图表生成函数
        if 'create_complexity_trend_figure_and_data' in globals():
            # 这个函数不接受筛选参数，直接调用生成图表
            fig, _ = create_complexity_trend_figure_and_data()
            return fig if fig else create_empty_figure("无缺陷复杂度数据")
        else:
            return create_empty_figure("缺陷复杂度趋势图加载失败")
    except Exception as e:
        print(f"缺陷复杂度趋势图生成错误: {e}")
        return create_empty_figure(f"错误: {str(e)}")

# 回调：缺陷矩阵分布图
@app.callback(
    Output("defect-matrix-graph", "figure"),
    [
        Input("project-filter", "value"),
        Input("pu-filter", "value"),
        Input("fv-filter", "value"),
        Input("topaida-filter", "value")
    ]
)
def update_defect_matrix(projects, pus, fvs, aidas):
    try:
        # 使用来自defect_matrix的图表生成函数
        if 'create_matrix_figure' in globals():
            selected_project = projects[0] if projects and projects != ['all'] else None
            selected_aida = aidas[0] if aidas and aidas != ['all'] else None
            filtered_by = {'project': selected_project, 'aida': selected_aida}
            # 这个函数接受筛选参数
            return create_matrix_figure(ddf, filtered_by)
        else:
            return create_empty_figure("缺陷矩阵分布图加载失败")
    except Exception as e:
        print(f"缺陷矩阵分布图生成错误: {e}")
        return create_empty_figure(f"错误: {str(e)}")

# 回调：风险分布图
@app.callback(
    Output("risk-distribution-graph", "figure"),
    [
        Input("project-filter", "value"),
        Input("pu-filter", "value"),
        Input("fv-filter", "value"),
        Input("topaida-filter", "value")
    ]
)
def update_risk_distribution(projects, pus, fvs, aidas):
    try:
        # 使用来自risk_analysis的图表生成函数
        if 'update_coverage_defect_dashboard' in globals():
            # 调用风险分析图表
            return update_coverage_defect_dashboard(10, 50, 0, False, [])
        else:
            return create_empty_figure("风险分布图加载失败")
    except Exception as e:
        print(f"风险分布图生成错误: {e}")
        return create_empty_figure(f"错误: {str(e)}")

# 回调函数: 应用筛选器（用于记录筛选器选择）
@app.callback(
    Output("project-filter", "value"),
    [
        Input("project-filter", "value"),
        Input("pu-filter", "value"),
        Input("fv-filter", "value"),
        Input("topaida-filter", "value")
    ]
)
def update_display(projects, pus, fvs, aidas):
    # 记录筛选器更改，但不进行实际更新（为了避免循环更新）
    ctx = dash.callback_context
    if ctx.triggered:
        print(f"筛选器已更改: {ctx.triggered[0]['prop_id']} = {ctx.triggered[0]['value']}")
    
    # 返回当前project值（不作更改）
    return dash.no_update

# 运行应用
if __name__ == '__main__':
    app.run_server(debug=True, port=8070)