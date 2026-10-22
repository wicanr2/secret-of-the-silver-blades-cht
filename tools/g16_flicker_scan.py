#!/usr/bin/env python3
"""#16 閃爍掃描：逐格截圖目錄中，列出「連續兩格同一區域都在變」的畫格（docs/re/010）。在 sosb-img 容器內執行。"""
import os, sys
from PIL import Image, ImageChops
d = sys.argv[1]
fs = sorted(os.listdir(d))
prev = prevbox = None
hits = []
for f in fs:
    im = Image.open(os.path.join(d, f)).convert('RGB')
    box = ImageChops.difference(im, prev).getbbox() if prev is not None else None
    if box and prevbox:
        ix = (max(box[0], prevbox[0]), max(box[1], prevbox[1]), min(box[2], prevbox[2]), min(box[3], prevbox[3]))
        if ix[0] < ix[2] and ix[1] < ix[3]:
            hits.append((f, box, prevbox))
    prev, prevbox = im, box
for h in hits:
    print(*h)
print(len(fs), 'frames', len(hits), 'consecutive-change hits')
