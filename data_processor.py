import os

# 默认关闭 reloader/hot reload，避免运行时文件写入触发服务重载
DISABLE_RELOADER = os.environ.get("DISABLE_RELOADER", "1").lower() in ("1", "true", "yes")

# 检查是否为 reloader 父进程：仅在启用 reloader 时才成立
IS_RELOADER = (not DISABLE_RELOADER) and (os.environ.get("WERKZEUG_RUN_MAIN") != "true")

if not IS_RELOADER:
    import json
    import re
    import sqlite3
    import numpy as np
    import pandas as pd
    import glob
    from datetime import datetime, timedelta
    from dash_common_styles import theme_manager, apply_light_theme_to_figure, apply_dark_theme_to_figure
    import plotly.graph_objects as go
    import warnings
    import math  # 导入数学函数库用于非线性计算
    from functools import lru_cache
    import concurrent.futures
    from typing import Dict, Optional, List

    # 导入数据库相关配置和工具
    try:
        from db_migration_config import DB_PATH, DEFAULT_TEAM, is_using_optimized_schema, is_db_first_mode, is_db_only_mode
        from database_utils import with_db_retry, get_db_connection
        HAS_DB_CONFIG = True
    except ImportError:
        HAS_DB_CONFIG = False
    try:
        from unified_data_loader import UnifiedDataLoader, DataSourceConfig
        HAS_UNIFIED_LOADER = True
    except ImportError:
        HAS_UNIFIED_LOADER = False
else:
    # Reloader进程的占位符导入
    print("🔄 data_processor: Reloader进程跳过重度导入")
    import json
    import sqlite3
    import pandas as pd
    from typing import Dict, Optional, List
    HAS_DB_CONFIG = False
    HAS_UNIFIED_LOADER = False

# ===== 历史数据缓存管理 =====

class HistoryCache:
    """历史数据缓存管理器"""
    
    def __init__(self, cache_size=1000):
        self._cache = {}
        self._cache_size = cache_size
        self._access_order = []
    
    def get(self, defect_id: str) -> Optional[Dict]:
        """获取缓存的历史数据"""
        if defect_id in self._cache:
            # 更新访问顺序
            self._access_order.remove(defect_id)
            self._access_order.append(defect_id)
            return self._cache[defect_id]
        return None
    
    def set(self, defect_id: str, data: Dict):
        """设置缓存数据"""
        # 如果缓存已满，删除最久未访问的项
        if len(self._cache) >= self._cache_size and defect_id not in self._cache:
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key]
        
        self._cache[defect_id] = data
        if defect_id in self._access_order:
            self._access_order.remove(defect_id)
        self._access_order.append(defect_id)
    
    def clear(self):
        """清空缓存"""
        self._cache.clear()
        self._access_order.clear()
    
    def preload_histories(self, defect_ids: List[str], history_dir: str = "history", max_workers: int = 10):
        """批量预加载历史数据"""
        print(f"开始预加载 {len(defect_ids)} 个历史文件...")
        
        def load_single_history(defect_id):
            try:
                history_data = get_history_data(defect_id, history_dir)
                if not history_data:
                    return None
                return defect_id, history_data
            except Exception as e:
                print(f"预加载历史文件失败 {defect_id}: {e}")
                return None
        
        loaded_count = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_id = {executor.submit(load_single_history, defect_id): defect_id 
                           for defect_id in defect_ids if self.get(defect_id) is None}
            
            for future in concurrent.futures.as_completed(future_to_id):
                result = future.result()
                if result and len(result) == 2:
                    defect_id, history_data = result
                    self.set(defect_id, history_data)
                    loaded_count += 1
        
        print(f"预加载完成，成功加载 {loaded_count} 个历史文件")

# 全局历史缓存实例
history_cache = HistoryCache(cache_size=2000)

_DEFAULT_OCTANE_DB_PATH = os.environ.get("OCTANE_DB_PATH", os.path.join("database", "local_data.db"))
_DEFAULT_OCTANE_TEAM = os.environ.get("OCTANE_TEAM", "DTSV_China")
_DEFAULT_HISTORY_ALLOW_FILE_FALLBACK = os.environ.get("OCTANE_HISTORY_ALLOW_FILE_FALLBACK", "0").lower() in ("1", "true", "yes")


def _load_history_from_db(defect_id: str, db_path: str) -> Optional[Dict]:
    if not db_path or not os.path.exists(db_path):
        return None
    try:
        conn = sqlite3.connect(db_path)
        try:
            row = conn.execute(
                "SELECT payload_json FROM octane_defect_histories WHERE defect_id = ?",
                (str(defect_id),),
            ).fetchone()
            if not row:
                return None
            return json.loads(row[0])
        finally:
            conn.close()
    except Exception:
        return None


def get_history_data(defect_id: str, history_dir: str = "history", db_path: Optional[str] = None) -> Optional[Dict]:
    """获取历史数据，使用缓存优化"""
    # 先从缓存获取
    cached_data = history_cache.get(defect_id)
    if cached_data is not None:
        return cached_data
    
    db_path_val = db_path or _DEFAULT_OCTANE_DB_PATH
    history_data_db = _load_history_from_db(defect_id, db_path_val)
    if history_data_db is not None:
        history_cache.set(defect_id, history_data_db)
        return history_data_db
    return None


def _iter_histories_from_db(db_path: Optional[str] = None):
    db_path_val = db_path or _DEFAULT_OCTANE_DB_PATH
    if not db_path_val or not os.path.exists(db_path_val):
        return
    try:
        conn = sqlite3.connect(db_path_val)
        try:
            rows = conn.execute("SELECT defect_id, payload_json FROM octane_defect_histories").fetchall()
        finally:
            conn.close()
        for defect_id, payload_json in rows:
            if payload_json is None:
                continue
            try:
                payload = json.loads(payload_json)
            except Exception:
                continue
            yield str(defect_id), payload
    except Exception:
        return

# ===== 通用工具函数 =====

def make_ticket_link(ticket_id):
    """将票据ID转换为超链接格式"""
    if pd.isna(ticket_id) or not str(ticket_id).strip():
        return ""
    
    ticket_id_str = str(ticket_id).strip()
    url = f"https://octane-prod.bmwgroup.net/ui/entity-navigation?p=1002/2001&entityType=work_item&id={ticket_id_str}"
    return f"[{ticket_id_str}]({url})"


def extract_english(text):
    """从文本中提取英文单词，如果为空或无法提取则返回'Unknown'"""
    if pd.isna(text) or text == '':
        return 'Unknown'
    # 查找所有连续的英文字母
    english_words = re.findall(r'[a-zA-Z]+', str(text))
    # 如果找到英文单词，则用空格连接，否则返回'Unknown'
    return ' '.join(english_words) if english_words else 'Unknown'

def load_vin_project_mapping(excel_file="project/vin_project_mapping.xlsx"):
    try:
        if not os.path.exists(excel_file):
            return {}, {}
        df_mapping = pd.read_excel(excel_file)
        if 'VIN' not in df_mapping.columns or 'project' not in df_mapping.columns:
            return {}, {}
        project_name_mapping = {
            'MGU_02_A': 'IDC',
            'MGU_02_L': 'MGU',
            'IDCEVO25': 'IDCEVO'
        }
        vin_to_project = {}
        vin_to_market = {}
        for _, row in df_mapping.iterrows():
            vin = str(row['VIN']).strip().upper()
            hu_name = str(row['project']).strip()
            project = project_name_mapping.get(hu_name, hu_name)
            vin_to_project[vin] = project
            if 'ISO Countrycode (INT)' in df_mapping.columns:
                iso_country = str(row['ISO Countrycode (INT)']).strip() if pd.notna(row['ISO Countrycode (INT)']) else ''
                if iso_country:
                    vin_to_market[vin] = iso_country
        return vin_to_project, vin_to_market
    except Exception:
        return {}, {}

def apply_vin_project_mapping(df, excel_file="project/vin_project_mapping.xlsx"):
    if df is None or df.empty:
        return df
    vin_col = None
    if 'vin' in df.columns:
        vin_col = 'vin'
    elif 'vin_udf' in df.columns:
        vin_col = 'vin_udf'
    if not vin_col:
        if 'project' not in df.columns:
            df['project'] = 'Unknown'
        if 'market' not in df.columns:
            df['market'] = 'Unknown'
        return df
    try:
        df[vin_col] = df[vin_col].astype(str).str.strip().str.upper()
    except Exception:
        pass
    vin_to_project, vin_to_market = load_vin_project_mapping(excel_file=excel_file)
    if 'project' not in df.columns:
        df['project'] = 'Unknown'
    if 'market' not in df.columns:
        df['market'] = 'Unknown'
    if vin_to_project:
        def _map_project(vin_val):
            if not isinstance(vin_val, str):
                return 'Unknown'
            projects = [vin_to_project.get(v.strip(), '') for v in vin_val.split(',') if v.strip() in vin_to_project]
            return ', '.join([p for p in projects if p]) or 'Unknown'
        df['project'] = df[vin_col].map(_map_project)
    if vin_to_market:
        def _map_market(vin_val):
            if not isinstance(vin_val, str):
                return 'Unknown'
            markets = [vin_to_market.get(v.strip(), '') for v in vin_val.split(',') if v.strip() in vin_to_market]
            return ', '.join([m for m in markets if m]) or 'Unknown'
        df['market'] = df[vin_col].map(_map_market)
    else:
        df['market'] = 'Unknown'
    return df

def load_app_rsu_mapping(excel_file="aida/top_aida_project_fv_mapping.xlsx"):
    try:
        if not os.path.exists(excel_file):
            return {'app': [], 'rsu': []}
        app_df = pd.read_excel(excel_file, sheet_name='App')
        rsu_df = pd.read_excel(excel_file, sheet_name='RSU')
        app_top_aidas = app_df['top_aida'].dropna().apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique().tolist() if 'top_aida' in app_df.columns else []
        rsu_top_aidas = rsu_df['top_aida'].dropna().apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique().tolist() if 'top_aida' in rsu_df.columns else []
        return {'app': app_top_aidas, 'rsu': rsu_top_aidas}
    except Exception:
        return {'app': [], 'rsu': []}

def apply_app_rsu_project_override(df, excel_file="aida/top_aida_project_fv_mapping.xlsx"):
    if df is None or df.empty:
        return df
    if 'top_aida' not in df.columns:
        return df
    if 'project' not in df.columns:
        df['project'] = 'Unknown'
    mapping = load_app_rsu_mapping(excel_file=excel_file)
    app_top_aidas = mapping.get('app', []) or []
    rsu_top_aidas = mapping.get('rsu', []) or []
    if app_top_aidas:
        app_mask = df['top_aida'].isin(app_top_aidas)
        df.loc[app_mask, 'project'] = 'App'
    if rsu_top_aidas:
        rsu_mask = df['top_aida'].isin(rsu_top_aidas)
        df.loc[rsu_mask, 'project'] = 'RSU'
    return df

def _get_file_mtime(path: str) -> float:
    try:
        return os.path.getmtime(path) if os.path.exists(path) else 0.0
    except Exception:
        return 0.0

@lru_cache(maxsize=8)
def _load_top_aida_fv_mapping(excel_file: str, mtime: float):
    mapping = {}
    if not os.path.exists(excel_file):
        return mapping
    try:
        writer = pd.ExcelFile(excel_file)
        for sheet_name in writer.sheet_names:
            try:
                df_map = pd.read_excel(excel_file, sheet_name=sheet_name)
            except Exception:
                continue
            if 'top_aida' not in df_map.columns or 'fv' not in df_map.columns:
                continue
            for _, row in df_map[['top_aida', 'fv']].dropna().iterrows():
                key = str(row['top_aida']).strip()
                val = str(row['fv']).strip()
                if key and val and val.lower() != 'nan' and key not in mapping:
                    mapping[key] = val
    except Exception:
        return {}
    return mapping

def apply_aida_fv_mapping(df, excel_file="aida/top_aida_project_fv_mapping.xlsx"):
    if df is None or df.empty:
        return df
    if 'fv' not in df.columns:
        df['fv'] = None
    if 'top_aida' not in df.columns and 'aida_english' in df.columns:
        df['top_aida'] = df['aida_english']
    if 'top_aida' not in df.columns:
        df['fv'] = df['fv'].fillna('Unknown')
        return df
    mtime = _get_file_mtime(excel_file)
    mapping = _load_top_aida_fv_mapping(excel_file, mtime)
    if not mapping:
        df['fv'] = df['fv'].fillna('Unknown')
        return df
    mask = df['fv'].isna() | (df['fv'].astype(str).str.strip() == '') | (df['fv'].astype(str) == 'Unknown')
    if mask.any():
        df.loc[mask, 'fv'] = df.loc[mask, 'top_aida'].astype(str).map(mapping)
    df['fv'] = df['fv'].fillna('Unknown')
    return df

def apply_team_fvp_mapping(df):
    if df is None or df.empty:
        return df
    if 'fv' not in df.columns:
        return df
    dips_fvs = [
        'DIPS_TSP_Call_Services', 'DIPS_TSP_CD_Updates', 'DIPS_TSP_Remote_Services',
        'Mybmw App', 'eMob', 'DIPS_TSP_Car_Apps_CN', 'DIPS_TSP_MobileApps',
        'DIPS_TSP_Enabler', 'Slip-Through'
    ]
    if 'team' not in df.columns:
        df['team'] = None
    team_mask = df['team'].isna() | (df['team'].astype(str).str.strip() == '') | (df['team'].astype(str) == 'Unknown')
    if team_mask.any():
        df.loc[team_mask, 'team'] = np.where(
            df.loc[team_mask, 'fv'].isin(dips_fvs) | df.loc[team_mask, 'fv'].isna(),
            'DIPS',
            'IUK'
        )
    fvp_mapping = {
        'DIPS_TSP_Call_Services': 'Tianhua',
        'DIPS_TSP_CD_Updates': 'Tianhua',
        'DIPS_TSP_Remote_Services': 'Tianhua',
        'eMob': 'Tianhua',
        'DIPS_TSP_MobileApps': 'Tianhua',
        'DIPS_TSP_Enabler': 'Tianhua',
        'IuK_TSP_Navi': 'Tony',
        'IuK_TSP_AZV': 'Xu Miao',
        'IuK_TSP_Entertainment': 'Xu Miao',
        'IuK_TSP_Audio': 'Xu Miao',
        'IuK_TSP_Connectivity': 'Xu Miao',
        'DIPS_TSP_Car_Apps_CN': 'Huanran',
        'IuK_TSP_HMI': 'Jerry',
        'DIPS_TSP_RSU': 'Jerry',
        'IuK_TSP_Carfunctions': 'Jerry',
        'IuK_TSP_Perso CN': 'Jerry',
        'RSU': 'Jerry',
        'Mybmw App': 'Marin'
    }
    if 'fvp' not in df.columns:
        df['fvp'] = None
    fvp_mask = df['fvp'].isna() | (df['fvp'].astype(str).str.strip() == '') | (df['fvp'].astype(str) == 'Unknown')
    if fvp_mask.any():
        df.loc[fvp_mask, 'fvp'] = df.loc[fvp_mask, 'fv'].map(fvp_mapping).fillna('Unknown')
    return df

def apply_chart_style(fig, title, x_title=None, y_title=None, height=600):
    """应用统一的图表样式，根据当前主题动态调整"""
    current_theme = theme_manager.get_theme()

    # 通用布局更新，不依赖于特定主题的设置先应用
    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        xaxis_tickangle=-45,
        height=height,
        width=None,  # 让图表自适应容器宽度
        legend_title_text="分类",
        margin=dict(l=50, r=50, t=100, b=50),
        title_x=0.5,  # 标题居中
        autosize=True,  # 启用自动调整大小
        hoverlabel=dict(
            bgcolor='#1a1a1a' if current_theme == 'dark' else '#f0f0f0', # 悬浮提示框背景色也应根据主题变化
            font_color='white' if current_theme == 'dark' else 'black' # 悬浮提示框文字颜色
        )
    )

    if current_theme == 'light':
        fig = apply_light_theme_to_figure(fig)
    else: # 默认为暗色主题或显式选择暗色主题
        fig = apply_dark_theme_to_figure(fig)
    
    # 可以在这里添加更多不区分主题的通用样式调整，如果需要的话
    # 例如，调整坐标轴的特定属性，如果它们不包含在主题函数中

    return fig

def create_empty_figure(message="没有数据显示", height=None):
    """
    创建一个带有消息的空图表，并根据当前主题应用样式。
    """
    fig = go.Figure() # Make sure plotly.graph_objects is imported as go if not already
    current_theme = theme_manager.get_theme()

    bg_color = '#2c2c2c' if current_theme == 'dark' else '#ffffff'
    text_color = 'white' if current_theme == 'dark' else 'black'
    
    layout_update = {
        "xaxis": {"visible": False},
        "yaxis": {"visible": False},
        "annotations": [{
            "text": message,
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "font": {"size": 16, "color": text_color}
        }],
        "plot_bgcolor": bg_color,
        "paper_bgcolor": bg_color,
    }
    if height is not None:
        layout_update["height"] = height
        
    fig.update_layout(**layout_update)

    return fig

# --- 添加 get_top_req 函数 ---
# (从 aida_top_project_manager.py 移植过来，用于计算 top_aida)
def get_top_req(req):
    if not isinstance(req, list) or len(req) == 0:
        return ''
    
    lst_req = req
    top_req = ''
    len_req = 1000
    n = len(lst_req)
    for i in range(n):
        # 检查元素是否为字符串
        if not isinstance(lst_req[i], str):
            continue # 跳过非字符串元素
        ith_req = lst_req[i]
        # 安全地分割字符串
        split_parts = ith_req.split(' ')
        if not split_parts: # 如果分割结果为空
             continue
        # 检查最后一部分是否有效
        last_part = split_parts[-1]
        if not last_part: # 如果最后一部分为空字符串
            continue
        try:
             # 尝试计算长度，如果最后一部分不是有效字符串（理论上应该总是），则跳过
            len_ith_req = len(last_part)
        except TypeError:
            continue

        if (len_ith_req < len_req):
            len_req = len_ith_req
            top_req = ith_req
    return top_req
# --- 添加结束 ---

# ===== 数据库加载支持 =====

