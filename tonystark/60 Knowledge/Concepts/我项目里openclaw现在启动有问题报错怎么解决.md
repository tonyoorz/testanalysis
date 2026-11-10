---
title: "我项目里openclaw现在启动有问题报错怎么解决"
type: knowledge
source: "Codex"
source_file: "10 Sources/raw/conversations/Codex/我项目里openclaw现在启动有问题报错-Image-1-怎么解决.md"
compiled_at: 2026-07-15
compiler: claude-sonnet-5
tags:
  - compiled-knowledge
---

# 我项目里openclaw现在启动有问题报错怎么解决

> 编译自 [[10 Sources/raw/conversations/Codex/我项目里openclaw现在启动有问题报错-Image-1-怎么解决.md]] 的完整对话。

## 核心问题
OpenClaw 项目启动/运行报错及后续配置问题，主要包括：
1. 启动报错 `No API key found for provider "anthropic"`，实际用户想用 Kimi/Moonshot 模型
2. WebSocket 连接被拒绝、设备配对未完成导致 dashboard 显示离线
3. Moonshot API Key 配置多次尝试后仍返回 `HTTP 401: Invalid Authentication`
4. Kimi 兼容 OpenAI 的 base URL 该用哪个存在疑惑（Moonshot vs Kimi Coding 两套体系混淆）
5. OpenClaw 如何接入微信/飞书，实现手机远程聊天控制
6. OpenClaw 模型知识只到 2024 年，是否需要装 skill 才能获取最新信息，以及批量安装热门 skill

## 关键结论
- **启动报错根因不是服务未启动**，而是设备配对问题：日志出现 `code=1008 reason=pairing required` / `device signature expired`，网关容器本身是健康的。
- Anthropic 报错是因为默认模型走 `anthropic` provider 但无可用 key，与"连上 dashboard"是两个独立问题。
- **Moonshot 与 Kimi Coding 是两套完全不同的体系**，不能混用 key：
  - **Moonshot（OpenAI 兼容）**：环境变量 `MOONSHOT_API_KEY`，模型 `moonshot/kimi-k2-turbo-preview`（或 `moonshot/kimi-k2.5`），baseUrl `https://api.moonshot.cn/v1`
  - **Kimi Coding（Anthropic 兼容）**：环境变量 `KIMI_API_KEY`，模型 `kimi-coding/k2p5`，baseUrl `https://api.kimi.com/coding/`
  - 用户最初把 `sk-kimi-...`（Kimi Code 的 key）当成 `MOONSHOT_API_KEY` 使用，导致持续 401
- 多轮 401 报错最终定位为 **key 本身无效**（不是配置路径问题），排查方式是直接在宿主机用 `curl` 打 Moonshot 官方接口验证，绕开 OpenClaw 配置层。
- **Skill 不能解决模型知识过时问题**：skill 只提供流程/工具能力，不会刷新模型训练数据；获取最新信息核心靠联网检索（web search）+ 模型/API 可用。
- OpenClaw 自带 `feishu` 插件（社区维护版），但存在依赖缺失问题；另有社区包 `@m1heng-clawd/feishu` 可安装，落地目录为 `/Users/tonyorz/.openclaw/extensions/feishu`。
- 已批量安装 OpenAI curated 全量 30 个热门 skill，包括 `playwright`、`pdf`、`screenshot`、`spreadsheet`、`speech`、`transcribe`、`openai-docs`、`security-*`、`vercel-deploy` 等。

## 操作要点
**设备配对修复：**
```bash
docker compose exec -T openclaw-gateway openclaw devices list
docker compose exec -T openclaw-gateway openclaw devices approve --latest
```
（可重复执行到 Pending 为 0），之后刷新 `http://127.0.0.1:18789/overview` 查看是否从 Health Offline 变在线。

**切换默认模型为 Moonshot：**
- 修改文件：`/Users/tonyorz/.openclaw/openclaw.json:9`（默认模型设为 `moonshot/kimi-k2.5`）、`:12`（模型白名单只保留 Moonshot）、`:21`
- 修改 `/Users/tonyorz/openclaw-docker/.env:10` 中的 `MOONSHOT_API_KEY`
- 重启网关：`docker compose up -d --force-recreate openclaw-gateway`

**验证配置是否生效：**
```bash
docker compose exec -T openclaw-gateway openclaw models status --probe --probe-provider moonshot --json
docker compose exec -T openclaw-gateway openclaw agent --agent main -m "回复ok" --json
```

**本地验证 key 是否有效（绕开 OpenClaw 排查）：**
```bash
curl -sS https://api.moonshot.cn/v1/models -H "Authorization: Bearer <key>"
```
返回 models 列表说明 key 没问题。

**安装飞书插件：**
```
openclaw plugins install @m1heng-clawd/feishu
```

**安装 skill 后需重启 Codex 以生效**（Restart Codex to pick up new skills）。

## 踩过的坑
- **手动输入 API Key 容易把 `I/l/1` 混淆**：用户发的 key 是 `...QX17IidQ`，截图里实际是 `...QX17lidQ`（小写 L），导致密钥判定无效。正确做法是用平台弹窗的"复制"按钮，不要手打。
- **把 Kimi Code 的 key（`sk-kimi-...`）当作 Moonshot 通用 key（`MOONSHOT_API_KEY`）使用**，导致持续 401，因为两者是不同体系、不同 endpoint。
- 多次更换 key 仍 401，最终确认是 **Moonshot 账号侧问题**（如未完成身份验证），而非本地配置问题；需在 Moonshot 平台点击"验证你的身份"并重新生成 key。
- **在聊天中明文发送过 API Key**，属于安全隐患，助手提醒应把已泄露的旧 key 全部删除重建。
- 误以为 skill 能解决"模型知识只到 2024 年"问题，实际 skill 与知识库更新无关，需要联网检索能力。

## 待解决问题
- 用户最终选择用哪一套（Moonshot 还是 Kimi Coding）以及是否切换到 `kimi-coding/k2p5`，对话中未给出最终确认结果（A6 中助手表示"你要的话我可以现在直接帮你切成 Kimi Coding 这套"，但未见用户后续回复）。
- 微信接入方案（对话中未涉及，仅讨论了飞书）。
- feishu 插件依赖缺失问题的具体修复（助手提出"检查并修复 feishu 插件依赖加载"作为下一步，但对话中未见执行结果）。
- 批量安装的 30 个 skill 是否全部验证可用（对话中未涉及具体验证过程）。
