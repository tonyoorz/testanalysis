# DATABASE_KNOWLEDGE.md — AI Agent 数据库深度认知文档

> 本文档是 AI Agent 理解业务数据库的完整知识源。
> 数据库: `database/local_data.db` (SQLite, ~5.4GB)
> 数据时间范围: 2024-01 ~ 2026-03
> 最后更新: 2026-04-16

---

## 一、业务背景

这是一个**汽车软件质量管理系统**，服务于 BMW 车载信息娱乐与通信系统（IuK / Infotainment und Kommunikation）的缺陷跟踪和测试管理。数据从 Micro Focus Octane（ALM 平台）同步到本地 SQLite 数据库进行深度分析、可视化和报表生成。

### 核心业务概念

| 概念 | 说明 |
|------|------|
| **Octane** | Micro Focus 的应用生命周期管理平台，是缺陷和测试数据的源头 |
| **Defect（缺陷）** | 在测试中发现的软件问题，记录在 Octane 中 |
| **Manual Run（手工测试执行）** | 测试人员按照测试用例手工执行的测试记录 |
| **AIDA** | Automotive Integrated Development Architecture — 汽车功能的层级分类体系，格式如 `01.04.02.01.01.02`，用于标识汽车软件功能域 |
| **top_aida** | AIDA 树中最细粒度的功能节点（测试团队定义的验证基石），是业务分析的核心维度 |
| **FV（Function Variant）** | 功能变体/功能团队，标识负责该功能的开发团队（如 IuK_TSP_HMI、IuK_TSP_Navi） |
| **Lead Model（引领车型）** | 软硬件 cluster 最先应用/落地的标准车型（如 NA6、G70、U12） |
| **ECU** | Electronic Control Unit — 电子控制单元，车载硬件模块（如 HU-MGU_02_A、IDCEVO-25） |
| **I-Step** | 研发里程碑周期（如 G070-26-07-460 表示 G70 车型、26年、07月SOP的版本） |
| **Spec / Release** | 软件发布规范（如 R-25-06），按年份+周号标识发布批次 |
| **Showstopper** | 阻断性问题，必须优先解决否则影响发布 |
| **PMG** | Preventing Maturity Grade — 阻碍成熟度评级的缺陷 |
| **Top Issue** | 经风险评分算法筛选出的高风险缺陷 |
| **Risk Score** | 综合评分（0~约210），考虑 matrix 严重度、classification、ECU/Domain 转移、父子复杂度、处理周期等维度 |
| **Matrix** | 严重性矩阵标签（Matrix-1A ~ Matrix-3A），用于标识缺陷严重程度分层 |
| **TQR** | Ticket Quality Rating — 缺陷质量评分（描述是否完整、可复现等） |
| **CW（Calendar Week）** | 测试周编号，一年 CW01~CW52 |
| **Taxonomy（测试平台分类）** | 测试执行平台类型（dWKP=动态子系统、dGS=动态系统、sWKP=静态子系统等） |
| **SOP** | Start of Production — 量产开始时间点 |
| **PU** | Product Use / first_use_sop_of_function — 功能首次使用SOP的时间窗口（如 25-07、26-07） |

### 组织架构

- **DTSV_China** — 核心测试团队（占数据量 94%），下设多个子团队：
  - `IuK_TSP_HMI` — 人机交互界面
  - `IuK_TSP_Navi` — 导航
  - `IuK_TSP_Entertainment` — 娱乐
  - `IuK_TSP_Connectivity` — 连接/蓝牙
  - `IuK_TSP_Audio` — 音频
  - `DIPS_TSP_Car_Apps_CN` — 手机应用（中国）
  - `DIPS_TSP_CD_Updates` — CD/软件更新
  - `DIPS_TSP_Call_Services` — 通话服务
  - 其他...
- **IuK_TSP_xxx** 子团队既是 team 字段值，也映射到 FV 字段
- **Problem Finder Teams** — 缺陷发现团队（DTSV_China、[AT]FIT_LAENDER_CHINA 等）

