---
title: "我本地的cli上的hermes agent 的模型可以改成model可以改成mo"
type: knowledge
source: "Claude-Code"
source_file: "10 Sources/raw/conversations/Claude-Code/我本地的cli上的hermes-agent-的模型可以改成model可以改成modelscope的么.md"
compiled_at: 2026-07-15
compiler: claude-sonnet-5
tags:
  - compiled-knowledge
---

# 我本地的cli上的hermes agent 的模型可以改成model可以改成mo

> 编译自 [[10 Sources/raw/conversations/Claude-Code/我本地的cli上的hermes-agent-的模型可以改成model可以改成modelscope的么.md]] 的完整对话。

## 核心问题

用户希望将本地 Hermes CLI Agent（`hermes` 命令，配置目录 `/Users/tonyorz/.hermes/`）的模型提供方从当前的 Zhipu/GLM 配置改为使用 ModelScope 提供的 API（Key: `ms-b5f5d089-754f-499d-9628-b6e47b5682b1`，模型 `ZhipuAI/GLM-5.1`，参考 ModelScope 官方 Anthropic 兼容 SDK 示例），并在过程中因多次配置错误反复调整，最终发现用户实际使用的是 Zhipu **coding plan**（GLM Coding Plan），其正确配置方式与直接调用 `bigmodel.cn` 标准 API 或 ModelScope 均不同。

## 关键结论

- Hermes Agent 的模型/提供方配置存放在两处：
  - `/Users/tonyorz/.hermes/config.yaml`（模型选择、`custom_providers` 列表等结构化配置）
  - `/Users/tonyorz/.hermes/.env`（各 Provider 的 API Key、Base URL 等敏感信息）
- 初始配置（改前）：
  ```yaml
  model:
    default: glm-5.1
    provider: zai
    base_url: https://open.bigmodel.cn/api/paas/v4
  ```
  对应 `.env` 中 `GLM_API_KEY` / `GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4`
- 尝试改为 ModelScope 后（`provider: zai`, `model: ZhipuAI/GLM-5.1`, `base_url: https://api-inference.modelscope.cn`），运行 `hermes chat` 报错 **HTTP 404 page not found**，说明该 base_url/model 组合不被 zai provider 预设正确解析。
- 用户指出应改回与 Claude Code 中使用的 Zhipu 配置一致（而非 ModelScope），改回 `https://open.bigmodel.cn/api/paas/v4` + `model: glm-5.1` 后，报错变为 **HTTP 429**：`余额不足或无可用资源包,请充值`（`code: 1113`）。
- 用户澄清自己使用的是 **Zhipu Coding Plan**（编程套餐），其正确配置与标准 `paas/v4` API 完全不同，需要参照 Claude Code 的实际生效配置：
  ```json
  {
    "env": {
      "ANTHROPIC_AUTH_TOKEN": "68c4dc9c635543b9b55b8c2ff175f322.b85dLPUROcbXkHDv",
      "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
      "ANTHROPIC_DEFAULT_HAIKU_MODEL": "GLM-4.5-air",
      "ANTHROPIC_DEFAULT_OPUS_MODEL": "GLM-5.1",
      "ANTHROPIC_DEFAULT_SONNET_MODEL": "GLM-5.1",
      "ANTHROPIC_MODEL": "GLM-5.1",
      "API_TIMEOUT_MS": "3000000",
      "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
      "DISABLE_ERROR_REPORTING": "1",
      "DISABLE_TELEMETRY": "1"
    }
  }
  ```
  关键区别：Coding Plan 使用的是 **`/api/anthropic`** 端点（Anthropic 兼容协议），而非 `/api/paas/v4`（标准 Zhipu API），且鉴权用 `ANTHROPIC_AUTH_TOKEN` 而非普通 `GLM_API_KEY`。
- Hermes 安装路径为 `/Users/tonyorz/.local/bin/hermes`，Agent 主体安装在 `/Users/tonyorz/.hermes/hermes-agent`。
- Hermes CLI 顶层子命令包括：`chat, model, gateway, setup, whatsapp, login, logout, auth, status, cron, webhook, doctor, dump, debug, backup, import, config, pairing, skills, plugins, memory, tools, mcp, sessions, insights, claw, version, update, uninstall, acp, profile, completion, dashboard, logs`（**无 `desktop` 子命令**）。
- `hermes config` 下有子命令：`show, edit, set, path, env-path, check, migrate`。
- `hermes model` 命令用于交互式选择 inference provider 与默认模型，支持 `--portal-url`、`--inference-url`、`--client-id`、`--scope`、`--no-browser`、`--timeout`、`--ca-bundle`、`--insecure` 等参数（主要面向 Nous OAuth 登录流程）。

## 操作要点

1. 查看当前配置：`hermes config show`
2. 定位配置文件路径：`hermes config path`（→ `/Users/tonyorz/.hermes/config.yaml`）与 `hermes config env-path`（→ `/Users/tonyorz/.hermes/.env`）
3. 修改 `config.yaml` 中 `model.provider` / `model.default` / `model.base_url` 字段以切换模型提供方
4. 在 `.env` 中对应设置该 provider 的 API Key 及 Base URL（如 `GLM_API_KEY`、`GLM_BASE_URL`）
5. `config.yaml` 支持 `custom_providers` 列表自定义 OpenAI-compatible 端点，字段包括 `name`、`base_url`、`api_key`、`api_mode`（如 `chat_completions`），当前配置中已有 `moonshot`、`volcengine`、`qclaw` 等自定义 provider 示例（注：该列表中 moonshot/volcengine/qclaw 各出现重复两次）
6. 修改后需重新运行 `hermes chat` 验证是否生效
7. 若使用 Zhipu Coding Plan，应比照 Claude Code 生效配置，使用 `ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic` + `ANTHROPIC_AUTH_TOKEN` 的方式配置，而非标准 `paas/v4` 端点（对话中未给出在 Hermes `config.yaml`/`.env` 中具体如何映射为 anthropic 兼容模式的最终操作步骤）

## 踩过的坑

- `hermes desktop` 不是合法子命令，导致执行报错（正确命令集见上）
- 将 `provider: zai` 搭配 ModelScope 的 `base_url: https://api-inference.modelscope.cn` 及 `model: ZhipuAI/GLM-5.1` 直接使用，报 **HTTP 404**（该 provider 预设与 ModelScope 端点/模型命名不兼容）
- 改回 `https://open.bigmodel.cn/api/paas/v4` + `glm-5.1` 后报 **HTTP 429（余额不足或无可用资源包,请
