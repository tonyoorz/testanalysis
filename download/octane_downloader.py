#!/usr/bin/env python3
"""
Octane 全量数据下载器 - 生产级版本
基于 downloader7 架构重构，支持：
1. 全量数据下载（当年+前一年）
2. 多线程并行下载
3. Parent-Child 关联缺陷下载
4. 直接入库模式（API → SQLite，跳过本地文件）
5. 完善的错误处理和重试机制
6. History 缓存机制
"""

import json
import time
import urllib.parse
import requests
import logging
import pandas as pd
from datetime import datetime, timedelta
import os
import argparse
import urllib3
import concurrent.futures
from tqdm import tqdm
import re
import sqlite3
from threading import Lock
from functools import lru_cache
from typing import Dict, Optional, List, Set, Tuple

# 尝试导入 sso_session，如果失败则告知用户
try:
    from sso_session import bmw_sso_session
    SSO_AVAILABLE = True
except ImportError:
    SSO_AVAILABLE = False
    def bmw_sso_session(*args, **kwargs):
        logging.error("sso_session 模块未找到，无法使用 SSO 认证。")
        return None

# --- 日志配置 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'octane_download_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8')
    ]
)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 常量定义 ---
BASE_URL = "https://octane-prod.bmwgroup.net"
API_SHARED_SPACES_URL = f"{BASE_URL}/api/shared_spaces/1002"
API_BASE_URL = f"{API_SHARED_SPACES_URL}/workspaces/2001"

# 性能配置
DEFAULT_LIMIT_PER_PAGE = 5000  # 超级优化：5倍分页大小
TURBO_LIMIT_PER_PAGE = 10000   # 极限模式

# API 端点
EP_DEFECT = "defects"
EP_MANUALRUN = "manual_runs"
EP_USER = "workspace_users"
EP_HISTORY = "history_logs"

# 完整的字段列表（与 downloader7 保持一致）
DEFAULT_F_DEFECT_MAIN = (
    "id", "name", "creation_time", "last_modified",
    "parent_child_udf",
    "team",
    "vin_udf", "user_tags", "tqr_udf", "product_areas", "aida_businesskey_udf",
    "software_version_udf", "ecu_no_of_changes_udf", "first_use_sop_of_function_udf",
    "tolerated_count_udf", "blocking_reason_udf", "reprel_changes_udf",
    "requirements",
    "parent",
    "parent_phase_udf", "sab_comment_udf",
    "relation_to_udf",  # 关键字段：用于 Parent-Child 关联
    "assigned_ecu_udf", "error_occurrence_udf",
    "problem_finder_team_udf", "program", "solution_responsible_udf",
    "solution_cluster_udf", "reporting_class_udf", "detected_in_release",
    "detected_by", "function_responsible1_udf", "owner", "phase", "severity",
    "involved_i_step1_udf", "author", "lead_model_udf", "problem_severity_udf",
    "ecu_to_modul_udf", "description"  # 添加 description 字段
)

DEFAULT_F_MANUALRUN = (
    "defect", "is_completed", "steps_num", "name", "version_stamp", "id",
    "last_modified", "started", "creation_time", "test_name", "test",
    "finished_udf", "testplatformid_udf", "exec_model_series_udf",
    "execution_sw_version_udf", "author", "release", "run_by",
    "product_areas", "program", "set_udf", "testing_tool_type", "taxonomies",
    "test_version", "test_phase", "run_team_000_udf", "domain_udf", "status",
    "native_status", "target_ecu_conf_udf"
)

F_DEFECT_FOR_HISTORY_IDS = (
    "id", "name", "last_modified", "creation_time", "team",
    "problem_finder_team_udf", "severity", "phase", "owner", "detected_in_release"
)

DEFAULT_TEAM = "DTSV_China"

# --- 数据库配置 ---
DB_FILE = '/Users/tonyorz/pre-analysis/database/local_data.db'

# --- 线程安全锁 ---
db_lock = Lock()

# --- 核心下载函数 ---

def fetch_octane_data(session, endpoint, fields, query, limit_per_page=DEFAULT_LIMIT_PER_PAGE,
                     order_by=None, api_url=API_BASE_URL):
    """
    串行获取 Octane 数据（备用方案）
    """
    all_data = []
    offset = 0
    total_fetched = 0
    logging.info(f"[串行模式] 开始从端点 '{endpoint}' 获取数据")

    while True:
        request_params = {
            "fields": ",".join(fields) if isinstance(fields, (list, tuple)) else fields,
            "query": query,
            "limit": limit_per_page,
            "offset": offset
        }
        if order_by:
            request_params["order_by"] = order_by

        try:
            resp = session.get(f"{api_url}/{endpoint}", params=request_params,
                             verify=False, allow_redirects=True, timeout=60)

            if resp.status_code in [401, 403, 404]:
                logging.error(f"HTTP {resp.status_code}: {resp.url}")
                break
            elif resp.status_code >= 400:
                logging.error(f"请求失败: {resp.status_code}. Response: {resp.text[:500]}")
                break

            resp.raise_for_status()
            data = resp.json()
            batch_data = data.get("data", [])
            batch_size = len(batch_data)
            total_count_api = data.get("total_count", 0)

            if not batch_data:
                break

            all_data.extend(batch_data)
            total_fetched += batch_size

            if total_fetched >= total_count_api or batch_size < limit_per_page:
                break

            offset += limit_per_page
            time.sleep(0.01)  # 超级优化：极小延迟

        except Exception as e:
            logging.error(f"请求错误: {e}")
            break

    logging.info(f"[串行模式] 从 '{endpoint}' 获取完成，共 {len(all_data)} 条")
    return all_data


