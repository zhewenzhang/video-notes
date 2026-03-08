#!/usr/bin/env python3
"""生成包含所有笔记的索引页"""

import os
import re
from datetime import datetime

INSIGHTS_DIR = "/Users/dave/video-notes/insights"
OUTPUT_FILE = "/Users/dave/video-notes/index.html"

def extract_meta(html_content):
    """从 HTML 中提取元数据"""
    title = ""
    channel = ""
    duration = ""
    date = ""
    tags = []
    excerpt = ""
    
    # 标题
    title_match = re.search(r'<h1>(.*?)</h1>', html_content)
    if title_match:
        title = title_match.group(1)
    
    # 元数据
    meta_match = re.search(r'<div class="meta">(.*?)</div>', html_content, re.DOTALL)
    if meta_match:
        meta = meta_match.group(1)
        channel_match = re.search(r'📺 (.*?)</span>', meta)
        if channel_match:
            channel = channel_match.group(1).strip()
        duration_match = re.search(r'⏱️ (.*?)</span>', meta)
        if duration_match:
            duration = duration_match.group(1).strip()
        date_match = re.search(r'📅 (.*?)</span>', meta)
        if date_match:
            date = date_match.group(1).strip()
    
    # 标签
    tags_matches = re.findall(r'<span class="tag">(.*?)</span>', html_content)
    tags = tags_matches[:4]  # 最多 4 个标签
    
    # 摘要（第一个段落）
    p_match = re.search(r'<div class="content">.*?<p>(.*?)</p>', html_content, re.DOTALL)
    if p_match:
        excerpt = re.sub(r'<.*?>', '', p_match.group(1))[:150] + "..."
    
    return title, channel, duration, date, tags, excerpt

def main():
    notes = []
    
    for filename in sorted(os.listdir(INSIGHTS_DIR)):
        if not filename.endswith('.html'):
            continue
        if filename == 'index.html':
            continue
        
        filepath = os.path.join(INSIGHTS_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        title, channel, duration, date, tags, excerpt = extract_meta(content)
        
        # 生成 slug
        slug = filename.replace('.html', '')
        
        notes.append({
            'title': title,
            'channel': channel,
            'duration': duration,
            'date': date,
            'tags': tags,
            'excerpt': excerpt,
            'slug': slug,
            'filename': filename
        })
    
    # 按日期排序（最新的在前）
    notes.sort(key=lambda x: x['date'], reverse=True)
    
    # 生成 HTML
    notes_html = ""
    for note in notes:
        tags_html = ''.join([f'<span class="tag">{tag}</span>' for tag in note['tags']])
        
        notes_html += f'''
            <article class="note-card">
                <h2><a href="./insights/{note['filename']}">{note['title']}</a></h2>
                <div class="note-meta">
                    <span>📺 {note['channel']}</span>
                    <span>⏱️ {note['duration']}</span>
                    <span>📅 {note['date']}</span>
                </div>
                <div class="note-tags">{tags_html}</div>
                <p class="note-excerpt">{note['excerpt']}</p>
            </article>
'''
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>小视频大思考 - 深度笔记</title>
    <style>
        :root {{ --primary: #2563eb; --secondary: #64748b; --bg: #f8fafc; --card-bg: #ffffff; --text: #1e293b; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; padding: 2rem 1rem; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        header {{ text-align: center; margin-bottom: 3rem; padding: 2rem 0; }}
        h1 {{ font-size: 2.5rem; color: var(--primary); margin-bottom: 0.5rem; }}
        .subtitle {{ color: var(--secondary); font-size: 1.1rem; }}
        .stats {{ color: var(--secondary); font-size: 0.9rem; margin-top: 0.5rem; }}
        .notes-grid {{ display: grid; gap: 1.5rem; }}
        .note-card {{ background: var(--card-bg); border-radius: 12px; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); transition: transform 0.2s, box-shadow 0.2s; }}
        .note-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
        .note-card h2 {{ font-size: 1.25rem; margin-bottom: 0.75rem; }}
        .note-card h2 a {{ color: var(--text); text-decoration: none; }}
        .note-card h2 a:hover {{ color: var(--primary); }}
        .note-meta {{ display: flex; gap: 1rem; font-size: 0.875rem; color: var(--secondary); margin-bottom: 1rem; flex-wrap: wrap; }}
        .note-tags {{ display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem; }}
        .tag {{ background: #e0e7ff; color: var(--primary); padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; }}
        .note-excerpt {{ color: var(--secondary); font-size: 0.95rem; }}
        footer {{ text-align: center; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #e2e8f0; color: var(--secondary); }}
        .paw {{ font-size: 1.5rem; }}
        .search-box {{ margin-bottom: 2rem; }}
        .search-box input {{ width: 100%; padding: 0.75rem 1rem; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 1rem; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📺 小视频大思考</h1>
            <p class="subtitle">深度视频笔记 · 每日更新</p>
            <p class="stats">已整理 {len(notes)} 篇深度笔记</p>
        </header>

        <div class="search-box">
            <input type="text" id="search" placeholder="🔍 搜索笔记..." onkeyup="filterNotes()">
        </div>

        <main class="notes-grid">
{notes_html}
        </main>

        <footer>
            <p>由小爪 <span class="paw">🐾</span> 整理 · 每晚更新，晨间阅读</p>
            <p style="margin-top: 0.5rem;"><a href="https://github.com/zhewenzhang/video-notes" style="color: var(--secondary);">GitHub</a></p>
        </footer>
    </div>
    
    <script>
        function filterNotes() {{
            const input = document.getElementById('search');
            const filter = input.value.toLowerCase();
            const cards = document.querySelectorAll('.note-card');
            cards.forEach(card => {{
                const text = card.textContent.toLowerCase();
                card.style.display = text.includes(filter) ? '' : 'none';
            }});
        }}
    </script>
</body>
</html>'''
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 索引页已生成：{len(notes)} 篇笔记")

if __name__ == '__main__':
    main()
