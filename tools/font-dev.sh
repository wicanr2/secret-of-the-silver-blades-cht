#!/usr/bin/env bash
# 由正式譯文（text/*.tsv）與工作區譯文批次重建開發用圓體字型（AGENTS.md 第 1 節：源泉圓體，2 倍 Medium、3 倍 Bold）。
# 輸出 workplace/font/sosb-rounded.golemfnt（16×16）與 sosb-rounded-3x.golemfnt（24×24）。
# 字型來源：workplace/fonts-src/rounded（GenSenRounded2 TW v2.100，OFL）、workplace/fonts-src/unifont（GNU Unifont 17.0.05，補字）。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/workplace/fonts-src"
UNI="$SRC/unifont/unifont-17.0.05/font/precompiled"
for f in "$SRC/rounded/GenSenRounded2TW-M.otf" "$SRC/rounded/GenSenRounded2TW-B.otf" "$UNI/unifont_t-17.0.05.hex"; do
  test -f "$f" || { echo "缺字型來源 $f" >&2; exit 1; }
done
mkdir -p "$ROOT/workplace/font"
cats=()
for f in "$ROOT"/text/*.tsv; do
  case "$(basename "$f")" in *-events.tsv|errata.tsv|glossary.tsv|term-avoid.tsv|walkthrough-terms.tsv|quiz-answers.tsv|translit-arpabet.tsv|translit-table.tsv|translit-names.tsv) continue ;; esac
  cats+=("/text/$(basename "$f")")
done
while IFS= read -r f; do cats+=("/w/${f#"$ROOT/workplace/"}"); done < <(find "$ROOT/workplace/tr" "$ROOT/workplace/text-src/trial" -name '*.tsv' -path '*done*' -o -name '*.zh-TW.tsv' -path '*trial*' 2>/dev/null | sort)
timeout 900 docker run --rm --network none -u "$(id -u):$(id -g)" --memory 2g --cpus 2 --pids-limit 32 \
  --log-opt max-size=10m --log-opt max-file=3 \
  -v "$ROOT/tools:/tools:ro" -v "$ROOT/text:/text:ro" -v "$ROOT/workplace:/w" -v "$SRC/rounded:/f:ro" -v "$UNI:/uni:ro" \
  sosb-img:r1 sh -c "
  python -I /tools/rounded_font.py ${cats[*]} --otf /f/GenSenRounded2TW-M.otf --cell 16 --fallback /uni/unifont_t-17.0.05.hex --out /w/font/sosb-rounded.golemfnt &&
  python -I /tools/rounded_font.py ${cats[*]} --otf /f/GenSenRounded2TW-B.otf --cell 24 --fallback /uni/unifont_t-17.0.05.hex --out /w/font/sosb-rounded-3x.golemfnt"
ls -la "$ROOT/workplace/font"/sosb-rounded*.golemfnt
