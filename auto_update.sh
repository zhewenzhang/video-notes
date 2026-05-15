#!/bin/bash
# auto_update.sh - OpenClaw 自动更新入口
# 由 cron 定时调用，完成：检查新视频 → 生成笔记 → 构建网站 → 推送 GitHub
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 [$(date '+%Y-%m-%d %H:%M')] 开始自动更新..."

# 1. 检查新视频
echo "📡 检查 YouTube 频道..."
python3 update_notes.py 2>&1

# 2. 如果有待处理笔记，生成内容
if [ -f "pending_notes.json" ]; then
    PENDING_COUNT=$(python3 -c "import json; print(len(json.load(open('pending_notes.json'))))")
    echo "📝 发现 $PENDING_COUNT 篇待处理笔记"
    
    if [ "$PENDING_COUNT" -gt 0 ]; then
        echo "⏳ 等待 AI 生成笔记内容（由 OpenClaw 处理）..."
        # AI 笔记生成由 OpenClaw agent 直接处理
        # 这里只负责检查和构建
    fi
fi

# 3. 构建网站
echo "🔨 构建网站..."
python3 build.py 2>&1

# 4. Git 提交并推送
echo "📤 推送到 GitHub..."
git add -A
CHANGES=$(git diff --cached --name-only)
if [ -n "$CHANGES" ]; then
    git commit -m "auto: 更新笔记 $(date '+%Y-%m-%d %H:%M')"
    git push origin main
    echo "✅ 推送成功！"
else
    echo "✅ 无变更，跳过推送"
fi

echo "🎉 [$(date '+%Y-%m-%d %H:%M')] 更新完成"
