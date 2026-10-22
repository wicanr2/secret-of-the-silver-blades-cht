#!/usr/bin/env bash
# G3 診斷路徑收據：標題 → 讀預建隊伍 → 開始冒險 → 查驗題 → 開場 → 3D 冒險畫面（docs/re/004）。
# 前置：tools/g2-startup-receipt.sh 產生的 workplace/probe/g2-receipt/title-300m.state 與其 scratch。
# 預建隊伍：比照安裝程式「use our ready-made characters」，把原版的 CHRDATA*、SAVGAMA.DAT 放進 scratch 的 SAVE/
# （blades.cfg 的存檔路徑 C:\SECRET\SAVE\）。
# 查驗題答案依第一次出題：手札第 18 則第 4 個字，字序含標題（STORY OF THE SILVER）→ SILVER。
# 每段從上一段的狀態檔接著跑；FROM=<段名> 從該段開始（loadq、adv、intro、walk、town）。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
G2="$ROOT/workplace/probe/g2-receipt"
OUT="$ROOT/workplace/probe/g3-receipt"
ST="$ROOT/workplace/probe/states"
test -f "$G2/title-300m.state" || { echo "缺 $G2/title-300m.state（先跑 tools/g2-startup-receipt.sh）" >&2; exit 1; }
FROM="${FROM:-title}"
if [[ "$FROM" == title ]]; then
  rm -rf "$OUT"; mkdir -p "$OUT/scratch/SAVE"
  cp "$G2/scratch/blades.cfg" "$OUT/scratch/"
  cp "$ROOT/workplace/input/dos/sosb/"CHRDATA* "$ROOT/workplace/input/dos/sosb/SAVGAMA.DAT" "$OUT/scratch/SAVE/"
  cp "$G2/title-300m.state" "$ST/g3-title.state"
fi
stage() { # 名稱 上一段狀態 終點步數 存狀態步數 其餘參數…
  local name=$1 from=$2 end=$3 save=$4; shift 4
  "$ROOT/tools/probe.sh" "$OUT" -scratch-dir /out/scratch -load-state "/st/$from.state" -steps "$end" \
    -save-state "$save:/out/$name.state" "$@" > "$OUT/$name.log" 2>&1
  cp "$OUT/$name.state" "$ST/g3-$name.state"
}
run=0
for s in loadq adv intro walk town; do
  [[ "$s" == "$FROM" || "$FROM" == title ]] && run=1
  [[ $run == 1 ]] || continue
  case $s in
    loadq) stage loadq g3-title 560001000 560000000 -bios-keys ' p' -bios-key-names Down,Down,Enter \
             -bios-key-from 305000000 -bios-key-every 50000000 -dump-at "559000000:/out/loadq.png" ;;
    adv)   stage adv g3-loadq 720001000 720000000 -bios-keys 'A' -bios-key-names Down,Down,Down,Down,Down,Enter \
             -bios-key-from 565000000 -bios-key-every 20000000 -dump-at "599000000:/out/party.png;719000000:/out/quiz.png" ;;
    intro) stage intro g3-adv 830001000 830000000 -bios-keys $'SILVER\r' -bios-key-from 725000000 \
             -bios-key-every 5000000 -dump-at "829000000:/out/intro.png" ;;
    walk)  stage walk g3-intro 1200001000 1200000000 -bios-keys $'\r\r\r\r\r\r\r\r' -bios-key-from 840000000 \
             -bios-key-every 40000000 -dump-at "1199000000:/out/walk.png" ;;
    town)  stage town g3-walk 1720001000 1720000000 -bios-keys $'\rEN\r\r\r' -bios-key-from 1210000000 \
             -bios-key-every 40000000 -dump-at "1719000000:/out/adventure.png" ;;
  esac
done
cd "$OUT" && sha256sum loadq.bin party.bin quiz.bin intro.bin walk.bin adventure.bin 2>/dev/null
