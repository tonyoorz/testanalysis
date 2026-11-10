# Night Compile State — tonystark vault

- started: 2026-11-11（夜间无人值守任务）
- vault: /Users/tonyorz/aianalysis/tonystark（用户指定 vault=tonystark；~/obsidian-vault 不存在）
- lint 工具: `.zcode/night/lint.py`（本轮新增，仅放行写入区）

## 环境映射决策（重要，后续轮次沿用）

用户指令里的 `inbox/`、`wiki/` 在本 vault 中按 CLAUDE.md/AGENTS.md 的既有 schema 映射：

| 指令词汇 | 本 vault 实际位置 | 依据 |
|---|---|---|
| inbox/（只读源） | `10 Sources/` + vault 根部未编译散文档 | CLAUDE.md "Raw sources: immutable" |
| wiki/（唯一可写区） | `20 Sessions/` `30 Topics/` `40 Tools/` `50 Syntheses/` `60 Knowledge/` | CLAUDE.md "Wiki: agent-maintained notes under …" |
| .zcode/night/ | `.zcode/night/`（state/lint/report） | 指令原文 |

## 2026-11-11 R1 扫描结果（生成队列的依据）

- vault 共 134 个 md 页；lint 基线：**断链 139（wiki 层 133 + 不可变源 6）**、**孤儿页 3**
- 最大未 ingest 素材：根部 `智能问数Agent全网深度调研-2026-08-03.md`（986 行，text-to-SQL/Data-Agent 全网调研）
  — 全库**零引用、自身零双链**，完全游离
- 断链分类：
  - E(~120): `40 Tools/*` 链向从未生成的 session 笔记（WorkBuddy~89、Claude Code~19、Codex~8、QClaw3、Kimi2、OpenClaw2）→ 死链改纯文本+加 caveat
  - C(5): 30 Topics 用裸名 `[[前段设计还能更好么]]`/`[[codex-windows桌面版下载]]`，与 10 Sources 原文同名歧义 → 改全路径
  - D(3): Topic Index 链文件夹 `[[60 Knowledge/Concepts/]]` → 文件夹不能作 wikilink 目标
  - B(2): `20 Sessions/QClaw/ae66c400` 里 JSON 键 `[[reply_to_current]]` 误成双链
  - A(6): 10 Sources 原文内的伪双链 —— 原文只读，不修，lint 已从验收口径排除
- 孤儿页 3：`40 Tools/Kimi` `40 Tools/Trae` `40 Tools/WorkBuddy`（出链全死或无链）→ R4 修 E 时自然解决

## QUEUE

1. [ ] R2 ingest `智能问数Agent全网深度调研-2026-08-03.md` → `60 Knowledge/Concepts/` 生成 6-12 概念页，每页 ≥3 双链 + 出处回链
2. [ ] R3 修 C+D+B：30 Topics 裸名歧义链、Topic Index 文件夹链、QClaw session 伪双链
3. [ ] R4 修 E+孤儿：40 Tools 六页死链降级为文本 + caveat，接入 Topic Index/Source Inventory，消 3 孤儿
4. [ ] R5 终检 lint（wiki 层 0 断链 0 孤儿）→ 写 QUEUE_EMPTY → night-report.md

## Round Log

### R1 @ 2026-11-11
- 做了：扫描 vault 全量、写 lint.py 跑基线、生成上述队列、建本 state.md
- 下一个：R2 ingest 调研文档
- 坑：① 用户给的仓库路径 ~/obsidian-vault 不存在，按用户补充"vault 是 tonystark"定位到本路径；② git 仓库根在上级 `aianalysis/`，含大量与 vault 无关的脏文件，**提交必须用 `git add -A -- .`（限 vault 路径）**，绝不能裸 `git add -A`；③ macOS ls 输出里 `10 Sources` 前缀易看漏，实际目录都带编号
