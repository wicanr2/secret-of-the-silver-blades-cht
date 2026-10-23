#!/usr/bin/env python3
"""合併珍056 說明書校讀稿並檢查頁碼連續（G4，Issue #5 完成條件「轉錄頁碼連續」；docs/re/006）。在 sosb-tools 容器內以 python3 -I 執行。

輸入 workplace/manual-zh/proof/out-*.tsv（cell、volume、page、text、note；校讀者對 300 dpi 頁面圖逐格轉錄，
說明見同目錄 PROMPT.md）。上冊第 49–50 頁的密碼表是跨頁表格，四格都沒有頁尾頁碼：左半（手札題）記 49，
右半（規則書題）記 50（OVERRIDE）。
檢查：每格只出現一次；上冊 1–74、下冊 1–26 每頁至少有一格；text 不含 tab、真換行與常見簡體字。不成立就以結束碼 1 結束。
輸出 TSV：volume、page、cell、text、note（依冊、頁、cell 排序；封面、目錄等無頁碼的格 page 空白、排在該冊最前）。
"""
import argparse
import csv
import sys
from pathlib import Path

OVERRIDE = {'p09r1c1': '50', 'p09r2c1': '50'}
PAGES = {'上冊': 74, '下冊': 26}
SIMPLIFIED = set('银册贼术门这们说时对经过动开')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--proof', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    a = ap.parse_args()
    rows, bad, seen = [], [], set()
    for p in sorted(a.proof.glob('out-*.tsv')):
        with open(p, encoding='utf-8', newline='') as f:
            for r in csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE):
                if r['cell'] in seen:
                    bad.append(f"{r['cell']} 重複")
                seen.add(r['cell'])
                if r['cell'] in OVERRIDE:
                    r['page'] = OVERRIDE[r['cell']]
                    r['note'] = (r['note'] + '；' if r['note'] else '') + '密碼表右頁，頁碼依左右頁推定為 50'
                if r['volume'] not in PAGES:
                    bad.append(f"{r['cell']} 冊別 {r['volume']!r}")
                if r['page'] and (not r['page'].isdigit() or not 1 <= int(r['page']) <= PAGES.get(r['volume'], 0)):
                    bad.append(f"{r['cell']} 頁碼 {r['page']!r} 超出範圍")
                if '\t' in r['text'] or '\n' in r['text'] or SIMPLIFIED & set(r['text']):
                    bad.append(f"{r['cell']} text 含 tab、換行或簡體字")
                rows.append(r)
    for vol, top in PAGES.items():
        have = {int(r['page']) for r in rows if r['volume'] == vol and r['page']}
        miss = [n for n in range(1, top + 1) if n not in have]
        if miss:
            bad.append(f'{vol}缺頁 {miss}')
        print(f'{vol}：{sum(1 for r in rows if r["volume"] == vol)} 格，頁 1–{top} 齊全' if not miss else f'{vol}缺 {len(miss)} 頁')
    rows.sort(key=lambda r: (list(PAGES).index(r['volume']), int(r['page'] or 0), r['cell']))
    out = ['volume\tpage\tcell\ttext\tnote'] + ['\t'.join([r['volume'], r['page'], r['cell'], r['text'], r['note']]) for r in rows]
    a.out.write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(f'{len(rows)} 格 → {a.out}')
    if bad:
        print('\n'.join(bad), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