### 车型与硬件

| 分类 | 主要值 | 说明 |
|------|--------|------|
| Lead Model | NA6(3420), G70(3265), U12(2217), G68(2099), NA5, G48, U11, J01 | 引领车型 |
| ECU | HU-MGU_02_A(5927), IDCEVO-25(5502), HU-MGU_02_L(1226) | 主力硬件平台 |
| App | APP_Mobile_2_0_IOS_CN(450), APP_Mobile_2_0_Android_CN(280) | 移动端 |

---

## 二、表级详解

### 1. octane_defects — 缺陷主表（16,178 条）

> **核心业务表**。每一行是一个 Octane 缺陷（work item）。
> 时间范围: 2024-01-02 ~ 2026-03-03
> 主键: `defect_id`

| 列名 | 类型 | 业务含义 | 典型值 / 分布 |
|------|------|----------|--------------|
| `defect_id` | TEXT PK | Octane 缺陷唯一 ID | 如 "1702573"、"2157632" |
| `name` | TEXT | 缺陷标题/描述 | 如 "[U12][IDC 2403]BT automatically turned off after switching from Carplay to BT" |
| `creation_time` | TEXT | 缺陷创建时间（UTC ISO格式） | "2024-01-02T02:39:17Z" |
| `last_modified` | TEXT | 最后修改时间 | "2024-07-13T09:59:01Z" |
| `team` | TEXT | 所属测试团队 | DTSV_China(15253), IuK_TSP_Navi(77), IuK_TSP_Entertainment(51)... |
| `problem_finder_team` | TEXT | 发现缺陷的团队 | DTSV_China(15989), [AT]FIT_LAENDER_CHINA(67), [AT]W72-FIT(46)... |
| `program` | TEXT | 项目/产品线 | IuK(7928), EE_MAIN(713), AF(82), EA(15), EF(7)，空值约7433条 |
| `author` | TEXT | 缺陷创建者 | 人名，如 "Weining Zhao"(938), "Jingpu Li"(907)... |
| `aida_businesskey` | TEXT | Octane 原始 AIDA 编号 | 如 "UR-0004782" |
| `aida_english` | TEXT | 提取的英文 AIDA 名称（去掉编号后的功能英文名） | 如 "Voice Interface"、"CarPlay" |
| `top_aida` | TEXT | 顶层 AIDA 功能分类（含编号） | 如 "Voice Interface [01.04.02.01.01.02]"(1623)、"Provide Navigation 2.0 [01.04.03.01.03.06]"(1011) |
| `product_areas` | TEXT | Octane 原始 AIDA 多值字段 | 与 top_aida 类似，但一个缺陷可能有多个 |
| `user_tags` | TEXT | 标签集合（逗号分隔） | 如 "IuK_TSP_FIFChecked,IuK_Cluster_23,Matrix-3A" |
| `phase` | TEXT | 缺陷生命周期阶段 | "09-Concluded without action"(9684), "06-Concluded"(5108), "04-In Progress"(776), "01-New"(163)... |
| `severity` | TEXT | 缺陷严重度 | Medium(10323), Low(5480), High(362), Critical(4), Very High(2) |
| `problem_severity` | TEXT | 问题严重度（另一个严重度口径） | 05-unsatisfactory(10302), 06-customer irritated(5196), 04-deficient(376)... |
| `status_phase` | TEXT | 组合状态（phase + severity） | 如 "09-Concluded without action_Medium" |
| `owner` | TEXT | 缺陷负责人/当前处理人 | 人名，如 "Yuan Wang"(1266), "Xiaying Cao"(773)... |
| `detected_by` | TEXT | 缺陷发现人/测试人员 | 人名，如 "Weining Zhao"(952), "Jingpu Li"(915)... |
| `detected_in_release` | TEXT | 发现时的 Release 版本 | 如 "R-24-12"(1241), "R-25-12"(999), "R-25-06"(906)... |
| `software_version` | TEXT | 被测软件版本 | 如 "pu2403-23w50.2-3" |
| `vin` | TEXT | 车辆识别号（测试车辆 VIN） | 如 "WBA61EE0005W65834" |
| `assigned_ecu` | TEXT | 关联的车载 ECU | HU-MGU_02_A(5927), IDCEVO-25(5502), HU-MGU_02_L(1226)... |
| `lead_model` | TEXT | 引领车型 | NA6(3420), G70(3265), U12(2217), G68(2099)... |
| `ecu_no_of_changes` | INT | ECU 变更次数 | 0(13402), 1(1848), 2(551), 3(205), 4(83) |
| `parent_id` | TEXT | 父缺陷 ID（Master 票） | 通常为 "2001"（Backlog 根节点）或其他缺陷 ID |
| `parent_child_type` | TEXT | 父子关系类型 | 空=独立票(10991), Child(4228), Parent(954), Child (Candidate)(5) |
| `relation_to` | TEXT | 关联的其他缺陷 ID（逗号分隔） | 缺陷 ID 列表，表示跨票关联 |
| `test_week` | TEXT | 计算的测试周（如 "2024-CW01"） | 格式 "YYYY-CWxx" |
| `risk_score` | REAL | 计算的风险分数 | 范围约 0~209，分数越高风险越大 |
| `fv` | TEXT | Function Variant / 功能团队 | IuK_TSP_HMI(4004), IuK_TSP_Navi(3029), DIPS_TSP_Car_Apps_CN(1675)... |
| `fvp` | TEXT | FV + Project 组合标识 | 人名（如 "Jerry"(4386), "Tony"(3029), "Xu Miao"(2371)）——实际映射为 FV 负责人 |
| `tqr` | TEXT | 缺陷质量评分（JSON 格式） | 如 `{"total_count": 1, "data": [{"name": "01-well created defect"}]}` |
| `blocking_reason` | TEXT | 阻塞原因 | Child (Duplicate)(3969), Expected behaviour(1588), Management decision(988), Not reproducible(970)... |
| `error_occurrence` | TEXT | 错误复现频率 | 04-reproducable(8069), 02-sporadic(4023), 01-single event(1936), 03-highly intermittend(1261) |
| `solution_responsible` | TEXT | 解决方案责任方 | bmw(15484), cc_jira(628), bmw_ATC-Jira(38), navis(14), HARMAN_IDCEVO(5) |
| `solution_cluster` | TEXT | 解决方案集群/开发团队 | Speech CN(1929), Navigation CN(1921), ENT_and_CON CN(1024), Entertainment(869)... |
| `reporting_class` | TEXT | 报告分类标签 | Showstopper_Candidate(60), Homologation L-labelled(15)... |
| `function_responsible` | TEXT | 功能负责人（通常为空） | 极少填充 |
| `involved_i_step` | TEXT | 涉及的 I-Step（研发里程碑） | 如 "G070-26-07-460"(573), "NA06-26-07-460"(519)... |
| `first_use_sop_of_function` | TEXT | 功能首次使用的 SOP 时间窗口 | "25-07"(3270), "26-07"(3240), "24-07"(2148), "26-03"(1622)... |
| `tolerated_count` | INT | 容忍次数（允许出现的次数） | 0(大多数), 1(996), 2(70), 3(10) |
| `reprel_changes` | TEXT | 代表性变更次数 | "1"(10871), "0"(2288), "2"(879)... |
| `is_showstopper` | INT | 是否为 Showstopper（0/1） | 76 个缺陷标记为 Showstopper |
| `is_pmg` | INT | 是否为 PMG 缺陷（0/1） | 3 个缺陷标记为 PMG |
| `is_top_issue` | INT | 是否为 Top Issue（0/1） | 1 个缺陷标记为 Top Issue |
| `raw_json` | TEXT | Octane 原始完整 JSON 数据 | 保留所有未解析字段，用于深度查询 |
| `year` | INT | 缺陷所属年份 | 2024(6723), 2025(8280), 2026(1175) |
| `fetched_at` | TEXT | 数据抓取时间 | 如 "2026-03-05T11:13:..." |

