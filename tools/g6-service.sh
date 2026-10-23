#!/usr/bin/env bash
# G6 城鎮服務盤點（#7，docs/re/011）：sosb-overlay-shot 從狀態檔（預設 g3-receipt/town.state，新維地格里城 3,3 面南）
# 依序送鍵，每個鍵之前截一張 2 倍原版與覆繪畫面，全程記印字盤點（inventory.tsv，含原文，只留工作區）。
# 用法：tools/g6-service.sh <名稱> "<鍵 鍵 …>"；鍵名同 sosb-overlay-shot（Up、Left、Return、Esc、單一字母…）。
# 環境變數：EVERY（鍵距步數，預設 15000000，約 156 畫格）、STATE（狀態檔，要在 workplace/probe/ 底下、同目錄有 scratch/）、
#   SHOTS=0 只記盤點不截圖。輸出 workplace/probe/g6-service/<名稱>/：inventory.tsv、kNN-base／overlay.png、run.log。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DG="$ROOT/workplace/dosgolem"
name=$1 keys=$2
state=$(realpath "${STATE:-$ROOT/workplace/probe/g3-receipt/town.state}")
[[ $state == "$ROOT/workplace/probe/"* ]] || { echo "狀態檔要在 workplace/probe/ 底下" >&2; exit 1; }
test -f "$state" && test -d "$(dirname "$state")/scratch" || { echo "缺 $state 或其 scratch/" >&2; exit 1; }
test -f "$ROOT/workplace/font/sosb-rounded.golemfnt" || { echo "缺字型" >&2; exit 1; }
EVERY=${EVERY:-15000000}
# 狀態檔的步數：sosb-overlay-shot 的步數是絕對值，從 JSON 以外的地方讀不到，呼叫端給（預設 town.state 的 1,720,001,000）
T=${T0:-1720001000}
OUT="$ROOT/workplace/probe/g6-service/$name"
rm -rf "$OUT"; mkdir -p "$OUT"; cp -r "$(dirname "$state")/scratch" "$OUT/scratch"; test -d "$OUT/scratch"
at=$((T + EVERY)) ka="" sh="" i=0
for k in $keys; do
  i=$((i + 1))
  [[ ${SHOTS:-1} == 0 ]] || sh+=",$((at - 1000000)):$(printf 'k%02d' "$i")"
  ka+=",$at:$k"
  at=$((at + EVERY))
done
[[ ${SHOTS:-1} == 0 ]] || sh+=",$((at - 1000000)):$(printf 'k%02d' $((i + 1)))"
rel=${state#"$ROOT/workplace/probe/"}
(cd "$DG" && DOSGOLEM_ORIG="$ROOT/workplace/input/dos/sosb" \
  DOSGOLEM_EXTRA_MOUNTS="$ROOT/workplace/probe:/st:ro;$OUT:/out;$ROOT/workplace/font:/font:ro;$ROOT/text:/text:ro" \
  DOSGOLEM_TIMEOUT="${TIMEOUT:-1800}s" DOSGOLEM_CPUS=2 DOSGOLEM_MEM=2g \
  tools/go.sh run ./cmd/sosb-overlay-shot -state "/st/$rel" -root /orig -scratch /out/scratch \
    -font /font/sosb-rounded.golemfnt -text-dir /text -keys-at "${ka#,}" ${sh:+-shots "${sh#,}"} \
    -inventory /out/inventory.tsv -until "$at" -out /out) > "$OUT/run.log" 2>&1 \
  || { echo "$name 失敗（$OUT/run.log）" >&2; exit 1; }
echo "$name 送 $i 鍵；缺口："
"$ROOT/tools/g6-misses.sh" "$OUT/inventory.tsv" | head -20
