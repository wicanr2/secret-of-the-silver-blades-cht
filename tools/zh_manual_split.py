#!/usr/bin/env python3
"""把珍056 每張 PDF 頁（300 dpi 灰階，pdftoppm -r 300 -gray）切成手冊頁（G4，docs/re/006）。在 sosb-img 容器內以 python -I 執行。

PDF 頁多為 3 列 × 2 欄拼版。切線以均分線（寬度 1/2、高度 1/3 與 2/3）為準，在前後 80 像素內找墨點最少的空白帶中心
（15 像素寬的滑動和）；範圍放寬會抓到頁內留白（安裝說明頁），把上一頁的頁碼切進來。每格存 pNNrRcC.png。拼版不同的頁（跨欄的表、整頁地圖）照同一切法，
只當 OCR 的輸入，不代表頁界。
"""
import argparse
from pathlib import Path

from PIL import Image


def profile(im, axis):
    """axis 0：每一欄的墨點數；axis 1：每一列的墨點數（亮度 < 128 算墨點）。"""
    w, h = im.size
    px = im.point(lambda v: 1 if v < 128 else 0).load()
    if axis == 0:
        return [sum(px[x, y] for y in range(0, h, 2)) for x in range(w)]
    return [sum(px[x, y] for x in range(0, w, 2)) for y in range(h)]


def quietest(p, lo, hi, win=15):
    best, at = None, lo
    s = sum(p[lo:lo + win])
    for i in range(lo, hi - win):
        if best is None or s < best:
            best, at = s, i + win // 2
        s += p[i + win] - p[i]
    return at


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pages', nargs='+', type=Path)
    ap.add_argument('--out', required=True, type=Path)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    for path in a.pages:
        n = int(path.stem.split('-')[-1])
        im = Image.open(path).convert('L')
        w, h = im.size
        small = im.resize((w // 2, h // 2))
        d = 40  # 半尺寸下的 ±80 像素
        cx = 2 * quietest(profile(small, 0), w // 4 - d, w // 4 + d)
        rows = profile(small, 1)
        y1, y2 = 2 * quietest(rows, h // 6 - d, h // 6 + d), 2 * quietest(rows, h // 3 - d, h // 3 + d)
        for r, (t, b) in enumerate([(0, y1), (y1, y2), (y2, h)]):
            for c, (l, rt) in enumerate([(0, cx), (cx, w)]):
                im.crop((l, t, rt, b)).save(a.out / f'p{n:02d}r{r}c{c}.png')
        print(f'p{n:02d}：直切 {cx}，橫切 {y1}、{y2}（{w}×{h}）')


if __name__ == '__main__':
    main()
