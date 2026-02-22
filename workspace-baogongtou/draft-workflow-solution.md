# 工作流自动化方案

## 问题分析

现有两个自动化断点：
1. **作家/研究员完成后** → 包工头无法自动检测并送审智库
2. **智库审核完成后** → 包工头无法自动交付给用户

**已尝试但失败的方案：**
- Cron + systemEvent → 每次触发都往群里发消息，严重刷屏
- Cron + isolated agentTurn → isolated session 没有包工头权限，流程跑不通
- Heartbeat → 触发时机不可控，无法精确响应任务完成事件

## 根因

缺乏一个**事件驱动的机制**来：
1. 可靠检测"任务完成"事件（而不是轮询）
2. 在不打扰用户的情况下触发下一步操作

## 解决方案

### 核心思路：使用 Hook 监听消息事件

OpenClaw 的 Hook 系统可以监听 `message:received` 事件，并在 Gateway 内部执行逻辑。我们可以：

1. **创建一个 Workflow Hook** 监听特定消息（如"已交稿"）
2. **在 Hook 内部** 更新工作流状态 + 触发下一步（通过 Webhook/RPC）
3. **静默执行**：不向主会话发送消息，只在后台完成流程

---

## 方案一：Message Hook + Webhook 触发（推荐）

### 原理

```
作家发送 "已交稿" 
    ↓
Hook 拦截 message:received 事件
    ↓
检查消息内容 + 发送者身份
    ↓
调用 POST /hooks/agent 触发智库审核
    ↓
智库完成 → 再次触发 → 交付给用户
```

### 实现步骤

#### Step 1: 创建 Workflow Hook

在 `~/.openclaw/hooks/workflow-trigger/` 创建：

```
workflow-trigger/
├── HOOK.md
└── handler.ts
```

**HOOK.md:**
```markdown
---
name: workflow-trigger
description: "监听工作流触发消息，自动送审智库或交付用户"
metadata:
  openclaw:
    emoji: "🔄"
    events: ["message:received"]
---

# Workflow Trigger Hook

监听特定消息触发工作流：
- "已交稿" → 自动送审智库
- "审核通过" → 自动交付给用户
```

**handler.ts:**
```typescript
import type { HookHandler } from "../../src/hooks/hooks.js";

const WORKFLOW_STATE_FILE = "/Users/mirkozhang/.openclaw/workspace-baogongtou/workflow-state.json";
const WEBHOOK_URL = "http://127.0.0.1:18789/hooks/agent";
const WEBHOOK_TOKEN = "YOUR_HOOK_TOKEN"; // 从环境变量读取

const handler: HookHandler = async (event) => {
  if (event.type !== "message" || event.action !== "received") {
    return;
  }

  const content = event.context.content?.toLowerCase() || "";
  const from = event.context.from;
  
  // 读取当前工作流状态
  let workflowState = { stage: "idle", taskId: null };
  try {
    const fs = await import("fs");
    if (fs.existsSync(WORKFLOW_STATE_FILE)) {
      workflowState = JSON.parse(fs.readFileSync(WORKFLOW_STATE_FILE, "utf-8"));
    }
  } catch (e) {
    console.error("[workflow-trigger] Failed to read state:", e);
  }

  // 场景1: 作家说"已交稿" → 送审智库
  if (content.includes("已交稿") && workflowState.stage === "writing") {
    console.log("[workflow-trigger] Detected completion, spawning zhiku...");
    
    // 更新状态
    workflowState.stage = "reviewing";
    // ... 保存状态
    
    // 触发智库审核 (isolated agent turn，静默执行)
    await triggerAgent({
      agentId: "zhiku",
      message: `请审核任务 ${workflowState.taskId} 的内容。作家已交稿。`,
      name: "Workflow-Zhiku",
      deliver: false, // 不发送消息到主会话
    });
    
    return;
  }

  // 场景2: 智库审核完成 → 交付用户
  if (content.includes("审核通过") && workflowState.stage === "reviewing") {
    console.log("[workflow-trigger] Review complete, delivering to user...");
    
    // 更新状态
    workflowState.stage = "delivered";
    // ... 保存状态
    
    // 触发包工头交付
    await triggerAgent({
      agentId: "baogongtou", 
      message: `任务 ${workflowState.taskId} 已通过审核，请交付给用户。`,
      name: "Workflow-Deliver",
      deliver: true,
      channel: "discord", // 或从上下文获取
      to: "user:xxx",
    });
    
    return;
  }
};

async function triggerAgent(params: {
  agentId: string;
  message: string;
  name: string;
  deliver?: boolean;
  channel?: string;
  to?: string;
}) {
  const response = await fetch(WEBHOOK_URL, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${WEBHOOK_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      agentId: params.agentId,
      message: params.message,
      name: params.name,
      deliver: params.deliver ?? false,
      channel: params.channel ?? "last",
      to: params.to,
      wakeMode: "now",
    }),
  });
  
  if (!response.ok) {
    console.error("[workflow-trigger] Failed to trigger agent:", await response.text());
  }
}

export default handler;
```

