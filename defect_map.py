import dash
from dash import dcc, html, Input, Output, callback, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import warnings
import json
import dash_bootstrap_components as dbc
import os

# 忽略特定警告
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# 从 data_processor 导入数据加载函数
try:
    from data_processor import load_defect_data, SEVERITY_COLORS
except ImportError:
    print("警告: 无法从 data_processor 导入，将使用备用逻辑。")
    def load_defect_data(): return pd.DataFrame(columns=['id', 'name', 'tester', 'status_phase', 'domain', 'tproject', 'creation_time', 'severity_group'])
    SEVERITY_COLORS = {'严重问题': '#ff4d4d', '一般问题': '#4dff4d', 'Unknown': '#cccccc'}

# 设置一个可用的 Mapbox 公共令牌 (如果没有设置的话)
if not os.environ.get('MAPBOX_ACCESS_TOKEN'):
    os.environ['MAPBOX_ACCESS_TOKEN'] = 'pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A'

# 创建初始地图图形
def create_initial_figure():
    """创建一个以中国为中心的初始地图图形"""
    fig = go.Figure()
    fig.update_layout(
        mapbox_style="carto-darkmatter",
        mapbox=dict(
            center=dict(lat=36, lon=103),  # 中国中心位置
            zoom=2.8,
            pitch=0
        ),
        margin={"r":0,"t":30,"l":0,"b":0},
        height=650,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig

# 创建 Dash 应用
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    assets_folder='assets',
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}]
)

# --- 数据加载和预处理 ---
try:
    raw_df = load_defect_data()
    if raw_df.empty: print("警告: 缺陷数据为空。")
except Exception as e:
    print(f"错误: 加载缺陷数据失败: {e}")
    raw_df = pd.DataFrame(columns=['id', 'name', 'tester', 'status_phase', 'domain', 'tproject', 'creation_time', 'severity_group'])

# 定义测试人员位置
testers_locations = {
    'Felipe Wu': {'city': 'Taipei', 'lat': 25.0330, 'lon': 121.5654, 'country': 'China'},
    'Adley Wong': {'city': 'Hong Kong', 'lat': 22.3193, 'lon': 114.1694, 'country': 'Hong Kong'},
    'Vito Wang': {'city': 'Nanjing', 'lat': 32.0603, 'lon': 118.7969, 'country': 'China'},
    'Linna Li': {'city': 'Nanjing', 'lat': 32.0603, 'lon': 118.7969, 'country': 'China'},
    # 为展示需要，手动加入澳门位置（若数据未出现也能显示）
    'Dummy Macau': {'city': 'Macau', 'lat': 22.1987, 'lon': 113.5439, 'country': 'Macau'},
}
# 将北京位置单独存储，作为辐射中心
beijing_location = {'city': 'Beijing', 'lat': 39.9042, 'lon': 116.4074, 'country': 'China'}
# 其他目标城市
target_locations = {name: loc for name, loc in testers_locations.items() if loc['city'] != 'Beijing'} # 排除北京自身

def get_location_info(tester_name):
    # 使用 testers_locations 或 beijing_location 获取基础位置
    location = testers_locations.get(tester_name, beijing_location) # 如果找不到特定测试员，默认为北京
    # 添加抖动，但确保北京自身不抖动或抖动很小，如果需要的话
    lat_jitter, lon_jitter = np.random.normal(0, 0.02, 2)
    return pd.Series([location['city'], location['country'], location['lat'] + lat_jitter, location['lon'] + lon_jitter])

# 应用位置信息
if not raw_df.empty and 'tester' in raw_df.columns:
    location_df = raw_df['tester'].apply(get_location_info)
    location_df.columns = ['city', 'country', 'latitude', 'longitude']
    df = pd.concat([raw_df, location_df], axis=1).fillna('Unknown')
else:
    df = pd.DataFrame(columns=list(raw_df.columns) + ['city', 'country', 'latitude', 'longitude'])

