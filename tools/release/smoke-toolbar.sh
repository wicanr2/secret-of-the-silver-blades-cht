#!/usr/bin/env bash
# 發行包切換列冒煙（規格 012、020）：Linux AppImage 與 Windows zip（Wine）各跑原版、HD 兩包，
# 冷開機到第 2400 格標題畫面，腳本動作 bar 讓切換列常駐、barfont=2 用中字級，3 倍截圖。
# 檢查結束碼 0、沒有缺字；切換列（上方 96 像素）Linux 與 Wine 逐像素相同；HD 包的標題與原版包不同。
# Wine 預設語系是 en-US，兩邊都指定 -lang zh-TW。
#
#   tools/release/smoke-toolbar.sh <版本> [patch|full-local]
# 輸出：dist-all/<版本>/smoke/<種類>/toolbar-<平台>-<版別>.png 與 toolbar.txt。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VER="${1:?版本}"
KIND="${2:-patch}"
SUF=""; [[ $KIND == full-local ]] && SUF=-with-data
ORIG="$ROOT/workplace/input/dos/sosb"
OUT="$ROOT/dist-all/$VER/smoke/$KIND/toolbar"
ARGS='-audio=false -lang zh-TW -scale 3 -frames 2400 -script 1:bar,2:barfont=2'
test -f "$ORIG/START.EXE" || { echo "缺原版 $ORIG" >&2; exit 1; }
rm -rf "$OUT"; mkdir -p "$OUT"
for ed in base hd; do
  sfx=""; [[ $ed == hd ]] && sfx=-hd
  app="$ROOT/dist-all/$VER/$KIND/SOSBCHT-$VER$sfx$SUF-x86_64.AppImage"
  zip="$ROOT/dist-all/$VER/$KIND/SOSBCHT-$VER$sfx$SUF-win64.zip"
  for f in "$app" "$zip"; do test -f "$f" || { echo "缺 $f" >&2; exit 1; }; done
  d="$OUT/linux-$ed"; mkdir -p "$d/pkg" "$d/home"
  cp "$app" "$d/pkg/SOSBCHT.AppImage"
  [[ $KIND == patch ]] && { mkdir -p "$d/pkg/original"; cp -r "$ORIG"/. "$d/pkg/original/"; }
  timeout 15m docker run --rm --init --network none --memory 2g --cpus 2 --pids-limit 256 \
    --log-opt max-size=10m --log-opt max-file=3 -u "$(id -u):$(id -g)" -e HOME=/s/home -e APPIMAGE_EXTRACT_AND_RUN=1 \
    -e SOSB_NO_DIALOG=1 -v "$d:/s" -w /s/pkg --entrypoint sh dosgolem-go-ebiten:1.24-r1 -c \
    "xvfb-run -a ./SOSBCHT.AppImage $ARGS -shot /s/shot.rgba > /s/run.log 2>&1; echo \"run exit=\$?\"" > "$d/smoke.txt" 2>&1
  rm -rf "$d/pkg" "$d/home"
  w="$OUT/windows-$ed"; mkdir -p "$w/win"
  timeout 300 docker run --rm --network none --memory 512m --cpus 1 --pids-limit 32 --log-opt max-size=10m --log-opt max-file=3 \
    -u "$(id -u):$(id -g)" -v "$(dirname "$zip"):/z:ro" -v "$w:/v" python:3.13-slim \
    python -I -c "import zipfile; zipfile.ZipFile('/z/$(basename "$zip")').extractall('/v/win')"
  [[ $KIND == patch ]] && { mkdir -p "$w/win/SOSBCHT/original"; cp -r "$ORIG"/. "$w/win/SOSBCHT/original/"; }
  timeout 30m docker run --rm --init --network none --memory 4g --cpus 2 --pids-limit 512 --log-opt max-size=10m --log-opt max-file=3 \
    -u "$(id -u):$(id -g)" -e HOME=/wine -e WINEDEBUG=-all -e WINEDLLOVERRIDES="mscoree,mshtml=" -e SOSB_NO_DIALOG=1 \
    -e ARGS="$ARGS" -v "$w:/v" --tmpfs "/wine:exec,uid=$(id -u),gid=$(id -g),size=2g" --entrypoint bash psgolem-wine-verify:noble-r2 -c '
export WINEPREFIX=/wine/prefix
mkdir -p /tmp/.X11-unix; Xvfb :99 -screen 0 1280x800x24 -nolisten tcp -ac >/dev/null 2>&1 &
i=0; while [ ! -S /tmp/.X11-unix/X99 ] && [ $i -lt 50 ]; do sleep 0.1; i=$((i+1)); done; export DISPLAY=:99
wine wineboot -i >/dev/null 2>&1
cd /v/win/SOSBCHT
wine ./SOSBCHT.exe $ARGS -shot "Z:\\v\\shot.rgba" > /v/run.log 2>&1; echo "run exit=$?"' > "$w/smoke.txt" 2>&1
  rm -rf "$w/win"
  for x in "$d" "$w"; do
    grep -qx "run exit=0" "$x/smoke.txt" || { echo "$x：執行失敗" >&2; tail -5 "$x/run.log" >&2; exit 1; }
    if grep -q '缺字' "$x/run.log"; then echo "$x：有缺字" >&2; exit 1; fi
    test -s "$x/shot.rgba" || { echo "$x：沒有截圖" >&2; exit 1; }
  done
done
docker run -i --rm --network none --memory 1g --cpus 1 --pids-limit 32 --log-opt max-size=10m --log-opt max-file=3 \
  -u "$(id -u):$(id -g)" -v "$OUT":/r sosb-img:r1 python3 -I - <<'PY' | tee "$OUT/toolbar.txt"
import hashlib, sys
from PIL import Image
im = {f'{p}-{e}': Image.frombytes('RGBA', (960, 600), open(f'/r/{p}-{e}/shot.rgba', 'rb').read()).convert('RGB')
      for p in ('linux', 'windows') for e in ('base', 'hd')}
ok = True
for k, v in im.items():
    v.save(f'/r/toolbar-{k}.png')
    print(k, '切換列 sha256', hashlib.sha256(v.crop((0, 0, 960, 96)).tobytes()).hexdigest()[:16])
for e in ('base', 'hd'):
    same = im[f'linux-{e}'].crop((0, 0, 960, 96)).tobytes() == im[f'windows-{e}'].crop((0, 0, 960, 96)).tobytes()
    print(e, '切換列 Linux 與 Wine', '相同' if same else '不同'); ok &= same
diff = im['linux-base'].tobytes() != im['linux-hd'].tobytes()
print('HD 包的標題畫面與原版包', '不同' if diff else '相同（HD 沒有載入）'); ok &= diff
sys.exit(0 if ok else 1)
PY
