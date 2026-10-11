# Nagi Story Music

物語・音楽・映像を組み合わせて作品を制作するクリエイター Nagi Story Music のポートフォリオサイト。

公開先（予定）: https://nagistorymusic.github.io

## 手元で見る

```bash
python3 tools/dev-server.py
```

→ http://localhost:8765/ （オープニングから見るときは `?intro=1`）

## 更新する

- 作品：`content/works.json` を編集 → `python3 tools/update_works.py`
- ショーリール：`tools/showreel/clips.csv` を編集 → `python3 tools/showreel/build.py --preview` → `python3 tools/showreel/build.py`
- プロフィール・リンク：`content/profile.json` ／ `content/site.json`

必要なもの：Python 3.9 以上、Pillow、ffmpeg（ショーリールを作るときだけ）。
作業の進め方と決定事項は [CLAUDE.md](CLAUDE.md) を参照。