def _load_defects_from_optimized_table(file_pattern="defect/2025_defect.json") -> pd.DataFrame:
    """
    从优化后的 octane_defects 表加载数据
    """
    if not HAS_DB_CONFIG:
        return pd.DataFrame()

    conn = sqlite3.connect(DB_PATH)
    try:
        # 从文件模式提取年份
        year_match = re.search(r"(\d{4})", file_pattern)
        year_val = int(year_match.group(1)) if year_match else None

        try:
            params = []
            update_where = "WHERE (relation_to IS NULL OR TRIM(relation_to) = '') AND json_extract(raw_json, '$.relation_to_udf') IS NOT NULL AND TRIM(CAST(json_extract(raw_json, '$.relation_to_udf') AS TEXT)) <> ''"
            if year_val:
                update_where += " AND year = ?"
                params.append(year_val)
            conn.execute(
                f"""
                UPDATE octane_defects
                SET relation_to = CAST(json_extract(raw_json, '$.relation_to_udf') AS TEXT)
                {update_where}
                """,
                params,
            )
            conn.commit()
        except Exception:
            pass

        # 构建查询 - 现在数据库中的字段应该已经正确填充
        # 不需要再从 raw_json 中提取
        query = """
            SELECT
                defect_id as id, name, creation_time, last_modified,
                team, problem_finder_team, program, author,
                aida_businesskey, aida_english, top_aida,
                product_areas, user_tags,
                phase, severity, problem_severity, status_phase,
                owner, detected_by,
                detected_in_release, software_version,
                vin, assigned_ecu as ecu, lead_model, ecu_no_of_changes as pingpong,
                parent_id, parent_child_type as parent_child, relation_to,
                test_week, risk_score, fv, fvp,
                tqr, blocking_reason, error_occurrence,
                solution_responsible, solution_cluster, solution_cluster as domain,
                json_extract(raw_json, '$.reporting_class_udf') as reporting_class_json,
                json_extract(raw_json, '$.sab_comment_udf') as sab_comment_udf_json,
                json_extract(raw_json, '$.parent_phase_udf') as parent_phase_udf_json,
                function_responsible,
                involved_i_step, first_use_sop_of_function as pu,
                tolerated_count, reprel_changes,
                year, fetched_at
            FROM octane_defects
            WHERE 1=1
        """
        params = []

        if year_val:
            query += " AND year = ?"
            params.append(year_val)

        df = pd.read_sql_query(query, conn, params=params)

        # 在JSON解析前，先保存user_tags用于matrix提取（数据库中是逗号分隔字符串，不是JSON）
        if 'user_tags' in df.columns:
            df['user_tags_raw'] = df['user_tags'].copy()

        # 解析 JSON 列（tqr 是 JSON 格式）
        # 注意：product_areas 和 reporting_class 现在是逗号分隔字符串
        if 'tqr' in df.columns:
            def safe_parse_json(x):
                if not x or not isinstance(x, str):
                    return []
                x = x.strip()
                if not x or x in ('null', 'NULL', 'None'):
                    return []
                try:
                    return json.loads(x)
                except json.JSONDecodeError:
                    return []
            df['tqr'] = df['tqr'].apply(safe_parse_json)

        if 'reporting_class_json' in df.columns:
            def extract_classification(reporting_class_json):
                if not reporting_class_json:
                    return []
                try:
                    data = json.loads(reporting_class_json) if isinstance(reporting_class_json, str) else reporting_class_json
                    if isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
                        return [item.get('name', '') for item in data['data'] if isinstance(item, dict) and item.get('name')]
                    return []
                except Exception:
                    return []
            df['classification'] = df['reporting_class_json'].apply(extract_classification)
            df = df.drop(columns=['reporting_class_json'])

        if 'sab_comment_udf_json' in df.columns:
            def extract_obj(val):
                if val is None or val == '':
                    return None
                try:
                    data = json.loads(val) if isinstance(val, str) else val
                    return data if isinstance(data, dict) else None
                except Exception:
                    return None
            df['sab_comment_udf'] = df['sab_comment_udf_json'].apply(extract_obj)
            df = df.drop(columns=['sab_comment_udf_json'])

        if 'parent_phase_udf_json' in df.columns:
            def extract_obj2(val):
                if val is None or val == '':
                    return None
                try:
                    data = json.loads(val) if isinstance(val, str) else val
                    return data if isinstance(data, dict) else None
                except Exception:
                    return None
            df['parent_phase_udf'] = df['parent_phase_udf_json'].apply(extract_obj2)
            df = df.drop(columns=['parent_phase_udf_json'])

        # 处理时间列
        if 'creation_time' in df.columns:
            df['creation_time'] = pd.to_datetime(df['creation_time'], errors='coerce')

        # 修复 status_phase 字段 - 去掉严重程度后缀（如 _Medium, _Low 等）
        # 数据库中的 status_phase 包含状态和下划线后缀，需要提取纯状态名
        if 'status_phase' in df.columns:
            def extract_base_status(status):
                """从 status_phase 中提取基础状态名，去掉后缀"""
                if pd.isna(status) or not isinstance(status, str):
                    return status
                # 查找最后一个下划线的位置
                if '_' in status:
                    # 检查是否是已知的严重程度后缀
                    severity_suffixes = ['_Critical', '_Very High', '_High', '_Medium', '_Low', '_Very Low']
                    for suffix in severity_suffixes:
                        if status.endswith(suffix):
                            return status[:-len(suffix)]
                return status
            df['status_phase'] = df['status_phase'].apply(extract_base_status)

        # 添加 matrix_display 列（从 user_tags 中提取 matrix 标签）
        def extract_matrix_display(user_tags):
            """从 user_tags 中提取 Matrix 标签用于显示"""
            # 处理字符串格式（从数据库加载的user_tags是逗号分隔的字符串）
            if isinstance(user_tags, str):
                tags = [t.strip() for t in user_tags.split(',') if t.strip()]
                for tag in tags:
                    if 'matrix-' in tag.lower():
                        return tag.replace('matrix-', 'Matrix-').upper()
                return 'UnknownMatrix'
            # 处理列表格式
            elif isinstance(user_tags, list):
                for tag in user_tags:
                    if isinstance(tag, dict):
                        tag_name = tag.get('name', '')
                    else:
                        tag_name = str(tag)
                    if tag_name and 'matrix-' in tag_name.lower():
                        # 转换为显示格式：matrix-1a -> Matrix-1A
                        return tag_name.replace('matrix-', 'Matrix-').upper()
                return 'UnknownMatrix'
            return 'UnknownMatrix'

        # 使用原始user_tags提取matrix（未被JSON解析破坏的）
        if 'user_tags_raw' in df.columns:
            df['matrix_display'] = df['user_tags_raw'].apply(extract_matrix_display)
            df['matrix'] = df['matrix_display']  # 同时设置 matrix 列
            df['user_tags'] = df['user_tags_raw']  # 恢复为原始值
            df.drop('user_tags_raw', axis=1, inplace=True)
        elif 'user_tags' in df.columns:
            df['matrix_display'] = df['user_tags'].apply(extract_matrix_display)
            df['matrix'] = df['matrix_display']

        # 添加缺失列的默认值，确保与文件加载格式一致
        # 注意：列表类型需要使用 .loc 或列表推导式创建
        string_columns = ['tester', 'severity_group', 'occurrence', 'release', 'istep', 'blocking_reason']
        list_columns = ['tags', 'ticket_quality', 'aidas']

        for col in string_columns:
            if col not in df.columns:
                df[col] = 'Unknown' if col in ['tester', 'release', 'istep'] else ''

        for col in list_columns:
            if col not in df.columns:
                df[col] = [[] for _ in range(len(df))]

        # 从 product_areas 设置 aidas（product_areas 是逗号分隔字符串）
        if 'aidas' in df.columns and 'product_areas' in df.columns:
            try:
                def extract_aidas_from_string(x):
                    """从逗号分隔的 product_areas 字符串提取 aidas 列表"""
                    if x is None or x == '':
                        return []
                    if isinstance(x, str):
                        return [item.strip() for item in x.split(',') if item.strip()]
                    return []

                df['aidas'] = df['product_areas'].apply(extract_aidas_from_string)
                print(f"  已从 product_areas 提取 aidas，非空值计数: {(df['aidas'].apply(len) > 0).sum()}")
            except Exception as e:
                print(f"  警告: 无法从 product_areas 设置 aidas: {e}")
                df['aidas'] = [[] for _ in range(len(df))]

        if 'relation_to' in df.columns and 'relation_to_udf' not in df.columns:
            df['relation_to_udf'] = df['relation_to']

        # 注意：top_aida 和 aida_english 现在已经在数据库存储时正确计算
        # 不需要在这里重新计算

        # 确保 classification 列不是 None
        if 'classification' in df.columns:
            df['classification'] = df['classification'].apply(lambda x: x if isinstance(x, list) else [])
        else:
            df['classification'] = [[] for _ in range(len(df))]

        if 'ecu_no_of_changes_udf' not in df.columns and 'pingpong' in df.columns:
            df['ecu_no_of_changes_udf'] = pd.to_numeric(df['pingpong'], errors='coerce').fillna(0).astype(int)

        # 创建 phase.name 列（兼容旧代码期望的格式）
        # 数据库中 phase 是字符串，需要创建嵌套字典格式
        if 'phase' in df.columns:
            # 创建 phase.name 列，与文件加载格式一致
            df['phase.name'] = df['phase']
            # 同时创建 phase 嵌套字典格式（某些代码可能使用）
            df['phase_dict'] = df['phase'].apply(lambda x: {'name': x} if x else {'name': ''})

        # 创建 severity.name 列（兼容格式）
        if 'severity' in df.columns:
            df['severity.name'] = df['severity']

        # 创建 detected_in_release.name 列（兼容格式）
        if 'detected_in_release' in df.columns:
            df['detected_in_release.name'] = df['detected_in_release']

        if 'team' in df.columns:
            try:
                team_series = df['team'].fillna('').astype(str)
                if (team_series == _DEFAULT_OCTANE_TEAM).any():
                    if 'octane_team' not in df.columns:
                        df['octane_team'] = df['team']
                    df['team'] = None
            except Exception:
                pass

        df = apply_vin_project_mapping(df)
        df = apply_app_rsu_project_override(df)
        df = apply_aida_fv_mapping(df)
        df = apply_team_fvp_mapping(df)

        if 'id' in df.columns and 'relation_to_udf' in df.columns:
            try:
                df['id'] = df['id'].astype(str)
                rel = df['relation_to_udf'].fillna('').astype(str).replace('nan', '').replace('None', '').str.strip()

                if 'parent_child' in df.columns:
                    pc = df['parent_child'].fillna('').astype(str)
                else:
                    pc = pd.Series(['' for _ in range(len(df))], index=df.index)

                is_child = pc.isin(['Child', 'Child (candidate)', 'Child (Candidate)'])
                is_parent = pc.eq('Parent')

                df['master_id'] = np.where(is_child, rel, '')

                master_child_counts = df.loc[is_child, 'master_id'].astype(str).str.strip()
                master_child_counts = master_child_counts[master_child_counts != ''].value_counts()
                df['child_count_of_master'] = df['master_id'].map(master_child_counts).fillna(0).astype(int)

                df['child_count'] = 0
                df.loc[is_parent, 'child_count'] = rel[is_parent].apply(_count_linked_defects).astype(int)

                if 'parent_child' not in df.columns:
                    df['parent_child'] = ''
                pc = df['parent_child'].fillna('').astype(str)
                empty_pc = pc.str.strip() == ''
                if empty_pc.any():
                    df.loc[empty_pc, 'parent_child'] = np.where(
                        df.loc[empty_pc, 'master_id'].astype(str).str.strip() != '',
                        'Child',
                        np.where(rel[empty_pc].apply(_count_linked_defects).astype(int) > 0, 'Parent', '')
                    )
            except Exception:
                pass

        if 'detected_by' in df.columns:
            detected_series = df['detected_by'].fillna('').astype(str).str.strip()
            if 'tester' not in df.columns:
                df['tester'] = detected_series
            else:
                tester_series = df['tester'].fillna('').astype(str).str.strip()
                unknown_mask = tester_series.str.lower().isin({'', 'unknown', 'unknown tester', 'nan', 'none'})
                if unknown_mask.any():
                    df.loc[unknown_mask, 'tester'] = detected_series[unknown_mask]
        elif 'tester' not in df.columns:
            df['tester'] = 'Unknown'
        
        # 再次确认tester列没有空字符串
        if 'tester' in df.columns:
            tester_clean = df['tester'].fillna('').astype(str).str.strip()
            tester_clean = tester_clean.replace({'nan': '', 'None': '', 'none': ''})
            df['tester'] = tester_clean.where(tester_clean != '', 'Unknown')

        # 注意：author 和 owner 已经在数据库存储时提取为 full_name
        # 不需要在这里再次提取

        if 'project' in df.columns:
            try:
                print(f"项目分布: {df['project'].value_counts().to_dict()}")
            except Exception:
                pass

        # 注意：FV、FVP、Team 等字段已经在数据库存储时正确计算和填充
        # 不需要在这里再次处理

        return df

    except Exception as e:
        print(f"从优化表加载失败: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def _ensure_defect_features_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS defect_features (
            defect_id TEXT PRIMARY KEY,
            topissue_risk_score REAL,
            topissue_display TEXT,
            topissue_recommend_reason TEXT,
            is_topissue INTEGER,
            is_master_score INTEGER,
            source_fetched_at TEXT,
            computed_at TEXT,
            feature_version TEXT
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_defect_features_is_topissue ON defect_features(is_topissue)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_defect_features_risk_score ON defect_features(topissue_risk_score)")

def _load_defect_features(conn: sqlite3.Connection, defect_ids: List[str]) -> pd.DataFrame:
    if not defect_ids:
        return pd.DataFrame()
    placeholders = ",".join(["?"] * len(defect_ids))
    query = f"""
        SELECT
            defect_id,
            topissue_risk_score,
            topissue_display,
            topissue_recommend_reason,
            is_topissue,
            is_master_score,
            source_fetched_at,
            computed_at,
            feature_version
        FROM defect_features
        WHERE defect_id IN ({placeholders})
    """
    return pd.read_sql_query(query, conn, params=defect_ids)

def _upsert_defect_features(conn: sqlite3.Connection, rows: List[Dict]) -> None:
    if not rows:
        return
    conn.executemany(
        """
        INSERT INTO defect_features(
            defect_id,
            topissue_risk_score,
            topissue_display,
            topissue_recommend_reason,
            is_topissue,
            is_master_score,
            source_fetched_at,
            computed_at,
            feature_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(defect_id) DO UPDATE SET
            topissue_risk_score=excluded.topissue_risk_score,
            topissue_display=excluded.topissue_display,
            topissue_recommend_reason=excluded.topissue_recommend_reason,
            is_topissue=excluded.is_topissue,
            is_master_score=excluded.is_master_score,
            source_fetched_at=excluded.source_fetched_at,
            computed_at=excluded.computed_at,
            feature_version=excluded.feature_version
        """,
        [
            (
                str(r.get("defect_id", "")),
                float(r.get("topissue_risk_score", 0.0)),
                str(r.get("topissue_display", "")),
                str(r.get("topissue_recommend_reason", "")),
                int(r.get("is_topissue", 0)),
                int(r.get("is_master_score", 0)),
                str(r.get("source_fetched_at", "")),
                str(r.get("computed_at", "")),
                str(r.get("feature_version", "")),
            )
            for r in rows
        ],
    )

def _count_linked_defects(relation_str) -> int:
    if relation_str is None or pd.isna(relation_str):
        return 0
    try:
        ids = str(relation_str).split(",")
        return len([x.strip() for x in ids if x and x.strip()])
    except Exception:
        return 0

def _build_topissue_recommendation(ticket_row: Dict) -> str:
    parts = []
    severity_items = []
    matrix = ticket_row.get("matrix", "")
    if matrix:
        severity_items.append(f"Matrix {str(matrix).replace('matrix-', '').replace('Matrix-', '').upper()}")
    classification = ticket_row.get("classification", [])
    if isinstance(classification, list):
        for name in [
            "Showstopper_Confirmed",
            "Preventing Maturity Grade ConDrive",
            "Showstopper_Candidate",
            "Obstructing Maturity Grade ConDrive",
            "Homologation L-labelled",
        ]:
            if name in classification:
                severity_items.append(name)
    if severity_items:
        parts.append(f"SEVERITY: {'; '.join(severity_items)}")

    high_runner_items = []
    ecu_pingpong = ticket_row.get("ecu_no_of_changes_udf", 0) or ticket_row.get("pingpong", 0)
    try:
        ecu_pingpong = int(ecu_pingpong)
    except Exception:
        ecu_pingpong = 0
    if ecu_pingpong > 0:
        high_runner_items.append(f"ECU transfer {ecu_pingpong} times")
    domain_pingpong = ticket_row.get("domain_pingpong_display", 0) or ticket_row.get("domain_pingpong_count", 0)
    try:
        domain_pingpong = int(domain_pingpong)
    except Exception:
        domain_pingpong = 0
    if domain_pingpong > 0:
        high_runner_items.append(f"Domain transfer {domain_pingpong} times")
    if high_runner_items:
        parts.append(f"HIGH RUNNER: {'; '.join(high_runner_items)}")

    complexity_items = []
    parent_child = ticket_row.get("parent_child", "")
    if parent_child == "Parent":
        c = ticket_row.get("子票数量", 0) or ticket_row.get("child_count", 0)
        try:
            c = int(c)
        except Exception:
            c = 0
        if c > 0:
            complexity_items.append(f"{c} child tickets")
    elif parent_child in ["Child", "Child (candidate)"]:
        c = ticket_row.get("子票数量", 0) or ticket_row.get("child_count", 0)
        try:
            c = int(c)
        except Exception:
            c = 0
        if c > 0:
            complexity_items.append(f"Master has {c} children")
    if complexity_items:
        parts.append(f"COMPLEXITY: {'; '.join(complexity_items)}")

    long_runner_items = []
    processing_days = ticket_row.get("processing_cycle_days", 0)
    try:
        processing_days = int(processing_days)
    except Exception:
        processing_days = 0
    if processing_days >= 7:
        long_runner_items.append(f"Cycle {processing_days} days")
    shift_pu = ticket_row.get("Shift_PU", "")
    if shift_pu and str(shift_pu).strip():
        long_runner_items.append(f"Shift {str(shift_pu).strip()}")
    if long_runner_items:
        parts.append(f"LONG RUNNER: {'; '.join(long_runner_items)}")

    return "\n".join(parts) if parts else "No specific risk factors"

def _ensure_and_attach_topissue_features(ddf: pd.DataFrame) -> pd.DataFrame:
    if ddf is None or ddf.empty or "id" not in ddf.columns:
        return ddf

    defect_ids = ddf["id"].astype(str).tolist()
    conn = sqlite3.connect(DB_PATH)
    try:
        _ensure_defect_features_table(conn)
        existing = _load_defect_features(conn, defect_ids)
        existing_map = {}
        if existing is not None and not existing.empty:
            existing_map = existing.set_index("defect_id").to_dict("index")

        to_compute = []
        for _, row in ddf[["id", "fetched_at"]].astype(str).iterrows():
            did = row["id"]
            fetched_at = row.get("fetched_at", "")
            cur = existing_map.get(did)
            if not cur:
                to_compute.append(did)
                continue
            if fetched_at and str(cur.get("source_fetched_at", "")) != fetched_at:
                to_compute.append(did)

        if to_compute:
            from risk_score_calculator import calculate_risk_score, calculate_with_master

            subset = ddf[ddf["id"].astype(str).isin(set(to_compute))].copy()
            if "processing_cycle_days" not in subset.columns and {"status_phase", "creation_time"}.issubset(set(subset.columns)):
                subset["processing_cycle_days"] = subset.apply(
                    lambda r: calculate_processing_cycle_days(str(r.get("id")), r.get("status_phase", ""), r.get("creation_time")),
                    axis=1,
                )
            if "processing_cycle_days" not in ddf.columns and "processing_cycle_days" in subset.columns:
                ddf = ddf.merge(subset[["id", "processing_cycle_days"]], on="id", how="left")

            master_lookup = {}
            if "parent_child" in ddf.columns:
                masters = ddf[ddf["parent_child"] == "Parent"].copy()
            else:
                masters = pd.DataFrame()
            if not masters.empty:
                masters["子票数量"] = masters["relation_to"].apply(_count_linked_defects) if "relation_to" in masters.columns else 0
                keys = [
                    "id",
                    "matrix",
                    "classification",
                    "ecu_no_of_changes_udf",
                    "pingpong",
                    "domain_pingpong_display",
                    "domain_pingpong_count",
                    "parent_child",
                    "子票数量",
                    "processing_cycle_days",
                    "Shift_PU",
                ]
                keys = [k for k in keys if k in masters.columns]
                master_lookup = masters[keys].set_index("id").to_dict("index")

            computed_at = datetime.utcnow().isoformat()
            feature_version = "topissue_v1"
            upserts = []
            for _, row in subset.iterrows():
                r = row.to_dict()
                parent_id = r.get("parent_id")
                if parent_id and not isinstance(r.get("parent"), dict):
                    r["parent"] = {"id": str(parent_id)}
                if r.get("parent_child") == "Parent":
                    r["子票数量"] = _count_linked_defects(r.get("relation_to"))
                score, _, _ = calculate_with_master(r, master_lookup)
                child_score, _, _ = calculate_risk_score(r)
                is_master_score = bool(
                    r.get("parent_child") in ["Child", "Child (candidate)"] and score > child_score
                )
                chosen_row = r
                if is_master_score and isinstance(r.get("parent"), dict):
                    mid = r.get("parent", {}).get("id")
                    if mid and str(mid) in master_lookup:
                        chosen_row = master_lookup[str(mid)].copy()
                        chosen_row["parent_child"] = "Parent"
                        chosen_row["子票数量"] = chosen_row.get("子票数量", 0)
                rec = _build_topissue_recommendation({**chosen_row, "processing_cycle_days": r.get("processing_cycle_days", chosen_row.get("processing_cycle_days", 0))})
                display = f"{int(round(score))}{'*' if is_master_score else ''}" if score and score > 0 else "0"
                upserts.append(
                    {
                        "defect_id": str(r.get("id")),
                        "topissue_risk_score": float(score),
                        "topissue_display": display,
                        "topissue_recommend_reason": rec,
                        "is_topissue": 1 if score >= 60 else 0,
                        "is_master_score": 1 if is_master_score else 0,
                        "source_fetched_at": str(r.get("fetched_at", "")),
                        "computed_at": computed_at,
                        "feature_version": feature_version,
                    }
                )

            _upsert_defect_features(conn, upserts)
            conn.commit()

        features = _load_defect_features(conn, defect_ids)
        if features is None or features.empty:
            return ddf
        merged = ddf.merge(features, left_on="id", right_on="defect_id", how="left")
        merged = merged.drop(columns=["defect_id"])
        return merged
    finally:
        conn.close()


# ===== 缺陷管理数据处理 =====

def load_defect_data(file_pattern="defect/2025_defect.json", use_db=None):
    """
    加载缺陷数据并进行基础处理，并添加 FV, Team, FVP 列

    Args:
        file_pattern: 文件匹配模式（文件模式时使用）
        use_db: 强制使用数据库（None=根据配置，True=强制数据库，False=强制文件）
    """
    # 如果是reloader进程，返回空DataFrame避免数据加载
    if IS_RELOADER:
        print("🔄 data_processor.load_defect_data: Reloader进程跳过数据加载")
        return pd.DataFrame()

    # 检查是否应该从数据库加载
    should_use_db = use_db if use_db is not None else (
        HAS_DB_CONFIG and (is_db_first_mode() or is_db_only_mode())
    )

    # 如果配置使用优化表，从新表加载
    if should_use_db and HAS_DB_CONFIG and is_using_optimized_schema():
        try:
            print("💾 从数据库优化表加载数据...")
            df = _load_defects_from_optimized_table(file_pattern)
            if not df.empty:
                print(f"✅ 从数据库加载 {len(df)} 条记录")
                return _ensure_and_attach_topissue_features(df)
            print("⚠️ 数据库优化表为空，继续尝试数据库原始载荷表")
        except Exception as e:
            print(f"⚠️ 从数据库加载失败: {e}")
            if is_db_only_mode():
                raise

    try:
        year_match = re.search(r"(\d{4})", str(file_pattern or ""))
        year_val = int(year_match.group(1)) if year_match else None
    except Exception:
        year_val = None

    db_path_val = _DEFAULT_OCTANE_DB_PATH
    if not os.path.exists(db_path_val):
        return pd.DataFrame()

    try:
        conn = sqlite3.connect(db_path_val)
        try:
            if year_val is not None:
                row = conn.execute(
                    "SELECT payload_json FROM octane_payloads WHERE kind=? AND team=? AND year=? AND spec=?",
                    ("defects", _DEFAULT_OCTANE_TEAM, int(year_val), ""),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT payload_json FROM octane_payloads WHERE kind=? AND team=? ORDER BY fetched_at DESC LIMIT 1",
                    ("defects", _DEFAULT_OCTANE_TEAM),
                ).fetchone()
        finally:
            conn.close()

        if not row:
            return pd.DataFrame()
        payload = json.loads(row[0])
        data_list = payload.get("data") if isinstance(payload, dict) else payload
        if not (isinstance(data_list, list) and data_list and all(isinstance(item, dict) for item in data_list)):
            return pd.DataFrame()
        ddf = pd.json_normalize(data_list, max_level=0)
    except Exception:
        return pd.DataFrame()
    
    # 处理时间和测试周
    if 'creation_time' in ddf.columns:
        ddf['creation_time'] = ddf['creation_time'].str.replace('T', ' ').str.replace('Z', '')
        ddf['creation_time'] = pd.to_datetime(ddf['creation_time'], format='%Y-%m-%d %H:%M:%S')
        
        # 生成包含年份的test_week
        ddf['test_week'] = (ddf['creation_time'].dt.year.astype(str) + '-CW' + 
                           ddf['creation_time'].dt.isocalendar().week.astype("string").str.zfill(2))
        
        print(f"数据行数: {len(ddf)}，时间范围: {ddf['creation_time'].min()} 到 {ddf['creation_time'].max()}")
    
    # 处理字段映射
    field_mappings = {
        "vin": "vin_udf",
        "occurrence": "error_occurrence_udf",
        "severity": "problem_severity_udf",
        "status_phase": "phase",
        "solution": "solution_responsible_udf",
        "parent_child": "parent_child_udf",
        "blocking_reason": "blocking_reason_udf",
        "pu": "first_use_sop_of_function_udf",
        "tester": "detected_by",
        "ecu": "assigned_ecu_udf",
        "release": "detected_in_release",
        "istep": "involved_i_step1_udf",
        "lead_model": "lead_model_udf",
        "software_version": "software_version_udf"
    }
    
    # 安全地提取字段值
    def safe_extract_name(x):
        if x is None:
            return ""
        if isinstance(x, dict) and "name" in x:
            return x["name"]
        if isinstance(x, dict) and "full_name" in x:
            return x["full_name"]
        return ""
    
    # 处理简单字段
    for new_field, source_field in field_mappings.items():
        if source_field in ddf.columns:
            if new_field == "software_version":
                # software_version_udf是简单字符串，直接使用
                ddf[new_field] = ddf[source_field].fillna("")
            else:
                ddf[new_field] = ddf[source_field].apply(safe_extract_name)
        else:
            ddf[new_field] = ""
    
    # 处理列表字段
    def safe_extract_list(x):
        if x is None:
            return []
        if isinstance(x, dict) and "data" in x and isinstance(x["data"], list):
            return [i.get("name", "") for i in x["data"] if isinstance(i, dict)]
        return []
    
    list_field_mappings = {
        "tags": "user_tags",
        "ticket_quality": "tqr_udf",
        "aidas": "product_areas"
    }
    
    for new_field, source_field in list_field_mappings.items():
        if source_field in ddf.columns:
            ddf[new_field] = ddf[source_field].apply(safe_extract_list)
        else:
            ddf[new_field] = [[] for _ in range(len(ddf))]
    
    # ---> ADDED: Create top_aida for ddf from the 'aidas' list <---
    if 'aidas' in ddf.columns:
        ddf['top_aida'] = ddf['aidas'].apply(get_top_req)
    else:
        ddf['top_aida'] = "" # Ensure column exists even if 'aidas' was missing
    # ---> END ADDED <---

    # 应用基于Excel的字段映射 (Project, FV, Team, FVP) - 恢复原有逻辑
    try:
        ddf = apply_vin_project_mapping(ddf)
        ddf = apply_app_rsu_project_override(ddf)
        ddf = apply_aida_fv_mapping(ddf)
        ddf = apply_team_fvp_mapping(ddf)
    except Exception as e:
        print(f"应用Excel映射失败: {e}")

    # 提取Matrix标签
    def extract_matrix(tags):
        if isinstance(tags, list) and len(tags) > 0:
            matrix_tags = [tag for tag in tags if isinstance(tag, str) and tag.lower().startswith('matrix-')]
            return matrix_tags[0] if len(matrix_tags) > 0 else ""
        return ""
    
    # 确保 'tags' 列存在 (可能来自 user_tags)
    if 'tags' not in ddf.columns and 'user_tags' in ddf.columns:
        ddf['tags'] = ddf['user_tags']
    elif 'tags' not in ddf.columns:
         ddf['tags'] = [[] for _ in range(len(ddf))] # 如果两者都不存在，创建空列表
         
    ddf["matrix"] = ddf["tags"].apply(extract_matrix)
    
    # 添加 Domain 列 (从 solution_cluster_udf)
    if 'solution_cluster_udf' in ddf.columns:
        ddf["domain"] = ddf["solution_cluster_udf"].apply(
            lambda x: x["name"] if isinstance(x, dict) and "name" in x else ""
        )
    else:
        ddf["domain"] = ""
        
    # 添加 Classification 列 (从 reporting_class_udf)
    if 'reporting_class_udf' in ddf.columns:
        ddf["classification"] = ddf["reporting_class_udf"].apply(
             lambda x: [i.get("name", "") for i in x["data"] if isinstance(i, dict)]
                       if isinstance(x, dict) and "data" in x and isinstance(x["data"], list)
                       else []
        )
    else:
        ddf["classification"] = [[] for _ in range(len(ddf))]

    # 确保 classification 列没有 None 值
    ddf["classification"] = ddf["classification"].apply(lambda x: x if isinstance(x, list) else [])

    # 添加Matrix显示和排序值
    ddf["matrix_display"] = ddf["matrix"].apply(lambda x: x.replace("matrix-", "").upper() if isinstance(x, str) and x else "")
    # 确保 matrix_severity_order 函数已定义或导入
    try:
        ddf["matrix_order"] = ddf["matrix"].apply(matrix_severity_order)
    except NameError:
        print("警告: matrix_severity_order 函数未定义，matrix_order 列将不会被创建或填充。")
        # 可以选择在这里定义一个默认的排序逻辑或赋值为 NaN/None
        ddf["matrix_order"] = pd.NA 
     
    # 添加严重性分组和TopIssue分类 - 新的风险评分系统
    def calculate_topissue_risk_score(row):
        """
        计算TopIssue风险分数 - 非线性算法，基于原有线性基础增加非线性考虑：
        
        核心改进：
        1. Matrix严重度 - 指数衰减：Matrix-1a(30分) → 1b(24分) → 1c(19分)，高危等级分数差距更大
        2. 缺陷时间 - 双峰分布：
           - 第一峰：0-3天新票（24-15分）- 需要快速响应
           - 低谷期：10-20天（5-15分）- 正常处理中
           - 第二峰：>30天长期票（15-25分）- Long Runner问题
        3. 子票数量 - 对数增长：1个(10分) → 3个(18分) → 10个(25分) → 20个(28分)
        4. 智能组合算法：
           - 高分项（>15分）：算术平均×1.2（加强影响）
           - 低分项（≤15分）：几何平均×0.8（降低影响）
        
        基础维度评分 (保持原有8个维度):
        1. Matrix Severity Level (High Weight - 30 points) - 改进为指数衰减
        2. Classification Contains Specific Values (High Weight - 30 points)
        3. ECU Transfer Count (High Weight - 30 points)
        4. Domain Transfer Count (Medium Weight - 20 points)
        5. Parent Ticket Child Count (High Weight - 30 points) - 改进为对数增长
        6. Child Ticket Master Sub-ticket Count (High Weight - 30 points) - 改进为对数增长
        7. Processing Cycle Days (Medium Weight - 20 points) - 改进为双峰分布
        8. Shift PU Status (Low Weight - 10 points) - 推迟修复维度
        
        If it is a Child ticket, the Master ticket score will also be calculated and the higher score will be taken
        """
        def calculate_single_risk_score(ticket_row):
            """Calculate risk score for single ticket"""
            score = 0
            reasons = []
            
            # 保存各维度的原始分数，用于后续非线性调整
            dimension_scores = {
                'matrix': 0,
                'classification': 0,
                'ecu_transfer': 0,
                'domain_transfer': 0,
                'parent_complexity': 0,
                'child_complexity': 0,
                'processing_days': 0,
                'shift_pu': 0
            }
            
            # 保存原始数据，用于后续非线性调整
            raw_data = {
                'matrix': '',
                'ecu_pingpong': 0,
                'domain_pingpong': 0,
                'parent_child': '',
                'child_count': 0,
                'processing_days': 0
            }
            
            # 第一维度：Matrix Severity Level (High Weight - 30 points) - 改进为指数衰减评分
            matrix = ticket_row.get('matrix', '')
            raw_data['matrix'] = matrix
            if isinstance(matrix, str) and matrix:
                matrix_lower = matrix.lower()
                
                # 定义Matrix等级序号和对应的指数衰减分数计算
                matrix_order = {
                    'matrix-1a': 0,   # 最高严重性
                    'matrix-1b': 1,
                    'matrix-1c': 2,
                    'matrix-1d': 3,
                    'matrix-1e': 4,
                    'matrix-2a': 5,
                    'matrix-2b': 6,
                    'matrix-3a': 7,   # High Severity 结束
                    'matrix-2d': 8,   # Medium Severity 开始
                    'matrix-2e': 9,
                    'matrix-3b': 10,
                    'matrix-3c': 11,
                    'matrix-3d': 12,
                    'matrix-4a': 13,   # Medium Severity 结束
                    'matrix-3e': 14,   # Low Severity 开始
                    'matrix-4b': 15,
                    'matrix-4c': 16,
                    'matrix-4d': 17,
                    'matrix-4e': 18    # Low Severity 结束
                }
                
                if matrix_lower in matrix_order:
                    # 指数衰减公式: score = 30 * exp(-0.25 * order)
                    # Matrix-1a: 30 * exp(0) = 30
                    # Matrix-1b: 30 * exp(-0.25) ≈ 24
                    # Matrix-1c: 30 * exp(-0.5) ≈ 19
                    # Matrix-1d: 30 * exp(-0.75) ≈ 14
                    order = matrix_order[matrix_lower]
                    matrix_score = round(30 * math.exp(-0.25 * order))
                    
                    # 确保最低分不少于2分
                    matrix_score = max(2, matrix_score)
                    
                    score += matrix_score
                    dimension_scores['matrix'] = matrix_score
                    
                    # 确定严重性级别
                    if matrix_lower in ['matrix-1a', 'matrix-1b', 'matrix-1c', 'matrix-1d', 'matrix-1e', 
                                       'matrix-2a', 'matrix-2b', 'matrix-3a']:
                        severity_level = "High Severity"
                    elif matrix_lower in ['matrix-2d', 'matrix-2e', 'matrix-3b', 'matrix-3c', 'matrix-3d', 'matrix-4a']:
                        severity_level = "Medium Severity"
                    else:  # matrix-3e, 4b, 4c, 4d, 4e
                        severity_level = "Low Severity"
                    
                    reasons.append(f"Matrix Level {matrix} ({severity_level}, {matrix_score}pts) [Exponential Decay]")
            
            # 第二维度：Classification Contains Specific Values (High Weight - 30 points)
            classification = ticket_row.get('classification', [])
            if isinstance(classification, list):
                if 'Showstopper_Confirmed' in classification:
                    score += 30
                    dimension_scores['classification'] = 30
                    reasons.append("Showstopper Confirmed (30pts)")
                elif 'Preventing Maturity Grade ConDrive' in classification:
                    score += 30
                    dimension_scores['classification'] = 30
                    reasons.append("Preventing Maturity ConDrive (30pts)")
                elif 'Showstopper_Candidate' in classification:
                    score += 20
                    dimension_scores['classification'] = 20
                    reasons.append("Showstopper Candidate (20pts)")
                elif 'Obstructing Maturity Grade ConDrive' in classification or 'Homologation L-labelled' in classification:
                    score += 10
                    dimension_scores['classification'] = 10
                    if 'Obstructing Maturity Grade ConDrive' in classification:
                        reasons.append("Obstructing Maturity ConDrive (10pts)")
                    else:
                        reasons.append("Homologation L-labelled (10pts)")
            
            # 第三维度：ECU Transfer Count (High Weight - 30 points)
            ecu_pingpong = ticket_row.get('ecu_no_of_changes_udf', 0)
            raw_data['ecu_pingpong'] = ecu_pingpong
            if pd.notna(ecu_pingpong) and ecu_pingpong > 0:
                if ecu_pingpong >= 5:
                    score += 30
                    dimension_scores['ecu_transfer'] = 30
                    reasons.append(f"ECU Transfer {ecu_pingpong} times (30pts)")
                elif ecu_pingpong >= 3:
                    score += 24
                    dimension_scores['ecu_transfer'] = 24
                    reasons.append(f"ECU Transfer {ecu_pingpong} times (24pts)")
                elif ecu_pingpong >= 1:
                    score += 20
                    dimension_scores['ecu_transfer'] = 20
                    reasons.append(f"ECU Transfer {ecu_pingpong} times (20pts)")
            
            # 第四维度：Domain Transfer Count (Medium Weight - 20 points)
            domain_pingpong = ticket_row.get('domain_pingpong_display', 0)
            raw_data['domain_pingpong'] = domain_pingpong
            if pd.notna(domain_pingpong) and domain_pingpong > 0:
                if domain_pingpong >= 5:
                    score += 20
                    dimension_scores['domain_transfer'] = 20
                    reasons.append(f"Domain Transfer {domain_pingpong} times (20pts)")
                elif domain_pingpong >= 3:
                    score += 14
                    dimension_scores['domain_transfer'] = 14
                    reasons.append(f"Domain Transfer {domain_pingpong} times (14pts)")
                elif domain_pingpong >= 1:
                    score += 10
                    dimension_scores['domain_transfer'] = 10
                    reasons.append(f"Domain Transfer {domain_pingpong} times (10pts)")
            
            # 第五维度：Parent Ticket Child Count (High Weight - 30 points) - 改进为对数增长
            parent_child = ticket_row.get('parent_child', '')
            raw_data['parent_child'] = parent_child
            if parent_child == 'Parent':
                parent_child_count = ticket_row.get('子票数量', 0)
                raw_data['child_count'] = parent_child_count
                if pd.notna(parent_child_count) and parent_child_count > 0:
                    # 对数增长公式：score = 10 * log(count + 1) * 2.5
                    # 1个子票: 10 * log(2) * 2.5 ≈ 10 * 0.693 * 2.5 ≈ 17分
                    # 3个子票: 10 * log(4) * 2.5 ≈ 10 * 1.386 * 2.5 ≈ 35分 -> 调整为30分上限
                    # 10个子票: 10 * log(11) * 2.5 ≈ 10 * 2.398 * 2.5 ≈ 60分 -> 调整为30分上限
                    parent_score = round(10 * math.log(parent_child_count + 1) * 2.5)
                    parent_score = min(30, parent_score)  # 确保不超过30分上限
                    
                    score += parent_score
                    dimension_scores['parent_complexity'] = parent_score
                    reasons.append(f"Parent ticket has {parent_child_count} child tickets ({parent_score}pts) [Logarithmic Growth]")
            
            # 第六维度：Child Ticket Master Sub-ticket Count (High Weight - 30 points) - 改进为对数增长
            if parent_child == 'Child':
                child_count = ticket_row.get('子票数量', 0)
                raw_data['child_count'] = child_count
                if pd.notna(child_count) and child_count > 0:
                    # 对数增长公式：score = 10 * log(count + 1) * 2.5
                    # 1个子票: 10分, 3个子票: 18分, 10个子票: 25分, 20个子票: 28分
                    child_score = round(10 * math.log(child_count + 1) * 2.5)
                    child_score = min(30, child_score)  # 确保不超过30分上限
                    
                    score += child_score
                    dimension_scores['child_complexity'] = child_score
                    reasons.append(f"Master has {child_count} child tickets ({child_score}pts) [Logarithmic Growth]")
            
            # 第七维度：Processing Cycle Days (Medium Weight - 20 points) - 改进为双峰分布
            processing_days = ticket_row.get('processing_cycle_days', 0)
            raw_data['processing_days'] = processing_days
            if pd.notna(processing_days) and processing_days > 0:
                # 双峰分布算法：
                # 第一峰：0-3天新票（24-15分）- 需要快速响应
                # 低谷期：4-20天（5-15分）- 正常处理中
                # 第二峰：21-30天（15-20分）- 开始进入Long Runner
                # 高峰期：>30天（20-25分）- Long Runner问题
                
                if processing_days <= 3:
                    # 第一峰：新票需要快速响应
                    # 0天=24分，1天=22分，2天=20分，3天=18分
                    processing_score = max(18, 24 - processing_days * 2)
                    peak_type = "New Issue Peak"
                elif processing_days <= 20:
                    # 低谷期：正常处理阶段
                    # 使用二次函数创建低谷：score = 5 + 10 * (1 - ((days-12)/12)^2)
                    # 在12天左右达到最低点约5分
                    normalized_days = (processing_days - 12) / 12
                    processing_score = round(5 + 10 * (1 - normalized_days ** 2))
                    processing_score = max(5, min(15, processing_score))
                    peak_type = "Normal Processing Valley"
                elif processing_days <= 30:
                    # 第二峰开始：Long Runner风险上升
                    # 21天=15分，线性增长到30天=20分
                    processing_score = round(15 + (processing_days - 21) * 0.5)
                    peak_type = "Long Runner Rise"
                else:
                    # 高峰期：严重的Long Runner问题
                    # 30天以上=20分基础，每增加10天加2分，最高25分
                    extra_days = processing_days - 30
                    processing_score = min(25, 20 + (extra_days // 10) * 2)
                    peak_type = "Long Runner Peak"
                
                score += processing_score
                dimension_scores['processing_days'] = processing_score
                reasons.append(f"Processing cycle {processing_days} days ({processing_score}pts) [{peak_type}]")
            
            # 第八维度：Shift PU Status (Low Weight - 10 points) - 推迟修复维度
            shift_pu = ticket_row.get('Shift_PU', '')
            if shift_pu and str(shift_pu).strip() and str(shift_pu).strip() != '':
                score += 10
                dimension_scores['shift_pu'] = 10
                reasons.append(f"Shift PU assigned: {shift_pu} (10pts)")
            
            # 基础维度评分完成，现在应用智能组合算法
            # 替换简单相加模式，使用智能组合算法
            
            # 1. 收集所有维度分数
            dimension_values = list(dimension_scores.values())
            dimension_values = [v for v in dimension_values if v > 0]  # 只考虑有分数的维度
            
            if dimension_values:
                # 2. 分离高分项和低分项
                high_score_items = [v for v in dimension_values if v > 15]
                low_score_items = [v for v in dimension_values if v <= 15]
                
                # 3. 智能组合算法
                combined_score = 0
                
                # 高分项（>15分）：算术平均×1.2（加强影响）
                if high_score_items:
                    high_score_avg = sum(high_score_items) / len(high_score_items)
                    high_score_contribution = high_score_avg * 1.2 * len(high_score_items)
                    combined_score += high_score_contribution
                    reasons.append(f"High-impact factors: {len(high_score_items)} items, avg {high_score_avg:.1f}pts × 1.2 = {high_score_contribution:.1f}pts")
                
                # 低分项（≤15分）：几何平均×0.8（降低影响）
                if low_score_items:
                    # 几何平均 = (a1 × a2 × ... × an)^(1/n)
                    geometric_mean = math.pow(math.prod(low_score_items), 1/len(low_score_items))
                    low_score_contribution = geometric_mean * 0.8 * len(low_score_items)
                    combined_score += low_score_contribution
                    reasons.append(f"Supporting factors: {len(low_score_items)} items, geo_mean {geometric_mean:.1f}pts × 0.8 = {low_score_contribution:.1f}pts")
                
                # 更新总分为智能组合后的分数
                score = round(combined_score)
                reasons.append(f"--- Smart Combined Score: {score}pts (was {sum(dimension_values)}pts) ---")
            
            # 基础智能组合完成，现在添加非线性调整
            nonlinear_adjustment = 0
            nonlinear_reasons = []
            
            # 1. 维度交互效应 - 当关键维度组合同时得分高时增加额外分数
            
            # 1.1 严重问题长期未解决 (Matrix + Processing Days)
            if dimension_scores['matrix'] >= 20 and raw_data['processing_days'] >= 30:
                extra_score = 15
                nonlinear_adjustment += extra_score
                nonlinear_reasons.append(f"High severity issue with long processing time (+{extra_score}pts)")
            
            # 1.2 跨ECU和跨领域的复杂问题 (ECU Transfer + Domain Transfer)
            if raw_data['ecu_pingpong'] >= 3 and raw_data['domain_pingpong'] >= 3:
                extra_score = 10
                nonlinear_adjustment += extra_score
                nonlinear_reasons.append(f"Complex cross-ECU and cross-domain issue (+{extra_score}pts)")
            
            # 1.3 严重的阻塞问题 (Matrix + Classification)
            if dimension_scores['matrix'] >= 24 and dimension_scores['classification'] >= 20:
                extra_score = 15
                nonlinear_adjustment += extra_score
                nonlinear_reasons.append(f"Critical blocking issue (+{extra_score}pts)")
            
            # 2. 时间衰减与加速 - 问题未解决时间越长，风险指数增加
            if raw_data['processing_days'] > 30:
                # 指数增长模型：超过30天后，每增加10天风险额外增加5分，但最多增加30分
                time_factor = min(30, ((raw_data['processing_days'] - 30) / 10) * 5)
                nonlinear_adjustment += time_factor
                nonlinear_reasons.append(f"Extended processing time risk acceleration (+{time_factor:.1f}pts)")
            
            # 3. 复杂度阈值效应 - 子票数量、ECU转移次数等超过特定阈值后风险急剧增加
            
            # 3.1 超大规模父票
            if raw_data['parent_child'] == 'Parent' and raw_data['child_count'] > 10:
                extra_score = min(25, (raw_data['child_count'] - 10) * 2.5)
                nonlinear_adjustment += extra_score
                nonlinear_reasons.append(f"Extremely large parent ticket with {raw_data['child_count']} children (+{extra_score:.1f}pts)")
            
            # 3.2 ECU频繁转移
            if raw_data['ecu_pingpong'] > 5:
                # 使用对数函数模拟边际递减效应
                extra_score = min(20, 10 * math.log(1 + (raw_data['ecu_pingpong'] - 5) / 2))
                nonlinear_adjustment += extra_score
                nonlinear_reasons.append(f"Extreme ECU transfer complexity (+{extra_score:.1f}pts)")
            
            # 将非线性调整添加到总分和原因中
            if nonlinear_adjustment > 0:
                score += nonlinear_adjustment
                reasons.append(f"--- Non-linear adjustments: +{nonlinear_adjustment:.1f}pts ---")
                reasons.extend(nonlinear_reasons)
            
            return score, reasons
        
        # 计算当前ticket的风险分数
        child_score, child_reasons = calculate_single_risk_score(row)
        final_score = child_score
        final_reasons = child_reasons.copy()
        is_master_score = False
        
        # 检查是否为Child ticket，如果是，还需要计算master ticket的风险分数
        parent_child = row.get('parent_child', '')
        parent_info = row.get('parent', {})
        
        # 从parent字段中提取master_id
        master_id = None
        if isinstance(parent_info, dict) and 'id' in parent_info:
            master_id = parent_info['id']
        
        if parent_child in ['Child', 'Child (candidate)'] and master_id and str(master_id).strip():
            # 尝试获取master ticket信息
            master_row = None
            
            # 首先尝试从当前ddf中查找master ticket
            try:
                master_id_str = str(master_id)
                possible_master = ddf[ddf['id'].astype(str) == master_id_str]
                if not possible_master.empty:
                    master_row = possible_master.iloc[0].to_dict()
            except:
                pass
            # 如果在当前ddf中没找到，尝试从预加载的master数据中获取
            if master_row is None and hasattr(calculate_topissue_risk_score, 'master_data_cache'):
                master_cache = calculate_topissue_risk_score.master_data_cache
                if master_id_str in master_cache:
                    master_row = master_cache[master_id_str].copy()
                    
                    # 为master row添加必要的字段以便风险计算
                    if 'parent_child' not in master_row:
                        # 检查master的relation_to_udf来确定它是Parent
                        relation_to_udf = master_row.get('relation_to_udf', '')
                        if relation_to_udf and str(relation_to_udf).strip():
                            master_row['parent_child'] = 'Parent'
                            # 计算子票数量
                            try:
                                child_ids = str(relation_to_udf).split(',')
                                master_row['子票数量'] = len([id.strip() for id in child_ids if id.strip()])
                            except:
                                master_row['子票数量'] = 0
                        else:
                            master_row['parent_child'] = ''
                            master_row['子票数量'] = 0
                    
                    # 添加其他可能需要的字段的默认值
                    if 'ecu_no_of_changes_udf' not in master_row:
                        master_row['ecu_no_of_changes_udf'] = master_row.get('ecu_no_of_changes_udf', 0)
                    if 'domain_pingpong_display' not in master_row:
                        master_row['domain_pingpong_display'] = master_row.get('domain_pingpong_count', 0)
                    if '子票数量' not in master_row:
                        master_row['子票数量'] = 0
                    if 'processing_cycle_days' not in master_row:
                        master_row['processing_cycle_days'] = 0
                    if 'Shift_PU' not in master_row:
                        master_row['Shift_PU'] = ''
            
            # 如果找到了master ticket，计算其风险分数
            if master_row is not None:
                master_score, master_reasons = calculate_single_risk_score(master_row)
                
                # 比较child和master的分数，取较高者
                if master_score > child_score:
                    final_score = master_score
                    final_reasons = master_reasons
                    is_master_score = True
                # 如果分数相等或child分数更高，保持原有的child分数和原因
        
        # 根据总分确定TopIssue等级 (总分可能超过200分，因为有非线性调整)
        if final_score >= 140:
            topissue_level = "Extremely High Risk"
        elif final_score >= 100:
            topissue_level = "High Risk"
        elif final_score >= 60:
            topissue_level = "Medium Risk"
        elif final_score >= 30:
            topissue_level = "Low Risk"
        else:
            topissue_level = ""
        
        # 生成推荐理由 - 简洁清晰的4个核心评估角度
        def generate_concise_recommendation(ticket_row, score):
            """
            Generate concise recommendation based on 4 core assessment dimensions:
            1. Severity (Matrix + Classification) - Dimensions 1&2
            2. High Runner (ECU + Domain transfers) - Dimensions 3&4  
            3. Complexity (Parent + Child relationships) - Dimensions 5&6
            4. Processing Efficiency (Processing cycle + Shift PU) - Dimensions 7&8
            """
            recommendation_parts = []
            
            # 1. SEVERITY Assessment
            severity_items = []
            matrix = ticket_row.get('matrix', '')
            if matrix:
                matrix_display = matrix.replace('matrix-', '').upper()
                severity_items.append(f"Matrix {matrix_display}")
            
            classification = ticket_row.get('classification', [])
            if isinstance(classification, list):
                if 'Showstopper_Confirmed' in classification:
                    severity_items.append("Showstopper Confirmed")
                elif 'Preventing Maturity Grade ConDrive' in classification:
                    severity_items.append("Preventing Maturity ConDrive")
                elif 'Showstopper_Candidate' in classification:
                    severity_items.append("Showstopper Candidate")
                elif 'Obstructing Maturity Grade ConDrive' in classification:
                    severity_items.append("Obstructing Maturity ConDrive")
                elif 'Homologation L-labelled' in classification:
                    severity_items.append("Homologation L-labelled")
            
            if severity_items:
                recommendation_parts.append(f"SEVERITY: {'; '.join(severity_items)}")
            
            # 2. HIGH RUNNER Assessment - 使用新的路径显示格式
            high_runner_items = []
            
            # ECU转移 - 尝试使用格式化后的路径，否则使用数字
            ecu_path = ticket_row.get('ecu_pingpong_display', '')
            if ecu_path and str(ecu_path) != 'No change' and str(ecu_path).strip():
                # 如果已经是格式化的路径（包含转移次数），直接使用
                if ', ' in str(ecu_path) and ' -> ' in str(ecu_path):
                    high_runner_items.append(f"ECU {ecu_path}")
                else:
                    # 否则使用原有逻辑
                    ecu_pingpong = ticket_row.get('ecu_no_of_changes_udf', 0)
                    if pd.notna(ecu_pingpong) and ecu_pingpong > 0:
                        high_runner_items.append(f"ECU transfer {ecu_pingpong} times")
            else:
                # 回退到原始数字
                ecu_pingpong = ticket_row.get('ecu_no_of_changes_udf', 0)
                if pd.notna(ecu_pingpong) and ecu_pingpong > 0:
                    high_runner_items.append(f"ECU transfer {ecu_pingpong} times")
            
            # Domain转移 - 尝试使用格式化后的路径，否则使用数字
            domain_path = ticket_row.get('domain_pingpong_display', '')
            if isinstance(domain_path, str) and domain_path != 'No change' and domain_path.strip():
                # 如果已经是格式化的路径（包含转移次数），直接使用
                if ', ' in domain_path and ' -> ' in domain_path:
                    high_runner_items.append(f"Domain {domain_path}")
                else:
                    # 检查是否是数字，如果是则使用原有格式
                    try:
                        domain_count = int(domain_path)
                        if domain_count > 0:
                            high_runner_items.append(f"Domain transfer {domain_count} times")
                    except:
                        # 不是数字，可能是其他格式，直接使用
                        high_runner_items.append(f"Domain: {domain_path}")
            else:
                # 回退到检查数字字段
                domain_pingpong = ticket_row.get('domain_pingpong_count', 0)
                if pd.notna(domain_pingpong) and domain_pingpong > 0:
                    high_runner_items.append(f"Domain transfer {domain_pingpong} times")
            
            if high_runner_items:
                recommendation_parts.append(f"HIGH RUNNER: {'; '.join(high_runner_items)}")
            
            # 3. COMPLEXITY Assessment
            complexity_items = []
            parent_child = ticket_row.get('parent_child', '')
            if parent_child == 'Parent':
                child_count = ticket_row.get('子票数量', 0)
                if pd.notna(child_count) and child_count > 0:
                    complexity_items.append(f"{child_count} child tickets")
            elif parent_child == 'Child':
                master_child_count = ticket_row.get('子票数量', 0)
                if pd.notna(master_child_count) and master_child_count > 0:
                    complexity_items.append(f"Master has {master_child_count} children")
            
            if complexity_items:
                recommendation_parts.append(f"COMPLEXITY: {'; '.join(complexity_items)}")
            
            # 4. LONG RUNNER Assessment
            long_runner_items = []
            processing_days = ticket_row.get('processing_cycle_days', 0)
            if pd.notna(processing_days) and processing_days >= 7:
                long_runner_items.append(f"Cycle {processing_days} days")
            
            shift_pu = ticket_row.get('Shift_PU', '')
            if shift_pu and str(shift_pu).strip():
                long_runner_items.append(f"Shift {shift_pu}")
            
            if long_runner_items:
                recommendation_parts.append(f"LONG RUNNER: {'; '.join(long_runner_items)}")
            
            # Combine all parts with line breaks
            if recommendation_parts:
                return '\n'.join(recommendation_parts)
            else:
                return "No specific risk factors"
        
        recommend_reason = generate_concise_recommendation(row, final_score)
        
        # 构建topissue_display - 始终显示实际分数
        if final_score > 0:
            if is_master_score:
                topissue_display = f"{final_score}*"  # Master分数加星号
            else:
                topissue_display = str(final_score)    # 只显示数字分数
        else:
            topissue_display = "0"  # 零分显示为0
        
        return {
            'topissue_display': topissue_display,
            'topissue_recommend_reason': recommend_reason,
            'topissue_risk_score': final_score,
            'is_topissue': final_score >= 60,  # 60分以上认为是TopIssue
            'is_master_score': is_master_score
        }

    master_data_cache = {}
    try:
        if 'id' in ddf.columns and 'relation_to_udf' in ddf.columns and not ddf.empty:
            master_mask = ddf['relation_to_udf'].notna() & ddf['relation_to_udf'].astype(str).str.strip().ne('')
            if 'parent_child' in ddf.columns:
                master_mask = master_mask | (ddf['parent_child'].astype(str) == 'Parent')
            master_df_temp = ddf.loc[master_mask].copy()
            if not master_df_temp.empty:
                master_df_temp['id'] = master_df_temp['id'].astype(str)
                for _, row in master_df_temp.iterrows():
                    mid = row.get('id')
                    if mid:
                        master_data_cache[str(mid)] = row.to_dict()
        print(f"预加载了 {len(master_data_cache)} 个master票数据以提高性能")
    except Exception as e:
        print(f"警告：无法预加载master ticket数据: {e}")
        master_data_cache = {}

    calculate_topissue_risk_score.master_data_cache = master_data_cache

    # 添加缺失的字段
    print("添加缺失的字段...")
    
    # 添加domain_pingpong_display字段（从domain_pingpong_count或其他字段计算）
    if 'domain_pingpong_count' in ddf.columns:
        ddf['domain_pingpong_display'] = ddf['domain_pingpong_count']
    else:
        ddf['domain_pingpong_display'] = 0
    
    # 添加子票数量字段
    if '子票数量' not in ddf.columns:
        ddf['子票数量'] = 0
    
    # 添加processing_cycle_days字段
    if 'processing_cycle_days' not in ddf.columns:
        if 'creation_time' in ddf.columns:
            print("计算处理周期天数...")
            ddf['processing_cycle_days'] = ddf.apply(
                lambda row: calculate_processing_cycle_days(
                    row.get('id'), 
                    row.get('status_phase', ''), 
                    row.get('creation_time')
                ), axis=1
            )
        else:
            ddf['processing_cycle_days'] = 0

    # 新增逻辑：为父票计算其直接的子票数量
    if 'relation_to_udf' in ddf.columns and 'parent_child' in ddf.columns:
        def _count_linked_defects(relation_str):
            if not relation_str or pd.isna(relation_str):
                return 0
            try:
                # 假设relation_to_udf是逗号分隔的ID列表
                ids = str(relation_str).split(',')
                return len([id.strip() for id in ids if id.strip()])
            except:
                return 0

        # 只对 'Parent' 类型的票据应用此逻辑
        parent_mask = ddf['parent_child'] == 'Parent'
        if parent_mask.any():
            print("为 'Parent' 票据计算子票数量...")
            # 使用 relation_to_udf 字段来计算
            ddf.loc[parent_mask, '子票数量'] = ddf.loc[parent_mask, 'relation_to_udf'].apply(_count_linked_defects)
            print(f"已为 {parent_mask.sum()} 个 'Parent' 票据更新了子票数量。")


    # 应用新的TopIssue风险评分系统
    print("计算TopIssue风险评分...")
    topissue_results = ddf.apply(calculate_topissue_risk_score, axis=1)
    
    # 拆分结果到对应列
    ddf["topissue_display"] = topissue_results.apply(lambda x: x["topissue_display"])
    ddf["topissue_recommend_reason"] = topissue_results.apply(lambda x: x["topissue_recommend_reason"])
    ddf["topissue_risk_score"] = topissue_results.apply(lambda x: x["topissue_risk_score"])
    ddf["is_topissue"] = topissue_results.apply(lambda x: x["is_topissue"])
    ddf["is_master_score"] = topissue_results.apply(lambda x: x["is_master_score"])

    # 添加严重性分组（基于Matrix）
    def categorize_severity_group(matrix_value):
        """根据Matrix标签确定问题严重性分组"""
        if not matrix_value or not isinstance(matrix_value, str):
            return "General Issues"
        
        matrix_lower = matrix_value.lower()
        severe_matrices = [
            'matrix-1a', 'matrix-1b', 'matrix-1c', 'matrix-1d', 'matrix-1e',
            'matrix-2a', 'matrix-2b', 'matrix-2c', 'matrix-2d', 'matrix-3a'
        ]
        
        return "Critical Issues" if matrix_lower in severe_matrices else "General Issues"

    ddf["severity_group"] = ddf["matrix"].apply(categorize_severity_group)

    # 添加复杂度分类
    if "ecu_no_of_changes_udf" in ddf.columns:
        ddf["ECU Pingpong"] = ddf["ecu_no_of_changes_udf"]
        
        def categorize_complexity(pingpong_value):
            if pingpong_value == 0:
                return 'simple'
            elif pingpong_value in [1, 2]:
                return 'medium'
            elif pingpong_value > 2:
                return 'complex'
            else:
                return np.nan
        
        ddf['complexity'] = ddf['ECU Pingpong'].apply(categorize_complexity)

    ddf["is_critical_issue"] = ddf["severity_group"].astype(str).str.lower().str.contains("critical")
    if "complexity" in ddf.columns:
        ddf["is_complex_ticket"] = ddf["complexity"].astype(str).str.lower().eq("complex")
    if "processing_cycle_days" in ddf.columns:
        ddf["is_long_runner"] = pd.to_numeric(ddf["processing_cycle_days"], errors="coerce").fillna(0).ge(30)
    
    if 'project' not in ddf.columns:
        ddf['project'] = ''
    if 'market' not in ddf.columns:
        ddf['market'] = ''

    if 'program' in ddf.columns:
        empty_mask = ddf['project'].isna() | (ddf['project'].astype(str).str.strip() == '')
        if empty_mask.any():
            ddf.loc[empty_mask, 'project'] = ddf.loc[empty_mask, 'program'].fillna('').astype(str)

    empty_mask2 = ddf['project'].isna() | (ddf['project'].astype(str).str.strip() == '')
    if empty_mask2.any() and 'lead_model' in ddf.columns:
        ddf.loc[empty_mask2, 'project'] = ddf.loc[empty_mask2, 'lead_model'].fillna('').astype(str)
    
    # 处理 aida_english 字段
    if 'aidas' in ddf.columns:
        # 从aidas列表中提取第一个AIDA，然后应用extract_english
        ddf['aida_english'] = ddf['aidas'].apply(
            lambda x: extract_english(x[0]) if isinstance(x, list) and len(x) > 0 else 'Unknown'
        )
    elif 'product_areas' in ddf.columns:
        # 尝试从product_areas中提取
        ddf['aida_english'] = ddf['product_areas'].apply(
            lambda x: extract_english(safe_extract_name(x[0])) if isinstance(x, list) and len(x) > 0 else 'Unknown'
        )
    else:
        # 如果没有相关字段，设置为默认值
        ddf['aida_english'] = 'Unknown'
    
    # --- 新增：计算 top_aida ---
    print("计算缺陷数据的 top_aida...")
    if 'aidas' in ddf.columns:
        ddf['top_aida'] = ddf['aidas'].apply(get_top_req)
        print("top_aida 列计算完成。")
    else:
        print("警告: 缺少 'aidas' 列，无法计算 'top_aida'。")
        ddf['top_aida'] = '' # 创建空列以避免后续错误
    # --- top_aida 计算结束 ---
    
    # --- App/RSU项目映射 (已移至上方统一处理) ---

    # 提取Matrix标签
    def extract_matrix(tags):
        if isinstance(tags, list) and len(tags) > 0:
            matrix_tags = [tag for tag in tags if isinstance(tag, str) and tag.lower().startswith('matrix-')]
            return matrix_tags[0] if len(matrix_tags) > 0 else ""
        return ""
    
    ddf["matrix"] = ddf["tags"].apply(extract_matrix)
    
    # 添加 Domain 列 (从 solution_cluster_udf)
    if 'solution_cluster_udf' in ddf.columns:
        ddf["domain"] = ddf["solution_cluster_udf"].apply(
            lambda x: x["name"] if isinstance(x, dict) and "name" in x else ""
        )
    else:
        ddf["domain"] = ""
        
    # 添加 Classification 列 (从 reporting_class_udf)
    if 'reporting_class_udf' in ddf.columns:
        ddf["classification"] = ddf["reporting_class_udf"].apply(
             lambda x: [i.get("name", "") for i in x["data"] if isinstance(i, dict)]
                       if isinstance(x, dict) and "data" in x and isinstance(x["data"], list)
                       else []
        )
    else:
        ddf["classification"] = [[] for _ in range(len(ddf))]

    # 确保 classification 列没有 None 值
    ddf["classification"] = ddf["classification"].apply(lambda x: x if isinstance(x, list) else [])

    # 添加Matrix显示和排序值
    ddf["matrix_display"] = ddf["matrix"].apply(lambda x: x.replace("matrix-", "").upper() if isinstance(x, str) and x else "")
    # 确保 matrix_severity_order 函数已定义或导入
    try:
        ddf["matrix_order"] = ddf["matrix"].apply(matrix_severity_order)
    except NameError:
        print("警告: matrix_severity_order 函数未定义，matrix_order 列将不会被创建或填充。")
        # 可以选择在这里定义一个默认的排序逻辑或赋值为 NaN/None
        ddf["matrix_order"] = pd.NA 
     
    # --- Team 和 FVP 分配 (已移至上方统一处理) ---

    print("开始智能FV补全...")
    if 'fv' not in ddf.columns:
        ddf['fv'] = '未分类数据'
    else:
        ddf['fv'] = ddf['fv'].fillna('未分类数据')
    # --- 智能FV补全结束 ---

    # 从history补充缺失的solution cluster值
    ddf = enrich_solution_cluster_from_history(ddf)
    # 添加 Shift_PU 列的处理
    if 'sab_comment_udf' in ddf.columns:
        ddf['Shift_PU'] = ddf['sab_comment_udf'].apply(
            lambda x: x.get('name', '') if isinstance(x, dict) and 'name' in x else ''
        )
        print("已添加 Shift_PU 列，从 sab_comment_udf 字段提取 name 数据。")
    else:
        ddf['Shift_PU'] = ''
        print("警告: 未找到 sab_comment_udf 字段，Shift_PU 列已初始化为空值。")

    
    print("缺陷数据加载和处理完成。")
    
    # 增强PU填充
    ddf = enhance_pu_filling(ddf)
    
    # 处理状态字段 - 确保status_phase字段正确填充
    print("处理状态字段...")
    if 'phase.name' in ddf.columns:
        # 如果status_phase字段不存在或为空，从phase.name中提取
        if 'status_phase' not in ddf.columns:
            ddf['status_phase'] = ddf['phase.name']
        else:
            # 填充空的status_phase字段
            mask = ddf['status_phase'].isna() | (ddf['status_phase'] == '')
            ddf.loc[mask, 'status_phase'] = ddf.loc[mask, 'phase.name']
        
        # 统计status_phase分布
        status_counts = ddf['status_phase'].value_counts()
        print(f"状态字段处理完成，状态分布: {status_counts.head(10).to_dict()}")
    else:
        print("警告: 数据中没有phase.name字段，无法处理状态")
    
    return ddf

def enrich_ddf_with_master_info(ddf, master_file_path="defect/2025_defect_master.json"):
    """
    通过加载主票据文件，使用主票据信息来充实 ddf DataFrame。
    主票据文件中的 'relation_to_udf' 字段将被解析以获取所有子票ID，用于与 ddf 的 'id' 字段进行匹配。
    匹配成功后，主票据的 ID、其自身的 child ticket 列表 (来自 relation_to_udf) 及其 child count 将被添加到 ddf 中。
    """
    print("开始从数据库加载主票据信息以充实 ddf...")

    if ddf is None or ddf.empty:
        return ddf

    if not HAS_DB_CONFIG or not is_using_optimized_schema():
        return ddf

    years = None
    if 'year' in ddf.columns:
        try:
            years = sorted([int(y) for y in ddf['year'].dropna().unique().tolist() if str(y).strip().isdigit()])
        except Exception:
            years = None

    try:
        conn = sqlite3.connect(DB_PATH)
        try:
            query = """
                SELECT
                    defect_id as id,
                    relation_to as relation_to_udf,
                    phase as "phase.name",
                    status_phase
                FROM octane_defects
                WHERE parent_child_type = 'Parent' AND relation_to IS NOT NULL AND TRIM(relation_to) <> ''
            """
            params = []
            if years:
                placeholders = ",".join(["?"] * len(years))
                query += f" AND year IN ({placeholders})"
                params.extend(years)
            master_df = pd.read_sql_query(query, conn, params=params)
        finally:
            conn.close()
    except Exception as e:
        print(f"警告: 从数据库加载主票数据失败: {e}")
        return ddf

    if master_df is None or master_df.empty:
        print("警告: 数据库中未找到主票据数据。跳过充实步骤。")
        return ddf

    required_cols_master = ['id', 'relation_to_udf']
    missing_cols = [col for col in required_cols_master if col not in master_df.columns]
    if missing_cols:
        print(f"警告: 主票据文件 {master_file_path} 缺少必要列: {missing_cols}。可用列: {master_df.columns.tolist()}。跳过充实步骤。")
        return ddf

    if 'master_id' in ddf.columns and 'child_count_of_master' in ddf.columns:
        try:
            ddf2 = ddf.copy()
            ddf2['master_id'] = ddf2['master_id'].fillna('').astype(str)
            if 'master_status' not in ddf2.columns:
                ddf2['master_status'] = ''

            m = master_df.copy()
            m['id'] = m['id'].astype(str)
            status_key = 'phase.name' if 'phase.name' in m.columns else 'status_phase'
            master_status_map = dict(zip(m['id'], m[status_key].fillna('').astype(str)))

            if 'parent_child' in ddf2.columns:
                pc = ddf2['parent_child'].fillna('').astype(str)
            else:
                pc = pd.Series(['' for _ in range(len(ddf2))], index=ddf2.index, dtype=str)

            child_mask = pc.isin(['Child', 'Child (candidate)', 'Child (Candidate)'])
            if child_mask.any():
                mids = ddf2.loc[child_mask, 'master_id'].astype(str).str.strip()
                ddf2.loc[child_mask, 'master_status'] = mids.map(master_status_map).fillna('')

            return ddf2
        except Exception:
            return ddf

    def parse_relation_to_udf(relations_val):
        """解析relation_to_udf字段，支持字符串和数字类型"""
        if pd.isna(relations_val):
            return []
        
        # 处理数字类型（int, float）
        if isinstance(relations_val, (int, float)):
            return [str(relations_val)]
        
        # 处理字符串类型
        if isinstance(relations_val, str) and relations_val.strip():
            return [child_id.strip() for child_id in relations_val.split(',') if child_id.strip()]
        
        return []

    # 创建子票到主票的映射
    child_to_master_mapping = []
    
    for _, master_row in master_df.iterrows():
        master_id = str(master_row['id'])
        relation_to_udf = master_row.get('relation_to_udf', '')
        child_ids = parse_relation_to_udf(relation_to_udf)
        
        # 为每个子票ID创建一个映射记录
        for child_id in child_ids:
            child_to_master_mapping.append({
                'child_id': child_id,
                'master_id': master_id,
                'master_relation_children_list': child_ids,
                'master_relation_children_count': len(child_ids)
            })
    
    if not child_to_master_mapping:
        print("警告: 没有找到有效的子票到主票映射。跳过充实步骤。")
        return ddf
    
    # 转换为DataFrame
    mapping_df = pd.DataFrame(child_to_master_mapping)
    mapping_df = mapping_df.drop_duplicates(subset=['child_id'], keep='first')
    
    if 'id' not in ddf.columns:
        print("警告: ddf 中缺少 'id' 列。无法合并主票据信息。")
        return ddf
    ddf['id_str_for_merge'] = ddf['id'].astype(str)

    print(f"准备合并主票据信息到 ddf。ddf 行数: {len(ddf)}, 主票据映射信息行数: {len(mapping_df)}")
    ddf_enriched = pd.merge(ddf, mapping_df, left_on='id_str_for_merge', right_on='child_id', how='left')
    
    if 'child_id' in ddf_enriched.columns:
        ddf_enriched = ddf_enriched.drop(columns=['child_id'])
    if 'id_str_for_merge' in ddf_enriched.columns:
        ddf_enriched = ddf_enriched.drop(columns=['id_str_for_merge'])
        
    rename_map = {
        'master_relation_children_list': 'child_ids_of_master',
        'master_relation_children_count': 'child_count_of_master'
    }
    ddf_enriched = ddf_enriched.rename(columns=rename_map)

    # Fill NaNs for newly added columns
    if 'master_id' in ddf_enriched.columns:
        ddf_enriched['master_id'] = ddf_enriched['master_id'].fillna('')
    
    if 'child_ids_of_master' in ddf_enriched.columns:
        # Ensure that NaN values (where no merge occurred) are replaced with empty lists
        # Apply this specifically to rows where the value is not already a list (i.e., it's NaN from the merge)
        mask_needs_empty_list = ddf_enriched['child_ids_of_master'].apply(lambda x: not isinstance(x, list))
        if mask_needs_empty_list.any():
            ddf_enriched.loc[mask_needs_empty_list, 'child_ids_of_master'] = pd.Series([[] for _ in range(mask_needs_empty_list.sum())], index=ddf_enriched.index[mask_needs_empty_list])
            
    if 'child_count_of_master' in ddf_enriched.columns:
        ddf_enriched['child_count_of_master'] = ddf_enriched['child_count_of_master'].fillna(0).astype(int)

    # 设置parent_child字段
    def determine_parent_child_status(row):
        """根据master_id和其他信息确定parent_child状态"""
        master_id = row.get('master_id', '')
        
        # 如果有有效的master_id（不为空且不为'N/A'），则为Child
        if master_id and str(master_id).strip() and str(master_id).strip().lower() != 'n/a':
            return 'Child'
        
        # 如果有child_count_of_master且大于0，或者有relation_to_udf字段且不为空，则为Parent
        child_count = row.get('child_count_of_master', 0)
        relation_to_udf = row.get('relation_to_udf', '')
        
        if child_count > 0 or (relation_to_udf and str(relation_to_udf).strip()):
            return 'Parent'
        
        # 默认情况下，如果既没有master_id也没有子票，则状态未知
        return ''
    
    # 只有当parent_child字段不存在或为空时才设置
    if 'parent_child' not in ddf_enriched.columns:
        ddf_enriched['parent_child'] = ddf_enriched.apply(determine_parent_child_status, axis=1)
    else:
        # 如果parent_child字段存在但为空，则填充
        mask_empty_parent_child = ddf_enriched['parent_child'].isna() | (ddf_enriched['parent_child'] == '')
        if mask_empty_parent_child.any():
            ddf_enriched.loc[mask_empty_parent_child, 'parent_child'] = ddf_enriched.loc[mask_empty_parent_child].apply(determine_parent_child_status, axis=1)

    # 设置master_status字段
    def get_master_status(row):
        """获取主票状态"""
        if row.get('parent_child') not in ['Child', 'Child (candidate)']:
            return ""
        
        master_id = row.get('master_id')
        if not master_id or pd.isna(master_id):
            return ""
        
        # 从master_df中查找主票状态
        master_id_str = str(master_id)
        master_df_copy = master_df.copy()
        master_df_copy['id'] = master_df_copy['id'].astype(str)
        
        parent_info = master_df_copy[master_df_copy['id'] == master_id_str]
        if not parent_info.empty:
            parent_row = parent_info.iloc[0]
            # 从phase.name字段获取状态
            phase_name = parent_row.get('phase.name', '')
            if phase_name:
                return phase_name
            # 如果phase.name为空，尝试其他可能的字段
            return parent_row.get('status_phase', '')
        
        return ""
    
    # 添加master_status字段
    ddf_enriched['master_status'] = ddf_enriched.apply(get_master_status, axis=1)

    # 补偿机制：为没有master_id的child ticket从其relation_to_udf字段获取主票信息
    def apply_compensation_for_missing_master_info(row):
        """为没有master_id的child ticket提供补偿机制"""
        # 只处理被识别为Child但没有master_id的记录
        if (row.get('parent_child') == 'Child' and 
            (not row.get('master_id') or pd.isna(row.get('master_id')) or row.get('master_id') == '')):
            
            # 从child ticket自身的relation_to_udf字段获取主票ID
            relation_to_udf = row.get('relation_to_udf', '')
            potential_master_id = None
            
            # 处理数字类型的relation_to_udf
            if isinstance(relation_to_udf, (int, float)):
                potential_master_id = str(relation_to_udf)
            # 处理字符串类型的relation_to_udf
            elif isinstance(relation_to_udf, str) and relation_to_udf.strip():
                potential_master_id = relation_to_udf.strip()
            
            if potential_master_id:
                # 在master_df中查找这个主票
                master_df_copy = master_df.copy()
                master_df_copy['id'] = master_df_copy['id'].astype(str)
                
                master_info = master_df_copy[master_df_copy['id'] == potential_master_id]
                if not master_info.empty:
                    master_row = master_info.iloc[0]
                    
                    # 更新master_id
                    row['master_id'] = potential_master_id
                    
                    # 更新master_status
                    phase_name = master_row.get('phase.name', '')
                    if phase_name:
                        row['master_status'] = phase_name
                    else:
                        row['master_status'] = master_row.get('status_phase', '')
                    
                    # 获取主票的子票信息
                    master_relation_to_udf = master_row.get('relation_to_udf', '')
                    if master_relation_to_udf:
                        child_ids = parse_relation_to_udf(master_relation_to_udf)
                        row['child_ids_of_master'] = child_ids
                        row['child_count_of_master'] = len(child_ids)
        
        return row
    
    # 应用补偿机制
    print("应用补偿机制，为没有master_id的child ticket补充主票信息...")
    before_compensation = len(ddf_enriched[(ddf_enriched['parent_child'] == 'Child') & 
                                          (ddf_enriched['master_id'].isna() | (ddf_enriched['master_id'] == ''))])
    
    ddf_enriched = ddf_enriched.apply(apply_compensation_for_missing_master_info, axis=1)
    
    after_compensation = len(ddf_enriched[(ddf_enriched['parent_child'] == 'Child') & 
                                         (ddf_enriched['master_id'].isna() | (ddf_enriched['master_id'] == ''))])
    
    compensated_count = before_compensation - after_compensation
    if compensated_count > 0:
        print(f"补偿机制成功为 {compensated_count} 个child ticket补充了主票信息")
    else:
        print("补偿机制未找到可补充的child ticket")

    print(f"主票据信息合并完成。ddf 更新后行数: {len(ddf_enriched)}")
    
    # 处理状态字段 - 确保status_phase字段正确填充
    print("处理合并后数据的状态字段...")
    if 'phase.name' in ddf_enriched.columns:
        # 如果status_phase字段不存在或为空，从phase.name中提取
        if 'status_phase' not in ddf_enriched.columns:
            ddf_enriched['status_phase'] = ddf_enriched['phase.name']
        else:
            # 填充空的status_phase字段
            mask = ddf_enriched['status_phase'].isna() | (ddf_enriched['status_phase'] == '')
            ddf_enriched.loc[mask, 'status_phase'] = ddf_enriched.loc[mask, 'phase.name']
        
        # 统计status_phase分布
        status_counts = ddf_enriched['status_phase'].value_counts()
        print(f"合并后状态字段处理完成，状态分布: {status_counts.head(10).to_dict()}")
    else:
        print("警告: 合并后数据中没有phase.name字段，无法处理状态")
    
    return ddf_enriched

def matrix_severity_order(matrix_value):
    """返回Matrix的排序值，1A最高(值最小)，未分类最低(值最大)"""
    if not matrix_value or not isinstance(matrix_value, str):
        return 999
    
    # 处理 'matrix-' 前缀 (如果存在)
    matrix_value = matrix_value.lower().replace('matrix-','')
    
    match = re.match(r'(\d)([a-e])', matrix_value)
    if not match:
        # 尝试匹配没有前缀的情况，以防万一
        match = re.match(r'(\d)([a-e])', matrix_value.lower())
        if not match:
             return 999
    
    number = int(match.group(1))
    letter = match.group(2).lower()
    
    # 计算排序值：数字*10 + 字母顺序(a=0, b=1, ...)
    letter_value = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4}.get(letter, 5)
    return number * 10 + letter_value

# ===== 缺陷历史数据处理 (用于 Long Runner) =====

def calculate_defect_lifecycles(history_dir="history"):
    """
    处理 history 文件夹中的 JSON 文件，计算每个缺陷从创建到最终状态（解决或拒绝）的时长。

    Args:
        history_dir (str): 包含缺陷历史 JSON 文件的目录路径。

    Returns:
        pandas.DataFrame: 包含 'defect_id', 'creation_time', 'final_time', 'duration_days', 'final_status' 的 DataFrame。
                         只包含已达到最终状态的缺陷。
    """
    lifecycle_data = []
    histories = list(_iter_histories_from_db())
    for _, history in histories:
        if not history or 'data' not in history or not history['data']:
            continue

        defect_id = None
        creation_time = None
        final_time = None
        final_status = None
        status_changes = []

        # 按时间戳升序排序历史记录
        history_entries = sorted(history['data'], key=lambda x: x.get('timestamp', ''))

        for entry in history_entries:
            ts_str = entry.get('timestamp')
            if not ts_str:
                continue

            try:
                # 尝试解析多种可能的日期格式
                current_time = pd.to_datetime(ts_str, errors='coerce')
                if pd.isna(current_time):
                     # 尝试其他格式，例如不带毫秒的
                     current_time = pd.to_datetime(ts_str.split('.')[0], errors='coerce', format='%Y-%m-%dT%H:%M:%S')
                     if pd.isna(current_time):
                         continue
            except Exception as e:
                continue

            if defect_id is None:
                defect_id = entry.get('entity_id')

            # 将首次出现的时间戳视为创建时间
            if creation_time is None:
                creation_time = current_time

            # 检查 change_set 中是否有状态变更
            change_set = entry.get('change_set', [])
            for change in change_set:
                # 假设状态字段名为 'phase' 或 'status_phase' (基于 load_defect_data)
                # 注意：这里可能需要根据实际 history 文件中的字段名调整
                if isinstance(change, dict) and change.get('field_name') in ['phase', 'status_phase', 'Status Phase']:
                    status_value = change.get('valueName') # 假设状态存储在 valueName
                    if not status_value: # 有时可能在 value 中
                        status_value = change.get('value')

                    if status_value:
                        status_changes.append({'time': current_time, 'status': status_value})

        if not defect_id or creation_time is None:
            continue

        # 查找最终状态 ('06 Solved' 或 '09 Rejected') 的首次出现时间
        final_states = ['06 Solved', '09 Rejected', 'Solved', 'Rejected'] # 添加一些可能的变体
        solved_rejected_entries = [
            sc for sc in status_changes
            if any(final_state.lower() in sc['status'].lower() for final_state in final_states)
        ]

        if solved_rejected_entries:
            # 按时间排序，取第一个达到最终状态的时间
            solved_rejected_entries.sort(key=lambda x: x['time'])
            final_entry = solved_rejected_entries[0]
            final_time = final_entry['time']
            final_status = final_entry['status']

            # 计算时长（天）
            duration = final_time - creation_time
            duration_days = duration.total_seconds() / (60 * 60 * 24)

            lifecycle_data.append({
                'defect_id': defect_id,
                'creation_time': creation_time,
                'final_time': final_time,
                'duration_days': duration_days,
                'final_status': final_status
            })
        # else:
            # 如果没有找到最终状态，则不添加到结果中，因为我们只关心已完成的生命周期

    if not lifecycle_data:
        # 返回一个空的 DataFrame，并指定列名和类型，以避免后续操作出错
        return pd.DataFrame(columns=['defect_id', 'creation_time', 'final_time', 'duration_days', 'final_status']).astype({
            'defect_id': str,
            'creation_time': 'datetime64[ns]',
            'final_time': 'datetime64[ns]',
            'duration_days': float,
            'final_status': str
        })


    return pd.DataFrame(lifecycle_data)

# ===== 测试管理数据处理 =====

def preprocess_test_data(df):
    """预处理测试数据，清理无效值并添加aida_english列"""
    df_clean = df.copy()
    # 定义需要清理的列和对应的无效值/占位符
    columns_to_clean = {
        'test_week': '未知周',
        'project': '未知项目',
        'top_aida': '未知AIDA',
        'run_status': '未知状态'
    }
    
    # 遍历需要清理的列
    for col, placeholder in columns_to_clean.items():
        # 检查列是否存在于DataFrame中
        if col in df_clean.columns:
            # 移除包含空字符串、占位符、None或NaN的行
            df_clean = df_clean[~df_clean[col].isin(['', placeholder, None, np.nan])]
        else:
            print(f"警告: 列 '{col}' 在预处理时未找到。")
    
    # 检查 'top_aida' 列是否存在，然后应用 extract_english
    if 'top_aida' in df_clean.columns:
        df_clean['aida_english'] = df_clean['top_aida'].apply(extract_english)
    else:
        print("警告: 列 'top_aida' 未找到，无法创建 'aida_english'。")
        df_clean['aida_english'] = 'Unknown'
    
    return df_clean

# 常量定义
SEVERITY_COLORS = {
    'Critical Issues': '#d62728',
    'General Issues': '#2ca02c'
}

CHART_HEIGHT = 600

def apply_filters(df, projects=None, test_weeks=None, aidas=None, statuses=None, pus=None):
    """
    通用筛选函数，支持多选筛选
    
    参数:
        df (DataFrame): 需要筛选的数据框
        projects (list): 项目列表
        test_weeks (list): 测试周列表  
        aidas (list): AIDA列表
        statuses (list): 状态列表
        pus (list): PU列表
        
    返回:
        DataFrame: 筛选后的数据框
    """
    filtered = df.copy()
    
    if projects and len(projects) > 0:
        filtered = filtered[filtered['project'].isin(projects)]
    if test_weeks and len(test_weeks) > 0:
        filtered = filtered[filtered['test_week'].isin(test_weeks)]
    if aidas and len(aidas) > 0:
        filtered = filtered[filtered['aida_english'].isin(aidas)]
    if statuses and len(statuses) > 0:
        # 检查是否包含特殊状态 "09-concluded without action (child)"
        if "09-concluded without action (child)" in statuses:
            # 创建普通状态列表（移除特殊状态）
            normal_statuses = [s for s in statuses if s != "09-concluded without action (child)"]
            
            # 创建新的子票筛选条件：
            # 1. 票据是Child类型
            # 2. 票据的phase是09或01
            # 3. 主票的状态不是09、06、10
            child_mask = (
                (filtered['parent_child'] == 'Child') &
                (filtered['status_phase'].isin(['09-Concluded without action', '01-New']))
            )
            
            # 进一步检查这些子票的主票状态
            if not filtered[child_mask].empty:
                # 获取所有主票ID
                master_ids = filtered[child_mask]['master_id'].dropna()
                if len(master_ids) > 0:
                    try:
                        # 检查主票是否为需要排除的状态
                        excluded_master_statuses = ['06-Concluded', '09-Concluded without action', '10-Rejected']
                        master_id_strs = master_ids.astype(str).tolist()
                        master_rows = filtered[filtered['id'].astype(str).isin(master_id_strs)] if 'id' in filtered.columns else pd.DataFrame()
                        if not master_rows.empty and 'phase.name' in master_rows.columns:
                            excluded_masters = master_rows[master_rows['phase.name'].isin(excluded_master_statuses)]['id'].astype(str).tolist()
                        elif not master_rows.empty and 'status_phase' in master_rows.columns:
                            excluded_masters = master_rows[master_rows['status_phase'].isin(excluded_master_statuses)]['id'].astype(str).tolist()
                        else:
                            excluded_masters = []
                        
                        # 过滤掉主票状态为排除状态的子票
                        if excluded_masters:
                            child_mask = child_mask & (~filtered['master_id'].astype(str).isin(excluded_masters))
                    except Exception as e:
                        print(f"警告：无法加载主票状态用于筛选: {e}")
            
            # 合并筛选条件
            if normal_statuses:
                # 有其他正常状态，需要与子票合并
                normal_mask = filtered['status_phase'].isin(normal_statuses)
                combined_mask = normal_mask | child_mask
                filtered = filtered[combined_mask]
            else:
                # 只选择了特殊状态
                filtered = filtered[child_mask]
        else:
            # 没有特殊状态，使用常规筛选
            filtered = filtered[filtered['status_phase'].isin(statuses)]
    if pus and len(pus) > 0:
        filtered = filtered[filtered['pu'].isin(pus)]
        
    return filtered

def load_test_data():
    """加载并返回测试管理数据 DataFrame (tdf)，包含来自 mr/*.json 和 aida/*.xlsx 的数据。"""
    # 如果是reloader进程，返回空DataFrame避免数据加载
    if IS_RELOADER:
        print("🔄 data_processor.load_test_data: Reloader进程跳过数据加载")
        return pd.DataFrame()
    print("开始加载测试管理数据...")
    expected_cols = [
        'model', 'test_id', 'test_name', 'author_name', 'test_event',
        'tester', 'aida_count', 'aida', 'pu', 'run_status',
        'finished_udf', 'test_week', 'project', 'top_aida', 'fv', 'team', 'fvp', 'lead_model'
    ]
    if not (HAS_DB_CONFIG and HAS_UNIFIED_LOADER):
        return pd.DataFrame(columns=expected_cols)

    try:
        config = DataSourceConfig()
        config.config = {**config.config, "mode": "db_only", "priority": "database", "fallback": False}
        loader = UnifiedDataLoader(db_path=DB_PATH, config=config, use_connection_pool=True)
        tdf = loader.load_tests(report_period=None, team=DEFAULT_TEAM)
        if tdf is None or tdf.empty:
            print("警告: 数据库中未找到测试数据。")
            return pd.DataFrame(columns=expected_cols)
        print(f"✅ 从数据库加载 {len(tdf)} 条测试数据")
    except Exception as e:
        print(f"⚠️ 从数据库加载测试数据失败: {e}")
        raise

    if tdf is None or tdf.empty:
        return pd.DataFrame(columns=expected_cols)

    # --- 数据转换和特征工程 ---
    print("开始进行数据转换和特征工程...")

    if 'exec_model_series_udf' not in tdf.columns and 'exec_model_series' in tdf.columns:
        tdf['exec_model_series_udf'] = tdf['exec_model_series'].apply(lambda x: {'name': x} if pd.notna(x) else {'name': ''})
    if 'test' not in tdf.columns and ('test_id' in tdf.columns or 'test_name' in tdf.columns):
        tdf['test'] = tdf.apply(lambda row: {'id': row.get('test_id', ''), 'name': row.get('test_name', '')}, axis=1)
    if 'author' in tdf.columns:
        tdf['author'] = tdf['author'].apply(lambda x: x if isinstance(x, dict) else {'full_name': x if pd.notna(x) else ''})
    elif 'author_name' in tdf.columns:
        tdf['author'] = tdf['author_name'].apply(lambda x: {'full_name': x} if pd.notna(x) else {'full_name': ''})
    if 'release' in tdf.columns:
        tdf['release'] = tdf['release'].apply(lambda x: x if isinstance(x, dict) else {'name': x if pd.notna(x) else ''})
    if 'run_by' in tdf.columns:
        tdf['run_by'] = tdf['run_by'].apply(lambda x: x if isinstance(x, dict) else {'full_name': x if pd.notna(x) else ''})
    if 'product_areas' in tdf.columns:
        def _wrap_product_areas(val):
            if isinstance(val, dict):
                return val
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return {'total_count': 0, 'data': []}
            if isinstance(val, list):
                data = [{'name': item} for item in val if isinstance(item, str) and item]
                return {'total_count': len(data), 'data': data}
            if isinstance(val, str):
                items = [v.strip() for v in val.split(',') if v.strip()]
                data = [{'name': item} for item in items]
                return {'total_count': len(data), 'data': data}
            return {'total_count': 0, 'data': []}
        tdf['product_areas'] = tdf['product_areas'].apply(_wrap_product_areas)
    if 'set_udf' not in tdf.columns and 'set_field' in tdf.columns:
        tdf['set_udf'] = tdf['set_field'].apply(lambda x: {'name': x} if pd.notna(x) else {'name': ''})
    if 'status' in tdf.columns:
        tdf['status'] = tdf['status'].apply(lambda x: x if isinstance(x, dict) else {'name': x if pd.notna(x) else ''})
    if 'finished_udf' not in tdf.columns and 'finished' in tdf.columns:
        tdf['finished_udf'] = tdf['finished']
    if 'target_ecu_conf_udf' not in tdf.columns and 'target_ecu_conf' in tdf.columns:
        tdf['target_ecu_conf_udf'] = tdf['target_ecu_conf']

    # 安全地提取嵌套字段
    def safe_get_name(x):
        return x.get("name", "") if isinstance(x, dict) else ""
    def safe_get_id(x):
        return x.get("id", "") if isinstance(x, dict) else ""
    def safe_get_fullname(x):
        return x.get("full_name", "") if isinstance(x, dict) else ""
    def safe_get_totalcount(x):
        return x.get("total_count", 0) if isinstance(x, dict) else 0 # 返回 0 而不是空字符串
    def safe_get_datanames(x):
        return [i.get("name", "") for i in x.get("data", []) if isinstance(i, dict)] if isinstance(x, dict) else []

    # 应用转换
    tdf["model"] = tdf["exec_model_series_udf"].apply(safe_get_name)
    tdf["test_id"] = tdf["test"].apply(safe_get_id)
    tdf["test_name"] = tdf["test"].apply(safe_get_name)
    tdf["author_name"] = tdf["author"].apply(safe_get_fullname)
    tdf["test_event"] = tdf["release"].apply(safe_get_name)
    tdf["tester"] = tdf["run_by"].apply(safe_get_fullname)
    tdf["aida_count"] = tdf["product_areas"].apply(safe_get_totalcount)
    tdf["aida"] = tdf["product_areas"].apply(safe_get_datanames)
    tdf["pu"] = tdf["set_udf"].apply(safe_get_name)
    tdf["run_status"] = tdf["status"].apply(safe_get_name)

    # 时间处理
    if 'finished_udf' in tdf.columns:
        # 检查是否有非 None 和非空字符串的值
        valid_timestamps = tdf['finished_udf'].dropna().astype(str).str.strip().replace('', pd.NA).dropna()
        if not valid_timestamps.empty:
            # 尝试转换，对无效格式填充 NaT
            tdf['finished_udf_dt'] = pd.to_datetime(
                tdf['finished_udf'].astype(str).str.replace('T', ' ').str.replace('Z', ''),
                errors='coerce', # 无效格式转为 NaT
                format='%Y-%m-%d %H:%M:%S'
            )
            # 计算 test_week，仅对有效日期进行计算
            tdf['test_week'] = np.where(
                tdf['finished_udf_dt'].notna(),
                # 使用 .dt.strftime('%Y-CW%V') 格式可能更符合 ISO 周标准
                tdf['finished_udf_dt'].dt.strftime('%y-CW%V'), # %y for 2-digit year, %V for ISO week
                # 对无效日期填充 'Future Planning'
                'Future Planning'
            )
            # 可以选择删除临时的 datetime 列
            # tdf = tdf.drop(columns=['finished_udf_dt'])
        else:
            print("警告: 'finished_udf' 列不包含有效的时间戳数据，无法计算 'test_week'。将使用 'Future Planning' 填充")
            tdf['test_week'] = 'Future Planning'
    else:
        print("警告: DataFrame 中缺少 'finished_udf' 列，无法计算 'test_week'。将使用 'Future Planning' 填充")
        tdf['test_week'] = 'Future Planning'

    # --- 生成top_aida列用于项目分类 ---
    print("生成top_aida列用于项目分类...")
    # 添加 top_aida 列 (从 aida 列表的第一个元素提取)
    tdf['top_aida'] = tdf['aida'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None)
    
    # 项目分类 - 按三步分离策略
    print("开始项目分类...")
    tdf['project'] = '' # 初始化列
    name_col = 'name' # 基于 name 列进行分类
    
    if name_col not in tdf.columns:
        print(f"警告: DataFrame 中缺少 '{name_col}' 列，无法进行项目分类。将 'project' 列填充为 'Unknown'。")
        tdf['project'] = 'Unknown'
    else:
        # 确保相关列是字符串类型，处理 NaN
        tdf[name_col] = tdf[name_col].fillna('').astype(str)
        if 'target_ecu_conf_udf' in tdf.columns:
            tdf['target_ecu_conf_udf'] = tdf['target_ecu_conf_udf'].fillna('').astype(str)
        
        # --- 第一步：用原来的RSU正则把RSU项目分离出来 ---
        print("第一步：分离RSU项目...")
        tdf.loc[tdf[name_col].str.contains('DTSV_CHINA-RSU', na=False) & (tdf.project==''), 'project'] = 'RSU'
        tdf.loc[tdf[name_col].str.contains('RSU', na=False) & (tdf.project==''), 'project'] = 'RSU'
        rsu_count = (tdf['project'] == 'RSU').sum()
        print(f"RSU项目分配完成，共 {rsu_count} 条记录")
        
        # --- 第二步：用target_ecu_conf_udf字段判断 ---
        print("第二步：基于target_ecu_conf_udf字段判断...")
        if 'target_ecu_conf_udf' in tdf.columns:
            # My BMW -> App项目 (忽略大小写)
            my_bmw_mask = tdf['target_ecu_conf_udf'].str.contains('My BMW', na=False, case=False) & (tdf.project=='')
            tdf.loc[my_bmw_mask, 'project'] = 'App'
            app_count = my_bmw_mask.sum()
            print(f"基于target_ecu_conf_udf包含'My BMW'，分配App项目 {app_count} 条记录")
            
            # IDCEVO -> IDCevo项目 (优先级高于IDC，忽略大小写)
            idcevo_mask = tdf['target_ecu_conf_udf'].str.contains('IDCEVO', na=False, case=False) & (tdf.project=='')
            tdf.loc[idcevo_mask, 'project'] = 'IDCevo'
            idcevo_count = idcevo_mask.sum()
            print(f"基于target_ecu_conf_udf包含'IDCEVO'，分配IDCevo项目 {idcevo_count} 条记录")
            
            # HU-MGU_02_L -> MGU项目 (忽略大小写)
            mgu_l_mask = tdf['target_ecu_conf_udf'].str.contains('HU-MGU_02_L', na=False, case=False) & (tdf.project=='')
            tdf.loc[mgu_l_mask, 'project'] = 'MGU'
            mgu_count = mgu_l_mask.sum()
            print(f"基于target_ecu_conf_udf包含'HU-MGU_02_L'，分配MGU项目 {mgu_count} 条记录")
            
            # HU-MGU_02_A -> IDC项目 (忽略大小写)
            idc_a_mask = tdf['target_ecu_conf_udf'].str.contains('HU-MGU_02_A', na=False, case=False) & (tdf.project=='')
            tdf.loc[idc_a_mask, 'project'] = 'IDC'
            idc_count = idc_a_mask.sum()
            print(f"基于target_ecu_conf_udf包含'HU-MGU_02_A'，分配IDC项目 {idc_count} 条记录")
        else:
            print("警告: DataFrame中缺少'target_ecu_conf_udf'列，跳过第二步分类")
        
        # --- 第三步：剩下的没有分配项目的再按照之前的正则（除RSU外）分配 ---
        print("第三步：用剩余正则处理未分配的记录...")
        unassigned_before = (tdf['project'] == '').sum()
        print(f"第三步前未分配的记录: {unassigned_before} 条")
        
        # App相关（排除已处理的RSU）
        tdf.loc[tdf[name_col].str.contains('IOS', na=False) & (tdf.project==''), 'project'] = 'App'
        tdf.loc[tdf[name_col].str.contains('Android', na=False) & (tdf.project==''), 'project'] = 'App'
        tdf.loc[tdf[name_col].str.contains('HarmonyOS', na=False) & (tdf.project==''), 'project'] = 'App'
        
        # IDC相关
        tdf.loc[tdf[name_col].str.contains('IDC23_MINI', na=False) & (tdf.project==''), 'project'] = 'IDC'
        tdf.loc[tdf[name_col].str.contains('IDC23_BMW', na=False) & (tdf.project==''), 'project'] = 'IDC'
        tdf.loc[tdf[name_col].str.contains('HU-MGU_02_A', na=False) & (tdf.project==''), 'project'] = 'IDC'
        tdf.loc[tdf[name_col].str.contains('IDC23', na=False) & (tdf.project==''), 'project'] = 'IDC'
        tdf.loc[tdf[name_col].str.contains('IDCEVO', na=False) & (tdf.project==''), 'project'] = 'IDCevo'
        
        # MGU相关
        tdf.loc[tdf[name_col].str.contains('MGU22', na=False) & (tdf.project==''), 'project'] = 'MGU22'
        tdf.loc[tdf[name_col].str.contains('HU-MGU_02_L', na=False) & (tdf.project==''), 'project'] = 'MGU22'
        tdf.loc[tdf[name_col].str.contains('HU-MGU_01', na=False) & (tdf.project==''), 'project'] = 'MGU22'
        tdf.loc[tdf[name_col].str.contains('MGU21', na=False) & (tdf.project==''), 'project'] = 'MGU21'
        tdf.loc[tdf[name_col].str.contains('MGU18', na=False) & (tdf.project==''), 'project'] = 'MGU18'
        
        # 对所有MGU子项目统一归类为MGU
        tdf.loc[tdf['project'].str.startswith('MGU', na=False) & (tdf.project != ''), 'project'] = 'MGU'
        
        unassigned_after = (tdf['project'] == '').sum()
        assigned_in_step3 = unassigned_before - unassigned_after
        print(f"第三步分配了 {assigned_in_step3} 条记录")
        
        # 将剩余未分类的标记为 Unknown
        tdf.loc[tdf['project'] == '', 'project'] = 'Unknown'
        unknown_count = (tdf['project'] == 'Unknown').sum()
        print(f"最终未分类（Unknown）: {unknown_count} 条记录")

        # --- 特殊覆盖规则：强制将包含 [Sys_RSU] 的记录分类为 RSU ---
        print("应用特殊覆盖规则：检查 top_aida 并强制分类 [Sys_RSU] 为 RSU 项目...")
        if 'top_aida' in tdf.columns:
            # 确保 top_aida 是字符串，处理 NaN
            tdf['top_aida'] = tdf['top_aida'].fillna('').astype(str)
            # 使用精确匹配 [Sys_RSU]
            sys_rsu_mask = tdf['top_aida'].str.contains('\\[Sys_RSU\\]', case=True, regex=True, na=False)
            original_count = sum(sys_rsu_mask)
            if original_count > 0:
                # 强制将 project 设置为 RSU
                tdf.loc[sys_rsu_mask, 'project'] = 'RSU'
                print(f"已将 {original_count} 条包含 [Sys_RSU] 的记录强制分类为 RSU 项目。")
            else:
                print("未找到 top_aida 包含 [Sys_RSU] 的记录。")
        else:
            print("警告: DataFrame 中缺少 'top_aida' 列，无法应用 [Sys_RSU] 覆盖规则。")
        # --- 覆盖规则结束 ---
        
        # 输出最终项目分布统计
        print("=== 最终项目分布统计 ===")
        project_counts = tdf['project'].value_counts()
        for project, count in project_counts.items():
            print(f"{project}: {count} 条记录")
        print(f"总记录数: {len(tdf)}")
        print("="*30)


    print("开始合并 AIDA/FV 映射...")
    print("为测试数据生成 aida_english 字段...")
    tdf['aida_english'] = tdf['top_aida'].apply(extract_english)
    print("aida_english 字段生成完成。")

    if 'fv' not in tdf.columns:
        tdf['fv'] = None
    tdf['fv'] = tdf['fv'].apply(lambda x: x.get('name') if isinstance(x, dict) else x)
    tdf = apply_aida_fv_mapping(tdf)
    fv_series = tdf['fv']
    fv_series = fv_series.where(pd.notna(fv_series), '')
    fv_series = fv_series.astype(str).str.strip()
    fv_series = fv_series.replace({'': 'Unknown', 'nan': 'Unknown', 'None': 'Unknown'})
    tdf['fv'] = fv_series
    tdf.loc[tdf['fv'] == 'Unknown', 'fv'] = '未分类数据'

    print("开始分配 Team 和 FVP...")
    tdf = apply_team_fvp_mapping(tdf)
    if 'fvp' in tdf.columns:
        tdf['fvp'] = tdf['fvp'].where(pd.notna(tdf['fvp']), '').astype(str).str.strip()
        tdf.loc[tdf['fvp'].isin(['', 'nan', 'None']), 'fvp'] = 'Unknown'

    # --- 处理 Lead Model 字段 ---
    print("开始处理 Lead Model 字段...")
    if 'lead_model_udf' in tdf.columns:
        # 安全地提取 lead_model_udf 的 name 字段
        def safe_extract_lead_model(x):
            if x is None:
                return ""
            if isinstance(x, dict):
                return x.get("name", "")
            return str(x)
        
        tdf["lead_model"] = tdf["lead_model_udf"].apply(safe_extract_lead_model)
        # 填充空值
        tdf['lead_model'] = tdf['lead_model'].fillna('').replace('', 'Unknown')
        print(f"Lead Model 处理完成。唯一值: {sorted(tdf['lead_model'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique())[:10]}...")  # 显示前10个唯一值
    else:
        print("警告: DataFrame 中缺少 'lead_model_udf' 列，无法提取 'lead_model'。")
        tdf['lead_model'] = 'Unknown'

    print("数据加载和处理完成。")
    print(f"最终 DataFrame 行数: {len(tdf)}, 列数: {len(tdf.columns)}")
    # 可以在这里打印 tdf.info() 或 tdf.head() 进行调试
    # print(tdf.info())
    # print(tdf.head())
    return tdf

# 如果你想在这里直接运行测试
# if __name__ == '__main__':
#     # 确保测试时你的工作目录结构正确 (包含 mr/ 和 aida/ 子目录及文件)
#     df = load_test_data()
#     if not df.empty:
#         print(df.head())
#         print(df.info())
#     else:
#         print("load_test_data 返回了一个空的 DataFrame。")

def get_latest_solution_cluster_from_history(defect_id, history_dir="history"):
    """
    从指定缺陷的历史文件中获取最新的solution cluster值
    
    参数:
    defect_id: 缺陷ID
    history_dir: history文件夹路径
    
    返回:
    最新的solution cluster name，如果没有找到则返回空字符串
    """
    try:
        history_data = get_history_data(defect_id, history_dir)
        if not history_data or 'data' not in history_data:
            return ""
        # 按时间戳排序，获取最新的solution_cluster_udf变更
        history_entries = sorted(history_data['data'], 
                               key=lambda x: x.get('timestamp', ''), 
                               reverse=True)
        
        for entry in history_entries:
            change_set = entry.get('change_set', [])
            if isinstance(change_set, list):
                for change in change_set:
                    if (isinstance(change, dict) and 
                        change.get('field_name') == 'solution_cluster_udf' and
                        change.get('value_text')):
                        return change.get('value_text', '')
        
        return ""
        
    except Exception as e:
        print(f"读取缺陷 {defect_id} 的历史文件时出错: {e}")
        return ""

def enrich_solution_cluster_from_history(df, history_dir="history"):
    """
    为缺失solution cluster的缺陷从history文件中补充最新值
    
    参数:
    df: 缺陷数据DataFrame
    history_dir: history文件夹路径
    
    返回:
    更新后的DataFrame
    """
    if 'domain' not in df.columns:
        print("警告: DataFrame中没有domain列")
        return df
    
    # 找到domain为空的缺陷
    empty_domain_mask = (df['domain'] == '') | (df['domain'].isna())
    empty_domain_defects = df[empty_domain_mask]
    
    if empty_domain_defects.empty:
        print("所有缺陷都已有solution cluster值")
        return df
    
    print(f"发现 {len(empty_domain_defects)} 个缺陷缺少solution cluster，正在从history补充...")
    
    updated_count = 0
    df_copy = df.copy()
    
    for idx, row in empty_domain_defects.iterrows():
        defect_id = row.get('id')
        if defect_id:
            latest_cluster = get_latest_solution_cluster_from_history(defect_id, history_dir)
            if latest_cluster:
                df_copy.at[idx, 'domain'] = latest_cluster
                updated_count += 1
    
    print(f"成功从history补充了 {updated_count} 个缺陷的solution cluster值")
    return df_copy


def calculate_processing_cycle_days(defect_id, status_phase, creation_time, history_dir="history"):
    """
    Calculate defect processing cycle (days)
    """
    try:
        import pandas as pd
        
        RESOLVED_PHASES = ['06-Concluded', '09-Concluded without action', '10-Closed']
        
        if pd.isna(creation_time):
            return 0
        
        creation_dt = pd.to_datetime(creation_time)
        if creation_dt.tz is not None:
            creation_dt = creation_dt.tz_convert('UTC').tz_localize(None)
        
        current_dt = pd.Timestamp.now()
        
        if status_phase in RESOLVED_PHASES:
            resolved_time = get_resolved_time_from_history(defect_id, history_dir)
            if resolved_time:
                resolved_dt = pd.to_datetime(resolved_time)
                if resolved_dt.tz is not None:
                    resolved_dt = resolved_dt.tz_convert('UTC').tz_localize(None)
                return (resolved_dt - creation_dt).days
            else:
                return (current_dt - creation_dt).days
        else:
            return (current_dt - creation_dt).days
            
    except Exception as e:
        print(f"计算处理周期时出错 (ID: {defect_id}): {e}")
        return 0


def get_resolved_time_from_history(defect_id, history_dir="history"):
    """
    从历史记录中获取缺陷解决时间（使用缓存优化）
    """
    try:
        history_data = get_history_data(defect_id, history_dir)
        if not history_data:
            return None
        
        if isinstance(history_data, dict) and 'data' in history_data:
            entries = history_data['data']
        elif isinstance(history_data, list):
            entries = history_data
        else:
            return None
            
        entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        RESOLVED_PHASES = ['06-Concluded', '09-Concluded without action', '10-Closed']
        
        for entry in entries:
            if entry.get('action') == 'update' and 'change_set' in entry:
                for change in entry['change_set']:
                    if change.get('field_name') == 'phase':
                        if change.get('value_text') in RESOLVED_PHASES:
                            return entry.get('timestamp')
                            
        return None
        
    except Exception as e:
        print(f"读取历史记录时出错 (ID: {defect_id}): {e}")
        return None

# ===== 流转路径分析函数 (从helper_functions.py迁移) =====

def extract_transition_path_from_history(defect_id: str, field_name: str, history_dir: str = "history") -> str:
    """
    从历史文件中提取指定字段的变化路径（使用缓存优化）
    
    Args:
        defect_id: 缺陷ID
        field_name: 字段名 (如 'assigned_ecu_udf' 或 'solution_cluster_udf')
        history_dir: 历史文件目录
    
    Returns:
        str: 变化路径，格式如 "转移次数, value1 -> value2 -> value3"
    """
    try:
        history_data = get_history_data(defect_id, history_dir)
        if not history_data:
            return ""
        
        if isinstance(history_data, dict) and 'data' in history_data:
            entries = history_data['data']
        elif isinstance(history_data, list):
            entries = history_data
        else:
            return ""
        
        # 按时间戳排序（升序，从老到新）
        entries.sort(key=lambda x: x.get('timestamp', ''))
        
        changes = []
        for entry in entries:
            if entry.get('action') == 'update' and 'change_set' in entry:
                for change in entry['change_set']:
                    if change.get('field_name') == field_name:
                        timestamp = entry.get('timestamp', '')
                        value_text = change.get('value_text', '')
                        old_value_text = change.get('old_value_text', '')
                        
                        # 记录变化
                        changes.append({
                            'timestamp': timestamp,
                            'value': value_text,
                            'old_value': old_value_text
                        })
        
        if not changes:
            return ""
        
        # 计算实际转移次数：考虑None作为中间状态
        # 构建有效值序列（过滤掉None，但保留转移关系）
        effective_values = []
        
        # 添加初始值（如果不为空）
        if changes[0].get('old_value') and changes[0]['old_value'].strip():
            effective_values.append(changes[0]['old_value'].strip())
        
        # 添加所有有效的新值（跳过None）
        for change in changes:
            value = change.get('value')
            if value is not None and str(value).strip().lower() not in ['none', '']:
                effective_values.append(str(value).strip())
        
        # 转移次数 = 有效值序列长度 - 1
        actual_transfer_count = len(effective_values) - 1 if len(effective_values) > 1 else 0
        
        # 使用已计算的有效值序列构建路径
        path_values = effective_values.copy()
        
        # 返回格式："转移次数, 完整路径"
        if len(path_values) > 1:
            path_str = " -> ".join(path_values)
            return f"{actual_transfer_count}, {path_str}"
        elif len(path_values) == 1 and actual_transfer_count > 0:
            # 只有一个值但有转移（比如从空到某个值）
            return f"{actual_transfer_count}, {path_values[0]}"
        else:
            return ""
        
    except Exception as e:
        print(f"提取变化路径时出错 (ID: {defect_id}, field: {field_name}): {e}")
        return ""

def simplify_ecu_name(ecu_name: str) -> str:
    """
    简化ECU名称显示
    """
    if not ecu_name:
        return ""
    
    # 移除常见前缀和后缀，保留核心名称
    simplified = ecu_name.strip()
    
    # 如果包含'-'，取第一部分
    if '-' in simplified:
        simplified = simplified.split('-')[0]
    
    # 移除常见的数字后缀
    if simplified.endswith(('_25', '_23', '_22')):
        simplified = simplified[:-3]
    
    return simplified

def get_ecu_transition_path(defect_id: str, history_dir: str = "history") -> str:
    """
    获取ECU流转路径
    """
    return extract_transition_path_from_history(defect_id, 'assigned_ecu_udf', history_dir)

def get_solution_cluster_transition_path(defect_id: str, history_dir: str = "history") -> str:
    """
    获取Solution Cluster流转路径
    """
    return extract_transition_path_from_history(defect_id, 'solution_cluster_udf', history_dir)

def enrich_data_with_transition_paths(df: pd.DataFrame) -> pd.DataFrame:
    """
    为数据框添加流转路径列（使用预加载优化）
    """
    df_enriched = df.copy()
    
    # 预加载所有需要的历史数据
    defect_ids = df_enriched['id'].astype(str).tolist()
    history_cache.preload_histories(defect_ids)
    
    # 添加ECU流转路径
    print("正在计算ECU流转路径...")
    df_enriched['ecu_transition_path'] = df_enriched['id'].astype(str).apply(
        lambda x: get_ecu_transition_path(x)
    )
    
    # 添加Solution Cluster流转路径
    print("正在计算Solution Cluster流转路径...")
    df_enriched['solution_cluster_transition_path'] = df_enriched['id'].astype(str).apply(
        lambda x: get_solution_cluster_transition_path(x)
    )
    
    return df_enriched

def enhance_pu_filling(ddf):
    """
    增强PU填充逻辑
    按优先级使用多种策略填充PU空值
    """
    print("🔧 开始增强PU填充...")
    
    # 记录填充来源
    if 'pu_fill_source' not in ddf.columns:
        ddf['pu_fill_source'] = ''
    
    initial_empty = ((ddf['pu'] == '') | (ddf['pu'].isna())).sum()
    filled_count = 0
    
    # 策略1: 使用Shift_PU填充
    shift_pu_mask = (
        ((ddf['pu'] == '') | (ddf['pu'].isna())) &
        (ddf['Shift_PU'].notna()) &
        (ddf['Shift_PU'] != '')
    )
    shift_pu_count = shift_pu_mask.sum()
    
    if shift_pu_count > 0:
        ddf.loc[shift_pu_mask, 'pu'] = ddf.loc[shift_pu_mask, 'Shift_PU']
        ddf.loc[shift_pu_mask, 'pu_fill_source'] = 'Shift_PU'
        filled_count += shift_pu_count
    
    # 策略2: 基于VIN的PU映射填充
    vin_pu_mapping = {}
    vin_fill_count = 0
    if 'vin_udf' in ddf.columns:
        vin_data = ddf[(ddf['vin_udf'].notna()) & (ddf['pu'] != '') & (~ddf['pu'].isna())]

        for _, row in vin_data.iterrows():
            if pd.notna(row['vin_udf']):
                vins = str(row['vin_udf']).split(',')
                for vin in vins:
                    vin = vin.strip().upper()
                    if vin and vin not in vin_pu_mapping:
                        vin_pu_mapping[vin] = row['pu']

        empty_mask = ((ddf['pu'] == '') | (ddf['pu'].isna()))
        for idx, row in ddf[empty_mask].iterrows():
            if pd.notna(row['vin_udf']):
                vins = str(row['vin_udf']).split(',')
                for vin in vins:
                    vin = vin.strip().upper()
                    if vin in vin_pu_mapping:
                        ddf.loc[idx, 'pu'] = vin_pu_mapping[vin]
                        ddf.loc[idx, 'pu_fill_source'] = 'VIN_mapping'
                        vin_fill_count += 1
                        break
    
    filled_count += vin_fill_count
    
    # 策略3: 基于项目+时间的智能填充
    project_week_pu = {}
    filled_data = ddf[(ddf['pu'] != '') & (~ddf['pu'].isna())]
    
    for project in ddf['project'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique():
        project_week_pu[project] = {}
        project_data = filled_data[filled_data['project'] == project]
        
        for week in project_data['test_week'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique():
            week_data = project_data[project_data['test_week'] == week]
            if len(week_data) > 0:
                most_common_pu = week_data['pu'].mode()
                if len(most_common_pu) > 0:
                    project_week_pu[project][week] = most_common_pu.iloc[0]
    
    # 应用项目+时间填充
    project_time_fill_count = 0
    empty_mask = ((ddf['pu'] == '') | (ddf['pu'].isna()))
    
    for idx, row in ddf[empty_mask].iterrows():
        project = row['project']
        week = row['test_week']
        
        if project in project_week_pu and week in project_week_pu[project]:
            ddf.loc[idx, 'pu'] = project_week_pu[project][week]
            ddf.loc[idx, 'pu_fill_source'] = f'project_time'
            project_time_fill_count += 1
    
    filled_count += project_time_fill_count
    
    # 策略4: 基于项目默认值填充
    project_defaults = {}
    for project in ddf['project'].apply(lambda x: str(x) if isinstance(x, dict) else x).dropna().unique():
        project_data = ddf[(ddf['project'] == project) & (ddf['pu'] != '') & (~ddf['pu'].isna())]
        if len(project_data) > 0:
            most_common_pu = project_data['pu'].mode()
            if len(most_common_pu) > 0:
                project_defaults[project] = most_common_pu.iloc[0]
    
    # 应用项目默认值
    project_default_fill_count = 0
    empty_mask = ((ddf['pu'] == '') | (ddf['pu'].isna()))
    
    for idx, row in ddf[empty_mask].iterrows():
        project = row['project']
        if project in project_defaults:
            ddf.loc[idx, 'pu'] = project_defaults[project]
            ddf.loc[idx, 'pu_fill_source'] = f'project_default'
            project_default_fill_count += 1
    
    filled_count += project_default_fill_count
    
    # 策略5: 全局默认值填充
    global_default_pu = ddf[(ddf['pu'] != '') & (~ddf['pu'].isna())]['pu'].mode()
    if len(global_default_pu) > 0:
        global_default = global_default_pu.iloc[0]
        
        global_fill_count = 0
        empty_mask = ((ddf['pu'] == '') | (ddf['pu'].isna()))
        
        for idx, row in ddf[empty_mask].iterrows():
            ddf.loc[idx, 'pu'] = global_default
            ddf.loc[idx, 'pu_fill_source'] = f'global_default'
            global_fill_count += 1
        
        filled_count += global_fill_count
    
    final_empty = ((ddf['pu'] == '') | (ddf['pu'].isna())).sum()
    print(f"PU填充完成: 填充了 {filled_count} 条记录，剩余空值 {final_empty} 条")
    
    return ddf

# ===== Inflow/Outflow 分析函数 =====
# 添加缓存支持
try:
    from scripts.performance.cache.cache_manager import cache, cached, default_cache_manager
    CACHE_AVAILABLE = True
except ImportError:
    print("缓存模块不可用，将不使用缓存")
    CACHE_AVAILABLE = False
    default_cache_manager = None
    def cached(key_prefix, timeout=3600):
        def decorator(func):
            return func
        return decorator

def calculate_inflow_outflow_trends(history_dir="history", date_range_weeks=52, force_refresh=False):
    """
    计算ticket的inflow和outflow趋势（完整模式，支持缓存）
    
    Inflow: 每周从phase 00到01的ticket数量
    Outflow: 每周从任意阶段到phase 06、09或10的ticket数量
    
    Args:
        history_dir (str): 历史文件目录路径
        date_range_weeks (int): 分析的周数范围
        force_refresh (bool): 是否强制刷新缓存
    
    Returns:
        pandas.DataFrame: 包含 'week', 'inflow', 'outflow' 的DataFrame
    """
    # 构建缓存键
    if CACHE_AVAILABLE:
        import hashlib
        cache_key = f"inflow_outflow_trends_{history_dir}_{date_range_weeks}"
        cache_key_hash = hashlib.md5(cache_key.encode()).hexdigest()
        
        # 如果不强制刷新，先尝试从缓存获取
        if not force_refresh and default_cache_manager:
            cached_result = default_cache_manager.get(cache_key_hash)
            if cached_result is not None:
                print("📋 使用缓存的Inflow/Outflow趋势数据 (8小时内有效)")
                print(f"   缓存结果: {len(cached_result)} 周数据")
                if not cached_result.empty:
                    total_inflow = cached_result['inflow'].sum()
                    total_outflow = cached_result['outflow'].sum()
                    print(f"   总Inflow: {total_inflow}, 总Outflow: {total_outflow}")
                return cached_result
        else:
            print("🔄 强制刷新缓存，重新计算Inflow/Outflow趋势...")
    
    # 执行实际计算
    result = _calculate_inflow_outflow_trends_impl(history_dir, date_range_weeks)
    
    # 保存到缓存 (8小时有效)
    if CACHE_AVAILABLE and default_cache_manager:
        default_cache_manager.set(cache_key_hash, result, timeout=28800)  # 8小时 = 28800秒
        print("💾 Inflow/Outflow趋势数据已缓存 (8小时有效)")
    
    return result

def _calculate_inflow_outflow_trends_impl(history_dir="history", date_range_weeks=52):
    """
    Inflow/Outflow趋势分析的实际实现
    """
    import pandas as pd
    from datetime import datetime, timedelta
    import time
    
    start_time = time.time()
    
    histories = list(_iter_histories_from_db())
    if not histories:
        return pd.DataFrame(columns=['week', 'inflow', 'outflow'])
    
    print(f"正在分析 {len(histories)} 个历史记录...")
    
    # 时间范围设定（使用UTC时间以匹配历史数据）
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(weeks=date_range_weeks)
    print(f"时间范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')} (UTC)")
    
    # 定义关键阶段
    outflow_phases = ['06', '09']  # 移除'10'，因为tolerate现在已经改成09状态
    
    # 计数器
    weekly_inflow = {}
    weekly_outflow = {}
    
    processed = 0
    for _, data in histories:
        try:
            if not data or 'data' not in data:
                continue

            for entry in data['data']:
                timestamp_str = entry.get('timestamp')
                if not timestamp_str:
                    continue
                
                try:
                    timestamp = pd.to_datetime(timestamp_str).tz_localize(None)  # 转换为naive datetime以便比较
                    if not (start_date <= timestamp <= end_date):
                        continue
                    
                    week_key = timestamp.strftime('%Y-W%V')
                    
                    # 初始化计数器
                    if week_key not in weekly_inflow:
                        weekly_inflow[week_key] = 0
                        weekly_outflow[week_key] = 0
                    
                    # 检查阶段变化
                    changes = entry.get('change_set', [])
                    for change in changes:
                        if (isinstance(change, dict) and 
                            change.get('field_name') == 'phase'):
                            
                            old_val = change.get('old_value_text', '')
                            new_val = change.get('value_text', '') or change.get('valueName', '')
                            
                            # Inflow: 00 -> 01 或者直接到01-new（从另一个系统创建的票）
                            if (old_val.startswith('00') and new_val.startswith('01')) or \
                               (not old_val and new_val.startswith('01')):
                                weekly_inflow[week_key] += 1
                            
                            # Outflow: any -> 06/09/10
                            if any(new_val.startswith(phase) for phase in outflow_phases):
                                weekly_outflow[week_key] += 1
                
                except:
                    continue
                    
        except Exception:
            continue
        
        processed += 1
        if processed % 100 == 0:
            elapsed = time.time() - start_time
            print(f"📈 进度: {processed}/{len(histories)} ({elapsed:.1f}s)")
    
    # 只保留有实际数据的周期，不生成未来的空数据
    # 找到最早和最晚有数据的周期
    data_weeks = set()
    for week_key in weekly_inflow.keys():
        if weekly_inflow[week_key] > 0 or weekly_outflow[week_key] > 0:
            data_weeks.add(week_key)
    
    if not data_weeks:
        # 如果没有任何数据，返回空DataFrame
        return pd.DataFrame(columns=['week', 'inflow', 'outflow'])
    
    # 按时间顺序排序周期，而不是按字符串排序
    def parse_week_key(week_key):
        """将周期键转换为可排序的元组 (year, week)"""
        try:
            year, week = week_key.split('-W')
            return (int(year), int(week))
        except:
            return (0, 0)
    
    # 找到数据的时间范围
    sorted_data_weeks = sorted(data_weeks, key=parse_week_key)
    earliest_week = sorted_data_weeks[0]
    latest_week = sorted_data_weeks[-1]
    
    # 生成从最早到最晚数据周期的完整周列表（填补中间的空白周）
    earliest_date = datetime.strptime(earliest_week + '-1', '%Y-W%W-%w')
    latest_date = datetime.strptime(latest_week + '-1', '%Y-W%W-%w')
    
    current = earliest_date
    while current <= latest_date:
        week_key = current.strftime('%Y-W%V')
        if week_key not in weekly_inflow:
            weekly_inflow[week_key] = 0
            weekly_outflow[week_key] = 0
        current += timedelta(weeks=1)
    
    # 构建结果DataFrame，只包含有数据范围内的周期
    weekly_data = []
    current = earliest_date
    while current <= latest_date:
        week_key = current.strftime('%Y-W%V')
        weekly_data.append({
            'week': week_key,
            'inflow': weekly_inflow[week_key],
            'outflow': weekly_outflow[week_key]
        })
        current += timedelta(weeks=1)
    
    df_result = pd.DataFrame(weekly_data)
    
    # 输出统计
    total_time = time.time() - start_time
    total_inflow = df_result['inflow'].sum() if not df_result.empty else 0
    total_outflow = df_result['outflow'].sum() if not df_result.empty else 0
    
    print(f"Inflow/Outflow 趋势分析完成，共 {len(df_result)} 周数据")
    print(f"总Inflow: {total_inflow}, 总Outflow: {total_outflow}")
    print(f"⏱️  完整模式耗时: {total_time:.2f} 秒")
    
    return df_result

def clear_inflow_outflow_cache():
    """清除Inflow/Outflow相关的缓存"""
    if CACHE_AVAILABLE and default_cache_manager:
        # 清除所有inflow_outflow相关的缓存
        # 由于缓存键包含inflow_outflow前缀，我们需要清除所有缓存
        default_cache_manager.clear()
        print("🗑️  已清除Inflow/Outflow缓存")
    else:
        print("缓存系统不可用")

def get_inflow_outflow_summary_stats(df_trends):
    """
    获取inflow/outflow的汇总统计信息
    
    Args:
        df_trends: calculate_inflow_outflow_trends返回的DataFrame
    
    Returns:
        dict: 包含统计信息的字典
    """
    if df_trends.empty:
        return {
            'total_inflow': 0,
            'total_outflow': 0,
            'avg_weekly_inflow': 0,
            'avg_weekly_outflow': 0,
            'net_accumulation': 0,
            'convergence_rate': 0
        }
    
    total_inflow = df_trends['inflow'].sum()
    total_outflow = df_trends['outflow'].sum()
    avg_weekly_inflow = df_trends['inflow'].mean()
    avg_weekly_outflow = df_trends['outflow'].mean()
    net_accumulation = total_inflow - total_outflow
    
    # 计算收敛率 (outflow/inflow)
    convergence_rate = (total_outflow / total_inflow * 100) if total_inflow > 0 else 0
    
    return {
        'total_inflow': int(total_inflow),
        'total_outflow': int(total_outflow),
        'avg_weekly_inflow': round(avg_weekly_inflow, 1),
        'avg_weekly_outflow': round(avg_weekly_outflow, 1),
        'net_accumulation': int(net_accumulation),
        'convergence_rate': round(convergence_rate, 1)
    }
