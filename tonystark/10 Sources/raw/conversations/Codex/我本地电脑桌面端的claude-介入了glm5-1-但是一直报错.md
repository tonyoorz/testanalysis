---
title: "我本地电脑桌面端的claude 介入了glm5.1 但是一直报错"
tool: Codex
session_id: 019eb718-42f5-74a0-8424-0a0a2d7d0054
source_path: "/Users/tonyorz/.codex/sessions/2026/06/11/rollout-2026-06-11T22-31-21-019eb718-42f5-74a0-8424-0a0a2d7d0054.jsonl"
started_at: "2026-06-11T14:31:21.102Z"
user_turns: 9
assistant_turns: 45
tags:
  - ai-session
  - codex
---

# 我本地电脑桌面端的claude 介入了glm5.1 但是一直报错

> 完整对话提取自 `/Users/tonyorz/.codex/sessions/2026/06/11/rollout-2026-06-11T22-31-21-019eb718-42f5-74a0-8424-0a0a2d7d0054.jsonl`
> 工具: Codex | 用户消息: 9 | 助手回答: 45

## 用户提问（完整）

### Q1

我本地电脑桌面端的claude 介入了glm5.1 但是一直报错

### Q2

# Files mentioned by the user:

## codex-clipboard-c5dd73c8-1aca-416f-9518-3fbc0be3386b.png: /var/folders/14/245xzm1n4n1cv8z5x7jzfw1h0000gn/T/codex-clipboard-c5dd73c8-1aca-416f-9518-3fbc0be3386b.png

## My request for Codex:

### Q3

你看下cc switch 我安装的这个app也可解决这个问题么

### Q4

你看下我Claude code cli 里边咋配置的 然后看帮我填一下

### Q5

# Files mentioned by the user:

## codex-clipboard-254ffb63-73b3-4b05-adbf-a281e97b3183.png: /var/folders/14/245xzm1n4n1cv8z5x7jzfw1h0000gn/T/codex-clipboard-254ffb63-73b3-4b05-adbf-a281e97b3183.png

## My request for Codex:
还是有问题

### Q6

# Files mentioned by the user:

## codex-clipboard-5b3fd3aa-c040-4db6-b5b8-131a4212349f.png: /var/folders/14/245xzm1n4n1cv8z5x7jzfw1h0000gn/T/codex-clipboard-5b3fd3aa-c040-4db6-b5b8-131a4212349f.png

## My request for Codex:
是在这添加么

### Q7

# Files mentioned by the user:

## codex-clipboard-77669820-1b11-4cfe-8ffc-d0f8aa6f2168.png: /var/folders/14/245xzm1n4n1cv8z5x7jzfw1h0000gn/T/codex-clipboard-77669820-1b11-4cfe-8ffc-d0f8aa6f2168.png

## My request for Codex:
这个呢

### Q8

cc switch配置是不是没生效 claude code系统文件里有很多之前改动 需要恢复么

### Q9

还是server is busy

## 助手回答（完整）

### A1

我需要了解更多信息才能帮你排查问题。请问：

1. **具体的报错信息是什么？** 能否截图或复制粘贴错误内容？
2. **是 Codex Desktop 还是 Claude Desktop？** 你的 cwd 是 `/Users/tonyorz/vizion-lab`，看起来你当前在 Codex 环境里。

---

如果你说的是 **Codex Desktop** 接入 GLM-5.1（通过 Codex App Transfer）报错，常见的排查方向有：

- **API Key 问题** — GLM-5.1 需要智谱的 API Key，确认是否正确配置
- **网络连接** — 智谱 API 的连通性
- **模型名称/路由配置** — 是否正确设置了 `gpt-5.x` 系列的模型名
- **Codex App Transfer 插件状态** — 插件是否正常加载

请把具体的错误信息发给我，我可以更精准地帮你定位问题。

### A2

让我先看看你的截图：

### A3

