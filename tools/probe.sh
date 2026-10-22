#!/usr/bin/env bash
# dosgolem 探針包裝：tools/probe.sh <輸出目錄> <cmd/probe 參數…>
# 原版唯讀掛 /orig，輸出目錄掛 /out，狀態庫 workplace/probe/states 掛 /st（唯讀）。
# 固定 -root /orig 與 -program-path C:\SECRET\START.EXE（docs/re/003）；scratch 由呼叫端用 -scratch-dir 指定。
# 換成別的 cmd：PROBE_CMD=./cmd/sosb-overlay-shot（此時不帶 -root／-program-path，由呼叫端給）。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$(mkdir -p "$1" && cd "$1" && pwd)"; shift
mkdir -p "$ROOT/workplace/probe/states"
test -f "$ROOT/workplace/input/dos/sosb/START.EXE" || { echo "缺原版（先跑 G1）" >&2; exit 1; }
CMD="${PROBE_CMD:-./cmd/probe}"
FIXED=(-root /orig -program-path 'C:\SECRET\START.EXE')
[[ "$CMD" == ./cmd/probe ]] || FIXED=()
cd "$ROOT/workplace/dosgolem"
DOSGOLEM_ORIG="$ROOT/workplace/input/dos/sosb" \
DOSGOLEM_EXTRA_MOUNTS="$OUT:/out;$ROOT/workplace/probe/states:/st:ro;$ROOT/text:/text:ro;$ROOT/workplace/font:/font:ro;$ROOT/workplace/text-src:/textsrc:ro" \
DOSGOLEM_TIMEOUT="${PROBE_TIMEOUT:-20m}" DOSGOLEM_CPUS="${PROBE_CPUS:-2}" \
  tools/go.sh run "$CMD" "${FIXED[@]}" "$@"
