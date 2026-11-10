#!/usr/bin/env python3
"""
从原始 jsonl 提取完整对话（不截断、不漏答案）。
复用 ingest_ai_conversations.py 已验证的解析逻辑，但输出完整 user+assistant 内容。
输出：每篇 session 一个 markdown 文件到 10 Sources/raw/conversations/<tool>/<session_id>.md
仅提取 user_turns >= MIN_TURNS 的有价值 session。
"""
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

VAULT_ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()

CLAUDE_ROOT = HOME / ".claude" / "projects"
KIMI_ROOT = HOME / ".kimi"
OPENCLAW_ROOT = HOME / ".openclaw"
QCLAW_ROOT = HOME / ".qclaw"
CODEX_ROOT = HOME / ".codex"

OUTPUT_ROOT = VAULT_ROOT / "10 Sources" / "raw" / "conversations"
MIN_TURNS = 3  # 只提取 >=3 轮的有价值 session


def sanitize_text(text: str) -> str:
    text = text or ""
    text = re.sub(r"sk-[A-Za-z0-9_-]{12,}", "[REDACTED_API_KEY]", text)
    text = re.sub(r"(Authorization:\s*Bearer\s+)[A-Za-z0-9._-]+", r"\1[REDACTED_TOKEN]", text, flags=re.I)
    return text


def textify(value: Any) -> List[str]:
    """递归提取文本，不截断。"""
    items: List[str] = []
    if value is None:
        return items
    if isinstance(value, str):
        text = sanitize_text(value.strip())
        if text:
            items.append(text)
        return items
    if isinstance(value, list):
        for item in value:
            items.extend(textify(item))
        return items
    if isinstance(value, dict):
        if value.get("type") == "text" and isinstance(value.get("text"), str):
            items.append(value["text"].strip())
        for key in ("content", "payload", "message", "user_input", "input"):
            if key in value:
                items.extend(textify(value[key]))
        return items
    return items


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def is_substantive(text: str) -> bool:
    """判断是否是有实质内容的用户消息（过滤 hi/help 等噪声）。"""
    text = (text or "").strip()
    if not text or len(text) < 10:
        return False
    trivial = {"hi", "hello", "hey", "thanks", "谢谢", "/help", "/model"}
    if text.lower().strip() in trivial:
        return False
    return True


def parse_claude(path: Path) -> Optional[Dict[str, Any]]:
    rows = load_jsonl(path)
    if not rows:
        return None
    user_turns, assistant_turns = [], []
    session_id = path.stem
    cwd, started = "", ""
    for row in rows:
        if not started and row.get("timestamp"):
            started = str(row.get("timestamp"))
        if not cwd and row.get("cwd"):
            cwd = str(row.get("cwd"))
        rtype = row.get("type")
        if rtype == "user":
            if row.get("isMeta"):
                continue
            texts = textify(row.get("message", {}).get("content"))
            joined = "\n".join(t for t in texts if t).strip()
            if joined:
                user_turns.append(joined)
        elif rtype == "assistant":
            for block in row.get("message", {}).get("content", []):
                if isinstance(block, dict) and block.get("type") == "text":
                    text = (block.get("text") or "").strip()
                    if text:
                        assistant_turns.append(sanitize_text(text))
    substantive_user = [t for t in user_turns if is_substantive(t)]
    if len(substantive_user) < MIN_TURNS:
        return None
    return {
        "tool": "Claude Code", "session_id": session_id, "cwd": cwd,
        "started": started, "user_turns": user_turns, "assistant_turns": assistant_turns,
        "source_path": str(path),
    }


def parse_codex(path: Path) -> Optional[Dict[str, Any]]:
    rows = load_jsonl(path)
    if not rows:
        return None
    user_turns, assistant_turns = [], []
    session_id, cwd, started = path.stem, "", ""
    for row in rows:
        started = started or str(row.get("timestamp") or "")
        rtype = row.get("type")
        payload = row.get("payload", {})
        if rtype == "session_meta":
            session_id = str(payload.get("id") or session_id)
            started = str(payload.get("timestamp") or started)
            cwd = cwd or str(payload.get("cwd") or "")
        elif rtype == "turn_context":
            cwd = cwd or str(payload.get("cwd") or "")
        elif rtype == "event_msg" and payload.get("type") == "user_message":
            text = (payload.get("message") or "").strip()
            if text:
                user_turns.append(sanitize_text(text))
        elif rtype == "response_item":
            ptype = payload.get("type")
            if ptype == "message" and payload.get("role") == "assistant":
                for block in payload.get("content", []):
                    if isinstance(block, dict) and block.get("type") in {"output_text", "text"}:
                        text = (block.get("text") or "").strip()
                        if text:
                            assistant_turns.append(sanitize_text(text))
    substantive_user = [t for t in user_turns if is_substantive(t)]
    if len(substantive_user) < MIN_TURNS:
        return None
    return {
        "tool": "Codex", "session_id": session_id, "cwd": cwd,
        "started": started, "user_turns": user_turns, "assistant_turns": assistant_turns,
        "source_path": str(path),
    }


