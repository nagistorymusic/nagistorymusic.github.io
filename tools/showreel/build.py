"""ショーリールを作り直すスクリプト（Windows / Mac 共通）

使い方:
    python3 tools/showreel/build.py            # 本番用を assets/showreel に書き出す
    python3 tools/showreel/build.py --preview  # 確認用 1080p MP4 を1本だけ（<素材>/preview に）

使う場面は tools/showreel/clips.csv に書く（上から順につながる）
    file   : 素材フォルダの hero-clips 内のファイル名
    start  : 使い始める秒
    length : 使う長さ（秒）。前後のクロスフェード分も含む
    adjust : 色の微調整（ffmpeg の eq フィルタなど。空欄なら無調整）
合計の長さ = length の合計 - クロスフェード秒 x 本数（最後は先頭へフェードして戻り、つなぎ目なくループする）

素材フォルダの場所（上から順に探す）:
    1. 環境変数 NSM_MATERIALS
    2. tools/local.json の "materials"（パソコンごとの設定。Git には入れない）
    3. リポジトリ直下の materials/

必要なもの: Python 3.9 以上、ffmpeg（PATH が通っていること）
"""
import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
NORM = "scale=2560:1440:force_original_aspect_ratio=increase,crop=2560:1440,fps=30,setsar=1,format=yuv420p"
SIZES = [  # 名前, 大きさ, H.264 の画質, VP9 の画質（数字が小さいほど高画質・重い）
    ("1440", "2560:1440", 24, 34),
    ("1080", "1920:1080", 24, 34),
    ("720", "1280:720", 26, 37),
]


def materials_dir():
    if os.environ.get("NSM_MATERIALS"):
        return Path(os.environ["NSM_MATERIALS"]).expanduser()
    local = ROOT / "tools" / "local.json"
    if local.exists():
        m = json.loads(local.read_text(encoding="utf-8")).get("materials")
        if m:
            p = Path(m).expanduser()
            return p if p.is_absolute() else ROOT / p
    return ROOT / "materials"


def ffmpeg(*args):
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", *map(str, args)])
    if r.returncode != 0:
        raise RuntimeError("ffmpeg が失敗しました: " + " ".join(map(str, args[:6])) + " …")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preview", action="store_true", help="確認用 1080p MP4 を1本だけ書き出す")
    ap.add_argument("--fade", type=float, default=0.3, help="クロスフェードの秒数（既定 0.3）")
    args = ap.parse_args()
    fade = args.fade

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg が見つかりません（Mac: brew install ffmpeg / Windows: winget install Gyan.FFmpeg）")
    mat = materials_dir()
    clip_dir = mat / "hero-clips"
    if not clip_dir.is_dir():
        sys.exit(f"素材フォルダが見つかりません: {clip_dir}\n（tools/local.json の materials を確認してください）")

    with open(HERE / "clips.csv", encoding="utf-8-sig", newline="") as f:
        clips = list(csv.DictReader(f))
    if len(clips) < 2:
        sys.exit("clips.csv に2本以上書いてください")

    tmp = Path(tempfile.mkdtemp(prefix="nsm-showreel-"))
    try:
        # 各場面を先に1本ずつ切り出す（4K素材を一度に開くとメモリが足りなくなるため）
        # 最後の1本は、ループのつなぎ目用に先頭の場面をもう一度（フェード分だけ）
        parts, lens = [], []
        for i, c in enumerate(clips + [clips[0]]):
            src = clip_dir / c["file"]
            if not src.exists():
                sys.exit(f"見つかりません: {src}")
            last = i == len(clips)
            length = fade + 0.1 if last else float(c["length"])
            if not last:
                lens.append(length)
            adj = f",{c['adjust']}" if c.get("adjust") else ""
            part = tmp / f"part{i}.mp4"
            print(f"切り出し {i + 1}/{len(clips) + 1}: {c['file']}  {c['start']}s から {length:g}s")
            ffmpeg("-ss", c["start"], "-t", length, "-i", src, "-an", "-vf", NORM + adj,
                   "-c:v", "libx264", "-preset", "veryfast", "-crf", 8, part)
            parts.append(part)

        # クロスフェードでつなぎ、最後は先頭の場面へフェードして戻す
        n = len(clips)
        inputs, filt = [], ""
        for i, p in enumerate(parts):
            inputs += ["-i", p]
            filt += f"[{i}:v]setpts=PTS-STARTPTS[v{i}];"
        prev, acc = "v0", lens[0]
        for k in range(1, n + 1):
            filt += f"[{prev}][v{k}]xfade=transition=fade:duration={fade}:offset={acc - fade:.3f}[x{k}];"
            prev = f"x{k}"
            if k < n:
                acc = acc - fade + lens[k]
        # 頭のフェード分を切り落とす → 最後のコマが最初のコマにそのままつながる
        total = round(sum(lens) - fade * n, 3)
        filt += f"[{prev}]trim=start={fade}:duration={total},setpts=PTS-STARTPTS[out]"
        print(f"場面 {n} 本 / 合計 {total:g} 秒")

        if args.preview:
            out_dir = mat / "preview"
            out_dir.mkdir(parents=True, exist_ok=True)
            out = out_dir / "showreel-preview.mp4"
            filt_1080 = filt.removesuffix("[out]") + ",scale=1920:1080:flags=lanczos[out]"
            ffmpeg(*inputs, "-filter_complex", filt_1080, "-map", "[out]", "-an",
                   "-c:v", "libx264", "-preset", "medium", "-crf", 20, "-movflags", "+faststart", out)
            print(f"書き出し: {out}")
            return

        # 高画質の中間ファイルを1本作り、そこから各サイズを書き出す
        master = tmp / "master.mp4"
        ffmpeg(*inputs, "-filter_complex", filt, "-map", "[out]", "-an",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", 10, master)
        out_dir = ROOT / "assets" / "showreel"
        out_dir.mkdir(parents=True, exist_ok=True)
        for name, scale, crf264, crf9 in SIZES:
            vf = f"scale={scale}:flags=lanczos,format=yuv420p"
            print(f"書き出し {name}p（MP4 / WebM）")
            ffmpeg("-i", master, "-vf", vf, "-an", "-c:v", "libx264", "-preset", "slow", "-profile:v", "high",
                   "-crf", crf264, "-movflags", "+faststart", out_dir / f"showreel-{name}.mp4")
            ffmpeg("-i", master, "-vf", vf, "-an", "-c:v", "libvpx-vp9", "-b:v", 0, "-crf", crf9,
                   "-row-mt", 1, "-deadline", "good", "-cpu-used", 2, out_dir / f"showreel-{name}.webm")
        # 待機画像（動画の最初のコマ）
        ffmpeg("-i", master, "-frames:v", 1, "-vf", "scale=1920:1080:flags=lanczos", "-q:v", 3, out_dir / "showreel-poster-1080.jpg")
        ffmpeg("-i", master, "-frames:v", 1, "-vf", "scale=1280:720", "-q:v", 4, out_dir / "showreel-poster-720.jpg")
        for p in sorted(out_dir.iterdir()):
            print(f"  {p.name:<28} {p.stat().st_size / 1e6:6.1f} MB")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
