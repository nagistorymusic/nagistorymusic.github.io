# Nagi Story Music ホームページ

音楽・MV制作者「Nagi Story Music」のポートフォリオサイト（1ページのLP）。
**内容（構成・文章・配色など）は本人と後で詰める。勝手に決めず、案を出して確認をとること。**

## 今の状況と決定事項（2026-10-11 時点・引き継ぎ用）

ステップ1〜7は完了。**残りはステップ8（公開）**。作業は Windows で進めたが、今後は Mac で管理する予定。

- **リポジトリ**：`nagistorymusic/nagistorymusic.github.io`（非公開・main）。LP 専用。
  GitHub は **nagistorymusic** アカウントで作業する。push の前に `gh auth status` で nagistorymusic が使われているか確認する。
- **公開先**：GitHub Pages で `https://nagistorymusic.github.io`（無料）。独自ドメインは見送り（必要になったら追加）。
  公開時にリポジトリを public にする。デザインの試作3案は `design-concepts` ブランチに保管し、main には入れない。
- **デザイン**：案A「上映プログラム（映画館）」。墨色 `#121111`・生成り `#ebe4d3`・朱 `#d9533b`。
  フォントは Google Fonts（Cormorant Garamond / Shippori Mincho / Zen Kaku Gothic New）。
- **演出（7つ）**：04 テキストリビール、06 ブラーイン、10 パララックス（透かしの NSM マーク）、15 背景色トランジション（7%）、23 隠れるヘッダー、
  ロゴのオープニング（NSM マーク → グリッチ → ワードマーク → 左上へ。1訪問1回、`?intro=1` で再生）、ベイート（マスコット B.A.I.R.T）がカーソルにあとからついてくる。
  試して外したもの：05 マスクリビール、11 スクロールズーム（変化を感じにくい／重い）。
- **作品**：6本・ほぼ新しい順。画像クリックでサイト内再生、「Watch on YouTube ↗」で YouTube へ。表記は基本「Official MV」、Halloween Night は「AI Film」。
  キーセンテンスは1文字ずつ演出するため日本語の禁則が効かない → **改行位置は `\n` で手で決める**。
- **英語**：見出し・ナビは英語、内容は日本語、プロフィールだけ日英併記。英語版の切り替えは付けない（海外の依頼が増えたら検討）。
- **お問い合わせ**：Web3Forms（Access Key は `content/site.json`、公開してよい値）。テスト送信成功済み。
- **一番上へ戻る**：ロゴ／ページ末尾の「Back to top」／スマホではベイートをタップ。

### ファイルの場所

| 場所 | 中身 |
|---|---|
| `index.html` | 本番ページ（案A） |
| `content/works.json` `profile.json` `site.json` | 表示内容（作品・プロフィール・リンク）。**ページはここを読んで表示する** |
| `assets/` | 動画・画像・ロゴ・アイコン・`js/site.js` |
| `tools/update_works.py` | 作品一覧を整え、サムネイルを取得・変換 |
| `tools/showreel/build.py` ＋ `clips.csv` | ショーリールの作り直し |
| `tools/dev-server.py` | 確認用サーバー（動画のシーク対応）→ `http://localhost:8765/` |
| `tools/local.json` | パソコンごとの設定（素材フォルダの場所）。Git に入れない。`local.example.json` を参考に作る |

### 更新のしかた

- **作品を入れ替える**：`content/works.json` に `{ "url": "YouTube の URL", "line": "キーセンテンス" }` を書く → `python3 tools/update_works.py`（タイトルとサムネイルを自動取得）→ 確認 → push
- **ショーリールを作り直す**：`tools/showreel/clips.csv` を編集 → `python3 tools/showreel/build.py --preview` で確認 → OK なら `python3 tools/showreel/build.py`
- **素材（materials）**：nagistorymusic の Google ドライブに置く予定（未移行）。場所は `tools/local.json` に書く。ショーリールを作るときは「オフラインで使用可能」にしておく

### Mac での準備

詳しい手順と確認方法は **`docs/mac-setup.md`**。概要：

1. `brew install ffmpeg python gh` ／ `pip3 install Pillow`
2. `gh auth login`（**nagistorymusic** でログイン）→ `gh repo clone nagistorymusic/nagistorymusic.github.io`
3. 素材を使うなら Google ドライブ パソコン版を入れ、`tools/local.json` に materials の場所を書く
4. `python3 tools/dev-server.py` → `http://localhost:8765/`

## 進め方（この順番を守る）

各ステップは「確認用を作る → 本人がOK → 次へ」。OKが出るまで次のステップに進まない。

| # | ステップ | 必要な素材 | 本人に確認すること |
|---|---|---|---|
| 1 | ショーリール | `materials/hero-clips/` | 使う場面、つなぎ方（カット/クロスフェード）、曲に合わせるか |
| 2 | 素材の整理 | `works/` `profile/` `header-candidates/` `mascot/` `logo/` | 掲載作品と並び順 |
| 3 | 内容を決める | — | セクション構成、各セクションに載せるもの |
| 4 | デザイン | ヘッダー候補 | 配色、フォント、雰囲気 |
| 5 | 演出を決める | — | 下のチートシートの番号で選んでもらう |
| 6 | LPを組む | 1〜5の結果 | 表示確認（PC・スマホ） |
| 7 | 文章・英訳・リンク | URL・プロフィールのメモ | 文章の最終確認 |
| 8 | 公開 | — | 公開先・ドメイン |

