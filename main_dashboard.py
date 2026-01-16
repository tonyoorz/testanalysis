import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import io
from wordcloud import WordCloud, STOPWORDS
# 设置matplotlib后端为非GUI模式，避免macOS上的NSWindow线程问题
import matplotlib
matplotlib.use('Agg')  # 使用非GUI后端
import matplotlib.pyplot as plt
import base64 # For embedding matplotlib wordcloud
import os

# 设置环境变量以避免trend_dashboard重复计算
os.environ['SKIP_DUPLICATE_CALCULATION'] = 'true'

# --- Import data loading and chart functions ---
try:
    from data_processor import load_defect_data, load_test_data, extract_english, SEVERITY_COLORS, apply_chart_style
    print("Successfully imported from data_processor")
except ImportError as e:
    print(f"Warning: Could not import from data_processor. Using dummy data/functions. Error: {e}")
    def load_defect_data(pattern=""): return pd.DataFrame()
    def load_test_data(): return pd.DataFrame()
    def extract_english(text): return str(text)
    SEVERITY_COLORS = {'严重问题': '#d62728', '一般问题': '#2ca02c', 'Unknown': '#cccccc'}
    def apply_chart_style(fig, title, x_title=None, y_title=None, height=400): return fig

# Import chart generation logic (or adapt functions directly)
# try:
#     # From defect_map_dashboard.py (Adapt relevant parts)
#     from defect_map_dashboard import testers_locations, beijing_location, target_locations, CITY_COLORS, update_animated_map, create_initial_figure
#     print("Successfully imported from defect_map_dashboard")
# except ImportError as e:
#     print(f"Warning: Could not import from defect_map_dashboard. Map functionality limited. Error: {e}")
#     testers_locations = {
#         'Felipe Wu': {'city': 'Taipei', 'lat': 25.0330, 'lon': 121.5654, 'country': 'China'},
#         'Adley Wong': {'city': 'Hong Kong', 'lat': 22.3193, 'lon': 114.1694, 'country': 'Hong Kong'},
#         'Vito Wang': {'city': 'Nanjing', 'lat': 32.0603, 'lon': 118.7969, 'country': 'China'},
#         'Linna Li': {'city': 'Nanjing', 'lat': 32.0603, 'lon': 118.7969, 'country': 'China'},
#     }
#     beijing_location = {'city': 'Beijing', 'lat': 39.9042, 'lon': 116.4074, 'country': 'China'}
#     target_locations = {name: loc for name, loc in testers_locations.items() if loc['city'] != 'Beijing'}
#     CITY_COLORS = {
#         'Beijing': '#aec7e8',   # 浅蓝
#         'Nanjing': '#98df8a',   # 浅绿
#         'Hong Kong': '#ffbb78', # 浅橙
#         'Taipei': '#ff9896',    # 浅红
#         'Unknown': '#cccccc'     # 灰色 (备用)
#     }
    
    # Define a proper create_initial_figure function
    # def create_initial_figure():
    #     fig = go.Figure()
    #     # Create a map with China as center
    #     fig.update_layout(
    #         mapbox_style="carto-darkmatter",
    #         mapbox=dict(
    #             center=dict(lat=36, lon=103),
    #             zoom=2.8,
    #             pitch=0
    #         ),
    #         margin={"r":0,"t":40,"l":0,"b":0},
    #         height=400,
    #         title="缺陷地理分布 (静态)",
    #         paper_bgcolor='rgba(0,0,0,0)',
    #         plot_bgcolor='rgba(0,0,0,0)',
    #     )
    #     return fig

try:
    # From defect_matrix_dashboard.py
    from defect_matrix_dashboard import create_matrix_figure_flipped
    print("Successfully imported from defect_matrix_dashboard")
except ImportError as e:
    print(f"Warning: Could not import from defect_matrix_dashboard. Matrix chart unavailable. Error: {e}")
    def create_matrix_figure_flipped(df, filtered_by=None): return go.Figure().update_layout(title="Matrix Unavailable")

try:
    # From trend_dashboard.py (Adapt relevant parts)
    from trend_dashboard import create_complexity_trend_figure_and_data # This returns fig and data, we might need just the fig part or adapt it
    print("Successfully imported from trend_dashboard")
