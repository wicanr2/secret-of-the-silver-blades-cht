#!/usr/bin/env python3
"""G9 HD 目視閘門（#10，本專案規格 010 §3）：產生批次並列圖，記錄目視結果。在 sosb-img 容器內以 python3 -I 執行。

  sheet  --req <requests/批次> --out <out/批次>：每項一列「原版 3 倍｜HD」，寫 review-sheet-<n>.png（每張最多 6 列）
  record --req … --out … --approve k1,k2 [--reject k3:原因]：寫 visual-review.json，逐項綁定目前 PNG 的 SHA-256；
         --approve all 表示 manifest 全部項目
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=('sheet', 'record'))
    ap.add_argument('--req', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--approve', default='')
    ap.add_argument('--reject', action='append', default=[])
    a = ap.parse_args()
    items = json.loads((a.req / 'manifest.json').read_text())['items']
    if a.cmd == 'sheet':
        rows = []
        for it in items:
            o = Image.open(a.req / it['reference_png']).convert('RGB')
            p = a.out / f'{it["key"]}.png'
            h = Image.open(p).convert('RGB') if p.exists() else Image.new('RGB', o.size, (255, 0, 255))
            s = 900 / (o.width * 2 + 8) if o.width * 2 + 8 > 900 else 1
            row = Image.new('RGB', (o.width * 2 + 8, o.height), (40, 40, 40))
            row.paste(o, (0, 0))
            row.paste(h, (o.width + 8, 0))
            rows.append(row.resize((int(row.width * s), int(row.height * s))))
        for n in range(0, len(rows), 6):
            part = rows[n:n + 6]
            sheet = Image.new('RGB', (max(r.width for r in part), sum(r.height + 6 for r in part)), (20, 20, 20))
            y = 0
            for r in part:
                sheet.paste(r, (0, y))
                y += r.height + 6
            sheet.save(a.out / f'review-sheet-{n // 6}.png')
            print(f'review-sheet-{n // 6}.png', [it['key'] for it in items[n:n + 6]])
        return
    keys = [it['key'] for it in items]
    ok = keys if a.approve == 'all' else [k for k in a.approve.split(',') if k]
    bad = dict(r.split(':', 1) for r in a.reject)
    rows = []
    for k in keys:
        p = a.out / f'{k}.png'
        if k in bad:
            rows.append(dict(key=k, approved=False, reason=bad[k], png_sha256=sha(p) if p.exists() else None))
        elif k in ok and p.exists():
            rows.append(dict(key=k, approved=True, png_sha256=sha(p)))
    (a.out / 'visual-review.json').write_text(json.dumps(dict(reviewer='Claude（逐張目視並列圖）', items=rows),
                                                          ensure_ascii=False, indent=2) + '\n')
    print('核可', sum(r['approved'] for r in rows), '退回', len(bad))


if __name__ == '__main__':
    main()
