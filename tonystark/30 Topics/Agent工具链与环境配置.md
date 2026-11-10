---
title: "Agent 工具链与环境配置"
type: topic
description: "AI Agent 工具（Hermes/OpenClaw/Claude Code/Codex）的配置、模型切换、报错排查"
page_count: 13
compiled_at: 2026-07-15
compiler: claude-sonnet-5
tags:
  - topic
  - compiled
---

# Agent 工具链与环境配置

> AI Agent 工具（Hermes/OpenClaw/Claude Code/Codex）的配置、模型切换、报错排查。综合 13 篇知识页。

## 主题概述

本主题汇总了在搭建、配置和维护 AI Agent 开发环境过程中遇到的各类工具链问题，涵盖模型 Provider 接入配置（Hermes CLI、Claude Desktop、OpenClaw）、Skill 生态安装与管理、Git 版本控制工作流、桌面/移动端协同方案，以及在此基础上进行的 Agent 架构设计与技术选型决策。这些知识页反映了从底层环境配置踩坑到上层架构决策的完整链路。

## 核心知识

### 模型 Provider 配置：多套体系易混淆

这是本主题中反复出现的高频痛点，多个知识页独立踩坑，最终共同揭示了国内大模型接入 Claude 系工具的复杂性：

**Zhipu/GLM 接入存在两套完全不同的体系**：
- 标准 API：`base_url: https://open.bigmodel.cn/api/paas/v4`，走普通计费
- **GLM Coding Plan（编程套餐）**：需使用 Anthropic 兼容端点 `https://open.bigmodel.cn/api/anthropic`，配置示例（来自 Claude Code 实际生效配置）：
  ```json
  {
    "env": {
      "ANTHROPIC_AUTH_TOKEN": "68c4dc9c...",
      "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
      "ANTHROPIC_DEFAULT_HAIKU_MODEL": "GLM-4.5-air",
      "ANTHROPIC_DEFAULT_OPUS_MODEL": "GLM-5.1"
    }
  }
  ```
- 在 Hermes CLI（配置文件 `/Users/tonyorz/.hermes/config.yaml` + `.env`）中误用标准 API 或 ModelScope 端点均报错（404 / 429 余额不足），根因是**用户实际购买的是 Coding Plan，套餐与标准 API 计费池不互通**。

**Moonshot 与 Kimi Coding 是两套完全不同的体系**（OpenClaw 场景踩坑）：
- **Moonshot（OpenAI 兼容）**：环境变量 `MOONSHOT_API_KEY`，模型 `moonshot/kimi-k2-turbo-preview`，`baseUrl: https://api.moonshot.cn/v1`
- **Kimi Coding（Anthropic 兼容）**：环境变量 `KIMI_API_KEY`，模型 `kimi-coding/k2p5`，`baseUrl: https://api.kimi.com/coding/`
- 用户曾将 Kimi Code 的 key（`sk-kimi-...`）误当 `MOONSHOT_API_KEY` 使用，持续报 401；最终通过 `curl` 直接打官方接口绕开配置层验证 key 有效性，才定位到 key 本身无效而非配置路径问题。

**Claude Desktop 与 Claude Code CLI 是两套独立配置，互不影响**：
- Claude Desktop：`~/Library/Application Support/Claude/claude_desktop_config.json`，默认 `"deploymentMode": "1p"`（走官方 Anthropic），需手动改为 `"3p"` 才能走第三方 Gateway
- Claude Code CLI：`~/.claude/settings.json`
- 第三方工具 **CC Switch**（v3.15.0）对 CLI 的接管有效（本地代理 `http://127.0.0.1:15721`，做模型名映射如 `claude-sonnet-4-6` → `GLM-5.1`），但对 Desktop 的"直接模式"切换存在 bug：数据库显示已切换但配置文件未同步写入，需**手动改配置文件作为可靠兜底**。

### Skill 生态：安装、局限与批量管理

- **skill-installer** 工具用于对比官方精选库与 GitHub 高热度 skill，决策依据是 Star 数与工作流完整度（如 `anthropics/skills` 下 `pptx` skill，16.1 万 Star，覆盖创建/编辑/模板/渲染/QA 全流程），安装路径固定在 `/Users/tonyorz/.codex/skills/<name>/SKILL.md`。
- **OpenClaw 已批量安装 30 个 OpenAI curated 热门 skill**，包括 `playwright`、`pdf`、`screenshot`、`spreadsheet`、`speech`、`transcribe`、`openai-docs`、`security-*`、`vercel-deploy` 等。
- **关键认知边界**：Skill 无法解决模型知识过时问题——skill 只提供流程/工具能力，不会刷新模型训练数据；获取最新信息核心依赖联网检索（web search），不是靠装 skill。
- OpenClaw 微信/飞书接入：自带 `feishu` 插件（社区维护版，存在依赖缺失），备选社区包 `@m1heng-clawd/feishu`，落地目录 `/Users/tonyorz/.openclaw/extensions/feishu`。

### Git 工作流与代码安全加固

