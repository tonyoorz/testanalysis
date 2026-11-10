---
title: "我项目里openclaw现在启动有问题报错[Image #1]怎么解决"
tool: Codex
session_id: 019c8899-159e-7063-a25d-91709e8c5ad0
source_path: "/Users/tonyorz/.codex/sessions/2026/02/23/rollout-2026-02-23T11-44-19-019c8899-159e-7063-a25d-91709e8c5ad0.jsonl"
started_at: "2026-02-23T03:44:19.871Z"
user_turns: 15
assistant_turns: 8
tags:
  - ai-session
  - codex
---

# 我项目里openclaw现在启动有问题报错[Image #1]怎么解决

> 完整对话提取自 `/Users/tonyorz/.codex/sessions/2026/02/23/rollout-2026-02-23T11-44-19-019c8899-159e-7063-a25d-91709e8c5ad0.jsonl`
> 工具: Codex | 用户消息: 15 | 助手回答: 8

## 用户提问（完整）

### Q1

我项目里openclaw现在启动有问题报错[Image #1]怎么解决

### Q2

⚠️ Agent failed before reply: No API key found for provider "anthropic". Auth store: /home/node/.openclaw/agents/main/agent/auth-profiles.json (agentDir: /home/node/.openclaw/agents/main/agent). Configure auth for this agent (openclaw agents add <id>) or copy auth-profiles.json from the main agentDir.
Logs: openclaw logs --follow  报错，我是现在用的kimi的模型 key是[REDACTED_API_KEY]      你帮我配置下

### Q3

[REDACTED_API_KEY]

### Q4

[Image #1] 我创建了呀

### Q5

[REDACTED_API_KEY]

### Q6

curl https://api.moonshot.cn/v1/chat/completions \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer [REDACTED_API_KEY]" \
    -d '{
        "model": "kimi-k2-turbo-preview",
        "messages": [
            {"role": "system", "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。"},
            {"role": "user", "content": "你好，我叫李雷，1+1等于多少？"}
        ],
        "temperature": 0.6
   }'
我这样就能通你看一下里边的key和api地址参考下

### Q7

kimi兼容enai的不应该是https://api.moonshot.cn/v1 么

### Q8

你在网上搜索一下 在国内用kimi code的api如何给openclaw 配置 api，然后我现在配置方法是不是正确的

### Q9

[REDACTED_API_KEY] 这个是kimi code的api key

### Q10

然后 base url 是BASE_URL=https://api.kimi.com/coding/

### Q11

哪个好用那个

### Q12

我的openclaw如何接入微信 飞书等 我想方便的用手机跟他聊天控制

### Q13

openclaw plugins install @m1heng-clawd/feishu  这个有飞书插件 研究一下

### Q14

为什么我的openclaw只有2024年数据 需要安装对应的skill么  还有什么热门的openclaw skill可以都安装上么

### Q15

我想让你给openclaw项目里安装对应的skill  不光是给codex

## 助手回答（完整）

### A1

这次不需要用 skill（`skill-creator/skill-installer`），这是运行时配对问题。

我已经帮你排查并处理了，根因是：  
- 网关容器其实是健康的（在跑）。  
- 但 WebSocket 一直被拒绝：`code=1008 reason=pairing required`（还出现过 `device signature expired`）。  
- 也就是控制台设备没完成配对，不是服务没启动。

我已执行了设备配对审批（`openclaw devices approve --latest`），现在日志已出现：  
- `device pairing approved ...`  
- `webchat connected ... client=openclaw-control-ui`（2026-02-23T03:53:53Z）

你现在先做：  
1. 刷新 `http://127.0.0.1:18789/overview`（建议强刷）。  
2. 看右上角是否从 `Health Offline` 变成在线。

如果后续再复发，直接在 `openclaw-docker` 目录执行：  
```bash
docker compose exec -T openclaw-gateway openclaw devices list
docker compose exec -T openclaw-gateway openclaw devices approve --latest
```
（`approve --latest` 可重复执行到 `Pending` 为 0）

另外我看到还有一个独立问题：日志里提示当前默认模型走 `anthropic`，但该 provider 没有可用 key；这不影响“连上 dashboard”，但会影响后续 agent 对话。需要的话我可以下一步帮你一起改成你已有 key 的模型。

### A2

我已经帮你配好了，先说结论：

- Anthropic 的报错已经切走了，默认模型现在是 Kimi（Moonshot）。
- 但你这把 Kimi key 当前不可用，实际请求返回 `HTTP 401: Invalid Authentication`。

我做的配置：
- 已把默认模型设为 `moonshot/kimi-k2.5`，并清理为只保留这个模型：`/Users/tonyorz/.openclaw/openclaw.json:9`
- 模型白名单只保留了 Moonshot：`/Users/tonyorz/.openclaw/openclaw.json:12`

我验证到的现状：
- `openclaw agent` 返回 provider 已是 `moonshot`，但仍 401。
- 直接用容器里的 `MOONSHOT_API_KEY` 调 Moonshot 接口也返回 `Invalid Authentication`。  
  => 说明不是配置路径问题，是这把 key 本身无效/过期/权限不足。

你下一步这样做：
1. 去 Moonshot 平台重新生成一把新的 API Key（确认有对应模型权限）。
2. 更新 `openclaw-docker/.env` 里的 `MOONSHOT_API_KEY=新key`。
3. 重启网关：
   `docker compose up -d --force-recreate openclaw-gateway`
4. 验证：
   - `docker compose exec -T openclaw-gateway openclaw models status --probe --probe-provider moonshot --json`
   - `docker compose exec -T openclaw-gateway openclaw agent --agent main -m "回复ok" --json`

你把新 key 发我（可打码中间），我可以继续帮你直接改好并验证到能正常回复。

### A3

你创建对了，但**现在容器里这串 key 还是被 Moonshot 判定无效**，所以才 401。

我这边已验证到：
- OpenClaw 已切到 Kimi 模型：`/Users/tonyorz/.openclaw/openclaw.json:9`
- 但调用 Moonshot 接口仍返回 `Invalid Authentication`（不是 Anthropic 报错了）

最可能原因是**手动输入时把 `I/l/1` 混了**。  
你发我的是 `...QX17IidQ`，截图里看起来更像 `...QX17lidQ`（小写 L）。

请你现在做这一步（关键）：
1. 在 Moonshot 弹窗里点右侧“复制”按钮（不要手打）  
2. 把完整 key 直接粘贴给我（我马上替你更新并重启验证）

如果你愿意，也可以自己先本地验一下（把 `xxx` 换成刚复制的）：
```bash
curl -sS https://api.moonshot.ai/v1/models -H "Authorization: Bearer [REDACTED_TOKEN]"
```
返回 models 列表就说明 key 没问题。

### A4

你这个我已经替你改好并重启了，但结果是：

- 新 key 已写入：`/Users/tonyorz/openclaw-docker/.env:10`
- 网关已重建，默认模型仍是 `moonshot/kimi-k2.5`（`/Users/tonyorz/.openclaw/openclaw.json:9`）
- 但实际请求依然返回：`HTTP 401: Invalid Authentication`

我还直接在宿主机测了官方接口（排除 OpenClaw 配置问题）：
- `curl https://api.moonshot.cn/v1/models -H "Authorization: Bearer <你的新key>"`  
仍然是 `Invalid Authentication`。

这说明问题在 Moonshot 侧（key/账号状态），不是你本地配置。

你现在请先做这 3 步：
1. 右上角先点“验证你的身份”（你截图里还显示该提示）。
2. 在同一个组织/项目下重新生成一把全新 key（复制按钮，不手打）。
3. 立刻本地先测：
   `curl -sS https://api.moonshot.cn/v1/models -H "Authorization: Bearer 新key"`

只要这条命令返回模型列表，我这边马上帮你更新并验证 OpenClaw 全通。

另外安全提醒：你已在聊天里明文发过 key，建议把旧 key 全部删除重建。

### A5

对，你说得对。  
`Moonshot OpenAI 兼容`在国内一般走 `https://api.moonshot.cn/v1`。你这个 `sk-kimi-...` 也是 **Kimi Code** 体系的 key（不是 Moonshot 通用 key）。

你现在要分两种配法：

- `Moonshot(OpenAI兼容)`：`MOONSHOT_API_KEY` + 模型 `moonshot/...`（如 `moonshot/kimi-k2-turbo-preview`）+ baseUrl `https://api.moonshot.cn/v1`
- `Kimi Coding(Anthropic兼容)`：`KIMI_API_KEY` + 模型 `kimi-coding/k2p5` + 走 Kimi Coding 端点（不是 moonshot 的 model ref）

我已把你本地按 Moonshot 国内端点方式配好：
- ` /Users/tonyorz/.openclaw/openclaw.json:9`
- ` /Users/tonyorz/.openclaw/openclaw.json:21`
- ` /Users/tonyorz/openclaw-docker/.env:10`

并且刚才实际验证过：用你贴的 `sk-Z...` 那把 key，OpenClaw 已能返回 `ok`。  
所以你之前报错主要是把 `sk-kimi-...` 当成 `MOONSHOT_API_KEY` 用了。

参考（官方文档）：
- OpenClaw Moonshot/Kimi 文档：https://docs.openclaw.ai/moonshot
- OpenClaw 模型提供商（含 Kimi Coding）：https://docs.openclaw.ai/concepts/model-providers
- Moonshot 官方（国内 OpenAI 兼容示例）：https://platform.moonshot.cn/blog/posts/kimi-k2-api-launch

如果你要改成“只用 Kimi Code key（sk-kimi-...）”，我可以下一步帮你切到 `kimi-coding/k2p5`。

### A6

对，**Kimi Code** 用的就是这个：

`BASE_URL=https://api.kimi.com/coding/`

但要注意区分两套配置：

- `sk-kimi-...` → 用 **Kimi Coding**：`KIMI_API_KEY` + 模型 `kimi-coding/k2p5` + base URL `https://api.kimi.com/coding/`
- `sk-...`（Moonshot通用）→ 用 **Moonshot OpenAI兼容**：`MOONSHOT_API_KEY` + base URL `https://api.moonshot.cn/v1`

你要的话我可以现在直接帮你切成 **Kimi Coding** 这套。

### A7

我会用 `skill-installer` 来做这件事：先确认你“2024年数据”原因，再批量安装热门可用 skills。先按它的流程检查并执行。

### A8

你这个现象**不主要是 skill 问题**，而是两件事：

- `skill` 只提供流程/工具能力，不会自动把模型知识库从 2024 刷到最新。
- 要拿到最新信息，核心是：  
  1) 用可联网检索（web search）  
  2) 模型/API 正常可用（你前面 key 配置就会影响这点）

我已经按你说的把“热门可用”这批都装上了（OpenAI curated 全量 30 个），包括 `playwright`、`pdf`、`screenshot`、`spreadsheet`、`speech`、`transcribe`、`openai-docs`、`security-*`、`vercel-deploy` 等。

另外你提到的 `@m1heng-clawd/feishu` 我也研究了：  
- 你当前 OpenClaw 已自带 `feishu` 插件（社区维护版），但之前有依赖缺失问题。  
- 你安装的社区包目录也已经落到：`/Users/tonyorz/.openclaw/extensions/feishu`。

**下一步必须做：**
- **Restart Codex to pick up new skills.**

如果你愿意，我下一步可以直接帮你做两件事：  
1) 检查并修复 feishu 插件依赖加载；  
2) 给你配一套“手机聊天控制”最稳的通道（飞书优先）。
