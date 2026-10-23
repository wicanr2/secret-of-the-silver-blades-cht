#!/usr/bin/env python3
"""由珍056 手冊頁的 PaddleOCR 結果組出逐頁轉錄草稿（G4，docs/re/006）。在 sosb-tools 容器內以 python3 -I 執行。

輸入 tools/ocr_batch.py 的逐格 JSON（tools/zh_manual_split.py 切的 pNNrRcC.png），每格取 rec_texts 與 rec_boxes：
文字框依中線 y 分行（中線差小於框高一半算同一行），行內依 x 排序、以一個空白相接。
頁碼取格子下緣 12% 內、只含 1–3 位數字的框；頁首書名圖字與「（上冊）」「（下冊）」照樣保留，校讀時再刪。
輸出 TSV：cell、page（抓不到頁碼留空）、text（行以字面 \\n 相接）、status（固定「OCR 草稿未校對」）。
"""
import argparse
import json
import re
from pathlib import Path


def lines(res):
    boxes = [(b[1], b[3], b[0], t.strip()) for t, b in zip(res['rec_texts'], res['rec_boxes']) if t.strip()]
    boxes.sort(key=lambda b: ((b[0] + b[1]) / 2, b[2]))
    rows, cur, mid = [], [], None
    for y0, y1, x0, t in boxes:
        m, half = (y0 + y1) / 2, (y1 - y0) / 2
        if cur and abs(m - mid) > half:
            rows.append(cur)
            cur = []
        cur.append((x0, t, y0, y1))
        mid = m if len(cur) == 1 else mid
    if cur:
        rows.append(cur)
    return [sorted(r) for r in rows]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ocr', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    a = ap.parse_args()
    out = ['cell\tpage\ttext\tstatus']
    for p in sorted(a.ocr.glob('p*.png.json')):
        res = json.loads(p.read_text(encoding='utf-8'))['result']
        h = max((b[3] for b in res['rec_boxes']), default=0)
        page, text = '', []
        for row in lines(res):
            words = [t for _, t, _, _ in row]
            if len(row) == 1 and re.fullmatch(r'\d{1,3}', words[0]) and row[0][2] > h * .88:
                page = words[0]
                continue
            text.append(' '.join(words).replace('\t', ' '))
        body = '\\n'.join(text)  # Python 3.11 的 f-string 運算式不能含反斜線
        out.append(f"{p.name.split('.')[0]}\t{page}\t{body}\tOCR 草稿未校對")
    a.out.write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(f'{len(out) - 1} 格 → {a.out}')


if __name__ == '__main__':
    main()
