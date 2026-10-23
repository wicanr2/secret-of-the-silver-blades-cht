#!/usr/bin/env bash
# G6 跨畫面盤點（#7，docs/re/011）：從冒險畫面的狀態檔交給 sosb-explore 自動探索（深度優先走遍每格，
# 戰鬥以瞄準近戰推進，選單照 -pick 或預設的離開選項），記下每次印字與是否覆繪（inv.tsv）。
# 用法：tools/g6-explore.sh <名稱> <狀態檔> [sosb-explore 其他參數…]
#   狀態檔要在 workplace/probe/ 底下；同目錄的 scratch/ 是該狀態的可寫層（複製一份再用，不改原檔）。
# 環境變數：ACTIONS（送鍵上限，預設 800）、UNTIL（路徑 B 訊息符合就停，預設不停）、TIMEOUT（秒，預設 3600）。
# 輸出 workplace/probe/g6-explore/<名稱>/：inv.tsv、explore.log、end.state、run.log。缺口用 tools/g6-misses.sh 彙整。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DG="$ROOT/workplace/dosgolem"
name=$1 state=$(realpath "$2"); shift 2
[[ $state == "$ROOT/workplace/probe/"* ]] || { echo "狀態檔要在 workplace/probe/ 底下" >&2; exit 1; }
test -f "$state" || { echo "缺 $state" >&2; exit 1; }
scr="$(dirname "$state")/scratch"
test -d "$scr" || { echo "缺 $scr" >&2; exit 1; }
for f in "$ROOT/workplace/font/sosb-rounded.golemfnt" "$ROOT/workplace/input/dos/sosb/START.EXE"; do test -f "$f" || { echo "缺 $f" >&2; exit 1; }; done
OUT="$ROOT/workplace/probe/g6-explore/$name"
rm -rf "$OUT"; mkdir -p "$OUT"; cp -r "$scr" "$OUT/scratch"
test -d "$OUT/scratch" || exit 1
rel=${state#"$ROOT/workplace/probe/"}
(cd "$DG" && DOSGOLEM_ORIG="$ROOT/workplace/input/dos/sosb" \
  DOSGOLEM_EXTRA_MOUNTS="$ROOT/workplace/probe:/st:ro;$OUT:/out;$ROOT/workplace/font:/font:ro;$ROOT/text:/text:ro" \
  DOSGOLEM_TIMEOUT="${TIMEOUT:-3600}s" DOSGOLEM_CPUS=2 DOSGOLEM_MEM=2g \
  tools/go.sh run ./cmd/sosb-explore -state "/st/$rel" -root /orig -scratch /out/scratch -font /font/sosb-rounded.golemfnt \
    -text-dir /text -until "${UNTIL:-NEVERMATCH}" -max-actions "${ACTIONS:-800}" -out /out "$@") > "$OUT/run.log" 2>&1 \
  || echo "$name 結束碼非 0（看 $OUT/run.log）" >&2
echo "$name $(tail -1 "$OUT/run.log")"
