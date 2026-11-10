#!/usr/bin/env python3
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


VAULT_ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()

CLAUDE_ROOT = HOME / ".claude" / "projects"
KIMI_ROOT = HOME / ".kimi"
TRAE_ROOT = HOME / "Library" / "Application Support" / "Trae"
OPENCLAW_ROOT = HOME / ".openclaw"
QCLAW_ROOT = HOME / ".qclaw"
CODEX_ROOT = HOME / ".codex"
WORKBUDDY_HISTORY_ROOT = HOME / "Library" / "Application Support" / "WorkBuddy" / "User" / "History"

SOURCE_NOTE = VAULT_ROOT / "10 Sources" / "Source Inventory.md"
SESSION_ROOT = VAULT_ROOT / "20 Sessions"
TOPICS_ROOT = VAULT_ROOT / "30 Topics"
TOOLS_ROOT = VAULT_ROOT / "40 Tools"
SYNTHESIS_NOTE = VAULT_ROOT / "50 Syntheses" / "AI Conversation Digest.md"
TOPICS_INDEX_NOTE = TOPICS_ROOT / "Topic Index.md"
HOW_TONY_WORKS_NOTE = VAULT_ROOT / "50 Syntheses" / "How Tony Works With AI Tools.md"
RECURRING_PROBLEMS_NOTE = VAULT_ROOT / "50 Syntheses" / "Recurring Coding Problems.md"
VALUABLE_REPOS_NOTE = VAULT_ROOT / "50 Syntheses" / "Most Valuable Repositories and Files.md"
PLAYBOOKS_NOTE = VAULT_ROOT / "50 Syntheses" / "AI Work Playbooks.md"
PLAYBOOK_PROMPTS_NOTE = VAULT_ROOT / "50 Syntheses" / "Prompt Templates for Playbooks.md"

TOOL_FOLDERS = {
    "Claude Code": SESSION_ROOT / "Claude Code",
    "Kimi": SESSION_ROOT / "Kimi",
    "Trae": SESSION_ROOT / "Trae",
    "OpenClaw": SESSION_ROOT / "OpenClaw",
    "QClaw": SESSION_ROOT / "QClaw",
    "Codex": SESSION_ROOT / "Codex",
    "WorkBuddy": SESSION_ROOT / "WorkBuddy",
}

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "your", "you",
    "have", "will", "what", "when", "where", "how", "为什么", "然后", "这个", "那个",
    "一下", "可以", "现在", "还是", "需要", "所有", "一个", "我们", "他们", "以及",
    "self", "str", "return", "none", "get", "set", "name", "type", "import",
    "tool", "line", "lines", "data", "context", "aliases", "def",
    "tonyorz", "staff", "string", "strings", "json", "file", "files",
    "system", "analysis", "not", "agent",
}

TOPIC_RULES = [
    ("KPI Reports", [r"\bkpi\b", r"report", r"看板", r"报告", r"dashboard"]),
    ("Defect Explore", [r"defect explore", r"defect_explore", r"modern", r"visual", r"plotly"]),
    ("Data Pipeline", [r"downloader", r"octane", r"manual_runs", r"history", r"payload", r"etl", r"processor"]),
    ("Databases", [r"sqlite", r"postgres", r"postgresql", r"duckdb", r"\bdb\b", r"database"]),
    ("OpenClaw Ecosystem", [r"openclaw", r"qclaw", r"skill", r"wechat", r"feishu", r"gateway"]),
    ("AI Tooling", [r"claude", r"codex", r"kimi", r"cursor", r"trae", r"workbuddy"]),
    ("Obsidian Knowledge Base", [r"obsidian", r"vault", r"wiki", r"knowledge base", r"tonystark"]),
    ("Agent Architecture", [r"agent", r"memory", r"mcp", r"context", r"tool", r"prompt"]),
    ("UI and Frontend", [r"ui", r"frontend", r"css", r"react", r"next.js", r"html", r"design"]),
    ("Deployment and Infra", [r"docker", r"deploy", r"cloudflare", r"render", r"nginx", r"gateway"]),
]


def ensure_dirs() -> None:
    for path in [SOURCE_NOTE.parent, SESSION_ROOT, TOPICS_ROOT, TOOLS_ROOT, SYNTHESIS_NOTE.parent, *TOOL_FOLDERS.values()]:
        path.mkdir(parents=True, exist_ok=True)


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


def sanitize_text(text: str) -> str:
    text = text or ""
    text = re.sub(r"sk-[A-Za-z0-9_-]{12,}", "[REDACTED_API_KEY]", text)
    text = re.sub(r"(Authorization:\s*Bearer\s+)[A-Za-z0-9._-]+", r"\1[REDACTED_TOKEN]", text, flags=re.I)
    text = re.sub(r'("?(?:appSecret|apiKey|api_key|token|access_token|refresh_token)"?\s*:\s*")[^"]+(")', r'\1[REDACTED]\2', text, flags=re.I)
    text = re.sub(r"([?&](?:token|key|secret)=)[^&\\s]+", r"\1[REDACTED]", text, flags=re.I)
    return text


def textify(value: Any) -> List[str]:
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


def find_paths(text: str) -> List[str]:
    paths = []
    for match in re.findall(r"/Users/[^\s\"'<>]+", text):
        paths.append(match.rstrip("`,.)]}*"))
    return sorted(set(paths))


def trim(text: str, limit: int = 160) -> str:
    text = sanitize_text(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def substantive(text: str) -> bool:
    text = trim(text, 500)
    if not text:
        return False
    bad_prefixes = (
        "/plan",
        "Enabled plan mode",
        "Request interrupted by user for tool use",
    )
    if any(text.startswith(prefix) for prefix in bad_prefixes):
        return False
    if text.startswith("local-command-stdout") or text.startswith("command-name"):
        return False
    return True


def keyword_bag(texts: Iterable[str], limit: int = 12) -> List[str]:
    counter: Counter[str] = Counter()
    for text in texts:
        text = trim(text, 2000)
        for token in re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z][A-Za-z0-9_/-]{2,}", text):
            token_l = token.lower()
            if token_l in STOPWORDS:
                continue
            if token.startswith("toolu_") or token.startswith("tooluse_"):
                continue
            if token_l.startswith(("drwx", "-rw", "rw-r", "quote", "users/")):
                continue
            if "/" in token_l or "\\" in token_l:
                continue
            if re.fullmatch(r"[a-f0-9]{8,}", token_l):
                continue
            counter[token] += 1
    return [token for token, _ in counter.most_common(limit)]


