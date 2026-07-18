# 7日間の自動運転を始める手順

このデモを実際にGitHubで走らせて、「7日で7記事が自動で増えた」という
実績スクリーンショットを作るまでの手順です。所要15分。

---

## 1. リポジトリを作る

GitHubで新規リポジトリを作成します。

- 名前: `ai-auto-site-demo`(何でもよい)
- 公開設定: **Public を推奨**
  - Privateだと営業時にURLを見せられません
  - Publicなら「実際に動いています」とリンクを出せます
  - GitHub ActionsもPublicなら完全無料(Privateは月2000分の制限あり)

## 2. ファイルを置いてpushする

ダウンロードした `ai-auto-site` フォルダの中で、ターミナルを開いて:

```
git init
git add .
git commit -m "AI自動更新サイトの初期構築"
git branch -M main
git remote add origin https://github.com/<あなたのユーザー名>/ai-auto-site-demo.git
git push -u origin main
```

※ PowerShellで複数行がうまく動かない場合は、1行ずつ実行してください。

## 3. APIキーを登録する

GitHubのリポジトリページで:

1. Settings → Secrets and variables → Actions
2. 「New repository secret」を押す
3. Name: `ANTHROPIC_API_KEY`
4. Secret: あなたのClaude APIキー(`sk-ant-` で始まる文字列)
5. 「Add secret」

**注意:** このキーは絶対にコードに直接書かないこと。Secretsに入れれば、
GitHubのログにも表示されず、他人からも見えません。

## 4. 書き込み権限を有効にする

これを忘れると、記事は生成されるのにコミットで失敗します。

1. Settings → Actions → General
2. 一番下の「Workflow permissions」
3. **「Read and write permissions」** を選択
4. Save

## 5. 動作確認(初回は手動で回す)

1. Actions タブを開く
2. 左のリストから「記事の自動生成」を選ぶ
3. 右の「Run workflow」→「Run workflow」を押す
4. 2〜3分待つ

緑のチェックがついたら成功です。`content/` に記事が1本増えているはずです。

## 6. あとは放置

翌朝7時から、毎日1本ずつ自動で増えます。
`keywords.txt` に8個キーワードが入っているので、8日分は勝手に動きます。

---

## 7日後にやること(営業材料の作成)

### スクリーンショットを2枚撮る

**1枚目: Actionsの実行履歴**
Actions タブを開くと、緑のチェックが7つ縦に並んでいます。
日付が毎日連続していることが一目で分かる状態で撮影。
→ これが「本当に自動で動いている」証拠になります。

**2枚目: 記事一覧ページ**
`site/index.html` をブラウザで開いて、記事が7本並んでいる状態を撮影。
→ これが「成果物」の証拠になります。

### GitHub Pages で公開する(任意・推奨)

営業でURLを見せられるようにするなら:

1. Settings → Pages
2. Source: 「Deploy from a branch」
3. Branch: `main` / フォルダ: `/site` を選択
4. Save

数分後に `https://<ユーザー名>.github.io/ai-auto-site-demo/` で公開されます。
**これも無料です。**

「このサイト、私は一切触っていません。毎朝AIが勝手に書いています」と
言えるURLが手に入ります。営業では実物のURLが一番強いです。

---

## トラブル時

| 症状 | 原因 |
|---|---|
| Actionsが赤くなる | APIキーが未登録か、間違っている |
| 記事は増えるがpushで失敗 | 手順4の書き込み権限が未設定 |
| 「変更なし」と出る | keywords.txt のキーワードを使い切った |
| APIエラー | Anthropicの残高切れ。コンソールで確認 |

## 費用について

7日間走らせても、かかるのは記事7本分のAPI代(**約50〜100円**)だけです。
GitHub Actions、GitHub Pages はいずれも無料枠の範囲内です。
