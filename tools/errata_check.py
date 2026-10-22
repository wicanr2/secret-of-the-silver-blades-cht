#!/usr/bin/env python3
"""檢查錯譯表 text/errata.tsv（AGENTS.md 第 3.2 節）。

欄位：key、entry、page、en、zh056、fix、category、reason、evidence、source。
- key 唯一，欄數正確，category 與 evidence 在允許清單內，page 在珍056 手札頁範圍（下冊 27–57）。
- fix 必須出現在正式手札譯文 text/journal.zh-TW.tsv 該則的 title 或 body；zh056 不得再出現在該則。
  例外：漏譯條目的 zh056 是保留下來的上下文；同一則另有合法用法時在 reason 寫「保留他處」。
任一條不成立就列出並以結束碼 1 結束。
"""
import argparse
import csv
import sys
from pathlib import Path

COLS = ['key', 'entry', 'page', 'en', 'zh056', 'fix', 'category', 'reason', 'evidence', 'source']
CATEGORIES = {'誤譯', '漏譯', '增譯', '專名', '譯名不一致', '錯字', '語氣'}
EVIDENCE = {'已證實', '強推論', '假說'}


def read(path):
    with open(path, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--errata', type=Path, default=Path('text/errata.tsv'))
    ap.add_argument('--journal', type=Path, default=Path('text/journal.zh-TW.tsv'))
    a = ap.parse_args()
    with open(a.errata, encoding='utf-8') as f:
        head = f.readline().rstrip('\n').split('\t')
    bad = []
    if head != COLS:
        bad.append(f'欄名 {head}，要 {COLS}')
    rows = read(a.errata)
    jour = {r['entry']: r['title'] + '\n' + r['body'] for r in read(a.journal)}
    seen = set()
    for i, r in enumerate(rows, 2):
        if None in r or any(r.get(c) is None for c in COLS):
            bad.append(f'第 {i} 列欄數不對')
            continue
        k = r['key']
        if k in seen:
            bad.append(f'{k} 重複')
        seen.add(k)
        if r['category'] not in CATEGORIES:
            bad.append(f'{k} 類別 {r["category"]!r} 不在 {sorted(CATEGORIES)}')
        if r['evidence'] not in EVIDENCE:
            bad.append(f'{k} 證據等級 {r["evidence"]!r} 不在 {sorted(EVIDENCE)}')
        if not r['page'].isdigit() or not 27 <= int(r['page']) <= 57:
            bad.append(f'{k} 頁碼 {r["page"]!r} 不在下冊 27–57')
        text = jour.get(r['entry'])
        if text is None:
            bad.append(f'{k} 第 {r["entry"]} 則不在正式手札')
            continue
        if r['fix'] and r['fix'] not in text:
            bad.append(f'{k} 修正「{r["fix"]}」不在第 {r["entry"]} 則')
        if r['zh056'] and r['zh056'] in text and r['category'] != '漏譯' and '保留他處' not in r['reason']:
            bad.append(f'{k} 原譯「{r["zh056"]}」仍在第 {r["entry"]} 則')
    print(f'錯譯 {len(rows)} 條，手札 {len(jour)} 則')
    if bad:
        print('\n'.join(bad), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
