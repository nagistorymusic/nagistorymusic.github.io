# ショーリールを作り直すスクリプト
#   使い方:  powershell -ExecutionPolicy Bypass -File tools\showreel\build.ps1
#   確認用だけ: ... build.ps1 -Preview   （1080p MP4 を materials\preview に1本だけ）
#
# 使う場面は tools\showreel\clips.csv に書く（上から順につながる）
#   file   : materials\hero-clips 内のファイル名
#   start  : 使い始める秒
#   length : 使う長さ（秒）。前後のクロスフェード分も含む
#   adjust : 色の微調整（ffmpeg の eq フィルタなど。空欄なら無調整）
# 合計の長さ = length の合計 - クロスフェード秒 x 本数

param(
  [switch]$Preview,
  [double]$Fade = 0.3
)

$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..\..')
$clipDir = Join-Path $root 'materials\hero-clips'
$outDir = if ($Preview) { Join-Path $root 'materials\preview' } else { Join-Path $root 'assets\showreel' }
New-Item -ItemType Directory -Force $outDir | Out-Null

$clips = @(Import-Csv -Encoding UTF8 (Join-Path $PSScriptRoot 'clips.csv'))
if ($clips.Count -lt 2) { throw 'clips.csv に2本以上書いてください' }

$norm = 'scale=2560:1440:force_original_aspect_ratio=increase,crop=2560:1440,fps=30,setsar=1,format=yuv420p'

# 各場面を先に1本ずつ切り出す（4K素材を一度に開くとメモリが足りなくなるため）
$tmp = Join-Path $env:TEMP 'nagi-showreel-parts'
New-Item -ItemType Directory -Force $tmp | Out-Null
$parts = @()
$lens = @()
for ($i = 0; $i -le $clips.Count; $i++) {
  # 最後の1本は、ループのつなぎ目用に先頭の場面をもう一度（フェード分だけ）
  $c = if ($i -lt $clips.Count) { $clips[$i] } else { $clips[0] }
  $path = Join-Path $clipDir $c.file
  if (-not (Test-Path -LiteralPath $path)) { throw "見つかりません: $($c.file)" }
  $len = if ($i -lt $clips.Count) { [double]$c.length } else { $Fade + 0.1 }
  if ($i -lt $clips.Count) { $lens += $len }
  $adj = if ($c.adjust) { ",$($c.adjust)" } else { '' }
  $part = Join-Path $tmp "part$i.mp4"
  & ffmpeg -v error -y -ss $c.start -t $len -i $path -an -vf "$norm$adj" -c:v libx264 -preset veryfast -crf 8 $part
  if ($LASTEXITCODE -ne 0) { throw "切り出しに失敗しました: $($c.file)" }
  $parts += $part
}
$inputs = @()
$filter = ''
for ($i = 0; $i -lt $parts.Count; $i++) {
  $inputs += @('-i', $parts[$i])
  $filter += "[${i}:v]setpts=PTS-STARTPTS[v$i];"
}
$w = $clips.Count
# クロスフェードでつなぎ、最後は先頭の場面へフェードして戻す
$prev = 'v0'
$acc = $lens[0]
for ($k = 1; $k -le $w; $k++) {
  $off = [math]::Round($acc - $Fade, 3)
  $filter += "[$prev][v$k]xfade=transition=fade:duration=${Fade}:offset=$off[x$k];"
  $prev = "x$k"
  if ($k -lt $w) { $acc = $acc - $Fade + $lens[$k] }
}
# 頭のフェード分を切り落とす → 最後のコマが最初のコマにそのままつながる
$total = [math]::Round((($lens | Measure-Object -Sum).Sum) - $Fade * $w, 3)
$filter += "[$prev]trim=start=${Fade}:duration=$total,setpts=PTS-STARTPTS[out]"

Write-Host "場面 $($clips.Count) 本 / 合計 $total 秒"

if ($Preview) {
  & ffmpeg -v error -y @inputs -filter_complex $filter -map '[out]' -an `
    -c:v libx264 -preset medium -crf 20 -movflags +faststart (Join-Path $outDir 'showreel-preview.mp4')
  Write-Host "書き出し: $(Join-Path $outDir 'showreel-preview.mp4')"
  return
}

# 高画質の中間ファイルを1本作り、そこから各サイズを書き出す
$master = Join-Path $env:TEMP 'nagi-showreel-master.mp4'
& ffmpeg -v error -y @inputs -filter_complex $filter -map '[out]' -an `
  -c:v libx264 -preset veryfast -crf 10 $master
if ($LASTEXITCODE -ne 0) { throw '中間ファイルの書き出しに失敗しました' }

$sizes = @(
  @{ name = '1440'; scale = '2560:1440'; crf264 = 24; crf9 = 34 },
  @{ name = '1080'; scale = '1920:1080'; crf264 = 24; crf9 = 34 },
  @{ name = '720';  scale = '1280:720';  crf264 = 26; crf9 = 37 }
)
foreach ($s in $sizes) {
  $vf = "scale=$($s.scale):flags=lanczos,format=yuv420p"
  & ffmpeg -v error -y -i $master -vf $vf -an -c:v libx264 -preset slow -profile:v high `
    -crf $s.crf264 -movflags +faststart (Join-Path $outDir "showreel-$($s.name).mp4")
  & ffmpeg -v error -y -i $master -vf $vf -an -c:v libvpx-vp9 -b:v 0 -crf $s.crf9 `
    -row-mt 1 -deadline good -cpu-used 2 (Join-Path $outDir "showreel-$($s.name).webm")
}

# 待機画像（動画の最初のコマ）
& ffmpeg -v error -y -i $master -frames:v 1 -vf 'scale=1920:1080:flags=lanczos' -q:v 3 (Join-Path $outDir 'showreel-poster-1080.jpg')
& ffmpeg -v error -y -i $master -frames:v 1 -vf 'scale=1280:720'  -q:v 4 (Join-Path $outDir 'showreel-poster-720.jpg')
Remove-Item $master
Remove-Item -Recurse $tmp

Get-ChildItem $outDir | ForEach-Object { '{0,-28} {1,6:N1} MB' -f $_.Name, ($_.Length / 1MB) }
