#!/usr/bin/env bash
# G7 手札自動彈出收據（克萊恩英豪規格 007）：sosb-play 自動模式走診斷路徑（tools/g3-party-receipt.sh 的按鍵，步數換成畫格，
# 一畫格 96,250 步）：讀預建隊伍 → 開始冒險 → 查驗題 → 開場 → 鎮長對白 → 新維地格里城。
# 第一趟跑到查驗題，從印字盤點讀題目、查 text/quiz-answers.tsv；第二趟作答並沿路每 208 畫格截圖（腳本動作 shot）。
# 到鎮上之後依序開攻略（F6）、手札翻閱（F5）、地圖（F7）、再開攻略，各截一張，看面板互斥（克萊恩英豪規格 007 §2.1、008、009 §2.3）。
# docker run 帶 --init：xvfb-run 當 PID 1 時等不到 Xvfb 的就緒訊號會一直卡住。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DG="$ROOT/workplace/dosgolem"
ORIG="$ROOT/workplace/input/dos/sosb"
FONT="$ROOT/workplace/font/sosb-rounded.golemfnt"
OUT="$ROOT/workplace/probe/g7-journal-receipt"
IMAGE=dosgolem-go-ebiten:1.24-r1
END=${END:-15000}
PANEL_END=$((END + 500))
for f in "$ORIG/START.EXE" "$FONT"; do test -f "$f" || { echo "缺 $f" >&2; exit 1; }; done
(cd "$DG" && DOSGOLEM_TIMEOUT=10m tools/go.sh build -o /src/workplace/bin/sosb-play ./cmd/sosb-play)
rm -rf "$OUT"; mkdir -p "$OUT/quiz" "$OUT/run"
play() { # 輸出目錄 畫格數 腳本 其餘參數…
  local dir=$1 frames=$2 script=$3; shift 3
  timeout 20m docker run --rm --init --network none --memory 2g --cpus 2 --pids-limit 256 \
    --log-opt max-size=10m --log-opt max-file=3 -u "$(id -u):$(id -g)" -e HOME=/tmp -e SOSB_NO_DIALOG=1 \
    -v "$DG/workplace/bin":/app:ro -v "$ORIG":/orig:ro -v "$ROOT/text":/text:ro -v "$ROOT/workplace/font":/font:ro \
    -v "$dir":/out --entrypoint xvfb-run "$IMAGE" -a /app/sosb-play -original /orig -save /out/save -text-dir /text \
    -font "/font/$(basename "$FONT")" -audio=false -scale 2 -frames "$frames" -script "$script" "$@" > "$dir/log.txt" 2>&1
}
keys() { # 起始畫格 間隔 動作…
  local f=$1 every=$2; shift 2
  for k in "$@"; do printf ',%d:%s' "$f" "$k"; f=$((f + every)); done
}
base="$(keys 3170 520 ' ' p Down Down Enter)$(keys 5870 208 A Down Down Down Down Down Enter)"
play "$OUT/quiz" 7500 "${base#,}" -inventory /out/inventory.tsv
q=$(cut -f9 "$OUT/quiz/inventory.tsv" | tr 'A-Z' 'a-z' | tr '\n' ' ')
w=$(sed -n 's/.*what is word # *\([0-9]*\).*/\1/p' <<<"$q" | head -1)
e=$(sed -n 's/.*journal entry # *\([0-9]*\).*/\1/p' <<<"$q" | head -1)
p=$(sed -n 's/.*journal, page *\([0-9]*\).*/\1/p' <<<"$q" | head -1)
a=$(awk -F'\t' -v p="$p" -v e="$e" -v w="$w" '$1==p && $2==e && $3==w {print $4}' "$ROOT/text/quiz-answers.tsv")
[[ -n "$a" ]] || { echo "查驗題 p$p e$e w$w 不在答案表" >&2; exit 1; }
echo "查驗題：第 $p 頁第 $e 則第 $w 字 → $a"
answer=(); for ((i = 0; i < ${#a}; i++)); do answer+=("${a:i:1}"); done
script="${base#,}$(keys 7540 52 "${answer[@]}" Enter)$(keys 8730 416 Enter Enter Enter Enter Enter Enter Enter Enter)"
script+="$(keys 12570 416 Enter E N Enter Enter Enter)"
for ((f = 7500; f < END; f += 208)); do script+=",$f:shot"; done
script+=",$((END + 50)):guide,$((END + 100)):shot,$((END + 150)):journal,$((END + 200)):shot"
script+=",$((END + 250)):map,$((END + 300)):shot,$((END + 350)):guide,$((END + 400)):shot"
play "$OUT/run" "$PANEL_END" "$script" -shot-dir /out/shots -inventory /out/inventory.tsv
if grep -q '缺字' "$OUT/run/log.txt"; then grep '缺字' "$OUT/run/log.txt" >&2; exit 1; fi
grep -i 'journal\|手札' "$OUT/run/log.txt" | head -20 || true
ls "$OUT/run/shots" | wc -l
cd "$OUT/run/shots" && sha256sum "sosb-f$(printf %06d $((END + 100))).png" "sosb-f$(printf %06d $((END + 200))).png" \
  "sosb-f$(printf %06d $((END + 300))).png" "sosb-f$(printf %06d $((END + 400))).png" "sosb-f$(printf %06d 11036).png"
