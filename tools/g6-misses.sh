#!/usr/bin/env bash
# 彙整盤點 inv.tsv／inventory.tsv 的未命中印字（移植克萊恩英豪 tools/area-misses.sh）：排除純數字、生命值與骰子表示法、
# 空白、標點、查驗題作答回顯的單一字母、預建隊員名與片頭的人名、題名、版本列（docs/re/007 決定維持原文），剩下的就是缺口。
# 用法：tools/g6-misses.sh <inv.tsv>…   輸出「次數  路徑  原文」。
set -euo pipefail
awk -F'\t' '
  FNR == 1 { next }
  $8 !~ /未命中/ { next }
  { t = $9; gsub(/^ +| +$/, "", t) }
  t == "" { next }
  t ~ /^[-+0-9()\/d ,.:%]+$/ { next }
  t ~ /^[A-Z]$/ { next }
  t ~ /^[.'"'"'"!?,]+$/ { next }
  toupper(t) ~ /^(GUY DE VALOIS|PAINE|EPONA|MALACHITE|DOMINIC|MORGAINE)$/ { next }
  t ~ /^(erik flom,james young,larry webber|Secret of the Silver Blades|Version 1\.30 +May 18,1990)$/ { next }
  { c[$2 "\t" t]++ }
  END { for (k in c) printf "%5d\t%s\n", c[k], k }
' "$@" | sort -rn
