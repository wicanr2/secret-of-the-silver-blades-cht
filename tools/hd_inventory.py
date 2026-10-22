#!/usr/bin/env python3
"""G9 HD 來源盤點（#10）：解本作 DAX 圖檔，以（寬、高、色號 SHA-256）去重，並找出與克萊恩英豪 HD 主題
基準（`.idx`）逐位元組相同的來源，那些可沿用前作重繪、不必再生圖。在 sosb-tools 容器內以 python3 -I 執行。

輸出 `<out>/inventory.json`（逐來源：尺寸、別名、是否動畫狀態、前作主題鍵）與 stdout 摘要。
動畫以第 0 幀為底、後續幀 XOR 成狀態（克萊恩英豪規格 010 §5.1 的同一規則）。
"""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dax_pics import dax, picture, frames  # noqa: E402

FAMILIES = ('TITLE', 'PIC', 'BIGPIC')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def states(raw):
    try:
        w, h, count, _, _, px = picture(raw)
        if count == 1:
            return w, h, [(0, px[:w * h])]
    except ValueError:
        pass
    fr = frames(raw)
    w, h = fr[0][1:3]
    base = fr[0][-1][:w * h]
    out = [(0, base)]
    for k, f in enumerate(fr[1:], 1):
        out.append((k, bytes(a ^ b for a, b in zip(base, f[-1][:w * h]))))
    return w, h, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--orig', required=True, type=Path)
    ap.add_argument('--prior-theme', type=Path, help='克萊恩英豪 workplace/hd/theme（唯讀）')
    ap.add_argument('--out', required=True, type=Path)
    a = ap.parse_args()
    prior = {}
    if a.prior_theme:
        for p in sorted(a.prior_theme.glob('*.idx')):
            prior.setdefault(sha(p.read_bytes()), []).append(p.stem)
    reg, fails = {}, Counter()
    for path in sorted(a.orig.glob('*.DAX')):
        fam = path.stem.rstrip('0123456789')
        if fam not in FAMILIES:
            continue
        for bid, raw in dax(path.read_bytes()):
            try:
                w, h, sts = states(raw)
            except Exception:  # 非圖片區塊照實記數
                fails[path.name] += 1
                continue
            for k, px in sts:
                key = f'{w}x{h}:{sha(px)}'
                row = reg.setdefault(key, dict(family=fam, width=w, height=h, indexed_sha256=sha(px), aliases=[],
                                               constant=len(set(px)) == 1, prior=prior.get(sha(px), []),
                                               pixels_hex=px.hex()))
                row['aliases'].append(dict(file=path.name, block=bid, frame=k, frames=len(sts)))
    a.out.mkdir(parents=True, exist_ok=True)
    items = sorted(reg.values(), key=lambda r: (r['family'], r['aliases'][0]['file'], r['aliases'][0]['block'],
                                                 r['aliases'][0]['frame']))
    (a.out / 'inventory.json').write_text(json.dumps(dict(items=items, undecoded=fails), ensure_ascii=False, indent=1))
    by = Counter(r['family'] for r in items)
    reuse = Counter(r['family'] for r in items if r['prior'])
    blocks = Counter((r['family'], al['file'], al['block']) for r in items for al in r['aliases'])
    for fam in FAMILIES:
        nb = len({(f, b) for (fm, f, b) in blocks if fm == fam})
        print(f'{fam}：來源區塊 {nb}、去重狀態 {by[fam]}、與前作主題相同 {reuse[fam]}')
    print('無法解為圖片的區塊：', dict(fails))


if __name__ == '__main__':
    main()
