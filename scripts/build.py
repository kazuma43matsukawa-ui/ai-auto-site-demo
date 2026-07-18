#!/usr/bin/env python3
import os
import re
import html
import json
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DIR = os.path.join(ROOT, "content")
SITE_DIR = os.path.join(ROOT, "site")
SITE_NAME = "地方進出支援・ビジネス・インタープリター"
SITE_URL = "https://example.com"


def md_to_html(md):
    lines = md.split("\n")
    out, in_list, in_code = [], False, False

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    for line in lines:
        if line.startswith("```"):
            close_list()
            out.append("</pre>" if in_code else "<pre>")
            in_code = not in_code
            continue
        if in_code:
            out.append(html.escape(line))
            continue
        if not line.strip():
            close_list()
            continue
        m = re.match(r"^(#{2,4})\s+(.*)", line)
        if m:
            close_list()
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            continue
        if re.match(r"^[-*]\s+", line):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline(re.sub(r'^[-*]\s+', '', line))}</li>")
            continue
        close_list()
        out.append(f"<p>{inline(line)}</p>")
    close_list()
    return "\n".join(out)


def inline(text):
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    return text


def parse_article(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    if not raw.startswith("---"):
        return None
    _, front, body = raw.split("---", 2)
    meta = {}
    for line in front.strip().split("\n"):
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            try:
                v = json.loads(v)
            except Exception:
                v = []
        else:
            v = v.strip('"')
        meta[k.strip()] = v
    meta["body"] = body.strip()
    meta["slug"] = os.path.basename(path).replace(".md", "")
    return meta


def load_articles():
    if not os.path.isdir(CONTENT_DIR):
        return []
    items = []
    for name in sorted(os.listdir(CONTENT_DIR), reverse=True):
        if name.endswith(".md"):
            a = parse_article(os.path.join(CONTENT_DIR, name))
            if a:
                items.append(a)
    return items


STYLE = """
:root{
  --ink:#14161a; --ink-soft:#565b66; --line:#e2e4e9;
  --paper:#ffffff; --wash:#f5f6f8; --seal:#9c2b2b;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"Hiragino Sans","Yu Gothic",sans-serif;color:var(--ink);background:var(--paper);line-height:1.9;-webkit-font-smoothing:antialiased}
.wrap{max-width:720px;margin:0 auto;padding:0 24px}
header{border-bottom:1px solid var(--line);padding:28px 0;margin-bottom:56px}
header .wrap{display:flex;align-items:baseline;justify-content:space-between;gap:16px}
.brand{font-size:15px;font-weight:700;letter-spacing:.04em;color:var(--ink);text-decoration:none}
.brand span{color:var(--seal)}
nav a{font-size:13px;color:var(--ink-soft);text-decoration:none;margin-left:20px}
nav a:hover{color:var(--ink)}
h1{font-size:31px;line-height:1.5;letter-spacing:-.01em;margin-bottom:16px;font-weight:700}
h2{font-size:20px;margin:44px 0 14px;padding-left:13px;border-left:3px solid var(--seal);line-height:1.5}
h3{font-size:16px;margin:30px 0 10px;color:var(--ink)}
p{margin:0 0 18px}
ul{margin:0 0 18px 22px}
li{margin-bottom:7px}
pre{background:var(--wash);padding:16px;overflow-x:auto;border-radius:4px;font-size:13px;margin-bottom:18px}
code{background:var(--wash);padding:2px 5px;border-radius:3px;font-size:.9em}
a{color:var(--seal)}
.meta{font-size:13px;color:var(--ink-soft);margin-bottom:40px;padding-bottom:20px;border-bottom:1px solid var(--line)}
.tag{display:inline-block;font-size:11px;background:var(--wash);color:var(--ink-soft);padding:3px 9px;border-radius:2px;margin-right:6px}
.list{list-style:none;margin:0}
.list li{border-bottom:1px solid var(--line);margin:0}
.list a{display:block;padding:22px 0;text-decoration:none;color:var(--ink)}
.list a:hover .t{color:var(--seal)}
.list .d{font-size:12px;color:var(--ink-soft);letter-spacing:.06em;margin-bottom:5px}
.list .t{font-size:17px;font-weight:700;line-height:1.5;margin-bottom:6px;transition:color .15s}
.list .s{font-size:13px;color:var(--ink-soft);line-height:1.7}
.lead{font-size:15px;color:var(--ink-soft);margin-bottom:48px;padding-bottom:28px;border-bottom:1px solid var(--line)}
footer{margin-top:80px;padding:28px 0;border-top:1px solid var(--line);font-size:12px;color:var(--ink-soft);text-align:center}
.back{display:inline-block;margin-bottom:28px;font-size:13px;color:var(--ink-soft);text-decoration:none}
.back:hover{color:var(--seal)}
@media(max-width:600px){h1{font-size:24px}h2{font-size:18px}body{line-height:1.85}}
"""


def page(title, description, body, canonical=""):
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
{f'<link rel="canonical" href="{canonical}">' if canonical else ''}
<style>{STYLE}</style>
</head>
<body>
<header><div class="wrap">
  <a href="/" class="brand">CRIE<span>.</span> ビジネス・インタープリター</a>
  <nav><a href="/">コラム一覧</a></nav>
</div></header>
<div class="wrap">
{body}
<footer>株式会社クリエ ／ このページの記事は毎朝AIが自動生成しています</footer>
</div>
</body>
</html>"""


def build():
    os.makedirs(SITE_DIR, exist_ok=True)
    articles = load_articles()
    items = []
    for a in articles:
        items.append(f"""<li><a href="{a['slug']}.html">
  <div class="d">{a.get('date','')}</div>
  <div class="t">{html.escape(a.get('title',''))}</div>
  <div class="s">{html.escape(a.get('description',''))}</div>
</a></li>""")
    index_body = f"""<h1>地方進出のいま</h1>
<p class="lead">地域DX・実証実験・地方進出の現場で起きていることを、毎朝ひとつずつ書き足しています。全{len(articles)}記事。</p>
<ul class="list">{''.join(items) if items else '<li><a>記事はまだありません</a></li>'}</ul>"""
    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(page(f"コラム | {SITE_NAME}", "地域DX・地方進出に関する記事一覧", index_body))
    for a in articles:
        tags = "".join(f'<span class="tag">{html.escape(t)}</span>'
                       for t in a.get("tags", []) if isinstance(t, str))
        body = f"""<a href="/" class="back">← コラム一覧</a>
<h1>{html.escape(a.get('title',''))}</h1>
<div class="meta">{a.get('date','')}　{tags}</div>
{md_to_html(a['body'])}"""
        with open(os.path.join(SITE_DIR, f"{a['slug']}.html"), "w", encoding="utf-8") as f:
            f.write(page(f"{a.get('title','')} | {SITE_NAME}", a.get("description", ""), body, f"{SITE_URL}/{a['slug']}.html"))
    urls = [f"  <url><loc>{SITE_URL}/</loc></url>"]
    for a in articles:
        urls.append(f"  <url><loc>{SITE_URL}/{a['slug']}.html</loc><lastmod>{a.get('date','')}</lastmod></url>")
    with open(os.path.join(SITE_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n")
    print(f"ビルド完了: {len(articles)}記事 → site/")


if __name__ == "__main__":
    build()