except ImportError as e:
    print(f"Warning: Could not import from trend_dashboard. Complexity trend unavailable. Error: {e}")
    def create_complexity_trend_figure_and_data(defect_data_pattern=".", history_folder="."): return go.Figure().update_layout(title="Complexity Trend Unavailable"), pd.DataFrame()

try:
    # From test_coverage.py (Adapt relevant parts)
    # Need to adapt the main callback logic or create specific chart functions
    print("Note: Test coverage charts will be adapted/simplified.")
except ImportError as e:
    print(f"Warning: Could not import from test_coverage. Test coverage charts unavailable. Error: {e}")


# --- Global Constants & Styles ---
REFRESH_INTERVAL = 60 * 60 * 1000 # Refresh data every hour (example)
CHART_BG_COLOR = 'rgba(0, 0, 0, 0)' # Transparent background for charts
FONT_COLOR = 'white'
GRID_COLOR = 'rgba(100, 100, 100, 0.5)'

# Default empty figure
def create_empty_figure(message="Loading...", height=300):
    fig = go.Figure()
    fig.update_layout(
        height=height,
        xaxis={"visible": False}, yaxis={"visible": False},
        annotations=[{"text": message, "xref": "paper", "yref": "paper", "showarrow": False, "font": {"size": 16, "color": FONT_COLOR}}],
        plot_bgcolor=CHART_BG_COLOR,
        paper_bgcolor=CHART_BG_COLOR
    )
    return fig

# --- Data Loading ---
print("Loading data...")
try:
    ddf = load_defect_data("defect/2025*.json") # Load defect data
    tdf = load_test_data() # Load test data
    print(f"Data loaded. Defects: {len(ddf)}, Tests: {len(tdf)}")
    if ddf.empty: print("Warning: Defect data is empty!")
    if tdf.empty: print("Warning: Test data is empty!")
except Exception as e:
    print(f"Error loading data: {e}")
    ddf = pd.DataFrame()
    tdf = pd.DataFrame()


# --- Prepare Data for Map (Adapted from defect_map_dashboard.py) ---
# This needs simplification or pre-calculation if animation is too complex for this combined view
# For now, let's just use the initial figure logic
# print("Preparing map data...")
# try:
#     # --- Simplified Map Data Prep ---
#     map_figure = create_initial_figure()
    
#     # 添加北京作为辐射中心（用特殊标记）
#     map_figure.add_trace(go.Scattermapbox(
#         lat=[beijing_location['lat']],
#         lon=[beijing_location['lon']],
#         mode='markers',
#         marker=go.scattermapbox.Marker(
#             size=15,
#             color='red',
#             opacity=0.8,
#             symbol="star"
#         ),
#         text=["北京 (总部)"],
#         hoverinfo='text',
#         name="总部"
#     ))
    
#     # 添加测试人员位置 
#     tester_lats = []
#     tester_lons = []
#     tester_texts = []
#     tester_sizes = []
    
#     for tester, loc in testers_locations.items():
#         if loc['city'] != 'Beijing':  # 排除北京（已作为单独标记）
#             tester_lats.append(loc['lat'])
#             tester_lons.append(loc['lon'])
#             tester_texts.append(f"{loc['city']} - {tester}")
            
#             # 根据缺陷数量设置大小（这里使用模拟数据）
#             # 实际应用时应该根据每个测试人员的缺陷数量计算
#             defect_count = np.random.randint(5, 20)  # 示例随机数，实际应该根据ddf计算
#             tester_sizes.append(defect_count)
    
#     # 添加测试人员位置
#     if tester_lats:
#         map_figure.add_trace(go.Scattermapbox(
#             lat=tester_lats,
#             lon=tester_lons,
#             mode='markers',
#             marker=go.scattermapbox.Marker(
#                 size=12,
#                 color='cyan',
#                 opacity=0.7
#             ),
#             text=tester_texts,
#             hoverinfo='text',
#             name="测试员"
#         ))
    
#     # 添加测试人员与北京之间的连线
#     for tester, loc in testers_locations.items():
#         if loc['city'] != 'Beijing':  # 排除北京
#             map_figure.add_trace(go.Scattermapbox(
#                 lat=[beijing_location['lat'], loc['lat']],
#                 lon=[beijing_location['lon'], loc['lon']],
#                 mode='lines',
#                 line=dict(width=1, color='rgba(255, 255, 255, 0.5)'),  # 半透明白线
#                 hoverinfo='none',
#                 showlegend=False
#             ))

