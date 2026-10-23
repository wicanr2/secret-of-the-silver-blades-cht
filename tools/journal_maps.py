#!/usr/bin/env python3
"""手札地圖則的圖面（#8，規格 022）。在 sosb-img 容器內以 python3 -I 執行。

從英文手札 PDF 的 300 dpi 頁面圖（`workplace/journal/en-300/p-NN.png`，`pdftoppm -r 300 -f 16 -l 24`）裁出 12 張地圖，
只留深藍墨線（去掉紅色標題與背面透字），抹掉英文標籤與原圖例，再把中文標籤畫回原位、圖例改列在右欄
（圖示由原圖例裁下）。標籤位置與譯文在 `text/journal-maps.zh-TW.tsv`（頁面座標，不含原圖像素）。

高瘦的地圖縮進一頁會小到看不清，依高寬比切成 2–3 段（上下重疊一格），每段一頁。
輸出 `<out>/NN-K.png`（K 從 1 起，通常是 workplace/journal/maps/zh-TW）：912×504（3 倍的 304×168 邏輯點，2 倍時由前端縮小），不進 Git（由原版手札衍生）。
"""
import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 912, 504
PAPER = (250, 246, 234)
INK = (24, 30, 92)
LEGEND_W = 216
MARGIN = 12
OVERLAP = 60  # 切段時上下重疊（300 dpi 像素，約一格）


