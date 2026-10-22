#!/usr/bin/env python3
"""由 mocagh 英文手札的 OCR 逐字座標組出各則正文草稿（docs/re/005）。

輸入 `pdftotext -bbox-layout` 的 XHTML（手札 PDF 第 16–24 頁，每頁一個跨頁、左右各兩欄）與標題表
（entry、page、title，含 body 為 [MAP] 的地圖則）。每頁依 x 分成四欄、欄內依 y 排序，
遇到 `Journal Entry N` 就開新的一則；接在標題列後、與標題表字數相同的字當標題略過，其餘是正文。
OCR 草稿未校對：查驗題答案以 quiz_answers.py 的長度核對把關，錯譯對照時再對頁面圖校讀。
輸出 TSV：entry、page、title、body、note（body 段落不分，note 標 OCR 草稿）。
"""
import argparse
import csv
import html
import re
import sys
from pathlib import Path

PAGE = re.compile(r'<page width="([\d.]+)"')
LINE = re.compile(r'<line xMin="([\d.]+)" yMin="([\d.]+)"[^>]*>(.*?)</line>', re.S)
WORD = re.compile(r'<word[^>]*>(.*?)</word>')
HEAD = re.compile(r'Journal\s*Entry\s*(\d+)', re.I)


def pages(xhtml):
    for chunk in xhtml.split('<page ')[1:]:
        w = float(PAGE.match('<page ' + chunk).group(1))
        lines = []
        for m in LINE.finditer(chunk):
            x, y = float(m.group(1)), float(m.group(2))
            words = [html.unescape(t) for t in WORD.findall(m.group(3))]
            col = min(3, int(x / (w / 4)))
            lines.append((col, y, words))
        lines.sort(key=lambda t: (t[0], t[1]))
        yield [ws for _, _, ws in lines]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bbox', required=True, type=Path, nargs='+', help='每頁一個 -bbox-layout 檔，依頁序')
    ap.add_argument('--titles', required=True, type=Path, nargs='+')
    ap.add_argument('--out', required=True, type=Path)
    a = ap.parse_args()
    meta = {}
    for p in a.titles:
        with open(p, encoding='utf-8', newline='') as f:
            for r in csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE):
                meta[int(r['entry'])] = r
    got, cur = {}, None
    for path in a.bbox:
        for page in pages(path.read_text(encoding='utf-8')):
            for ws in page:
                text = ' '.join(ws)
                m = HEAD.search(text)
                if m:
                    before, after = text[:m.start()].split(), text[m.end():].split()
                    before = [w for w in before if re.search(r'[A-Za-z]{2}', w)]  # 核取方塊的 OCR 殘字（D、0、O）不算
                    if cur is not None:
                        got[cur].extend(before)
                    cur = int(m.group(1))
                    got.setdefault(cur, []).extend(after)
                    continue
                if cur is not None:
                    got[cur].extend(ws)
    rows, bad = [], []
    for n in range(1, 73):
        r = meta.get(n)
        if r is None or n not in got:
            bad.append(f'第 {n} 則缺{"標題表" if r is None else " OCR"}')
            continue
        ws = got[n]
        if r.get('body', '').strip() == '[MAP]':
            body = '[MAP]'
        else:
            k = len(r['title'].split())
            body = ' '.join(ws[k:])
            body = re.sub(r'(\w)- (\w)', r'\1\2', body)  # 行尾斷字
        rows.append((n, r['page'], r['title'], body, 'OCR 草稿未校對'))
    with open(a.out, 'w', encoding='utf-8', newline='') as f:
        f.write('entry\tpage\ttitle\tbody\tnote\n')
        for row in rows:
            f.write('\t'.join(str(c).replace('\t', ' ') for c in row) + '\n')
    print(f'{len(rows)} 則')
    if bad:
        print('\n'.join(bad), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