# 确保关键列存在
def ensure_columns(dataframe, required_cols):
    for col in required_cols:
        if col not in dataframe.columns:
            print(f"警告: 列 '{col}' 不存在，将添加为 NA。")
            dataframe[col] = pd.NA
    return dataframe

df = ensure_columns(df, ['id', 'name', 'tester', 'status_phase', 'domain', 'tproject',
                         'creation_time', 'severity_group', 'city', 'country',
                         'latitude', 'longitude'])

# 转换时间并处理错误
valid_time_column = False
if 'creation_time' in df.columns:
    df['creation_time'] = pd.to_datetime(df['creation_time'], errors='coerce')
    original_count = len(df)
    df = df.dropna(subset=['creation_time'])
    if len(df) < original_count: print(f"警告: 移除了 {original_count - len(df)} 行因无效的 'creation_time'。")
    if not df.empty: valid_time_column = True
else: print("警告: 缺少 'creation_time' 列。"); df['creation_time'] = pd.NaT

# 如果 severity_group 不存在，则创建一个默认列
if 'severity_group' not in df.columns:
    df['severity_group'] = '一般问题'

# 为城市定义颜色
CITY_COLORS = {
    'Beijing': '#aec7e8',   # 浅蓝
    'Nanjing': '#98df8a',   # 浅绿
    'Hong Kong': '#ffbb78', # 浅橙
    'Taipei': '#ff9896',    # 浅红
    'Macau': '#f7b6d2',    # 粉色
    'Unknown': '#cccccc'     # 灰色 (备用)
}

# 需要重点突出的城市（会放大气泡）
HIGHLIGHT_CITIES = ['Beijing', 'Nanjing', 'Hong Kong', 'Macau', 'Taipei']

# --- 准备动画数据 (2025 Weekly Defects) ---
animation_df = pd.DataFrame()

if valid_time_column:
    df_2025 = df[df['creation_time'].dt.year == 2025].copy()
    if not df_2025.empty:
        # 处理周数据
        df_2025['week_number'] = df_2025['creation_time'].dt.isocalendar().week
        df_2025['week_display'] = df_2025['week_number'].apply(lambda w: f"2025-W{w:02d}")
        weekly_counts = df_2025.groupby(['city', 'week_number', 'week_display']).size().reset_index(name='weekly_count')

        # 获取所有需要绘制位置的城市 (北京 + 其他测试城市)
        all_plot_cities_dict = {beijing_location['city']: beijing_location}
        for loc in testers_locations.values():
            all_plot_cities_dict[loc['city']] = loc
        all_plot_cities = list(all_plot_cities_dict.keys())

        # 只展示重点城市（即使数据未出现，也要展示）
        all_cities_for_animation = [c for c in HIGHLIGHT_CITIES if c in all_plot_cities]
        
        max_week = df_2025['week_number'].max() if not df_2025['week_number'].empty else 0
        all_weeks = range(1, int(max_week) + 1) if pd.notna(max_week) and max_week > 0 else []

        if all_cities_for_animation and all_weeks:
            # 创建每周每城市的组合
            mux = pd.MultiIndex.from_product([all_cities_for_animation, all_weeks], names=['city', 'week_number'])
            all_combinations = pd.DataFrame(index=mux).reset_index()
            all_combinations['week_display'] = all_combinations['week_number'].apply(lambda w: f"2025-W{w:02d}")

            # 合并每周计数数据
            animation_df = pd.merge(all_combinations, weekly_counts[['city', 'week_number', 'weekly_count']],
                                    on=['city', 'week_number'], how='left').fillna({'weekly_count': 0})
            animation_df = animation_df.sort_values(by=['week_number', 'city'])

            # 聚合城市位置信息
            city_info = df_2025.groupby('city').agg(
                latitude=('latitude', 'mean'), longitude=('longitude', 'mean'), country=('country', 'first')
            ).reset_index()
            city_info['latitude'] = pd.to_numeric(city_info['latitude'], errors='coerce')
            city_info['longitude'] = pd.to_numeric(city_info['longitude'], errors='coerce')
            city_info = city_info.dropna(subset=['latitude', 'longitude'])

            # 对于缺失的重点城市（可能 2025 年无缺陷记录），强制补充位置信息
            missing_cities = [c for c in all_cities_for_animation if c not in city_info['city'].values]
            if missing_cities:
                supplement_rows = []
                for mc in missing_cities:
                    # 优先 testers_locations 获取，否则跳过
                    loc = next((v for v in testers_locations.values() if v['city'] == mc), None)
                    if loc:
                        supplement_rows.append({'city': mc, 'latitude': loc['lat'], 'longitude': loc['lon'], 'country': loc.get('country', 'Unknown')})
                if supplement_rows:
                    city_info = pd.concat([city_info, pd.DataFrame(supplement_rows)], ignore_index=True)

            # 合并位置信息
            animation_df = pd.merge(animation_df, city_info, on='city', how='left')
            
            # 添加颜色和大小信息
            animation_df['color'] = animation_df['city'].map(CITY_COLORS).fillna(CITY_COLORS['Unknown'])
            # 调整放大系数，使得气泡更易分辨
            base_scaling_factor = 10  # 原值为 6
            animation_df['scaled_size'] = animation_df['weekly_count'] * base_scaling_factor
            animation_df['scaled_size'] = animation_df['scaled_size'].apply(lambda x: max(x, 8))
            # 如果是需要重点显示的城市，再放大 2 倍
            animation_df.loc[animation_df['city'].isin(HIGHLIGHT_CITIES), 'scaled_size'] *= 2.0

            # 确保所有必要列没有缺失值
            final_required_cols = ['latitude', 'longitude', 'city', 'week_display', 'color', 'scaled_size', 'country', 'weekly_count']
            animation_df = animation_df.dropna(subset=final_required_cols)