def is_noise_ask(text: str) -> bool:
    normalized = trim(text, 300).lower()
    if not normalized:
        return True
    trivial = {
        "hi", "hello", "hey", "thanks", "谢谢",
        "cd testagent", "/model model", "/help",
    }
    if normalized in trivial:
        return True
    if len(normalized) < 12:
        return True
    return False


def meaningful_file_refs(paths: Iterable[str]) -> List[str]:
    results: List[str] = []
    for raw in paths:
        clean = raw.rstrip("\\")
        p = Path(clean)
        if clean in {"/Users/tonyorz", "/Users/tonyorz/aianalysis", "/Users/tonyorz/aianalysis/"}:
            continue
        if not p.suffix:
            continue
        if p.name.startswith("."):
            continue
        results.append(clean)
    return results


def normalize_repo_key(path: str) -> str:
    clean = path.replace("//Users/", "/Users/").rstrip("/")
    parts = Path(clean).parts
    if len(parts) >= 5 and parts[1] == "Users":
        return "/" + "/".join(parts[1:5])
    return str(Path(clean).parent)


def is_synthesis_noise(text: str) -> bool:
    normalized = trim(text, 300).lower()
    if not normalized:
        return True
    bad_markers = [
        "request interrupted by user",
        "web search results for query:",
        "search results for query:",
        "found 115 files",
        "found 14 files",
        "found 172 files",
        "found 10 files",
        "found ",
        "output too large",
        "export anthropic_",
        "total 10928",
        "drwx",
        "tonyorz ",
        "1→import ",
        "1→# ",
        "{\"title\":",
        "[{\"title\":",
        "\"{\"title\":",
        "\"[{\"title\":",
        "/users/tonyorz/aianalysis/qgate.py",
        "file content (",
        "现在我电脑什么程序运行中",
        "我下载的cc switch在哪儿",
        "skill-lookup /skill-lookup",
    ]
    return any(marker in normalized for marker in bad_markers)


def likely_problem_statement(text: str) -> bool:
    normalized = trim(text, 300)
    if is_synthesis_noise(normalized) or is_noise_ask(normalized):
        return False
    if normalized.startswith(("/", "{", "[", "1→", "2→")):
        return False
    if normalized.count("/") > 8:
        return False
    return any(
        marker in normalized.lower()
        for marker in [
            "需要", "如何", "问题", "报错", "不准", "升级", "分析", "explore",
            "understand", "find", "query", "data flow", "sql", "database",
            "docker", "deploy", "kpi", "report", "defect", "tool",
        ]
    )


def explain_asset(path: str) -> str:
    lower = path.lower()
    if "/agent/core/" in lower:
        return "Core agent orchestration and reasoning flow."
    if lower.endswith("local_data.db"):
        return "Primary local database repeatedly queried in analysis workflows."
    if lower.endswith("data_processor.py"):
        return "Central data cleaning and transformation logic."
    if "prompt_templates" in lower:
        return "Reusable prompting layer that shapes agent behavior."
    if "smart_tool_selector" in lower:
        return "Tool-routing logic, useful for diagnosing inaccurate tool choice."
    if "semantic_catalog" in lower:
        return "Schema/catalog artifacts that help agents interpret business data."
    if "aianalysis-nextjs" in lower:
        return "Modern frontend/reporting app iteration area."
    if "/history" in lower:
        return "Historical raw data that feeds trend and longitudinal analysis."
    if "/database" in lower:
        return "Operational storage for local analytics and agent memory."
    if ".openclaw" in lower:
        return "OpenClaw ecosystem configuration, skills, or extensions."
    if "/qgate" in lower:
        return "QGate-side defect or quality data inputs."
    if "/aida" in lower:
        return "Domain datasets used in defect/test exploration."
    if "/testagent" in lower:
        return "Related experimental agent codebase referenced for architecture comparison."
    if "/scripts" in lower:
        return "Automation scripts repeatedly reused in workflows."
    return "Frequently revisited in conversations, indicating reuse or debugging importance."


def frontmatter(data: Dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f'{key}: "{value}"')
    lines.append("---")
    return "\n".join(lines)