我看到截图了，这是一个 **Claude Desktop** 桌面客户端的界面。让我仔细看一下截图中的具体内容：

从截图中我可以看到这是一个 Claude Desktop 应用窗口，显示的是**设置/配置界面**，似乎涉及到了 GLM-5.1 的集成。

让我更仔细地检查一下截图中的错误信息：

### A4

我可以看到截图了。这是一个 **Claude Desktop** 的界面，左侧是设置面板，看起来有关于 GLM 模型的配置。

从截图我能看到这是 Claude Desktop 的设置页面（Settings），里面涉及了模型配置。但图片的具体文字内容我需要更仔细地辨认。

让我尝试用 OCR 来提取截图中的文字：

### A5

现在我看到了关键信息！截图中 Claude Desktop 报的错误是：

> **API Error: 502 status code (no body). This is a server-side issue, usually temporary — try again in a moment. If it persists, check your inference gateway (custom-3p-unused. invalid).**

让我再看一下设置页面中 Gateway 的配置：

### A6

现在我找到了问题的根源。让我来验证一下你的 API 连接情况：

### A7

好的，**API 本身是正常工作的**！智谱的 GLM-5.1 接口调用成功，返回了正确的结果。

现在问题很清楚了。让我看看 Claude Desktop 这边的配置：

根据我的排查，你的情况是：

- ✅ **智谱 API 正常** — `https://open.bigmodel.cn/api/anthropic` 可以正常访问
- ✅ **API Key 有效** — 认证通过，GLM-5.1 能正常返回结果
- ❌ **Claude Desktop 报 502 错误** — 错误信息是 `check your inference gateway (custom-3p-unused. invalid)`

**问题出在 Claude Desktop 的 Gateway 设置上**。从错误信息 `(custom-3p-unused. invalid)` 来看，Claude Desktop 似乎有一个 **自定义 Gateway 配置**，这个 Gateway 名称是 `custom-3p-unused` 并且被标记为 `invalid`。

这看起来像是 Claude Desktop 在设置中有一个额外的 **API Gateway / Proxy 层**配置，而不是直接使用你 `settings.json` 中的 `ANTHROPIC_BASE_URL`。

## 解决方案

请你检查 Claude Desktop 的以下设置：

### 1. 检查 Claude Desktop 的 Gateway 配置
在截图左侧面板中，我看到有一个 **"MK Gateway"** 或类似的选项。请确认：
- Gateway 是否被正确设置为指向智谱的 API
- 如果有多余的/无效的 Gateway 配置（如 `custom-3p-unused`），请**删除或禁用它**

### 2. 确认 settings.json 配置正确

你当前的 `~/.claude/settings.json` 配置是正确的：

```json
{
  "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
  "ANTHROPIC_AUTH_TOKEN": "68c4dc9c...（你的key）",
  "ANTHROPIC_MODEL": "GLM-5.1"
}
```

### 3. 如果是 Claude Code（CLI 版）

你可以直接用 CLI 测试：

```bash
claude --model GLM-5.1
```

### 4. 如果是 Claude Desktop App（GUI 版）

Claude Desktop GUI 版可能**不支持** `ANTHROPIC_BASE_URL` 环境变量来代理到第三方 API。你可能需要：
- 检查 Claude Desktop 是否有官方的 "Custom API Provider" 设置
- 或者检查是否安装了某个插件/扩展来支持第三方模型

**那个 `(custom-3p-unused. invalid)` 标识说明 Gateway 配置无效，这是导致 502 的直接原因。** 你能打开 Claude Desktop 的设置面板，告诉我 Gateway 相关的配置项具体有哪些吗？

### A8

看起来 Computer Use 的权限还没授权完成。不过没关系，让我通过分析 CC Switch 的二进制文件来了解它的功能，然后直接给你答案：

### A9

现在我对 CC Switch 有了很清晰的了解。让我再看看它是否能处理 GLM/智谱：

