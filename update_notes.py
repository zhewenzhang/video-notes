#!/usr/bin/env python3
"""
update_notes.py - 自动抓取新视频并生成笔记
由 OpenClaw 定时调用。

用法:
  python3 update_notes.py                    # 检查所有频道
  python3 update_notes.py --channel a16z     # 只检查指定频道
  python3 update_notes.py --list             # 列出已跟踪的频道
"""
import os
import sys
import json
import glob
import re
import argparse
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(SCRIPT_DIR, "notes")
CONFIG_FILE = os.path.join(SCRIPT_DIR, "channels.json")

# 默认频道配置
DEFAULT_CHANNELS = [
    {
        "name": "a16z",
        "youtube_url": "https://www.youtube.com/@a16z",
        "youtube_channel_id": "UCBcRF18a7Qf58cCRy5xuWwQ",
        "tags": ["#a16z", "#VC", "#AI投资"]
    },
    {
        "name": "Lex Fridman",
        "youtube_url": "https://www.youtube.com/@lexfridman",
        "youtube_channel_id": "UCSHZKJJfhK61IS3o3Q1GhZg",
        "tags": ["#LexFridman", "#AI", "#深度访谈"]
    },
    {
        "name": "Matthew Berman",
        "youtube_url": "https://www.youtube.com/@MatthewBerman",
        "youtube_channel_id": "UCjutqHWhhag_UBgP1OJ7wkg",
        "tags": ["#MatthewBerman", "#AI", "#LLM"]
    },
    {
        "name": "All-In Podcast",
        "youtube_url": "https://www.youtube.com/@AllInPodcast",
        "youtube_channel_id": "UCESLZhusAkFfsNsApnjF_Cg",
        "tags": ["#AllInPodcast", "#科技", "#投资"]
    },
    {
        "name": "Invest Like The Best",
        "youtube_url": "https://www.youtube.com/@InvestLikeBest",
        "youtube_channel_id": "UC1_wCOt3bOHiI_Q8tFQd7Zw",
        "tags": ["#InvestLikeTheBest", "#投资", "#访谈"]
    },
    {
        "name": "Y Combinator",
        "youtube_url": "https://www.youtube.com/@ycombinator",
        "youtube_channel_id": "UCcefcZRL2oaA_uBNeo5UOWg",
        "tags": ["#YCombinator", "#创业", "#AI"]
    },
    {
        "name": "Stanford Online",
        "youtube_url": "https://www.youtube.com/@stanfordonline",
        "youtube_channel_id": "UC-6nunShRVPaUIPI1p1GKig",
        "tags": ["#Stanford", "#CS", "#AI"]
    }
]

def load_config():
    """加载频道配置"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # 创建默认配置
    save_config(DEFAULT_CHANNELS)
    return DEFAULT_CHANNELS

def save_config(config):
    """保存频道配置"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def get_existing_notes():
    """获取已有的笔记列表"""
    existing = set()
    for md_file in glob.glob(os.path.join(NOTES_DIR, "*.md")):
        basename = os.path.basename(md_file).replace(".md", "")
        existing.add(basename)
    return existing

def fetch_youtube_videos(channel_id, max_results=10):
    """
    抓取频道最新视频列表。
    使用 YouTube RSS feed (无需 API key)。
    """
    import urllib.request
    
    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    try:
        req = urllib.request.Request(rss_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml_data = resp.read().decode("utf-8")
    except Exception as e:
        print(f"  ⚠️  RSS 抓取失败: {e}")
        return []
    
    videos = []
    # Parse entries
    entries = re.findall(r'<entry>(.*?)</entry>', xml_data, re.DOTALL)
    for entry in entries[:max_results]:
        video_id = re.search(r'<yt:videoId>(.*?)</yt:videoId>', entry)
        title = re.search(r'<media:title>(.*?)</media:title>', entry)
        published = re.search(r'<published>(.*?)</published>', entry)
        description = re.search(r'<media:description>(.*?)</media:description>', entry, re.DOTALL)
        
        if video_id and title:
            pub_date = published.group(1)[:10] if published else ""
            videos.append({
                "id": video_id.group(1),
                "title": title.group(1),
                "date": pub_date,
                "description": (description.group(1)[:300] if description else ""),
                "url": f"https://www.youtube.com/watch?v={video_id.group(1)}"
            })
    
    return videos

def check_new_videos(channel_config, existing_notes):
    """检查频道是否有新视频"""
    channel_name = channel_config["name"]
    channel_id = channel_config.get("youtube_channel_id", "")
    
    if not channel_id:
        print(f"  ⚠️  {channel_name}: 缺少 youtube_channel_id")
        return []
    
    videos = fetch_youtube_videos(channel_id)
    new_videos = []
    
    for v in videos:
        # 生成预期的文件名
        date_str = v["date"]
        slug = re.sub(r'[^a-z0-9]+', '-', v["title"].lower()).strip('-')[:60]
        filename = f"{date_str}-{channel_name.lower().replace(' ', '-')}-{slug}"
        
        # 检查是否已存在
        if filename not in existing_notes:
            new_videos.append({**v, "filename": filename})
    
    return new_videos

def create_note_stub(video, channel_config):
    """创建笔记 Markdown 模板（等待 AI 填充内容）"""
    tags = channel_config.get("tags", [])
    
    content = f"""---
title: "{video['title']}"
channel: {channel_config['name']}
date: {video['date']}
tags: {json.dumps(tags, ensure_ascii=False)}
source_url: {video['url']}
status: pending
---

# {video['title']}

> 📺 来源: [{channel_config['name']}]({video['url']})
> 📅 发布: {video['date']}

## 视频简介

{video.get('description', '')}

---
*⏳ 等待 AI 生成深度笔记...*
"""
    
    out_file = os.path.join(NOTES_DIR, f"{video['filename']}.md")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    return out_file

def main():
    parser = argparse.ArgumentParser(description="检查 YouTube 频道新视频")
    parser.add_argument("--channel", help="只检查指定频道")
    parser.add_argument("--list", action="store_true", help="列出频道")
    parser.add_argument("--max-per-channel", type=int, default=5, help="每个频道最多检查视频数")
    args = parser.parse_args()
    
    config = load_config()
    
    if args.list:
        print("📺 已配置的频道:")
        for ch in config:
            print(f"  • {ch['name']} - {ch['youtube_url']}")
        return
    
    existing = get_existing_notes()
    print(f"📚 已有 {len(existing)} 篇笔记")
    print()
    
    new_videos_all = []
    
    for ch in config:
        if args.channel and ch["name"].lower() != args.channel.lower():
            continue
        
        print(f"🔍 检查 {ch['name']}...")
        new_videos = check_new_videos(ch, existing)
        
        if new_videos:
            print(f"  🆕 发现 {len(new_videos)} 个新视频:")
            for v in new_videos:
                print(f"    • {v['title']} ({v['date']})")
                create_note_stub(v, ch)
                new_videos_all.append({**v, "channel": ch["name"]})
        else:
            print(f"  ✅ 无新视频")
    
    print()
    if new_videos_all:
        print(f"🎉 共发现 {len(new_videos_all)} 个新视频，已创建笔记模板")
        # 输出 JSON 供 AI 使用
        output_file = os.path.join(SCRIPT_DIR, "pending_notes.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(new_videos_all, f, ensure_ascii=False, indent=2)
        print(f"📝 待处理列表: {output_file}")
    else:
        print("✅ 所有频道都是最新的，无新内容")

if __name__ == "__main__":
    main()
