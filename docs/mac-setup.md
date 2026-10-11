# Mac での作業の始め方（Nagi Story Music LP）

Windows で進めてきた LP の管理を Mac に移すための手順書。
**この手順書を読んだ Claude へ**：上から順に進め、各ステップの「確認」が通ったら次へ。つまずいたら、エラーの内容を本人に見せて相談すること。
決定事項や進め方のルールは、リポジトリ直下の `CLAUDE.md`（特に冒頭の「今の状況と決定事項」）にある。作業を始める前に必ず読むこと。

---

## 0. 前提（大事）

- GitHub は **nagistorymusic** アカウントで作業する。このリポジトリ（`nagistorymusic/nagistorymusic.github.io`）はこちら
  - push の前に `gh auth status` で nagistorymusic が使われているか確認する
- アカウントの作成・パスワードの入力・ログインの許可は **本人がやる**（Claude は代わりにやらない）
- リポジトリは **public**（2026-10-11 に公開済み）。誰でも中身を見られるので、個人情報や非公開の情報を入れない

## 1. 道具を入れる

Homebrew が無ければ先に入れる（https://brew.sh の1行コマンド。本人のパスワード入力が必要）。

```bash
brew install git gh python ffmpeg
pip3 install Pillow
```

**確認**：次の4つがどれもバージョンを表示する。

```bash
git --version
gh --version
python3 --version   # 3.9 以上
ffmpeg -version
```

## 2. GitHub に nagistorymusic でログインする

```bash
gh auth login --hostname github.com --git-protocol https --web
```

- 「Authenticate Git with your GitHub credentials?」→ `Y`
- 表示された8文字のコードを、ブラウザで **nagistorymusic にログインした状態で** 入力して Authorize（本人が操作）

**確認**：`gh auth status` に `Logged in to github.com account nagistorymusic` と出る。
（別のアカウントが表示されたら、ブラウザでアカウントを切り替えてやり直す）

## 3. リポジトリを取ってくる

置き場所は本人に確認する。特に希望が無ければ `~/Documents/Nagi Story Music`。

```bash
cd ~/Documents
gh repo clone nagistorymusic/nagistorymusic.github.io "Nagi Story Music"
cd "Nagi Story Music"
```

**確認**：`git status` が `On branch main` で、`index.html` `content/` `assets/` `tools/` がある。

## 4. サイトを手元で表示する

```bash
python3 tools/dev-server.py
```

ブラウザで http://localhost:8765/?intro=1 を開く。

**確認**：ロゴのオープニング → ショーリール → 作品6本 → プロフィール → お問い合わせ、まで表示される。
止めるときは Ctrl+C。

## 5. 作品を更新できるか試す（任意）

```bash
python3 tools/update_works.py
```

**確認**：6作品が並んで「サムネイル: そのまま」と出る。`git status` で `content/works.json` に変更が出ない（出たら改行コードの違いだけか `git diff` で確かめる）。

作品を入れ替えるときは `content/works.json` に次の形で書いて、同じコマンドを実行する（タイトルとサムネイルは自動で入る）。

```json
{ "url": "https://youtu.be/xxxxxxxxxxx", "line": "キーセンテンス（改行は \\n）" }
```

## 6. 素材フォルダ（ショーリールを作り直すときだけ必要）

元の動画素材（`materials/`、約3.5GB）は Git に入っていない。nagistorymusic の Google ドライブに置く予定。

1. 本人が「Google ドライブ パソコン版」を入れ、nagistorymusic のアカウントでログインする
2. ドライブ内の `Nagi Story Music/materials` を右クリック →「オフラインで使用可能」にする（ショーリールを作るときに動画を丸ごと読むため）
3. `tools/local.example.json` を `tools/local.json` にコピーし、`materials` に場所を書く
   - Mac の例：`~/Library/CloudStorage/GoogleDrive-<メールアドレス>/マイドライブ/Nagi Story Music/materials`
   - 実際の場所は Finder でフォルダを右クリック →（option キーを押しながら）「パス名をコピー」で確かめる

**確認**：`python3 tools/showreel/build.py --preview` で、`materials/preview/showreel-preview.mp4`（15秒・1920×1080）ができる。

※ まだ素材をドライブに移していない場合は、このステップは飛ばしてよい（サイトの表示・作品の更新には不要）。

## 7. 変更を GitHub に送る

```bash
git add -A
git commit -m "変更内容を日本語で一言"
git push
```

push は **本人に頼まれたときだけ** 行う。

---

## 残っている作業

- 素材を Google ドライブへ移す（本人の準備ができたら）
