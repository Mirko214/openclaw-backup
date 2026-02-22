# NotebookLM 调研报告

## 1. 现有 Skill 检查
经检查 `~/.nvm/versions/node/v24.13.0/lib/node_modules/openclaw/skills/` 目录下**没有**内置的 notebooklm 相关的 skill。

## 2. notebooklm-py 简介与评估
[notebooklm-py](https://github.com/teng-lin/notebooklm-py) 是一个非官方的 Google NotebookLM Python API 和 CLI 工具，甚至支持将其作为 Claude Code 的 Agent Skill。

### 对 Mirko (X/Twitter 内容运营) 的核心价值：
这对内容运营来说是一个**极其强大的生产力工具**。
1. **内容降维与重塑**：可以批量导入长文链接、PDF、甚至是 YouTube 视频，然后一键生成音频播客 (Audio Overview)、短视频 (Video Overview)、信息图表 (Infographic)。这些多媒体格式在 X/Twitter 上具有极高的互动率。
2. **提炼推文素材**：通过 `notebooklm ask` 接口，可以快速向长篇资料提问，提取核心观点，非常适合用来编写 Twitter Thread（推文串）。
3. **自动化工作流**：支持 Python 异步 API 和 CLI。配合其他自动化脚本，可以实现“监控特定信息源 -> 自动导入 NotebookLM -> 自动生成观点总结 -> 自动草拟推文”的流水线。
4. **Claude Code 无缝集成**：自带 `notebooklm skill install`，可以用自然语言直接指挥 NotebookLM 干活。

## 3. 安装步骤
建议安装包含浏览器登录支持的版本（首次认证需要）：
```bash
# 基础安装并包含浏览器支持
pip install "notebooklm-py[browser]"

# 安装 playwright 依赖的浏览器
playwright install chromium

# 首次登录认证（会打开浏览器）
notebooklm login
```

## 4. 初步使用建议
**场景 A：长文/视频转推文串 (Twitter Thread)**
```bash
# 创建知识库并导入链接（例如一篇长文或 YouTube 视频）
notebooklm create "推文素材"
notebooklm use <notebook_id>
notebooklm source add "https://example.com/long-article"

# 提取核心观点用于发推
notebooklm ask "用适合 Twitter Thread 的风格，提取这篇文章的 5 个最核心的观点，每个观点限制在 200 字以内并带有适当的 Emoji。"
```

**场景 B：生成富媒体推文配图/视频**
```bash
# 生成白板风格的解说短视频
notebooklm generate video --style whiteboard --wait
notebooklm download video ./overview.mp4

# 生成信息图表作为推文配图
notebooklm generate infographic --orientation portrait
```

**场景 C：作为 Agent 技能**
如果在终端中使用 Claude Code 或者类似的基于命令行的 LLM Agent，可以直接运行 `notebooklm skill install`，然后用自然语言让 Agent 帮你整理资料和生成内容。