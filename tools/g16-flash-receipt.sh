#!/usr/bin/env bash
# 不露原版收據（規格 021 §6 第 2 項，抽樣路線；使用者 2026-10-23：抽樣驗證即可）：
#   demo：開場 demo 到 9000 格（訊息、3D 行走、戰鬥訊息區的原版還原顯存）。
#   bank：手札路徑冷開機到新維地格里城，走到 (7,8) 看金庫招牌，按 M 轉南進金庫，到 19500 格。
# 兩條都以 -flash-audit 量測，閃現都要是 0。截圖只取幾個關鍵時點（金庫招牌、金庫內）。
# 依賴 tools/g16-flicker-probe.sh；鎮上路線約 30 分鐘。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DG="$ROOT/workplace/dosgolem"
PROBE="$ROOT/workplace/probe"
(cd "$DG" && DOSGOLEM_TIMEOUT=10m tools/go.sh build -o /src/workplace/bin/sosb-play ./cmd/sosb-play)
keys() { local f=$1 every=$2; shift 2; for k in "$@"; do printf ',%d:%s' "$f" "$k"; f=$((f + every)); done; }
walk="$(keys 15100 104 M Left Up Right Up Up Up Up Up Left Up Up Up Up)$(keys 17100 208 Enter M Right Up)"
# 序跑：共用主機負載高時並行會互搶 CPU；開頭與結尾記負載
echo "開始：負載 $(cut -d' ' -f1-3 /proc/loadavg)"
ROUTE=demo NAME=receipt-demo FROM=4500 TO=4500 FRAMES=9000 TIMEOUT=40m "$ROOT/tools/g16-flicker-probe.sh" > "$PROBE/g16-receipt-demo.out" 2>&1
NAME=receipt-bank EXTRA="${walk#,}" FROM=17000 TO=19500 STEP=1250 FRAMES=19501 TIMEOUT=70m \
  "$ROOT/tools/g16-flicker-probe.sh" > "$PROBE/g16-receipt-bank.out" 2>&1
echo "結束：負載 $(cut -d' ' -f1-3 /proc/loadavg)"
fail=0
for n in demo bank; do
  line=$(grep -m1 '閃現 [0-9]* 次' "$PROBE/g16-flicker/receipt-$n/log.txt" || echo '沒有量尺紀錄')
  echo "$n：$line"
  [[ $line == *"閃現 0 次"* ]] || fail=1
done
exit $fail
