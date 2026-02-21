#!/bin/bash

# OpenClaw 定时搜索脚本
# 每天 12:00 执行，搜索 X 和 YouTube 上的 OpenClaw 教程/更新

DATE=$(date +%Y-%m-%d)
LOG_FILE="/Users/mirkozhang/.openclaw/workspace-zhiku/memory/openclaw-search-$DATE.md"
KNOWLEDGE_DIR="/Users/mirkozhang/.openclaw/workspace-zhiku/knowledge"

echo "# OpenClaw 相关搜索 - $DATE" > "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 搜索 X (Twitter) - 使用英文关键词避免中文限制
echo "## X (Twitter) 搜索结果" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

X_RESULTS=$(curl -s "https://api.twitter.com/2/tweets/search/recent?query=OpenClaw+OR+openclawai+OR+%23OpenClaw+-is:retweet&max_results=10" \
  -H "Authorization: Bearer $TWITTER_BEARER_TOKEN" 2>/dev/null || echo "[]")

if [ "$X_RESULTS" != "[]" ] && [ -n "$TWITTER_BEARER_TOKEN" ]; then
  echo "$X_RESULTS" | jq -r '.data[]? | "- @" + .author_id + ": " + .text[0:200]' 2>/dev/null >> "$LOG_FILE"
else
  echo "- (无 Twitter API 访问权限或无结果)" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# 搜索 YouTube
echo "## YouTube 搜索结果" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

YT_RESULTS=$(curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=5&q=OpenClaw+AI+agent&type=video&regionCode=US" \
  -H "Authorization: Bearer $YOUTUBE_API_KEY" 2>/dev/null || echo "{}")

if [ "$YT_RESULTS" != "{}" ] && [ -n "$YOUTUBE_API_KEY" ]; then
  echo "$YT_RESULTS" | jq -r '.items[]? | "- [" + .snippet.title + "](https://youtube.com/watch?v=" + .id.videoId + ") - " + .snippet.channelTitle' 2>/dev/null >> "$LOG_FILE"
else
  echo "- (无 YouTube API 访问权限，使用网页搜索替代)" >> "$LOG_FILE"
  # 备用：使用网页搜索
  WEB_SEARCH=$(web_search --count 5 --freshness pw --query "OpenClaw AI agent tutorial")
  echo "$WEB_SEARCH" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# 分析总结
echo "## 分析总结" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "- 搜索完成时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "- 待人工分析内容" >> "$LOG_FILE"

# 移动到知识库待处理
mv "$LOG_FILE" "$KNOWLEDGE_DIR/pending/"
echo "搜索完成，已保存到知识库待分析"
