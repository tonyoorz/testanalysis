---
title: "Conversation info untrusted metadata jso"
type: knowledge
source: "QClaw"
source_file: "10 Sources/raw/conversations/QClaw/Conversation-info-untrusted-metadata-json-message_.md"
compiled_at: 2026-07-15
compiler: claude-sonnet-5
tags:
  - compiled-knowledge
---

# Conversation info untrusted metadata jso

> 编译自 [[10 Sources/raw/conversations/QClaw/Conversation-info-untrusted-metadata-json-message_.md]] 的完整对话。

## 核心问题

用户长时间与 AI 助手协作，对 Mac 电脑进行磁盘空间清理与优化，涵盖：AI 大模型文件（Ollama/HuggingFace）、Downloads 下载文件、开发工具缓存（JetBrains/npm/Docker/pip/Homebrew）、大型软件（Parallels/Windows 虚拟机）、重复文件、大项目文件夹（aianalysis/LLaMA-Factory/dify）、数据库备份等。后期话题转向在 Claude Code 中安装配置第三方扩展工具（claude-hud、openclaw-weixin-cli）。

## 关键结论

**已确认删除并释放的空间（用户明确执行）：**

| 清理轮次 | 内容 | 释放空间 |
|---|---|---|
| Ollama 模型 | `llama3:8b`(4.7GB,12月未用) + `qwen3:0.6b`(522MB,6月未用) | 5.2 GB |
| Downloads 压缩包/DMG | `PYQT 2.zip`(381MB)、`TM_DM_Jupyter_pygwalker.zip`(290MB)、`QClaw-0.1.12-5001-57-arm64.dmg`(164MB)、`dify-for-dsl-20250611-main.zip`(164MB)、`TM_DM_Jupyter.zip`(68MB)、`awesome-claude-skills-master.zip`(3.3MB)、`skills-main.zip`(3.2MB) | 1.07 GB |
| JetBrains 缓存 + Steam App Support | — | 3.3 GB |
| npm 缓存 + 开发残留 | npm缓存(3.7GB)、Codeium(826MB)、Chromium旧快照(348MB)、EasyOCR模型(100MB)、PyOctane .venv(36MB) | ~5.0 GB |
| 软件卸载 | Windows 10.pvm(38GB,2025-09未用)、ClashX(47MB) 已成功移至废纸篓 | ~38 GB+ |

**累计释放（用户明确汇总）：约 54 GB**

**保留的模型：** `qwen3-embedding:latest`（4.7GB，6周前用过，仍活跃）

**待用户确认是否删除的大项目/资源（尚未执行）：**
- `~/aianalysis/`（30GB，最后活跃2025-06）
- `~/LLaMA-Factory
