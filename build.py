#!/usr/bin/env python3
"""
build.py - 小视频大思考 静态站点构建器
从 notes/ 目录的 Markdown 文件生成完整的静态网站。
用法: python3 build.py
"""
import os
import re
import json
import glob
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(SCRIPT_DIR, "notes")
OUTPUT_DIR = SCRIPT_DIR

def parse_frontmatter(content):
    """解析 YAML frontmatter"""
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            fm_text = content[3:end].strip()
            body = content[end+3:].strip()
            meta = {}
            for line in fm_text.split("\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip()
                    if val.startswith("[") and val.endswith("]"):
                        val = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",") if v.strip()]
                    meta[key] = val
            return meta, body
    return {}, content

def md_to_html(md_text):
    """简易 Markdown → HTML 转换"""
    lines = md_text.split("\n")
    html_parts = []
    in_code = False
    in_table = False
    table_rows = []
    
    for line in lines:
        # Code blocks
        if line.strip().startswith("```"):
            if in_code:
                html_parts.append("</code></pre>")
                in_code = False
            else:
                lang = line.strip()[3:]
                html_parts.append(f'<pre><code class="{lang}">')
                in_code = True
            continue
        if in_code:
            html_parts.append(line.replace("<", "&lt;").replace(">", "&gt;"))
            continue
        
        # Table
        if "|" in line and line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                continue  # separator row
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(cells)
            continue
        elif in_table:
            html_parts.append(render_table(table_rows))
            in_table = False
            table_rows = []
        
        # Headers
        if line.startswith("### "):
            html_parts.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("## "):
            html_parts.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            html_parts.append(f"<h1>{line[2:]}</h1>")
        elif line.strip() == "":
            html_parts.append("")
        elif line.startswith("> "):
            html_parts.append(f"<blockquote>{line[2:]}</blockquote>")
        elif line.startswith("- ") or line.startswith("* "):
            html_parts.append(f"<p>• {line[2:]}</p>")
        elif re.match(r'^\d+\.', line):
            html_parts.append(f"<p>{line}</p>")
        else:
            # Inline formatting
            line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
            line = re.sub(r'\*(.+?)\*', r'<em>\1</em>', line)
            line = re.sub(r'`(.+?)`', r'<code>\1</code>', line)
            html_parts.append(f"<p>{line}</p>")
    
    if in_table:
        html_parts.append(render_table(table_rows))
    
    return "\n".join(html_parts)

def render_table(rows):
    """渲染 HTML 表格"""
    if not rows:
        return ""
    html = '<table class="content-table"><thead><tr>'
    for cell in rows[0]:
        html += f"<th>{cell}</th>"
    html += "</tr></thead><tbody>"
    for row in rows[1:]:
        html += "<tr>"
        for cell in row:
            html += f"<td>{cell}</td>"
        html += "</tr>"
    html += "</tbody></table>"
    return html