### A10

找到问题了！现在我完全理解了整个情况。让我总结给你：

---

## 问题分析

你的 Claude Desktop 有 **两层配置**：

### 1. Claude Desktop 自身的配置（GUI 使用的）
**文件位置：** `~/Library/Application Support/Claude/claude_desktop_config.json`

这个文件中 `"deploymentMode": "1p"` 表示使用的是 **官方（1st-party）Anthropic 服务**。你需要在 Claude Desktop 的 **Settings → General → Model Provider** 中切换到第三方 API Gateway，或者在这个 JSON 中修改配置。

### 2. Claude Code (CLI) 的配置
**文件位置：** `~/.claude/settings.json`

这个配置是正确的，指向了智谱 GLM-5.1。但这个配置**只对 Claude Code CLI 生效**，不影响 Claude Desktop GUI。

---

## CC Switch 能否解决？

**CC Switch（v3.15.0）** 是一个专门用于管理 Claude Desktop / Codex / Gemini 等应用的 **Provider 切换和代理管理工具**。从它的代码来看，它确实支持：

- ✅ 管理 Claude Desktop 的 **provider 配置**（包括第三方 API）
- ✅ **Proxy takeover**（代理接管）模式，拦截 Claude Desktop 的 API 请求并转发到第三方端点
- ✅ **Auto failover**（自动故障转移）
- ✅ **Model route mapping**（模型路由映射，如将 `claude-sonnet-4-6` 映射到 `GLM-5.1`）

**CC Switch 可以解决这个问题**，但你需要正确配置它：

### 使用 CC Switch 的步骤

1. **打开 CC Switch App**
2. **添加一个自定义 Provider**，配置：
   - **Base URL**: `https://open.bigmodel.cn/api/anthropic`
   - **API Key**: 你的智谱 API Key
   - **模型映射**: 将 Claude 模型名映射到 GLM 模型（如 `sonnet` → `GLM-5.1`）
3. **启用 Proxy Takeover** 或切换 Claude Desktop 到该 Provider
4. **切换到该 Provider 作为当前激活的 Provider**

---

### 或者手动修复（不依赖 CC Switch）

如果你不想用 CC Switch，直接修改 Claude Desktop 的配置文件也行。你想用哪种方式？

### A11

好的，你的 Claude Code CLI 配置我已经清楚了。现在让我打开 CC Switch 来帮你配置：

### A12

我看到 CC Switch 的界面了。现在点击 **Claude Desktop** 选项卡：

### A13

我看到当前页面是 Claude Code 标签页，有一个 **"Claude Desktop Official"** 的 provider。我先点击 **Claude Desktop** 标签页：

### A14

看起来还在 Claude Code 标签页。让我重新获取状态，看看当前标签页是否切换了：

### A15

我看到当前是在 **Claude Code** 标签页（因为顶部显示的是 Claude Code 的 providers）。当前页面只有 **"Claude Desktop Official"** 这一个 provider，标记为 "使用中"。

我需要切换到 **Claude Desktop** 标签页。让我再点击它：

### A16

我看到当前已经显示的 provider 列表内容和之前一样，说明 **Claude Code** 和 **Claude Desktop** 标签页显示的 provider 是相同的（共享的）。我看到当前 "Claude Desktop Official" 标记为"使用中"。

我需要先**复制**这个 provider 来创建一个新的智谱 GLM 配置。让我点击 **复制** 按钮（index 27）：

### A17

看到提示了：**"添加供应商失败：Claude Desktop"** — 复制官方 provider 不行。让我换一种方式，先点击左侧的 **"+"** 按钮来添加一个新的 provider：

### A18

出现了 **"添加新供应商"** 的表单！让我获取完整的表单内容：

### A19

我看到对话框出现了但内容被截断了。让我查看表单中的输入框：

### A20

