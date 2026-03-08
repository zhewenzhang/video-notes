#!/usr/bin/env python3
"""批量转换 markdown 笔记为 HTML"""

import os
import re
from datetime import datetime

SOURCE_DIR = "/Users/dave/clawd/memory/youtube-tracker/insights"
OUTPUT_DIR = "/Users/dave/video-notes/insights"

# 已转换的文件（跳过）
SKIP_FILES = [
    "marc-andreessen-ai-boom.html",
    "gavin-baker-gpu-tpu.html", 
    "henry-ellenbogen-1-percent.html"
]

def parse_markdown(content):
    """解析 markdown 内容"""
    lines = content.split('\n')
    
    title = ""
    channel = ""
    duration = ""
    date = ""
    tags = []
    body_lines = []
    in_tags = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 提取标题（第一个 H1）
        if line.startswith('# ') and not title:
            title = line[2:].strip()
            i += 1
            continue
        
        # 提取视频信息
        if '**频道：**' in line:
            channel = line.split('**频道：**')[1].strip()
        elif '**时长：**' in line:
            duration = line.split('**时长：**')[1].strip()
        elif '**日期**' in line or '**发布**' in line:
            date = line.split(':')[1].strip() if ':' in line else ""
        elif '📅' in line:
            date = line.split('📅')[1].strip() if '📅' in line else ""
        
        # 提取标签
        if '_标签：' in line:
            tag_part = line.split('_标签：')[1]
            tags = re.findall(r'#\w+', tag_part)
            i += 1
            continue
        
        # 跳过分隔线之前的元数据
        if line.startswith('---') and not body_lines:
            i += 1
            continue
        
        # 正文内容
        body_lines.append(line)
        i += 1
    
    body = '\n'.join(body_lines)
    return title, channel, duration, date, tags, body

def convert_md_to_html(md_content, filename):
    """转换 markdown 为 HTML"""
    title, channel, duration, date, tags, body = parse_markdown(md_content)
    
    # 生成 slug
    slug = filename.replace('.md', '')
    
    # 转换 markdown 语法
    html_body = body
    
    # H2
    html_body = re.sub(r'^## (.*?)$', r'<h3>\1</h3>', html_body, flags=re.MULTILINE)
    # H3
    html_body = re.sub(r'^### (.*?)$', r'<h4>\1</h4>', html_body, flags=re.MULTILINE)
    # Bold
    html_body = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_body)
    # Italic
    html_body = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_body)
    # Links
    html_body = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank">\1</a>', html_body)
    # Code
    html_body = re.sub(r'`(.*?)`', r'<code>\1</code>', html_body)
    
    # 列表
    html_body = re.sub(r'^- (.*?)$', r'<li>\1</li>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'^\d+\. (.*?)$', r'<li>\1</li>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'(<li>.*?</li>\n?)+', lambda m: '<ul>' + m.group(0) + '</ul>', html_body)
    
    # 引用
    html_body = re.sub(r'^> (.*?)$', r'<blockquote>\1</blockquote>', html_body, flags=re.MULTILINE)
    
    # 表格（简化处理）
    html_body = re.sub(r'^\| (.*?) \|$', r'<div class="table-row">\1</div>', html_body, flags=re.MULTILINE)
    
    # 段落
    paragraphs = re.split(r'\n\n+', html_body.strip())
    html_paragraphs = []
    for p in paragraphs:
        if p.strip() and not p.strip().startswith('<'):
            html_paragraphs.append(f'<p>{p.strip()}</p>')
        else:
            html_paragraphs.append(p.strip())
    
    html_body = '\n'.join(html_paragraphs)
    
    # 清理空标签
    html_body = re.sub(r'<ul>\s*</ul>', '', html_body)
    html_body = re.sub(r'</li>\n<li>', '</li><li>', html_body)
    
    return html_body, title, channel, duration, date, tags