**关键业务规则**：
- `phase` 编号规则：00-Draft → 01-New → 02-In Pre-Analysis → 03-In Analysis → 04-In Progress → 05-In Testing → 06-Concluded → 07-In Pre-Verification → 08-In Verification → 09-Concluded without action
- `severity` 和 `problem_severity` 是两套严重度体系：severity 用于通用分级，problem_severity 更偏向用户影响角度
- `blocking_reason` 为 "Child (Duplicate)" 表示子票重复，"Expected behaviour" 表示预期行为（非真正缺陷）
- `top_aida` 格式为 "英文名 [AIDA编号]"，分析时通常按此维度聚合
- `fv` 与 `team` 有映射关系但不完全相同：fv 侧重功能责任，team 侧重组织归属
- `fvp` 虽然字段名暗示 FV+Project，实际存储的是 FV 负责人姓名

---

### 2. octane_manual_runs — 手工测试执行表（67,787 条）

> 每一行是一次手工测试执行记录。
> 时间范围: 2024-01-22 ~ 2026-03-03
> 主键: `mr_id`

| 列名 | 类型 | 业务含义 | 典型值 / 分布 |
|------|------|----------|--------------|
| `mr_id` | TEXT PK | 测试执行记录唯一 ID | 如 "9613927" |
| `name` | TEXT | 测试执行名称（含平台/配置信息） | 如 "[DTSV_China]_IDCEVO-25 & ICON-25 & CID_MID-25_[CN]" |
| `test_name` | TEXT | 测试用例名称 | 如 "[TOUCH BK25, CID_MID-25]_Single finger Drag and Drop" |
| `test_id` | TEXT | 关联的测试用例 ID | 如 "1221307" |
| `creation_time` | TEXT | 记录创建时间 | ISO 格式 |
| `last_modified` | TEXT | 最后修改时间 | ISO 格式 |
| `started` | TEXT | 测试开始执行时间 | ISO 格式 |
| `finished` | TEXT | 测试完成时间 | ISO 格式 |
| `defect_id` | TEXT | 关联的缺陷 ID（全部为空） | 当前所有记录均无关联缺陷 |
| `run_team` | TEXT | 执行团队 | 全部为 "DTSV_China" |
| `program` | TEXT | 项目 | IuK(67230), EE_MAIN(557) |
| `author` | TEXT | 测试用例作者 | 人名 |
| `run_by` | TEXT | 测试执行人 | 人名（如 "Qxz2fs8_delete"） |
| `status` | TEXT | 测试结果状态（标准化） | Passed(58019), Requires Attention(6085), Failed(2785), Planned(898) |
| `native_status` | TEXT | Octane 原始状态 | Passed(58019), Blocked(6061), Failed(2785), Planned(898), In Progress(24) |
| `is_completed` | INT | 是否已完成（0/1） | 1(66865), 0(922) |
| `steps_num` | INT | 测试步骤数 | 1~20+，以 3~12 居多 |
| `version_stamp` | TEXT | 版本戳 | |
| `release` | TEXT | 所属 Release | 如 "R-24-01" |
| `exec_model_series` | TEXT | 执行车型系列 | G70(13250), NA6(12233), G68(9682), U12(6543)... |
| `execution_sw_version` | TEXT | 执行使用的软件版本 | 如 "[I&K25_26-07_480_25w51] I&K25 Cluster ATS-4"(886) |
| `test_version` | TEXT | 测试用例版本 | "0.2.0"(25882), "0.3.0"(13453), "0.4.0"(7774)... |
| `product_areas` | TEXT | AIDA 产品域 | |
| `domain` | TEXT | 测试域 | IuK_IuA(67760), IuK_CoC(15), EA_Antrieb_IuA(12) |
| `test_phase` | TEXT | 测试阶段 | Ready(67354), For Review(355), New / In Design(42), Review Error(30) |
| `testing_tool_type` | TEXT | 测试工具类型 | 全部为 "Manual Runner" |
| `taxonomies` | TEXT | 测试平台分类（逗号分隔，可多值） | dWKP(37975), dWKP+sWKP(15861), dGS(5184)... |
| `set_field` | TEXT | I-Step / 发布周期标识 | "26-03"(15339), "26-07"(12124), "25-07"(10629)... |
| `target_ecu_conf` | TEXT | 目标 ECU 配置 | "IDCEVO-25 and ICON-25"(20480), "HU-MGU_02_A and WAVE-01"(9102)... |
| `testplatformid` | TEXT | 测试平台 ID（通常是测试车辆 VIN） | VIN 码列表 |
| `raw_json` | TEXT | Octane 原始 JSON | 完整记录 |
| `year` | INT | 所属年份 | 2024(29749), 2025(33115), 2026(4923) |
| `spec` | TEXT | Release 规范 | 如 "R-24-01", "R-25-06", "R-26-01" |
| `fetched_at` | TEXT | 数据抓取时间 | |

