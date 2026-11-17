# 2024 vs 2025 KPI Analysis Report（Custom）

## A. 测试类指标（Testing Cluster）

### A1. 核心指标概览

| 指标 | 2024 | 2025 | 变化 |
|---|---:|---:|---:|
| 执行总量 | 29,749 | 33,115 | +3,366（+11.3%） |
| Pass率 | 24,991（84.01%） | 29,513（89.12%） | +5.11pp |
| Failed率 | 1,234（4.15%） | 1,363（4.12%） | -0.03pp |
| Blocked率（Requires Attention） | 3,524（11.85%） | 2,239（6.76%） | -5.09pp |
| 关联缺陷数 | 0（0.00%，占总缺陷0.00%） | 0（0.00%，占总缺陷0.00%） | - |

### A2. 覆盖矩阵（项目 × 车型 × 配置）

口径说明：
- 仅保留项目：`IDCEVO / IDC / MGU / App`；
- 以 `target_ecu_conf` 作为“配置”列；
- 已去除 Unknown 项。

| 项目 | 车型 | 配置 | 2024 | 2025 |
|---|---|---|---:|---:|
| IDCEVO | NA6 | IDCEVO-25 and ICON-25 | 3,270 | 7,357 |
| IDCEVO | G70 | IDCEVO-25 and ICON-25 | 134 | 5,192 |
| IDCEVO | NA5 | IDCEVO-25 and ICON-25 | 28 | 2,132 |
| IDCEVO | NA6 | ICON-25 and IDCEVO-25 | 31 | 84 |
| IDC | G68 | HU-MGU_02_A and WAVE-01 | 4 | 2,910 |
| IDC | U12 | HU-MGU_02_A and WAVE-01 | 163 | 1,156 |
| IDC | U12 | HU-MGU_02_A | 666 | 280 |
| IDC | J01 | HU-MGU_02_A and WAVE-01 | 0 | 815 |
| MGU | G70 | HU-MGU_02_L and WAVE-01 | 366 | 2,372 |
| MGU | G68 | HU-MGU_02_L and WAVE-01 | 241 | 685 |
| MGU | G28 | HU-MGU_02_L and WAVE-01 | 55 | 454 |
| MGU | G70 | HU-MGU_02_L | 209 | 198 |
| App | U12 | My BMW v5.7.0 CN | 0 | 208 |
| App | U12 | My BMW v5.11.0 CN | 0 | 185 |
| App | NA6 | My BMW v5.11.0 CN | 0 | 162 |
| App | U12 | My BMW v5.9.0 CN | 0 | 161 |

### A3. 覆盖评估输出（周维度 Release 成功/失败率）

替换原“覆盖评估”输出为周维度结果，口径与 defect_explore6 类似（柱状：成功/失败/Blocked；折线：成功率）：

| 年份 | 周别 | Passed | Failed | Blocked | 成功率 |
|---|---|---:|---:|---:|---:|
| 2024 | W01 | 478 | 17 | 11 | 94.47% |
| 2024 | W02 | 365 | 7 | 4 | 97.07% |
| 2024 | W03 | 327 | 66 | 17 | 79.76% |
| 2024 | W04 | 479 | 37 | 111 | 76.40% |
| 2025 | W01 | 512 | 31 | 24 | 90.30% |
| 2025 | W02 | 571 | 25 | 41 | 89.64% |
| 2025 | W03 | 548 | 22 | 37 | 90.28% |
| 2025 | W04 | 603 | 19 | 40 | 91.09% |

## B. 缺陷类指标（Defect Cluster）

### B1. 核心缺陷指标概览（重症口径）

| 指标 | 2024 | 2025 | 变化 |
|---|---:|---:|---:|
| 缺陷总量 | 6,708 | 8,280 | +1,572（+23.4%） |
| Showstopper Confirmed | 641（9.56%） | 711（8.59%） | +70（-0.97pp） |
| Preventing Maturity Grade | 298（4.44%） | 218（2.63%） | -80（-1.81pp） |
| Showstopper Candidate | 2,374（35.39%） | 3,007（36.33%） | +633（+0.94pp） |
| Homologation | 274（4.08%） | 690（8.34%） | +416（+4.26pp） |