# --- 应用布局 ---
app.layout = dbc.Container(fluid=True, className="dark-theme-container", children=[
    dbc.Row([
        dbc.Col(html.H1("团队缺陷发现地理分布图", 
                        style={'textAlign': 'center', 'color': '#E0E0E0', 'marginBottom': '20px',
                               'textShadow': '2px 2px 4px #000000'}), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="loading-map",
                type="default", # 使用 "default" (或 "circle", "cube" 等)
                children=[
                    dcc.Graph(id='defect-map', figure=create_initial_figure()),
                    dcc.Store(id='current-week-store', data=None) # 存储当前周
                ]
            )
        ], width=12)
    ]),
    html.Div(id='map-status-message', style={'textAlign': 'center', 'marginTop': '10px', 'color': '#FFD700'})
])

# --- 回调函数 ---
@callback(
    Output('current-week-store', 'data'),
    Input('defect-map', 'relayoutData'),
    State('current-week-store', 'data')
)
def update_current_week(relayout_data, current_week):
    """根据地图缩放和平移更新当前周（非动画控制，仅用于交互触发）"""
    # 仅在用户交互时触发（如缩放/平移，虽然当前配置为固定视角）
    if relayout_data is not None and 'mapbox.zoom' in relayout_data:
        # 这里可以添加逻辑，例如在特定交互后重置或改变动画状态，但目前保持不变
        return dash.no_update
    return dash.no_update # 保持周状态不变，让动画自行控制

