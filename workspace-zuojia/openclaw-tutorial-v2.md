# OpenClaw 入门教程 ✦ v2

> 你的私人 AI 助手，住在你自己的设备上，随时待命 🦞

---

## 什么是 OpenClaw？

简单来说：OpenClaw 是一个运行在**你自己电脑上**的 AI 助手，能帮你处理各种事务——而且你可以直接在平时用的 app 里和它聊天。

不管是 **Telegram、Discord、WhatsApp、Slack、Signal、Google Chat**，还是 iMessage、Microsoft Teams，OpenClaw 都能接入。甚至还有 Matrix、Zalo 等更多平台。一次配置，到处能用。

---

## 开始之前，你需要准备什么？

OpenClaw 不需要你写代码，但需要跟着步骤做一些配置。准备好以下两件事，就能顺利上手：

**1. 安装 Node.js（版本 22 或更高）**

Node.js 是运行 OpenClaw 的基础环境，去官网下载安装就好：  
👉 https://nodejs.org

安装后，打开**终端**（Mac 上叫 Terminal，Windows 上叫 PowerShell），输入下面这行来确认安装成功：

```
node --version
```

如果看到 `v22.x.x` 或更高的数字，说明没问题。

**2. 一个能用的终端窗口**

之后几步都需要在终端里输入命令。别担心，每一步都有说明，复制粘贴就行。

---

## 第一步：安装 OpenClaw

打开终端，输入以下命令安装 OpenClaw：

```bash
npm install -g openclaw@latest
```

安装完成后，运行向导来完成初始设置：

```bash
openclaw onboard --install-daemon
```

向导会一步步引导你：选择 AI 模型（比如 Claude、GPT 等）、配置通讯渠道、安装常用功能。跟着提示走就好，大约 10-15 分钟可以完成。

---

## 第二步：选择你的通讯渠道

向导会问你想用哪个 app 和 OpenClaw 聊天。常见选项有：

- **Telegram** — 最简单，强烈推荐新手从这里开始
- **Discord** — 适合已经有 Discord 服务器的人
- **WhatsApp** — 日常用 WhatsApp 的话很方便
- **Slack** — 工作环境里用 Slack 的首选
- **Signal** — 注重隐私的用户
- **Google Chat** — G Suite 用户的选项
- **其他** — iMessage、Microsoft Teams、Matrix、WebChat 等也都支持

选一个你最常用的就行，以后随时可以再添加其他渠道。

---

## 第三步：关于"配对"这件事

配置好渠道之后，你在 app 里找到 bot，发一条消息——但可能没有反应？

别慌，这是正常的。OpenClaw 有一套**配对机制（Pairing）**，专门为了安全考虑：陌生人主动发消息给 bot 时，系统不会直接响应，而是先要求对方输入配对码。

这样做的好处是：防止你的 bot 被陌生人随便使用。

**怎么配对？**

1. 当你（或任何新用户）第一次给 bot 发消息，bot 会回复一个配对码
2. 在安装了 OpenClaw 的电脑上，打开终端，输入：
   ```
   openclaw pairing approve
   ```
3. 审批通过后，这个用户就加入了白名单，以后可以正常聊天

**只想让自己用？** 那就只批准自己的设备就好，其他人的请求直接忽略。

---

## 第四步：开始聊天！

配对完成后，在你选的 app 里给 bot 发消息，它就会回应你了。

你可以问它任何事：

> "帮我整理一下今天的待办事项"  
> "翻译这段英文"  
> "给我搜索一下最近的 AI 新闻"  
> "写一封邮件给客户道歉"

OpenClaw 会用你选的 AI 模型（Claude、GPT 或其他）来回答，感觉就像有个全能助理随时在线。

---

## 常见问题

**Q: 设置完了 bot 不回应怎么办？**  
大概率是配对没完成，或者 Gateway 没有正常运行。试试在终端输入 `openclaw doctor`，它会帮你诊断问题。

**Q: 换电脑了怎么办？**  
OpenClaw 的数据保存在本地，换电脑需要重新配置。建议把配置文件备份一下。

**Q: 可以同时用多个 app 吗？**  
可以！在向导里添加多个渠道就行，Telegram 和 Discord 可以同时连着。

**Q: 费用怎么算？**  
OpenClaw 本身免费开源。AI 模型的费用取决于你选的服务商（Anthropic、OpenAI 等），按实际用量收费。

---

## 进阶玩法（可选）

入门之后，如果想更进一步：

- **Skills（技能扩展）** — 去 [ClawHub](https://clawhub.ai/) 找现成的技能包，给 bot 增加新能力
- **Cron 定时任务** — 让 bot 每天早上自动给你发简报
- **多 Agent 协作** — 配置多个 bot 各司其职，像一个小团队

---

需要帮助随时可以查官方文档：  
📖 https://docs.openclaw.ai  
💬 Discord 社区：https://discord.gg/clawd

祝上手顺利！🦞
