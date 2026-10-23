#!/usr/bin/env bash
# Linux AppImage smoke（規格 012 §4 第 3 項；由克萊恩英豪 tools/release/smoke-linux.sh 移植）：
# 空資料目錄冷開機，第 2400 格截標題（規格 010：HD 版換成重繪圖），再送空白、p 進主選單（同 tools/play-smoke.sh），
# 3 倍畫面截圖。原版、HD 兩包各跑一次；兩包的標題應不同、主選單（沒有 HD 圖）應相同。
# patch 包把原版放在 AppImage 旁，再驗缺原版時以錯誤結束並留下 sosb-error.log；
# full-local 包的原版在 AppImage 內，只驗冷開機與原版匯入（拿不掉包內原版，缺原版的情形由 patch 包驗）。
#
#   tools/release/smoke-linux.sh <版本> [patch|full-local]
# 輸出：dist-all/<版本>/smoke/<種類>/linux-<版別>/（截圖 PNG、log、錯誤紀錄）。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VER="${1:?版本}"
KIND="${2:-patch}"
SUF=""; [[ $KIND == full-local ]] && SUF=-with-data
ORIG="$ROOT/workplace/input/dos/sosb"
IMAGE=dosgolem-go-ebiten:1.24-r1
test -f "$ORIG/START.EXE" || { echo "缺原版 $ORIG" >&2; exit 1; }
for ed in base hd; do
  sfx=""; [[ $ed == hd ]] && sfx=-hd
  app="$ROOT/dist-all/$VER/$KIND/SOSBCHT-$VER$sfx$SUF-x86_64.AppImage"
  if ! test -f "$app"; then [[ $ed == hd ]] && { echo "略過 hd（沒有 HD 包）"; continue; }; echo "缺 $app" >&2; exit 1; fi
  out="$ROOT/dist-all/$VER/smoke/$KIND/linux-$ed"
  rm -rf "$out"; mkdir -p "$out/pkg" "$out/home"
  cp "$app" "$out/pkg/SOSBCHT.AppImage"
  [[ $KIND == patch ]] && { mkdir -p "$out/pkg/original"; cp -r "$ORIG"/. "$out/pkg/original/"; }
  # 第 1 次：冷開機進主選單；-scale 3 讓 HD 版畫出 HD。APPIMAGE_EXTRACT_AND_RUN：容器內沒有 FUSE。
  # 第 2 次（只有 patch）：拿掉原版與已匯入的 game/，應以錯誤結束。
  timeout 15m docker run --rm --init --network none --memory 2g --cpus 2 --pids-limit 256 \
    --log-opt max-size=10m --log-opt max-file=3 -u "$(id -u):$(id -g)" -e HOME=/s/home -e APPIMAGE_EXTRACT_AND_RUN=1 \
    -e SOSB_NO_DIALOG=1 -e KIND="$KIND" -v "$out:/s" -w /s/pkg --entrypoint sh "$IMAGE" -c '
      xvfb-run -a ./SOSBCHT.AppImage -audio=false -scale 3 -frames 4400 -script "2400:shot,3200: ,3700:p" -shot /s/menu.rgba > /s/run.log 2>&1; echo "run exit=$?"
      xvfb-run -a ./SOSBCHT.AppImage -version  # ebiten 在 init 就開 GLFW，沒有顯示會 panic
      D=/s/home/.local/share/sosb-cht; ls "$D"; ls "$D/game" | grep -c . | sed "s/^/game 檔數 /"; cp "$D/screenshots/sosb-f002400.png" /s/title.png
      if [ "$KIND" = patch ]; then
        rm -rf original "$D/game"
        xvfb-run -a ./SOSBCHT.AppImage -audio=false -frames 5 > /s/noorig.log 2>&1; echo "noorig exit=$?"
        cp "$D/sosb-error.log" /s/ 2>/dev/null; ls "$D"
      fi' > "$out/smoke.txt" 2>&1
  cat "$out/smoke.txt"
  # 結束碼與截圖都要檢查（前作 v.0.9.5–v.1.0.2 一啟動就結束，舊腳本沒看結束碼而照樣回報成功）
  grep -qx "run exit=0" "$out/smoke.txt" || { echo "$ed：冷開機執行失敗" >&2; tail -5 "$out/run.log" >&2; exit 1; }
  grep -q '^game 檔數 [1-9]' "$out/smoke.txt" || { echo "$ed：原版沒有匯入 game/" >&2; exit 1; }
  if [[ $KIND == patch ]]; then
    grep -qE "^noorig exit=[1-9]" "$out/smoke.txt" || { echo "$ed：拿掉原版後應以錯誤結束" >&2; exit 1; }
    test -s "$out/sosb-error.log" || { echo "$ed：拿掉原版後沒有 sosb-error.log" >&2; exit 1; }
  fi
  test -s "$out/menu.rgba" || { echo "$ed：沒有主選單截圖" >&2; exit 1; }
  test -s "$out/title.png" || { echo "$ed：沒有標題截圖" >&2; exit 1; }
  if grep -q '缺字' "$out/run.log"; then echo "$ed：有缺字" >&2; exit 1; fi
  rm -rf "$out/pkg"
done
docker run -i --rm --network none --memory 1g --cpus 1 --pids-limit 32 --log-opt max-size=10m --log-opt max-file=3 \
  -u "$(id -u):$(id -g)" -e KIND="$KIND" -v "$ROOT/dist-all/$VER/smoke":/r sosb-img:r1 python3 -I - <<'PY'
import hashlib, os, sys
from PIL import Image, ImageStat
k = os.environ['KIND']
px = {ed: Image.open(f'/r/{k}/linux-{ed}/title.png').convert('RGB').tobytes() for ed in ('base', 'hd') if os.path.exists(f'/r/{k}/linux-{ed}/title.png')}
for ed, b in px.items():
    print(ed, '標題截圖 sha256', hashlib.sha256(b).hexdigest()[:16])
if len(px) == 2:
    n = sum(px['base'][i:i + 3] != px['hd'][i:i + 3] for i in range(0, len(px['base']), 3))
    print('HD 版標題與原版不同', n, '像素' if n else '像素（HD 沒有載入）')
    if not n:
        sys.exit(1)
for ed in ('base', 'hd'):
    p = f'/r/{k}/linux-{ed}/menu.rgba'
    if not os.path.exists(p):
        continue
    raw = open(p, 'rb').read()
    im = Image.frombytes('RGBA', (960, 600), raw).convert('RGB')
    im.save(p[:-5] + '.png')
    print(ed, '主選單截圖 sha256', hashlib.sha256(raw).hexdigest()[:16], '標準差', [round(s, 1) for s in ImageStat.Stat(im).stddev])
PY
