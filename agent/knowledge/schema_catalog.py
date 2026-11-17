"""
Schema业务语义目录

将数据库Schema与业务语义关联，让Agent真正理解数据含义
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json
import os


@dataclass
class ColumnSemantics:
    """字段业务语义定义"""
    business_name: str  # 业务名称
    description: str  # 业务描述
    data_type: str  # 数据类型
    examples: List[str] = field(default_factory=list)  # 示例值
    business_values: Dict[str, str] = field(default_factory=dict)  # 业务值映射
    calculation_rule: Optional[str] = None  # 计算规则
    business_rules: List[str] = field(default_factory=list)  # 业务规则
    aliases: List[str] = field(default_factory=list)  # 别名（用于NL理解）
    category: str = "general"  # 分类：basic, classification, temporal, relation, calculated


@dataclass
class TableSemantics:
    """表业务语义定义"""
    business_name: str  # 业务名称
    description: str  # 业务描述
    columns: Dict[str, ColumnSemantics]  # 字段定义
    primary_key: str  # 主键
    relationships: List[Dict[str, str]] = field(default_factory=list)  # 关联关系
    common_queries: List[str] = field(default_factory=list)  # 常见查询模式


class SchemaCatalog:
    """Schema业务语义目录"""

    def __init__(self):
        self.tables: Dict[str, TableSemantics] = {}
        self._init_defects_table()
        self._init_payloads_table()
        self._init_histories_table()

    def _init_defects_table(self):
        """初始化缺陷主表语义"""
        self.tables["octane_defects"] = TableSemantics(
            business_name="缺陷主表",
            description="存储所有缺陷的基本信息、状态、分类和关联关系",
            primary_key="defect_id",
            columns={
                # ========== 主键和基本信息 ==========
                "defect_id": ColumnSemantics(
                    business_name="缺陷ID",
                    description="缺陷的唯一标识符",
                    data_type="TEXT",
                    examples=["123456", "789012"],
                    category="basic"
                ),
                "name": ColumnSemantics(
                    business_name="缺陷标题",
                    description="缺陷的简短描述",
                    data_type="TEXT",
                    examples=["Audio playback stuttering", "Navigation map not loading"],
                    category="basic"
                ),
                "creation_time": ColumnSemantics(
                    business_name="创建时间",
                    description="缺陷被创建的时间",
                    data_type="DATETIME",
                    examples=["2025-01-15T10:30:00+08:00"],
                    category="temporal",
                    aliases=["创建时间", "创建日期", "发现时间", "created_at", "created_date"]
                ),
                "last_modified": ColumnSemantics(
                    business_name="最后修改时间",
                    description="缺陷最后被修改的时间",
                    data_type="DATETIME",
                    category="temporal"
                ),

                # ========== 团队和项目 ==========
                "team": ColumnSemantics(
                    business_name="负责团队",
                    description="当前负责处理该缺陷的团队",
                    data_type="TEXT",
                    examples=["DTSV_China", "Spotlight_FIT"],
                    business_values={
                        "DTSV_China": "中国DTSV团队",
                        "Spotlight_DTSV_China": "中国Spotlight团队",
                        "Spotlight_FIT": "FIT Spotlight团队",
                        "[AT]BBA_Basis-FIT": "BBA基础FIT团队",
                        "[AT]FIT_LAENDER_CHINA": "中国地区FIT团队",
                        "[AT]W71-FIT": "W71车型FIT团队",
                        "[AT]W72-FIT": "W72车型FIT团队"
                    },
                    category="classification",
                    aliases=["团队", "负责团队", "项目组"]
                ),
                "problem_finder_team": ColumnSemantics(
                    business_name="发现团队",
                    description="发现该缺陷的团队",
                    data_type="TEXT",
                    category="classification"
                ),
                "program": ColumnSemantics(
                    business_name="项目",
                    description="缺陷所属的项目",
                    data_type="TEXT",
                    examples=["idcevo", "idc", "mgu"],
                    business_values={
                        "idcevo": "IDCEVO项目-下一代座舱平台",
                        "idc": "IDC项目-当前主力平台",
                        "mgu": "MGU项目-入门级平台",
                        "App": "应用项目",
                        "RSU": "RSU项目"
                    },
                    category="classification",
                    aliases=["项目", "project", "tproject", "program"]
                ),
                "author": ColumnSemantics(
                    business_name="创建人",
                    description="创建该缺陷的人员",
                    data_type="TEXT",
                    category="basic"
                ),

                # ========== AIDA分类 ==========
                "aida_businesskey": ColumnSemantics(
                    business_name="AIDA业务键",
                    description="AIDA的原始业务标识",
                    data_type="TEXT",
                    category="classification"
                ),
                "aida_english": ColumnSemantics(
                    business_name="AIDA英文名称",
                    description="AIDA的英文名称，代表一个核心客户功能",
                    data_type="TEXT",
                    examples=[
                        "Audio System",
                        "Navigation",
                        "Bluetooth Connectivity",
                        "Voice Recognition"
                    ],
                    category="classification",
                    aliases=["AIDA", "aida", "功能模块", "客户功能", "top_aida"]
                ),
                "top_aida": ColumnSemantics(
                    business_name="顶层AIDA",
                    description="顶层AIDA分类",
                    data_type="TEXT",
                    category="classification",
                    aliases=["顶层AIDA", "主AIDA"]
                ),
                "product_areas": ColumnSemantics(
                    business_name="产品区域",
                    description="产品功能区域",
                    data_type="TEXT",
                    category="classification"
                ),
                "user_tags": ColumnSemantics(
                    business_name="用户标签",
                    description="用户自定义标签，逗号分隔",
                    data_type="TEXT",
                    examples=["audio,bluetooth,critical", "navigation,map"],
                    category="classification",
                    aliases=["标签", "tag", "tags"]
                ),

                # ========== 状态和严重性 ==========
                "phase": ColumnSemantics(
                    business_name="阶段",
                    description="缺陷当前阶段",
                    data_type="TEXT",
                    examples=["New", "Assigned", "In Progress", "Fixed", "Closed"],
                    category="classification"
                ),
                "severity": ColumnSemantics(
                    business_name="严重级别",
                    description="缺陷的严重程度",
                    data_type="TEXT",
                    examples=["Critical", "Major", "Minor"],
                    business_values={
                        "Critical": "阻断性问题，车辆无法交付或存在安全风险，必须立即处理",
                        "Major": "严重影响功能或用户体验，需要优先处理",
                        "Minor": "轻微问题，不影响主要功能，按计划处理"
                    },
                    category="classification",
                    aliases=["严重性", "severity_group", "严重级别", "严重程度"]
                ),
                "problem_severity": ColumnSemantics(
                    business_name="问题严重级别",
                    description="问题的严重程度细分",
                    data_type="TEXT",
                    category="classification"
                ),
                "status_phase": ColumnSemantics(
                    business_name="组合状态",
                    description="缺陷的组合状态（计算字段）",
                    data_type="TEXT",
                    examples=["New", "Assigned", "In Progress", "Fixed", "Closed", "Rejected"],
                    business_values={
                        "New": "新建，尚未分配",
                        "Assigned": "已分配，等待处理",
                        "In Progress": "处理中",
                        "Fixed": "已修复，等待验证",
                        "Closed": "已关闭",
                        "Rejected": "被拒绝"
                    },
                    category="calculated",
                    aliases=["状态", "status", "当前状态"]
                ),

                # ========== 责任人 ==========
                "owner": ColumnSemantics(
                    business_name="负责人",
                    description="当前负责处理该缺陷的人员",
                    data_type="TEXT",
                    category="basic",
                    aliases=["负责人", "处理人", "assignee"]
                ),
                "detected_by": ColumnSemantics(
                    business_name="发现人",
                    description="发现该缺陷的人员",
                    data_type="TEXT",
                    category="basic"
                ),

                # ========== 版本和发布 ==========
                "detected_in_release": ColumnSemantics(
                    business_name="发现版本",
                    description="发现该缺陷的软件版本",
                    data_type="TEXT",
                    examples=["2025.03.1", "2025.04.0"],
                    category="classification"
                ),
                "software_version": ColumnSemantics(
                    business_name="软件版本",
                    description="相关软件版本",
                    data_type="TEXT",
                    category="classification"
                ),

                # ========== 车辆和ECU ==========
                "vin": ColumnSemantics(
                    business_name="车辆识别号",
                    description="发现缺陷的车辆VIN码",
                    data_type="TEXT",
                    examples=["WBA1234567890"],
                    category="basic",
                    aliases=["VIN", "vin_udf", "车辆识别码"]
                ),
                "assigned_ecu": ColumnSemantics(
                    business_name="ECU",
                    description="缺陷分配的ECU（电子控制单元）",
                    data_type="TEXT",
                    examples=["HU", "IC", "CMB"],
                    category="classification",
                    aliases=["ECU", "ecu", "控制单元"]
                ),
                "lead_model": ColumnSemantics(
                    business_name="主导车型",
                    description="缺陷关联的主要车型",
                    data_type="TEXT",
                    examples=["G70", "G60", "NA6"],
                    business_values={
                        "NA6": "新世代车型（Neue Klasse）",
                        "G70": "最新7系",
                        "G60": "最新5系",
                        "G20": "3系",
                        "G22": "4系",
                        "G26": "i4",
                        "G01": "X3",
                        "G02": "X4",
                        "G05": "X5"
                    },
                    category="classification",
                    aliases=["车型", "model", "vehicle_model"]
                ),
                "ecu_no_of_changes": ColumnSemantics(
                    business_name="ECU变更次数",
                    description="ECU转移次数（ping-pong）",
                    data_type="INTEGER",
                    category="calculated",
                    business_rules=[
                        "高转移次数表示责任不清或问题复杂"
                    ],
                    aliases=["ECU转移次数", "ecu_transfer_count"]
                ),

                # ========== 关系 ==========
                "parent_id": ColumnSemantics(
                    business_name="父缺陷ID",
                    description="父缺陷的ID（如果有）",
                    data_type="TEXT",
                    category="relation"
                ),
                "parent_child_type": ColumnSemantics(
                    business_name="父子类型",
                    description="父子缺陷关系类型",
                    data_type="TEXT",
                    category="relation"
                ),
                "relation_to": ColumnSemantics(
                    business_name="关联到",
                    description="关联的其他缺陷",
                    data_type="TEXT",
                    category="relation"
                ),

                # ========== 计算字段 ==========
                "test_week": ColumnSemantics(
                    business_name="测试周",
                    description="格式为YYYY-CWNN的测试周（计算字段）",
                    data_type="TEXT",
                    examples=["2025-CW11", "2025-CW12"],
                    calculation_rule="基于creation_time计算ISO周",
                    category="calculated",
                    aliases=["测试周", "周", "week"]
                ),
                "risk_score": ColumnSemantics(
                    business_name="风险分数",
                    description="计算的风险评分（0-100）",
                    data_type="REAL",
                    examples=["85.5", "42.0"],
                    calculation_rule="基于severity、matrix、age、is_topissue等计算",
                    business_rules=[
                        "80-100: 极高风险 🔴",
                        "60-80: 高风险 🟠",
                        "40-60: 中风险 🟡",
                        "0-40: 低风险 🟢"
                    ],
                    category="calculated",
                    aliases=["风险评分", "risk", "风险"]
                ),
                "defect_age_days": ColumnSemantics(
                    business_name="缺陷年龄",
                    description="缺陷存在的天数（计算字段）",
                    data_type="INTEGER",
                    examples=["5", "30", "45"],
                    calculation_rule="当前日期 - creation_time",
                    business_rules=[
                        ">30天: Long Runner（长期缺陷）",
                        ">60天: 需要特别关注"
                    ],
                    category="calculated",
                    aliases=["年龄", "age", "存在天数"]
                ),
                "is_long_runner": ColumnSemantics(
                    business_name="是否长期缺陷",
                    description="是否为长期未关闭的缺陷（计算字段）",
                    data_type="INTEGER",
                    examples=["0", "1"],
                    calculation_rule="defect_age_days > 30",
                    business_rules=[
                        "1: 是Long Runner，需要优先处理",
                        "0: 正常缺陷"
                    ],
                    category="calculated",
                    aliases=["长期缺陷", "long runner", "is_long_runner"]
                ),
                "is_topissue": ColumnSemantics(
                    business_name="是否TopIssue",
                    description="是否被标记为TopIssue（计算字段）",
                    data_type="INTEGER",
                    examples=["0", "1"],
                    business_rules=[
                        "1: 是TopIssue，必须优先汇报和处理",
                        "0: 普通缺陷"
                    ],
                    category="calculated",
                    aliases=["TopIssue", "topissue", "重点问题"]
                ),
                "matrix_display": ColumnSemantics(
                    business_name="Matrix矩阵位置",
                    description="严重性矩阵位置（计算字段）",
                    data_type="TEXT",
                    examples=["1A", "1B", "2C", "3A"],
                    calculation_rule="基于severity和impact范围计算",
                    business_values={
                        "1A": "最高严重性 - Critical级别 + 高影响范围，必须24小时内响应",
                        "1B": "高严重性 - Critical级别 + 中影响范围，必须24小时内响应",
                        "1C": "严重 - Major级别 + 高影响范围，本周内必须处理",
                        "1D": "严重 - Major级别 + 中影响范围，本周内必须处理",
                        "1E": "严重 - Major级别 + 低影响范围，本周内必须处理",
                        "2A": "中等 - Major级别 + 特定范围，按计划处理",
                        "2B": "中等 - Major级别 + 特定范围，按计划处理",
                        "2C": "中等 - Major级别 + 特定范围，按计划处理",
                        "3A/3B/3C": "轻微 - 低风险问题",
                        "4A/4B/4C/4D": "最低 - cosmetic或文档类问题"
                    },
                    category="calculated",
                    aliases=["Matrix", "matrix", "矩阵位置", "严重性矩阵"]
                ),
                "severity_group": ColumnSemantics(
                    business_name="严重级别分组",
                    description="严重级别的标准化分组（计算字段）",
                    data_type="TEXT",
                    examples=["Critical", "Major", "Minor"],
                    category="calculated"
                ),
                "parent_count": ColumnSemantics(
                    business_name="子缺陷数量",
                    description="作为父缺陷的子缺陷数量（计算字段）",
                    data_type="INTEGER",
                    business_rules=[
                        "高数量表示复杂缺陷"
                    ],
                    category="calculated"
                ),
                "child_count": ColumnSemantics(
                    business_name="父缺陷数量",
                    description="关联的父缺陷数量（计算字段）",
                    data_type="INTEGER",
                    category="calculated"
                ),
                "domain_transfer_count": ColumnSemantics(
                    business_name="Domain转移次数",
                    description="Domain转移次数（ping-pong）（计算字段）",
                    data_type="INTEGER",
                    business_rules=[
                        "高转移次数表示跨Domain协调问题"
                    ],
                    category="calculated",
                    aliases=["Domain转移", "domain_transfer_count"]
                ),
            },
            relationships=[
                {
                    "to_table": "octane_defect_histories",
                    "from_column": "defect_id",
                    "to_column": "defect_id",
                    "relationship": "一对多",
                    "description": "一个缺陷对应多条历史记录"
                }
            ],
            common_queries=[
                "按项目统计缺陷数量",
                "按AIDA统计缺陷分布",
                "查询高风险缺陷（risk_score > 80）",
                "查询长期未关闭缺陷（is_long_runner = 1）",
                "按周统计缺陷趋势",
                "查询TopIssue列表"
            ]
        )

    def _init_payloads_table(self):
        """初始化payloads表语义"""
        self.tables["octane_payloads"] = TableSemantics(
            business_name="原始数据存储表",
            description="存储从Octane API获取的原始数据",
            primary_key="(kind, team, year, spec)",
            columns={
                "kind": ColumnSemantics(
                    business_name="数据类型",
                    description="数据类型标识",
                    data_type="TEXT",
                    examples=["defects", "tests"],
                    category="basic"
                ),
                "team": ColumnSemantics(
                    business_name="团队",
                    description="数据所属团队",
                    data_type="TEXT",
                    category="classification"
                ),
                "year": ColumnSemantics(
                    business_name="年份",
                    description="数据年份",
                    data_type="INTEGER",
                    category="temporal"
                ),
                "spec": ColumnSemantics(
                    business_name="规格",
                    description="数据规格标识",
                    data_type="TEXT",
                    category="basic"
                ),
                "payload_json": ColumnSemantics(
                    business_name="JSON数据",
                    description="原始JSON格式数据",
                    data_type="TEXT",
                    category="basic"
                ),
                "fetched_at": ColumnSemantics(
                    business_name="获取时间",
                    description="数据获取时间",
                    data_type="DATETIME",
                    category="temporal"
                ),
            },
            relationships=[],
            common_queries=[]
        )

    def _init_histories_table(self):
        """初始化历史表语义"""
        self.tables["octane_defect_histories"] = TableSemantics(
            business_name="缺陷历史表",
            description="存储缺陷的历史变更记录",
            primary_key="defect_id",
            columns={
                "defect_id": ColumnSemantics(
                    business_name="缺陷ID",
                    description="缺陷唯一标识",
                    data_type="TEXT",
                    category="basic"
                ),
                "team": ColumnSemantics(
                    business_name="团队",
                    description="数据所属团队",
                    data_type="TEXT",
                    category="classification"
                ),
                "total_count": ColumnSemantics(
                    business_name="历史记录数",
                    description="该缺陷的历史记录总数",
                    data_type="INTEGER",
                    category="calculated"
                ),
                "payload_json": ColumnSemantics(
                    business_name="历史数据",
                    description="JSON格式的历史记录",
                    data_type="TEXT",
                    category="basic"
                ),
                "fetched_at": ColumnSemantics(
                    business_name="获取时间",
                    description="数据获取时间",
                    data_type="DATETIME",
                    category="temporal"
                ),
            },
            relationships=[
                {
                    "to_table": "octane_defects",
                    "from_column": "defect_id",
                    "to_column": "defect_id",
                    "relationship": "多对一",
                    "description": "多条历史记录对应一个缺陷"
                }
            ],
            common_queries=[
                "查询缺陷的历史变更",
                "统计缺陷的状态流转次数"
            ]
        )

    def get_table(self, table_name: str) -> Optional[TableSemantics]:
        """获取表语义定义"""
        return self.tables.get(table_name)

    def get_column(self, table_name: str, column_name: str) -> Optional[ColumnSemantics]:
        """获取字段语义定义"""
        table = self.tables.get(table_name)
        if table:
            return table.columns.get(column_name)
        return None

    def find_column_by_alias(self, table_name: str, alias: str) -> Optional[str]:
        """根据别名查找字段名"""
        table = self.tables.get(table_name)
        if not table:
            return None

        alias_lower = alias.lower()
        for col_name, col_sem in table.columns.items():
            if alias_lower == col_name.lower():
                return col_name
            if alias_lower in [a.lower() for a in col_sem.aliases]:
                return col_name
        return None

    def get_column_description(self, table_name: str, column_name: str) -> str:
        """获取字段业务描述"""
        col = self.get_column(table_name, column_name)
        if col:
            return f"{col.business_name}: {col.description}"
        return f"{column_name}: 未知字段"

    def get_business_values(self, table_name: str, column_name: str) -> Dict[str, str]:
        """获取字段的业务值映射"""
        col = self.get_column(table_name, column_name)
        if col:
            return col.business_values
        return {}

    def get_table_schema_context(self, table_name: str) -> str:
        """生成表的Schema上下文（用于Prompt）"""
        table = self.tables.get(table_name)
        if not table:
            return f"表 {table_name} 未定义"

        lines = [
            f"表名: {table_name} ({table.business_name})",
            f"描述: {table.description}",
            "",
            "字段定义:",
        ]

        for col_name, col in table.columns.items():
            line = f"  - {col_name} ({col.business_name}): {col.description}"
            if col.business_values:
                values_str = ", ".join([f"{k}={v}" for k, v in list(col.business_values.items())[:3]])
                if len(col.business_values) > 3:
                    values_str += f" 等{len(col.business_values)}个值"
                line += f" [{values_str}]"
            lines.append(line)

        if table.relationships:
            lines.extend(["", "关联关系:"])
            for rel in table.relationships:
                lines.append(f"  - {rel['from_column']} -> {rel['to_table']}.{rel['to_column']} ({rel['relationship']})")

        return "\n".join(lines)

    def get_all_columns_for_nl(self, table_name: str) -> Dict[str, List[str]]:
        """获取所有可用于自然语言理解的字段和别名"""
        table = self.tables.get(table_name)
        if not table:
            return {}

        result = {}
        for col_name, col in table.columns.items():
            all_names = [col_name, col.business_name] + col.aliases
            result[col_name] = list(set(all_names))
        return result


# 全局实例
_schema_catalog = None


def get_schema_catalog() -> SchemaCatalog:
    """获取Schema目录单例"""
    global _schema_catalog
    if _schema_catalog is None:
        _schema_catalog = SchemaCatalog()
    return _schema_catalog


# 便捷函数
def get_column_business_name(table_name: str, column_name: str) -> str:
    """获取字段业务名称"""
    catalog = get_schema_catalog()
    col = catalog.get_column(table_name, column_name)
    return col.business_name if col else column_name


def resolve_column_alias(table_name: str, alias: str) -> Optional[str]:
    """解析字段别名"""
    catalog = get_schema_catalog()
    return catalog.find_column_by_alias(table_name, alias)


if __name__ == "__main__":
    # 测试
    catalog = get_schema_catalog()

    print("=" * 60)
    print("Schema业务语义目录测试")
    print("=" * 60)

    # 测试1: 获取表定义
    print("\n1. 缺陷表定义:")
    print(catalog.get_table_schema_context("octane_defects")[:1000])

    # 测试2: 查找字段别名
    print("\n2. 别名查找测试:")
    aliases_to_test = ["创建时间", "项目", "AIDA", "风险", "长期缺陷"]
    for alias in aliases_to_test:
        col = catalog.find_column_by_alias("octane_defects", alias)
        print(f"  '{alias}' -> {col}")

    # 测试3: 获取业务值
    print("\n3. 业务值映射:")
    print(f"  severity: {catalog.get_business_values('octane_defects', 'severity')}")
    print(f"  program: {catalog.get_business_values('octane_defects', 'program')}")

    print("\n✅ 测试完成!")