### B2. CWA 聚类分析（替换空值质量统计）

聚类方式：仅统计 `Phase 09`，按 `blocking_reason` 分成三类：
- Green（Positive CWA）
- Yellow（有问题但可接受）
- Red（不可接受）

| 年份 | Green | Yellow | Red |
|---|---:|---:|---:|
| 2024 | 3,012（71.39%） | 939（22.26%） | 268（6.35%） |
| 2025 | 3,631（70.40%） | 1,268（24.58%） | 259（5.02%） |

2025 CWA 亮点结论：
- **Red CWA 仅 5.02%**，不可接受项占比保持低位；
- **Function not implemented/testable yet = 112 条（占 CWA 2.17%）**，可视为新功能开发阶段的正向信号；
- Green 占比约 **70.4%**，整体 CWA 结构仍以可接受闭环为主。

2025 Phase09 Top Blocking Reasons：
| Blocking Reason | Count |
|---|---:|
| Child (Duplicate) | 2,356 |
| Expected behaviour | 745 |
| Not reproducible | 568 |
| Management decision | 418 |
| Additional Information necessary | 376 |
| Further traces necessary | 206 |
| Function not implemented/testable yet | 112 |
| User Error | 111 |
| Invalid Testcase | 80 |
| Tolerated | 71 |

### B3. Ticket Matrix 对比（2024 vs 2025）

以下为两个年度并排对比口径（与 defect_explore6 的 matrix 统计方法一致）：

| Matrix | 2024 | 2025 |
|---|---:|---:|
| Matrix-3A | 832 | 2,233 |
| Matrix-2A | 788 | 1,239 |
| Matrix-3C | 221 | 830 |
| Matrix-2C | 356 | 823 |
| Matrix-1C | 232 | 366 |
| Matrix-4A | 209 | 365 |
| Matrix-2E | 171 | 339 |
| Matrix-1E | 201 | 334 |
| Matrix-1A | 258 | 318 |
| Matrix-3D | 52 | 201 |
| Matrix-2D | 77 | 197 |

### B4. 缺陷提票人统计（替换团队统计，Top15，两年对比）

口径：仅统计 `problem_finder_team = DTSV_China`。

| 排名 | 提票人 | 2024 | 2025 | 两年合计 |
|---:|---|---:|---:|---:|
| 1 | Weining Zhao | 415 | 476 | 891 |
| 2 | Jingpu Li | 386 | 474 | 860 |
| 3 | Jingsheng Liang | 356 | 394 | 750 |
| 4 | Wei Yang | 245 | 447 | 692 |
| 5 | Adley Wong | 288 | 363 | 651 |
| 6 | Felipe Wu | 229 | 418 | 647 |
| 7 | Dian Wang | 246 | 348 | 594 |
| 8 | Yuteng Zhao | 278 | 263 | 541 |
| 9 | Size Li | 229 | 312 | 541 |
| 10 | Kyle Ge | 276 | 261 | 537 |
| 11 | zhaokun hou | 245 | 243 | 488 |
| 12 | Linna Lu | 134 | 337 | 471 |
| 13 | Yunwei Gao | 193 | 269 | 462 |
| 14 | pengxiao zhang | 168 | 280 | 448 |
| 15 | Lijia Ma | 108 | 323 | 431 |

## C. 管理层摘要（最终版）

- **测试侧**：2025 执行规模持续增长（+11.3%），Pass率提升到 89.12%，Blocked率显著下降。  
- **缺陷侧**：总量上升但高风险结构下降（Showstopper Confirmed/Preventing 占比均下降）。  
- **CWA侧**：不可接受 Red 仅 5.02%，整体处于可控区间；“Function not implemented”可作为需求澄清与新功能推进的正向信号。  
