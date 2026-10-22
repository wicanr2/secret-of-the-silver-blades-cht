#!/usr/bin/env python3
"""由原版題目表與英文手札逐字稿算出手冊查驗題答案（docs/re/005）。

題目表在 START.EXE：每筆 5 bytes `[?, 第幾字, 第幾則, 頁, 答案長度]`，以實機答對的
「第 18 則第 4 字第 30 頁長度 6（SILVER）」定位，前後延伸到欄位不合範圍為止，不寫死檔案位置。
字序從標題第一個字算起（docs/re/004：SILVER、YULASH 兩題實機證實）；只含標點的記號（如 —）不算字。
答案取字中的英數字轉大寫，長度要等於表中的答案長度，否則報錯並結束碼非 0。
輸出 TSV：page、entry、word、answer。
"""
import argparse
import csv
import re
import sys
from pathlib import Path

ANCHOR = bytes([4, 18, 30, 6])


def quiz_table(exe):
    d = exe.read_bytes()
    hits = [i - 1 for i in range(len(d) - 4) if d[i:i + 4] == ANCHOR]
    if len(hits) != 1:
        sys.exit(f'題目表錨點命中 {len(hits)} 處')
    ok = lambda o: 0 <= o and 1 <= d[o + 1] <= 30 and 1 <= d[o + 2] <= 72 and 20 <= d[o + 3] <= 60 and 1 <= d[o + 4] <= 20
    s = hits[0]
    while ok(s - 5):
        s -= 5
    recs, o = [], s
    while ok(o):
        recs.append(tuple(d[o:o + 5]))
        o += 5
    return s, recs


def words(title, body):
    text = f'{title} {body}'.replace('\\n', ' ')
    out = []
    for tok in text.split():
        core = re.sub(r'[^A-Za-z0-9]', '', tok)
        if core:
            out.append(core.upper())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--exe', required=True, type=Path)
    ap.add_argument('--journal', required=True, type=Path, help='英文手札 TSV（entry、page、title、body）')
    ap.add_argument('--out', required=True, type=Path)
    a = ap.parse_args()
    with open(a.journal, encoding='utf-8', newline='') as f:
        jour = {int(r['entry']): r for r in csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)}
    start, recs = quiz_table(a.exe)
    rows, bad = [], []
    for _, w, e, page, n in recs:
        r = jour.get(e)
        if r is None:
            bad.append(f'第 {e} 則不在手札表')
            continue
        if int(r['page']) != page and not (int(r['page']) < page <= int(r['page']) + 1):
            bad.append(f'第 {e} 則標題在第 {r["page"]} 頁，表上是第 {page} 頁')
        ws = words(r['title'], r['body'])
        if w > len(ws):
            bad.append(f'第 {e} 則只有 {len(ws)} 字，要第 {w} 字')
            continue
        ans = ws[w - 1]
        if len(ans) != n:
            bad.append(f'第 {e} 則第 {w} 字 {ans} 長度 {len(ans)}，表上 {n}')
        rows.append((page, e, w, ans))
    with open(a.out, 'w', encoding='utf-8', newline='') as f:
        f.write('page\tentry\tword\tanswer\n')
        for r in rows:
            f.write('\t'.join(map(str, r)) + '\n')
    print(f'題目表 START.EXE 0x{start:X}，{len(recs)} 筆；答案 {len(rows)} 筆')
    if bad:
        print('\n'.join(bad), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
