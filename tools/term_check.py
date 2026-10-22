#!/usr/bin/env python3
"""術語一致性檢查：text/term-avoid.tsv 列出的舊譯不得出現在正式譯文（text/*.zh-TW.tsv）。

用法：python3 -I tools/term_check.py [text 目錄]；有殘留就逐一列出並以結束碼 1 結束。
題名「銀色匕首之謎」依使用者決定保留，檢查前先從字串中移除。
"""
import csv
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'text')
with open(root / 'term-avoid.tsv', encoding='utf-8', newline='') as f:
    avoid = list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
bad = []
for p in sorted(root.glob('*.zh-TW.tsv')):
    with open(p, encoding='utf-8', newline='') as f:
        for i, r in enumerate(csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE), 1):
            line = '\t'.join(r[1:]).replace('銀色匕首之謎', '')
            for a in avoid:
                if a['avoid'] in line:
                    bad.append(f"{p.name}:{i} 「{a['avoid']}」應改「{a['use']}」（{a['note']}）")
print(f'檢查 {len(avoid)} 個舊譯')
if bad:
    print('\n'.join(bad), file=sys.stderr)
    sys.exit(1)