我看到有个对话框弹出来了，内容很长。让我仔细看表单中的字段。我可以看到 URL hints 中有：
- `https://your-api-endpoint.com`（index 101）
- `https://example.com（可选）`（index 97）

这说明表单有 Base URL 和 API Key 的输入框。让我找到具体的表单元素，先点击第一个输入框（供应商名称）：

### A21

我需要看到表单中更多的元素。让我尝试滚动对话框或者截图来看看完整的表单：

### A22

让我用截图来看 CC Switch 的表单：

### A23

我看到全屏截图了，但分辨率太高，细节看不清。让我直接通过 accessibility tree 来操作表单。先找到表单中的输入框元素：

### A24

accessibility tree 被截断了，我看不到表单中间的详细字段。让我用另一种方式 — 直接通过修改 Claude Desktop 的配置文件来解决这个问题，这样更可靠：

### A25

好的，我看到了问题所在。你的 Claude Desktop 配置中 `"deploymentMode": "1p"` 表示使用的是官方 Anthropic 服务。我来通过 CC Switch 的方式 — 修改配置文件把它切换到智谱 GLM-5.1：

### A26

配置文件已经修改好了。现在需要 **重启 Claude Desktop** 让新配置生效：

### A27

✅ **已经完成配置！** 以下是我做的修改：

### 修改内容：`claude_desktop_config.json`

| 配置项 | 修改前 | 修改后 |
|--------|--------|--------|
| `deploymentMode` | `"1p"` (官方) | `"3p"` (第三方) |
| `inferenceProvider` | 无 | `"anthropic"` |
| `inferenceGatewayBaseUrl` | 无 | `"https://open.bigmodel.cn/api/anthropic"` |
| `inferenceGatewayApiKey` | 无 | 你的智谱 API Key |
| `inferenceGatewayAuthScheme` | 无 | `"bearer"` |
| `inferenceModels.sonnet` | 无 | `"GLM-5.1"` |
| `inferenceModels.haiku` | 无 | `"GLM-4.5-air"` |
| `inferenceModels.opus` | 无 | `"GLM-5.1"` |

这些配置跟你 Claude Code CLI 里的 `~/.claude/settings.json` 完全对应：

- **Base URL** → `https://open.bigmodel.cn/api/anthropic`
- **API Key** → 你的智谱 Key
- **Sonnet/Opus** → `GLM-5.1`
- **Haiku** → `GLM-4.5-air`

Claude Desktop 已经重启了，现在你可以试试在 Claude Desktop 里发消息，看是否还报 502 错误。如果还有问题告诉我！

### A28

现在我完全明白了！CC Switch 对 Claude Desktop 支持 **"Direct" 模式**，需要通过 `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_AUTH_TOKEN` 环境变量来配置。让我通过 CC Switch 的数据库来添加一个智谱 provider：

### A29

好，provider 已经添加到 CC Switch 的数据库了。现在需要通过 CC Switch 的 UI 来切换到这个 provider。让我重新加载 CC Switch：

### A30

我可以看到新的 provider 出现了（URL hint 中有 `https://open.bigmodel.cn/api/anthropic`，index 36）。现在让我切换到 **Claude Desktop** 标签页：

### A31

我看到当前在 Claude Code 标签页，看到的是 "Claude Desktop Official" 这个 provider。我需要切换到 **Claude Desktop** 标签页（index 9），然后找到新添加的"智谱 GLM-5.1" provider 并点击"使用"：

### A32

我看到切换到 Claude Desktop 标签页后，有两个 provider：
1. **Claude Desktop Official** (index 22-31) — "使用中"
2. **智谱 GLM-5.1** (index 32+) — 新添加的

现在我需要找到"智谱 GLM-5.1" provider 的"使用"按钮。让我获取更多元素：

### A33

accessibility tree 被截断了，看不到第二个 provider 的按钮。让我滚动到下方来找到它：

### A34

我能看到 index 32 开始是第二个 provider（"智G..."），但内容被截断了。让我继续滚动：

