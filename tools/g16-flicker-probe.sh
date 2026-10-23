#!/usr/bin/env bash
# #16 閃爍量測：sosb-play 自動模式走 tools/g7-journal-receipt.sh 的路徑（查驗題答案沿用該收據實測的 YULASH），
# 在 FROM..TO 畫格逐格截圖（覆繪後畫面），檢查有沒有先露出英文再換中文的畫格。
# ROUTE=demo 改走開場 demo（標題按空白、選單選 d，之後不送鍵；demo 含訊息、3D 行走與戰鬥）。
# EXTRA 接在路徑後的腳本動作（例：鎮上走到商店）；STEP 截圖間隔（預設 1＝逐格，探路時放大）。
# 一律帶 -flash-audit（規格 021）：log.txt 結尾印閃現次數與前 20 筆。FRAMES 指定總畫格數（預設 TO+1）；只量不截圖時 STEP 設 0。
# SCALE 改倍率（預設 2）；HD=1 掛 repo 的 hd/theme（只在 3 倍顯示，規格 010）。
# 例：ROUTE=demo NAME=hd-demo SCALE=3 HD=1 FROM=1 TO=0 STEP=0 FRAMES=9000 TIMEOUT=60m tools/g16-flicker-probe.sh
# 用法：FROM=10805 TO=10840 tools/g16-flicker-probe.sh；ROUTE=demo NAME=demo FROM=3690 TO=9000 tools/g16-flicker-probe.sh
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
if [[ ${ROUTE:-mayor} == demo ]]; then
  s=",3170: ,3690:d"
else
  s="$(keys 3170 520 ' ' p Down Down Enter)$(keys 5870 208 A Down Down Down Down Down Enter)"
  s+="$(keys 7540 52 Y U L A S H Enter)$(keys 8730 416 Enter Enter Enter Enter Enter Enter Enter Enter)"
  s+="$(keys 12570 416 Enter E N Enter Enter Enter)"
fi
s+="${EXTRA:+,$EXTRA}"
if (( ${STEP:-1} > 0 )); then for ((f = FROM; f <= TO; f += ${STEP:-1})); do s+=",$f:shot"; done; fi
timeout "${TIMEOUT:-20m}" docker run --rm --init --network none --memory 2g --cpus 2 --pids-limit 256 \
  --log-opt max-size=10m --log-opt max-file=3 -u "$(id -u):$(id -g)" -e HOME=/tmp -e SOSB_NO_DIALOG=1 \
  -v "$DG/workplace/bin":/app:ro -v "$ORIG":/orig:ro -v "$ROOT/text":/text:ro -v "$ROOT/workplace/font":/font:ro \
  -v "$OUT":/out ${HD:+-v "$ROOT/hd/theme":/hd:ro} --entrypoint xvfb-run "$IMAGE" -a /app/sosb-play -original /orig -save /out/save -text-dir /text \
  -font "/font/$(basename "$FONT")" -audio=false -scale "${SCALE:-2}" ${HD:+-hd /hd} -frames "${FRAMES:-$((TO + 1))}" -script "${s#,}" -shot-dir /out/shots \
  -inventory /out/inventory.tsv -flash-audit > "$OUT/log.txt" 2>&1
grep '閃現' "$OUT/log.txt" | head -3
