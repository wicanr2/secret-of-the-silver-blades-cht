#!/usr/bin/env python3
"""日文、韓文翻譯批次（#11，克萊恩英豪規格 015 §5）。在 sosb-tools 容器內以 python3 -I 執行。

只收繁中已有譯文、而克萊恩英豪的 <表>.ja.tsv 沒有同 key 的列（同 key 表示原文雜湊相同，直接沿用前作譯文）。
ECL 依 key 排序（同一區塊的片段依位移接續），附前後一則原文（prev、next）與繁中定案譯文（zh）供接句；介面字串接在 ECL 之後。
輸出 <out>/batches/bNN.tsv（key、original、prev、next、zh），每批約 --size 列；含原文，只放工作區。
"""
import argparse
import csv
from pathlib import Path


def read(p):
    with open(p, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--prior', type=Path, required=True, help='克萊恩英豪 text/（唯讀）')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--size', type=int, default=126)
    a = ap.parse_args()
    reused = {r['key'] for t in ('ecl-text', 'ui-text') for r in read(a.prior / f'{t}.ja.tsv')}
    rows = []
    for t in ('ecl-text', 'ui-text'):
        src = {r['key']: r['original'] for r in read(a.root / 'workplace/text-src' / f'{t}-source.tsv')}
        zh = {r['key']: r['translation'] for r in read(a.root / 'text' / f'{t}.zh-TW.tsv')}
        keys = sorted(k for k in zh if k not in reused)
        order = sorted(src)
        pos = {k: i for i, k in enumerate(order)}
        for k in keys:
            i = pos[k]
            prev = src[order[i - 1]] if t == 'ecl-text' and i > 0 and order[i - 1].rsplit('.', 1)[0] == k.rsplit('.', 1)[0] else ''
            nxt = src[order[i + 1]] if t == 'ecl-text' and i + 1 < len(order) and order[i + 1].rsplit('.', 1)[0] == k.rsplit('.', 1)[0] else ''
            rows.append([k, src[k], prev, nxt, zh[k]])
    d = a.out / 'batches'
    d.mkdir(parents=True, exist_ok=True)
    n = 0
    for i in range(0, len(rows), a.size):
        n += 1
        with open(d / f'b{n:02d}.tsv', 'w', encoding='utf-8', newline='') as f:
            f.write('key\toriginal\tprev\tnext\tzh\n')
            for r in rows[i:i + a.size]:
                assert not any('\t' in c or '\n' in c for c in r), r[0]
                f.write('\t'.join(r) + '\n')
    print(f'{len(rows)} 列（沿用前作 {len(reused)} key 不收），{n} 批')


if __name__ == '__main__':
    main()