def parse_openclaw_family(tool: str, path: Path) -> Optional[Dict[str, Any]]:
    rows = load_jsonl(path)
    if not rows:
        return None
    user_turns, assistant_turns = [], []
    session_id, cwd, started = path.stem, "", ""
    for row in rows:
        if row.get("type") == "session":
            session_id = str(row.get("id") or session_id)
            started = started or str(row.get("timestamp") or "")
            cwd = cwd or str(row.get("cwd") or "")
            continue
        if row.get("type") != "message":
            continue
        message = row.get("message", {})
        role = message.get("role")
        contents = message.get("content", [])
        if not isinstance(contents, list):
            contents = [contents]
        if role == "user":
            text = "\n".join(t for t in textify(contents) if t).strip()
            if text:
                user_turns.append(text)
        elif role == "assistant":
            for block in contents:
                if isinstance(block, dict) and block.get("type") == "text":
                    text = (block.get("text") or "").strip()
                    if text:
                        assistant_turns.append(sanitize_text(text))
    substantive_user = [t for t in user_turns if is_substantive(t)]
    if len(substantive_user) < MIN_TURNS:
        return None
    return {
        "tool": tool, "session_id": session_id, "cwd": cwd,
        "started": started, "user_turns": user_turns, "assistant_turns": assistant_turns,
        "source_path": str(path),
    }


def derive_title(user_turns: List[str]) -> str:
    """从第一个有内容的 user turn 生成人类可读标题。"""
    for t in user_turns:
        t = re.sub(r"<[^>]+>", " ", t)
        t = re.sub(r"!\[Image[^\]]*\]", "", t)
        t = re.sub(r"https?://\S+", "", t)
        t = re.sub(r"\s+", " ", t).strip()
        if len(t) >= 8:
            return t[:60].rstrip() + ("…" if len(t) > 60 else "")
    return "untitled-session"


def slugify(text: str) -> str:
    s = re.sub(r"[^\w\u4e00-\u9fff]+", "-", text).strip("-")
    return s[:50] or "session"


def render_conversation_md(rec: Dict[str, Any]) -> str:
    """渲染完整对话 markdown（不截断）。"""
    tool = rec["tool"]
    sid = rec["session_id"]
    title = derive_title(rec["user_turns"])
    lines = [
        "---",
        f'title: "{title.replace(chr(34), chr(39))}"',
        f"tool: {tool}",
        f"session_id: {sid}",
        f'source_path: "{rec["source_path"]}"',
        f'started_at: "{rec["started"]}"',
        f"user_turns: {len(rec['user_turns'])}",
        f"assistant_turns: {len(rec['assistant_turns'])}",
        "tags:",
        "  - ai-session",
        f"  - {tool.lower().replace(' ', '-')}",
        "---",
        "",
        f"# {title}",
        "",
        f"> 完整对话提取自 `{rec['source_path']}`",
        f"> 工具: {tool} | 用户消息: {len(rec['user_turns'])} | 助手回答: {len(rec['assistant_turns'])}",
        "",
    ]
    # 交错渲染 user/assistant（按原始顺序无法完全保证，但分别全量输出）
    lines.append("## 用户提问（完整）")
    lines.append("")
    for i, t in enumerate(rec["user_turns"], 1):
        lines.append(f"### Q{i}")
        lines.append("")
        lines.append(t)
        lines.append("")
    lines.append("## 助手回答（完整）")
    lines.append("")
    for i, t in enumerate(rec["assistant_turns"], 1):
        lines.append(f"### A{i}")
        lines.append("")
        lines.append(t)
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    records: List[Dict[str, Any]] = []

    # Claude Code
    for path in sorted(CLAUDE_ROOT.glob("**/*.jsonl")):
        rec = parse_claude(path)
        if rec:
            records.append(rec)

    # Codex
    for path in sorted(CODEX_ROOT.glob("**/*.jsonl")):
        rec = parse_codex(path)
        if rec:
            records.append(rec)

    # OpenClaw
    for path in sorted((OPENCLAW_ROOT / "agents" / "main" / "sessions").glob("*.jsonl")):
        rec = parse_openclaw_family("OpenClaw", path)
        if rec:
            records.append(rec)

    # QClaw
    for path in sorted((QCLAW_ROOT / "agents" / "main" / "sessions").glob("*.jsonl")):
        rec = parse_openclaw_family("QClaw", path)
        if rec:
            records.append(rec)

    # 写出
    by_tool: Dict[str, List[Dict[str, Any]]] = {}
    for rec in records:
        by_tool.setdefault(rec["tool"], []).append(rec)

    total_written = 0
    for tool, recs in by_tool.items():
        tool_dir = OUTPUT_ROOT / tool.replace(" ", "-")
        tool_dir.mkdir(parents=True, exist_ok=True)
        for rec in recs:
            title = derive_title(rec["user_turns"])
            fname = f"{slugify(title)}.md"
            out_path = tool_dir / fname
            # 防止重名
            if out_path.exists():
                fname = f"{slugify(title)}-{rec['session_id'][:8]}.md"
                out_path = tool_dir / fname
            out_path.write_text(render_conversation_md(rec), encoding="utf-8")
            total_written += 1

    print(f"提取完成：{total_written} 篇有价值 session（≥{MIN_TURNS}轮）")
    for tool, recs in by_tool.items():
        print(f"  {tool}: {len(recs)} 篇")
    print(f"输出目录: {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
