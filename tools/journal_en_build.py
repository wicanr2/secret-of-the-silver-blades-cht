#!/usr/bin/env python3
"""合併英文手札逐字稿成 text/journal.en.tsv（多語系 en 的手札面板，克萊恩英豪規格 015）。在 sosb-tools 容器內以 python3 -I 執行。

輸入 workplace/journal/en/：part-a.tsv（第 1–37 則，對頁面圖轉錄）、part-b.tsv（第 38–72 則的頁碼、標題與地圖註記）、
proof-b.tsv（entry、body：第 38–72 則純文字則的正文，以 OCR 草稿為底逐欄對頁面圖 en-cols/p35–p44 校讀）。
part-* 欄位 entry、page、title、body、note；body 段落以字面 \\n 分隔，地圖則為 [MAP]。

輸出表頭 entry、title、body、source：標題去掉印刷上的句尾句點；地圖則寫一句指向原版手札頁碼的說明；
source 為 `Adventurer's Journal p.N`。1–72 則缺漏、重複、正文空白或含 tab 就失敗。
"""
import argparse
import csv
from pathlib import Path


def rows(p):
    with open(p, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', type=Path, required=True, help='workplace/journal/en')
    ap.add_argument('--out', type=Path, required=True, help='text/journal.en.tsv')
    a = ap.parse_args()
    meta = rows(a.src / 'part-a.tsv') + rows(a.src / 'part-b.tsv')
    proof = {}
    for line in (a.src / 'proof-b.tsv').read_text(encoding='utf-8').splitlines():
        n, body = line.split('\t')
        if n in proof:
            raise SystemExit(f'proof-b.tsv 第 {n} 則重複')
        proof[n] = body
    seen, out = set(), ['entry\ttitle\tbody\tsource']
    for r in meta:
        n = r['entry']
        if n in seen:
            raise SystemExit(f'第 {n} 則重複')
        seen.add(n)
        body = r['body']
        if body == '[MAP]':
            body = f"(This entry is a map. See page {r['page']} of the printed journal.)"
        elif not body:
            body = proof.pop(n, '')
        if not body.strip() or '\t' in body or '\n' in body:
            raise SystemExit(f'第 {n} 則正文空白或含 tab／換行')
        out.append(f"{n}\t{r['title'].rstrip('.').strip()}\t{body}\tAdventurer's Journal p.{r['page']}")
    if seen != {str(i) for i in range(1, 73)} or proof:
        raise SystemExit(f'手札編號不是 1–72（多出 proof：{sorted(proof)}）')
    a.out.write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(f'{len(out) - 1} 則 → {a.out}')


if __name__ == '__main__':
    main()
