#!/usr/bin/env bash
# 由正式譯文（text/*.tsv）與工作區譯文批次重建開發用圓體字型（AGENTS.md 第 1 節：源泉圓體，2 倍 Medium、3 倍 Bold）。
# 輸出 workplace/font/sosb-rounded.golemfnt（16×16）與 sosb-rounded-3x.golemfnt（24×24）；
# 切換列字級（主專案規格 020）另出 sosb-rounded-bar12.golemfnt（Medium）與 -bar22.golemfnt（Bold），字集只收 host-text。
# 字型來源：workplace/fonts-src/rounded（GenSenRounded2 TW v2.100，OFL）、workplace/fonts-src/unifont（GNU Unifont 17.0.05，補字）。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/workplace/fonts-src"
UNI="$SRC/unifont/unifont-17.0.05/font/precompiled"
for f in "$SRC/rounded/GenSenRounded2TW-M.otf" "$SRC/rounded/GenSenRounded2TW-B.otf" "$UNI/unifont_t-17.0.05.hex"; do
  test -f "$f" || { echo "缺字型來源 $f" >&2; exit 1; }
done
mkdir -p "$ROOT/workplace/font"
# 繁中字集只收玩家看得到的表（明確清單，同克萊恩英豪；新表要顯示中文時加在這裡）
cats=()
for f in ecl-text.zh-TW ui-text.zh-TW name.zh-TW composed-templates host-text.zh-TW journal.zh-TW journal-maps.zh-TW menu-masters \
  translit-chars.zh-TW walkthrough.zh-TW map-guide.zh-TW map-geo map-titles; do
  test -f "$ROOT/text/$f.tsv" || { echo "缺 text/$f.tsv" >&2; exit 1; }
  cats+=("/text/$f.tsv")
done
while IFS= read -r f; do cats+=("/w/${f#"$ROOT/workplace/"}"); done < <(find "$ROOT/workplace/tr" "$ROOT/workplace/text-src/trial" -name '*.tsv' -path '*done*' -o -name '*.zh-TW.tsv' -path '*trial*' 2>/dev/null | sort)
timeout 900 docker run --rm --network none -u "$(id -u):$(id -g)" --memory 2g --cpus 2 --pids-limit 32 \
  --log-opt max-size=10m --log-opt max-file=3 \
  -v "$ROOT/tools:/tools:ro" -v "$ROOT/text:/text:ro" -v "$ROOT/workplace:/w" -v "$SRC/rounded:/f:ro" -v "$UNI:/uni:ro" \
  sosb-img:r1 sh -c "
  python -I /tools/rounded_font.py ${cats[*]} --otf /f/GenSenRounded2TW-M.otf --cell 16 --fallback /uni/unifont_t-17.0.05.hex --out /w/font/sosb-rounded.golemfnt &&
  python -I /tools/rounded_font.py ${cats[*]} --otf /f/GenSenRounded2TW-B.otf --cell 24 --fallback /uni/unifont_t-17.0.05.hex --out /w/font/sosb-rounded-3x.golemfnt &&
  python -I /tools/rounded_font.py /text/host-text.zh-TW.tsv --otf /f/GenSenRounded2TW-M.otf --cell 12 --fallback /uni/unifont_t-17.0.05.hex --out /w/font/sosb-rounded-bar12.golemfnt &&
  python -I /tools/rounded_font.py /text/host-text.zh-TW.tsv --otf /f/GenSenRounded2TW-B.otf --cell 22 --fallback /uni/unifont_t-17.0.05.hex --out /w/font/sosb-rounded-bar22.golemfnt"
# 多語系（克萊恩英豪規格 015 §2.5、§3.1）：简中、日文、韓文用 GNU Unifont 各地字形，字集取該語言的 *.<語言>.tsv；
# 英文用 Courier Prime Bold（workplace/fonts-src/courier，OFL）拉寬，2 倍 16×16、3 倍 24×24。
shopt -s nullglob
for L in zh-CN:unifont ja:unifont_jp ko:unifont_t; do
  code=${L%%:*} hex=${L#*:}
  lc=(); for f in "$ROOT"/text/*."$code".tsv; do lc+=("/text/$(basename "$f")"); done
  # 玩家名音譯字集（規格 013、015）：該語言有自己的音譯表時一併收字
  test -f "$ROOT/text/translit-$code/translit-chars.zh-TW.tsv" && lc+=("/text/translit-$code/translit-chars.zh-TW.tsv")
  (( ${#lc[@]} )) || continue
  timeout 600 docker run --rm --network none -u "$(id -u):$(id -g)" --memory 1g --cpus 1 --pids-limit 32 \
    --log-opt max-size=10m --log-opt max-file=3 \
    -v "$ROOT/tools:/tools:ro" -v "$ROOT/text:/text:ro" -v "$ROOT/workplace:/w" -v "$UNI:/uni:ro" \
    sosb-img:r1 python -I /tools/eten_font.py "${lc[@]}" --unifont "/uni/$hex-17.0.05.hex" --out "/w/font/sosb-$code.golemfnt"
done
if test -f "$ROOT/text/host-text.en.tsv" && test -f "$SRC/courier/courierprime__CourierPrime-Bold.ttf"; then
  for c in 16 24; do
    n=sosb-en; [[ $c == 24 ]] && n=sosb-en-3x
    timeout 300 docker run --rm --network none -u "$(id -u):$(id -g)" --memory 1g --cpus 1 --pids-limit 32 \
      --log-opt max-size=10m --log-opt max-file=3 \
      -v "$ROOT/tools:/tools:ro" -v "$SRC/courier:/f:ro" -v "$ROOT/workplace:/w" \
      sosb-img:r1 python -I /tools/en_font.py --ttf /f/courierprime__CourierPrime-Bold.ttf --cell $c --out "/w/font/$n.golemfnt"
  done
fi
ls -la "$ROOT/workplace/font"/sosb-*.golemfnt
