---
title: "codex windows桌面版下载"
type: knowledge
source: "Claude-Code"
source_file: "10 Sources/raw/conversations/Claude-Code/codex-windows桌面版下载.md"
compiled_at: 2026-07-15
compiler: claude-sonnet-5
tags:
  - compiled-knowledge
---

# codex windows桌面版下载

> 编译自 [[10 Sources/raw/conversations/Claude-Code/codex-windows桌面版下载.md]] 的完整对话。

## 核心问题
用户询问如何下载 Codex（OpenAI 的 AI 编程助手）的 Windows 桌面版，并进一步明确需要 x64 架构版本。

## 关键结论
- Codex 桌面版（Codex Desktop App / Codex app）是 OpenAI 推出的 AI 编程助手桌面应用，支持 macOS 和 Windows 平台。
- Windows 版官方推荐下载渠道是 **Microsoft Store**（微软应用商店），链接：`https://apps.microsoft.com/detail/9plm9xgg6vks?hl=zh-CN&gl=CN`。
- 官方文档地址：`https://developers.openai.com/codex/app/windows`（Windows 专属说明）与 `https://developers.openai.com/codex/app`（总览，含 macOS/Windows 下载入口）。
- Windows 系统要求：Windows 10 版本 19041.0 或更高版本。
- 命令行安装方式：
  ```
  winget install Codex -s msstore
  ```
- 更新方式：打开 Microsoft Store → Downloads → Check for updates。
- 企业部署：管理员可通过 Microsoft Store app distribution 结合企业管理工具批量部署。
- Codex 桌面版在 Windows 上原生运行于 PowerShell，并使用 **Windows sandbox**；也可配置运行在 **WSL2**（Windows Subsystem for Linux 2）中，使用 Linux sandbox（`bubblewrap`）。
  - WSL1 仅在 Codex 0.114 之前支持，0.115 起 Linux sandbox 迁移到 `bubblewrap`，不再支持 WSL1。
- 若已使用过 Codex CLI，桌面版通常会直接读取已有配置，无需重复设置。
- Codex 主目录（Codex home directory）：Windows 应用与原生 Windows Codex 共用 `%USERPROFILE%\.codex`；WSL 内的 CLI 默认使用 Linux 主目录，不会自动与 Windows 应用共享配置/缓存认证/会话历史，可通过设置 `CODEX_HOME` 环境变量（如 `export CODEX_HOME=/mnt/c/Users/<windows-user>/.codex`）实现共享。
- 也存在非 Microsoft Store 的替代下载/构建方式（如 GitHub Release 二进制、社区教程"从零构建"含安装包），来源于第三方博客（CSDN、loongphy.com 等），非官方首选路径。
- GitHub 仓库发布地址：`https://github.com/openai/codex/releases`（含 CLI 二进制及版本更新日志，如 0.129.0 版本包含大量 Windows sandbox、ConPTY、named pipe、PowerShell 执行规则等修复）。

## 操作要点
1. **推荐安装路径**：在 Microsoft Store 搜索 "Codex" 或直接访问商店详情页下载安装。
2. **命令行安装**：`winget install Codex -s msstore`
3. **切换代理运行模式（Windows Native vs WSL2）**：
   - 打开 Codex 应用 __Settings__，将 agent 从 Windows native 切换为 WSL，然后 __restart the app__（重启后生效，项目保持不变）。
4. **配置 sandbox 权限**：在 Composer 中发送消息前，将 sandbox permissions 设置为 __Default permissions__ 以启用沙箱保护。
5. **添加 WSL 文件系统项目**：点击 __Add new project__ 或按 `Ctrl+O`，在文件浏览器输入 `\\wsl$\` 选择 Linux 发行版及目标文件夹。若使用 Windows-native agent，建议项目存放在 Windows 文件系统，通过 `/mnt/<drive>/...` 从 WSL 访问，比直接从 WSL 文件系统打开更可靠。
6. **常用开发工具安装（通过 winget）**：
   ```
   winget install --id Git.Git
   winget install --id OpenJS.NodeJS.LTS
   winget install --id Python.Python.3.14
   winget install --id Microsoft.DotNet.SDK.10
   winget install --id GitHub.cli
   ```
   安装 GitHub CLI 后运行 `gh auth login` 启用 GitHub 功能。
7. **以管理员权限运行**：需要 Codex 以提升权限运行命令时，在开始菜单找到 Codex，选择"以管理员身份运行"，Codex agent 会继承该权限级别。
8. **PowerShell 执行策略问题修复**：
   ```
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned
   ```
9. **配置默认编辑器/终端**：可在应用设置中选择默认 __Open__ 应用（Visual Studio、VS Code 等，可按项目覆盖）及默认集成终端（PowerShell / Command Prompt / Git Bash / WSL），终端切换仅对新会话生效，需重启应用或新建 thread。

## 踩过的坑
- `npm.ps1 cannot be loaded because running scripts is disabled on this system.` —— PowerShell 执行策略限制导致 Node.js/npm 脚本无法运行，需调整执行策略为 `RemoteSigned`。
- WSL1 已不再受支持（自 Codex 0.115 起，因 Linux sandbox 迁移至 `bubblewrap`）。
- 若直接从 WSL 文件系统（`\\wsl$\`）打开项目并使用 Windows-native agent，可靠性不如将项目放在 Windows 文件系统再通过 `/mnt/<drive>/...` 从 WSL 访问。
- WSL 内的 Codex CLI 默认不会自动与 Windows 桌面应用共享配置、缓存认证、会话历史，需手动同步 `~/.codex` 或设置 `CODEX_HOME` 指向 Windows 目录。
- 切换 agent 运行模式（Windows native ↔ WSL）后必须重启应用才能生效，仅切换设置不会立即生效。
- 终端默认设置变更仅对新开的集成终端会话生效，已打开的终端不会自动切换。

## 待解决问题
- 对话内容被截断，Q6 之后助手的具体回答（针对 x64 版本的最终下载指引、是否需要区分 Intel/ARM64 构建等）未完整呈现，（对话中未涉及）。
- Codex 桌面版具体版本号与用户最终采用的下载方式（Microsoft Store vs GitHub Release 二进制 vs 第三方构建教程）未在对话中明确确认，（对话中未涉及）。
- API Key 配置、中文界面设置等后续使用步骤未在提供的对话片段中展开，（对话中未涉及）。
