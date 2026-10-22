#!/usr/bin/env bash
# CPU 速度等價性（主專案規格 019 §4 第 2 項；dosgolem 規格 429 §4 第 3 項）：sosb-play 1x、同一腳本
# （tools/g7-journal-receipt.sh 的路徑，查驗題答案沿用實測的 YULASH），TP Delay 快轉開與關跑到同一畫格，
# 比對結束時的記憶體、色號畫面雜湊與截圖。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DG="$ROOT/workplace/dosgolem"
ORIG="$ROOT/workplace/input/dos/sosb"
FONT="$ROOT/workplace/font/sosb-rounded.golemfnt"
OUT="$ROOT/workplace/probe/g14-delay-equiv"
IMAGE=dosgolem-go-ebiten:1.24-r1
END=${END:-15000}
(cd "$DG" && DOSGOLEM_TIMEOUT=10m tools/go.sh build -o /src/workplace/bin/sosb-play ./cmd/sosb-play)
rm -rf "$OUT"; mkdir -p "$OUT/on" "$OUT/off"
keys() { local f=$1 every=$2; shift 2; for k in "$@"; do printf ',%d:%s' "$f" "$k"; f=$((f + every)); done; }
s="$(keys 3170 520 ' ' p Down Down Enter)$(keys 5870 208 A Down Down Down Down Down Enter)"
s+="$(keys 7540 52 Y U L A S H Enter)$(keys 8730 416 Enter Enter Enter Enter Enter Enter Enter Enter)"
s+="$(keys 12570 416 Enter E N Enter Enter Enter)"
run() { # 名稱 -delay-accel 值
  timeout 40m docker run --rm --init --network none --memory 2g --cpus 2 --pids-limit 256 \
    --log-opt max-size=10m --log-opt max-file=3 -u "$(id -u):$(id -g)" -e HOME=/tmp -e SOSB_NO_DIALOG=1 \
    -v "$DG/workplace/bin":/app:ro -v "$ORIG":/orig:ro -v "$ROOT/text":/text:ro -v "$ROOT/workplace/font":/font:ro \
    -v "$OUT/$1":/out --entrypoint xvfb-run "$IMAGE" -a /app/sosb-play -original /orig -save /out/save -text-dir /text \
    -font "/font/$(basename "$FONT")" -audio=false -scale 2 -frames "$END" -script "${s#,}" -delay-accel="$2" \
    -shot /out/shot.rgba > "$OUT/$1/log.txt" 2>&1
}
start=$(date +%s); run on true; mid=$(date +%s); run off false; end=$(date +%s)
for n in on off; do echo "$n：$(grep -o 'memory_sha256=[0-9a-f]* indexed_sha256=[0-9a-f]*' "$OUT/$n/log.txt")；截圖 $(sha256sum < "$OUT/$n/shot.rgba" | cut -c1-16)；$(grep -o '快轉 [0-9]* 步' "$OUT/$n/log.txt")"; done
echo "牆鐘：快轉開 $((mid - start)) 秒、關 $((end - mid)) 秒"
a=$(grep -o 'memory_sha256=[0-9a-f]* indexed_sha256=[0-9a-f]*' "$OUT/on/log.txt"); b=$(grep -o 'memory_sha256=[0-9a-f]* indexed_sha256=[0-9a-f]*' "$OUT/off/log.txt")
if [[ "$a" == "$b" ]] && cmp -s "$OUT/on/shot.rgba" "$OUT/off/shot.rgba"; then echo "等價：通過"; else echo "等價：不通過"; exit 1; fi
