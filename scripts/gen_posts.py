#!/usr/bin/env python3
"""
Xの投稿案を毎朝まとめて生成するスクリプト
生成された下書きを人が見て、良いものを選んで自分でXに貼る運用です。
"""

import os
import sys
import json
import datetime
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT, "posts")
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"

PROFILE = """発信者: 現役大学生で、業務自動化エンジニア。
ClaudeなどのAIを使って「面倒な作業を自動でやる仕組み」を作っている。
実物として、毎朝AIが記事を自動生成するWebサイトをGitHub Actionsで運用中(サーバー代0円)。

届けたい相手:
1. 中小企業・店舗の経営者(人手不足、手作業に疲れている)
2. AI初心者(「AIって結局どう使うの?」と思っている人)

発信の軸:
「初心者だった自分がここまで作れるようになった。あなたの業務でも同じことができる」
という橋渡し。自慢でもノウハウの垂れ流しでもなく、相手の仕事に引きつける。"""

POST_TYPES = [
    "共感フック型: 読者の『あるある』な悩み(手作業、コピペ地獄、AIへの苦手意識)から入り、解決の糸口を1つ示す",
    "実物公開型: 自分が作った自動化の仕組みを具体的に紹介し、『これがサーバー代0円で動いている』と実物で語る",
    "初心者向けTips型: AIを使う上での具体的で小さなコツを1つ、専門用語を避けて教える",
    "ビフォーアフター型: 『手作業だと〇時間→自動化で〇分』のように、業務が変わる様子を数字で見せる",
    "問いかけ型: 経営者や個人事業主に『こういう作業、まだ手でやっていませんか?』と問いかけ、相談のきっかけを作る",
]

SYSTEM_PROMPT = f"""あなたはX(旧Twitter)の投稿を作るプロの構成作家です。
以下の発信者になりきって、その日の投稿案を作ります。

{PROFILE}

Xで伸びる投稿の鉄則:
- 最初の1行(フック)がすべて。スクロールの手を止めさせる
- 1投稿1メッセージ。欲張らない
- 専門用語を避け、中学生でも分かる言葉で
- 「私はすごい」ではなく「あなたにもできる/あなたの役に立つ」の視点
- 絵文字は使いすぎない(0〜2個)
- 140字以内(日本語)。長すぎない
- ハッシュタグは付けても1〜2個まで。無理なら付けない
- 煽り・誇大表現・「稼げる」系のワードは絶対に使わない(信頼を失う)

必ず次のJSON形式のみで出力。前置き・コードブロック記法は一切なし:
{{"posts":[{{"type":"投稿の型の名前","hook":"最初の1行だけ抜き出したもの","text":"投稿本文(140字以内)","note":"この投稿の狙いを一言(自分用メモ)"}}]}}"""


def call_claude():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY が設定されていません")
    types_text = "\n".join(f"{i+1}. {t}" for i, t in enumerate(POST_TYPES))
    user_msg = f"""今日の投稿案を、次の5つの型で1本ずつ、合計5本作ってください。
各型の投稿が互いに似ないよう、話題を変えてください。

{types_text}"""
    payload = {
        "model": MODEL,
        "max_tokens": 2000,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_msg}],
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


def save_posts(result):
    os.makedirs(POSTS_DIR, exist_ok=True)
    today = datetime.date.today().isoformat()
    path = os.path.join(POSTS_DIR, f"{today}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"date": today, "posts": result.get("posts", [])},
                  f, ensure_ascii=False, indent=2)
    return path, len(result.get("posts", []))


def main():
    print("投稿案を生成中...")
    result = call_claude()
    path, n = save_posts(result)
    print(f"保存しました: {os.path.relpath(path, ROOT)}")
    print(f"投稿案 {n}本を生成しました")


if __name__ == "__main__":
    main()
