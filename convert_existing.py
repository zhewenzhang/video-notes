#!/usr/bin/env python3
"""将现有 HTML 笔记转换为 Markdown 源文件"""
import os
import re
import json
import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INSIGHTS_DIR = os.path.join(SCRIPT_DIR, "insights")
NOTES_DIR = os.path.join(SCRIPT_DIR, "notes")

def html_to_md(html_content):
    """简易 HTML → Markdown 转换"""
    text = html_content
    
    # Remove style/script tags
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
    
    # Extract article content
    article_match = re.search(r'<article[^>]*>(.*?)</article>', text, re.DOTALL)
    if article_match:
        text = article_match.group(1)
    
    # Headers
    text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', text, flags=re.DOTALL)
    text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', text, flags=re.DOTALL)
    text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', text, flags=re.DOTALL)
    
    # Bold/italic
    text = re.sub(r'<strong>(.*?)</strong>', r'**\1**', text, flags=re.DOTALL)
    text = re.sub(r'<em>(.*?)</em>', r'*\1*', text, flags=re.DOTALL)
    
    # Code
    text = re.sub(r'<code>(.*?)</code>', r'`\1`', text, flags=re.DOTALL)
    
    # Blockquote
    text = re.sub(r'<blockquote>(.*?)</blockquote>', r'> \1', text, flags=re.DOTALL)
    
    # Lists
    text = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', text, flags=re.DOTALL)
    
    # Paragraphs
    text = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n', text, flags=re.DOTALL)
    
    # Remove remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Clean up
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    # Decode HTML entities
    text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&quot;', '"')
    
    return text

def extract_meta_from_html(html_content):
    """从 HTML 中提取元数据"""
    meta = {}
    
    # Title from article header
    title_match = re.search(r'<h1>(.*?)</h1>', html_content)
    if title_match:
        meta['title'] = title_match.group(1).strip()
    
    # Meta spans (channel, duration, date)
    meta_match = re.search(r'<div class="article-meta">(.*?)</div>', html_content, re.DOTALL)
    if meta_match:
        spans = re.findall(r'<span>(.*?)</span>', meta_match.group(1))
        if len(spans) >= 1:
            meta['channel'] = spans[0]
        if len(spans) >= 2:
            meta['duration'] = spans[1]
        if len(spans) >= 3:
            meta['date'] = spans[2]
    
    # Tags
    tags = re.findall(r'<span class="note-tag">(.*?)</span>', html_content)
    if tags:
        meta['tags'] = tags
    
    return meta

def main():
    os.makedirs(NOTES_DIR, exist_ok=True)
    
    html_files = sorted(glob.glob(os.path.join(INSIGHTS_DIR, "*.html")))
    print(f"找到 {len(html_files)} 个 HTML 文件")
    
    for html_file in html_files:
        basename = os.path.basename(html_file).replace(".html", "")
        
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        meta = extract_meta_from_html(html_content)
        md_body = html_to_md(html_content)
        
        # Build frontmatter
        fm_lines = ["---"]
        for key in ['title', 'channel', 'duration', 'date']:
            if key in meta:
                fm_lines.append(f"{key}: {meta[key]}")
        if 'tags' in meta:
            fm_lines.append(f"tags: {json.dumps(meta['tags'], ensure_ascii=False)}")
        fm_lines.append("---")
        
        md_content = "\n".join(fm_lines) + "\n\n" + md_body
        
        out_file = os.path.join(NOTES_DIR, f"{basename}.md")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(md_content)
        
        print(f"  ✅ {basename}.md")
    
    print(f"\n转换完成！共 {len(html_files)} 个文件")

if __name__ == "__main__":
    main()
