"""並列印出英文手札與珍056 手札（錯譯對照用）：journal_pair.py <英文 TSV> <珍056 TSV…> <起> <迄>"""
import csv
import sys


def rd(paths):
    out = {}
    for p in paths:
        with open(p, encoding='utf-8', newline='') as f:
            for r in csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE):
                out[int(r['entry'])] = r
    return out


en = rd([sys.argv[1]])
zh = rd(sys.argv[2:-2])
lo, hi = int(sys.argv[-2]), int(sys.argv[-1])
for n in range(lo, hi + 1):
    e, z = en.get(n, {}), zh.get(n, {})
    print(f"## {n} p{e.get('page')}/{z.get('page')} EN[{e.get('title')}] {e.get('body')}")
    print(f"   ZH[{z.get('title')}] {z.get('body')}")
