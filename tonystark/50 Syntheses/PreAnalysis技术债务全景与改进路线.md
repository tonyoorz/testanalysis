---
title: "PreAnalysis 技术债务全景与改进路线"
type: synthesis
compiled_at: 2026-07-15
compiler: claude-sonnet-5
tags:
  - synthesis
  - compiled
---

# PreAnalysis 技术债务全景与改进路线

> 跨主题综合页，基于 `60 Knowledge/` 全部知识页提炼。

# Data-Agent / PreAnalysis 技术债务评估报告

## 债务全景（按类别）

### 1. 安全与代码质量
- `agent/interpret/code_interpreter.py` 已完成从"子串黑名单"到"AST 静态分析 + 受限 builtins + 资源限制 + 最小化子进程环境"四层防御的加固（commit `8c920089`，297 insertions / 87 deletions，含 `tests/test_code_interpreter.py`），但**该加固仅存在于 `feature/2026-06-22-p1-complete` 分支**，尚未确认是否已合并进最新分支 `feature/2026-07-01-data-agent-sync`。
- `agent/sql_engine/generator.py`（`NL2SQLEngine.query()` 起始于 `:590`）、`aianalysis/data_processor.py`（引用行号已至 `:3298`、`:3810`）均为超大单体文件，缺乏模块拆分，工程治理债务明显。

### 2. 数据层 / 存储迁移
- SQLite → PostgreSQL 迁移处于"字段兼容但数据未迁移、读取链路未切换"的中间态：
  - PG 表 `octane_defects`（`defect_id/raw_json/fetched_at` NOT NULL）、`octane_manual_runs`（`mr_id/raw_json/fetched_at` NOT NULL）、`octane_payloads.year`（NOT NULL, default -1）比 SQLite 约束更严格，SQLite 侧当前允许为空，直接迁移会失败。
  - 数据量差距：defects 15298（SQLite）vs 0（PG）、manual_runs 34333 vs 0、histories 8493 vs 0。
  - 读取主链路仍走 SQLite：`aianalysis/data_processor.py:921`、`aianalysis/defect_explore6
