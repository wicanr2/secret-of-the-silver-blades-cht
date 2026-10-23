#!/usr/bin/env python3
"""G9 HD 執行期證據（#10，規格 010）：在錄好的 3 倍畫格裡找主題項目（TITLE、BIGPIC、PIC）出現的畫格。
在 sosb-img 容器內以 python3 -I 執行。

    python3 -I tools/hd_observe.py --theme hd/theme --seg <畫格目錄> [--seg …] --out observed.json

畫格是 cmd/sosb-promo 輸出的 3 倍合成畫面（960×600 PNG）。每格對每個項目的 screen_rect（放大 3 倍）比兩種：
- hd：該區塊逐像素等於主題的 HD 圖，表示執行期以色號吻合換上了 HD；
- orig：該區塊逐像素等於原版色號（.idx，EGA 預設 16 色）最近鄰放大 3 倍，等同 tools/hd_request.py 的 --evidence。
輸出 {key: ["<段>:<畫格>:<hd|orig>", …]}（每項最多記 3 格）；hd_theme.py、hd_review_md.py 以 --observed 讀入。
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dax_pics import EGA  # noqa: E402

S = 3


def digest(b):
    return hashlib.sha256(b).digest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--theme', required=True, type=Path)
    ap.add_argument('--seg', action='append', required=True, type=Path, help='畫格目錄，可重複')
    ap.add_argument('--out', required=True, type=Path)
    a = ap.parse_args()
    items = json.loads((a.theme / 'theme.json').read_text())['items']
    want = {'hd': {}, 'orig': {}}  # 模式 → 矩形 → {雜湊: [key]}
    for it in items:
        x, y, w, h = it['screen_rect']
        rect = (x * S, y * S, (x + w) * S, (y + h) * S)
        hd = Image.open(a.theme / it['png']).convert('RGB')
        want['hd'].setdefault(rect, {}).setdefault(digest(hd.tobytes()), []).append(it['key'])
        idx = (a.theme / it['indexed']).read_bytes()
        rgb = bytearray()
        for j in range(h):
            row = b''.join(bytes(EGA[p]) * S for p in idx[j * w:(j + 1) * w])
            rgb += row * S
        want['orig'].setdefault(rect, {}).setdefault(digest(bytes(rgb)), []).append(it['key'])
    seen = {}
    for d in a.seg:
        frames = sorted(d.glob('*.png'))
        if not frames:
            sys.exit(f'{d} 沒有畫格')
        name = d.parent.name if d.name == 'frames' else d.name
        for f in frames:
            im = Image.open(f).convert('RGB')
            if im.size != (320 * S, 200 * S):
                sys.exit(f'{f}：不是 3 倍畫面 {im.size}')
            crops = {}
            for mode, rects in want.items():
                for rect, table in rects.items():
                    if rect not in crops:
                        crops[rect] = digest(im.crop(rect).tobytes())
                    for key in table.get(crops[rect], []):
                        ev = seen.setdefault(key, [])
                        if len(ev) < 3:
                            ev.append(f'{name}:{f.stem}:{mode}')
        print(f'{name}：{len(frames)} 格，累計 {len(seen)} 項')
    a.out.write_text(json.dumps(dict(sorted(seen.items())), ensure_ascii=False, indent=1) + '\n')
    print(f'{len(seen)}／{len(items)} 項有執行期證據 → {a.out}')


if __name__ == '__main__':
    main()
