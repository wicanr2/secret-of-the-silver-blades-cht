#!/usr/bin/env bash
# G6 正常玩家路徑收據：標題 → 主選單 → 建角（精靈戰士 ROLAND）→ 存檔 → 加入隊伍 → 開始冒險 → 查驗題（依答案表作答）→ 開場劇情。
# 前置：tools/g2-startup-receipt.sh（標題狀態與首次執行寫出的 blades.cfg）。scratch 每次重建，只放 blades.cfg；
# 存檔路徑 C:\SECRET\SAVE\ 落在 scratch/SAVE/（docs/re/003、007）。
# 建角：種族、性別、職業、陣營各 Enter（第一項：ELF、MALE、FIGHTER、LAWFUL GOOD），REROLL STATS? 按 N，
# 名字 ROLAND，圖示編輯器 E、IS THIS ICON OK? Y、SAVE ROLAND? Y。
# 分段存狀態；FROM=<段名> 從該段續跑（create、add、begin、answer）。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
G2="$ROOT/workplace/probe/g2-receipt"
OUT="$ROOT/workplace/probe/g6-create-receipt"
ST="$ROOT/workplace/probe/states"
test -f "$G2/title-300m.state" || { echo "缺 $G2/title-300m.state（先跑 tools/g2-startup-receipt.sh）" >&2; exit 1; }
FROM="${FROM:-menu}"
CR=$'\r'
if [[ "$FROM" == menu ]]; then
  rm -rf "$OUT"; mkdir -p "$OUT/scratch"; cp "$G2/scratch/blades.cfg" "$OUT/scratch/"
  cp "$G2/title-300m.state" "$ST/g6r-title.state"
fi
stage() { # 名稱 上一段 終點步數 存狀態步數 其餘參數…
  local name=$1 from=$2 end=$3 save=$4; shift 4
  "$ROOT/tools/probe.sh" "$OUT" -scratch-dir /out/scratch -load-state "/st/g6r-$from.state" -steps "$end" \
    -save-state "$save:/out/$name.state" "$@" > "$OUT/$name.log" 2>&1
  cp "$OUT/$name.state" "$ST/g6r-$name.state"
}
go=0
for s in menu create add begin answer; do
  [[ "$s" == "$FROM" ]] && go=1
  [[ $go == 1 ]] || continue
  case $s in
    menu)   stage menu title 400001000 400000000 -bios-keys ' p' -bios-key-from 305000000 -bios-key-every 50000000 ;;
    create) stage create1 menu 760001000 760000000 -bios-keys "$CR$CR$CR$CR$CR" -bios-key-from 401000000 -bios-key-every 60000000
            stage create2 create1 900001000 900000000 -bios-keys 'N' -bios-key-from 761000000 -dump-at "899000000:/out/name-prompt.png"
            stage create3 create2 1100001000 1100000000 -bios-keys "ROLAND$CR" -bios-key-from 901000000 -bios-key-every 5000000
            stage create create3 1700001000 1700000000 -bios-keys 'EYY' -bios-key-from 1101000000 -bios-key-every 100000000 \
              -dump-at "1699000000:/out/created.png" ;;
    add)    stage add1 create 1900001000 1900000000 -bios-key-names "Down,Return,Return" -bios-key-from 1701000000 -bios-key-every 60000000
            stage add add1 2100001000 2100000000 -bios-keys 'AE' -bios-key-from 1901000000 -bios-key-every 80000000 \
              -dump-at "2099000000:/out/party.png" ;;
    begin)  stage begin add 2400001000 2400000000 -bios-key-names "Down,Down,Down,Down,Down,Down,Return" \
              -bios-key-from 2101000000 -bios-key-every 10000000 -call-args "0650:035D:6:2100000000:2400000000" -call-length-string \
              -dump-at "2399000000:/out/quiz.png" ;;
    answer) q=$(grep -o 'string="[^"]*"' "$OUT/begin.log" | tr -d '"' | sed 's/string=//' | tr '\n' ' ')
            w=$(sed -n 's/.*what is word # *\([0-9]*\).*/\1/p' <<<"$q" | head -1)
            e=$(sed -n 's/.*journal entry # *\([0-9]*\).*/\1/p' <<<"$q" | head -1)
            p=$(sed -n 's/.*journal, page *\([0-9]*\).*/\1/p' <<<"$q" | head -1)
            a=$(awk -F'\t' -v p="$p" -v e="$e" -v w="$w" '$1==p && $2==e && $3==w {print $4}' "$ROOT/text/quiz-answers.tsv")
            [[ -n "$a" ]] || { echo "查驗題 p$p e$e w$w 不在答案表" >&2; exit 1; }
            echo "查驗題：第 $p 頁第 $e 則第 $w 字 → $a"
            stage answer begin 2700001000 2700000000 -bios-keys "$a$CR" -bios-key-from 2401000000 -bios-key-every 5000000 \
              -dump-at "2699000000:/out/opening.png" ;;
  esac
done
ls "$OUT/scratch/SAVE"
cd "$OUT" && sha256sum created.bin party.bin quiz.bin opening.bin 2>/dev/null
