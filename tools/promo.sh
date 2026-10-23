#!/usr/bin/env bash
# 推廣影片（規格 016，#11；由克萊恩英豪移植）：錄各段、組裝成 workplace/promo/sosb-promo.mp4。各段分鏡檢查用 tools/promo-sheet.sh。
# town-nohd、battle-nohd 是同參數不載入 HD 的原版對照段（HD 切換示範）；f12 是中文與英文原版切換示範。
# 前置：dosgolem 的 sosb-promo（tools/go.sh build -o /src/workplace/bin/sosb-promo ./cmd/sosb-promo）、cok-ffmpeg:r1、
# HD 主題 hd/theme、各語言字型（tools/font-dev.sh）、配樂 workplace/music/out/、下列狀態檔。
#
# 狀態檔載入前已印的文字沒有覆繪，而且狀態檔不含 OPL 暫存器：
# - 標題曲在第 43M 步讀 SOUND.dax 時設好音色，所以 title 從冷開機第 40M 步的狀態起錄（workplace/probe/g10-promo，
#   cmd/probe 冷開機回答設定後 -save-state 40000000）。
# - 鎮上先紮營再離開讓遊戲重印隊伍欄；戰鬥從 well-fight 狀態起錄，每 15M 步送 Q（電腦控制）。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; R="$ROOT/tools/promo-rec.sh"; CR=$'\r'; P="$ROOT/workplace/probe"
OPEN=(-keys "$CR$CR$CR$CR$CR$CR$CR$CR" -key-from 840000000 -key-every 40000000)
TOWN=(-keys-at "1730000000:E,1760000000:E,1780000000:M" -key-names 'Left,Up,Right,Up,Up,Up,Up,Up,Left,Up,Up,Up,Up'
  -key-from 1800000000 -key-every 20000000)
Q=$(for i in $(seq 0 11); do printf '%d:Q,' $((10830000000 + i * 15000000)); done)
"$R" title "$P/g10-promo" boot-40m.state 41000000 460000000 &
"$R" open "$P/g3-receipt" intro.state 835000000 1720000000 "${OPEN[@]}" \
  -keys-at "1210000000:Enter,1250000000:E,1290000000:N,1330000000:Enter,1370000000:Enter,1410000000:Enter"; wait
"$R" town "$P/g3-receipt" town.state 1722000000 2290000000 "${TOWN[@]}" \
  -actions "2070000000:map,2100000000:map-reveal,2130000000:map-close,2132000000:guide=1:1,2165000000:guide-page,2195000000:guide-close" &
PROMO_NOHD=1 "$R" town-nohd "$P/g3-receipt" town.state 1722000000 2070000000 "${TOWN[@]}"; wait
"$R" battle "$P/g6-states/well-fight" fight.state 10826000000 11030000000 -keys-at "${Q%,}" &
PROMO_NOHD=1 "$R" battle-nohd "$P/g6-states/well-fight" fight.state 10826000000 11030000000 -keys-at "${Q%,}"; wait
"$R" f12 "$P/g3-receipt" intro.state 955000000 1045000000 "${OPEN[@]}" -actions "982000000:original,1015000000:chinese" &
"$R" langs "$P/g3-receipt" intro.state 955000000 1045000000 "${OPEN[@]}" \
  -actions "968000000:lang=zh-CN,982000000:lang=ja,996000000:lang=ko,1010000000:lang=en,1024000000:lang=zh-TW"; wait
"$ROOT/tools/promo-build.sh"
