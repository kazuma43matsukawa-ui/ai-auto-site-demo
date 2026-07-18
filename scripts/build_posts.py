#!/usr/bin/env python3
"""
生成された投稿案を、スマホで見やすいHTMLページにまとめる
毎朝これをスマホで開き、良い投稿の「コピー」を押してXに貼るだけ。
"""

import os
import json
import html
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT, "posts")
DOCS_DIR = os.path.join(ROOT, "docs")


def load_all():
    if not os.path.isdir(POSTS_DIR):
        return []
    days = []
    for name in sorted(os.listdir(POSTS_DIR), reverse=True):
        if name.endswith(".json"):
            with open(os.path.join(POSTS_DIR, name), encoding="utf-8") as f:
                days.append(json.load(f))
    return days


PAGE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>今日の投稿案</title>
<style>
:root{{--ink:#0f1419;--soft:#536471;--line:#eff3f4;--brand:#1d9bf0;--ok:#00ba7c;--bg:#f7f9f9}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,"Hiragino Sans","Yu Gothic",sans-serif;background:var(--bg);color:var(--ink);line-height:1.7;padding:16px;max-width:560px;margin:0 auto}}
h1{{font-size:20px;margin-bottom:4px}}
.sub{{font-size:13px;color:var(--soft);margin-bottom:20px}}
.day{{margin-bottom:32px}}
.day-label{{font-size:12px;color:var(--soft);font-weight:700;letter-spacing:.04em;margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid var(--line)}}
.card{{background:#fff;border:1px solid var(--line);border-radius:16px;padding:16px;margin-bottom:12px}}
.type{{display:inline-block;font-size:11px;color:var(--brand);background:#e8f5fe;padding:3px 10px;border-radius:20px;margin-bottom:10px}}
.text{{font-size:15px;white-space:pre-wrap;margin-bottom:8px}}
.count{{font-size:12px;color:var(--soft)}}
.count.over{{color:#f4212e}}
.note{{font-size:12px;color:var(--soft);background:var(--bg);padding:8px 10px;border-radius:8px;margin:10px 0}}
.actions{{display:flex;gap:8px;margin-top:12px}}
button{{flex:1;border:0;border-radius:20px;padding:10px;font-size:14px;font-weight:700;cursor:pointer}}
.copy{{background:var(--ink);color:#fff}}
.copy.done{{background:var(--ok)}}
.post{{background:var(--brand);color:#fff;text-decoration:none;display:flex;align-items:center;justify-content:center}}
.empty{{text-align:center;color:var(--soft);padding:40px 0}}
</style>
</head>
<body>
<h1>今日の投稿案</h1>
<p class="sub">良いものを選んで、コピー→Xに貼るだけ。投稿は自分の手で。</p>
{body}
<script>
function copyText(id, btn){{
  const el = document.getElementById(id);
  navigator.clipboard.writeText(el.dataset.raw).then(()=>{{
    btn.textContent = "コピーしました";
    btn.classList.add("done");
    setTimeout(()=>{{btn.textContent="コピー";btn.classList.remove("done");}}, 1500);
  }});
}}
</script>
</body>
</html>"""


def build():
    os.makedirs(DOCS_DIR, exist_ok=True)
    days = load_all()
    if not days:
        body = '<div class="empty">まだ投稿案がありません</div>'
    else:
        blocks = []
        idx = 0
        for day in days:
            cards = []
            for p in day.get("posts", []):
                idx += 1
                cid = f"p{idx}"
                text = p.get("text", "")
                raw = html.escape(text, quote=True)
                length = len(text)
                over = " over" if length > 140 else ""
                intent = ""
                if p.get("note"):
                    intent = f'<div class="note">狙い: {html.escape(p.get("note",""))}</div>'
                share = "https://twitter.com/intent/tweet?text=" + urllib.parse.quote(text)
                cards.append(f"""<div class="card">
  <span class="type">{html.escape(p.get("type",""))}</span>
  <div class="text" id="{cid}" data-raw="{raw}">{html.escape(text)}</div>
  <div class="count{over}">{length} / 140字</div>
  {intent}
  <div class="actions">
    <button class="copy" onclick="copyText('{cid}', this)">コピー</button>
    <a class="post" href="{share}" target="_blank">Xで開く</a>
  </div>
</div>""")
            blocks.append(f'<div class="day"><div class="day-label">{day.get("date","")}</div>{"".join(cards)}</div>')
        body = "\n".join(blocks)
    with open(os.path.join(DOCS_DIR, "posts.html"), "w", encoding="utf-8") as f:
        f.write(PAGE.format(body=body))
    print(f"投稿案ページを作成: docs/posts.html ({len(days)}日分)")


if __name__ == "__main__":
    build()
