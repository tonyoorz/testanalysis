#!/usr/bin/env python3
"""
迁移脚本：修复 octane_defects 表中缺失的字段
从 raw_json 中提取并重新计算所有派生字段
"""

import json
import sqlite3
import re
from pathlib import Path

# 导入 data_processor 中的相关函数
import sys
sys.path.insert(0, str(Path(__file__).parent))

DB_PATH = "database/local_data.db"
EXCEL_FILE = "aida/top_aida_project_fv_mapping.xlsx"


def extract_english(text):
    """从文本中提取英文单词"""
    if not text or text == '':
        return 'Unknown'
    english_words = re.findall(r'[a-zA-Z]+', str(text))
    return ' '.join(english_words) if english_words else 'Unknown'


def get_top_req(req_list):
    """从 AIDA 列表中提取最短的作为 top_aida"""
    if not isinstance(req_list, list) or len(req_list) == 0:
        return ''
    top_req = ''
    len_req = 1000
    for ith_req in req_list:
        if not isinstance(ith_req, str):
            continue
        parts = ith_req.split(' ')
        if not parts:
            continue
        last_part = parts[-1]
        if not last_part:
            continue
        try:
            len_ith_req = len(last_part)
        except TypeError:
            continue
        if len_ith_req < len_req:
            len_req = len_ith_req
            top_req = ith_req
    return top_req


def extract_full_name(field_value):
    """从嵌套字典中提取 full_name"""
    if isinstance(field_value, dict):
        return field_value.get('full_name') or field_value.get('name')
    return field_value


def get_aidas_from_product_areas(pa_data):
    """从 product_areas 提取 aidas 列表"""
    if not pa_data:
        return []
    if isinstance(pa_data, dict):
        data = pa_data.get('data', [])
        if isinstance(data, list):
            return [pa.get('name', '') for pa in data if isinstance(pa, dict) and pa.get('name')]
        return []
    if isinstance(pa_data, list):
        return [pa.get('name', '') for pa in pa_data if isinstance(pa, dict) and pa.get('name')]
    return []


def load_aida_fv_mapping():
    """加载 AIDA 到 FV 的映射"""
    mapping = {}

    if not Path(EXCEL_FILE).exists():
        print(f"警告: Excel 文件 '{EXCEL_FILE}' 不存在")
        return mapping

    try:
        import pandas as pd
        for sheet_name in ['IDCevo', 'IDC', 'MGU', 'App', 'RSU']:
            try:
                df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
                if 'top_aida' in df.columns and 'fv' in df.columns:
                    for _, row in df.iterrows():
                        if pd.notna(row['top_aida']) and pd.notna(row['fv']):
                            aida = str(row['top_aida']).strip()
                            fv = str(row['fv']).strip()
                            if aida and fv and fv != 'nan':
                                mapping[aida] = fv
                                aida_english = extract_english(aida)
                                if aida_english and aida_english != 'Unknown':
                                    mapping[aida_english] = fv
                if 'aida_english' in df.columns and 'fv' in df.columns:
                    for _, row in df.iterrows():
                        if pd.notna(row['aida_english']) and pd.notna(row['fv']):
                            aida_english = str(row['aida_english']).strip()
                            fv = str(row['fv']).strip()
                            if aida_english and fv and fv != 'nan':
                                mapping[aida_english] = fv
            except Exception as e:
                print(f"  处理工作表 '{sheet_name}' 时出错: {e}")
                continue
    except Exception as e:
        print(f"加载 AIDA/FV 映射失败: {e}")

    return mapping


def get_fvp_from_fv(fv):
    """根据 FV 获取 FVP"""
    if not fv:
        return None

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
        'IuK_TSP_HMI': 'Jerry',
        'DIPS_TSP_RSU': 'Jerry',
        'IuK_TSP_Carfunctions': 'Jerry',
        'IuK_TSP_Perso CN': 'Jerry',
        'RSU': 'Jerry',
        'Mybmw App': 'Marin'
    }

    return fvp_mapping.get(fv)


def migrate_defects():
    """迁移缺陷数据"""
    print("开始迁移缺陷数据...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 加载 AIDA/FV 映射
    print("加载 AIDA/FV 映射...")
    aida_fv_map = load_aida_fv_mapping()
    print(f"  加载了 {len(aida_fv_map)} 个映射")

    # 获取所有记录
    cursor.execute("SELECT defect_id, raw_json FROM octane_defects")
    records = cursor.fetchall()
    print(f"共有 {len(records)} 条记录需要处理")

    updated = 0
    errors = 0

    for defect_id, raw_json in records:
        try:
            defect = json.loads(raw_json)

            # 提取字段
            author = extract_full_name(defect.get('author'))
            owner = extract_full_name(defect.get('owner'))
            detected_by = extract_full_name(defect.get('detected_by'))

            # 处理 product_areas
            product_areas_raw = defect.get('product_areas')
            aidas_list = get_aidas_from_product_areas(product_areas_raw)

            # 计算 top_aida 和 aida_english
            top_aida = get_top_req(aidas_list)
            aida_english = extract_english(top_aida)

            # 提取其他字段
            reporting_class = extract_full_name(defect.get('reporting_class_udf'))
            function_responsible = extract_full_name(defect.get('function_responsible1_udf'))
            solution_responsible = extract_full_name(defect.get('solution_responsible_udf'))
            solution_cluster = extract_full_name(defect.get('solution_cluster_udf'))

            # 分配 FV
            fv = aida_fv_map.get(top_aida) or aida_fv_map.get(aida_english)
            fvp = get_fvp_from_fv(fv)

            # product_areas 存储为逗号分隔字符串
            product_areas_str = ','.join(aidas_list) if aidas_list else None

            # 更新数据库
            cursor.execute("""
                UPDATE octane_defects SET
                    author = ?,
                    owner = ?,
                    detected_by = ?,
                    top_aida = ?,
                    aida_english = ?,
                    product_areas = ?,
                    reporting_class = ?,
                    function_responsible = ?,
                    solution_responsible = ?,
                    solution_cluster = ?,
                    fv = ?,
                    fvp = ?
                WHERE defect_id = ?
            """, (
                author, owner, detected_by, top_aida, aida_english,
                product_areas_str, reporting_class, function_responsible,
                solution_responsible, solution_cluster, fv, fvp, defect_id
            ))

            updated += 1
            if updated % 500 == 0:
                conn.commit()
                print(f"  已处理 {updated} 条记录...")

        except Exception as e:
            print(f"  处理记录 {defect_id} 时出错: {e}")
            errors += 1
            continue

    conn.commit()
    conn.close()

    print(f"\n迁移完成:")
    print(f"  成功更新: {updated} 条")
    print(f"  错误: {errors} 条")


if __name__ == "__main__":
    migrate_defects()
