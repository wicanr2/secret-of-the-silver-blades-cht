#!/usr/bin/env bash
# G8 攻略面板收據（克萊恩英豪規格 008）：sosb-play 冷開機到主選單（同 tools/play-smoke.sh），以腳本動作開 F6 攻略面板截圖。
# 組合：open（開面板）、next（開面板後換到下一段）、far（連換 N 段，預設 25，半蜘精靈基地的地圖圖例）。
# docker run 帶 --init：xvfb-run 當 PID 1 時等不到 Xvfb 的就緒訊號會一直卡住。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DG="$ROOT/workplace/dosgolem"
ORIG="$ROOT/workplace/input/dos/sosb"
FONT="$ROOT/workplace/font/sosb-rounded.golemfnt"
OUT="$ROOT/workplace/probe/g8-guide-receipt"
IMAGE=dosgolem-go-ebiten:1.24-r1
FAR=${FAR:-25}
for f in "$ORIG/START.EXE" "$FONT" "$ROOT/text/walkthrough.zh-TW.tsv"; do test -f "$f" || { echo "缺 $f" >&2; exit 1; }; done
(cd "$DG" && DOSGOLEM_TIMEOUT=10m tools/go.sh build -o /src/workplace/bin/sosb-play ./cmd/sosb-play)
rm -rf "$OUT"; mkdir -p "$OUT"
run() { # 名稱 腳本
  local name=$1 script=$2
  mkdir -p "$OUT/$name"
  timeout 10m docker run --rm --init --network none --memory 2g --cpus 2 --pids-limit 256 \
    --log-opt max-size=10m --log-opt max-file=3 -u "$(id -u):$(id -g)" -e HOME=/tmp -e SOSB_NO_DIALOG=1 \
    -v "$DG/workplace/bin":/app:ro -v "$ORIG":/orig:ro -v "$ROOT/text":/text:ro -v "$ROOT/workplace/font":/font:ro \
    -v "$OUT/$name":/out --entrypoint xvfb-run "$IMAGE" -a /app/sosb-play -original /orig -save /out/save -text-dir /text \
    -font "/font/$(basename "$FONT")" -audio=false -scale 2 -frames 4300 -script "3200: ,3700:p,$script" \
    -shot /out/shot.rgba > "$OUT/$name/log.txt" 2>&1
}
nexts=""; for ((i = 0; i < FAR; i++)); do nexts+=",$((4110 + i * 4)):next"; done
run open 4100:guide &
run next 4100:guide,4150:next &
run far "4100:guide$nexts" &
wait
if grep -l '缺字' "$OUT"/*/log.txt; then echo "有缺字" >&2; exit 1; fi
timeout 120 docker run --rm --network none --memory 1g --cpus 1 --pids-limit 64 --log-opt max-size=10m --log-opt max-file=3 \
  -u "$(id -u):$(id -g)" -v "$OUT":/d sosb-img:r1 python3 -c "
from PIL import Image
for n in ('open', 'next', 'far'):
    Image.frombytes('RGBA', (640, 400), open(f'/d/{n}/shot.rgba', 'rb').read()).save(f'/d/{n}.png')"
cd "$OUT" && sha256sum */shot.rgba
