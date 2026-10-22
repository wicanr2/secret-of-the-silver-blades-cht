#!/usr/bin/env bash
# G6 存讀檔收據：sosb-play 自動模式。
# 第一趟同 tools/g7-journal-receipt.sh 走到新維地格里城，紮營（E）→ 存檔（S）→ B 槽，存完截圖。
# 第二趟沿用同一個存檔目錄冷開機：主選單載入儲存遊戲 → B 槽 → 開始冒險 → 查驗題（從印字盤點讀題目）→ 回到紮營畫面。
# 只在關鍵時點截圖（使用者 2026-10-22：抽樣就好）：存檔提示、存完、讀檔後的隊伍選單、查驗題、回到遊戲。
# docker run 帶 --init：xvfb-run 當 PID 1 時等不到 Xvfb 的就緒訊號會一直卡住。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DG="$ROOT/workplace/dosgolem"
ORIG="$ROOT/workplace/input/dos/sosb"
FONT="$ROOT/workplace/font/sosb-rounded.golemfnt"
OUT="$ROOT/workplace/probe/g6-saveload-receipt"
IMAGE=dosgolem-go-ebiten:1.24-r1
for f in "$ORIG/START.EXE" "$FONT"; do test -f "$f" || { echo "缺 $f" >&2; exit 1; }; done
(cd "$DG" && DOSGOLEM_TIMEOUT=10m tools/go.sh build -o /src/workplace/bin/sosb-play ./cmd/sosb-play)
rm -rf "$OUT"; mkdir -p "$OUT/save" "$OUT/load" "$OUT/quiz1" "$OUT/quiz2"
play() { # 輸出目錄 存檔目錄 畫格數 腳本 其餘參數…
  local dir=$1 save=$2 frames=$3 script=$4; shift 4
  mkdir -p "$dir" "$save"  # 掛載前先建：來源不存在時 dockerd 會以 root 建空目錄頂替
  timeout 20m docker run --rm --init --network none --memory 2g --cpus 2 --pids-limit 256 \
    --log-opt max-size=10m --log-opt max-file=3 -u "$(id -u):$(id -g)" -e HOME=/tmp -e SOSB_NO_DIALOG=1 \
    -v "$DG/workplace/bin":/app:ro -v "$ORIG":/orig:ro -v "$ROOT/text":/text:ro -v "$ROOT/workplace/font":/font:ro \
    -v "$dir":/out -v "$save":/save --entrypoint xvfb-run "$IMAGE" -a /app/sosb-play -original /orig -save /save -text-dir /text \
    -font "/font/$(basename "$FONT")" -audio=false -scale 2 -frames "$frames" -script "$script" "$@" > "$dir/log.txt" 2>&1
}
keys() { # 起始畫格 間隔 動作…
  local f=$1 every=$2; shift 2
  for k in "$@"; do printf ',%d:%s' "$f" "$k"; f=$((f + every)); done
}
answer() { # 盤點檔 → 答案字母（以逗號分隔的腳本動作要逐字送）
  local q w e p a
  q=$(cut -f9 "$1" | tr 'A-Z' 'a-z' | tr '\n' ' ')
  w=$(sed -n 's/.*what is word # *\([0-9]*\).*/\1/p' <<<"$q" | head -1)
  e=$(sed -n 's/.*journal entry # *\([0-9]*\).*/\1/p' <<<"$q" | head -1)
  p=$(sed -n 's/.*journal, page *\([0-9]*\).*/\1/p' <<<"$q" | head -1)
  a=$(awk -F'\t' -v p="$p" -v e="$e" -v w="$w" '$1==p && $2==e && $3==w {print $4}' "$ROOT/text/quiz-answers.tsv")
  [[ -n "$a" ]] || { echo "查驗題 p$p e$e w$w 不在答案表" >&2; exit 1; }
  echo "查驗題：第 $p 頁第 $e 則第 $w 字 → $a" >&2
  echo "$a"
}
spell() { local a=$1 i; for ((i = 0; i < ${#a}; i++)); do printf '%s ' "${a:i:1}"; done; }
shots() { local f; for f in "$@"; do printf ',%d:shot' "$f"; done; }

# 第一趟：讀預建隊伍到鎮上（tools/g7-journal-receipt.sh 的按鍵），紮營存 B 槽
base="$(keys 3170 520 ' ' p Down Down Enter)$(keys 5870 208 A Down Down Down Down Down Enter)"
play "$OUT/quiz1" "$OUT/quiz1/save" 7500 "${base#,}" -inventory /out/inventory.tsv
a=$(answer "$OUT/quiz1/inventory.tsv")
s1="${base#,}$(keys 7540 52 $(spell "$a") Enter)$(keys 8730 416 Enter Enter Enter Enter Enter Enter Enter Enter)"
s1+="$(keys 12570 416 Enter E N Enter Enter Enter)$(keys 15100 400 E S B)$(shots 15000 15832 16976)"
play "$OUT/save" "$OUT/save/data" 17000 "$s1" -shot-dir /out/shots -inventory /out/inventory.tsv
ls "$OUT/save/data" | grep -i 'savgamb' || { echo "沒有存到 B 槽" >&2; exit 1; }

# 第二趟：同一存檔目錄冷開機，讀 B 槽
load="$(keys 3170 520 ' ' p Down Down Enter)$(keys 5870 208 B)"
play "$OUT/quiz2" "$OUT/save/data" 7500 "${load#,}$(keys 6080 208 Down Down Down Down Down Enter)" -inventory /out/inventory.tsv
a=$(answer "$OUT/quiz2/inventory.tsv")
s2="${load#,}$(keys 6080 208 Down Down Down Down Down Enter)$(keys 7540 52 $(spell "$a") Enter)$(shots 6008 7500 9960)"
play "$OUT/load" "$OUT/save/data" 10000 "$s2" -shot-dir /out/shots -inventory /out/inventory.tsv
for d in save load; do if grep -q '缺字' "$OUT/$d/log.txt"; then grep '缺字' "$OUT/$d/log.txt" >&2; exit 1; fi; done
ls "$OUT/save/shots" "$OUT/load/shots" | wc -l
