#!/usr/bin/env python3
"""G9 HD 重繪請求（#10，本專案規格 010）：從 tools/hd_inventory.py 的盤點取來源，產生一批請求。
在 sosb-tools 容器內以 python3 -I 執行。

每項輸出到 `<out>/<批次>/`：
- `<key>.png`：原版 1 倍（EGA 16 色）；`<key>-x3.png`：最近鄰 3 倍，生圖的構圖參考
- `<key>.idx`：原版色號（逐列每像素 1 byte），驗收與接入比對用
- 動畫非第 0 幀另有 `<key>-mask-x3.png`（與第 0 幀不同的像素，白）
- `manifest.json`：來源、畫面位置、證據、提示詞、前作可沿用的主題鍵

畫面位置依家族契約（克萊恩英豪規格 010 §5.1，本作以截圖驗證）：PIC (24,24) 88×88、BIGPIC (8,8) 304×120、
TITLE 全幅 (0,0)。`--evidence 名稱=PNG`（1 倍或整數倍的原版畫面）在對應位置逐色號吻合的來源標為 observed。
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dax_pics import EGA, png  # noqa: E402

PLACE = {'PIC': (24, 24), 'BIGPIC': (8, 8), 'TITLE': (0, 0)}
PROMPT = ('Edit image 1, an original Secret of the Silver Blades (1990 Gold Box) EGA game picture, into a production '
          'HD game bitmap. Trace the original structural contours and EXACT placement, proportions, pose, camera and '
          'full canvas crop. Preserve every object, silhouette, clothing, architecture and foreground/background '
          'boundary. Match the original spatial EGA colors, including black negative space. Replace dithering with '
          'painted shading without changing the underlying shapes. Style B: richly detailed classic fantasy '
          'hand-painted illustration, crisp outlines, vivid colors; image 2 shows the brushwork only, do not import '
          'any object or color from it. No new people, props, border, labels, text or decorations. No recentering or '
          'perspective change. Fully opaque, original aspect ratio {w}:{h}, intended final {W}x{H}.')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def rgb_png(path, idx, w, h, s, pal=EGA):
    big = bytearray()
    for yy in range(h * s):
        row = idx[(yy // s) * w:(yy // s + 1) * w]
        for xx in range(w * s):
            big += bytes(pal[row[xx // s]])
    png(path, w * s, h * s, big)


def screen_indexed(path):
    """把原版畫面 PNG（320×200 的整數倍、只含 EGA 16 色）還原成 320×200 色號。"""
    from PIL import Image
    im = Image.open(path).convert('RGB')
    s = im.width // 320
    if im.width != 320 * s or im.height != 200 * s:
        sys.exit(f'{path}：不是 320×200 的整數倍')
    im = im.resize((320, 200), Image.NEAREST)
    lut = {c: i for i, c in enumerate(EGA)}
    try:
        return bytes(lut[c] for c in im.getdata())
    except KeyError as e:
        sys.exit(f'{path}：含非 EGA 顏色 {e}')


def region(scr, x, y, w, h):
    return bytes(scr[(y + j) * 320 + x + i] for j in range(h) for i in range(w))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--orig', required=True, type=Path)
    ap.add_argument('--inventory', required=True, type=Path)
    ap.add_argument('--batch', required=True)
    ap.add_argument('--select', default='', help='逗號分隔的「檔名:區塊」，例 PIC1.DAX:3；動畫的全部幀一起出')
    ap.add_argument('--composite', action='append', default=[],
                    help='組圖：鍵=證據名=檔名:區塊@x,y+檔名:區塊@x,y（後者蓋前者），組好須與證據畫面全幅逐色號相同')
    ap.add_argument('--evidence', action='append', default=[], help='名稱=畫面 PNG')
    ap.add_argument('--style-ref', required=True, help='風格參考圖（只取筆觸）')
    ap.add_argument('--out', required=True, type=Path)
    a = ap.parse_args()
    inv = json.loads(a.inventory.read_text())['items']
    screens = {n: screen_indexed(p) for n, p in (e.split('=', 1) for e in a.evidence)}
    want = [s.split(':') for s in a.select.split(',') if s]
    out = a.out / a.batch
    if out.exists():
        sys.exit(f'{out} 已存在；不覆寫請求')
    out.mkdir(parents=True)
    items = []
    for fname, bid in want:
        rows = [r for r in inv if any(al['file'] == fname and al['block'] == int(bid) for al in r['aliases'])]
        if not rows:
            sys.exit(f'{fname}:{bid} 不在盤點')
        base_px = None
        for r in sorted(rows, key=lambda r: next(al['frame'] for al in r['aliases'] if al['file'] == fname)):
            al = next(al for al in r['aliases'] if al['file'] == fname and al['block'] == int(bid))
            w, h, k, n = r['width'], r['height'], al['frame'], al['frames']
            px = bytes.fromhex(r['pixels_hex'])
            stem = f'{Path(fname).stem.lower()}-{int(bid):03d}'
            key = f'{stem}@{k}' if n > 1 else stem
            x, y = PLACE[r['family']]
            if r['family'] == 'TITLE':
                x, y = (320 - w) // 2 if w < 320 else 0, 0 if h == 200 else 8
            seen = [name for name, scr in screens.items() if region(scr, x, y, w, h) == px]
            (out / f'{key}.idx').write_bytes(px)
            rgb_png(out / f'{key}.png', px, w, h, 1)
            rgb_png(out / f'{key}-x3.png', px, w, h, 3)
            it = dict(key=key, family=r['family'], description=f'{fname} 區塊 {bid} 幀 {k}/{n}',
                      screen_rect=[x, y, w, h], size=[w, h], target_size=[w * 3, h * 3],
                      png=f'{key}.png', reference_png=f'{key}-x3.png', indexed=f'{key}.idx', indexed_sha256=sha(px),
                      aliases=r['aliases'], prior_theme_keys=r['prior'],
                      runtime_evidence='observed' if seen else 'unobserved', evidence_screens=seen,
                      position_grade='已證實' if seen else '家族契約，未觀測',
                      prompt=PROMPT.format(w=w, h=h, W=w * 3, H=h * 3))
            if r['family'] == 'TITLE' and not seen:
                it['position_grade'] = '未知，接入前要有畫面證據'
            if n > 1 and k == 0:
                base_px = px
            if n > 1 and k:
                mask = bytes(int(p != q) for p, q in zip(px, base_px))
                rgb_png(out / f'{key}-mask-x3.png', mask, w, h, 3, [(0, 0, 0), (255, 255, 255)])
                it['animation'] = dict(rule='第 0 幀 XOR 原始幀', frame=k, base=f'{stem}@0', mask=f'{key}-mask-x3.png')
            items.append(it)
            print(key, it['runtime_evidence'], ','.join(seen), '前作:' + ','.join(r['prior']) if r['prior'] else '')
    for spec in a.composite:
        key, ev, parts = spec.split('=', 2)
        canvas, sources = bytearray(320 * 200), []
        for part in parts.split('+'):
            src, at = part.split('@')
            fname, bid = src.split(':')
            x, y = map(int, at.split(','))
            r = next(r for r in inv if any(al['file'] == fname and al['block'] == int(bid) for al in r['aliases']))
            w, h, px = r['width'], r['height'], bytes.fromhex(r['pixels_hex'])
            for j in range(h):
                canvas[(y + j) * 320 + x:(y + j) * 320 + x + w] = px[j * w:(j + 1) * w]
            sources.append(dict(file=fname, block=int(bid), placed_at=[x, y], block_size=[w, h]))
        if bytes(canvas) != screens[ev]:
            sys.exit(f'{key}：組圖與證據畫面 {ev} 不同')
        px = bytes(canvas)
        (out / f'{key}.idx').write_bytes(px)
        rgb_png(out / f'{key}.png', px, 320, 200, 1)
        rgb_png(out / f'{key}-x3.png', px, 320, 200, 3)
        items.append(dict(key=key, family='TITLE', description='組圖：' + parts, screen_rect=[0, 0, 320, 200],
                          size=[320, 200], target_size=[960, 600], png=f'{key}.png', reference_png=f'{key}-x3.png',
                          indexed=f'{key}.idx', indexed_sha256=sha(px), sources=sources, prior_theme_keys=[],
                          runtime_evidence='observed', evidence_screens=[ev], position_grade='已證實',
                          prompt=PROMPT.format(w=320, h=200, W=960, H=600) +
                          ' Keep the title lettering shapes, spelling and placement exactly; do not restyle the letters.'))
        print(key, 'observed', ev)
    man = dict(batch=a.batch, issue='#10', spec='docs/spec/010-hd-theme.md', scale=3, style='B',
               style_reference=a.style_ref, palette=dict(name='EGA 預設 16 色', rgb=[list(c) for c in EGA]),
               items=items)
    (out / 'manifest.json').write_text(json.dumps(man, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