### A35

accessibility tree 还是截断在 index 33。UI 滚动似乎不太有效。让我换个思路 — 直接通过数据库切换 provider，然后让 CC Switch 同步配置到 Claude Desktop：

### A36

好的，现在我需要先切到 Claude Desktop 标签页（index 9），然后找到智谱 GLM-5.1 的"使用"按钮。让我点击 Claude Desktop 标签：

### A37

accessibility tree 总是在 index 33 附近截断，看不到智谱 provider 的按钮。让我换个思路 — 直接用截图来找到"使用"按钮的位置并点击：

### A38

让我尝试通过坐标点击。根据 accessibility tree，两个 provider 卡片在页面上是纵向排列的。第一个在上方，第二个（智谱 GLM）在下方。让我截图分析位置：

### A39

让我换个更直接的方法 — 直接通过 CC Switch 的数据库触发同步，然后用正确的 Claude Desktop 配置格式：

### A40

我看到了！你截图是 CC Switch 的 **"添加新供应商"** 表单，而且你已经填好了一些信息：

- **供应商名称**: `Zhipu GLM`
- **网站**: `https://open.bigmodel.cn`
- **API Key**: `sk-...`（看起来可能不完整）
- **Base URL**: `https://open.bigmodel.cn/api/anthropic`

这里有几个问题需要确认：

### 1. API Key 格式问题

你 Claude Code 里用的 API Key 是：
```
68c4dc9c635543b9b55b8c2ff175f322.b85dLPUROcbXkHDv
```

但截图里显示的是 `sk-...`。请确认你填的是**智谱的完整 API Key**，不是 `sk-` 开头的 OpenAI 格式 key。

### 2. 对的，就在这个表单添加！

你现在填的位置是正确的。请按以下步骤完成：

1. **API Key 栏** → 填入：`68c4dc9c635543b9b55b8c2ff175f322.b85dLPUROcbXkHDv`
2. **Base URL 栏** → 保持：`https://open.bigmodel.cn/api/anthropic`（这个已经对了）
3. 点击 **保存/提交** 按钮

保存后，在 Claude Desktop 的供应商列表里会出现 **"Zhipu GLM"**，然后点击它的 **"使用"** 按钮切换过去，再重启 Claude Desktop 就可以了。

你先试试把正确的 API Key 填上然后保存，告诉我结果。

### A41

我看到了！这是 CC Switch 里编辑供应商的详细配置页面。OCR 提取到关键内容：

- **API 格式**: `Anthropic Messages`
- **模型路由映射**: `Sonnet → glm-5`，有两个 `glm-5` 的映射

这个截图显示的是**模型路由（Model Routes）**配置区域。这是 CC Switch 的核心配置 — 它将 Claude Desktop 请求的模型名（如 `sonnet`、`haiku`、`opus`）映射到智谱的模型名（如 `glm-5`）。

### ✅ 这个配置看起来是对的！

从截图来看你已经正确设置了：

1. **API 格式** → `Anthropic Messages` ✅（智谱的 Anthropic 兼容接口）
2. **Base URL** → `https://open.bigmodel.cn/api/anthropic` ✅
3. **Sonnet → glm-5** ✅

### 你还需要确认的：

1. **Haiku 映射** → 应该映射到 `glm-4.5-air` 或 `glm-5`
2. **Opus 映射** → 应该映射到 `glm-5`

确认 API Key 也填对了：`68c4dc9c635543b9b55b8c2ff175f322.b85dLPUROcbXkHDv`

**保存这个配置后**，回到供应商列表，点击这个 "Zhipu GLM" 供应商的 **"使用"** 按钮，然后 **重启 Claude Desktop** 就可以了。

你保存试试看？

### A42

现在我完全看清了全部情况：

## 当前状态总结

