---
title: "我如何在手机上看到我Claude code桌面版编程的进度，所有的对话等等都可以"
type: knowledge
source: "Claude-Code"
source_file: "10 Sources/raw/conversations/Claude-Code/我如何在手机上看到我Claude-code桌面版编程的进度-所有的对话等等都可以看进度包括交互等等-.md"
compiled_at: 2026-07-15
compiler: claude-sonnet-5
tags:
  - compiled-knowledge
---

# 我如何在手机上看到我Claude code桌面版编程的进度，所有的对话等等都可以

> 编译自 [[10 Sources/raw/conversations/Claude-Code/我如何在手机上看到我Claude-code桌面版编程的进度-所有的对话等等都可以看进度包括交互等等-.md]] 的完整对话。

## 核心问题

用户使用 Claude Code 桌面版编程，后台通过 `cc-switch` 代理接入国内 GLM 模型（智谱），希望能在手机上实时查看/参与桌面版 Claude Code 的编程进度和完整交互记录。由于 Claude 官方手机 App 在国内不可用，用户需要寻找并落地一个"最好用的第三方方案"来实现手机端远程监控/操控。

## 关键结论

### 方案调研结果（三次 web_search）

1. **官方 Remote Control 功能**（Anthropic 原生）
   - Claude 始终在本地运行，内容不上云，完整保留上下文
   - 启动方式：命令行参数启动，或在已有会话中输入 `/rc` 直接转移到手机/浏览器
   - 也可通过 `/config` 开启 "Enable Remote Control for all sessions" 让每次会话自动开启
   - 手机端通过 claude.ai/code 或官方 iOS/Android App 连接
   - 已知问题：GitHub Issue #30691（远程会话不显示在手机 App 中，需先配置 SSH + `/config`）；社区反馈长任务建议配合推送通知
   - 文档：https://code.claude.com/docs/zh-CN/remote-control

2. **Happy（slopus/happy，开源，最终选定方案）**
   - 定位：Claude Code / Codex 的移动+网页客户端，"跑在自己的硬件上"，端到端加密，无遥测
   - 核心用法：用 `happy claude` 替代 `claude` 命令（或 `happy codex` 替代 `codex`）启动包装后的会话；手机端接管时会话自动切到远程模式，键盘任意键可切回本机
   - 组件：happy-app（Expo 移动/网页客户端）、happy-cli（命令行入口）、happy-agent（远程 agent 控制 CLI）、happy-server（加密同步后端）
   - 安装：`npm install -g happy`（原包名 `happy-coder`，已迁移为 `happy`）
   - 仓库：https://github.com/slopus/happy ，官网 https://happy.engineering/

3. **SSH 自建方案**：Termius/Termux + SSH 直连远程主机跑 Claude Code；Claude Code 桌面版已原生支持 SSH，不再依赖 TMUX
4. **tmate/ttyd 中继方案**：把终端搬到浏览器/手机，需自建中继服务器规避第三方依赖
5. **GLM/AutoGLM 相关**：智谱 Coding Tool Helper 可将 GLM 编码套餐接入 Claude Code；AutoGLM/Open-AutoGLM 可通过 WiFi 远程 ADB/HDC 把手机变成"AI 手机"（与本次核心需求关联度较低，作为补充信息）

### 环境现状（排查所得）

- Node `v22.22.3`，npm `10.9.8`，`claude` 位于 `/opt/homebrew/bin/claude`
- Claude Code 版本：`2.1.63`
- 桌面版通过 **cc-switch** 工具管理多套 API 配置，环境变量：
  - `ANTHROPIC_BASE_URL=http://127.0.0.1:15721`（本地代理端口，cc-switch 进程监听，PID 48557）
  - `ANTHROPIC_AUTH_TOKEN=PROXY_MANAGED`
  - `ANTHROPIC_DEFAULT_OPUS_MODEL_NAME=GLM-5.2`（映射 `claude-opus-4-8[1M]`）
  - `ANTHROPIC_DEFAULT_SONNET_MODEL_NAME=GLM-5.1`（映射 `claude-sonnet-4-6[1M]`）
  - `ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME=glm-5`
- cc-switch 相关文件：`~/.cc-switch/settings.json`、`~/.cc-switch/cc-switch.db`、`~/.cc-switch/logs/cc-switch.log`、`~/.cc-switch/backups/`
- `~/.claude-code-router` 目录不存在（未使用 claude-code-router 方案）
- Node 全局包路径为 `/Users/tonyorz/.hermes/node/lib/node_modules`

## 操作要点

1. 安装 Happy CLI：
   ```bash
   npm install -g happy
   ```
   该命令在后台任务中执行（task id `bfhyd5pwp`），耗时约 8 分钟，成功安装 312 个包（`added 312 packages in 8m`，exit_code 0）
2. 安装后确认 npm bin 目录下已生成符号链接：
   ```
   happy -> ../lib/node_modules/happy/bin/happy.mjs
   happy-mcp -> ../lib/node_modules/happy/bin/happy-mcp.mjs
   ```
3. 后续用法（按官方 README）：日常用 `happy claude` 替代 `claude` 启动会话，手机端接管时会话自动转远程模式，按键盘任意键切回本机控制

## 踩过的坑

- **`happy: command not found`**：npm 全局安装成功、符号链接已生成，但 shell 无法识别 `happy` 命令，根本原因指向 **PATH 未包含 Node 全局 bin 目录**（`/Users/tonyorz/.hermes/node/lib/node_modules` 所在的 bin 路径未在 `.zshrc`/`.bash_profile` 中配置）。检查 `.bash_profile` 后发现该文件中配置了大量其他工具的 PATH（Python、conda、opencode、Docker、CodeBuddy、Antigravity、Windsurf 等），但未见 hermes node 对应路径的导出语句。
- 用户环境中存在多套 AI CLI 工具共存（opencode、codex、codebuddy、openclaw、antigravity 等），PATH 配置较为复杂，增加了排查难度。

## 待解决问题

- **PATH 问题尚未修复**：对话在排查 `happy` 命令为何找不到时被截断，尚未确认最终是否将 hermes node 的全局 bin 路径正确加入 PATH，也未验证 `happy claude` 是否能成功启动并联动手机端 App。
- 未验证 Happy 客户端（iOS/Android App 或 Web App）与本机 `happy` CLI 之间的配对/连接流程是否顺利。
- 未确认 Happy 方案与当前 cc-switch + GLM 代理（`http://127.0.0.1:15721`）组合使用时是否存在兼容性问题。
- 官方 Remote Control 方案（`/rc`、`/config`）作为备选方案未在本次会话中实际测试。
