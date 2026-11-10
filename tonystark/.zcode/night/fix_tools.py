#!/usr/bin/env python3
"""R4: 修复 40 Tools 六页死链 + 孤儿页。

规则（AGENTS.md: partial source → inventory note + caveat，不臆造笔记）：
1. [[20 Sessions/<dir>/<id>]] 目标不存在 → 降级为纯文本 `id`
2. Sessions 节首插入 caveat（含 Source Inventory 真实链接）
3. Summary 的 Session notes 计数改为 20 Sessions/<dir>/ 实际笔记数
4. Trae/Kimi/WorkBuddy 借 caveat/相关节获得解析出链 → 消孤儿
"""
import os
import re

VAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
TOOLS = {
    "Claude Code": "Claude Code",
    "Codex": "Codex",
    "Kimi": "Kimi",
    "OpenClaw": "OpenClaw",
    "QClaw": "QClaw",
    "WorkBuddy": "WorkBuddy",
    "Trae": "Trae",
}
REASON = {
    "WorkBuddy": "仅 artifact 快照历史，非完整对话",
    "Kimi": "wire/命令级日志，非完整对话",
    "Claude Code": "<3 轮低价值对话，编译时按规则剔除",
    "Codex": "<3 轮低价值对话，编译时按规则剔除",
    "OpenClaw": "<3 轮低价值对话，编译时按规则剔除",
    "QClaw": "<3 轮低价值对话，编译时按规则剔除",
}

for tool, sdir in TOOLS.items():
    path = os.path.join(VAULT, "40 Tools", f"{tool}.md")
    text = open(path, encoding="utf-8").read()
    orig = text
    sessions_dir = os.path.join(VAULT, "20 Sessions", sdir)
    notes = [f[:-3] for f in os.listdir(sessions_dir) if f.endswith(".md")] if os.path.isdir(sessions_dir) else []

    dead = []

    def repl(m):
        sid = m.group(1)
        if sid in notes:
            return m.group(0)
        dead.append(sid)
        return f"`{sid}`"

    text = re.sub(r"\[\[20 Sessions/[^/\]]+/([^\]]+)\]\]", repl, text)

    # 修正 Summary 计数
    text = re.sub(r"(## Summary\n- Session notes: )`\d+`", rf"\1`{len(notes)}`", text)

    # Sessions 节加 caveat（仅当确有死链被降级）
    if dead:
        caveat = (
            f"> [!note] 未建笔记的来源\n"
            f"> 下列纯文本 ID（共 {len(dead)} 个）是 [[10 Sources/Source Inventory|Source Inventory]] "
            f"中已编目、但未生成 session 笔记的来源：{REASON[tool]}。按 AGENTS.md 规则不为其臆造笔记，原始路径见清单。\n\n"
        )
        text = re.sub(r"(## Sessions\n)", rf"\1{caveat}", text, count=1)

    if text != orig:
        open(path, "w", encoding="utf-8").write(text)
        print(f"{tool}: de-linked {len(dead)}, session notes={len(notes)}")
    else:
        print(f"{tool}: no change")
