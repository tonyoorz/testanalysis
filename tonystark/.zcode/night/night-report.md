# Night Report — 2026-11-11

> 任务：编译 inbox 素材进 wiki，使知识库自洽可溯源。完成定义已达成：**QUEUE_EMPTY**。
> 执行记录：[[.zcode/night/state|state.md]]；lint/fix 脚本在 `.zcode/night/`。

## 数字总览

| 指标 | 起点 | 终点 |
|---|---|---|
| wiki 层断链 | 133 | **0** |
| 孤儿页 | 3 | **0** |
| 知识页（60 Knowledge） | 17 | **27**（新增 10 概念页） |
| 全库页面 | 134 | 144 |
| git 提交 | — | 5 个（基线 + 4 轮） |

修好的断链明细：
- 30 Topics 层 12 条：7 条裸名歧义链补全路径（`前段设计还能更好么` / `codex-windows桌面版下载` 与源文件同名导致无法解析）、3 条文件夹伪链（Topic Index 改为全量 27 页真实索引）、2 条 session 内 JSON 键伪双链。
- 40 Tools 层 121 条：全部指向「从未生成的 session 笔记」，降级为纯文本 ID + `[!note]` caveat（原因：<3 轮低价值 / 仅 artifact 快照 / wire 级日志），链回 Source Inventory，不臆造笔记。
- 剩余 6 条断链在 `10 Sources/` 原文内部（引文里的 `[[hooks.PreToolUse]]` 等），原文只读不修。
- 附带修正：WorkBuddy/Kimi 页自述的 session 笔记数（87/2）与实况（0/0）不符，已改为文件系统实况；R1 误跟踪的 `.obsidian/` 5 个文件已从 git 索引移除（磁盘未动，仓库本地 exclude）。

## 3 个最值得明早看的发现

### 1. 根目录 986 行调研文档此前是完全的孤岛，且断点 B 最锋利
`智能问数Agent全网深度调研-2026-08-03.md` 全库零引用、自身零双链。现已编译为 10 个概念页（[[30 Topics/Topic Index|Topic Index]] → 问数 Agent 调研编译 一节可入）。
其中 [[60 Knowledge/Concepts/Data-Agent架构基线与代码断点|架构基线与代码断点]] 给出 8 个代码级断点，最该先看**断点 B**：`query_semantic_records` 底层仍调 `_aggregate_rows()`（`semantic_query.py` L499/L575）——「聚合发现异常 → 取明细解释」的核心闭环实际是断的，records 返回的仍是分组计数表。

### 2. Ontology 接入状态存在新旧两个版本的矛盾说法（已标注，待确认）
- 2026-07-14 [[60 Knowledge/Solutions/goal-全网深度分析我的项目里的agent-分析一下我这个智能问数agent如|Codex 全网分析]]：Ontology「未接入主对话」。
- 2026-08-03 [[智能问数Agent全网深度调研-2026-08-03|代码级调研]]：`query_semantic_metrics/records/traceability` 语义工具入口已存在。
两者相差 3 周，大概率是演进而非错误，但按规则已用 `> [!contradiction]` 双源标注（见断点页），未删旧内容。建议明早确认实际分支状态。

### 3. 三个工具页的「笔记计数」是幻觉，暴露 compile 流程缺陷
Kimi(2)/WorkBuddy(87) 自称的 session 笔记从未存在——页面把「打算生成的链接」当成了「已生成的笔记」。这说明 vault 的编译脚本（`scripts/compile_all.py` 等）与实际产物之间没有对账机制。今夜的 `lint.py` 可直接充当这个对账器（断链=未兑现的计划），建议纳入日常流程。

## 交接说明
- 环境映射：`~/obsidian-vault` 不存在，按用户指示 vault=`tonystark`（`/Users/tonyorz/aianalysis/tonystark`）；inbox→`10 Sources`+根部散文档，wiki→五层编号目录（依据 vault 自带 CLAUDE.md schema）。
- git 仓库根在上级 `aianalysis/`，所有提交均用路径限定 `git add -A -- .`，未触碰仓库内其他脏文件。
- 20 个 raw 对话源此前已全部有对应知识页（19 页，其中 goal 两段对话合一页），本轮未发现新的未编译对话源。
