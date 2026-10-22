#!/usr/bin/env bash
# 切換列速度與字級收據（#14、#15；主專案規格 019、020）：sosb-play 冷開機到標題畫面，腳本動作 bar 讓切換列顯示，
# 截 2 倍、3 倍各字級的切換列，以及速度、字級下拉選單展開的畫面。只看切換列與選單，不比對遊戲畫面。
# 倍率在最後 10 格才切：自動模式固定照設定倍率跑，32x 跑全程要 32 倍時間。
# docker run 帶 --init：xvfb-run 當 PID 1 時等不到 Xvfb 的就緒訊號會一直卡住。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DG="$ROOT/workplace/dosgolem"
ORIG="$ROOT/workplace/input/dos/sosb"
FONT="$ROOT/workplace/font/sosb-rounded.golemfnt"
OUT="$ROOT/workplace/probe/g14-toolbar-receipt"
IMAGE=dosgolem-go-ebiten:1.24-r1
for f in "$ORIG/START.EXE" "$FONT" "${FONT%.golemfnt}-bar12.golemfnt" "${FONT%.golemfnt}-bar22.golemfnt"; do
  test -f "$f" || { echo "缺 $f（先跑 tools/font-dev.sh）" >&2; exit 1; }
done
(cd "$DG" && DOSGOLEM_TIMEOUT=10m tools/go.sh build -o /src/workplace/bin/sosb-play ./cmd/sosb-play)
rm -rf "$OUT"; mkdir -p "$OUT"
run() { # 名稱 倍率 腳本 其餘參數…
  local name=$1 scale=$2 script=$3; shift 3
  mkdir -p "$OUT/$name"
  timeout 10m docker run --rm --init --network none --memory 2g --cpus 2 --pids-limit 256 \
    --log-opt max-size=10m --log-opt max-file=3 -u "$(id -u):$(id -g)" -e HOME=/tmp -e SOSB_NO_DIALOG=1 \
    -v "$DG/workplace/bin":/app:ro -v "$ORIG":/orig:ro -v "$ROOT/text":/text:ro -v "$ROOT/workplace/font":/font:ro \
    -v "$OUT/$name":/out --entrypoint xvfb-run "$IMAGE" -a /app/sosb-play -original /orig -save /out/save -text-dir /text \
    -font "/font/$(basename "$FONT")" -audio=false -scale "$scale" -frames 1200 -script "$script" "$@" \
    -shot /out/shot.rgba > "$OUT/$name/log.txt" 2>&1
  timeout 120 docker run --rm --network none --memory 1g --cpus 1 --pids-limit 32 --log-opt max-size=10m --log-opt max-file=3 \
    -u "$(id -u):$(id -g)" -v "$OUT":/d sosb-img:r1 python3 -I -c "
from PIL import Image
w, h = 320 * $scale, 200 * $scale
Image.frombytes('RGBA', (w, h), open('/d/$name/shot.rgba', 'rb').read()).crop((0, 0, w, 12 * 8 * $scale)).save('/d/$name.png')"
}
run s2-small 2 "1:bar,1:barfont=1" &
run s2-medium-speeds 2 "1:bar,1190:speed=8,1191:speeds" &
wait
run s3-small 3 "1:bar,1:barfont=1,1190:speed=32" &
run s3-medium 3 "1:bar,1:barfont=2,1190:speed=32,1191:speeds" &
wait
run s3-large-sizes 3 "1:bar,1:barfont=3,2:barfonts" &
run s2-large 2 "1:bar,1:barfont=3,1190:speed=16" &
wait
if grep -l '缺字' "$OUT"/*/log.txt; then grep -h '缺字' "$OUT"/*/log.txt | sort -u >&2; exit 1; fi
grep -h 'CPU 速度' "$OUT"/*/log.txt
ls "$OUT"/*.png
