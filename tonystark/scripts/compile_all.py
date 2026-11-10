#!/usr/bin/env python3
"""
全量编译：扫描 raw/conversations/ 所有对话，编译为知识页并自动归类。
已编译的跳过（基于 source_file frontmatter 去重）。
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parents[1]
CONVERSATIONS_ROOT = VAULT_ROOT / "10 Sources" / "raw" / "conversations"
KNOWLEDGE_ROOT = VAULT_ROOT / "60 Knowledge"

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL = "anthropic/claude-sonnet-5"
PROXY_HANDLERS = urllib.request.ProxyHandler({})

# 主题归类规则：(关键词列表, 目标子目录)
# 按优先级匹配，先匹配到的优先
TOPIC_RULES = [
    (["octane", "downloader", "data_processor", "数据流", "数据下载", "数据链路",
      "defect_explore", "数据清洗", "数据看板", "前端设计", "复刻", "网页设计"],
     "Solutions"),
    (["pgsql", "postgres", "sqlite", "数据库", "迁移", "字段匹配", "db"],
     "Decisions"),
    (["agent", "智能问数", "pi agent", "工具调用", "context", "记忆", "ontology",
      "本体", "data agent", "重构", "技术栈", "30天", "60天", "90天", "能力对标"],
     "Concepts"),
    (["openclaw", "hermes", "claude code", "codex", "modelscope", "glm",
      "启动报错", "环境配置", "skill", "windows", "桌面版", "手机", "model"],
     "Solutions"),
    (["git", "github", "仓库", "dataagent"],
     "Solutions"),
]


def classify_topic(title: str, content_preview: str) -> str:
    """根据标题和内容预览判断主题归类。"""
    haystack = (title + " " + content_preview[:2000]).lower()
    for keywords, subdir in TOPIC_RULES:
        if any(kw.lower() in haystack for kw in keywords):
            return subdir
    return "Solutions"  # 默认


def llm_compile(system_prompt: str, user_content: str) -> str:
    opener = urllib.request.build_opener(PROXY_HANDLERS)
    payload = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.3,
        "max_tokens": 4096,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
        },
    )
    with opener.open(req, timeout=180) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"]


SYSTEM_PROMPT = """你是一个知识编译引擎。把 AI 对话日志编译成结构化知识页（中文）。

规则：
1. 只从对话内容提炼，绝不编造（无据不写）
2. 信息不足时明确标注"（对话中未涉及）"
3. 保留所有具体文件路径、函数名、字段名、数值（高价值细节）
4. 输出严格 Markdown，章节：## 核心问题 / ## 关键结论 / ## 操作要点 / ## 踩过的坑 / ## 待解决问题
5. 不要输出 frontmatter 和标题行，直接从 ## 核心问题 开始
6. 保持中文，技术术语保留英文"""


def get_already_compiled() -> set:
    """返回已编译的 source_file 集合。"""
    compiled = set()
    for f in KNOWLEDGE_ROOT.rglob("*.md"):
        txt = f.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r'^source_file:\s*"(.*?)"', txt, re.M)
        if m:
            compiled.add(m.group(1))
    return compiled


def short_title(raw_title: str) -> str:
    """生成简短可读标题。"""
    t = re.sub(r"\[Image[^\]]*\]", "", raw_title)
    t = re.sub(r"https?://\S+", "", t)
    t = re.sub(r"[^\w\u4e00-\u9fff\s\-：，。、]+", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:40].rstrip("，。、 ") or "session"


def slugify(text: str) -> str:
    s = re.sub(r"[^\w\u4e00-\u9fff]+", "-", text).strip("-")
    return s[:40] or "session"


def compile_one(conv_path: Path, already: set) -> str:
    rel = str(conv_path.relative_to(VAULT_ROOT))
    if rel in already:
        return "SKIP"

    conversation = conv_path.read_text(encoding="utf-8")
    # 检查是否有答案
    a_count = len(re.findall(r"^### A\d", conversation, re.M))
    if a_count == 0:
        return "NO_ANSWER"

    # 截断超长对话
    if len(conversation) > 30000:
        conversation = conversation[:30000] + "\n\n[... 对话过长，已截断 ...]"

    title_match = re.search(r'^title:\s*"(.*)"', conversation, re.M)
    raw_title = title_match.group(1) if title_match else conv_path.stem
    stitle = short_title(raw_title)
    subdir = classify_topic(raw_title, conversation)
    source_label = conv_path.parent.name

    print(f"  编译: [{subdir}] {stitle} ({len(conversation)}字, {a_count}答案)...", flush=True)
    body = llm_compile(SYSTEM_PROMPT, f"以下是一段 AI 对话日志，请编译成知识页：\n\n---\n\n{conversation}")

    frontmatter = f"""---
title: "{stitle.replace(chr(34), chr(39))}"
type: knowledge
source: "{source_label}"
source_file: "{rel}"
compiled_at: {datetime.now().strftime("%Y-%m-%d")}
compiler: claude-sonnet-5
tags:
  - compiled-knowledge
---

# {stitle}

> 编译自 [[{rel}]] 的完整对话。

"""
    out_dir = KNOWLEDGE_ROOT / subdir
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{slugify(stitle)}.md"
    out_path = out_dir / fname
    # 防重名
    if out_path.exists():
        fname = f"{slugify(stitle)}-{conv_path.stem[:8]}.md"
        out_path = out_dir / fname
    out_path.write_text(frontmatter + body + "\n", encoding="utf-8")
    return "OK"


def main():
    if not OPENROUTER_KEY:
        print("ERROR: OPENROUTER_API_KEY 未设置", file=sys.stderr)
        sys.exit(1)

    already = get_already_compiled()
    print(f"已编译: {len(already)} 篇\n")

    all_convs = sorted(CONVERSATIONS_ROOT.rglob("*.md"))
    print(f"待处理: {len(all_convs)} 篇\n")

    ok, skip, no_answer, fail = 0, 0, 0, 0
    for conv_path in all_convs:
        try:
            result = compile_one(conv_path, already)
            if result == "OK":
                ok += 1
                print(f"  ✅ 完成\n")
            elif result == "SKIP":
                skip += 1
            elif result == "NO_ANSWER":
                no_answer += 1
                print(f"  ⏭ 跳过(无答案): {conv_path.name}\n")
        except Exception as e:
            fail += 1
            print(f"  ❌ 失败: {conv_path.name} - {e}\n")

    print(f"\n{'='*50}")
    print(f"编译完成: 成功 {ok} | 跳过(已编译) {skip} | 跳过(无答案) {no_answer} | 失败 {fail}")
    print(f"知识页输出: {KNOWLEDGE_ROOT}")


if __name__ == "__main__":
    main()