**关键业务规则**：
- `status` vs `native_status`：status 是标准化映射，native_status 是 Octane 原始值。"Requires Attention" 对应 native "Blocked"
- **通过率**: 总体 85.6%（Passed / (Passed+Failed+Requires Attention)）
- `defect_id` 字段当前全为空，测试与缺陷的关联需要通过其他方式（如 AIDA、时间窗口、车型等）推断
- `spec` 和 `release` 相同含义，都是 Release 版本标识（如 R-25-06）
- `set_field` 表示 I-Step 周期，格式为 "YY-MM"（如 "26-07" 表示 2026 年 7 月 SOP）
- `taxonomies` 的平台分类含义：
  - `d`=dynamic（动态/实车）, `s`=static（静态/台架）, `v`=virtual（虚拟）
  - `GS`=系统测试, `WKP`=子系统测试, `KP`=组件测试
  - 如 dWKP = 实车动态子系统测试平台

---

### 3. octane_defect_histories — 缺陷历史变更记录（13,592 条）

> 每一行是一个缺陷的所有历史变更事件的打包记录（JSON）。
> 主键: `defect_id` + `team`

| 列名 | 类型 | 业务含义 | 典型值 |
|------|------|----------|--------|
| `defect_id` | TEXT PK | 关联的缺陷 ID | 如 "2111678" |
| `team` | TEXT | 所属团队（全部为 "DTSV_China"） | "DTSV_China" |
| `total_count` | INT | 该缺陷的变更事件总数 | 如 114, 147, 107 |
| `payload_json` | TEXT | 所有变更事件的 JSON 数组 | 包含 total_count 个事件对象 |
| `fetched_at` | TEXT | 数据抓取时间 | ISO 格式 |

