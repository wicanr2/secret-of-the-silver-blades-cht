#!/usr/bin/env bash
# 多語系收據（#11，克萊恩英豪規格 015）：sosb-play 自動模式以指定語言冷開機，走 tools/g7-journal-receipt.sh 的路徑
# （讀預建隊伍 → 查驗題 → 開場 → 鎮長 → 新維地格里城），在關鍵時點截圖，到鎮上後開攻略、手札、地圖各一張。
# 用法：tools/g10-lang-receipt.sh [語言…]（預設 zh-CN en ja ko，有字型的才跑）。字型由 tools/font-dev.sh 產生。
# 查驗題答案沿用 g7 收據實測的 YULASH（同一存檔目錄與按鍵，題目固定）。輸出 workplace/probe/g10-lang/<語言>/。
# 要求：log 沒有「缺字」、沒有啟動錯誤；截圖另行抽看。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DG="$ROOT/workplace/dosgolem"
ORIG="$ROOT/workplace/input/dos/sosb"
FONTS="$ROOT/workplace/font"
IMAGE=dosgolem-go-ebiten:1.24-r1
test -f "$ORIG/START.EXE" && test -f "$FONTS/sosb-rounded.golemfnt" || { echo "缺原版或字型" >&2; exit 1; }
(cd "$DG" && DOSGOLEM_TIMEOUT=10m tools/go.sh build -o /src/workplace/bin/sosb-play ./cmd/sosb-play)
keys() { local f=$1 every=$2; shift 2; for k in "$@"; do printf ',%d:%s' "$f" "$k"; f=$((f + every)); done; }
s="$(keys 3170 520 ' ' p Down Down Enter)$(keys 5870 208 A Down Down Down Down Down Enter)"
s+="$(keys 7540 52 Y U L A S H Enter)$(keys 8730 416 Enter Enter Enter Enter Enter Enter Enter Enter)"
s+="$(keys 12570 416 Enter E N Enter Enter Enter)"
s+=",3600:shot,7600:shot,9200:shot,11036:shot,15000:shot,15050:guide,15100:shot,15150:guide,15160:journal,15200:shot,15250:journal,15260:map,15300:shot"
lf=""
for c in zh-CN ja ko; do test -f "$FONTS/sosb-$c.golemfnt" && lf+=",$c=/font/sosb-$c.golemfnt"; done
test -f "$FONTS/sosb-en.golemfnt" && lf+=",en=/font/sosb-en.golemfnt"
pids=()
for L in "${@:-zh-CN en ja ko}"; do
  for code in $L; do
    [[ $code == en ]] && ! test -f "$FONTS/sosb-en.golemfnt" && continue
    [[ $code != en ]] && ! test -f "$FONTS/sosb-$code.golemfnt" && { echo "$code 沒有字型，略過"; continue; }
    OUT="$ROOT/workplace/probe/g10-lang/$code"
    rm -rf "$OUT"; mkdir -p "$OUT"; test -d "$OUT"
    timeout 90m docker run --rm --init --network none --memory 2g --cpus 2 --pids-limit 256 \
      --log-opt max-size=10m --log-opt max-file=3 -u "$(id -u):$(id -g)" -e HOME=/tmp -e SOSB_NO_DIALOG=1 \
      -v "$DG/workplace/bin":/app:ro -v "$ORIG":/orig:ro -v "$ROOT/text":/text:ro -v "$FONTS":/font:ro -v "$OUT":/out \
      --entrypoint xvfb-run "$IMAGE" -a /app/sosb-play -original /orig -save /out/save -text-dir /text \
      -font /font/sosb-rounded.golemfnt -lang "$code" -lang-fonts "${lf#,}" -audio=false -frames 15400 \
      -script "${s#,}" -shot-dir /out/shots -inventory /out/inventory.tsv > "$OUT/log.txt" 2>&1 &
    pids+=($!)
  done
done
fail=0
for p in "${pids[@]}"; do wait "$p" || fail=1; done
for d in "$ROOT"/workplace/probe/g10-lang/*/; do
  c=$(basename "$d")
  printf '%s：截圖 %s 張，缺字 %s 行，%s\n' "$c" "$(ls "$d/shots" 2>/dev/null | wc -l)" "$(grep -c '缺字' "$d/log.txt" || true)" "$(grep -m1 'memory_sha256' "$d/log.txt" | cut -c1-60)"
  grep -q 'memory_sha256' "$d/log.txt" || fail=1
done
exit $fail