## 素材

`materials/` は元素材置き場。`.gitignore` で除外済みで、Git には入れない。
Web用に書き出した完成ファイルだけをリポジトリに入れる。

```text
materials/
├─ hero-clips/          ショーリール用動画 5〜7本（16:9、使う区間は各3〜8秒）
├─ works/work-01〜04/   サムネイル、プレビュー動画（任意）、作品メモ
├─ profile/             アイコン
├─ header-candidates/   ヘッダー候補 3〜5枚（配色決めの参考）
├─ mascot/              黒ウサギ（透過PNG、最大4表情）
├─ logo/                ある場合のみ
└─ cpp/                 CapCut / Pollo AI CPP 関連
```

足りない素材があれば、あるものだけで進めてよい。CPPのロゴや認定表示は、公開してよいか本人に確認してから使う。非公開情報や個人情報は載せない。

## ステップ1：ショーリールの仕様

1. メモ（例 `01_xxx.mp4：00:12〜00:15`）の区間を切り出す。メモが無ければ候補の場面を提案する
2. **約15秒**のループ動画につなぐ
3. 16:9・1920×1080 にそろえる（比率が違う素材はクロップ）。色味を軽くそろえる
4. 音声なし（自動再生用）
5. PC用 1080p とスマホ用 720p。MP4(H.264) と WebM(VP9)。軽さを優先
6. 待機画像（poster）を書き出す
7. まず確認用を1本作って見せる。本番の書き出しはOKが出てから

## スクロール演出チートシート24

本人とは**番号**でやりとりする（例：「03と11」）。
実装手段を添えると精度が上がる：CSSだけ / GSAP ScrollTrigger / Framer Motion。

### 1. 出てくる動き（画面に入ったら1回だけ再生）

| # | 名前 | 英語名 | 動き |
|---|---|---|---|
| 01 | フェードイン | Scroll-triggered fade-in | 画面に入ったらふわっと表示 |
| 02 | スライドイン | Slide-in | 横からすべり込む |
| 03 | スタッガー | Stagger animation | 時間差で順番に表示 |
| 04 | テキストリビール | Text reveal (Split text) | 文字が1字ずつ浮き上がる |
| 05 | マスクリビール | Clip-path reveal | 幕が開くように画像が出る |
| 06 | ブラーイン | Blur-in reveal | ぼかしからくっきり表示 |
| 07 | タイプライター | Typewriter effect | 1文字ずつ打ち込まれる |
| 08 | カウントアップ | Count-up animation | 数字が0から増えていく |

### 2. スクロールに連動する動き（スクロール量に比例して進む）

| # | 名前 | 英語名 | 動き |
|---|---|---|---|
| 09 | スクロール連動 | Scroll-linked animation | スクロール量に合わせて進む（読了バーなど） |
| 10 | パララックス | Parallax scrolling | 背景と手前が違う速さで動く |
| 11 | スクロールズーム | Scale on scroll | 画像が拡大して全画面に |
| 12 | 画像シーケンス | Scroll-scrubbed image sequence | 連番画像をコマ送り再生 |
| 13 | SVGラインドロー | SVG line drawing | 線が描かれていく |
| 14 | テキストフィル | Text fill on scroll | 読み進めるほど文字が塗られる |
| 15 | 背景色トランジション | Background color transition | 背景色がなめらかに変わる |
| 16 | マーキー | Marquee (scroll velocity) | 流れ続け、スクロールで加速 |

### 3. 固定・送り・ナビ（止める・送る・現在地を示す）

| # | 名前 | 英語名 | 動き |
|---|---|---|---|
| 17 | スティッキー | position: sticky | 見出しが上に貼り付く |
| 18 | ピン留め＋スクラブ | Pin + scrub (GSAP ScrollTrigger) | 画面を固定して中身だけ進む |
| 19 | スクロールテリング | Scrollytelling | 文章に合わせて固定図が切り替わる |
| 20 | カードスタック | Stacking cards | カードが重なっていく |
| 21 | スクロールスナップ | CSS scroll snap | 1画面ずつピタッと止まる |
| 22 | 横スクロール | Horizontal scroll | 縦スクロールで横に流れる |
| 23 | 隠れるヘッダー | Hide-on-scroll header | 下で隠れ、戻すと出る |
| 24 | スクロールスパイ | Scrollspy | 目次が現在地をハイライト |

### このサイトでの候補（未確定。ステップ5で本人と決める）

- ヒーロー：11 または 18 ／ タイトル：06＋04 ／ 作品一覧：20 または 03＋05、15
- 区切り帯：16 ／ 黒ウサギ：10 ／ プロフィール文：14 ／ ナビ：23
- 合わないもの：08（見せる数字が無い）、12（重い）、19・24（長文ページ向け）、07（04とかぶる）、21（スマホで操作しにくい）

### 演出のルール

- 使う演出は6〜8個まで（動画が多いサイトなので重くしない）
- `prefers-reduced-motion`（OSの「視差効果を減らす」設定）のときは演出を止めるか弱める
- スマホで重くないか必ず確認する