**payload_json 内部结构**（单个事件对象）:
```json
{
  "type": "history_log",
  "id": "1103628919",
  "user_name": "qqTCQ",
  "timestamp": "2025-03-07T10:45:14.063Z",
  "action": "update",
  "entity_type": "defect",
  "entity_id": "2111678",
  // ...更多字段如 field_name, old_value, new_value 等
}
```

**用途**: 用于分析缺陷状态流转（inflow/outflow）、处理周期（long runner）、ECU/Team 转派（ping-pong）等。

---

### 4. octane_history_events — 缺陷历史事件明细表（0 条）

> 预留的历史事件明细表，当前为空。设计用于将 payload_json 中的事件展开为独立行。

| 列名 | 类型 | 业务含义 |
|------|------|----------|
| `event_id` | INT PK AUTO | 事件自增 ID |
| `defect_id` | TEXT FK | 关联缺陷 ID（外键 → octane_defects） |
| `timestamp` | TEXT | 事件时间 |
| `event_type` | TEXT | 事件类型（field_change, status_change, comment, attachment 等） |
| `field_name` | TEXT | 变更的字段名 |
| `old_value` | TEXT | 变更前值 |
| `new_value` | TEXT | 变更后值 |
| `user_name` | TEXT | 操作人用户名 |
| `user_email` | TEXT | 操作人邮箱 |
| `user_full_name` | TEXT | 操作人全名 |
| `description` | TEXT | 事件描述 |
| `comment` | TEXT | 评论内容 |
| `raw_json` | TEXT | 原始 JSON |
| `created_at` | TEXT | 记录创建时间 |