def fetch_single_page(session, endpoint, fields, query, limit_per_page, offset,
                     order_by=None, api_url=API_BASE_URL):
    """获取单个分页的数据（用于多线程）"""
    request_params = {
        "fields": ",".join(fields) if isinstance(fields, (list, tuple)) else fields,
        "query": query,
        "limit": limit_per_page,
        "offset": offset
    }
    if order_by:
        request_params["order_by"] = order_by

    try:
        resp = session.get(f"{api_url}/{endpoint}", params=request_params,
                          verify=False, allow_redirects=True, timeout=60)

        if resp.status_code >= 400:
            return {"error": f"HTTP {resp.status_code}", "data": []}

        resp.raise_for_status()
        data = resp.json()
        return {
            "data": data.get("data", []),
            "total_count": data.get("total_count", 0),
            "offset": offset,
            "page_size": len(data.get("data", [])),
            "error": None
        }
    except Exception as e:
        return {"error": str(e), "data": []}


def fetch_octane_data_parallel(session, endpoint, fields, query,
                               limit_per_page=DEFAULT_LIMIT_PER_PAGE,
                               order_by=None, api_url=API_BASE_URL, max_workers=10):
    """
    多线程并发获取 Octane 数据（与 downloader7 一致）
    """
    logging.info(f"[并行模式] 开始下载 '{endpoint}'，并发数: {max_workers}")

    # 首先获取第一页
    first_page = fetch_single_page(session, endpoint, fields, query, limit_per_page, 0, order_by, api_url)

    if first_page["error"]:
        logging.error(f"获取第一页失败: {first_page['error']}")
        return []

    if not first_page["data"]:
        logging.info(f"端点 '{endpoint}' 没有数据")
        return []

    total_count = first_page["total_count"]
    all_data = first_page["data"].copy()

    if len(first_page["data"]) < limit_per_page or total_count <= limit_per_page:
        return all_data

    # 计算剩余页数
    total_pages = (total_count + limit_per_page - 1) // limit_per_page
    remaining_pages = total_pages - 1

    page_offsets = [limit_per_page * (i + 1) for i in range(remaining_pages)]

    successful_pages = 0
    failed_pages = 0

    with tqdm(total=remaining_pages, desc=f"并发下载 {endpoint}") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_offset = {
                executor.submit(fetch_single_page, session, endpoint, fields, query,
                               limit_per_page, offset, order_by, api_url): offset
                for offset in page_offsets
            }

            for future in concurrent.futures.as_completed(future_to_offset):
                offset = future_to_offset[future]
                try:
                    result = future.result()
                    if result["error"]:
                        failed_pages += 1
                    else:
                        all_data.extend(result["data"])
                        successful_pages += 1
                except Exception as e:
                    logging.error(f"处理页面 offset={offset} 异常: {e}")
                    failed_pages += 1
                pbar.update(1)

    success_rate = (successful_pages / remaining_pages * 100) if remaining_pages > 0 else 100
    logging.info(f"[并行模式] 完成！成功率: {success_rate:.1f}%，总数据: {len(all_data)}")

    return all_data


# --- 认证函数 ---

def get_authenticated_session(auth_method_choice, sso_login_file=None, cookie_file_path=None):
    """获取认证会话"""
    session_obj = requests.Session()
    session_obj.verify = False

    if auth_method_choice == 'sso':
        if not SSO_AVAILABLE:
            logging.error("SSO 模块不可用")
            return None
        try:
            if not sso_login_file or not os.path.exists(sso_login_file):
                logging.error(f"SSO 文件不存在: {sso_login_file}")
                return None

            with open(sso_login_file, "r", encoding="utf-8") as f:
                user_name, password = f.readline().strip(), f.readline().strip()

            if not user_name or not password:
                logging.error("登录文件格式不正确")
                return None

            logging.info(f"SSO 认证用户: {user_name}")
            auth_session = bmw_sso_session(BASE_URL, user_name, password, session=session_obj)
            if not auth_session:
                logging.error("SSO 认证失败")
                return None
            session_obj = auth_session
            logging.info("SSO 认证成功")
        except Exception as e:
            logging.error(f"SSO 认证错误: {e}")
            return None

    elif auth_method_choice == 'cookie':
        actual_cookie_file = cookie_file_path or "cookie.txt"
        try:
            if not os.path.exists(actual_cookie_file):
                logging.error(f"Cookie 文件不存在: {actual_cookie_file}")
                return None

            with open(actual_cookie_file, "r", encoding="utf-8") as f:
                cookie_val = f.read().strip()

            if not cookie_val:
                logging.error("Cookie 文件为空")
                return None

            session_obj.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "cookie": cookie_val
            })
            logging.info(f"使用 Cookie 认证: {actual_cookie_file}")
        except Exception as e:
            logging.error(f"Cookie 认证错误: {e}")
            return None
    else:
        logging.error(f"无效认证方法: {auth_method_choice}")
        return None

    # 测试认证
    test_url = f"{API_BASE_URL}/{EP_USER}"
    try:
        test_resp = session_obj.get(test_url, params={"limit": 1, "fields": "id"}, timeout=15)
        if test_resp.status_code != 200:
            logging.error(f"认证测试失败: {test_resp.status_code}")
            return None
        logging.info("认证测试成功")
    except Exception as e:
        logging.error(f"认证测试错误: {e}")
        return None

    return session_obj


# --- 数据库操作 ---

