#!/usr/bin/env bash
# sosb-play 無頭冒煙（docs/re/007 冷開機路徑）：空存檔目錄冷開機，第 3200 畫格送空白、3700 畫格送 p 進主選單，
# 第 4400 畫格截圖並寫印字盤點。檢查 blades.cfg 與原版首次設定相同（docs/re/003）。
# docker run 帶 --init：xvfb-run 當 PID 1 時等不到 Xvfb 的就緒訊號會一直卡住。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DG="$ROOT/workplace/dosgolem"
ORIG="$ROOT/workplace/input/dos/sosb"
FONT="$ROOT/workplace/font/sosb-rounded.golemfnt"
OUT="$ROOT/workplace/play-smoke"
IMAGE=dosgolem-go-ebiten:1.24-r1
CFG_SHA=00cbd89ee14e59022941a6a5fe3c5107cf8d26b27dc60c096174a091d55923b3
for f in "$ORIG/START.EXE" "$FONT"; do test -f "$f" || { echo "缺 $f" >&2; exit 1; }; done
(cd "$DG" && DOSGOLEM_TIMEOUT=10m tools/go.sh build -o /src/workplace/bin/sosb-play ./cmd/sosb-play)
rm -rf "$OUT"; mkdir -p "$OUT"
timeout 10m docker run --rm --init --network none --memory 2g --cpus 2 --pids-limit 256 \
  --log-opt max-size=10m --log-opt max-file=3 -u "$(id -u):$(id -g)" -e HOME=/tmp -e SOSB_NO_DIALOG=1 \
  -v "$DG/workplace/bin":/app:ro -v "$ORIG":/orig:ro -v "$ROOT/text":/text:ro -v "$ROOT/workplace/font":/font:ro \
  -v "$OUT":/data --entrypoint xvfb-run "$IMAGE" -a /app/sosb-play -original /orig -save /data/save -text-dir /text \
  -font "/font/$(basename "$FONT")" -audio=false -scale 2 -frames 4400 -script '3200: ,3700:p' \
  -shot /data/menu.rgba -inventory /data/inventory.tsv > "$OUT/run.log" 2>&1
echo "$CFG_SHA  $OUT/save/blades.cfg" | sha256sum -c -
grep -q 'A map\[.*覆繪:' "$OUT/run.log" || { echo "主選單沒有覆繪" >&2; exit 1; }
if grep -q '缺字' "$OUT/run.log"; then echo "有缺字" >&2; exit 1; fi
timeout 120 docker run --rm --network none --memory 1g --cpus 1 --pids-limit 64 --log-opt max-size=10m --log-opt max-file=3 \
  -u "$(id -u):$(id -g)" -v "$OUT":/d sosb-img:r1 python3 -c "
from PIL import Image
Image.frombytes('RGBA',(640,400),open('/d/menu.rgba','rb').read()).save('/d/menu.png')"
tail -1 "$OUT/run.log"