---

### 5. defect_features — 缺陷风险特征表（16,178 条）

> 每行对应一个缺陷的风险评分结果，与 octane_defects 一一对应。
> 主键: `defect_id`

| 列名 | 类型 | 业务含义 | 典型值 |
|------|------|----------|--------|
| `defect_id` | TEXT PK | 缺陷 ID | 与 octane_defects.defect_id 关联 |
| `topissue_risk_score` | REAL | TopIssue 风险评分（0~约210） | 如 50.5, 81.5, 95.0, 208.9 |
| `topissue_display` | TEXT | 显示用评分（四舍五入整数） | 如 "50", "82", "95", "209" |
| `topissue_recommend_reason` | TEXT | 推荐为 Top Issue 的理由说明 | |
| `is_topissue` | INT | 是否被标记为 Top Issue（0/1） | 1=极少数高风险缺陷 |
| `is_master_score` | INT | 是否为 Master 票评分（0/1） | |
| `source_fetched_at` | TEXT | 源数据获取时间 | |
| `computed_at` | TEXT | 评分计算时间 | |
| `feature_version` | TEXT | 评分算法版本 | "topissue_v1" |

**风险评分算法维度**（参考 `data_processor.calculate_topissue_risk_score`）：
1. Matrix 严重度（Matrix-1A ~ Matrix-3A 权重不同）
2. Classification（Showstopper_Candidate 等）
3. ECU 转移次数（ecu_pingpong_count）
4. Domain 转移次数（domain_pingpong_count）
5. 父子复杂度（parent_child + child_count）
6. 处理周期天数（processing_days）
7. 是否推迟 PU/SOP（shift_pu_status）
8. 非线性组合计算最终分数

---

### 6. octane_payloads — Octane 原始数据载荷（32 条）

> 存储从 Octane API 获取的原始 JSON 响应数据，按 kind/team/year/spec 分组。
> 主键: (`kind`, `team`, `year`, `spec`)

| 列名 | 类型 | 业务含义 | 典型值 |
|------|------|----------|--------|
| `kind` | TEXT PK | 数据类型 | "defects"(3), "manual_runs"(29) |
| `team` | TEXT PK | 团队 | "DTSV_China" |
| `year` | INT PK | 年份 | 2024, 2025, 2026 |
| `spec` | TEXT PK | Release 规范 | 缺陷类为空，测试类如 "R-25-01" |
| `payload_json` | TEXT | 原始 JSON（可能很大，数 MB） | 大型 JSON 数组 |
| `fetched_at` | TEXT | 数据抓取时间 | ISO 格式 |

**用途**: 作为数据回溯和重新处理的备份。defects 有 3 条（按年），manual_runs 有 29 条（按年+spec）。

---

### 7. defect_stats_daily — 每日缺陷统计聚合（3,260 条）

> 按日期+项目+团队+严重度聚合的每日缺陷统计快照。

| 列名 | 类型 | 业务含义 | 典型值 |
|------|------|----------|--------|
| `date` | TEXT | 统计日期 | "2024-01-02" |
| `program` | TEXT | 项目 | "IuK" 或空 |
| `team` | TEXT | 团队 | "DTSV_China", "IuK_TSP_HMI", "IuK_TSP_Navi"... |
| `severity` | TEXT | 严重度 | "Medium", "Low", "High"... |
| `defect_count` | INT | 当日缺陷数 | |
| `showstopper_count` | INT | 当日 Showstopper 数 | |
| `pmg_count` | INT | 当日 PMG 数 | |

