#!/usr/bin/env bash
# #16 閃爍量測：sosb-play 自動模式走 tools/g7-journal-receipt.sh 的路徑（查驗題答案沿用該收據實測的 YULASH），
# 在 FROM..TO 畫格逐格截圖（覆繪後畫面），檢查有沒有先露出英文再換中文的畫格。
# 用法：FROM=10805 TO=10840 tools/g16-flicker-probe.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DG="$ROOT/workplace/dosgolem"
ORIG="$ROOT/workplace/input/dos/sosb"
FONT="$ROOT/workplace/font/sosb-rounded.golemfnt"
OUT="$ROOT/workplace/probe/g16-flicker/${NAME:-mayor}"
IMAGE=dosgolem-go-ebiten:1.24-r1
FROM=${FROM:-10805}; TO=${TO:-10840}
rm -rf "$OUT"; mkdir -p "$OUT"
keys() { local f=$1 every=$2; shift 2; for k in "$@"; do printf ',%d:%s' "$f" "$k"; f=$((f + every)); done; }
s="$(keys 3170 520 ' ' p Down Down Enter)$(keys 5870 208 A Down Down Down Down Down Enter)"
s+="$(keys 7540 52 Y U L A S H Enter)$(keys 8730 416 Enter Enter Enter Enter Enter Enter Enter Enter)"
s+="$(keys 12570 416 Enter E N Enter Enter Enter)"
for ((f = FROM; f <= TO; f++)); do s+=",$f:shot"; done
timeout 20m docker run --rm --init --network none --memory 2g --cpus 2 --pids-limit 256 \
  --log-opt max-size=10m --log-opt max-file=3 -u "$(id -u):$(id -g)" -e HOME=/tmp -e SOSB_NO_DIALOG=1 \
  -v "$DG/workplace/bin":/app:ro -v "$ORIG":/orig:ro -v "$ROOT/text":/text:ro -v "$ROOT/workplace/font":/font:ro \
  -v "$OUT":/out --entrypoint xvfb-run "$IMAGE" -a /app/sosb-play -original /orig -save /out/save -text-dir /text \
  -font "/font/$(basename "$FONT")" -audio=false -scale 2 -frames "$((TO + 1))" -script "${s#,}" -shot-dir /out/shots \
  -inventory /out/inventory.tsv > "$OUT/log.txt" 2>&1
ls "$OUT/shots" | wc -l