#     # 更新地图布局为暗色主题 
#     map_figure.update_layout(
#         mapbox=dict(
#             style="carto-positron",  # Changed to light theme for debugging
#             center=dict(lat=30, lon=110),  # 居中显示中国
#             zoom=3,  # 适当的缩放级别
#         ),
#         paper_bgcolor='rgba(240,240,240,1)', # Light background for map
#         plot_bgcolor='rgba(240,240,240,1)',  # Light background for map
#         title=dict(text='缺陷地理分布 (静态)', font=dict(color='black')), # Black text for light map
#         margin={"r": 0, "t": 40, "l": 0, "b": 0},
#         height=400,  # 设置高度适合卡片
#         legend=dict(
#             orientation="h",
#             yanchor="bottom",
#             y=0.02,
#             xanchor="right",
#             x=0.99,
#             font=dict(color='black') # Black legend text for light map
#         )
#         # Removed autosize=True as height is specified
#     )
#     print("Map figure prepared.")
# except Exception as e:
#     print(f"Error preparing map figure: {e}")
#     map_figure = create_empty_figure("Map Error")


# --- Prepare Defect Matrix Figure ---
print("Preparing matrix figure...")
try:
    matrix_figure = create_matrix_figure_flipped(ddf, filtered_by="Overall")
    matrix_figure.update_layout(
        paper_bgcolor=CHART_BG_COLOR,
        plot_bgcolor=CHART_BG_COLOR,
        font=dict(color=FONT_COLOR),
        title=dict(text='缺陷矩阵分布', font=dict(color=FONT_COLOR)),
        height=400 # Added height
        # autosize=True # Removed autosize
    )
    print("Matrix figure prepared.")
except Exception as e:
    print(f"Error preparing matrix figure: {e}")
    matrix_figure = create_empty_figure("Matrix Error", height=300)

# --- Prepare Complexity Trend Figure ---
print("Preparing complexity trend figure...")
try:
    # Note: This function might be slow if history files are many/large
    complexity_fig, complexity_data = create_complexity_trend_figure_and_data(defect_data_pattern="defect/2025*.json", history_folder="history")
    if complexity_fig:
        complexity_fig.update_layout(
            paper_bgcolor=CHART_BG_COLOR,
            plot_bgcolor=CHART_BG_COLOR,
            font=dict(color=FONT_COLOR),
            legend=dict(font=dict(color=FONT_COLOR)),
            xaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, zerolinecolor=GRID_COLOR, tickfont=dict(color=FONT_COLOR), title_font=dict(color=FONT_COLOR)),
            yaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, zerolinecolor=GRID_COLOR, tickfont=dict(color=FONT_COLOR), title_font=dict(color=FONT_COLOR)),
            title=dict(text='缺陷复杂度趋势', font=dict(color=FONT_COLOR)),
            height=400 # Added height
            # autosize=True # Removed autosize
        )
        print("Complexity trend figure prepared.")
    else:
        raise ValueError("Complexity figure creation returned None")
except Exception as e:
    print(f"Error preparing complexity trend figure: {e}")
    complexity_fig = create_empty_figure("Complexity Trend Error", height=300)


