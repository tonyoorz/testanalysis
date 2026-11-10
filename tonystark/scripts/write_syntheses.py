#!/usr/bin/env python3
"""
读取 60 Knowledge/ 全部知识页，用 LLM 综合成高价值 Synthesis 页。
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
SYNTH_ROOT = VAULT_ROOT / "50 Syntheses"

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL = "anthropic/claude-sonnet-5"
PROXY_HANDLERS = urllib.request.ProxyHandler({
    "http": "http://127.0.0.1:7897",
    "https": "http://127.0.0.1:7897",
})


def llm(system_prompt: str, user_content: str, retries: int = 3) -> str:
    import time
    last_err = None
    for attempt in range(retries):
        try:
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
            with opener.open(req, timeout=300) as resp:
                data = json.loads(resp.read())
            msg = data["choices"][0]["message"]
            content = msg.get("content")
            # claude-sonnet-5 可能把内容放 reasoning 字段
            if not content and msg.get("reasoning"):
                content = msg["reasoning"]
            if not content:
                raise ValueError("API 返回空 content")
            return content
        except Exception as e:
            last_err = e
            print(f"    重试 {attempt+1}/{retries}: {type(e).__name__}", flush=True)
            time.sleep(5 * (attempt + 1))
    raise last_err


# 3 个综合页的定义：(标题, slug, 系统提示, 用户提示)
SYNTHESES = [
    ("PreAnalysis 技术债务全景与改进路线",
     "PreAnalysis技术债务全景与改进路线",
     "你是技术架构师。综合知识页，梳理一个数据分析和 AI Agent 系统的技术债务，按优先级（P0/P1/P2）给改进路线。中文输出，保留具体文件路径、行号、数据量。",
     "综合以下知识页，梳理 PreAnalysis/Data-Agent 项目的技术债务全景，按 P0/P1/P2 优先级给改进路线图。结构：## 债务全景（按类别） / ## 改进路线（P0/P1/P2，每项含具体文件和预估工作量） / ## 风险与依赖。"),

    ("数据分析系统完整数据流",
     "数据分析系统完整数据流",
     "你是数据工程师。综合知识页，梳理一个数据分析系统的完整数据流（从源头到展示）。中文输出，保留表名、字段数、文件路径。",
     "综合以下知识页，梳理 PreAnalysis 的完整数据流：Octane 下载 → 清洗 → 特征 → 存储（SQLite/PG）→ Defect Explore 展示。结构：## 数据源 / ## 下载链路 / ## 处理与清洗 / ## 存储层（表结构、数据量、双写状态） / ## 展示层 / ## 已知断点与风险。"),

    ("AI Agent 能力盘点与演进",
     "AI-Agent能力盘点与演进",
     "你是 Agent 架构师。综合知识页，盘点一个企业数据分析 Agent 的能力现状，给出演进建议。中文输出。",
     "综合以下知识页，盘点 Data-Agent 的能力现状（工具链、记忆、可解释性、评测等），对标成熟框架，给出演进建议。结构：## 能力现状（按维度） / ## 与成熟框架的差距 / ## 演进建议（30/60/90天） / ## 不要做的事（避免 overengineering）。"),
]


def load_all_summaries() -> str:
    """加载所有知识页摘要，拼接成上下文。"""
    parts = []
    total = 0
    for f in sorted(KNOWLEDGE_ROOT.rglob("*.md")):
        txt = f.read_text(encoding="utf-8", errors="ignore")
        title_m = re.search(r'^title:\s*"(.*)"', txt, re.M)
        title = title_m.group(1) if title_m else f.stem
        # 取核心问题+关键结论部分
        body = txt[txt.find("# ") :]
        # 截取摘要（控制总长度）
        summary = body[:1800]
        parts.append(f"### {title}\n\n{summary}\n")
        total += len(summary)
        if total > 25000:  # 控制总长度，避免请求过大
            break
    return "\n---\n".join(parts)


def main():
    if not OPENROUTER_KEY:
        print("ERROR: OPENROUTER_API_KEY 未设置", file=sys.stderr)
        sys.exit(1)

    context = load_all_summaries()
    print(f"加载知识页上下文 ({len(context)} 字符)\n")

    for title, slug, sys_prompt, user_prompt in SYNTHESES:
        print(f"📝 生成综合页: {title}...", flush=True)
        user_msg = f"{user_prompt}\n\n以下是全部知识页摘要：\n\n---\n\n{context}"
        body = llm(sys_prompt, user_msg)

        frontmatter = f"""---
title: "{title}"
type: synthesis
compiled_at: {datetime.now().strftime("%Y-%m-%d")}
compiler: claude-sonnet-5
tags:
  - synthesis
  - compiled
---

# {title}

> 跨主题综合页，基于 `60 Knowledge/` 全部知识页提炼。

"""
        out_path = SYNTH_ROOT / f"{slug}.md"
        out_path.write_text(frontmatter + body + "\n", encoding="utf-8")
        print(f"  ✅ 完成: {out_path.name} ({len(body)} 字符)\n")

    print(f"综合页生成完成，输出到 {SYNTH_ROOT}")


if __name__ == "__main__":
    main()
