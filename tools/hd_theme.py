#!/usr/bin/env python3
"""G9 HD 主題組裝（#10，本專案規格 010 §3；比照克萊恩英豪 tools/hd_theme.py）。在 sosb-img 容器內以 python3 -I 執行。

只收數值閘門（validation.json）與目視（visual-review.json）都通過、且圖片與請求在驗收後沒有改變的項目。
先全部檢查再寫檔：`<out>/<key>.png`、`<key>.idx`、`theme.json`（dosgolem apps/sosb LoadHDTheme 讀取）。
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from PIL import Image

SCALE = 3


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--req', required=True, type=Path)
    ap.add_argument('--hd', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--batches', required=True)
    a = ap.parse_args()
    items, prepared, seen, skipped = [], [], set(), []
    for batch in a.batches.split(','):
        man_b = (a.req / batch / 'manifest.json').read_bytes()
        man = json.loads(man_b)
        val = json.loads((a.hd / batch / 'validation.json').read_text())
        rev = {r['key']: r for r in json.loads((a.hd / batch / 'visual-review.json').read_text())['items']}
        if val['request_manifest_sha256'] != sha(man_b):
            sys.exit(f'{batch}：請求在數值驗收後改變，須重跑')
        vrows = {r['key']: r for r in val['items']}
        for it in man['items']:
            key = it['key']
            if key in seen:
                sys.exit(f'重複 key：{key}')
            seen.add(key)
            src = a.hd / batch / f'{key}.png'
            v, r = vrows.get(key, {}), rev.get(key, {})
            if not (v.get('target_met') and r.get('approved')) or it.get('position_grade', '').startswith('未知'):
                skipped.append(f'{batch}/{key}')
                continue
            png_sha = sha(src.read_bytes())
            if png_sha != v['png_sha256'] or png_sha != r['png_sha256']:
                sys.exit(f'{key}：驗收後圖片改變，須重跑驗收')
            X, Y, W, H = it['screen_rect']
            if X % 8 or Y % 8 or W % 8 or H % 8:
                sys.exit(f'{key}：矩形 {it["screen_rect"]} 未對齊 8 像素格')
            im = Image.open(src)
            if im.mode != 'RGBA' or im.size != (W * SCALE, H * SCALE) or im.getextrema()[3][0] != 255:
                sys.exit(f'{key}：不是 {W * SCALE}×{H * SCALE} 不透明 RGBA')
            idx = (a.req / batch / it['indexed']).read_bytes()
            if len(idx) != W * H or sha(idx) != it['indexed_sha256']:
                sys.exit(f'{key}：色號基準與請求不符')
            prepared.append((src, key, idx))
            items.append(dict(key=key, batch=batch, screen_rect=[X, Y, W, H], png=f'{key}.png', png_sha256=png_sha,
                              indexed=f'{key}.idx', indexed_sha256=it['indexed_sha256'],
                              runtime_evidence=it['runtime_evidence']))
    a.out.mkdir(parents=True, exist_ok=True)
    for src, key, idx in prepared:
        shutil.copyfile(src, a.out / f'{key}.png')
        (a.out / f'{key}.idx').write_bytes(idx)
    (a.out / 'theme.json').write_text(json.dumps(dict(spec='docs/spec/010-hd-theme.md', issue='#10', scale=SCALE,
                                                      items=items), ensure_ascii=False, indent=2) + '\n')
    print(f'主題 {len(items)} 項；未收 {len(skipped)} 項', ' '.join(skipped))


if __name__ == '__main__':
    main()
