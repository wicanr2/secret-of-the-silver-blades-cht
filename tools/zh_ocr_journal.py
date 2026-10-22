#!/usr/bin/env python3
"""由珍056 手札頁的 PaddleOCR 結果組出各則草稿（docs/re/006）。

輸入 tools/ocr_batch.py 的逐頁 JSON（依頁序給），每頁取 rec_texts 與 rec_boxes：
頁首（書名圖字、「（下冊）」）與頁尾（頁碼、裝飾）依 y 位置略過；「旅行手札 N」開新的一則，
接著那一行若不是以「開頭、且不是縮排起段，當小標；縮排（x 明顯大於左緣）起新段落，段落以兩個字元 \\n 相接。
OCR 草稿未校對，常見錯字（黑圖／黑圈、學生／孿生）要對頁面圖校讀。
輸出 TSV：entry、page、title、body、note。
"""
import argparse
import json
import re
import sys
from pathlib import Path

HEAD = re.compile(r'^旅行手[札扎礼]\s*(\d+)$')


def lines(path):
    d = json.loads(path.read_text(encoding='utf-8'))['result']
    h = max(b[3] for b in d['rec_boxes']) if d['rec_boxes'] else 0
    out = []
    for t, (x0, y0, x1, y1) in zip(d['rec_texts'], d['rec_boxes']):
        if y0 < 120 or y0 > h - 40 or re.fullmatch(r'[\d\sA-Z]*', t):
            continue
        out.append((y0, x0, t.strip()))
    out.sort()
    left = min((x for _, x, _ in out), default=0)
    return [(x - left, t) for _, x, t in out]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pages', required=True, nargs='+', help='頁碼=JSON 路徑，依頁序')
    ap.add_argument('--out', required=True, type=Path)
    a = ap.parse_args()
    ents, cur = {}, None
    for spec in a.pages:
        page, path = spec.split('=', 1)
        for dx, t in lines(Path(path)):
            m = HEAD.match(t.replace(' ', ''))
            if m:
                cur = int(m.group(1))
                ents[cur] = {'page': page, 'title': None, 'paras': []}
                continue
            if cur is None:
                continue
            e = ents[cur]
            if e['title'] is None and not e['paras']:
                if not t.startswith('「') and dx < 20:
                    e['title'] = t
                    continue
                e['title'] = ''
            if dx >= 20 or not e['paras']:
                e['paras'].append(t)
            else:
                e['paras'][-1] += t
    with open(a.out, 'w', encoding='utf-8', newline='') as f:
        f.write('entry\tpage\ttitle\tbody\tnote\n')
        for n in sorted(ents):
            e = ents[n]
            body = '\\n'.join(e['paras'])
            f.write(f"{n}\t{e['page']}\t{e['title'] or ''}\t{body}\tOCR 草稿未校對\n")
    print(f'{len(ents)} 則：{min(ents)}–{max(ents)}', file=sys.stderr)


if __name__ == '__main__':
    main()
