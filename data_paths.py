"""
数据路径统一配置
解决 mr_data/ vs mr/ 等目录不一致问题
"""
import os

# 可配置的数据目录（可通过环境变量覆盖）
DATA_DIRS = {
    "defect": os.getenv("DEFECT_DIR", "defect"),
    "mr": os.getenv("MR_DIR", "mr"),  # 统一使用mr/而不是mr_data/
    "history": os.getenv("HISTORY_DIR", "history"),
    "aida": os.getenv("AIDA_DIR", "aida"),
    "cache": os.getenv("CACHE_DIR", "cache"),
}

# 年份配置（动态检测或固定）
ACTIVE_YEARS = os.getenv("ACTIVE_YEARS", "2025,2026").split(",")
ACTIVE_YEARS = [int(y.strip()) for y in ACTIVE_YEARS]


def get_data_path(data_type: str, filename: str = None) -> str:
    """
    获取标准化的数据路径

    Args:
        data_type: 数据类型 (defect/mr/history/aida/cache)
        filename: 可选的具体文件名

    Returns:
        完整路径
    """
    base = DATA_DIRS.get(data_type, data_type)
    if filename:
        return os.path.join(base, filename)
    return base


def get_defect_files(years: list = None) -> list:
    """获取缺陷文件列表（支持多版本）"""
    years = years or ACTIVE_YEARS
    files = []
    for year in years:
        # 优先检查.json，然后是.csv
        for ext in [".json", ".csv"]:
            f = get_data_path("defect", f"{year}_defect{ext}")
            if os.path.exists(f):
                files.append(f)
                break
    return files


def get_mr_files() -> list:
    """获取Manual Run文件列表"""
    import glob
    mr_dir = DATA_DIRS["mr"]
    # 支持 R25*.json, R2601.json 等模式
    patterns = ["R25*.json", "R26*.json", "R*.json"]
    files = []
    for pattern in patterns:
        files.extend(glob.glob(os.path.join(mr_dir, pattern)))
    return sorted(files)


# 向后兼容的便捷变量
DEFECT_DIR = DATA_DIRS["defect"]
MR_DIR = DATA_DIRS["mr"]
HISTORY_DIR = DATA_DIRS["history"]
AIDA_DIR = DATA_DIRS["aida"]
CACHE_DIR = DATA_DIRS["cache"]
