---
title: "你现在完整的查看一下我的项目，现在我是否是通过一键octane download把数据从octane"
type: knowledge
source: "Codex"
source_file: "10 Sources/raw/conversations/Codex/你现在完整的查看一下我的项目-现在我是否是通过一键octane-download把数据从octane.md"
compiled_at: 2026-07-15
compiler: claude-sonnet-5
tags:
  - compiled-knowledge
---

# 你现在完整的查看一下我的项目，现在我是否是通过一键octane download把数据从octane

> 编译自 [[10 Sources/raw/conversations/Codex/你现在完整的查看一下我的项目-现在我是否是通过一键octane-download把数据从octane.md]] 的完整对话。

## 核心问题
围绕"Octane 数据下载 → 清洗 → 特征 → Defect Explore 可视化分析"全流程，梳理当前项目的数据库使用现状（SQLite 是否已完全取代本地 JSON/history 文件），并在此基础上讨论项目文件结构的重构精简方案，以及是否需要为支撑未来 AI Agent 系统而更换/升级本地数据库技术栈（SQLite → PostgreSQL+pgvector），最终要求在不破坏现有 SQLite/本地文件逻辑与看板可运行性的前提下完成迁移实施。

## 关键结论

**现状诊断（数据链路）**
- 项目中存在两套下载器：`download/octane_downloader.py`（默认写数据库，除非加 `--skip-db`）和 `downloader7.py`（纯文件落地流程，无数据库写入逻辑）。
- 两者的字段定义一致：`DEFAULT_F_DEFECT_MAIN`、`DEFAULT_F_MANUALRUN` 均为 40/30 字段，覆盖对齐。
- History 抓取存在潜在差异风险：`downloader7.py` 单票 history limit=10000，`octane_downloader.py` 为 5000，极端情况可能截断。
- 当前 DB 实际数据量：`octane_defects=15298`、`octane_manual_runs=34333`、`octane_defect_histories=8493`，与本地文件数量一致（对齐状态）。
- 读取模式是**DB优先+文件回退**而非纯 DB only：默认 `db_first`（`db_migration_config.py:14`），写入默认 `both`（`db_migration_config.py:20`）；`data_processor.py` 的 `load_defect_data/load_test_data` 均有回退逻辑。
- `defect_explore6.py:669` 主加载走 `use_db=True`，但底层仍可能回退文件。
- **结论：本地 defect/mr/history 文件尚未完全变成备用方案**，部分分析仍直接读 `history/*.json`（如 `data_processor.py:3298`、`data_processor.py:3810`、`longrunner_analysis.py:93/289`），是流程中仍在依赖的部分，而非纯备份。

**数据库选型结论**
- SQLite 在当前阶段"完全可用"，不需要因为"要接入 AI"就立刻换 DuckDB 或向量库；性能瓶颈的真实来源通常是 JSON 反复读取解析、特征重复计算、history 文件级遍历，而非数据库本身。
- 最终锁定技术栈方向：**主库升级为 PostgreSQL 16 + pgvector**（结构化查询 + 语义检索统一在一套设施里），**DuckDB 仅作为可选的二阶段分析加速层**（非业务主库替代）。
- 换库判断门槛（达到任一条才考虑）：看板查询 P95 > 2s（索引/缓存优化后仍无改善）；AI 问答首答 P95 > 5s 且瓶颈在聚合层；单机内存峰值长期 > 80%；SQLite 写锁成为明显并发瓶颈。
- SQLite → PostgreSQL 迁移难度评估：中等难度，预计 1-2 周落地首版（保守 2-3 周），可实现"爬虫直写 PostgreSQL"而不再需要"先落本地 JSON 再迁移"的中间步骤。

**迁移原则（用户明确要求）**
- 迁移不得破坏现有 SQLite 与本地文件逻辑，看板需保持可运行。
- 采用"先双写不切读"的安全策略，任意阶段可回滚。

## 操作要点 / 实现细节

**项目重构规划（Q2/Q3，仅为计划未执行）**
- 目标目录结构：`apps/(defect_explore, agent)` `data_pipeline/(download, processing, storage)` `domain/(defect, test_run, history)` `shared/(utils, config, prompts)` `tests/(unit, integration, regression)` `scripts/(ops, diagnostics)` `docs/` `archive/(legacy_*)`。
- 文件分级策略：A类立即保留主线（`defect_explore6.py`、`data_processor.py`、`unified_data_loader.py`、`octane_db.py`、`db_migration_config.py`、`intelligent_agent.py`、`download/octane_downloader.py` 等）；B类先归档非主线（旧看板、`downloader7.py`、并行下载器、临时分析脚本、过期文档图片）；C类大体积数据资产处理（`qgate/`~4.6GB 移出主仓、`database/local_data.db`~4.3GB 不进 Git、`history/`~1.4GB 改为运行时目录仅留 smoke 样本）。
- 巨型文件拆分建议：`defect_explore6.py` → `layout/callbacks/charts/filters/state`；`data_processor.py` → `loaders/transforms/features/history_enrich/kpi`；`intelligent_agent.py` → `planner/tools/executors/prompting`。
- 分阶段执行：Phase 0 基线冻结 → Phase 1 结构重排不删 → Phase 2 归档清理 → Phase 3 数据资产瘦身 → Phase 4 兼容窗口后删除。

