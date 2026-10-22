#!/usr/bin/env bash
# 開場 demo 控制收據（#13；規格 018，比照幽靈騎士規格 015 §4）：sosb-play 自動模式冷開機，以腳本送鍵。
#   menu     ：標題畫面按空白進 PLAY／DEMO 選單後不再送鍵，停留 3700 格（超過原版 30 秒逾時），仍在選單。
#   message／walk／combat：選 DEMO 後在訊息、3D 行走、戰鬥各按一次空白，demo 結束後每隔 520 格按 p 三次，
#              主選單畫面與不經 demo 直接按 p 的 play 相同。
# 畫格以 sosb-play 預設時脈實測（tools/play-smoke.sh 同時脈）：3170 格按空白、3690 格選 d；
# demo 中 3800 格訊息、3960 格 3D 行走、4500 格戰鬥（workplace/probe/demo-inv 的印字盤點）。
# 用法：tools/g13-demo-receipt.sh；RUN=名稱:畫格數:腳本 可單跑探索。
# docker run 帶 --init：xvfb-run 當 PID 1 時等不到 Xvfb 的就緒訊號會一直卡住。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DG="$ROOT/workplace/dosgolem"
ORIG="$ROOT/workplace/input/dos/sosb"
FONT="$ROOT/workplace/font/sosb-rounded.golemfnt"
OUT="$ROOT/workplace/probe/g13-demo-receipt"
IMAGE=dosgolem-go-ebiten:1.24-r1
for f in "$ORIG/START.EXE" "$FONT"; do test -f "$f" || { echo "缺 $f" >&2; exit 1; }; done
mkdir -p "$OUT"
(cd "$DG" && DOSGOLEM_TIMEOUT=10m tools/go.sh build -o /src/workplace/bin/sosb-play ./cmd/sosb-play)
run() { # 名稱 畫格數 腳本
  local name=$1 frames=$2 script=$3
  rm -rf "$OUT/$name"; mkdir -p "$OUT/$name"
  timeout 40m docker run --rm --init --network none --memory 2g --cpus 2 --pids-limit 256 \
    --log-opt max-size=10m --log-opt max-file=3 -u "$(id -u):$(id -g)" -e HOME=/tmp -e SOSB_NO_DIALOG=1 \
    -v "$DG/workplace/bin":/app:ro -v "$ORIG":/orig:ro -v "$ROOT/text":/text:ro \
    -v "$ROOT/workplace/font":/font:ro -v "$OUT/$name":/out \
    --entrypoint xvfb-run "$IMAGE" -a /app/sosb-play -original /orig -save /out/save -text-dir /text \
    -font "/font/$(basename "$FONT")" -audio=false -scale 2 -frames "$frames" -script "$script" \
    -shot /out/shot.rgba -shot-original /out/orig.rgba > "$OUT/$name/log.txt" 2>&1
  echo "$name：$(grep 'demo 控制' "$OUT/$name/log.txt" || echo '沒有 demo 控制紀錄')"
}
if [[ -n "${RUN:-}" ]]; then
  IFS=: read -r n f s <<<"$RUN"; run "$n" "$f" "$s"; exit 0
fi
run menu-ref 3260 "3170: " &
run menu 6870 "3170: " &
run play 4400 "3170: ,3690:p" &
wait
for p in message:3800 walk:3960 combat:4500; do  # 一次兩個，避免佔滿共用主機
  n=${p%:*}; a=${p#*:}
  run "$n-at" "$a" "3170: ,3690:d" &
  # 中止後原版依序顯示 Forgotten Realms 開頭圖、本作標題（各等一次按鍵）再進選單；中止所需時間不同（訊息幾乎立刻、
  # 戰鬥約 8 秒），所以每隔 520 格送三次 p：前兩次當任意鍵，到選單時選「進入遊戲」，主選單不理會 p。
  run "$n" $((a + 3800)) "3170: ,3690:d,$a: ,$((a + 2000)):p,$((a + 2520)):p,$((a + 3040)):p" &
  wait
done
if grep -l "缺字" "$OUT"/*/log.txt; then echo "有缺字" >&2; exit 1; fi
timeout 300 docker run --rm --network none --memory 1g --cpus 1 --pids-limit 32 --log-opt max-size=10m --log-opt max-file=3 \
  -u "$(id -u):$(id -g)" -v "$OUT":/r sosb-img:r1 python3 -I -c '
import re, sys
from PIL import Image, ImageChops
def shot(n):
    return Image.frombytes("RGBA", (640, 400), open(f"/r/{n}/orig.rgba", "rb").read()).convert("RGB")
def diff(a, b):
    d = ImageChops.difference(shot(a), shot(b)).convert("L")
    return sum(1 for v in d.getdata() if v)
def demo(n):
    m = re.search(r"逾時寫入擋下 (\d+) 次、中止 (\d+) 次、中止後返回 (\d+) 次（最近 (\d+) 步）、執行中 (\w+)、錯誤 (\S+)",
                  open(f"/r/{n}/log.txt", encoding="utf-8").read())
    return (int(m[1]), int(m[2]), int(m[3]), int(m[4]), m[5] == "true", m[6]) if m else None
ok = True
def check(name, cond, msg):
    global ok
    ok &= bool(cond)
    print(f"{name}：{msg}", "通過" if cond else "不通過")
for n in ("menu-ref", "menu", "play", "message-at", "message", "walk-at", "walk", "combat-at", "combat"):
    shot(n).save(f"/r/{n}.png")
d = demo("menu"); px = diff("menu", "menu-ref")
check("menu", d and d[0] >= 1 and d[1] == 0 and not d[4] and d[5] == "<nil>" and px == 0,
      f"逾時擋下 {d and d[0]} 次、未進 demo；停留 3700 格後與選單剛出現的畫面差 {px} 像素")
for n in ("message", "walk", "combat"):
    at, af = demo(f"{n}-at"), demo(n); px = diff(n, "play")
    check(n, at and at[4] and af and af[1] == 1 and af[2] == 1 and not af[4] and af[5] == "<nil>" and px == 0,
          f"按鍵時在 demo={at and at[4]}；中止 {af and af[1]}、返回 {af and af[2]}（{af and af[3]} 步）；"
          f"按 p 後與不經 demo 的主選單畫面差 {px} 像素")
sys.exit(0 if ok else 1)
'
