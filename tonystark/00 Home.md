---
title: TonyStark
tags:
  - vault/home
  - second-brain
---

# TonyStark · 第二大脑

> AI 对话知识的持久化 wiki。原始对话经 LLM 编译为结构化知识页，可用自然语言检索与综合。

## 🔍 快速检索
```bash
# 语义检索
gbrain query "你的问题"
# 跨页综合（带引用）
gbrain think "复杂问题" --model openrouter:anthropic/claude-sonnet-5
```

## 📚 知识结构

### 第二大脑入口
- [[30 Topics/Topic Index|主题索引]] — 5 大主题导航
- [[50 Syntheses/PreAnalysis技术债务全景与改进路线|技术债务全景]] — P0/P1/P2 改进路线
- [[50 Syntheses/数据分析系统完整数据流|完整数据流]] — Octane→清洗→存储→展示
- [[50 Syntheses/AI-Agent能力盘点与演进|Agent 能力盘点]] — 现状+30/60/90天演进

### 主题页（LLM 综合生成）
- [[30 Topics/Data-Agent-项目架构|Data-Agent 项目架构]]
- [[30 Topics/数据管道与数据库|数据管道与数据库]]
- [[30 Topics/Agent工具链与环境配置|Agent 工具链与环境配置]]
- [[30 Topics/前端与数据可视化|前端与数据可视化]]
- [[30 Topics/工程治理与环境维护|工程治理与环境维护]]

### 知识页（17 篇，LLM 编译）
- `60 Knowledge/Concepts/` — 概念与架构理解（4 篇）
- `60 Knowledge/Decisions/` — 决策与方案（7 篇）
- `60 Knowledge/Solutions/` — 解决方案与排查（6 篇）

### 工具
- [[40 Tools/Claude Code]] · [[40 Tools/Codex]] · [[40 Tools/OpenClaw]] · [[40 Tools/QClaw]]

## 📂 文件夹约定
| 目录 | 内容 | 数量 |
|------|------|------|
| `10 Sources/` | 原始源（inventory + raw 对话） | — |
| `20 Sessions/` | 有价值 session 原文（≥3轮，可追溯） | 78 |
| `30 Topics/` | 深度主题页（LLM 综合） | 5 |
| `40 Tools/` | AI 工具页 | 7 |
| `50 Syntheses/` | 跨主题综合页 | 3 |
| `60 Knowledge/` | 🆕 编译后的实体知识页 | 17 |

## 🔄 知识编译工作流
1. 原始对话存于 `10 Sources/raw/conversations/`（从 jsonl 提取完整对话）
2. `scripts/compile_all.py` 用 LLM 把对话编译成 `60 Knowledge/` 知识页
3. `scripts/write_topics.py` 综合知识页生成 `30 Topics/` 主题页
4. `scripts/write_syntheses.py` 跨主题综合生成 `50 Syntheses/`
5. `gbrain import` 索引全部内容，支持语义检索与综合问答