**PostgreSQL 双写迁移实施（已落地执行的代码改动）**
- 新增文件：
  - `pg_storage.py` — PostgreSQL 存储适配器
  - `init_postgres_db.py` — 建表初始化脚本
  - `deploy/start_postgres.sh` — Docker 本机启停脚本
  - `deploy/verify_dual_write.py` — SQLite vs PostgreSQL 对账脚本
- 修改文件：
  - `download/octane_downloader.py`：新增 `--enable-pg`、`--pg-url`、`--pg-schema` 等参数（`download/octane_downloader.py:370/379/380/382/428`）；Defect/MR/History 写入均已支持多目标（`:500`、`:609`、`:305`、`:669`）；默认不加参数时行为与原逻辑完全一致（`:437`、`:523`、`:633`）
  - `db_migration_config.py`：新增 `ENABLE_PG_WRITE`、`PG_URL`、`PG_SCHEMA`、`DB_BACKEND` 等配置项（`:27`）
  - `unified_data_loader.py`：新增可选 PostgreSQL 读取后端，默认仍 SQLite（`:46`、`:103`）；PG 连接与查询封装支持 `psycopg`/`psycopg2` 自动兼容（`:145`、`:160`）；Defect 读取双后端（`:442`、`:525`、`:565`）；Manual Runs 读取双后端（`:699`、`:772`、`:802`）；语义目录/AIDA 映射也加了 PG 分支（`:838`、`:875`）；数据源信息含 backend 状态，close 时关闭 PG 连接（`:927`、`:954`）
  - `requirements.txt:55`：新增 PostgreSQL 相关依赖
  - `DB_QUICK_START.md`、`README.md`：补充双写运行说明、PG 读取启用/回滚步骤

**PostgreSQL 表结构（与 SQLite 对齐策略）**
- 主表同名同字段：`octane_defects`（主键 `defect_id`）、`octane_manual_runs`（主键 `mr_id`）、`octane_defect_histories`（主键 `defect_id`）、可选 `defect_features`（主键 `defect_id`）。
- 索引：`octane_defects(year, team, phase, severity, program)`；`octane_manual_runs(year, run_team, release, defect_id)`；`octane_defect_histories(team, fetched_at)`。
- 写入策略：全部 `UPSERT`（`ON CONFLICT ... DO UPDATE`）、批量写入、失败降级小批重试。

**实际运行命令**
```bash
# 启动 PostgreSQL（Docker）
./deploy/start_postgres.sh up

# 初始化表
python init_postgres_db.py --pg-url "postgresql://octane:octane_pwd@localhost:5432/octane_local" --pg-schema public

# 启用双写下载
python download/octane_downloader.py \
  --auth-method cookie \
  --enable-pg \
  --pg-url "postgresql://octane:octane_pwd@localhost:5432/octane_local" \
  --fetch-history

# 对账（SQLite vs PostgreSQL）
python deploy/verify_dual_write.py \
  --sqlite-path database/local_data.db \
  --pg-url "postgresql://octane:octane_pwd@localhost:5432/octane_local" \
  --pg-schema public
```

**启用 PG 读取（不影响写入逻辑）**
```bash
export DB_BACKEND=postgres
export POSTGRES_URL="postgresql://octane:octane_pwd@localhost:5432/octane_local"
export PG_SCHEMA=public
# 启动原有看板即可验证
```

**手动检查 PostgreSQL 数据（psql）**
```bash
# mac 若无客户端先安装
brew install libpq
brew link --force libpq

psql "postgresql://octane:octane_pwd@localhost:5432/octane_local"
SET search_path TO public;
\dt
\d octane_defects
\d octane_manual_runs
\d octane_defect_histories
SELECT COUNT(*) FROM octane_defects;
SELECT COUNT(*) FROM octane_manual_runs;
SELECT COUNT(*) FROM octane_defect_histories;
SELECT defect_id, name, team, year, fv, fetched_at FROM octane_defects LIMIT 5;
SELECT mr_id, name, run_team, year, spec, fetched_at FROM octane_manual_runs LIMIT 5;
SELECT year, COUNT(*) FROM octane_defects GROUP BY year ORDER BY year;
\q
```

**验收/校验方式**
- 计数校验：defect/mr/history 文件数 vs DB 行数一致。
- 字段校验：抽样对比 raw_json 与历史分析关键字段。
- KPI 校验：关键图表/KPI 与旧版本基线差异阈值控制（建议 ≤1%）。
- 已完成的基础验证：语法/AST 检查通过；CLI `--help` 参数可见；SQLite 路径实测加载正常；`db_backend=postgres` 未配置 URL 时安全告警不中断默认流程。

## 踩过的坑 / 注意事项
- 本地 defect/mr/history JSON 文件**尚未完全**成为备用方案，多处分析代码（`data_processor.py:3298/3810`、`longrunner_analysis.py:93/289`）仍直接扫文件，未统一走 DB，是隐藏的技术债。
- `downloader7.py` 与 `octane_downloader.py` 的 history 抓取 limit 不一致（10000 vs 5000），极端情况可能导致数据截断风险。
- 项目中存在大体积目录拖累仓库：`qgate/`（~4.6GB）、`database/`（~4.3GB）、`history/`（~1.4GB），需要作为重构重点处理对象。
- 重构/清理策略采用"先归档 archive/ 再删除"，避免因隐藏依赖（如被定时任务调用的脚本）导致功能中断；入口变更需加日志观察至少一个周期后再决定删除。
- 数据库切换/双写风险点：双写增加失败面（需各存储目标独立异常处理，不互相阻断）
