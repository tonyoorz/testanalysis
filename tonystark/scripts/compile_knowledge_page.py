#!/usr/bin/env python3
"""
用 LLM (OpenRouter claude-sonnet) 把完整对话编译成结构化知识页。
读取 raw/conversations/ 的对话 markdown，输出 60 Knowledge/ 知识页。
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
# 绕过失效代理
PROXY_HANDLERS = urllib.request.ProxyHandler({})


def llm_compile(system_prompt: str, user_content: str) -> str:
    """调用 OpenRouter claude-sonnet 编译。"""
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


SYSTEM_PROMPT = """你是一个知识编译引擎。你的任务是把 AI 对话日志编译成结构化的知识页（中文）。

规则：
1. 只从对话内容中提炼，绝不编造对话中没有的信息（无据不写）
2. 如果对话中信息不足，明确标注"（对话中未涉及）"
3. 保留所有具体的文件路径、函数名、字段名、数值（这些是高价值细节）
4. 输出严格的 Markdown，包含以下章节：

## 核心问题
（1-3句话概括这个对话要解决什么问题）

## 关键结论
（提炼对话中得到的实质性结论，每条带具体细节。用列表。）

## 操作要点 / 实现细节
（可复用的步骤、代码结构、配置等。如果对话讨论了具体实现，详细记录。）

## 踩过的坑 / 注意事项
（对话中提到的问题、风险、待办事项）

## 待解决问题
（对话中明确未解决的开放问题）

不要输出 frontmatter、不要输出标题行（# xxx），直接从 ## 核心问题 开始。
保持中文，技术术语保留英文。"""


def compile_one(conversation_path: Path, output_path: Path, source_label: str) -> str:
    """编译一篇对话为知识页。"""
    conversation = conversation_path.read_text(encoding="utf-8")
    # 截断过长的对话（避免超 token）
    if len(conversation) > 30000:
        conversation = conversation[:30000] + "\n\n[... 对话过长，已截断 ...]"

    user_msg = f"以下是一段 AI 对话日志，请编译成知识页：\n\n---\n\n{conversation}"
    print(f"  编译中: {conversation_path.name} ({len(conversation)} 字符)...", flush=True)
    body = llm_compile(SYSTEM_PROMPT, user_msg)

    # 提取标题：从对话第一个 user turn 或现有 frontmatter
    title_match = re.search(r'^title:\s*"(.*)"', conversation, re.M)
    raw_title = title_match.group(1) if title_match else conversation_path.stem
    # 生成简短标题
    title = raw_title[:50].rstrip("，。、 ") or conversation_path.stem

    frontmatter = f"""---
title: "{title}"
type: knowledge
source: "{source_label}"
source_file: "{conversation_path.relative_to(VAULT_ROOT)}"
compiled_at: {datetime.now().strftime("%Y-%m-%d")}
compiler: claude-sonnet-5
tags:
  - compiled-knowledge
---

# {title}

> 编译自 [[{conversation_path.relative_to(VAULT_ROOT)}]] 的完整对话。

"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(frontmatter + body + "\n", encoding="utf-8")
    return title


def main():
    if not OPENROUTER_KEY:
        print("ERROR: OPENROUTER_API_KEY 未设置", file=sys.stderr)
        sys.exit(1)

    # 试点：指定的 3 篇 Data-Pipeline 对话
    targets = [
        ("Codex/你现在完整的查看一下我的项目-现在我是否是通过一键octane-download把数据从octane.md",
         "Solutions/octane数据下载与入库链路.md"),
        ("Codex/我现在pqsql-和sqlite一样看一下里边数据存储字段是匹配的么-我想确保我之后迁移到pqsql.md",
         "Decisions/pgsql迁移与字段匹配.md"),
        ("Codex/Image-1-你可以在-defect-explore-modem里边复刻我刚才给你发的图片的网页设.md",
         "Solutions/defect-explore看板设计.md"),
    ]

    print(f"开始编译 {len(targets)} 篇知识页（模型: {MODEL}）...\n")
    for conv_rel, out_rel in targets:
        conv_path = CONVERSATIONS_ROOT / conv_rel
        out_path = KNOWLEDGE_ROOT / out_rel
        if not conv_path.exists():
            print(f"  跳过（文件不存在）: {conv_rel}")
            continue
        source_label = conv_path.parts[-2]  # tool name
        title = compile_one(conv_path, out_path, source_label)
        print(f"  ✅ 完成: {out_rel} ({title})\n")

    print(f"\n编译完成，输出到 {KNOWLEDGE_ROOT}")


if __name__ == "__main__":
    main()