**用途**: 快速生成趋势图，避免每次都扫描全量缺陷表。

---

### 8. test_stats_daily — 每日测试统计聚合（716 条）

> 按日期+项目+状态聚合的每日测试执行统计。

| 列名 | 类型 | 业务含义 | 典型值 |
|------|------|----------|--------|
| `date` | TEXT | 统计日期 | "2024-01-18" |
| `program` | TEXT | 项目 | "IuK" |
| `status` | TEXT | 测试状态 | "Passed", "Failed", "Requires Attention", "Planned" |
| `test_count` | INT | 当日测试数 | |

---

### 9. project_summary — 项目汇总表（5 条）

> 按项目汇总的 KPI 快照。

| 列名 | 类型 | 业务含义 | 值分布 |
|------|------|----------|--------|
| `project` | TEXT | 项目名 | IuK, EE_MAIN, AF, EA, EF |
| `total_defects` | INT | 总缺陷数 | IuK: 7928, EE_MAIN: 713 |
| `showstoppers` | INT | Showstopper 数 | IuK: 47, EE_MAIN: 5 |
| `pmg` | INT | PMG 数 | IuK: 2 |
| `total_tests` | INT | 总测试数 | IuK: 67230, EE_MAIN: 557 |
| `passed_tests` | INT | 通过数 | IuK: 57763, EE_MAIN: 256 |
| `pass_rate` | REAL | 通过率 | IuK: 0.859 (85.9%), EE_MAIN: 0.46 (46%) |
| `defect_density` | REAL | 缺陷密度 | IuK: 0.118, EE_MAIN: 1.28 |

---

### 10. aida_mappings — AIDA 映射表（0 条，空表）

> 预留表，设计用于存储 AIDA 编号到功能名称的映射关系。

| 列名 | 类型 | 业务含义 |
|------|------|----------|
| `aida_id` | TEXT PK | AIDA 唯一 ID |
| `aida_name` | TEXT | AIDA 名称 |
| `aida_english` | TEXT | AIDA 英文名 |
| `top_aida` | TEXT | 顶层 AIDA |
| `project` | TEXT | 所属项目 |
| `fv` | TEXT | Function Variant |
| `category` | TEXT | 分类 |
| `test_case_id` | TEXT | 关联测试用例 ID |
| `test_case_name` | TEXT | 关联测试用例名称 |
| `created_at` | TEXT | 创建时间 |

---

### 11. semantic_catalog — 语义目录表（4 条）

> 存储系统用到的各种元数据目录（JSON 格式）。

| 列名 | 类型 | 业务含义 |
|------|------|----------|
| `catalog_type` | TEXT PK | 目录类型：charts, datasets, metrics, sql_templates |
| `catalog_json` | TEXT | 目录内容（JSON） |
| `updated_at` | TEXT | 更新时间 |

---

## 三、表间关系

```
octane_defects (核心缺陷表)
    ├── 1:1 ── defect_features (风险评分，通过 defect_id 关联)
    ├── 1:1 ── octane_defect_histories (变更历史，通过 defect_id 关联)
    │              └── payload_json 内含 N 个 history events
    ├── 预留 1:N ── octane_history_events (事件明细，通过 defect_id FK 关联，当前为空)
    └── 自关联: parent_id → defect_id (父子缺陷关系)

octane_manual_runs (测试执行表)
    ├── 预留关联: defect_id → octane_defects (当前全为空)
    └── 与缺陷的间接关联: 通过 AIDA/车型/时间窗口等维度匹配

octane_payloads (原始数据备份)
    └── kind="defects" → 对应 octane_defects 的源数据
    └── kind="manual_runs" → 对应 octane_manual_runs 的源数据

defect_stats_daily ← 聚合自 octane_defects
test_stats_daily ← 聚合自 octane_manual_runs
project_summary ← 聚合自 octane_defects + octane_manual_runs

semantic_catalog → 独立元数据，定义图表/数据集/指标/SQL模板
```

