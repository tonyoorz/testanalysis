#!/usr/bin/env python3
"""
读取 60 Knowledge/ 知识页，按主题分组，用 LLM 综合成深度 Topic 页。
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_ROOT = VAULT_ROOT / "60 Knowledge"
TOPICS_ROOT = VAULT_ROOT / "30 Topics"

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL = "anthropic/claude-sonnet-5"
PROXY_HANDLERS = urllib.request.ProxyHandler({})

# 5 大主题：name -> (关键词匹配, slug, 简介)
TOPICS = [
    ("Data-Agent 项目架构", ["Data-Agent", "text-to-sql", "缺陷", "octane", "智能问数",
        "ontology", "本体", "pi agent", "全网深度分析", "successfully", "explore the project"],
     "Data-Agent-项目架构",
     "Data-Agent（汽车测试缺陷/Octane 数据的 text-to-SQL Agent）的整体架构、能力分析与演进"),
    ("数据管道与数据库", ["octane download", "downloader", "data_processor", "pgsql", "postgres",
        "sqlite", "迁移", "字段匹配", "数据链路", "数据下载", "入库"],
     "数据管道与数据库",
     "数据从 Octane 下载 → 清洗 → 存储（SQLite/PostgreSQL）→ 展示的完整链路与数据库迁移"),
    ("Agent 工具链与环境配置", ["hermes", "openclaw", "claude code", "codex", "modelscope", "glm",
        "启动报错", "cc-switch", "桌面版", "手机", "model", "报错", "环境"],
     "Agent工具链与环境配置",
     "AI Agent 工具（Hermes/OpenClaw/Claude Code/Codex）的配置、模型切换、报错排查"),
    ("前端与数据可视化", ["defect explore", "前端设计", "网页设计", "复刻", "可视化",
        "看板", "前端", "vizion", "dtsv", "ai chat"],
     "前端与数据可视化",
     "数据看板（Defect Explore）的设计、前端优化、AI Chat 集成"),
    ("工程治理与环境维护", ["磁盘", "清理", "git", "仓库", "skill", "ppt", "查重",
        "分支", "ollama", "huggingface", "docker"],
     "工程治理与环境维护",
     "项目仓库管理、磁盘清理、技能/PPT 制作等工程治理事项"),
]


def llm_synthesize(system_prompt: str, user_content: str) -> str:
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
        headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
    )
    with opener.open(req, timeout=180) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"]


SYSTEM_PROMPT = """你是一个知识综合引擎。读取多篇知识页摘要，综合成一个深度主题页（中文）。

规则：
1. 只综合提供的知识页内容，不编造
2. 找出各篇之间的关联、矛盾、演进脉络
3. 保留所有具体文件路径、数值、技术细节
4. 输出 Markdown，结构：

## 主题概述
（2-3句说明这个主题讲什么）

## 核心知识
（按子主题组织，每个子主题综合多篇知识页的结论。用 ### 子标题。）

## 关键决策与方案
（这个主题下做出的重要技术决策、选型、方案）

## 待解决问题与技术债
（综合各篇的 Gap 和踩坑）

## 知识页索引
（列出本主题包含的知识页，用 wikilink 格式）

不要输出 frontmatter 和标题行，从 ## 主题概述 开始。"""


def load_knowledge_pages() -> list:
    """加载所有知识页的 (路径, 标题, 内容摘要)。"""
    pages = []
    for f in sorted(KNOWLEDGE_ROOT.rglob("*.md")):
        txt = f.read_text(encoding="utf-8", errors="ignore")
        title_m = re.search(r'^title:\s*"(.*)"', txt, re.M)
        title = title_m.group(1) if title_m else f.stem
        # 摘要：取到第一个 ## 待解决问题 之前的内容（去掉 frontmatter 和标题行）
        body = re.sub(r'^---\n.*?\n---\n', '', txt, flags=re.S, count=1)
        body = re.sub(r'^# .*\n\n^> .*\n\n', '', body, flags=re.M)
        # 截取核心问题+关键结论部分作为摘要
        summary = body[:2000]
        rel = f.relative_to(VAULT_ROOT)
        slug = f.stem
        pages.append({"path": rel, "title": title, "summary": summary, "slug": slug})
    return pages


def match_topic(page: dict) -> list:
    """返回一篇知识页匹配的所有主题名。"""
    haystack = (page["title"] + " " + page["summary"][:1500]).lower()
    matched = []
    for name, keywords, slug, desc in TOPICS:
        if any(kw.lower() in haystack for kw in keywords):
            matched.append(name)
    return matched


def main():
    if not OPENROUTER_KEY:
        print("ERROR: OPENROUTER_API_KEY 未设置", file=sys.stderr)
        sys.exit(1)

    pages = load_knowledge_pages()
    print(f"加载 {len(pages)} 篇知识页\n")

    # 分组
    topic_pages = {name: [] for name, _, _, _ in TOPICS}
    for p in pages:
        matched = match_topic(p)
        if not matched:
            # 未匹配的归到最相关的或通用
            topic_pages["工程治理与环境维护"].append(p)
        for name in matched:
            topic_pages[name].append(p)

    for name, _, slug, desc in TOPICS:
        member_pages = topic_pages[name]
        if not member_pages:
            print(f"⏭ [{name}] 无匹配知识页，跳过")
            continue

        print(f"📝 综合主题: {name} ({len(member_pages)} 篇知识页)...", flush=True)

        # 构造输入：各篇知识页的标题+摘要
        parts = []
        for p in member_pages:
            parts.append(f"### 知识页：{p['title']}\n\n{p['summary'][:1500]}\n")
        user_msg = f"以下是「{name}」主题下的 {len(member_pages)} 篇知识页摘要，请综合成深度主题页：\n\n---\n\n" + "\n---\n".join(parts)

        body = llm_synthesize(SYSTEM_PROMPT, user_msg)

        # 生成知识页索引 wikilinks
        index_lines = "\n".join(f"- [[{p['slug']}|{p['title']}]]" for p in member_pages)
        body = body.replace("## 知识页索引", f"## 知识页索引\n{index_lines}") if "## 知识页索引" in body else body + f"\n## 知识页索引\n{index_lines}\n"

        frontmatter = f"""---
title: "{name}"
type: topic
description: "{desc}"
page_count: {len(member_pages)}
compiled_at: {datetime.now().strftime("%Y-%m-%d")}
compiler: claude-sonnet-5
tags:
  - topic
  - compiled
---

# {name}

> {desc}。综合 {len(member_pages)} 篇知识页。

"""
        out_path = TOPICS_ROOT / f"{slug}.md"
        out_path.write_text(frontmatter + body + "\n", encoding="utf-8")
        print(f"  ✅ 完成: {out_path.name}\n")

    print(f"\n主题页生成完成，输出到 {TOPICS_ROOT}")


if __name__ == "__main__":
    main()
