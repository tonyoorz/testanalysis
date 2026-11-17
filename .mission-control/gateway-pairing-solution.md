# OpenClaw Gateway 配对解决方案

## 问题诊断

根据日志分析，Mission Control 连接 OpenClaw Gateway 时出现：
```
unauthorized conn=... reason=token_missing
```

**根本原因**：Mission Control 没有正确传递 Gateway token。

---

## 解决方案

### 方案 1：在 Mission Control UI 中手动配置（推荐）

#### 步骤 1：访问 OpenClaw Control UI
```
URL: http://192.168.0.200:18789
```

#### 步骤 2：查看已配对的设备
1. 在 OpenClaw Control UI 中，查看 "Paired Devices" 或类似选项
2. 如果已经有设备配对，查看连接信息

#### 步骤 3：创建新的配对码
1. 在 OpenClaw Control UI 中，找到 "Pair New Device" 或 "Create Pairing Code"
2. 生成一个配对码（Pairing Code）
3. 复制这个配对码

#### 步骤 4：在 Mission Control 中配对
1. 访问 Mission Control: http://localhost:3000
2. 创建 Gateway 时，输入：
   - **Name**: OpenClaw Docker
   - **URL**: `ws://192.168.0.200:18789`
   - **Workspace Root**: `/Users/tonyorz/openclaw-docker/workspace`
   - **Pairing Code**: [从 OpenClaw Control UI 获取的配对码]
   - **Token**: `openclaw-local-token-2024`

---

### 方案 2：直接使用 Token（如果 UI 支持）

在 Mission Control 创建 Gateway 时，尝试以下字段：

```json
{
  "name": "OpenClaw Docker",
  "url": "ws://192.168.0.200:18789",
  "workspace_root": "/Users/tonyorz/openclaw-docker/workspace",
  "description": "OpenClaw Gateway for AI Analysis project optimization",
  "token": "openclaw-local-token-2024"
}
```

**关键点**：
- 确保 token 字段名正确（可能是 `token` 或 `auth_token`）
- URL 必须是 WebSocket 协议（`ws://`）
- 使用宿主机 IP（`192.168.0.200`）而不是 localhost

---

### 方案 3：检查 Mission Control Backend 日志

查看详细的错误信息：
```bash
docker logs openclaw-mission-control-backend-1 --tail 100
```

查找与 Gateway 创建相关的错误消息。

---

### 方案 4：临时禁用 Token 验证（仅用于测试）

如果急需开始工作，可以临时禁用 OpenClaw Gateway 的 token 验证：

#### 修改 openclaw.json
```json
"gateway": {
  "port": 18789,
  "bind": "0.0.0.0",
  "controlUi": {
    "allowedOrigins": [
      "http://localhost:18789",
      "http://127.0.0.1:18789"
    ]
  },
  "auth": {
    "token": "openclaw-local-token-2024",
    "allowPairing": true  // 添加这一行
  }
}
```

或尝试：
```json
"gateway": {
  "port": 18789,
  "bind": "0.0.0.0",
  "controlUi": {
    "allowedOrigins": [
      "http://localhost:18789",
      "http://127.0.0.1:18789"
    ]
  },
  "auth": {
    "enabled": false  // 临时禁用
  }
}
```

#### 重启 OpenClaw Gateway
```bash
cd /Users/tonyorz/openclaw-docker
docker compose restart
```

---

## 验证配置

### 测试 WebSocket 连接
```bash
# 使用 wscat 测试连接
npm install -g wscat
wscat -c ws://192.168.0.200:18789 -H "Authorization: Bearer openclaw-local-token-2024"
```

### 测试 HTTP 连接
```bash
curl -H "Authorization: Bearer openclaw-local-token-2024" \
  http://192.168.0.200:18789/health
```

---

## 下一步

### 如果配对成功
1. 在 Mission Control 中创建 Board
2. 选择 "OpenClaw Docker" Gateway
3. 开始创建 Agents 和任务

### 如果仍然失败
1. 查看详细日志（见方案 3）
2. 尝试方案 4（临时禁用 token）
3. 联系 OpenClaw/Mission Control 支持

---

## 快速参考

### OpenClaw Gateway 信息
- **URL**: `ws://192.168.0.200:18789`
- **Token**: `openclaw-local-token-2024`
- **Workspace**: `/Users/tonyorz/openclaw-docker/workspace`
- **Status**: ✅ 运行正常

### Mission Control 信息
- **URL**: http://localhost:3000
- **API**: http://localhost:8000
- **Status**: ✅ 运行正常

### 相关文件
- OpenClaw Config: `/Users/tonyorz/openclaw-docker/openclaw.json`
- Mission Control .env: `/Users/tonyorz/openclaw-docker/openclaw-mission-control/.env`