@callback(
    Output('defect-map', 'figure'),
    Input('current-week-store', 'data')
)
def update_animated_map(current_week):
    """更新地图动画帧"""
    # 确保 animation_df 准备就绪
    if animation_df.empty or not valid_time_column or not all_weeks:
        return create_initial_figure().update_layout(title_text="数据不足，无法生成动画")

    # 创建动画的 Figure 对象
    fig = px.scatter_mapbox(
        animation_df,
        lat="latitude",
        lon="longitude",
        size="scaled_size",
        color="color",
        animation_frame="week_display",
        animation_group="city",
        mapbox_style="carto-darkmatter",
        hover_name="city",
        hover_data={
            "country": True,
            "weekly_count": True,
            "latitude": False,  # 不显示经纬度
            "longitude": False,
            "color": False, # 不显示颜色代码
            "scaled_size": False # 不显示缩放后的大小
        },
        custom_data=['city', 'weekly_count'], # 用于自定义悬停信息
        category_orders={"week_display": sorted(animation_df['week_display'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique())}
    )
    
    fig.update_traces(
        marker=dict(opacity=0.8, sizemin=4), # 设置最小尺寸和透明度
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "周新增缺陷: %{customdata[1]}<br>"
            "<extra></extra>" # 移除默认的跟踪信息
        )
    )

    # 添加北京和其他主要城市作为静态点（背景）
    static_cities_data = []
    for name, loc in testers_locations.items():
        if loc['city'] not in [beijing_location['city']]: # 排除北京，因为它会单独添加
            static_cities_data.append({
                'lat': loc['lat'], 'lon': loc['lon'], 'city': loc['city'],
                'color': CITY_COLORS.get(loc['city'], CITY_COLORS['Unknown'])
            })
    # 添加北京
    static_cities_data.append({
        'lat': beijing_location['lat'], 'lon': beijing_location['lon'], 'city': beijing_location['city'],
        'color': CITY_COLORS.get(beijing_location['city'], CITY_COLORS['Unknown'])
    })
    
    static_cities_df = pd.DataFrame(static_cities_data)
    
    fig.add_trace(go.Scattermapbox(
        lat=static_cities_df['lat'],
        lon=static_cities_df['lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10, # 静态点的大小
            color=static_cities_df['color'],
            opacity=0.5
        ),
        text=static_cities_df['city'],
        hoverinfo='text',
        name='主要城市'
    ))
    
    # 动态添加从北京到其他城市的连线 (仅对第一帧或静态图有效，动画时可能不理想)
    # 如果需要随动画变化，此逻辑需要移入动画帧的生成中
    # for name, loc in target_locations.items():
    #     fig.add_trace(go.Scattermapbox(
    #         mode = "lines",
    #         lon = [beijing_location['lon'], loc['lon']],
    #         lat = [beijing_location['lat'], loc['lat']],
    #         line = dict(width = 1, color = 'rgba(255, 255, 255, 0.3)'),
    #         hoverinfo='none'
    #     ))

    # 设置地图布局
    fig.update_layout(
        mapbox=dict(
            center=dict(lat=36, lon=103), # 中国中心
            zoom=2.8,
            pitch=0,
            style="carto-darkmatter"
        ),
        margin={"r":0,"t":40,"l":0,"b":0},
        height=650,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, font=dict(color="#E0E0E0")), # 图例样式
        title=dict(text="2025年每周缺陷地理分布变化 (动画)", font=dict(color="#E0E0E0", size=16), x=0.5, y=0.98), # 标题样式
        # 动画播放器样式
        sliders=[dict(
            active=0,
            currentvalue={"prefix": "当前周: ", "font": {"color": "#FFD700"}},
            pad={"t": 20, "b":10},
            font={"color": "#E0E0E0"}
        )],
        updatemenus=[dict(
            type='buttons',
            showactive=False,
            buttons=[dict(
                label='播放',
                method='animate',
                args=[None, dict(frame=dict(duration=500, redraw=True), fromcurrent=True, mode='immediate')]
            ), dict(
                label='暂停',
                method='animate',
                args=[[None], dict(frame=dict(duration=0, redraw=False), mode='immediate')]
            )],
            direction='left',
            pad={"r": 10, "t": 30},
            x=0.1, xanchor='right', y=0, yanchor='top',
            bgcolor='rgba(50,50,50,0.7)', 
            bordercolor='#E0E0E0', 
            font={"color": "#E0E0E0"}
        )]
    )
    return fig

# 启动应用
if __name__ == '__main__':
    app.run(debug=True, port=8054) # 端口可自定义