def write_note(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def build_record(
    *,
    tool: str,
    session_id: str,
    title: str,
    source_path: str,
    started_at: str = "",
    cwd: str = "",
    user_turns: Optional[List[str]] = None,
    assistant_turns: Optional[List[str]] = None,
    tool_counter: Optional[Counter[str]] = None,
    file_refs: Optional[Iterable[str]] = None,
    note_name: Optional[str] = None,
    kind: str = "session",
) -> Dict[str, Any]:
    user_turns = [sanitize_text(text) for text in (user_turns or []) if text]
    assistant_turns = [sanitize_text(text) for text in (assistant_turns or []) if text]
    meaningful_user_turns = [text for text in user_turns if substantive(text)]
    return {
        "tool": tool,
        "kind": kind,
        "session_id": session_id,
        "title": trim(title or session_id, 70).replace("/", " "),
        "started_at": started_at,
        "cwd": cwd,
        "source_path": source_path,
        "user_turns": user_turns,
        "assistant_turns": assistant_turns,
        "tool_counter": tool_counter or Counter(),
        "file_refs": sorted(set(file_refs or [])),
        "keywords": keyword_bag((meaningful_user_turns or user_turns)[:3]),
        "note_path": TOOL_FOLDERS[tool] / (note_name or f"{session_id}.md"),
    }


def resource_to_path(resource: str) -> str:
    resource = resource or ""
    if resource.startswith("file://"):
        return resource.replace("file://", "").replace("%20", " ")
    return resource


def parse_claude_session(path: Path) -> Optional[Dict[str, Any]]:
    rows = load_jsonl(path)
    if not rows:
        return None

    user_turns: List[str] = []
    assistant_turns: List[str] = []
    tool_counter: Counter[str] = Counter()
    file_refs: set[str] = set()
    session_id = path.stem
    cwd = ""
    started = ""

    for row in rows:
        if not started and row.get("timestamp"):
            started = str(row.get("timestamp"))
        if not cwd and row.get("cwd"):
            cwd = str(row.get("cwd"))

        row_type = row.get("type")
        if row_type == "user":
            if row.get("isMeta"):
                continue
            message = row.get("message", {})
            texts = textify(message.get("content"))
            joined = "\n".join(texts).strip()
            if joined:
                user_turns.append(joined)
                file_refs.update(find_paths(joined))
        elif row_type == "assistant":
            message = row.get("message", {})
            for block in message.get("content", []):
                if isinstance(block, dict) and block.get("type") == "text":
                    text = (block.get("text") or "").strip()
                    if text:
                        assistant_turns.append(text)
                        file_refs.update(find_paths(text))
                elif isinstance(block, dict) and block.get("type") == "tool_use":
                    tool_counter[block.get("name") or "unknown"] += 1
                    file_refs.update(find_paths(json.dumps(block, ensure_ascii=False)))

    if not user_turns and not assistant_turns:
        return None

    meaningful_user_turns = [text for text in user_turns if substantive(text)]
    first_prompt = meaningful_user_turns[0] if meaningful_user_turns else (user_turns[0] if user_turns else session_id)
    return build_record(
        tool="Claude Code",
        session_id=session_id,
        title=first_prompt,
        started_at=started,
        cwd=cwd,
        source_path=str(path),
        user_turns=user_turns,
        assistant_turns=assistant_turns,
        tool_counter=tool_counter,
        file_refs=file_refs,
    )


def parse_kimi_sources() -> List[Dict[str, Any]]:
    notes: List[Dict[str, Any]] = []

    for path in sorted((KIMI_ROOT / "sessions").glob("**/wire.jsonl")):
        rows = load_jsonl(path)
        if not rows:
            continue
        user_turns: List[str] = []
        assistant_turns: List[str] = []
        started = ""
        for row in rows:
            if not started and row.get("timestamp"):
                started = datetime.fromtimestamp(float(row["timestamp"])).isoformat()
            message = row.get("message", {})
            if message.get("type") == "TurnBegin":
                user_turns.extend(textify(message.get("payload", {}).get("user_input")))
            else:
                assistant_turns.extend(textify(message))
        session_id = path.parent.name
        if not user_turns and not assistant_turns:
            continue
        notes.append(build_record(
            tool="Kimi",
            session_id=session_id,
            title=user_turns[0] if user_turns else session_id,
            started_at=started,
            source_path=str(path),
            user_turns=user_turns,
            assistant_turns=assistant_turns,
            file_refs={p for text in user_turns + assistant_turns for p in find_paths(text)},
        ))

    history_path = next(iter(sorted((KIMI_ROOT / "user-history").glob("*.jsonl"))), None)
    if history_path:
        history_rows = load_jsonl(history_path)
        history_turns = [row.get("content", "").strip() for row in history_rows if row.get("content")]
        if history_turns:
            notes.append(build_record(
                tool="Kimi",
                session_id=history_path.stem,
                title="Kimi user history",
                source_path=str(history_path),
                user_turns=history_turns,
                assistant_turns=[],
                note_name=f"{history_path.stem}-history.md",
                kind="history",
            ))

    return notes


def build_trae_inventory() -> Dict[str, Any]:
    log_files = sorted(TRAE_ROOT.glob("logs/**/*.log"))
    return {
        "tool": "Trae",
        "count": len(log_files),
        "examples": [str(path) for path in log_files[:10]],
        "note_path": TOOL_FOLDERS["Trae"] / "Trae Source Inventory.md",
    }


def parse_openclaw_family(tool: str, root: Path) -> List[Dict[str, Any]]:
    notes: List[Dict[str, Any]] = []
    for path in sorted((root / "agents" / "main" / "sessions").glob("*.jsonl")):
        rows = load_jsonl(path)
        if not rows:
            continue
        user_turns: List[str] = []
        assistant_turns: List[str] = []
        tool_counter: Counter[str] = Counter()
        file_refs: set[str] = set()
        session_id = path.stem
        cwd = ""
        started = ""

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
                text = "\n".join(textify(contents)).strip()
                if text:
                    user_turns.append(text)
                    file_refs.update(find_paths(text))
            elif role == "assistant":
                for block in contents:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "text":
                        text = trim(block.get("text") or "", 2000)
                        if text:
                            assistant_turns.append(text)
                            file_refs.update(find_paths(text))
                    elif block.get("type") == "toolCall":
                        tool_counter[block.get("name") or "unknown"] += 1
                        file_refs.update(find_paths(json.dumps(block, ensure_ascii=False)))

        if not user_turns and not assistant_turns:
            continue
        title = next((text for text in user_turns if substantive(text)), user_turns[0] if user_turns else session_id)
        notes.append(build_record(
            tool=tool,
            session_id=session_id,
            title=title,
            started_at=started,
            cwd=cwd,
            source_path=str(path),
            user_turns=user_turns,
            assistant_turns=assistant_turns,
            tool_counter=tool_counter,
            file_refs=file_refs,
        ))
    return notes


def parse_codex_sources() -> List[Dict[str, Any]]:
    notes: List[Dict[str, Any]] = []

    for path in sorted((CODEX_ROOT / "sessions").glob("**/*.jsonl")):
        rows = load_jsonl(path)
        if not rows:
            continue
        user_turns: List[str] = []
        assistant_turns: List[str] = []
        tool_counter: Counter[str] = Counter()
        file_refs: set[str] = set()
        session_id = path.stem
        cwd = ""
        started = ""

        for row in rows:
            started = started or str(row.get("timestamp") or "")
            row_type = row.get("type")
            payload = row.get("payload", {})

            if row_type == "session_meta":
                meta = row.get("payload", {})
                session_id = str(meta.get("id") or session_id)
                started = str(meta.get("timestamp") or started)
                cwd = cwd or str(meta.get("cwd") or "")
            elif row_type == "turn_context":
                cwd = cwd or str(payload.get("cwd") or "")
            elif row_type == "event_msg" and payload.get("type") == "user_message":
                text = trim(payload.get("message") or "", 4000)
                if text:
                    user_turns.append(text)
                    file_refs.update(find_paths(text))
            elif row_type == "response_item":
                ptype = payload.get("type")
                if ptype == "message" and payload.get("role") == "assistant":
                    for block in payload.get("content", []):
                        if isinstance(block, dict) and block.get("type") in {"output_text", "text"}:
                            text = trim(block.get("text") or "", 2000)
                            if text:
                                assistant_turns.append(text)
                                file_refs.update(find_paths(text))
                elif ptype == "function_call":
                    tool_counter[payload.get("name") or "unknown"] += 1
                    file_refs.update(find_paths(json.dumps(payload, ensure_ascii=False)))

        if not user_turns and not assistant_turns:
            continue
        title = next((text for text in user_turns if substantive(text)), user_turns[0] if user_turns else session_id)
        notes.append(build_record(
            tool="Codex",
            session_id=session_id,
            title=title,
            started_at=started,
            cwd=cwd,
            source_path=str(path),
            user_turns=user_turns,
            assistant_turns=assistant_turns,
            tool_counter=tool_counter,
            file_refs=file_refs,
        ))

    history_path = CODEX_ROOT / "history.jsonl"
    if history_path.exists():
        rows = load_jsonl(history_path)
        prompts = [trim((row.get("text") or ""), 2000) for row in rows if row.get("text")]
        if prompts:
            notes.append(build_record(
                tool="Codex",
                session_id="history",
                title="Codex history",
                source_path=str(history_path),
                user_turns=prompts,
                assistant_turns=[],
                note_name="history.md",
                kind="history",
            ))

    return notes


def parse_workbuddy_sources() -> List[Dict[str, Any]]:
    notes: List[Dict[str, Any]] = []
    for entries_path in sorted(WORKBUDDY_HISTORY_ROOT.glob("**/entries.json")):
        try:
            data = json.loads(entries_path.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            continue
        entries = data.get("entries", [])
        if not entries:
            continue

        resource = resource_to_path(data.get("resource", ""))
        folder = entries_path.parent
        session_id = folder.name
        snippets: List[str] = []
        latest_ts = ""
        for entry in entries[:5]:
            entry_id = entry.get("id")
            latest_ts = latest_ts or str(entry.get("timestamp") or "")
            if not entry_id:
                continue
            snapshot = folder / entry_id
            if not snapshot.exists():
                continue
            raw = snapshot.read_text(encoding="utf-8", errors="ignore")
            snippets.append(f"{entry_id}: {trim(raw, 400)}")

        title_seed = Path(resource).name if resource else f"WorkBuddy {session_id}"
        notes.append(build_record(
            tool="WorkBuddy",
            session_id=session_id,
            title=f"WorkBuddy history - {title_seed}",
            started_at=latest_ts,
            source_path=str(entries_path),
            user_turns=[f"Tracked resource: {resource or 'unknown'}"],
            assistant_turns=snippets,
            file_refs=[resource] if resource.startswith("/Users/") else [],
            kind="artifact-history",
        ))
    return notes


def render_session_note(record: Dict[str, Any]) -> str:
    meaningful_user_turns = [text for text in record["user_turns"] if substantive(text)]
    top_tools = ", ".join(f"{name} x{count}" for name, count in record["tool_counter"].most_common(8)) or "none"
    file_lines = "\n".join(f"- `{path}`" for path in record["file_refs"][:20]) or "- none"
    user_lines = "\n".join(f"- {trim(text)}" for text in (meaningful_user_turns or record["user_turns"])[:10]) or "- none"
    assistant_lines = "\n".join(f"- {trim(text)}" for text in record["assistant_turns"][:6]) or "- none"
    keywords = ", ".join(record["keywords"]) or "none"

    fm = frontmatter({
        "title": record["title"],
        "tool": record["tool"],
        "session_id": record["session_id"],
        "source_path": record["source_path"],
        "started_at": record["started_at"],
        "user_turns": len(record["user_turns"]),
        "assistant_turns": len(record["assistant_turns"]),
        "tags": ["ai-session", record["tool"].lower().replace(" ", "-")],
    })

    return f"""{fm}

# {record["title"]}

## Snapshot
- Tool: [[40 Tools/{record["tool"]}]]
- Source: `{record["source_path"]}`
- Kind: `{record.get("kind", "session")}`
- Started: `{record["started_at"] or "unknown"}`
- Working directory: `{record["cwd"] or "unknown"}`
- User turns: `{len(record["user_turns"])}`
- Assistant turns: `{len(record["assistant_turns"])}`
- Tool usage: `{top_tools}`
- Keywords: `{keywords}`

## First Request
> {trim((meaningful_user_turns or record["user_turns"])[0]) if (meaningful_user_turns or record["user_turns"]) else "No user text captured."}

## Key User Asks
{user_lines}

## Representative Assistant Responses
{assistant_lines}

## Mentioned Files
{file_lines}

## Raw Source
- `{record["source_path"]}`
"""


def render_tool_note(tool: str, session_notes: List[Dict[str, Any]], caveat: str) -> str:
    source_paths = sorted({item["source_path"] for item in session_notes})
    linked_sessions = "\n".join(
        f"- [[20 Sessions/{tool}/{item['note_path'].name[:-3]}]]"
        for item in session_notes
    ) or "- none"
    sources_block = "\n".join(f"- `{path}`" for path in source_paths) or "- none"
    fm = frontmatter({
        "title": tool,
        "tags": ["ai-tool", "conversation-source"],
    })
    return f"""{fm}

# {tool}

## Summary
- Session notes: `{len(session_notes)}`
- Caveat: {caveat}

## Example Sources
{sources_block}

## Sessions
{linked_sessions}
"""


def render_source_inventory(sections: Dict[str, List[str]], notes: List[str]) -> str:
    blocks = []
    for name, paths in sections.items():
        lines = "\n".join(f"- `{path}`" for path in paths) or "- none"
        blocks.append(f"## {name}\n{lines}")
    return f"""---
title: Source Inventory
tags:
  - source-inventory
  - ai-conversations
---

# Source Inventory

{chr(10).join(blocks)}

## Notes
{chr(10).join(f"- {note}" for note in notes)}
"""


def render_trae_note(info: Dict[str, Any]) -> str:
    examples = "\n".join(f"- `{path}`" for path in info["examples"]) or "- none"
    fm = frontmatter({
        "title": "Trae",
        "tags": ["ai-tool", "conversation-source"],
    })
    return f"""{fm}

# Trae

## Current State
- Discovered log files: `{info["count"]}`
- Current local files look like runtime or editor logs, not full transcript exports.
- Recommended workflow: export or paste richer Trae conversations into `10 Sources/raw/trae/`.

## Example Log Paths
{examples}
"""


def render_digest(all_sessions: List[Dict[str, Any]]) -> str:
    tool_counter = Counter(item["tool"] for item in all_sessions)
    keywords = keyword_bag(
        (next((text for text in item["user_turns"] if substantive(text)), item["user_turns"][0] if item["user_turns"] else ""))
        for item in all_sessions
    )
    examples = "\n".join(
        f"- [[20 Sessions/{item['tool']}/{item['note_path'].name[:-3]}]]"
        for item in all_sessions
    ) or "- none"
    tool_lines = "\n".join(f"- {tool}: `{count}` sessions" for tool, count in tool_counter.items()) or "- none"
    keyword_lines = "\n".join(f"- {word}" for word in keywords[:20]) or "- none"
    return f"""---
title: AI Conversation Digest
tags:
  - synthesis
  - ai-conversations
---

# AI Conversation Digest

## Coverage
{tool_lines}

## Recurring Keywords
{keyword_lines}

## All Sessions
{examples}

## Workflow Note
- This digest is generated from local machine logs and manual source drops.
- It should be refreshed by re-running `python3 scripts/ingest_ai_conversations.py`.
"""


def slugify_topic(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-") or "topic"


def classify_topics(record: Dict[str, Any]) -> List[str]:
    haystack = " ".join([
        record.get("title", ""),
        " ".join(record.get("keywords", [])),
        " ".join(record.get("user_turns", [])[:5]),
        " ".join(record.get("assistant_turns", [])[:3]),
        " ".join(record.get("file_refs", [])[:10]),
        record.get("tool", ""),
    ]).lower()
    matched = [name for name, patterns in TOPIC_RULES if any(re.search(pattern, haystack, flags=re.I) for pattern in patterns)]
    if not matched:
        matched = ["Uncategorized"]
    return matched


def render_topic_note(name: str, records: List[Dict[str, Any]]) -> str:
    tool_counts = Counter(item["tool"] for item in records)
    topic_keywords = keyword_bag(
        text
        for item in records
        for text in (
            [item.get("title", "")]
            + item.get("keywords", [])
            + item.get("user_turns", [])[:3]
        )
    )
    file_counts = Counter(
        file_ref
        for item in records
        for file_ref in meaningful_file_refs(item.get("file_refs", [])[:10])
    )
    representative_asks = []
    for item in records:
        prompt = next((text for text in item.get("user_turns", []) if substantive(text)), "")
        if prompt and not is_noise_ask(prompt):
            representative_asks.append(prompt)
    deduped_asks: List[str] = []
    seen = set()
    for ask in representative_asks:
        key = trim(ask, 180).lower()
        if key in seen:
            continue
        seen.add(key)
        deduped_asks.append(ask)

    lead_keywords = ", ".join(topic_keywords[:6]) or "none"
    lead_tools = ", ".join(f"{tool} ({count})" for tool, count in sorted(tool_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:4]) or "none"
    top_files = [path for path, _ in file_counts.most_common(5)]
    focus_lines = []
    if top_files:
        focus_lines.append(f"This topic repeatedly touches `{top_files[0]}` and related files.")
    if len(top_files) > 1:
        focus_lines.append(f"Frequently co-mentioned files include `{top_files[1]}` and `{top_files[2] if len(top_files) > 2 else top_files[1]}`.")
    if deduped_asks:
        focus_lines.append(f"Representative work centers on: {trim(deduped_asks[0], 220)}")
    unresolved = []
    for ask in deduped_asks:
        text = trim(ask, 240)
        if any(marker in text.lower() for marker in ["why", "how", "优化", "如何", "改进", "问题", "报错", "不准", "升级"]):
            unresolved.append(text)
    unresolved_lines = "\n".join(f"- {item}" for item in unresolved[:6]) or "- none"
    focus_block = "\n".join(f"- {line}" for line in focus_lines) or "- none"

    tool_lines = "\n".join(f"- {tool}: `{count}`" for tool, count in sorted(tool_counts.items())) or "- none"
    session_lines = "\n".join(
        f"- [[20 Sessions/{item['tool']}/{item['note_path'].name[:-3]}]]"
        for item in sorted(records, key=lambda r: (r.get("started_at") or "", r["title"]))
    ) or "- none"
    source_lines = "\n".join(f"- `{item['source_path']}`" for item in records[:20]) or "- none"
    keyword_lines = "\n".join(f"- {word}" for word in topic_keywords[:15]) or "- none"
    file_lines = "\n".join(f"- `{path}` x `{count}`" for path, count in file_counts.most_common(12)) or "- none"
    ask_lines = "\n".join(f"- {trim(text, 180)}" for text in deduped_asks[:12]) or "- none"
    fm = frontmatter({
        "title": name,
        "tags": ["topic", "ai-conversations"],
    })
    return f"""{fm}

# {name}

## Summary
- Sessions: `{len(records)}`
- Tools covered: `{len(tool_counts)}`

## Topic Narrative
- This topic is primarily about `{name}` across repeated AI-tool conversations.
- The most visible tools here are: {lead_tools}.
- The dominant vocabulary suggests recurring focus on: {lead_keywords}.

## Working Patterns
{focus_block}

## Open Threads
{unresolved_lines}

## Tool Coverage
{tool_lines}

## Recurring Keywords
{keyword_lines}

## Common Files
{file_lines}

## Representative Asks
{ask_lines}

## Sessions
{session_lines}

## Example Sources
{source_lines}
"""


def render_topic_index(topic_map: Dict[str, List[Dict[str, Any]]]) -> str:
    lines = []
    for name in sorted(topic_map):
        path = slugify_topic(name)
        lines.append(f"- [[30 Topics/{path}|{name}]]: `{len(topic_map[name])}` sessions")
    fm = frontmatter({
        "title": "Topic Index",
        "tags": ["topic-index", "ai-conversations"],
    })
    return f"""{fm}

# Topic Index

## Topics
{chr(10).join(lines) if lines else "- none"}
"""


def render_how_tony_works(all_sessions: List[Dict[str, Any]], topic_map: Dict[str, List[Dict[str, Any]]]) -> str:
    tool_counter = Counter(item["tool"] for item in all_sessions)
    topic_counter = sorted(((name, len(records)) for name, records in topic_map.items()), key=lambda item: item[1], reverse=True)
    representative = []
    for item in all_sessions:
        prompt = next((text for text in item.get("user_turns", []) if substantive(text) and not is_noise_ask(text)), "")
        if prompt and not is_synthesis_noise(prompt):
            representative.append((item["tool"], trim(prompt, 220)))
    rep_lines = "\n".join(f"- {tool}: {text}" for tool, text in representative[:12]) or "- none"
    tool_lines = "\n".join(f"- {tool}: `{count}` sessions" for tool, count in tool_counter.most_common()) or "- none"
    topic_lines = "\n".join(f"- [[30 Topics/{slugify_topic(name)}|{name}]]: `{count}` sessions" for name, count in topic_counter[:10]) or "- none"
    fm = frontmatter({"title": "How Tony Works With AI Tools", "tags": ["synthesis", "workflow", "ai-conversations"]})
    return f"""{fm}

# How Tony Works With AI Tools

## Overview
- This synthesis summarizes recurring working habits visible across local AI-tool conversations.
- The current corpus suggests a workflow centered on repository exploration, data-pipeline understanding, agent architecture iteration, and report/dashboard refinement.

## Tool Mix
{tool_lines}

## Dominant Themes
{topic_lines}

## Observed Workflow
- Starts from broad repository mapping or system diagnosis, then narrows into specific files, tables, or defects.
- Reuses multiple agent interfaces for similar themes: coding execution, architecture analysis, tooling setup, and knowledge-base maintenance.
- Frequently turns concrete work into reusable structure, such as scripts, plans, report generators, or wiki pages.

## Representative Patterns
{rep_lines}
"""


def render_recurring_problems(all_sessions: List[Dict[str, Any]]) -> str:
    problem_buckets = {
        "Data flow and lineage confusion": ["data flow", "数据流", "downloader", "processor", "history", "从哪来"],
        "Database querying accuracy": ["sqlite", "postgres", "sql", "查询", "不准", "database"],
        "Agent/tool selection reliability": ["tool", "agent", "mcp", "参数", "不准确", "selector"],
        "UI/report consistency": ["report", "kpi", "html", "dashboard", "看板", "图表"],
        "Infra and environment setup": ["docker", "deploy", "gateway", "安装", "启动", "upgrade"],
    }
    matched: Dict[str, List[str]] = {name: [] for name in problem_buckets}
    for item in all_sessions:
        for text in item.get("user_turns", [])[:6]:
            if not likely_problem_statement(text):
                continue
            lower = text.lower()
            for bucket, needles in problem_buckets.items():
                if any(needle.lower() in lower for needle in needles):
                    matched[bucket].append(trim(text, 220))
    sections = []
    for bucket, items in matched.items():
        deduped = []
        seen = set()
        for text in items:
            if text in seen or is_synthesis_noise(text):
                continue
            seen.add(text)
            deduped.append(text)
        lines = "\n".join(f"- {text}" for text in deduped[:8]) or "- none"
        sections.append(f"## {bucket}\n{lines}")
    fm = frontmatter({"title": "Recurring Coding Problems", "tags": ["synthesis", "problems", "ai-conversations"]})
    return f"""{fm}

# Recurring Coding Problems

## Overview
- These are the most repeated classes of engineering problems visible across the imported AI-tool history.
- They are useful as a prioritization layer for future playbooks, guardrails, and reusable prompts.

{chr(10).join(sections)}
"""


def render_valuable_repos(all_sessions: List[Dict[str, Any]]) -> str:
    file_counts = Counter(
        file_ref
        for item in all_sessions
        for file_ref in meaningful_file_refs(item.get("file_refs", []))
    )
    repo_counts: Counter[str] = Counter()
    for path, count in file_counts.items():
        repo_key = normalize_repo_key(path)
        repo_counts[repo_key] += count
    top_repos = "\n".join(
        f"- `{repo}` x `{count}` references: {explain_asset(repo)}"
        for repo, count in repo_counts.most_common(15)
    ) or "- none"
    top_files = "\n".join(
        f"- `{path}` x `{count}` references: {explain_asset(path)}"
        for path, count in file_counts.most_common(20)
    ) or "- none"
    fm = frontmatter({"title": "Most Valuable Repositories and Files", "tags": ["synthesis", "repositories", "ai-conversations"]})
    return f"""{fm}

# Most Valuable Repositories and Files

## Overview
- This page highlights the repositories and files that recur most often across AI-tool conversations.
- High recurrence usually indicates either architectural importance, repeated debugging pressure, or strong reuse value.

## Repositories
{top_repos}

## Files
{top_files}
"""


def render_playbooks(topic_map: Dict[str, List[Dict[str, Any]]]) -> str:
    def topic_count(name: str) -> int:
        return len(topic_map.get(name, []))

    playbooks = [
        {
            "title": "Repository Discovery",
            "when": f"Use when a repo is unfamiliar or when a task starts with architecture mapping. Strongest signal: `Data Pipeline` ({topic_count('Data Pipeline')}) and `Agent Architecture` ({topic_count('Agent Architecture')}).",
            "steps": [
                "Ask for the overall directory structure and entry points first.",
                "Identify build files, runtime entry scripts, and configuration files.",
                "Map data flow or request flow before changing code.",
                "Promote findings into topic notes or synthesis pages after understanding stabilizes.",
            ],
        },
        {
            "title": "Data Pipeline Tracing",
            "when": f"Use when defects, KPI numbers, or downstream visualizations look wrong. Strongest signal: `Data Pipeline` ({topic_count('Data Pipeline')}) and `Defect Explore` ({topic_count('Defect Explore')}).",
            "steps": [
                "Start from the final report or visualization and trace backward to processors and downloaders.",
                "List raw source files, transformation steps, and database tables in order.",
                "Check column names, join keys, time filters, and deduplication logic.",
                "Summarize lineage in one note so the same investigation is not repeated from scratch.",
            ],
        },
        {
            "title": "DB-First Agent Analysis",
            "when": f"Use when agent answers are inaccurate against local business data. Strongest signal: `Databases` ({topic_count('Databases')}) and `Agent Architecture` ({topic_count('Agent Architecture')}).",
            "steps": [
                "Identify the primary database and core tables before asking the agent to reason broadly.",
                "Prefer schema discovery and small validation queries before complex generation.",
                "Inspect tool-routing, SQL generation, and context loading code paths together.",
                "Capture the trusted query path in a synthesis note for future reuse.",
            ],
        },
        {
            "title": "Report Generation and Verification",
            "when": f"Use when HTML, KPI, or dashboard output must match business totals. Strongest signal: `KPI Reports` ({topic_count('KPI Reports')}) and `UI and Frontend` ({topic_count('UI and Frontend')}).",
            "steps": [
                "Keep one canonical generator instead of patching outputs manually.",
                "Regenerate artifacts after each logic change and compare key totals.",
                "Verify totals, subtotals, ratios, and special-case rows explicitly.",
                "Promote reusable report logic into scripts instead of one-off edits.",
            ],
        },
        {
            "title": "AI Tooling and Environment Setup",
            "when": f"Use when switching models, configuring OpenClaw/QClaw, or setting up new AI workflows. Strongest signal: `AI Tooling` ({topic_count('AI Tooling')}) and `OpenClaw Ecosystem` ({topic_count('OpenClaw Ecosystem')}).",
            "steps": [
                "First confirm local installation paths, config files, and running services.",
                "Separate transcript sources from runtime logs before building automation around them.",
                "Record stable config and capability notes in tool pages.",
                "When a setup stabilizes, turn it into a reusable playbook or skill-backed workflow.",
            ],
        },
    ]

    blocks = []
    for playbook in playbooks:
        step_lines = "\n".join(f"- {step}" for step in playbook["steps"])
        blocks.append(
            f"## {playbook['title']}\n"
            f"- When to use: {playbook['when']}\n"
            f"- Goal: Turn repeated conversation patterns into a repeatable operating sequence.\n"
            f"{step_lines}"
        )
    fm = frontmatter({"title": "AI Work Playbooks", "tags": ["synthesis", "playbooks", "ai-conversations"]})
    return f"""{fm}

# AI Work Playbooks

## Overview
- These playbooks convert recurring AI-tool conversation patterns into reusable workflows.
- They are intended to reduce repeated rediscovery and make future sessions converge faster.

{chr(10).join(blocks)}
"""


def render_playbook_prompts() -> str:
    prompts = [
        {
            "title": "Repository Discovery",
            "prompt": (
                "请探索 `{repo_path}` 的整体结构，重点完成：\n"
                "1. 列出主要目录与入口文件\n"
                "2. 识别技术栈与运行方式\n"
                "3. 找出关键配置、核心模块和数据流入口\n"
                "4. 输出一份结构化总结，说明哪些目录最值得后续深入\n"
                "限制：先做结构理解，不要直接改代码。"
            ),
        },
        {
            "title": "Data Pipeline Tracing",
            "prompt": (
                "请追踪 `{project_path}` 中 `{target_artifact}` 的完整数据链路，重点完成：\n"
                "1. 找到原始数据来源\n"
                "2. 找到下载器、处理器、存储层和最终展示层\n"
                "3. 说明关键字段如何流转与变换\n"
                "4. 标出最可能导致结果错误的环节\n"
                "输出格式：source -> processing -> storage -> output。"
            ),
        },
        {
            "title": "DB-First Agent Analysis",
            "prompt": (
                "请分析 `{project_path}` 中 agent 针对数据库 `{db_path}` 的工作方式，重点完成：\n"
                "1. 找出 schema 获取、SQL 生成、工具调用、结果解释 的代码路径\n"
                "2. 判断为什么查询会不准或偏离业务语义\n"
                "3. 给出一个 DB-first 的改进方案\n"
                "4. 优先关注 schema discovery、query validation、tool routing。"
            ),
        },
        {
            "title": "Report Generation and Verification",
            "prompt": (
                "请分析 `{project_path}` 中 `{report_name}` 的生成逻辑，重点完成：\n"
                "1. 找到报表生成入口和依赖数据\n"
                "2. 找到关键计算逻辑、聚合逻辑、过滤逻辑\n"
                "3. 说明如何验证总数、比率和特殊项是否正确\n"
                "4. 给出最适合沉淀为脚本的复用步骤。"
            ),
        },
        {
            "title": "AI Tooling and Environment Setup",
            "prompt": (
                "请检查 `{tool_name}` 在本机的安装、配置和运行状态，重点完成：\n"
                "1. 找到本地配置目录、日志目录、会话目录\n"
                "2. 区分 transcript、history、runtime log\n"
                "3. 判断哪些内容适合导入 Obsidian\n"
                "4. 给出后续自动化维护建议。"
            ),
        },
    ]

    blocks = []
    for item in prompts:
        blocks.append(
            f"## {item['title']}\n"
            f"- Use with: [[50 Syntheses/AI Work Playbooks]]\n\n"
            f"```text\n{item['prompt']}\n```"
        )
    fm = frontmatter({"title": "Prompt Templates for Playbooks", "tags": ["synthesis", "prompts", "playbooks"]})
    return f"""{fm}

# Prompt Templates for Playbooks

## Overview
- These templates are copyable starting prompts for recurring AI work patterns.
- Replace placeholder variables like `{{repo_path}}` or `{{db_path}}` before use.

{chr(10).join(blocks)}
"""


def main() -> None:
    ensure_dirs()

    claude_files = sorted(CLAUDE_ROOT.glob("**/*.jsonl"))
    kimi_wire_files = sorted((KIMI_ROOT / "sessions").glob("**/wire.jsonl"))
    kimi_history_files = sorted((KIMI_ROOT / "user-history").glob("*.jsonl"))
    openclaw_files = sorted((OPENCLAW_ROOT / "agents" / "main" / "sessions").glob("*.jsonl"))
    qclaw_files = sorted((QCLAW_ROOT / "agents" / "main" / "sessions").glob("*.jsonl"))
    codex_files = sorted((CODEX_ROOT / "sessions").glob("**/*.jsonl"))
    workbuddy_files = sorted(WORKBUDDY_HISTORY_ROOT.glob("**/entries.json"))

    claude_sessions = [item for item in (parse_claude_session(path) for path in claude_files) if item]
    kimi_sessions = parse_kimi_sources()
    openclaw_sessions = parse_openclaw_family("OpenClaw", OPENCLAW_ROOT)
    qclaw_sessions = parse_openclaw_family("QClaw", QCLAW_ROOT)
    codex_sessions = parse_codex_sources()
    workbuddy_sessions = parse_workbuddy_sources()
    trae_info = build_trae_inventory()

    all_sessions = claude_sessions + kimi_sessions + openclaw_sessions + qclaw_sessions + codex_sessions + workbuddy_sessions
    topic_map: Dict[str, List[Dict[str, Any]]] = {}
    for record in all_sessions:
        for topic in classify_topics(record):
            topic_map.setdefault(topic, []).append(record)

    for record in all_sessions:
        write_note(record["note_path"], render_session_note(record))
    for topic, records in topic_map.items():
        write_note(TOPICS_ROOT / f"{slugify_topic(topic)}.md", render_topic_note(topic, records))
    write_note(TOPICS_INDEX_NOTE, render_topic_index(topic_map))

    write_note(TOOLS_ROOT / "Claude Code.md", render_tool_note(
        "Claude Code",
        claude_sessions,
        "Rich local JSONL transcripts are available and used as primary source material.",
    ))
    write_note(TOOLS_ROOT / "Kimi.md", render_tool_note(
        "Kimi",
        kimi_sessions,
        "Local sources are thinner than Claude Code; some sessions may only expose command-level history.",
    ))
    write_note(TOOLS_ROOT / "OpenClaw.md", render_tool_note(
        "OpenClaw",
        openclaw_sessions,
        "Local JSONL sessions are available and include user, assistant, and tool-call events.",
    ))
    write_note(TOOLS_ROOT / "QClaw.md", render_tool_note(
        "QClaw",
        qclaw_sessions,
        "Local JSONL sessions are available across webchat and channel-connected conversations.",
    ))
    write_note(TOOLS_ROOT / "Codex.md", render_tool_note(
        "Codex",
        codex_sessions,
        "Codex has rich session JSONL plus a lightweight prompt history file; sensitive strings are redacted during ingest.",
    ))
    write_note(TOOLS_ROOT / "WorkBuddy.md", render_tool_note(
        "WorkBuddy",
        workbuddy_sessions,
        "WorkBuddy currently exposes artifact-history entries more clearly than direct chat transcripts; notes summarize tracked resources and recent snapshots.",
    ))
    write_note(trae_info["note_path"], render_trae_note(trae_info))
    write_note(TOOLS_ROOT / "Trae.md", render_tool_note(
        "Trae",
        [],
        "Current local logs are operational/editor logs. Manual conversation exports are recommended for higher-fidelity notes.",
    ))

    write_note(SOURCE_NOTE, render_source_inventory(
        {
            "Claude Code": [str(path) for path in claude_files],
            "Kimi": [str(path) for path in kimi_wire_files + kimi_history_files],
            "OpenClaw": [str(path) for path in openclaw_files],
            "QClaw": [str(path) for path in qclaw_files],
            "Codex": [str(path) for path in codex_files] + ([str(CODEX_ROOT / "history.jsonl")] if (CODEX_ROOT / "history.jsonl").exists() else []),
            "WorkBuddy": [str(path) for path in workbuddy_files],
            "Trae": trae_info["examples"],
        },
        [
            "Claude Code sources are rich `.jsonl` session logs.",
            "Kimi sources currently expose command and wire-level logs.",
            "OpenClaw and QClaw both store standard JSONL session transcripts.",
            "Codex stores full session JSONL plus a lightweight prompt history file.",
            "WorkBuddy history currently looks more like artifact snapshots than full chat transcripts.",
            "Trae local logs appear to be runtime/editor logs, not full user-assistant transcripts.",
            "For missing tools or richer exports, place manual dumps under `10 Sources/raw/`.",
        ],
    ))
    write_note(SYNTHESIS_NOTE, render_digest(all_sessions))
    write_note(HOW_TONY_WORKS_NOTE, render_how_tony_works(all_sessions, topic_map))
    write_note(RECURRING_PROBLEMS_NOTE, render_recurring_problems(all_sessions))
    write_note(VALUABLE_REPOS_NOTE, render_valuable_repos(all_sessions))
    write_note(PLAYBOOKS_NOTE, render_playbooks(topic_map))
    write_note(PLAYBOOK_PROMPTS_NOTE, render_playbook_prompts())

    print(f"Vault updated: {VAULT_ROOT}")
    print(f"Claude sessions: {len(claude_sessions)}")
    print(f"Kimi sessions: {len(kimi_sessions)}")
    print(f"OpenClaw sessions: {len(openclaw_sessions)}")
    print(f"QClaw sessions: {len(qclaw_sessions)}")
    print(f"Codex sessions: {len(codex_sessions)}")
    print(f"WorkBuddy histories: {len(workbuddy_sessions)}")
    print(f"Trae log files: {trae_info['count']}")
    print(f"Topics: {len(topic_map)}")


if __name__ == "__main__":
    main()
