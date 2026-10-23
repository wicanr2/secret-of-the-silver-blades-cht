#!/usr/bin/env bash
# 手札地圖頁收據（規格 022 §5 第 2 項）：sosb-overlay-shot 從鎮上狀態（g3-receipt/town.state，新維地格里城 3,3 面南）
# 以翻閱模式開指定手札與頁，截 2 倍覆繪畫面。地圖圖檔先以 tools/journal_maps.py 產到 workplace/journal/maps/zh-TW/。
# 用法：tools/g7-journal-maps-receipt.sh [則:頁 …]（預設 1:1 1:2 32:1 72:1）。輸出 workplace/probe/g7-journal-maps/<則>-<頁>/。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DG="$ROOT/workplace/dosgolem"
ST="$ROOT/workplace/probe/g3-receipt"
MAPS="$ROOT/workplace/journal/maps/zh-TW"
for f in "$ST/town.state" "$ROOT/workplace/font/sosb-rounded.golemfnt" "$MAPS/01-1.png"; do test -f "$f" || { echo "缺 $f" >&2; exit 1; }; done
test -d "$ST/scratch" || { echo "缺 $ST/scratch" >&2; exit 1; }
T=1720001000
for spec in "${@:-1:1 1:2 32:1 72:1}"; do
  for one in $spec; do
    n=${one%:*} k=${one#*:} out="$ROOT/workplace/probe/g7-journal-maps/$n-$k"
    rm -rf "$out"; mkdir -p "$out"; cp -r "$ST/scratch" "$out/scratch"; test -d "$out/scratch"
    (cd "$DG" && DOSGOLEM_ORIG="$ROOT/workplace/input/dos/sosb" \
      DOSGOLEM_EXTRA_MOUNTS="$ST:/st:ro;$out:/out;$ROOT/workplace/font:/font:ro;$ROOT/text:/text:ro;$MAPS:/maps:ro" \
      DOSGOLEM_TIMEOUT=10m DOSGOLEM_CPUS=2 DOSGOLEM_MEM=2g \
      tools/go.sh run ./cmd/sosb-overlay-shot -state /st/town.state -root /orig -scratch /out/scratch \
        -font /font/sosb-rounded.golemfnt -text-dir /text -journal-maps /maps -journal-preview "$n" -journal-page "$k" \
        -shots "$((T + 20000000)):journal" -until "$((T + 21000000))" -out /out) > "$out/run.log" 2>&1 \
      || { echo "$n:$k 失敗（$out/run.log）" >&2; exit 1; }
    echo "$n:$k $(grep -o '"DiffOutside": *[0-9]*' "$out"/*.json 2>/dev/null | head -1 || true) $(sha256sum "$out/journal-overlay.png" | cut -c1-16)"
  done
done