#### Step 2: 启用 Hook

```bash
openclaw hooks enable workflow-trigger
# 需要先放在 ~/.openclaw/hooks/workflow-trigger/
```

#### Step 3: 配置 Webhook Endpoint

在 `~/.openclaw/config.yaml` 中：

```yaml
hooks:
  enabled: true
  token: "YOUR_HOOK_TOKEN"
  path: "/hooks"
  allowedAgentIds: ["baogongtou", "zhiku", "zuojia", "yanjiuyuan"]
```

#### Step 4: 定义工作流状态文件

`workflow-state.json` 结构：
```json
{
  "stage": "writing|reviewing|delivered|idle",
  "taskId": "task-123",
  "author": "zuojia",
  "createdAt": "2026-02-22T10:00:00Z",
  "updatedAt": "2026-02-22T13:00:00Z"
}
```

---

## 方案二：协议约定 + Cron 定时检查（备选）

如果 Hook 方式不可行，可以使用轻量级的轮询方案：

### 原理

1. 工作流状态记录在文件中
2. Cron job 每分钟检查一次状态变化
3. 只在状态真正变化时才执行操作

### 实现

```bash
# 每分钟检查一次工作流状态
openclaw cron add \
  --name "Workflow Check" \
  --cron "* * * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "检查工作流状态文件 ~/.openclaw/workspace-baogongtou/workflow-state.json，如果 stage 从 writing 变为 reviewing，触发智库审核。如果 stage 从 reviewing 变为 delivered，交付给用户。只在状态真正变化时回复，如果没变化则回复 HEARTBEAT_OK。" \
  --announce \
  --channel discord \
  --to "channel:xxx"
```

**注意**：这个方案的问题是需要每次都运行 agent 来检查，效率较低。推荐方案一。

---

## 方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| **方案一：Hook + Webhook** | 事件驱动，精确响应，无轮询开销，静默执行 | 需要写 TypeScript handler |
| **方案二：Cron 轮询** | 简单，无需写代码 | 有延迟（最多1分钟），每次都消耗 API |

---

## 实施计划

1. **立即可做**：在包工头 workspace 创建 `workflow-state.json` 状态文件
2. **短期**：创建 `workflow-trigger` Hook 监听消息
3. **中期**：配置 Webhook endpoint 并测试完整流程
4. **长期**：考虑将状态存储改为数据库（当前用文件）

---

## 注意事项

1. **安全问题**：Hook token 要保密，不要泄露
2. **幂等性**：确保同一个"已交稿"消息不会重复触发（可以检查消息 ID 或时间戳）
3. **错误处理**：Hook 中要捕获异常，避免影响正常消息处理
4. **测试**：先用 `deliver: false` 测试，确认逻辑正确后再开启交付

---

## 参考文档

- [Hooks 文档](~/.nvm/versions/node/v24.13.0/lib/node_modules/openclaw/docs/automation/hooks.md)
- [Webhook 文档](~/.nvm/versions/node/v24.13.0/lib/node_modules/openclaw/docs/automation/webhook.md)
- [Cron 文档](~/.nvm/versions/node/v24.13.0/lib/node_modules/openclaw/docs/automation/cron-jobs.md)