---

## 四、常用查询模式

### 4.1 缺陷趋势分析
```sql
-- 按月缺陷创建趋势
SELECT strftime('%Y-%m', creation_time) as month, COUNT(*)
FROM octane_defects GROUP BY month ORDER BY month;
```

### 4.2 通过率分析
```sql
-- 按 spec 的测试通过率
SELECT spec,
  COUNT(*) as total,
  SUM(CASE WHEN status='Passed' THEN 1 ELSE 0 END) as passed,
  ROUND(100.0 * SUM(CASE WHEN status='Passed' THEN 1 ELSE 0 END) / COUNT(*), 1) as pass_rate
FROM octane_manual_runs
WHERE spec IS NOT NULL
GROUP BY spec ORDER BY spec;
```

### 4.3 高风险缺陷筛选
```sql
-- Top Issue 级别的缺陷
SELECT d.defect_id, d.name, d.severity, d.top_aida, f.topissue_risk_score
FROM octane_defects d
JOIN defect_features f ON d.defect_id = f.defect_id
WHERE f.is_topissue = 1
ORDER BY f.topissue_risk_score DESC;
```

### 4.4 AIDA 维度分析
```sql
-- 按 top_aida 统计缺陷分布
SELECT top_aida, COUNT(*) as cnt,
  SUM(CASE WHEN is_showstopper=1 THEN 1 ELSE 0 END) as showstoppers
FROM octane_defects
WHERE top_aida IS NOT NULL
GROUP BY top_aida ORDER BY cnt DESC LIMIT 20;
```

### 4.5 跨维度关联（缺陷+测试）
```sql
-- 缺陷和测试无法直接 JOIN（defect_id 在 manual_runs 中为空）
-- 需要通过共同维度间接关联：AIDA、车型（lead_model/exec_model_series）、
-- 时间窗口、ECU 配置等
```

---

## 五、数据质量注意事项

1. **program 字段空值率高**: 约 46% 的缺陷 program 为空，这些大多属于 IuK 项目（可通过 team 和其他字段推断）
2. **defect_id 在 manual_runs 中全为空**: 测试与缺陷无法直接关联，需通过共同维度间接分析
3. **severity 和 problem_severity 是两套体系**: 分析时需明确使用哪一套
4. **blocking_reason 中 "Child (Duplicate)" 占比最高**: 这些通常是预期关闭的子票
5. **2026 年数据不完整**: 截至 2026-03-03，Q1 数据仍在积累中
6. **tqr 字段为 JSON 格式**: 需要解析才能获取实际质量评分
7. **history_events 表为空**: 历史事件仍在 payload_json 中，未展开存储
8. **aida_mappings 表为空**: AIDA 映射关系存储在代码/Excel 中而非数据库

---

## 六、业务指标定义

| 指标 | 计算公式 | 数据源 |
|------|----------|--------|
| 测试通过率 | Passed / (Passed + Failed + Requires Attention) × 100 | octane_manual_runs |
| 缺陷密度 | 总缺陷数 / 总测试数 | project_summary |
| 严重缺陷率 | severity_group='Critical Issues' 的缺陷数 / 总缺陷数 × 100 | octane_defects (需计算 matrix+classification) |
| Showstopper 数量 | is_showstopper = 1 的缺陷数 | octane_defects |
| Top Issue 风险评分 | 综合算法（见 defect_features 表说明） | defect_features |
| 月均新增缺陷 | 按月 GROUP BY creation_time 后取均值 | octane_defects |
| 处理周期 | 从 creation_time 到状态迁移到 resolved 的时间 | octane_defect_histories |