def build_article(meta, body, filename):
    """生成单篇文章 HTML"""
    title = meta.get("title", filename)
    channel = meta.get("channel", "")
    duration = meta.get("duration", "")
    date = meta.get("date", "")
    tags = meta.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    
    content_html = md_to_html(body)
    
    tags_html = ""
    if tags:
        tag_items = "".join(f'<span class="note-tag">{t}</span>' for t in tags)
        tags_html = f'<div class="note-tags">{tag_items}</div>'
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} - 小视频大思考</title>
<meta property="og:title" content="{title}">
<meta property="og:description" content="来自{channel}的深度视频笔记">
<meta property="og:type" content="article">
<link rel="stylesheet" href="../style.css">
</head>
<body>
<div class="wrap">
<a href="../index.html" class="back-link">← 返回目录</a>
<header class="article-header">
<h1>{title}</h1>
<div class="article-meta">
<span>{channel}</span>
<span>{duration}</span>
<span>{date}</span>
</div>
{tags_html}
</header>
<article class="article-content">
{content_html}
</article>
<footer class="site-footer">
<p>由小爪 🐾 整理 · 每晚更新，晨间阅读</p>
<p><a href="https://github.com/zhewenzhang/video-notes">GitHub</a></p>
</footer>
</div>
<script>
document.addEventListener("DOMContentLoaded",function(){{
  const f=document.querySelector(".fab");
  window.addEventListener("scroll",()=>{{f.classList.toggle("visible",window.scrollY>300)}});
  f.addEventListener("click",()=>{{window.scrollTo({{top:0,behavior:"smooth"}})}});
}});
</script>
<button class="fab">↑</button>
</body>
</html>'''

def build_index(notes_data):
    """生成 index.html"""
    notes_json = json.dumps(notes_data, ensure_ascii=False)
    channels = sorted(set(n.get("channel", "") for n in notes_data if n.get("channel")))
    all_tags = set()
    for n in notes_data:
        for t in n.get("tags", []):
            all_tags.add(t)
    tags = sorted(all_tags)
    channels_json = json.dumps(channels, ensure_ascii=False)
    tags_json = json.dumps(tags, ensure_ascii=False)
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>小视频大思考</title>
<meta property="og:title" content="小视频大思考">
<meta property="og:description" content="深度视频笔记 · 每日更新">
<meta name="description" content="AI时代精选视频笔记，涵盖a16z、Lex Fridman、All-In Podcast等顶级频道的深度内容">
<link rel="alternate" type="application/rss+xml" title="小视频大思考 RSS" href="feed.xml">
<link rel="stylesheet" href="style.css">
</head>
<body>
<div class="wrap">
<header class="masthead">
<div class="masthead-eyebrow">Video Notes Collection</div>
<h1>小视频大思考</h1>
<p>深度视频笔记 · 每日更新</p>
</header>
<div class="stats-bar">
<div class="stat-item"><div class="stat-num" id="totalCount">{len(notes_data)}</div><div class="stat-label">篇笔记</div></div>
<div class="stat-item"><div class="stat-num">{len(channels)}</div><div class="stat-label">个频道</div></div>
<div class="stat-item"><div class="stat-num">{len(tags)}</div><div class="stat-label">个标签</div></div>
</div>
<div class="search-wrap">
<input type="text" id="searchInput" placeholder="搜索笔记...">
</div>
<div class="filters">
<div class="filter-header">
<span class="filter-title">筛选 <span id="resultCount">{len(notes_data)}</span> 篇</span>
<span class="filter-toggle">▼</span>
</div>
<div class="filter-body">
<div class="filter-section">
<div class="filter-label">频道</div>
<div class="filter-options" id="chList"></div>
</div>
<div class="filter-section">
<div class="filter-label">标签</div>
<div class="filter-options" id="tagList"></div>
</div>
<div class="filter-section">
<div class="filter-label">日期</div>
<div class="filter-options">
<button class="filter-btn active" data-filter="date" data-value="all">全部</button>
<button class="filter-btn" data-filter="date" data-value="week">本周</button>
<button class="filter-btn" data-filter="date" data-value="month">本月</button>
</div>
</div>
<div class="filter-section">
<div class="filter-label">排序</div>
<div class="filter-options">
<button class="filter-btn active" data-filter="sort" data-value="new">最新</button>
<button class="filter-btn" data-filter="sort" data-value="old">最早</button>
<button class="filter-btn" data-filter="sort" data-value="channel">频道</button>
</div>
</div>
<button class="clear-btn" id="clearBtn">清除筛选</button>
</div>
</div>
<main class="notes" id="notes"></main>
<footer class="site-footer">
<p>由小爪 🐾 整理 · 每晚更新，晨间阅读</p>
<p><a href="https://github.com/zhewenzhang/video-notes">GitHub</a></p>
</footer>
</div>
<button class="fab">↑</button>
<script>
const NOTES={notes_json};
const CHANNELS={channels_json};
const TAGS={tags_json};

function render(notes) {{
  const c=document.getElementById("notes");
  if(!notes.length){{c.innerHTML='<div class="empty"><div class="empty-icon">📭</div><h3>没有找到匹配的笔记</h3><p>试试其他搜索词或筛选条件</p></div>';document.getElementById("resultCount").textContent="0";return}}
  document.getElementById("resultCount").textContent=notes.length;
  c.innerHTML=notes.map((n,i)=>`<div class="note-card"><span class="note-number">${{String(i+1).padStart(2,"0")}}</span><div class="note-meta"><span>${{n.channel||""}}</span><span>${{n.duration||""}}</span><span>${{n.date||""}}</span></div><h2><a href="insights/${{n.file}}">${{n.title}}</a></h2>${{n.tags&&n.tags.length?`<div class="note-tags">${{n.tags.map(t=>`<span class="note-tag">${{t}}</span>`).join("")}}</div>`:""}}<p class="note-summary">${{n.summary||"点击查看详情..."}}</p></div>`).join("")
}}

// Filters
let activeFilters={{channel:null,tag:null,date:"all",sort:"new"}};

function applyFilters() {{
  let filtered=[...NOTES];
  if(activeFilters.channel) filtered=filtered.filter(n=>n.channel===activeFilters.channel);
  if(activeFilters.tag) filtered=filtered.filter(n=>n.tags&&n.tags.includes(activeFilters.tag));
  if(activeFilters.date==="week") {{
    const weekAgo=new Date();weekAgo.setDate(weekAgo.getDate()-7);
    filtered=filtered.filter(n=>n.date&&new Date(n.date)>=weekAgo);
  }} else if(activeFilters.date==="month") {{
    const monthAgo=new Date();monthAgo.setDate(monthAgo.getDate()-30);
    filtered=filtered.filter(n=>n.date&&new Date(n.date)>=monthAgo);
  }}
  const q=document.getElementById("searchInput").value.toLowerCase();
  if(q) filtered=filtered.filter(n=>(n.title+" "+n.summary+" "+n.channel+" "+(n.tags||[]).join(" ")).toLowerCase().includes(q));
  if(activeFilters.sort==="new") filtered.sort((a,b)=>(b.date||"").localeCompare(a.date||""));
  else if(activeFilters.sort==="old") filtered.sort((a,b)=>(a.date||"").localeCompare(b.date||""));
  else if(activeFilters.sort==="channel") filtered.sort((a,b)=>(a.channel||"").localeCompare(b.channel||""));
  render(filtered);
}}

// Init channel buttons
const chList=document.getElementById("chList");
CHANNELS.forEach(ch=>{{const b=document.createElement("button");b.className="filter-btn small";b.dataset.filter="channel";b.dataset.value=ch;b.textContent=ch;b.onclick=()=>{{activeFilters.channel=activeFilters.channel===ch?null:ch;document.querySelectorAll('[data-filter="channel"]').forEach(x=>x.classList.toggle("active",x.dataset.value===activeFilters.channel));applyFilters()}};chList.appendChild(b)}});

// Init tag buttons
const tagList=document.getElementById("tagList");
TAGS.forEach(t=>{{const b=document.createElement("button");b.className="filter-btn small";b.dataset.filter="tag";b.dataset.value=t;b.textContent=t;b.onclick=()=>{{activeFilters.tag=activeFilters.tag===t?null:t;document.querySelectorAll('[data-filter="tag"]').forEach(x=>x.classList.toggle("active",x.dataset.value===activeFilters.tag));applyFilters()}};tagList.appendChild(b)}});

// Date & Sort buttons
document.querySelectorAll('[data-filter="date"]').forEach(b=>b.onclick=()=>{{activeFilters.date=b.dataset.value;document.querySelectorAll('[data-filter="date"]').forEach(x=>x.classList.remove("active"));b.classList.add("active");applyFilters()}});
document.querySelectorAll('[data-filter="sort"]').forEach(b=>b.onclick=()=>{{activeFilters.sort=b.dataset.value;document.querySelectorAll('[data-filter="sort"]').forEach(x=>x.classList.remove("active"));b.classList.add("active");applyFilters()}});

// Search
document.getElementById("searchInput").addEventListener("input",applyFilters);

// Clear
document.getElementById("clearBtn").addEventListener("click",()=>{{activeFilters={{channel:null,tag:null,date:"all",sort:"new"}};document.getElementById("searchInput").value="";document.querySelectorAll(".filter-btn").forEach(b=>b.classList.remove("active"));document.querySelector('[data-value="all"]').classList.add("active");document.querySelector('[data-value="new"]').classList.add("active");applyFilters()}});

// Toggle filters
document.querySelector(".filter-header").addEventListener("click",()=>document.querySelector(".filters").classList.toggle("open"));

// Scroll to top
const fab=document.querySelector(".fab");
window.addEventListener("scroll",()=>{{fab.classList.toggle("visible",window.scrollY>300)}});
fab.addEventListener("click",()=>{{window.scrollTo({{top:0,behavior:"smooth"}})}});

render(NOTES);
</script>
</body>
</html>'''

