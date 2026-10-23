#!/usr/bin/env bash
# macOS zip 結構檢查（規格 012 §4 第 3 項；由克萊恩英豪 tools/release/smoke-macos.sh 移植；沒有 macOS 實機，只驗結構）：
# .app 的執行檔是 universal Mach-O（x86_64＋arm64）、Info.plist 的 CFBundleExecutable 與版號、Resources 內的 text／font／授權，
# HD 版另有 hd/theme.json。patch 包不得含 original/ 與手札地圖頁；full-local 包要有 original/、倚天字型與手札地圖頁。
#
#   tools/release/smoke-macos.sh <版本> [patch|full-local]
# 輸出：dist-all/<版本>/smoke/<種類>/macos.txt。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VER="${1:?版本}"
KIND="${2:-patch}"
SUF=""; [[ $KIND == full-local ]] && SUF=-with-data
test -d "$ROOT/dist-all/$VER/$KIND" || { echo "缺 dist-all/$VER/$KIND" >&2; exit 1; }
mkdir -p "$ROOT/dist-all/$VER/smoke/$KIND"
docker run -i --rm --network none --memory 1g --cpus 1 --pids-limit 32 --log-opt max-size=10m --log-opt max-file=3 \
  -u "$(id -u):$(id -g)" -e VER="$VER" -e KIND="$KIND" -e SUF="$SUF" -v "$ROOT/dist-all/$VER/$KIND":/p:ro python:3.13-slim python -I - <<'PY' | tee "$ROOT/dist-all/$VER/smoke/$KIND/macos.txt"
import os, plistlib, struct, sys, zipfile
ver, kind, suf, ok = os.environ['VER'], os.environ['KIND'], os.environ['SUF'], True
full = kind == 'full-local'
for ed, sfx in (('base', ''), ('hd', '-hd')):
    path = f'/p/SOSBCHT-{ver}{sfx}{suf}-macos.zip'
    if not os.path.exists(path) and ed == 'hd':
        print('略過 hd（沒有 HD 包）'); continue
    z = zipfile.ZipFile(path)
    names = set(z.namelist())
    app = 'SOSBCHT/SOSBCHT.app/Contents/'
    plist = plistlib.loads(z.read(app + 'Info.plist'))
    exe = z.read(app + 'MacOS/' + plist['CFBundleExecutable'])
    magic, n = struct.unpack('>II', exe[:8])
    cpus = {struct.unpack('>I', exe[8 + 20 * i:12 + 20 * i])[0] for i in range(n)} if magic == 0xCAFEBABE else set()
    mode = z.getinfo(app + 'MacOS/' + plist['CFBundleExecutable']).external_attr >> 16
    need = [app + 'Resources/' + p for p in ('text/host-text.zh-TW.tsv', 'text/music-cues.tsv', 'font/sosb-rounded.golemfnt',
            'font/sosb-unifont.golemfnt', 'music/music.tsv', 'LICENSE', 'THIRD-PARTY.md', 'sosb-cht.icns')]
    need += ['SOSBCHT/讀我.txt', 'SOSBCHT/LICENSE']
    hd = app + 'Resources/hd/theme.json' in names
    orig = app + 'Resources/original/START.EXE' in names
    local = [app + 'Resources/font/sosb-eten.golemfnt', app + 'Resources/journal-maps/01-1.png', 'SOSBCHT/本機自用-請勿散布.txt']
    checks = {
        'universal（x86_64 0x1000007、arm64 0x100000C）': cpus == {0x1000007, 0x100000C},
        '執行權限': bool(mode & 0o111),
        f'版號 {ver}': plist['CFBundleVersion'] == ver,
        '必要檔': all(p in names for p in need),
        'hd/theme.json 只在 HD 版': hd == (ed == 'hd'),
    }
    if full:
        checks['含 original/START.EXE'] = orig
        checks['含倚天字型、手札地圖頁與本機自用說明'] = all(p in names for p in local)
    else:
        checks['不含 original/'] = not any('/original/' in p for p in names)
        checks['不含倚天字型與手札地圖頁'] = not any(p in names for p in local[:2]) and not any('journal-maps' in p for p in names)
    for k, v in checks.items():
        print(f'{ed}：{k} {"通過" if v else "不通過"}')
        ok &= v
sys.exit(0 if ok else 1)
PY
