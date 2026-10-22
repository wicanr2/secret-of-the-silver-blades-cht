#!/usr/bin/env python3
"""G9 HD 前處理（#10，本專案規格 010）：Codex 生成的原圖整幅縮放到目標尺寸、轉不透明 RGBA；
動畫非第 0 幀只取原版 XOR 遮罩外擴 6 個輸出像素的範圍，其餘沿用第 0 幀（克萊恩英豪規格 010 §5.2 同規則）。
不裁切、不自動對位；raw 不覆寫。在 sosb-img 容器內以 python3 -I 執行。

用法：hd_prepare.py --req <requests/批次> --out <out/批次>；每個 key 取 jobs/ 裡最後一個 status=generated 的 raw。
前作沿用：item 有 prior_theme_keys 且 --prior 目錄有同名 PNG 時直接複製，記在 reuse.json。
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image, ImageFilter


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--req', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--prior', type=Path, help='克萊恩英豪 workplace/hd/theme（唯讀）')
    a = ap.parse_args()
    man = json.loads((a.req / 'manifest.json').read_text())
    jobs = {}
    for j in sorted((a.out / 'jobs').glob('*.json')) if (a.out / 'jobs').exists() else []:
        d = json.loads(j.read_text())
        if d.get('status') == 'generated' and (a.out / d['raw']).exists():
            jobs[d['key']] = d  # 檔名排序，後面的版本（r1、r2…）取代前面的
    reuse, rows = [], []
    for it in sorted(man['items'], key=lambda it: bool(it.get('animation'))):
        key, dst = it['key'], a.out / f'{it["key"]}.png'
        prior = [k for k in it.get('prior_theme_keys', []) if a.prior and (a.prior / f'{k}.png').exists()]
        if prior:
            shutil.copyfile(a.prior / f'{prior[0]}.png', dst)
            reuse.append(dict(key=key, prior_key=prior[0], png_sha256=sha(dst.read_bytes())))
        elif key in jobs:
            im = Image.open(a.out / jobs[key]['raw']).convert('RGBA').resize(tuple(it['target_size']),
                                                                            Image.Resampling.LANCZOS)
            im.putalpha(255)
            anim = it.get('animation')
            if anim:
                base = a.out / f'{anim["base"]}.png'
                if not base.exists():
                    rows.append(dict(key=key, status='missing-base'))
                    continue
                mask = Image.open(a.req / anim['mask']).convert('L').filter(ImageFilter.MaxFilter(13))
                im = Image.composite(im, Image.open(base).convert('RGBA'), mask)
            im.save(dst)
        rows.append(dict(key=key, status='candidate' if dst.exists() else 'missing',
                         png_sha256=sha(dst.read_bytes()) if dst.exists() else None,
                         source='prior' if prior else ('generated:' + jobs[key]['raw'] if key in jobs else None)))
        print(key, rows[-1]['status'], rows[-1]['source'])
    (a.out / 'reuse.json').write_text(json.dumps(reuse, ensure_ascii=False, indent=2) + '\n')
    (a.out / 'manifest.json').write_text(json.dumps(dict(
        batch=man['batch'], issue=man['issue'], spec=man['spec'], scale=3, style='B',
        request_sha256=sha((a.req / 'manifest.json').read_bytes()), processing='tools/hd_prepare.py',
        rights_note='Codex 內建 image_gen 生成，依專案定案可放入原版＋HD patch；前作沿用見 reuse.json。',
        items=rows), ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
