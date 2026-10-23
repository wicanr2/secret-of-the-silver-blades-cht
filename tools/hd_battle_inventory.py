#!/usr/bin/env python3
"""G9 HD 第二階段來源盤點（#10，本專案規格 010 §6；規則沿用克萊恩英豪 tools/hd_battle_inventory.py 與其規格 010 §6）。
在 sosb-img 容器內以 python3 -I 執行。

解本作戰鬥地形、CPIC、頭身、COMSPR、SPRIT 的 DAX，以（家族、尺寸、色號 SHA-256）去重；人物家族的來源色號 0 與 8 互換
（克萊恩英豪規格 010 §6.2，前景以色號 8 以外判斷）。再找克萊恩英豪各批請求中尺寸與基準色號逐位元組相同、已有成品的項目，
列為可沿用候選（本作仍要重新驗收）。DAX 目錄可重複 block ID，保留目錄序號與檔案 offset。

輸出 `<out>/inventory.json` 與 `<out>/<key>.idx`；stdout 印各家族數量與可沿用數。
"""
import argparse
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dax_pics import dax, frames, picture  # noqa: E402

FILES = ('DUNGCOM', 'CPIC1', 'CHEAD', 'CBODY', 'COMSPR', 'SPRIT1')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def kind(n):
    if n == 'DUNGCOM':
        return 'terrain'
    if n.startswith('CPIC'):
        return 'actor'
    return {'CHEAD': 'head', 'CBODY': 'body', 'COMSPR': 'effect'}.get(n, 'encounter' if n.startswith('SPRIT') else 'other')


def records(path):
    data = path.read_bytes()
    header = struct.unpack_from('<H', data)[0] + 2
    blocks = dax(data)
    assert (header - 2) % 9 == 0 and len(blocks) == (header - 2) // 9
    for n, (bid, raw) in enumerate(blocks):
        entry = 2 + n * 9
        check, offset, decoded, packed = struct.unpack_from('<BIHH', data, entry)
        assert bid == check and len(raw) == decoded
        yield bid, raw, dict(file=path.name, block=bid, record_index=n, entry_offset=entry, offset=header + offset,
                             decoded_sha256=sha(raw))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--orig', required=True, type=Path)
    ap.add_argument('--prior', required=True, type=Path, help='克萊恩英豪 workplace/hd（唯讀）')
    ap.add_argument('--out', required=True, type=Path)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    reg = {}
    for name in FILES:
        for bid, raw, src in records(a.orig / f'{name}.DAX'):
            try:
                pics = [picture(raw)]
            except ValueError:
                pics = [f[1:] for f in frames(raw)]
            for frame, (w, h, count, x, y, px) in enumerate(pics):
                for item in range(count):
                    rawpx = px[item * w * h:(item + 1) * w * h]
                    k = kind(name)
                    mapped = bytes(8 if c == 0 else 0 if c == 8 else c for c in rawpx) \
                        if k in ('actor', 'head', 'body', 'effect') else bytes(rawpx)
                    row = reg.setdefault((k, w, h, sha(mapped)), dict(
                        key=f'{name.lower()}-{bid:03d}-{frame:02d}-{item:02d}', kind=k, size=[w, h],
                        indexed=f'{name.lower()}-{bid:03d}-{frame:02d}-{item:02d}.idx', indexed_sha256=sha(mapped),
                        colors=dict(Counter(mapped)), aliases=[]))
                    row['aliases'].append(dict(src, frame=frame, item=item, header_xy=[x, y]))
                    p = a.out / row['indexed']
                    if not p.exists():
                        p.write_bytes(mapped)
    prior = {}
    for man in sorted((a.prior / 'requests').glob('b*/manifest.json')):
        for it in json.loads(man.read_text()).get('items', []):
            idx, png = man.parent / it.get('indexed', '-'), a.prior / 'out' / man.parent.name / f'{it["key"]}.png'
            if 'size' in it and idx.is_file() and png.is_file():
                prior.setdefault((tuple(it['size']), sha(idx.read_bytes())),
                                 dict(batch=man.parent.name, key=it['key'], png_sha256=sha(png.read_bytes())))
    rows = sorted(reg.values(), key=lambda r: r['key'])
    for r in rows:
        r['reuse_candidate'] = prior.get((tuple(r['size']), r['indexed_sha256']))
    (a.out / 'inventory.json').write_text(json.dumps(dict(spec='docs/spec/010-hd-theme.md §6', items=rows),
                                                     ensure_ascii=False, indent=1) + '\n')
    for k in ('terrain', 'actor', 'head', 'body', 'effect', 'encounter'):
        part = [r for r in rows if r['kind'] == k]
        sizes = Counter(tuple(r['size']) for r in part)
        print(f'{k}：去重 {len(part)}、可沿用 {sum(bool(r["reuse_candidate"]) for r in part)}、尺寸 {dict(sizes)}')


if __name__ == '__main__':
    main()