- Data-Agent 仓库分支管理案例：本地分支与其对应远端分支同步（0 ahead/0 behind）**不代表是仓库最新分支**，需 `git branch -a` 遍历比对所有分支时间线，避免误判"已是最新"。
- 该案例中同步暴露了**分支分叉风险**：新分支近期提交（dashboard analytics、qgate refresh 等）与旧分支工作方向差异很大，说明旧分支的安全加固改动不一定存在于新分支，切换分支后需重新核实关键改动是否合并。
- **代码沙箱分层防御设计**（`agent/interpret/code_interpreter.py`）：从子串黑名单升级为四层防御：
  1. AST 静态分析（`_SafetyVisitor` 类）拦截非法 import、dunder 内省链、危险内置名
  2. 运行时受限 `__builtins__`，`__import__` 替换为白名单守卫版本
  3. `resource.setrlimit` 做 OS 资源限制（CPU、文件写入、地址空间）
  4. 最小化子进程环境（清空环境变量、`-E`、临时 `cwd`）
  - 提交 `8c920089`：297 insertions / 87 deletions，commit message `P1-9: Harden code interpreter security (AST + restricted builtins + resource limits)`
  - 原黑名单方案（`FORBIDDEN_PATTERNS` 子串匹配，如禁止 `"open("`, `"__import__"`）易被 `__builtins__`、`getattr` 等手法绕过，仅适用于可信单用户场景，是本次加固的直接动因。

### 桌面客户端与移动端协同

- **Codex 桌面版**（Windows）官方渠道为 Microsoft Store，`winget install Codex -s msstore`；Windows sandbox 原生运行 PowerShell，也可配置在 WSL2 中用 Linux sandbox（`bubblewrap`，0.115 起不再支持 WSL1）；主目录 `%USERPROFILE%\.codex`，WSL 内 CLI 默认用 Linux 主目录，需设置 `CODEX_HOME` 才能与 Windows 应用共享配置。
- **Claude Code 手机端远程监控**方案调研与选型：
  - 官方 Remote Control：`/rc` 命令或 `/config` 开启"Enable Remote Control for all sessions"，本地运行不上云；已知 issue：远程会话不显示在手机 App（需先配置 SSH）
  - **Happy（slopus/happy，最终选定）**：开源、端到端加密、无遥测，用 `happy claude` 包装原生 `claude` 命令启动，手机端接管自动切远程模式；`npm install -g happy`（原名 `happy-coder`）
  - 备选：SSH 直连（Termius/Termux）、tmate/ttyd 中继（需自建）
  - 环境依赖：Node `v22.22.3`、npm `10.9.8`、Claude Code `2.1.63`

### Agent 架构设计与技术选型（Data-Agent 项目）

- **架构定位**：非简单"LLM + 向量库"，而是理解层（term_resolver→entity_extractor→intent_detector）→ SQL生成（3条候选路径：Direct/Decomposed/PlanBased）→ 多路径执行比对（UNANIMOUS 0.95/MAJORITY 0.80/DISAGREE仲裁）→ 自修正（QueryFixer）→ 结果校验（ResultValidator）→ 叙事生成（Storyteller）。
- **Ontology 是全局单一事实来源**：`agent/ontology/objects/*.yaml`，驱动 schema、别名解析、类别分组、业务规则、治理约束。
- **降级设计彻底**：所有依赖 LLM 的路径均有规则回退，可完全离线运行（意图/实体提取纯正则、SQL 模板化、code interpreter 有 `_fallback_code`）。
- **主 Agent Runtime 选型决策**（架构规格文档：`/Users/tonyorz/Data-Agent/docs/super
## 知识页索引
- [[gitgithubcomtonyoorzData-Agentgit-我本地这个d|gitgithubcomtonyoorzData-Agentgit 我本地这个d]]
- [[skill-installerUserstonyorzcodexskillssy|skill-installerUserstonyorzcodexskillssy]]
- [[我本地的cli上的hermes-agent-的模型可以改成model可以改成mo|我本地的cli上的hermes agent 的模型可以改成model可以改成mo]]
- [[我项目里openclaw现在启动有问题报错怎么解决|我项目里openclaw现在启动有问题报错怎么解决]]
- [[Conversation-info-untrusted-metadata-jso-Conversa|Conversation info untrusted metadata jso]]
- [[Conversation-info-untrusted-metadata-jso|Conversation info untrusted metadata jso]]
- [[Successfully-changed-chat-title-to-Casua|Successfully changed chat title to Casua]]
- [[pgsql迁移与字段匹配|我现在pqsql 和sqlite一样看一下里边数据存储字段是匹配的么。 我想确保我之后迁移到pqsq]]
- [[我本地电脑桌面端的claude-介入了glm51-但是一直报错|我本地电脑桌面端的claude 介入了glm51 但是一直报错]]
- [[60 Knowledge/Solutions/codex-windows桌面版下载|codex windows桌面版下载]]
- [[goal-全网深度分析我的项目里的agent-分析一下我这个智能问数agent如|goal 全网深度分析我的项目里的agent，分析一下我这个智能问数agent如]]
- [[60 Knowledge/Solutions/前段设计还能更好么|前段设计还能更好么]]
- [[我如何在手机上看到我Claude-code桌面版编程的进度-所有的对话等等都可以|我如何在手机上看到我Claude code桌面版编程的进度，所有的对话等等都可以]]