# --- Prepare Test Coverage Figure (Example: AIDA vs Week) ---
print("Preparing test coverage figure (AIDA vs Week)...")
try:
    # Simplified adaptation of test_coverage chart 2 logic
    if tdf.empty or 'top_aida' not in tdf.columns:
        test_coverage_fig = create_empty_figure("Test Data Missing")
    else:
        count_col_test = 'id' if 'id' in tdf.columns else None # Assuming 'id' is the MR ID
        if count_col_test:
            grouped_data_test = tdf.groupby(
                ["test_week", "top_aida", "run_status"], as_index=False
            )[count_col_test].nunique().rename(columns={count_col_test: 'count'})

            extract_pattern_test = r'(\d{2})-CW(\d{2})'
            valid_week_mask_test = grouped_data_test['test_week'].astype(str).str.match(extract_pattern_test)
            grouped_data_test = grouped_data_test[valid_week_mask_test.fillna(False)]

            if grouped_data_test.empty:
                test_coverage_fig = create_empty_figure("No Valid Test Weeks")
            else:
                # Sorting logic (simplified for integration)
                grouped_data_test = grouped_data_test.sort_values(["test_week", "top_aida"])
                sorted_weeks_test = grouped_data_test['test_week'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique()
                sorted_aidas_test = sorted(grouped_data_test['top_aida'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique())

                test_coverage_fig = px.scatter(
                    grouped_data_test, x='test_week', y='top_aida', color='run_status', size='count',
                    size_max=20, # Smaller bubbles for dashboard
                    opacity=0.8,
                    labels={'count': '测试数量', 'top_aida': 'Top AIDA', 'test_week': '测试周', 'run_status': '状态'},
                    color_discrete_map={"Passed": "#2ca02c", "Failed": "#d62728", "Requires Attention": "#ff7f0e", "Planned": "#cccccc"}, # Use defined colors
                    category_orders={'test_week': list(sorted_weeks_test), 'top_aida': list(sorted_aidas_test)}
                )
                test_coverage_fig.update_layout(
                    paper_bgcolor=CHART_BG_COLOR,
                    plot_bgcolor=CHART_BG_COLOR,
                    font=dict(color=FONT_COLOR),
                    legend=dict(font=dict(color=FONT_COLOR)),
                    xaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, zerolinecolor=GRID_COLOR, tickfont=dict(color=FONT_COLOR), title_font=dict(color=FONT_COLOR), tickangle=-45),
                    yaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, zerolinecolor=GRID_COLOR, tickfont=dict(color=FONT_COLOR), title_font=dict(color=FONT_COLOR)),
                    title=dict(text='测试覆盖率 (AIDA vs 周)', font=dict(color=FONT_COLOR)),
                    height=400 # Added height
                    # autosize=True # Removed autosize
                )
                test_coverage_fig.update_traces(marker=dict(sizemode='area', line_width=1, line_color='grey'))
                print("Test coverage figure prepared.")
        else:
            test_coverage_fig = create_empty_figure("Missing Count Column in Test Data")
except Exception as e:
    print(f"Error preparing test coverage figure: {e}")
    test_coverage_fig = create_empty_figure("Test Coverage Error", height=300)