def build_rss(notes_data):
    """生成 RSS feed"""
    items = ""
    for n in sorted(notes_data, key=lambda x: x.get("date", ""), reverse=True)[:20]:
        items += f"""<item>
<title>{n.get('title', '')}</title>
<link>https://zhewenzhang.github.io/video-notes/insights/{n.get('file', '')}</link>
<description>{n.get('summary', '')}</description>
<pubDate>{n.get('date', '')}</pubDate>
</item>
"""
    
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>小视频大思考</title>
<link>https://zhewenzhang.github.io/video-notes/</link>
<description>深度视频笔记 · 每日更新</description>
{items}
</channel>
</rss>"""

def main():
    notes_data = []
    md_files = sorted(glob.glob(os.path.join(NOTES_DIR, "*.md")))
    
    if not md_files:
        print("⚠️  notes/ 目录为空，跳过构建。")
        return
    
    print(f"📝 找到 {len(md_files)} 个 Markdown 文件")
    
    for md_file in md_files:
        filename = os.path.basename(md_file).replace(".md", "")
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        meta, body = parse_frontmatter(content)
        
        # Generate article HTML
        html = build_article(meta, body, filename)
        out_file = os.path.join(OUTPUT_DIR, "insights", f"{filename}.html")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(html)
        
        # Collect metadata for index
        tags = meta.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        
        notes_data.append({
            "file": f"{filename}.html",
            "title": meta.get("title", filename),
            "channel": meta.get("channel", ""),
            "duration": meta.get("duration", ""),
            "date": meta.get("date", ""),
            "tags": tags,
            "summary": meta.get("summary", body[:120] + "...")
        })
        print(f"  ✅ {filename}")
    
    # Sort by date desc
    notes_data.sort(key=lambda x: x.get("date", ""), reverse=True)
    
    # Generate index.html
    index_html = build_index(notes_data)
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"✅ index.html 已生成 ({len(notes_data)} 篇笔记)")
    
    # Generate RSS
    rss = build_rss(notes_data)
    with open(os.path.join(OUTPUT_DIR, "feed.xml"), "w", encoding="utf-8") as f:
        f.write(rss)
    print("✅ feed.xml (RSS) 已生成")
    
    print(f"\n🎉 构建完成！共 {len(notes_data)} 篇笔记")

if __name__ == "__main__":
    main()
