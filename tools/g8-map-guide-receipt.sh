#!/usr/bin/env bash
# 地圖疊層攻略點收據（#9，克萊恩英豪規格 009；docs/re/009）：sosb-overlay-shot 從狀態檔開地圖疊層（全圖模式），
# 截 2 倍覆繪畫面，看攻略點編號是否落在《軟體世界》地圖圖例標的格子。
# 用法：tools/g8-map-guide-receipt.sh <名稱> <狀態檔> <狀態檔步數>（狀態檔在 workplace/probe/ 底下、同目錄有 scratch/）。
# 預設：town＝g3-receipt/town.state（新維地格里城 3,3 面南，#1,720,001,000）。輸出 workplace/probe/g8-map-guide/<名稱>/。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DG="$ROOT/workplace/dosgolem"
name=${1:-town} state=$(realpath "${2:-$ROOT/workplace/probe/g3-receipt/town.state}") T=${3:-1720001000}
[[ $state == "$ROOT/workplace/probe/"* ]] || { echo "狀態檔要在 workplace/probe/ 底下" >&2; exit 1; }
test -f "$state" && test -d "$(dirname "$state")/scratch" || { echo "缺 $state 或其 scratch/" >&2; exit 1; }
OUT="$ROOT/workplace/probe/g8-map-guide/$name"
rm -rf "$OUT"; mkdir -p "$OUT"; cp -r "$(dirname "$state")/scratch" "$OUT/scratch"; test -d "$OUT/scratch"
rel=${state#"$ROOT/workplace/probe/"}
(cd "$DG" && DOSGOLEM_ORIG="$ROOT/workplace/input/dos/sosb" \
  DOSGOLEM_EXTRA_MOUNTS="$ROOT/workplace/probe:/st:ro;$OUT:/out;$ROOT/workplace/font:/font:ro;$ROOT/text:/text:ro" \
  DOSGOLEM_TIMEOUT=10m DOSGOLEM_CPUS=2 DOSGOLEM_MEM=2g \
  tools/go.sh run ./cmd/sosb-overlay-shot -state "/st/$rel" -root /orig -scratch /out/scratch \
    -font /font/sosb-rounded.golemfnt -text-dir /text -map-preview 全圖 \
    -shots "$((T + 20000000)):map" -until "$((T + 21000000))" -out /out) > "$OUT/run.log" 2>&1 \
  || { echo "$name 失敗（$OUT/run.log）" >&2; exit 1; }
echo "$name $(sha256sum "$OUT/map-overlay.png" | cut -c1-16)"