class DatabaseManager:
    """数据库管理器 - 支持直接入库"""

    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._local = threading.local()
        self._ensure_connection()
        self._create_tables()

    def _ensure_connection(self):
        """确保线程有独立的数据库连接"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.cursor = self._local.conn.cursor()

    def _create_tables(self):
        """创建数据表"""
        self._ensure_connection()
        cursor = self._local.cursor

        # Test Runs 表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_runs (
            run_id TEXT NOT NULL,
            report_period TEXT NOT NULL,
            test_id TEXT,
            test_name TEXT,
            run_status TEXT,
            tester TEXT,
            finished_time TEXT,
            test_week TEXT,
            project TEXT,
            model TEXT,
            aidas TEXT,
            top_aida TEXT,
            source_file TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (report_period, run_id)
        )
        ''')

        # Defects 表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS defects (
            defect_id TEXT NOT NULL PRIMARY KEY,
            year INTEGER NOT NULL,
            creation_time TEXT,
            summary TEXT,
            description TEXT,
            status_phase TEXT,
            severity TEXT,
            project TEXT,
            detected_by TEXT,
            detected_in_release TEXT,
            domain TEXT,
            aidas TEXT,
            top_aida TEXT,
            tags TEXT,
            classification TEXT,
            pingpong INTEGER,
            vin TEXT,
            parent_child_type TEXT,
            relation_to TEXT,
            referenced_by_child_id TEXT,
            source_file TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # History Log 表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS history_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            object_id TEXT,
            log_timestamp TEXT,
            user TEXT,
            action_type TEXT,
            change_details TEXT,
            source_file TEXT,
            source_format TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_defect_year ON defects (year)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_defect_phase ON defects (status_phase)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_object_id ON history_log (object_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_timestamp ON history_log (log_timestamp)')

        self._local.conn.commit()
        logging.info("数据库表结构已确保")

    def insert_defects(self, defects_data: List[Dict], year: int, source_file: str = ""):
        """批量插入 defects"""
        if not defects_data:
            return

        self._ensure_connection()
        records = []

        for record in defects_data:
            if not isinstance(record, dict):
                continue

            defect_id = record.get('id')
            if defect_id is None:
                continue

            # 提取 aidas
            aidas_list = []
            product_areas = record.get('product_areas', {})
            if isinstance(product_areas, dict) and 'data' in product_areas:
                aidas_list = [item.get('name') for item in product_areas['data']
                             if isinstance(item, dict) and item.get('name')]

            # 提取 tags
            tags_list = []
            user_tags = record.get('user_tags', {})
            if isinstance(user_tags, dict) and 'data' in user_tags:
                tags_list = [item.get('name') for item in user_tags['data']
                            if isinstance(item, dict) and item.get('name')]

            # 提取 classification
            class_list = []
            reporting_class = record.get('reporting_class_udf', {})
            if isinstance(reporting_class, dict) and 'data' in reporting_class:
                class_list = [item.get('name') for item in reporting_class['data']
                             if isinstance(item, dict) and item.get('name')]

            records.append({
                'defect_id': str(defect_id),
                'year': year,
                'creation_time': record.get('creation_time'),
                'summary': record.get('name'),
                'description': record.get('description'),
                'status_phase': record.get('phase', {}).get('name') if isinstance(record.get('phase'), dict) else None,
                'severity': record.get('problem_severity_udf', {}).get('name') if isinstance(record.get('problem_severity_udf'), dict) else None,
                'project': record.get('assigned_ecu_udf', {}).get('name') if isinstance(record.get('assigned_ecu_udf'), dict) else None,
                'detected_by': record.get('detected_by', {}).get('full_name') if isinstance(record.get('detected_by'), dict) else None,
                'detected_in_release': record.get('detected_in_release', {}).get('name') if isinstance(record.get('detected_in_release'), dict) else None,
                'domain': record.get('solution_cluster_udf', {}).get('name') if isinstance(record.get('solution_cluster_udf'), dict) else None,
                'aidas': json.dumps(aidas_list) if aidas_list else None,
                'top_aida': aidas_list[0] if aidas_list else None,
                'tags': json.dumps(tags_list) if tags_list else None,
                'classification': json.dumps(class_list) if class_list else None,
                'pingpong': record.get('ecu_no_of_changes_udf'),
                'vin': record.get('vin_udf'),
                'parent_child_type': record.get('parent_child_udf', {}).get('name') if isinstance(record.get('parent_child_udf'), dict) else None,
                'relation_to': record.get('relation_to_udf'),
                'referenced_by_child_id': record.get('referenced_by_child_id'),
                'source_file': source_file
            })

        if records:
            try:
                with db_lock:
                    self._local.cursor.executemany('''
                        INSERT OR REPLACE INTO defects
                        (defect_id, year, creation_time, summary, description, status_phase, severity,
                         project, detected_by, detected_in_release, domain, aidas, top_aida, tags,
                         classification, pingpong, vin, parent_child_type, relation_to,
                         referenced_by_child_id, source_file)
                        VALUES (:defect_id, :year, :creation_time, :summary, :description, :status_phase,
                                :severity, :project, :detected_by, :detected_in_release, :domain, :aidas,
                                :top_aida, :tags, :classification, :pingpong, :vin, :parent_child_type,
                                :relation_to, :referenced_by_child_id, :source_file)
                    ''', records)
                    self._local.conn.commit()
                    logging.info(f"[DB] 插入/更新 {len(records)} 条 defects")
            except sqlite3.Error as e:
                logging.error(f"[DB] 插入 defects 错误: {e}")

    def insert_test_runs(self, runs_data: List[Dict], report_period: str, source_file: str = ""):
        """批量插入 test runs"""
        if not runs_data:
            return

        self._ensure_connection()
        records = []

        for record in runs_data:
            if not isinstance(record, dict):
                continue

            run_id = record.get('id')
            if run_id is None:
                continue

            # 提取 aidas
            aidas_list = []
            product_areas = record.get('product_areas', {})
            if isinstance(product_areas, dict) and 'data' in product_areas:
                aidas_list = [item.get('name') for item in product_areas['data']
                             if isinstance(item, dict) and item.get('name')]

            # 计算 test_week
            finished_time = record.get('finished_udf')
            test_week = self._calculate_test_week(finished_time)

            records.append({
                'run_id': str(run_id),
                'report_period': report_period,
                'test_id': record.get('test', {}).get('id') if isinstance(record.get('test'), dict) else None,
                'test_name': record.get('test', {}).get('name') if isinstance(record.get('test'), dict) else None,
                'run_status': record.get('status', {}).get('name') if isinstance(record.get('status'), dict) else None,
                'tester': record.get('run_by', {}).get('full_name') if isinstance(record.get('run_by'), dict) else None,
                'finished_time': finished_time,
                'test_week': test_week,
                'project': record.get('release', {}).get('name') if isinstance(record.get('release'), dict) else 'Unknown',
                'model': record.get('exec_model_series_udf', {}).get('name') if isinstance(record.get('exec_model_series_udf'), dict) else None,
                'aidas': json.dumps(aidas_list) if aidas_list else None,
                'top_aida': aidas_list[0] if aidas_list else None,
                'source_file': source_file
            })

        if records:
            try:
                with db_lock:
                    self._local.cursor.executemany('''
                        INSERT OR REPLACE INTO test_runs
                        (run_id, report_period, test_id, test_name, run_status, tester, finished_time,
                         test_week, project, model, aidas, top_aida, source_file)
                        VALUES (:run_id, :report_period, :test_id, :test_name, :run_status, :tester,
                                :finished_time, :test_week, :project, :model, :aidas, :top_aida, :source_file)
                    ''', records)
                    self._local.conn.commit()
                    logging.info(f"[DB] 插入/更新 {len(records)} 条 test runs")
            except sqlite3.Error as e:
                logging.error(f"[DB] 插入 test runs 错误: {e}")

    def insert_history_logs(self, history_data: List[Dict], object_id: str, source_file: str = ""):
        """批量插入 history logs"""
        if not history_data:
            return

        self._ensure_connection()
        records = []

        for record in history_data:
            if not isinstance(record, dict):
                continue

            records.append({
                'object_id': str(object_id),
                'log_timestamp': record.get('timestamp'),
                'user': record.get('user', {}).get('full_name') if isinstance(record.get('user'), dict) else None,
                'action_type': record.get('operation_type'),
                'change_details': json.dumps(record.get('change_set')) if record.get('change_set') else json.dumps(record),
                'source_file': source_file,
                'source_format': 'SpecificJSON'
            })

        if records:
            try:
                with db_lock:
                    self._local.cursor.executemany('''
                        INSERT INTO history_log
                        (object_id, log_timestamp, user, action_type, change_details, source_file, source_format)
                        VALUES (:object_id, :log_timestamp, :user, :action_type, :change_details, :source_file, :source_format)
                    ''', records)
                    self._local.conn.commit()
            except sqlite3.Error as e:
                logging.error(f"[DB] 插入 history logs 错误: {e}")

    @staticmethod
    def _calculate_test_week(timestamp_str: str) -> str:
        """从时间戳计算测试周"""
        if not timestamp_str:
            return 'Future Planning'
        try:
            dt = pd.to_datetime(timestamp_str.replace('T', ' ').replace('Z', ''),
                               errors='coerce', format='%Y-%m-%d %H:%M:%S')
            if pd.isna(dt):
                dt = pd.to_datetime(timestamp_str.split('.')[0], errors='coerce')
            if not pd.isna(dt):
                return dt.strftime('%y-CW%V')
        except Exception:
            pass
        return 'Future Planning'

    def close(self):
        """关闭连接"""
        if hasattr(self._local, 'conn') and self._local.conn:
            self._local.conn.close()
            self._local.conn = None


# --- Parent-Child 关联缺陷处理（与 downloader7 一致）---

def extract_and_download_related_defects(session, defect_data, db_manager: Optional[DatabaseManager],
                                         output_dir: str, year_str: str, save_csv_flag: bool,
                                         save_excel_flag: bool, limit_per_page: int, max_workers: int):
    """
    从已下载的缺陷数据中，识别 Child 缺陷并下载关联的 Master 缺陷
    与 downloader7 完全一致
    """
    if not defect_data:
        logging.info("没有缺陷数据用于提取关联关系")
        return

    master_to_referencing_child_ids = {}

    logging.info("分析缺陷数据，查找 'Child' 类型缺陷...")
    for defect in defect_data:
        parent_child_info = defect.get("parent_child_udf", {})
        current_child_defect_id = defect.get('id')

        if not current_child_defect_id:
            continue
        current_child_defect_id = str(current_child_defect_id)

        if isinstance(parent_child_info, dict) and "child" in parent_child_info.get("name", "").lower():
            relation_to = defect.get("relation_to_udf")
            child_type_name = parent_child_info.get('name', '未知类型')
            master_ids_from_relation = []

            if relation_to and isinstance(relation_to, str):
                master_ids_from_relation = [d_id.strip() for d_id in relation_to.split(',') if d_id.strip()]
            elif relation_to and isinstance(relation_to, (int, float)):
                master_ids_from_relation.append(str(relation_to))

            if master_ids_from_relation:
                logging.info(f"Child缺陷 ID: {current_child_defect_id} (类型: {child_type_name}), "
                           f"解析出 Master ID(s): {master_ids_from_relation}")
                for master_id in master_ids_from_relation:
                    master_to_referencing_child_ids.setdefault(master_id, []).append(current_child_defect_id)

    unique_master_ids_to_fetch = list(master_to_referencing_child_ids.keys())

    if not unique_master_ids_to_fetch:
        logging.info("未找到任何可下载的 Master 缺陷ID")
        return

    logging.info(f"共找到 {len(unique_master_ids_to_fetch)} 个唯一的 Master 缺陷ID")

    # ID 格式验证和清理
    valid_ids = []
    invalid_ids = []

    for master_id in unique_master_ids_to_fetch:
        if not master_id or str(master_id).strip() == '':
            invalid_ids.append(master_id)
            continue

        master_id_str = str(master_id).strip()

        # 清理包含"Defect"前缀的ID
        if master_id_str.lower().startswith('defect'):
            numbers = re.findall(r'\d+', master_id_str)
            if numbers:
                master_id_str = numbers[0]
            else:
                invalid_ids.append(master_id)
                continue

        # 移除特殊字符
        master_id_str = re.sub(r'[^\w-]', '', master_id_str)

        if not master_id_str:
            invalid_ids.append(master_id)
            continue

        valid_ids.append(master_id_str)

    if invalid_ids:
        logging.warning(f"发现 {len(invalid_ids)} 个无效 Master ID")

    if not valid_ids:
        logging.warning("没有有效的 Master ID 可供下载")
        return

    # 分块下载（每块50个ID）
    chunks = [valid_ids[i:i + 50] for i in range(0, len(valid_ids), 50)]
    all_master_defects_data = []
    failed_ids = {}
    successful_ids = set()

    for chunk_idx, chunk in enumerate(chunks):
        valid_chunk_ids = []
        for chunk_id in chunk:
            chunk_id_str = str(chunk_id).strip()
            if ' ' in chunk_id_str or any(char in chunk_id_str for char in ['(', ')', '[', ']', '{', '}', '"', "'"]):
                failed_ids[chunk_id_str] = "ID格式包含特殊字符"
                continue
            valid_chunk_ids.append(chunk_id_str)

        if not valid_chunk_ids:
            continue

        id_conditions = [f"id='{master_id}'" for master_id in valid_chunk_ids]
        id_query = "||".join(id_conditions)
        query = f'"({id_query})"'

        logging.info(f"下载 Master 缺陷数据块 {chunk_idx + 1}/{len(chunks)}...")

        master_defects_chunk = fetch_octane_data_parallel(
            session, EP_DEFECT, DEFAULT_F_DEFECT_MAIN, query,
            limit_per_page=limit_per_page, max_workers=max_workers
        )

        if master_defects_chunk:
            chunk_successful_ids = {str(item.get("id")) for item in master_defects_chunk}
            successful_ids.update(chunk_successful_ids)

            chunk_failed_ids = set(valid_chunk_ids) - chunk_successful_ids
            for failed_id in chunk_failed_ids:
                failed_ids[failed_id] = "API查询未返回数据"

            for master_defect_item in master_defects_chunk:
                master_item_id = str(master_defect_item.get("id"))
                referencing_child_ids = master_to_referencing_child_ids.get(master_item_id, [])

                if referencing_child_ids:
                    master_defect_item["referenced_by_child_id"] = referencing_child_ids[0]
                    if len(referencing_child_ids) > 1:
                        logging.warning(
                            f"Master 缺陷 {master_item_id} 被多个 Child 缺陷引用: {referencing_child_ids}"
                        )
                else:
                    master_defect_item["referenced_by_child_id"] = None

                all_master_defects_data.append(master_defect_item)
        else:
            for failed_id in valid_chunk_ids:
                failed_ids[failed_id] = "整个数据块查询失败"

    # 并发重试失败的ID
    if failed_ids:
        logging.info(f"尝试并发重试 {len(failed_ids)} 个失败的 Master ID...")
        retry_successful = 0
        failed_ids_list = list(failed_ids.keys())

        def retry_single_id(failed_id):
            try:
                single_query = f'"(id=\'{failed_id}\')"'
                single_result = fetch_octane_data(
                    session, EP_DEFECT, DEFAULT_F_DEFECT_MAIN, single_query,
                    limit_per_page=limit_per_page
                )

                if single_result:
                    return failed_id, single_result, None
                else:
                    return failed_id, None, "重试仍无数据"
            except Exception as e:
                return failed_id, None, f"重试异常: {str(e)}"

        with concurrent.futures.ThreadPoolExecutor(max_workers=min(max_workers, len(failed_ids_list))) as executor:
            retry_futures = {executor.submit(retry_single_id, failed_id): failed_id
                           for failed_id in failed_ids_list}

            for future in tqdm(concurrent.futures.as_completed(retry_futures),
                              total=len(retry_futures), desc="重试失败的 Master ID"):
                failed_id, single_result, error_msg = future.result()

                if single_result:
                    for master_defect_item in single_result:
                        master_item_id = str(master_defect_item.get("id"))
                        referencing_child_ids = master_to_referencing_child_ids.get(master_item_id, [])
                        master_defect_item["referenced_by_child_id"] = referencing_child_ids[0] if referencing_child_ids else None
                        all_master_defects_data.append(master_defect_item)

                    del failed_ids[failed_id]
                    successful_ids.add(failed_id)
                    retry_successful += 1
                else:
                    failed_ids[failed_id] = error_msg

        logging.info(f"重试完成，成功: {retry_successful}, 仍失败: {len(failed_ids)}")

    # 保存失败报告
    if failed_ids:
        failure_report_path = os.path.join(output_dir, f"{year_str}_master_download_failures.json")
        try:
            with open(failure_report_path, "w", encoding="utf-8") as f:
                json.dump({
                    'failed_master_ids': failed_ids,
                    'summary': {
                        'total_failed': len(failed_ids),
                        'successful': len(successful_ids),
                        'total_requested': len(unique_master_ids_to_fetch)
                    }
                }, f, ensure_ascii=False, indent=2)
            logging.info(f"失败报告已保存: {failure_report_path}")
        except Exception as e:
            logging.error(f"保存失败报告错误: {e}")

    # 保存到数据库或文件
    if all_master_defects_data:
        # 保存到本地文件
        filename = f"{year_str}_defect_master"
        save_data_to_file(all_master_defects_data, filename, output_dir, save_csv_flag, save_excel_flag)
        logging.info(f"已保存 {len(all_master_defects_data)} 个 Master 缺陷到文件")

        # 保存到数据库
        if db_manager:
            db_manager.insert_defects(all_master_defects_data, int(year_str), f"{year_str}_defect_master.json")

        logging.info(f"成功率: {len(successful_ids)}/{len(valid_ids)} ({len(successful_ids)/len(valid_ids)*100:.1f}%)")


# --- History 下载模块 ---

def get_all_defect_ids_for_history(session, team="DTSV_China", start_date=None, end_date=None,
                                   filter_field="creation_time", limit_per_page=DEFAULT_LIMIT_PER_PAGE):
    """获取符合条件的所有 defect ID"""
    start_date_formatted = f"{start_date}T00:00:00Z" if start_date else "2000-01-01T00:00:00Z"
    end_date_formatted = f"{end_date}T23:59:59Z" if end_date else "2099-12-31T23:59:59Z"

    field_description = "创建" if filter_field == "creation_time" else "修改"
    logging.info(f"获取 {team} 在 {start_date} 至 {end_date} 期间按{field_description}筛选的 defect ID...")

    query_parts = []
    if team:
        safe_team_name = team.replace("'", "\\'")
        query_parts.append(f"problem_finder_team_udf={{name=\'{safe_team_name}\'}}")

    if start_date:
        query_parts.append(f"{filter_field}>=\'{start_date_formatted}\'")
    if end_date:
        query_parts.append(f"{filter_field}<=\'{end_date_formatted}\'")

    if not query_parts:
        query = '""'
    else:
        query_string = ";".join(query_parts)
        query = f'"({query_string})"'

    try:
        resp_data = fetch_octane_data_parallel(
            session, EP_DEFECT, ("id",), query,
            limit_per_page=limit_per_page, max_workers=10
        )

        if not resp_data:
            return []

        defect_ids = [item["id"] for item in resp_data]
        logging.info(f"总共获取到 {len(defect_ids)} 个 defect ID")
        return list(set(defect_ids))

    except Exception as e:
        logging.error(f"获取 defect ID 异常: {e}")
        return []


def get_single_defect_history(defect_id, session):
    """获取单个 defect 的历史记录"""
    s_query = f'"(entity_id=\'{defect_id}\';entity_type=\'defect\')"'

    request_params = {
        "query": s_query,
        "limit": 10000,
        "offset": 0,
        "order_by": "-timestamp"
    }

    request_params_encoded = urllib.parse.urlencode(request_params)
    request_url = f"{API_BASE_URL}/{EP_HISTORY}?{request_params_encoded}"

    try:
        resp = session.get(request_url, verify=False, allow_redirects=True, timeout=90)

        if not (200 <= resp.status_code < 400):
            logging.warning(f"获取 defect {defect_id} 历史失败: {resp.status_code}")
            return None

        return resp.json()

    except Exception as e:
        logging.error(f"获取 defect {defect_id} 历史异常: {e}")
        return None


def fetch_histories_parallel(defect_ids, session, max_workers, output_dir, db_manager: Optional[DatabaseManager] = None):
    """并行获取多个 defect 的历史记录"""
    processed_ids = []
    error_ids = []

    os.makedirs(output_dir, exist_ok=True)
    logging.info(f"历史记录将保存到: {output_dir}")

    with tqdm(total=len(defect_ids), desc="获取 Defect 历史") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_id = {
                executor.submit(get_single_defect_history, defect_id, session): defect_id
                for defect_id in defect_ids
            }

            for future in concurrent.futures.as_completed(future_to_id):
                defect_id = future_to_id[future]
                try:
                    history_data = future.result()

                    if history_data and history_data.get("data"):
                        # 保存到本地文件
                        history_filename = os.path.join(output_dir, f"{defect_id}_history.json")
                        with open(history_filename, "w", encoding="utf-8") as f:
                            json.dump(history_data, f, ensure_ascii=False, indent=2)

                        # 保存到数据库
                        if db_manager:
                            db_manager.insert_history_logs(history_data.get("data", []), defect_id, history_filename)

                        processed_ids.append(defect_id)
                    elif history_data is None:
                        error_ids.append(defect_id)
                    else:
                        logging.debug(f"Defect {defect_id} 历史数据为空")
                        error_ids.append(defect_id)

                except Exception as e:
                    logging.error(f"处理 defect {defect_id} 历史错误: {e}")
                    error_ids.append(defect_id)

                pbar.update(1)

    logging.info(f"历史记录获取完成！成功: {len(processed_ids)}, 失败: {len(error_ids)}")

    if error_ids:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        failed_ids_filename = os.path.join(output_dir, f"failed_defect_ids_for_history_{timestamp}.json")
        with open(failed_ids_filename, "w", encoding="utf-8") as f:
            json.dump(error_ids, f, ensure_ascii=False, indent=2)
        logging.warning(f"已将失败的 {len(error_ids)} 个 defect ID 保存至: {failed_ids_filename}")

    return processed_ids, error_ids


# --- 文件保存工具 ---

def save_data_to_file(data_to_save, filename_prefix, output_directory, save_csv_flag=False, save_excel_flag=False):
    """保存数据到本地文件"""
    if not data_to_save:
        logging.warning(f"没有数据保存到 {filename_prefix}")
        return

    os.makedirs(output_directory, exist_ok=True)
    json_filepath = os.path.join(output_directory, f"{filename_prefix}.json")

    try:
        with open(json_filepath, "w", encoding="utf-8") as f:
            json.dump({"data": data_to_save}, f, ensure_ascii=False, indent=2)
        logging.info(f"数据已保存为 JSON: {json_filepath}")
    except Exception as e:
        logging.error(f"保存 JSON 错误: {e}")

    if isinstance(data_to_save, list) and data_to_save and isinstance(data_to_save[0], dict):
        if save_csv_flag or save_excel_flag:
            try:
                df = pd.json_normalize(data_to_save, sep='_')
                if save_csv_flag:
                    csv_filepath = os.path.join(output_directory, f"{filename_prefix}.csv")
                    df.to_csv(csv_filepath, index=False, encoding="utf-8")
                    logging.info(f"数据已保存为 CSV: {csv_filepath}")
                if save_excel_flag:
                    excel_filepath = os.path.join(output_directory, f"{filename_prefix}.xlsx")
                    df.to_excel(excel_filepath, index=False, engine="openpyxl")
                    logging.info(f"数据已保存为 Excel: {excel_filepath}")
            except Exception as e:
                logging.error(f"保存 CSV/Excel 错误: {e}")


# --- 主程序 ---

def main():
    global DEFAULT_LIMIT_PER_PAGE

    parser = argparse.ArgumentParser(description="Octane 全量数据下载器 - 生产级版本")

    auth_group = parser.add_argument_group('认证选项')
    auth_group.add_argument("--auth-method", choices=['sso', 'cookie'], default='cookie',
                           help="认证方法 (默认: cookie)")
    auth_group.add_argument("--login-file", default="login_info.txt",
                           help="SSO 用户名密码文件")
    auth_group.add_argument("--cookie-file", default="cookie.txt",
                           help="Cookie 文件路径")

    general_group = parser.add_argument_group('通用选项')
    general_group.add_argument("--team", default=DEFAULT_TEAM,
                              help=f"默认团队 (默认: {DEFAULT_TEAM})")
    general_group.add_argument("--save-csv", action='store_true',
                              help="同时保存为 CSV")
    general_group.add_argument("--save-excel", action='store_true',
                              help="同时保存为 Excel")
    general_group.add_argument("--limit-per-page", type=int, default=DEFAULT_LIMIT_PER_PAGE,
                              help=f"API 分页大小 (默认: {DEFAULT_LIMIT_PER_PAGE})")

    defect_group = parser.add_argument_group('Defect 下载选项')
    defect_group.add_argument("--skip-defects", action='store_true',
                             help="跳过下载 Defects")
    current_year = datetime.now().year
    default_years = f"{current_year-1},{current_year}"
    defect_group.add_argument("--defect-years", default=default_years,
                             help=f"Defects 年份列表 (默认: {default_years})")
    defect_group.add_argument("--skip-parent-related", action='store_true',
                             help="跳过下载 Parent 关联的 Master 缺陷")

    mr_group = parser.add_argument_group('Manual Run 下载选项')
    mr_group.add_argument("--skip-mr", action='store_true',
                         help="跳过下载 Manual Runs")
    default_mr_spec = f"{current_year-1}:01-13,{current_year}:01-13"
    mr_group.add_argument("--mr-spec", default=default_mr_spec,
                         help=f"MR 年份和 Release 范围 (默认: {default_mr_spec})")

    history_group = parser.add_argument_group('History 下载选项')
    history_group.add_argument("--skip-history", action='store_true',
                              help="跳过历史下载")
    history_group.add_argument("--history-max-workers", type=int, default=50,
                              help="并行下载历史线程数 (默认: 50)")
    history_group.add_argument("--history-output-dir", default="history",
                              help="保存历史记录的目录 (默认: history)")
    history_group.add_argument("--history-team", default=None,
                              help="历史下载的团队 (默认: 使用 --team)")
    default_start = f"{current_year-1}-01-01"
    default_end = datetime.now().strftime("%Y-%m-%d")
    history_group.add_argument("--history-start-date", default=default_start,
                              help=f"历史开始日期 (默认: {default_start})")
    history_group.add_argument("--history-end-date", default=default_end,
                              help=f"历史结束日期 (默认: {default_end})")
    history_group.add_argument("--history-filter-field", choices=['creation_time', 'last_modified'],
                              default='creation_time', help="历史筛选字段 (默认: creation_time)")

    db_group = parser.add_argument_group('数据库选项')
    db_group.add_argument("--direct-to-db", action='store_true',
                         help="直接入库模式: API → SQLite，跳过本地文件保存")
    db_group.add_argument("--db-path", default=DB_FILE,
                         help=f"SQLite 数据库路径 (默认: {DB_FILE})")

    performance_group = parser.add_argument_group('性能选项')
    performance_group.add_argument("--turbo-mode", action='store_true',
                                  help="极限性能模式 (更大分页+更多并发+极小延迟)")
    performance_group.add_argument("--max-concurrent-requests", type=int, default=10,
                                  help="最大并发请求数 (默认: 10, 极限模式: 25)")

    args = parser.parse_args()

    # 应用性能优化设置
    if args.turbo_mode:
        DEFAULT_LIMIT_PER_PAGE = TURBO_LIMIT_PER_PAGE
        args.history_max_workers = min(25, args.history_max_workers)
        args.max_concurrent_requests = 25
        logging.info("🚀 极限性能模式已启用！分页=10000，并发=25")
    else:
        logging.info("🚀 超级性能优化模式：分页=5000，并发=10")

    # 初始化数据库管理器
    db_manager = None
    if args.direct_to_db:
        try:
            import threading
            db_manager = DatabaseManager(args.db_path)
            logging.info(f"📦 直接入库模式已启用，数据库: {args.db_path}")
        except Exception as e:
            logging.error(f"数据库初始化失败: {e}")
            return
    else:
        logging.info("💾 文件保存模式: 数据将保存到本地 JSON/CSV/Excel 文件")

    # 认证
    session_active = get_authenticated_session(args.auth_method, args.login_file, args.cookie_file)
    if not session_active:
        logging.critical("认证失败，脚本终止")
        return

    # 设置输出目录
    script_dir_path = os.path.dirname(os.path.abspath(__file__))
    defect_output_path = os.path.join(script_dir_path, "defect")
    mr_output_path = os.path.join(script_dir_path, "mr")
    history_output_path = os.path.join(script_dir_path, args.history_output_dir)

    os.makedirs(defect_output_path, exist_ok=True)
    os.makedirs(mr_output_path, exist_ok=True)
    os.makedirs(history_output_path, exist_ok=True)

    # 存储每年下载的 defect 数据，用于处理 Parent 关联
    year_to_defects_map = {}

    # --- 下载 Defects ---
    if not args.skip_defects and args.defect_years:
        years_list = [y.strip() for y in args.defect_years.split(',')
                     if y.strip().isdigit() and len(y.strip()) == 4]

        for year_str in years_list:
            logging.info(f"📥 下载 {year_str} Defects (团队: {args.team})...")
            start_t = f"{year_str}-01-01T00:00:00Z"
            end_t = f"{year_str}-12-31T23:59:59Z"

            # 构建查询
            time_query = f"creation_time>=\'{start_t}\';creation_time<=\'{end_t}\'"
            team_query_parts = []
            if args.team:
                safe_team = args.team.replace("'", "\\'")
                team_query_parts.append(f"problem_finder_team_udf={{name=\'{safe_team}\'}}")
                team_query_parts.append(f"author={{name=\'{safe_team}\'}}")
                team_query_parts.append(f"team={{name=\'{safe_team}\'}}")

            if team_query_parts:
                team_combined = f"({'||'.join(team_query_parts)})"
                q_defect = f'"(({time_query});{team_combined})"'
            else:
                q_defect = f'"({time_query})"'

            # 并行下载
            defect_data_list = fetch_octane_data_parallel(
                session_active, EP_DEFECT, DEFAULT_F_DEFECT_MAIN, q_defect,
                order_by="creation_time", limit_per_page=args.limit_per_page,
                max_workers=args.max_concurrent_requests
            )

            if defect_data_list:
                # 保存到文件
                if not args.direct_to_db:
                    fn_defect = f"{year_str}_defect"
                    save_data_to_file(defect_data_list, fn_defect, defect_output_path,
                                     args.save_csv, args.save_excel)

                # 保存到数据库
                if db_manager:
                    db_manager.insert_defects(defect_data_list, int(year_str), f"{year_str}_defect.json")

                # 存储用于后续处理 Parent 关联
                year_to_defects_map[year_str] = defect_data_list
                logging.info(f"✅ {year_str} Defects 下载完成: {len(defect_data_list)} 条")
            else:
                logging.warning(f"⚠️ {year_str} 未找到 Defects")

    # --- 处理 Parent 关联缺陷 ---
    if not args.skip_defects and not args.skip_parent_related and year_to_defects_map:
        logging.info("🔗 开始处理 Child 关联缺陷...")
        for year_str, defects_data in year_to_defects_map.items():
            extract_and_download_related_defects(
                session_active, defects_data, db_manager,
                defect_output_path, year_str,
                args.save_csv, args.save_excel,
                args.limit_per_page, args.max_concurrent_requests
            )

    # --- 下载 Manual Runs ---
    if not args.skip_mr and args.mr_spec:
        year_specs = args.mr_spec.split(',')
        for spec in year_specs:
            try:
                if ':' not in spec:
                    logging.error(f"MR 规范格式错误: {spec}")
                    continue

                year_s, rel_s = spec.strip().split(':', 1)
                year_v = int(year_s)

                rels_fetch = []
                for group in rel_s.split(';'):
                    group = group.strip()
                    if not group:
                        continue
                    if '-' in group:
                        s, e = map(int, group.split('-'))
                        rels_fetch.extend([f"{i:02d}" for i in range(s, e + 1)])
                    elif group.isdigit():
                        rels_fetch.append(f"{int(group):02d}")

                rels_fetch = sorted(list(set(rels_fetch)))

                for rel_num in rels_fetch:
                    rel_name = f"R-{str(year_v)[-2:]}-{rel_num}"
                    logging.info(f"📥 下载 {rel_name}...")

                    safe_team = args.team.replace("'", "\\'")
                    q_mr = f'"(run_team_000_udf={{name=\'{safe_team}\'}});(release={{name=\'{rel_name}\'}})"'

                    mr_data = fetch_octane_data_parallel(
                        session_active, EP_MANUALRUN, DEFAULT_F_MANUALRUN, q_mr,
                        limit_per_page=args.limit_per_page,
                        max_workers=args.max_concurrent_requests
                    )

                    if mr_data:
                        report_period = f"R{str(year_v)[-2:]}{rel_num}"

                        # 保存到文件
                        if not args.direct_to_db:
                            fn_mr = f"R{str(year_v)[-2:]}{rel_num}"
                            save_data_to_file(mr_data, fn_mr, mr_output_path,
                                            args.save_csv, args.save_excel)

                        # 保存到数据库
                        if db_manager:
                            db_manager.insert_test_runs(mr_data, report_period, f"{fn_mr}.json")

                        logging.info(f"✅ {rel_name} 下载完成: {len(mr_data)} 条")
                    else:
                        logging.info(f"ℹ️ {rel_name} 无数据")

            except Exception as e:
                logging.error(f"处理 MR 规范错误: {e}")

    # --- 下载 History ---
    if not args.skip_history:
        logging.info("📜 开始下载 Defect History...")

        hist_start = args.history_start_date
        hist_end = args.history_end_date
        hist_team = args.history_team or args.team
        hist_filter = args.history_filter_field

        logging.info(f"历史下载配置: 团队={hist_team}, 范围={hist_start} 至 {hist_end}, 字段={hist_filter}")

        defect_ids = get_all_defect_ids_for_history(
            session_active, hist_team, hist_start, hist_end, hist_filter, args.limit_per_page
        )

        if defect_ids:
            hist_workers = min(max(1, args.history_max_workers), 50)
            logging.info(f"使用 {hist_workers} 线程并行获取 {len(defect_ids)} 个 Defects 的历史...")

            fetch_histories_parallel(defect_ids, session_active, hist_workers,
                                    history_output_path, db_manager)
        else:
            logging.warning("未找到符合条件的 Defect IDs")

    # 清理
    if db_manager:
        db_manager.close()

    logging.info("🎉 所有任务完成!")


if __name__ == "__main__":
    main()