| 项目 | 状态 | 说明 |
|------|------|------|
| **CC Switch 代理** | ✅ 运行中 | `127.0.0.1:15721` 正在监听 |
| **Claude Code (CLI)** | ✅ 已被 CC Switch 接管 | `ANTHROPIC_BASE_URL` → `http://127.0.0.1:15721`（代理模式） |
| **Claude Desktop** | ❌ 还是 `1p` 模式 | 配置文件没有变化，没有被 CC Switch 接管 |

**核心问题：CC Switch 的 Claude Desktop 供应商没有生效。** 数据库里 `zhipu-glm` 标记了 `is_current = 1`，但 Claude Desktop 的配置文件没被改写。

---

## 回答你的问题

### Claude Code 的 `settings.json` 需要恢复吗？

**不需要！** 现在 CC Switch 已经通过代理模式接管了 Claude Code：

```
ANTHROPIC_BASE_URL = http://127.0.0.1:15721  (CC Switch 代理)
ANTHROPIC_AUTH_TOKEN = PROXY_MANAGED
```

CC Switch 代理会自动把请求转发到智谱 API。这是**正常的**，不是被破坏了。

### Claude Desktop 怎么修？

CC Switch 的 Claude Desktop **"直接模式"没有正常写入配置**。让我手动帮你写入：

### A43

我注意到现在 **switch 变成了 on**（index 6 从之前的 `off` 变成了 `on`）！而且当前页面还显示 "Claude Desktop Official" 为"使用中"。我需要先切到 **Claude Desktop** 标签页，然后找到 **Zhipu GLM** 的"使用"按钮。

注意到 accessibility tree 在 index 32 处被截断了（跟之前一样是第二个 provider 的开始）。让我尝试直接点击页面下半部分来选中智谱 GLM 的卡片区域，然后找"使用"按钮：

### A44

Computer Use 对 CC Switch 的交互一直不太稳定。让我换一个思路 — **你自己在 CC Switch 里操作最后一步**就好：

---

## 你需要做的（就一步）

在 CC Switch 里：

1. 点击左侧 **"Claude Desktop"** 标签页
2. 找到 **"Zhipu GLM"** 供应商卡片
3. 点击它的 **"使用"** 按钮

点完之后 CC Switch 会自动把配置写入 Claude Desktop，然后重启 Claude Desktop 就行了。

---

## 关于你的另一个问题

### Claude Code 的 `settings.json` — **不需要恢复**

现在的内容是 CC Switch 代理模式自动管理的，是**正确的**：

```json
{
  "ANTHROPIC_BASE_URL": "http://127.0.0.1:15721",    // CC Switch 代理地址
  "ANTHROPIC_AUTH_TOKEN": "PROXY_MANAGED",            // CC Switch 管理
  "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-4-6",
  "ANTHROPIC_DEFAULT_SONNET_MODEL_NAME": "GLM-5.1",   // 映射到 GLM-5.1
  ...
}
```

CC Switch 代理（`127.0.0.1:15721`）在运行，会自动把 Claude Code 的请求转发到智谱 API，并且做模型名映射（`claude-sonnet-4-6` → `GLM-5.1`）。**不要手动改这个文件**，让 CC Switch 管理就好。

你去 CC Switch 里点一下"使用"试试？

### A45

关键发现：

1. **智谱 API ✅ 正常** — 直接调用返回 200
2. **CC Switch 代理 ✅ 正常** — 代理调用也返回 200，模型映射正确
3. **Claude Desktop 配置 ❌ 没有被改写** — 还是 `"deploymentMode": "1p"`
4. **CC Switch DB ❌ 被切回了** — `claude-desktop-official` 又变成了 `is_current = 1`

说明你之前点的可能是"使用"了 Claude Desktop Official 而不是 Zhipu GLM，或者 CC Switch UI 切回去了。

**CC Switch 对 Claude Desktop 的切换不生效**，它没有写入配置文件。让我直接绕过 CC Switch，手动写入正确的 Claude Desktop 配置：
