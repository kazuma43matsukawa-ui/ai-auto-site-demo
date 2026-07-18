#!/usr/bin/env python3
import os
import re
import sys
import json
import datetime
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYWORDS_FILE = os.path.join(ROOT, "keywords.txt")
CONTENT_DIR = os.path.join(ROOT, "content")
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """あなたは地方創生・地域DXに詳しい実務家のライターです。
中小企業の新規事業担当者に向けて、SEOに強く、かつ読み応えのある記事を書きます。

必ず守ること:
- 事実として確認できないことは書かない。統計や固有名詞をでっち上げない
- 一般論で終わらせず、具体的な打ち手まで踏み込む
- 「〜ではないでしょうか」のような曖昧な締め方をしない
- 見出しは検索意図に沿ってつける
- 1500〜2000字程度

出力は必ず次のJSON形式のみ。前置きやコードブロック記法は一切つけない:
{"title":"記事タイトル(32字以内)","description":"検索結果に出る説明文(100字前後)","tags":["タグ1","タグ2"],"body":"本文(Markdown形式。h2は##、h3は###を使う。タイトルは本文に含めない)"}"""


def load_keywords():
    if not os.path.exists(KEYWORDS_FILE):
        sys.exit(f"キーワードファイルが見つかりません: {KEYWORDS_FILE}")
    with open(KEYWORDS_FILE, encoding="utf-8") as f:
        lines = f.read().splitlines()
    pending = [(i, l.strip()) for i, l in enumerate(lines)
               if l.strip() and not l.startswith("#")]
    return lines, pending


def mark_done(lines, index):
    lines[index] = "# " + lines[index]
    with open(KEYWORDS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def call_claude(keyword):
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY が設定されていません")
    payload = {
        "model": MODEL,
        "max_tokens": 4000,
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user",
             "content": f"次のキーワードで記事を書いてください: {keyword}"}
        ],
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req, timeout=180) as res:
        data = json.loads(res.read().decode("utf-8"))
    text = "".join(b.get("text", "") for b in data.get("content", [])
                   if b.get("type") == "text")
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)


def slugify(text):
    s = re.sub(r"[^\w\-]+", "-", text.lower()).strip("-")
    if not s or not re.search(r"[a-z0-9]", s):
        s = datetime.datetime.now().strftime("post-%Y%m%d-%H%M")
    return s[:50]


def save_article(article, keyword):
    os.makedirs(CONTENT_DIR, exist_ok=True)
    today = datetime.date.today().isoformat()
    slug = slugify(article.get("title", ""))
    path = os.path.join(CONTENT_DIR, f"{today}-{slug}.md")
    tags = article.get("tags", [])
    front = [
        "---",
        f'title: "{article["title"]}"',
        f'description: "{article["description"]}"',
        f"date: {today}",
        f"tags: [{', '.join(json.dumps(t, ensure_ascii=False) for t in tags)}]",
        f'keyword: "{keyword}"',
        "---",
        "",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(front) + article["body"].strip() + "\n")
    return path


def main():
    lines, pending = load_keywords()
    if not pending:
        print("未処理のキーワードがありません。keywords.txt に追記してください。")
        return
    index, keyword = pending[0]
    print(f"生成中: {keyword}")
    article = call_claude(keyword)
    path = save_article(article, keyword)
    mark_done(lines, index)
    print(f"保存しました: {os.path.relpath(path, ROOT)}")
    print(f"タイトル: {article['title']}")
    print(f"残りのキーワード: {len(pending) - 1}件")


if __name__ == "__main__":
    main()