# --- Prepare Word Cloud Figure ---
print("Preparing word cloud figure...")
wordcloud_image_src = None
try:
    if not ddf.empty and 'top_aida' in ddf.columns:
        complex_defects = ddf[ddf.get('complexity_category', '简单') == '复杂'] if 'complexity_category' in ddf.columns else ddf # Fallback to all if no complexity
        if not complex_defects.empty:
            text_series = complex_defects['top_aida'].dropna().astype(str)
            text = ' '.join(text_series[text_series != ''].str.lower().tolist())
            if text:
                stopwords_wc = set(STOPWORDS)
                stopwords_wc.update({'tsp', 'cn', 'iuk', 'dips', 'bmw', 'sys', 'mini', 'evo', 'unknown', 'nan'})

                wc = WordCloud(width=400, height=250, background_color=None, mode='RGBA',
                               stopwords=stopwords_wc, collocations=False).generate(text)

                # Save to buffer and encode
                img_buffer = io.BytesIO()
                # Use a color map appropriate for dark backgrounds if needed
                # plt.imshow(wc.recolor(color_func=lambda *args, **kwargs: "cyan"), interpolation="bilinear") # Example recolor
                plt.imshow(wc, interpolation="bilinear")
                plt.axis("off")
                plt.savefig(img_buffer, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
                plt.close() # Close the plot to free memory
                img_buffer.seek(0)
                wordcloud_image_src = 'data:image/png;base64,{}'.format(base64.b64encode(img_buffer.read()).decode())
                print("Word cloud figure prepared.")
            else: print("Warning: No text data for word cloud after filtering.")
        else: print("Warning: No complex defects found for word cloud.")
    else: print("Warning: Defect data empty or missing 'top_aida' for word cloud.")
except Exception as e:
    print(f"Error preparing word cloud: {e}")


# --- Define KPIs (Example) ---
print("Calculating KPIs...")
kpi_total_defects = len(ddf) if not ddf.empty else 0
kpi_severe_defects = 0
if not ddf.empty and 'severity_group' in ddf.columns:
    kpi_severe_defects = len(ddf[ddf['severity_group'] == '严重问题'])
kpi_total_tests = len(tdf) if not tdf.empty else 0
kpi_passed_tests = 0
if not tdf.empty and 'run_status' in tdf.columns:
    kpi_passed_tests = len(tdf[tdf['run_status'] == 'Passed'])
print(f"KPIs: Defects={kpi_total_defects}, Severe={kpi_severe_defects}, Tests={kpi_total_tests}, Passed={kpi_passed_tests}")


# --- Create App Layout ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], assets_folder='assets', suppress_callback_exceptions=True)
app.title = "测试数据大屏"

# Custom CSS for styling closer to the target image
# Create an 'assets' folder in the same directory as your script
# and place a 'dark_theme.css' file inside it.
# Example content for assets/dark_theme.css:
"""
body {
    background-color: #0f172a !important; /* Dark blue background */
    color: #e2e8f0 !important; /* Light text color */
}

.card {
    background-color: rgba(30, 41, 59, 0.7) !important; /* Semi-transparent dark card */
    border: 1px solid #334155 !important; /* Subtle border */
    border-radius: 8px !important;
    margin-bottom: 15px !important; /* Add space between cards */
    height: 100%; /* Make cards fill column height */
}

.card-header {
    background-color: rgba(51, 65, 85, 0.8) !important;
    border-bottom: 1px solid #334155 !important;
    font-weight: bold;
    color: #94a3b8; /* Header text color */
    padding: 0.5rem 1rem; /* Adjust padding */
    font-size: 0.9rem; /* Adjust font size */
}

.card-body {
    padding: 0.75rem; /* Adjust padding */
}

/* Style graph containers */
.dash-graph {
    height: 100%;
}
.plotly {
   height: 100% !important; /* Ensure plotly graph fills container */
}

/* Style KPI cards */
.kpi-card {
    text-align: center;
    padding: 1rem;
}

.kpi-value {
    font-size: 2rem;
    font-weight: bold;
    color: #5eead4; /* Teal color for values */
}

.kpi-label {
    font-size: 0.9rem;
    color: #94a3b8;
    margin-top: 0.25rem;
}

/* Center the main title */
h1.main-title {
    color: #e2e8f0;
    text-align: center;
    margin-top: 20px;
    margin-bottom: 30px;
    font-size: 1.8rem;
    text-shadow: 0 0 5px rgba(94, 234, 212, 0.7); /* Subtle glow effect */
}

/* Style the defect table */
.defect-table {
    font-size: 0.8rem;
}
.defect-table .dash-header {
    background-color: rgba(51, 65, 85, 0.8);
    color: #94a3b8;
    font-weight: bold;
}
.defect-table .dash-cell {
    background-color: rgba(30, 41, 59, 0.7);
    color: #e2e8f0;
    border: 1px solid #334155;
    padding: 5px;
}
.defect-table .dash-cell tr:nth-child(even) {
     background-color: rgba(40, 51, 69, 0.7) !important;
}

/* Word cloud image */
.wordcloud-container img {
    display: block;
    margin-left: auto;
    margin-right: auto;
    max-width: 100%;
    height: auto;
}
"""


# --- Layout Definition ---
app.layout = dbc.Container(fluid=True, style={'padding': '15px'}, children=[
    dbc.Row([
        dbc.Col(html.H1("测试数据大屏", className="main-title"))
    ]),

    dbc.Row([
        # --- Left Column ---
        dbc.Col(md=3, children=[
            dbc.Card([
                dbc.CardHeader("测试执行 KPI (示例)"),
                dbc.CardBody(className="kpi-card", children=[
                    dbc.Row([
                        dbc.Col([
                            html.Div(f"{kpi_total_tests:,}", className="kpi-value"),
                            html.Div("总执行数", className="kpi-label")
                        ]),
                        dbc.Col([
                            html.Div(f"{kpi_passed_tests:,}", className="kpi-value"),
                            html.Div("通过数", className="kpi-label")
                        ]),
                    ]),
                     html.Div(f"{kpi_total_tests - kpi_passed_tests:,}", className="kpi-value", style={'marginTop':'10px'}),
                    html.Div("失败/阻塞数", className="kpi-label")
                ])
            ]),
            dbc.Card([
                dbc.CardHeader("测试覆盖率 (AIDA vs 周)"), # Placeholder Title 1
                dbc.CardBody(dcc.Graph(id='test-coverage-chart', figure=test_coverage_fig))
            ]),
             dbc.Card([
                dbc.CardHeader("测试通过率趋势 (占位符)"), # Placeholder Title 2
                dbc.CardBody(dcc.Graph(figure=create_empty_figure("通过率趋势待开发")))
            ]),
            dbc.Card([
                dbc.CardHeader("测试阻塞看板 (占位符)"), # Placeholder Title 3
                dbc.CardBody(dcc.Graph(figure=create_empty_figure("阻塞看板待开发")))
            ]),
        ]),

        # --- Center Column ---
        dbc.Col(md=6, children=[
            # dbc.Card([
            #     dbc.CardHeader("缺陷地理分布"),
            #     dbc.CardBody(dcc.Graph(id='defect-map', figure=map_figure))
            # ]),
            dbc.Card([
                dbc.CardHeader("实时缺陷信息 (示例)"),
                dbc.CardBody(
                    dash_table.DataTable(
                        id='defect-detail-table',
                        columns=[{"name": i, "id": i} for i in ddf[['id', 'name', 'status_phase', 'tester', 'severity_group']].columns] if not ddf.empty else [{"name":"No Data", "id":"No Data"}],
                        data=ddf[['id', 'name', 'status_phase', 'tester', 'severity_group']].head(10).to_dict('records') if not ddf.empty else [],
                        page_size=5,
                        style_table={'overflowY': 'auto', 'height': '200px'}, # Limit height and make scrollable
                        style_as_list_view=True, # Remove cell borders
                        # Dark theme styles for table
                        style_header={'backgroundColor': 'rgba(51, 65, 85, 0.8)', 'color': '#94a3b8', 'fontWeight': 'bold', 'border': 'none'},
                        style_data={'backgroundColor': 'transparent', 'color': '#e2e8f0', 'border': 'none'},
                        style_cell={'textAlign': 'left', 'padding': '5px', 'border': 'none'},
                    ),
                    className="defect-table" # Apply custom class if needed
                )
            ]),
        ]),

        # --- Right Column ---
        dbc.Col(md=3, children=[
            dbc.Card([
                dbc.CardHeader("缺陷 KPI (示例)"),
                 dbc.CardBody(className="kpi-card", children=[
                    dbc.Row([
                        dbc.Col([
                            html.Div(f"{kpi_total_defects:,}", className="kpi-value"),
                            html.Div("总缺陷数", className="kpi-label")
                        ]),
                        dbc.Col([
                            html.Div(f"{kpi_severe_defects:,}", className="kpi-value", style={'color': '#f87171'}), # Red color for severe
                            html.Div("严重缺陷", className="kpi-label")
                        ]),
                    ])
                ])
            ]),
            dbc.Card([
                dbc.CardHeader("缺陷矩阵分布"),
                dbc.CardBody(dcc.Graph(id='defect-matrix-chart', figure=matrix_figure))
            ]),
            dbc.Card([
                dbc.CardHeader("缺陷复杂度趋势"),
                dbc.CardBody(dcc.Graph(id='complexity-trend-chart', figure=complexity_fig))
            ]),
            dbc.Card([
                dbc.CardHeader("高复杂度缺陷词云"),
                dbc.CardBody(
                    html.Img(src=wordcloud_image_src, style={'maxWidth': '100%', 'maxHeight': '330px', 'height': 'auto', 'display': 'block', 'margin': 'auto'}) if wordcloud_image_src else html.P("无法生成词云"),
                    className="wordcloud-container", # Center image if needed via CSS
                    style={'height': '400px', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}
                )
            ]),
        ]),
    ])
])


# --- Run App ---
if __name__ == '__main__':
    print("Starting dashboard server...")
    # Make sure 'assets' folder exists in the same directory
    # Run on 0.0.0.0 to make it accessible on the network if needed
    app.run(debug=True, port=8061, host='0.0.0.0')