#!/usr/bin/env bash
# #14 速度量測（主專案規格 019 §4 第 4 項，比照幽靈騎士規格 016 §4.1）：自動模式加 -speed-adaptive 讓實際倍率照互動模式調節，
# 3 倍畫面、同一段開場 demo（標題按空白、選單選 d），1x、8x、32x 各跑一次，-perf 印每格模擬與繪製耗時、畫出 fps、平均實際倍率。
# 一次只跑一組，避免互相搶 CPU；開頭與結尾記主機負載。本作還沒有 HD 主題（G9），3 倍只放大原版畫面。
# 用法：tools/g14-perf.sh；FRAMES 改畫格數（預設 6700，demo 從 3690 格開始，約 3000 格 demo）。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DG="$ROOT/workplace/dosgolem"
ORIG="$ROOT/workplace/input/dos/sosb"
FONT="$ROOT/workplace/font/sosb-rounded.golemfnt"
OUT="$ROOT/workplace/probe/g14-perf"
IMAGE=dosgolem-go-ebiten:1.24-r1
FRAMES=${FRAMES:-6700}
for f in "$ORIG/START.EXE" "$FONT"; do test -f "$f" || { echo "缺 $f" >&2; exit 1; }; done
mkdir -p "$OUT"
for m in 1 8 32; do
  rm -rf "$OUT/$m"; mkdir -p "$OUT/$m"
  echo "${m}x 開始：$(cut -d' ' -f1-3 /proc/loadavg)"
  timeout 40m docker run --rm --init --network none --memory 2g --cpus 2 --pids-limit 256 \
    --log-opt max-size=10m --log-opt max-file=3 -u "$(id -u):$(id -g)" -e HOME=/tmp -e SOSB_NO_DIALOG=1 \
    -v "$DG/workplace/bin":/app:ro -v "$ORIG":/orig:ro -v "$ROOT/text":/text:ro -v "$ROOT/workplace/font":/font:ro \
    -v "$OUT/$m":/out --entrypoint xvfb-run "$IMAGE" -a /app/sosb-play -original /orig -save /out/save -text-dir /text \
    -font "/font/$(basename "$FONT")" -audio=false -scale 3 -frames "$FRAMES" -script "3170: ,3690:d" \
    -speed "$m" -speed-adaptive -perf > "$OUT/$m/log.txt" 2>&1
  echo "${m}x：$(grep -E 'perf|fps' "$OUT/$m/log.txt" | tr '\n' ' ')"
  echo "${m}x 結束：$(cut -d' ' -f1-3 /proc/loadavg)"
done
