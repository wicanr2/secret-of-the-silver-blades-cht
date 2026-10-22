#!/usr/bin/env bash
# G2 冷啟動收據：原版 START.EXE 由 dosgolem 冷啟動，走玩家第一次執行的設定問答
# （顯示卡 [2] EGA、音效 [1] AdLib、輸入 [2] MOUSE、存檔路徑按 Enter 用預設），
# 寫出 scratch 層的 blades.cfg，過標題後到建立隊伍主選單。
# 冷啟動到 #300,000,000（標題畫面）存狀態，再從狀態重播兩次到 #399,000,000 比對主選單色號雜湊。
# -program-path 給安裝程式的預設目錄 C:\SECRET，預設存檔路徑才會是 C:\SECRET\SAVE\。
# 注意：-save-state／-dump-at 的步數須小於 -steps，等於上限時不會觸發。
# 前置：workplace/input/dos/sosb（G1 展開）、workplace/dosgolem（固定 commit 的隔離 clone）。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ORIG="$ROOT/workplace/input/dos/sosb"
DG="$ROOT/workplace/dosgolem"
OUT="$ROOT/workplace/probe/g2-receipt"
test -f "$ORIG/START.EXE" || { echo "缺 $ORIG/START.EXE（先跑 G1 的 tools/inventory.py）" >&2; exit 1; }
test -x "$DG/tools/go.sh" || { echo "缺 $DG（dosgolem 隔離 clone）" >&2; exit 1; }
rm -rf "$OUT"
mkdir -p "$OUT/scratch"
run() {
  DOSGOLEM_ORIG="$ORIG" DOSGOLEM_EXTRA_MOUNT="$OUT:/out" DOSGOLEM_TIMEOUT=15m DOSGOLEM_CPUS=2 \
    "$DG/tools/go.sh" run ./cmd/probe -root /orig -scratch-dir /out/scratch \
    -program-path 'C:\SECRET\START.EXE' "$@"
}
cd "$DG"
run -exe /orig/START.EXE -steps 300001000 \
  -bios-keys $'212\r' -bios-key-from 9500000 -bios-key-every 5000000 \
  -save-state 300000000:/out/title-300m.state -dump-at "300000000:/out/title.png" > "$OUT/cold.log" 2>&1
for tag in a b; do
  run -load-state /out/title-300m.state -steps 400001000 \
    -dump-at "399000000:/out/menu-$tag.png" > "$OUT/menu-$tag.log" 2>&1
done
sha256sum "$OUT/scratch/blades.cfg" "$OUT/title-300m.state" "$OUT/menu-a.bin" "$OUT/menu-b.bin"
a=$(sha256sum < "$OUT/menu-a.bin"); b=$(sha256sum < "$OUT/menu-b.bin")
[[ "$a" == "$b" ]] && echo "重播一致" || { echo "重播不一致" >&2; exit 1; }
