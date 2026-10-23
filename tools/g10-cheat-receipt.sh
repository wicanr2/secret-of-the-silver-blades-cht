#!/usr/bin/env bash
# 我方無敵收據（#17，規格 017；欄位見 docs/re/012）：sosb-play 冷開機走開場 demo（標題按空白、選單選 d，之後不送鍵），
# demo 第 4,500–5,300 格是隊伍對兩隻遠古巨龍的戰鬥。無敵關、開各跑一次到 FRAMES 格（預設 6000）。
# 要求：開啟時有還原、結束時隊員狀態都是 0；關閉時不印無敵報告；兩次都沒有缺字。
# 原版 demo 裡亞維羅斯會倒下（記憶體傾印 docs/re/012），所以開啟時的還原次數必須大於 0。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DG="$ROOT/workplace/dosgolem"
ORIG="$ROOT/workplace/input/dos/sosb"
FONT="$ROOT/workplace/font/sosb-rounded.golemfnt"
OUT="$ROOT/workplace/probe/g10-cheat"
IMAGE=dosgolem-go-ebiten:1.24-r1
FRAMES=${FRAMES:-6000}
for f in "$ORIG/START.EXE" "$FONT"; do test -f "$f" || { echo "缺 $f" >&2; exit 1; }; done
(cd "$DG" && DOSGOLEM_TIMEOUT=10m tools/go.sh build -o /src/workplace/bin/sosb-play ./cmd/sosb-play)
rm -rf "$OUT"; mkdir -p "$OUT/off" "$OUT/on"
run() { # 名稱 旗標…
  local name=$1; shift
  timeout 60m docker run --rm --init --network none --memory 2g --cpus 2 --pids-limit 256 \
    --log-opt max-size=10m --log-opt max-file=3 -u "$(id -u):$(id -g)" -e HOME=/tmp -e SOSB_NO_DIALOG=1 \
    -v "$DG/workplace/bin":/app:ro -v "$ORIG":/orig:ro -v "$ROOT/text":/text:ro -v "$ROOT/workplace/font":/font:ro \
    -v "$OUT/$name":/out --entrypoint xvfb-run "$IMAGE" -a /app/sosb-play -original /orig -save /out/save -text-dir /text \
    -font "/font/$(basename "$FONT")" -audio=false -frames "$FRAMES" -script "3170: ,3690:d,4700:shot,5200:shot" \
    -shot-dir /out/shots "$@" > "$OUT/$name/log.txt" 2>&1
}
run off & run on -cheat; wait
grep -h "無敵\|memory_sha256" "$OUT"/*/log.txt
if grep -l "缺字" "$OUT"/*/log.txt; then echo "有缺字" >&2; exit 1; fi
grep -q "無敵" "$OUT/off/log.txt" && { echo "關閉時不該有無敵報告" >&2; exit 1; }
line=$(grep "無敵" "$OUT/on/log.txt") || { echo "開啟時沒有無敵報告" >&2; exit 1; }
n=$(sed -E 's/.*還原 ([0-9]+) 次.*/\1/' <<< "$line"); [[ "$n" -gt 0 ]] || { echo "開啟時沒有任何還原" >&2; exit 1; }
grep -qE "/[1-9][0-9]*；" <<< "$line" && { echo "有隊員狀態異常" >&2; exit 1; }
echo "通過：還原 $n 次"
