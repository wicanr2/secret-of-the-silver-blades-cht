#!/usr/bin/env bash
# Windows zip 的 Wine smoke（規格 012 §4 第 3 項；由克萊恩英豪 tools/release/smoke-windows.sh 移植）：
# 解開 zip，空資料目錄冷開機，第 2400 格截標題，再送空白、p 進主選單，3 倍畫面截圖；再拿掉原版與已匯入的 game/，
# 驗以錯誤結束並留下 sosb-error.log。patch 包把原版放在 exe 旁，full-local 包本來就有 original/。
# ⚠ Wine 不是 Windows。原版、HD 兩包各跑一次。截圖與 Linux smoke 比對（先跑 smoke-linux.sh）。
# Wine 預設語系是 en-US，不指定時依設計選英文（規格 015）；比對用 -lang zh-TW。
#
#   tools/release/smoke-windows.sh <版本> [patch|full-local]
# 輸出：dist-all/<版本>/smoke/<種類>/windows-<版別>/。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VER="${1:?版本}"
KIND="${2:-patch}"
SUF=""; [[ $KIND == full-local ]] && SUF=-with-data
ORIG="$ROOT/workplace/input/dos/sosb"
IMAGE=psgolem-wine-verify:noble-r2  # 只使用，不刪除、不改標籤
test -f "$ORIG/START.EXE" || { echo "缺原版 $ORIG" >&2; exit 1; }
for ed in base hd; do
  sfx=""; [[ $ed == hd ]] && sfx=-hd
  zip="$ROOT/dist-all/$VER/$KIND/SOSBCHT-$VER$sfx$SUF-win64.zip"
  if ! test -f "$zip"; then [[ $ed == hd ]] && { echo "略過 hd（沒有 HD 包）"; continue; }; echo "缺 $zip" >&2; exit 1; fi
  out="$ROOT/dist-all/$VER/smoke/$KIND/windows-$ed"
  rm -rf "$out"; mkdir -p "$out/win"
  timeout 300 docker run --rm --network none --memory 512m --cpus 1 --pids-limit 32 --log-opt max-size=10m --log-opt max-file=3 \
    -u "$(id -u):$(id -g)" -v "$(dirname "$zip"):/z:ro" -v "$out:/v" python:3.13-slim \
    python -I -c "import zipfile; zipfile.ZipFile('/z/$(basename "$zip")').extractall('/v/win')"
  if [[ $KIND == patch ]]; then mkdir -p "$out/win/SOSBCHT/original"; cp -r "$ORIG"/. "$out/win/SOSBCHT/original/"; fi
  test -f "$out/win/SOSBCHT/original/START.EXE" || { echo "$ed：exe 旁沒有 original/" >&2; exit 1; }
  timeout 30m docker run --rm --init --network none --memory 4g --cpus 2 --pids-limit 512 --log-opt max-size=10m --log-opt max-file=3 \
    -u "$(id -u):$(id -g)" -e HOME=/wine -e WINEDEBUG=-all -e WINEDLLOVERRIDES="mscoree,mshtml=" -e SOSB_NO_DIALOG=1 \
    -v "$out:/v" --tmpfs "/wine:exec,uid=$(id -u),gid=$(id -g),size=2g" --entrypoint bash "$IMAGE" -c '
export WINEPREFIX=/wine/prefix
mkdir -p /tmp/.X11-unix; Xvfb :99 -screen 0 1280x800x24 -nolisten tcp -ac >/dev/null 2>&1 &
i=0; while [ ! -S /tmp/.X11-unix/X99 ] && [ $i -lt 50 ]; do sleep 0.1; i=$((i+1)); done; export DISPLAY=:99
wine --version; wine wineboot -i >/dev/null 2>&1
cd /v/win/SOSBCHT
wine ./SOSBCHT.exe -audio=false -lang zh-TW -scale 3 -frames 4400 -script "2400:shot,3200: ,3700:p" -shot "Z:\\v\\menu.rgba" > /v/run.log 2>&1; echo "run exit=$?"
D=$(ls -d /wine/prefix/drive_c/users/*/AppData/Roaming/SOSBCHT); ls "$D"; ls "$D/game" | grep -c . | sed "s/^/game 檔數 /"; cp "$D/screenshots/sosb-f002400.png" /v/title.png
rm -rf original "$D/game"
wine ./SOSBCHT.exe -audio=false -frames 5 > /v/noorig.log 2>&1; echo "noorig exit=$?"
cp "$D/sosb-error.log" /v/ 2>/dev/null; ls "$D"' > "$out/smoke.txt" 2>&1
  cat "$out/smoke.txt"
  grep -qx "run exit=0" "$out/smoke.txt" || { echo "$ed：冷開機執行失敗" >&2; tail -5 "$out/run.log" >&2; exit 1; }
  grep -q '^game 檔數 [1-9]' "$out/smoke.txt" || { echo "$ed：原版沒有匯入 game/" >&2; exit 1; }
  grep -qE "^noorig exit=[1-9]" "$out/smoke.txt" || { echo "$ed：拿掉原版後應以錯誤結束" >&2; exit 1; }
  test -s "$out/sosb-error.log" || { echo "$ed：拿掉原版後沒有 sosb-error.log" >&2; exit 1; }
  test -s "$out/menu.rgba" || { echo "$ed：沒有主選單截圖" >&2; exit 1; }
  test -s "$out/title.png" || { echo "$ed：沒有標題截圖" >&2; exit 1; }
  rm -rf "$out/win"
done
docker run -i --rm --network none --memory 1g --cpus 1 --pids-limit 32 --log-opt max-size=10m --log-opt max-file=3 \
  -u "$(id -u):$(id -g)" -e KIND="$KIND" -v "$ROOT/dist-all/$VER/smoke":/r sosb-img:r1 python3 -I - <<'PY'
import hashlib, os
from PIL import Image
k = os.environ['KIND']
for ed in ('base', 'hd'):
    p = f'/r/{k}/windows-{ed}/menu.rgba'
    if not os.path.exists(p):
        continue
    w = open(p, 'rb').read()
    Image.frombytes('RGBA', (960, 600), w).convert('RGB').save(p[:-5] + '.png')
    lp = f'/r/{k}/linux-{ed}/menu.rgba'
    if not os.path.exists(lp):
        print(ed, '沒有 Linux 截圖可比'); continue
    l = open(lp, 'rb').read()
    diff = sum(w[i:i + 4] != l[i:i + 4] for i in range(0, len(w), 4)) if len(w) == len(l) else -1
    print(ed, 'Windows 主選單截圖 sha256', hashlib.sha256(w).hexdigest()[:16], '與 Linux 相同' if w == l else f'與 Linux 不同 {diff} 像素')
    wt = Image.open(f'/r/{k}/windows-{ed}/title.png').convert('RGB').tobytes()
    lt = Image.open(f'/r/{k}/linux-{ed}/title.png').convert('RGB').tobytes()
    print(ed, 'Windows 標題截圖', '與 Linux 相同' if wt == lt else '與 Linux 不同')
PY