def ink_mask(rgb):
    a = np.asarray(rgb, dtype=np.int32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = (r * 299 + g * 587 + b * 114) // 1000
    return (lum < 165) & (r - b < 40)  # 深藍墨線；紅色標題與淺灰透字不算


def paint(mask):
    out = np.empty(mask.shape + (3,), np.uint8)
    out[:] = PAPER
    out[mask] = INK
    return Image.fromarray(out)


def trim(mask):
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def text_size(draw, s, font):
    l, t, r, b = draw.textbbox((0, 0), s, font=font)
    return r - l, b - t, l, t


def halo_text(draw, xy, s, font, fill=INK):
    x, y = xy
    for dx in (-2, -1, 0, 1, 2):
        for dy in (-2, -1, 0, 1, 2):
            if dx or dy:
                draw.text((x + dx, y + dy), s, font=font, fill=PAPER)
    draw.text((x, y), s, font=font, fill=fill)


def blocks(flags):
    """連續為真的區段 [(start, end)]。"""
    out, start = [], None
    for i, f in enumerate(list(flags) + [False]):
        if f and start is None:
            start = i
        elif not f and start is not None:
            out.append((start, i))
            start = None
    return out


def despeckle(mask, win=11, keep=12):
    """去掉背面透字留下的孤立小點：win×win 視窗內墨點少於 keep 的點不算線。"""
    p = win // 2
    ii = np.pad(mask.astype(np.int32), ((p + 1, p), (p + 1, p))).cumsum(0).cumsum(1)
    n = ii[win:, win:] - ii[:-win, win:] - ii[win:, :-win] + ii[:-win, :-win]
    return mask & (n >= keep)


def key_icon(mask, keybox, label, others):
    """圖例標籤正上方的圖示：在標籤寬度附近找最高的一段連續墨線列，去掉圖例外框與上一列標籤。"""
    kx0, ky0, kx1, ky1 = keybox
    x0, y0, x1, y1 = label
    cx = (x0 + x1) // 2
    wx0, wx1, wy0, wy1 = max(kx0 + 8, cx - 38), min(kx1 - 8, cx + 38), max(ky0 + 8, y0 - 80), y0 - 2
    for ox0, oy0, ox1, oy1 in others:  # 上方同欄的標籤字
        if oy1 <= y0 and ox1 > wx0 and ox0 < wx1:
            wy0 = max(wy0, oy1 + 2)
    sub = mask[wy0:wy1, wx0:wx1].copy()
    bl = [b for b in blocks(sub.any(axis=1)) if b[1] - b[0] >= 20]
    if not bl:
        return None
    s, e = max(bl, key=lambda b: (b[1] - b[0], b[1]))
    sub[:s], sub[e:] = False, False
    cols = [b for b in blocks(sub.any(axis=0)) if b[1] - b[0] >= 3]
    if not cols:
        return None
    # 取最靠近標籤中心的一段連續欄（相鄰圖示或框線不算）
    mid = cx - wx0
    c0, c1 = min(cols, key=lambda b: abs((b[0] + b[1]) / 2 - mid))
    # 圖示本身可能由數段欄組成（例 牆的雙線）：把間距 6 點以內的相鄰段併進來
    for b in sorted(cols):
        if b[1] >= c0 - 6 and b[0] <= c1 + 6:
            c0, c1 = min(c0, b[0]), max(c1, b[1])
    sub[:, :c0], sub[:, c1:] = False, False
    bb = trim(sub)
    if not bb:
        return None
    bx0, by0, bx1, by1 = bb
    return paint(sub[by0:by1, bx0:bx1])


def render(rows, page_img, font_path):
    crop = next(r for r in rows if r['kind'] == 'crop')
    cx0, cy0, cx1, cy1 = (int(crop[k]) for k in ('x0', 'y0', 'x1', 'y1'))
    mask = despeckle(ink_mask(page_img.crop((cx0, cy0, cx1, cy1)).convert('RGB')))
    rel = lambda r: (int(r['x0']) - cx0, int(r['y0']) - cy0, int(r['x1']) - cx0, int(r['y1']) - cy0)
    keybox = next((rel(r) for r in rows if r['kind'] == 'keybox'), None)
    keys = [rel(r) for r in rows if r['kind'] == 'key']
    icons = [(key_icon(mask, keybox, rel(r), keys), r['label']) for r in rows if r['kind'] == 'key']
    for r in rows:
        if r['kind'] in ('keybox', 'label', 'vlabel'):
            x0, y0, x1, y1 = rel(r)
            pad = 12 if r['kind'] == 'keybox' else 3  # 圖例外框線在量測框外緣
            mask[max(0, y0 - pad):y1 + pad, max(0, x0 - pad):x1 + pad] = False
    bb = trim(mask)
    mx0, my0, mx1, my1 = bb
    mask = mask[my0:my1, mx0:mx1]
    labels = [(r['kind'], r['label'], (int(r['x0']) - cx0 - mx0 + int(r['x1']) - cx0 - mx0) / 2,
               (int(r['y0']) - cy0 - my0 + int(r['y1']) - cy0 - my0) / 2) for r in rows if r['kind'] in ('label', 'vlabel')]
    mw, mh = W - LEGEND_W - 3 * MARGIN, H - 2 * MARGIN
    h, w = mask.shape
    k = 1
    while k < 3 and min(mw / w, mh / ((h + (k - 1) * OVERLAP) / k)) < 0.42 and (h / k) / w > mh / mw:
        k += 1
    seg = math.ceil((h + (k - 1) * OVERLAP) / k)
    pages = []
    for i in range(k):
        top = min(i * (seg - OVERLAP), max(0, h - seg))
        part = mask[top:top + seg]
        s = min(mw / w, mh / part.shape[0])
        size = max(1, round(2 / s)) | 1  # 縮小後線寬約 2 點
        big = Image.fromarray((~part).astype(np.uint8) * 255).filter(ImageFilter.MinFilter(size))
        sw, sh = max(1, round(big.width * s)), max(1, round(big.height * s))
        m = np.asarray(big.resize((sw, sh), Image.LANCZOS)) < 150
        canvas = Image.new('RGB', (W, H), PAPER)
        ox, oy = MARGIN + (mw - sw) // 2, MARGIN + (mh - sh) // 2
        canvas.paste(paint(m), (ox, oy))
        d = ImageDraw.Draw(canvas)
        f_label = ImageFont.truetype(font_path, 22)
        for kind, zh, lx, ly in labels:
            if not top <= ly < top + part.shape[0]:
                continue
            px, py = ox + lx * s, oy + (ly - top) * s
            if kind == 'label':
                tw, th, l, t = text_size(d, zh, f_label)
                tx = min(max(MARGIN, px - tw / 2), W - LEGEND_W - 2 * MARGIN - tw)
                halo_text(d, (tx - l, py - th / 2 - t), zh, f_label)
            else:  # 直書：一字一列
                chars = [c for c in zh if c != ' ']
                step = 24
                top_y = min(max(MARGIN, py - step * len(chars) / 2), H - MARGIN - step * len(chars))
                for j, c in enumerate(chars):
                    tw, th, l, t = text_size(d, c, f_label)
                    halo_text(d, (px - tw / 2 - l, top_y + j * step - t), c, f_label)
        legend(d, canvas, icons, font_path, '')  # 頁碼由手札面板畫（規格 022 §4）
        pages.append(canvas)
    return pages


def legend(d, canvas, icons, font_path, part):
    lx = W - LEGEND_W - MARGIN
    d.rectangle([lx, MARGIN, W - MARGIN, H - MARGIN], outline=INK, width=3)
    f_head = ImageFont.truetype(font_path, 26)
    f_label = ImageFont.truetype(font_path, 22)
    tw, th, l, t = text_size(d, '圖例', f_head)
    d.text((lx + (LEGEND_W - tw) / 2 - l, MARGIN + 10 - t), '圖例', font=f_head, fill=INK)
    y = MARGIN + 10 + th + 14
    bottom = H - MARGIN - 8 - (34 if part else 0)
    row_h = min(58, (bottom - y) // max(1, len(icons)))
    for icon, zh in icons:
        if icon is not None:
            k = min((row_h - 8) / icon.height, 48 / icon.width)
            ic = icon.resize((max(1, round(icon.width * k)), max(1, round(icon.height * k))), Image.LANCZOS)
            canvas.paste(ic, (lx + 14 + (48 - ic.width) // 2, y + (row_h - ic.height) // 2))
        tw, th, l, t = text_size(d, zh, f_label)
        d.text((lx + 74 - l, y + (row_h - th) / 2 - t), zh, font=f_label, fill=INK)
        y += row_h
    if part:
        tw, th, l, t = text_size(d, part, f_label)
        d.text((lx + (LEGEND_W - tw) / 2 - l, H - MARGIN - 10 - th - t), part, font=f_label, fill=INK)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--spec', required=True, type=Path, help='text/journal-maps.zh-TW.tsv')
    ap.add_argument('--pages', required=True, type=Path, help='workplace/journal/en-300（唯讀）')
    ap.add_argument('--font', required=True, type=Path, help='GenSenRounded2TW-M.otf')
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--only', type=int, nargs='*')
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    with open(a.spec, encoding='utf-8', newline='') as f:
        spec = list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
    by = defaultdict(list)
    for r in spec:
        by[int(r['entry'])].append(r)
    pages = {}
    for n, rows in sorted(by.items()):
        if a.only and n not in a.only:
            continue
        p = int(next(r for r in rows if r['kind'] == 'crop')['page'])
        if p not in pages:
            pages[p] = Image.open(a.pages / f'p-{p}.png')
        for old in a.out.glob(f'{n:02d}-*.png'):
            old.unlink()
        out = render(rows, pages[p], str(a.font))
        for i, im in enumerate(out, 1):
            im.save(a.out / f'{n:02d}-{i}.png')
        print(n, len(out), '頁')


if __name__ == '__main__':
    main()
