"""作品一覧（content/works.json）を整えて、サムネイルを用意するスクリプト

使い方（Windows / Mac 共通）:
    python3 tools/update_works.py            # 足りないサムネイルだけ取ってくる
    python3 tools/update_works.py --force    # サムネイルを全部取り直す

works.json には、最低限これだけ書けば OK（上から順にサイトに並ぶ）:
    { "url": "https://youtu.be/xxxxxxxxxxx", "line": "キーセンテンス" }

    - タイトルを書かなければ YouTube から自動で入れる
    - "kind" を書くと小さな表記が変わる（省略時は Official MV）
    - キーセンテンスの改行は \n

必要なもの: Python 3.9 以上、Pillow（pip3 install Pillow）
"""
import argparse
import io
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
WORKS = ROOT / "content" / "works.json"
THUMBS = ROOT / "assets" / "works"
SIZES = (640, 1280)
UA = {"User-Agent": "Mozilla/5.0 (nagistorymusic site updater)"}

ID_RE = re.compile(r"(?:v=|youtu\.be/|shorts/|embed/)([A-Za-z0-9_-]{11})")


def video_id(entry):
    for key in ("youtube", "url"):
        v = entry.get(key, "")
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", v):
            return v
        m = ID_RE.search(v)
        if m:
            return m.group(1)
    raise ValueError(f"YouTube の URL が見つかりません: {entry}")


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        return r.read()


def fetch_title(vid):
    q = urllib.parse.quote(f"https://www.youtube.com/watch?v={vid}", safe="")
    data = json.loads(get(f"https://www.youtube.com/oembed?url={q}&format=json"))
    # 「道化師と僕 // Official MV」→「道化師と僕」
    return re.split(r"\s*//\s*|\s*\|\s*", data["title"])[0].strip()


def make_thumbs(vid, force):
    outs = [THUMBS / f"{vid}-{w}.webp" for w in SIZES]
    if not force and all(o.exists() for o in outs):
        return "そのまま"
    for name in ("maxresdefault", "sddefault", "hqdefault"):
        try:
            raw = get(f"https://i.ytimg.com/vi/{vid}/{name}.jpg")
            break
        except Exception:
            continue
    else:
        raise RuntimeError(f"サムネイルを取得できませんでした: {vid}")
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    # 黒帯付きの 4:3 サムネイル（hqdefault など）は 16:9 に切り抜く
    target_h = round(im.width * 9 / 16)
    if im.height > target_h:
        top = (im.height - target_h) // 2
        im = im.crop((0, top, im.width, top + target_h))
    THUMBS.mkdir(parents=True, exist_ok=True)
    for w, out in zip(SIZES, outs):
        im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(out, quality=80, method=6)
    return f"作成（元画像 {name}）"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="サムネイルを全部取り直す")
    args = ap.parse_args()

    works = json.loads(WORKS.read_text(encoding="utf-8"))
    cleaned = []
    for i, e in enumerate(works, 1):
        vid = video_id(e)
        title = e.get("title") or fetch_title(vid)
        item = {"title": title, "youtube": vid}
        if e.get("kind"):
            item["kind"] = e["kind"]
        item["line"] = e.get("line", "")
        status = make_thumbs(vid, args.force)
        print(f"{i:02d} {title}  [{vid}]  サムネイル: {status}" + ("" if item["line"] else "  ※キーセンテンスが空です"))
        cleaned.append(item)

    WORKS.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    used = {f"{w['youtube']}-{s}.webp" for w in cleaned for s in SIZES}
    unused = sorted(p.name for p in THUMBS.glob("*.webp") if p.name not in used)
    if unused:
        print("\n使われていないサムネイル（消してもよい）:", *unused, sep="\n  ")
    print(f"\n{len(cleaned)} 作品を {WORKS.relative_to(ROOT)} に書き出しました。")
    print("確認: python3 tools/dev-server.py → http://localhost:8765/")


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        sys.exit(f"エラー: {err}")