def generate_html(title, channel, duration, date, tags, body, slug):
    """生成完整 HTML 页面"""
    tags_html = ''.join([f'<span class="tag">{tag}</span>' for tag in tags])
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 小视频大思考</title>
    <style>
        :root {{ --primary: #2563eb; --secondary: #64748b; --bg: #f8fafc; --card-bg: #ffffff; --text: #1e293b; --quote-bg: #f1f5f9; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.8; padding: 2rem 1rem; }}
        .container {{ max-width: 700px; margin: 0 auto; }}
        .back-link {{ display: inline-block; margin-bottom: 1.5rem; color: var(--primary); text-decoration: none; }}
        .back-link:hover {{ text-decoration: underline; }}
        article {{ background: var(--card-bg); border-radius: 12px; padding: 2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        h1 {{ font-size: 1.75rem; margin-bottom: 1rem; }}
        .meta {{ display: flex; gap: 1rem; color: var(--secondary); font-size: 0.875rem; margin-bottom: 1.5rem; flex-wrap: wrap; }}
        .tags {{ display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 2rem; }}
        .tag {{ background: #e0e7ff; color: var(--primary); padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; }}
        h3 {{ font-size: 1.25rem; margin: 2rem 0 1rem; color: var(--text); }}
        h4 {{ font-size: 1rem; margin: 1.5rem 0 0.75rem; color: var(--secondary); }}
        ul {{ margin-left: 1.5rem; margin-bottom: 1rem; }}
        li {{ margin-bottom: 0.5rem; }}
        blockquote {{ background: var(--quote-bg); border-left: 4px solid var(--primary); padding: 1rem 1.5rem; margin: 1.5rem 0; font-style: italic; color: var(--secondary); }}
        blockquote strong {{ color: var(--text); font-style: normal; }}
        a {{ color: var(--primary); }}
        .youtube-link {{ display: inline-block; background: #ff0000; color: white; padding: 0.75rem 1.5rem; border-radius: 8px; text-decoration: none; margin: 1.5rem 0; font-weight: 500; }}
        .youtube-link:hover {{ background: #cc0000; }}
        table {{ width: 100%; border-collapse: collapse; margin: 1.5rem 0; }}
        th, td {{ border: 1px solid #e2e8f0; padding: 0.75rem; text-align: left; }}
        th {{ background: #f8fafc; font-weight: 600; }}
        code {{ background: #f1f5f9; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.9em; }}
        .table-row {{ padding: 0.5rem; border-bottom: 1px solid #e2e8f0; }}
    </style>
</head>
<body>
    <div class="container">
        <a href="../index.html" class="back-link">← 返回索引</a>
        <article>
            <h1>{title}</h1>
            <div class="meta">
                <span>📺 {channel}</span>
                <span>⏱️ {duration}</span>
                <span>📅 {date if date else "2026-03"}</span>
            </div>
            <div class="tags">{tags_html}</div>
            <div class="content">{body}</div>
        </article>
        <footer style="text-align: center; margin-top: 2rem; color: var(--secondary); padding: 1rem;">
            <p>由小爪 🐾 整理 · <a href="../index.html">返回索引</a></p>
        </footer>
    </div>
</body>
</html>'''
    return html

def main():
    converted = 0
    skipped = 0
    
    for filename in os.listdir(SOURCE_DIR):
        if not filename.endswith('.md'):
            continue
        
        html_filename = filename.replace('.md', '.html')
        if html_filename in SKIP_FILES:
            skipped += 1
            print(f"⏭️  跳过：{html_filename}")
            continue
        
        # 读取 markdown
        with open(os.path.join(SOURCE_DIR, filename), 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # 转换
        body, title, channel, duration, date, tags = convert_md_to_html(md_content, filename)
        html = generate_html(title, channel, duration, date, tags, body, filename)
        
        # 写入
        output_path = os.path.join(OUTPUT_DIR, html_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        converted += 1
        print(f"✅ 转换：{html_filename}")
    
    print(f"\n🎉 完成！转换 {converted} 篇，跳过 {skipped} 篇")

if __name__ == '__main__':
    main()
