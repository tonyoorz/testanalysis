---
title: "我本地电脑桌面端的claude 介入了glm51 但是一直报错"
type: knowledge
source: "Codex"
source_file: "10 Sources/raw/conversations/Codex/我本地电脑桌面端的claude-介入了glm5-1-但是一直报错.md"
compiled_at: 2026-07-15
compiler: claude-sonnet-5
tags:
  - compiled-knowledge
---

# 我本地电脑桌面端的claude 介入了glm51 但是一直报错

> 编译自 [[10 Sources/raw/conversations/Codex/我本地电脑桌面端的claude-介入了glm5-1-但是一直报错.md]] 的完整对话。

## 核心问题

用户在本地 macOS 电脑上使用 Claude Desktop 桌面客户端接入智谱 GLM-5.1 模型，持续报错（先是 502 错误，后是 "server is busy"）。用户同时尝试使用第三方工具 **CC Switch**（v3.15.0）来管理 Provider 切换，但配置始终无法生效。核心诉求：让 Claude Desktop 和 Claude Code CLI 都能正常调用智谱 GLM-5.1。

## 关键结论

- **智谱 API 本身正常**：直接调用 `https://open.bigmodel.cn/api/anthropic` 返回 200，GLM-5.1 能正确响应，问题不在 API 侧。
- **Claude Desktop 与 Claude Code CLI 是两套独立配置**，互不影响：
  - Claude Desktop 配置文件：`~/Library/Application Support/Claude/claude_desktop_config.json`
  - Claude Code CLI 配置文件：`~/.claude/settings.json`
- Claude Desktop 默认 `"deploymentMode": "1p"` 表示走官方 Anthropic 服务，需切换为 `"3p"`（第三方）才能走智谱 Gateway。
- 最初报错信息：`API Error: 502 status code (no body)... check your inference gateway (custom-3p-unused. invalid)`，说明 Gateway 配置无效或未正确指向智谱端点。
- **CC Switch 对 Claude Code CLI 的接管是有效的**：通过本地代理模式（`http://127.0.0.1:15721`）接管，`ANTHROPIC_BASE_URL` 指向该代理，代理再转发到智谱 API 并做模型名映射（如 `claude-sonnet-4-6` → `GLM-5.1`），代理调用验证返回 200，工作正常。
- **CC Switch 对 Claude Desktop 的"直接模式"切换持续失败**：数据库里虽然显示 `zhipu-glm` 的 `is_current = 1`，但实际未写入 `claude_desktop_config.json`，配置文件仍停留在 `"deploymentMode": "1p"`；且多次操作后数据库又被切回 `claude-desktop-official` 为 `is_current = 1`，UI 交互与实际生效状态不同步。
- 最终判断：CC Switch 对 Claude Desktop 的自动写入机制存在 bug 或未完全支持，需要手动修改配置文件作为可靠的兜底方案。

## 操作要点

1. **排查报错信息**：从 Claude Desktop 截图中通过 OCR 提取具体错误文本，定位到 Gateway 配置问题。
2. **验证 API 连通性**：直接调用智谱 API 端点确认 Key 与服务可用，排除 API 侧问题。
3. **手动修改 `claude_desktop_config.json`**，关键字段：

| 配置项 | 修改前 | 修改后 |
|---|---|---|
| `deploymentMode` | `"1p"` | `"3p"` |
| `inferenceProvider` | 无 | `"anthropic"` |
| `inferenceGatewayBaseUrl` | 无 | `"https://open.bigmodel.cn/api/anthropic"` |
| `inferenceGatewayApiKey` | 无 | 智谱 API Key |
| `inferenceGatewayAuthScheme` | 无 | `"bearer"` |
| `inferenceModels.sonnet` | 无 | `"GLM-5.1"` |
| `inferenceModels.haiku` | 无 | `"GLM-4.5-air"` |
| `inferenceModels.opus` | 无 | `"GLM-5.1"` |

修改后需**重启 Claude Desktop** 生效。

4. **Claude Code CLI 配置参考**（`~/.claude/settings.json`，CC Switch 代理接管模式下的正确内容）：
```json
{
  "ANTHROPIC_BASE_URL": "http://127.0.0.1:15721",
  "ANTHROPIC_AUTH_TOKEN": "PROXY_MANAGED",
  "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-4-6",
  "ANTHROPIC_DEFAULT_SONNET_MODEL_NAME": "GLM-5.1"
}
```
（若未使用 CC Switch 代理，也可直接配置 `ANTHROPIC_BASE_URL: https://open.bigmodel.cn/api/anthropic` + `ANTHROPIC_AUTH_TOKEN` + `ANTHROPIC_MODEL: GLM-5.1`）

5. **在 CC Switch 中添加自定义 Provider 的步骤**：
   - 打开 CC Switch → 点击"+"新增供应商
   - 填写：供应商名称（如 `Zhipu GLM`）、网站 `https://open.bigmodel.cn`、Base URL `https://open.bigmodel.cn/api/anthropic`、API Key（智谱完整 Key，格式如 `68c4dc9c635543b9b55b8c2ff175f322.b85dLPUROcbXkHDv`，非 `sk-` 开头）
   - API 格式选择 `Anthropic Messages`
   - 配置模型路由映射：Sonnet → `glm-5`，Haiku → `glm-4.5-air`（或 `glm-5`），Opus → `glm-5`
   - 保存后需切换到 **Claude Desktop 标签页**，找到该供应商卡片点击"使用"

## 踩过的坑

- **CC Switch 复制官方 Provider 失败**：尝试复制 "Claude Desktop Official" 这个 provider 创建新配置时报错"添加供应商失败：Claude Desktop"，需改用左侧"+"按钮新建。
- **Computer Use / accessibility tree 交互不稳定**：多次尝试通过自动化点击 CC Switch UI 切换 Provider 标签页和"使用"按钮均失败，accessibility tree 在特定 index（如 index 32-33）处被截断，无法定位第二个 provider 卡片的按钮；截图分辨率过高导致细节难以辨认；坐标点击方案也未验证成功。
- **CC Switch 对 Claude Desktop 的直接模式配置不生效**：数据库层面 `is_current` 标记已切换为 `zhipu-glm`，但实际未写入 `claude_desktop_config.json` 文件；且后续检查发现数据库又自动切回 `claude-desktop-official` 的 `is_current = 1`，怀疑是用户误点或 UI 与后端状态不同步导致的回退。
- **API Key 格式混淆**：用户在 CC Switch 表单中一度填入了 `sk-` 开头的 Key（疑似误填 OpenAI 格式），需要提醒替换为智谱格式的完整 Key。
- **两套配置文件互不生效的认知误区**：一开始误以为修改 `~/.claude/settings.json`（Claude Code CLI 配置）能影响 Claude Desktop GUI，实际两者完全独立，需分别配置。

## 待解决问题

- 最终报错变为 **"server is busy"**（Q9），根本原因未在对话中给出结论——是智谱侧限流/繁忙，还是 CC Switch 代理转发异常，或 Claude Desktop 配置仍未真正切换成功，均未确认。
- CC Switch 对 **Claude Desktop 的 Provider 切换为何持续不写入配置文件 / 为何切换状态会被自动回退**，未查明具体 bug 原因（对话中未涉及最终修复结果）。
- 用户是否已成功在 CC Switch UI 中手动完成"切到 Claude Desktop 标签页 → 点击 Zhipu GLM 供应商 → 点击使用"这一步骤，未见后续确认。
- 是否需要绕过 CC Switch、完全手动维护 `claude_desktop_config.json` 作为长期方案，尚无定论。
