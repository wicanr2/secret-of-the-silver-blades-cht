#!/usr/bin/env python3
"""G9 HD 第三階段（#10，本專案規格 010 §7）：3D 牆面 8×8 圖塊與 SKY。規則沿用克萊恩英豪 tools/hd_wall_inventory.py、
hd_wall_art.py、hd_wall_theme.py 與其規格 010 §7。在 sosb-img 容器內執行。

  init     --orig --prior <克萊恩英豪 workplace/hd> --req <requests> --out <out>：WALLDEF 用到的 8X8D 圖塊（b13）與 SKY（b14）的請求；
           與前作來源逐位元組相同的沿用前作成品；其餘 64 件拼一張 8×8 圖集（每格 128，圖塊 96×96 在 (16,16)）
  prepare  --req --out：拆圖集、縮到 3 倍；來源 13（留底）補灰 (85,85,85)；牆面最外一圈輸出像素固定為原版邊界色
  validate --req --out：尺寸、alpha、留底遮罩、色相差中位 < 30 度、結構 ≥ 0.40（小圖塊用克萊恩英豪規格 010 §7.3–7.4 的校準）
  evidence --orig --screens <PNG 目錄>… --out <inventory/wall>：3D 視窗以「天空色＋SKY 252 地面 (0,40)」重建，記下觀測到的組合格
  redo     --req --out：數值未過的牆面圖塊拼成 4×4 重畫圖集 redo-NN（每件 192×192 在 (32,32)），原輸出另存 *-failed-NN.png
  theme    --req --hd --inv --theme：walls.json（dosgolem apps/sosb wall_hd.go 讀取）
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dax_pics import EGA, dax, picture, png  # noqa: E402
from hd_compare import hue_score, lowpass, structural_score  # noqa: E402

LAYOUTS = [(0, 1, 2), (2, 1, 4), (6, 1, 4), (10, 3, 4), (22, 2, 8), (38, 2, 8), (54, 7, 8), (110, 2, 11), (132, 2, 11),
           (154, 1, 2)]
SKY_COLORS = (0, 11, 15)  # 本作已觀測：室外 11、室內 15；0 為夜間（demo 地城入口）
GROUND = (252, 0, 40)     # SKY 區塊 252 地面貼在視窗 (0,40)
GREY = np.array(EGA[8], np.uint8)
PROMPT = ('Production HD refinement of a precisely registered 8 by 8 atlas of fantasy town and dungeon wall texture fragments '
          'for Secret of the Silver Blades (1990 Gold Box). Output an exactly square 1024x1024 image keeping exactly eight columns '
          'and eight rows; each cell is 128x128 with a centered 96x96 fragment at offset 16,16 that must stay inside those exact '
          'bounds. Repaint every populated square in restrained, finely painted fantasy illustration style B using the original '
          'local colors. These are tiny stone, brick, wood plank, cobblestone, roof, door and diagonal perspective wall fragments, '
          'not characters or icons. Preserve the precise positions, proportions, perspective edges, mortar lines, plank lines, '
          'highlights and dark regions of EVERY fragment; keep black black, brown brown, cyan cyan, grey grey, red red, blue blue, '
          'white white; do not desaturate or recolor. Flat grey RGB 85,85,85 margins and grey masked-out regions stay flat grey. '
          'Leave empty cells empty. No numbers, labels, text, frames, lighting effects, shadows or extra scenery. Tile continuity '
          'is critical: do not move edge pixels, corners or line endpoints; adjacent fragments must join without a new seam. '
          'Paint subtle surface detail inside the original shapes only. Fully opaque.')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def write(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def rgb_png(path, idx, w, h, s):
    a = np.array(EGA, np.uint8)[np.frombuffer(idx, np.uint8).reshape(h, w)]
    png(path, w * s, h * s, np.repeat(np.repeat(a, s, 0), s, 1).tobytes())


def load_tiles(orig):
    """回 {raw: dict(key, aliases)}（WALLDEF 用到、非全留底的 8×8 圖塊）與 SKY 圖。"""
    tiles = {}
    for name in ('8X8D1', '8X8D2', '8X8D3'):
        for n, (bid, raw) in enumerate(dax((orig / f'{name}.DAX').read_bytes())):
            w, h, cnt, x, y, px = picture(raw)
            for i in range(cnt):
                tiles[(f'{name}.DAX', bid, i)] = (bytes(px[i * 64:(i + 1) * 64]), n)
    used = {}
    for name in ('WALLDEF1', 'WALLDEF2', 'WALLDEF3'):
        for bid, raw in dax((orig / f'{name}.DAX').read_bytes()):
            k = len(raw) // 780
            blocks = [bid] if k == 1 else [bid * 10 + i + 1 for i in range(k)]
            bank = f'8X8D{name[7]}.DAX'
            for s in raw:
                if s == 0:
                    continue
                if s <= 45:
                    loc = ('8X8D1.DAX', 203, s - 1)
                else:
                    band = (s - 46) // 70
                    loc = (bank, blocks[band], (s - 46) % 70) if band < len(blocks) else None
                if loc in tiles and any(v != 13 for v in tiles[loc][0]):
                    p, rec = tiles[loc]
                    row = used.setdefault(p, dict(key=f'wall-{loc[0][4]}-{loc[1]:03d}-{loc[2]:02d}', aliases=[]))
                    src = dict(file=loc[0], block=loc[1], record_index=rec, item=loc[2])
                    if src not in row['aliases']:
                        row['aliases'].append(src)
    sky = {}
    for n, (bid, raw) in enumerate(dax((orig / 'SKY.DAX').read_bytes())):
        w, h, cnt, x, y, px = picture(raw)
        sky[bid] = dict(key=f'sky-{bid:03d}-00', size=[w, h], raw=bytes(px[:w * h]),
                        aliases=[dict(file='SKY.DAX', block=bid, record_index=n, item=0)])
    return used, sky


def init(a):
    used, sky = load_tiles(a.orig)
    prior = {}
    pm = a.prior / 'requests/b13/manifest.json'
    for it in json.loads(pm.read_text())['items'] if pm.exists() else []:
        png_p = a.prior / 'out/b13' / f'{it["key"]}.png'
        if png_p.is_file():
            prior[it['raw_indexed_sha256']] = (it['key'], png_p)
    for b, rows in (('b13', [dict(v, raw=k, size=[8, 8]) for k, v in used.items()]), ('b14', list(sky.values()))):
        req, out = a.req / b, a.out / b
        req.mkdir(parents=True, exist_ok=True)
        (out / 'jobs').mkdir(parents=True, exist_ok=True)
        items = []
        for r in sorted(rows, key=lambda r: r['key']):
            key, (w, h), raw = r['key'], r['size'], r['raw']
            mapped = bytes(8 if c == 13 else c for c in raw)
            (req / f'{key}.idx').write_bytes(mapped)
            (req / f'{key}.raw.idx').write_bytes(raw)
            rgb_png(req / f'{key}.png', mapped, w, h, 1)
            rgb_png(req / f'{key}-x3.png', mapped, w, h, 3)
            it = dict(key=key, kind='wall' if b == 'b13' else 'sky', size=[w, h], target_size=[w * 3, h * 3],
                      png=f'{key}.png', reference_png=f'{key}-x3.png', indexed=f'{key}.idx', indexed_sha256=sha(mapped),
                      raw_indexed=f'{key}.raw.idx', raw_indexed_sha256=sha(raw), sources=r['aliases'],
                      description='、'.join(f'{s["file"]}:{s["block"]}#{s["record_index"]}/{s["item"]}' for s in r['aliases']),
                      runtime_evidence='見 inventory/wall/evidence.json', transparent_source=13,
                      rendering='native_exact_constant' if len(set(mapped)) == 1 else 'painted')
            dst = out / f'{key}.png'
            if sha(raw) in prior and b == 'b13':
                shutil.copyfile(prior[sha(raw)][1], dst)
                it['generation'] = f'沿用克萊恩英豪 b13/{prior[sha(raw)][0]}（來源逐位元組相同）'
            elif it['rendering'] == 'native_exact_constant':
                Image.open(req / it['reference_png']).convert('RGBA').save(dst)
                it['generation'] = '原版純色保真'
            items.append(it)
        write(req / 'manifest.json', dict(batch=b, issue='#10', spec='docs/spec/010-hd-theme.md §7', scale=3,
                                          kind='wall-tiles' if b == 'b13' else 'sky',
                                          palette=dict(name='EGA 預設 16 色；13 留底以灰色表示', rgb=[list(c) for c in EGA]),
                                          items=items))
        pending = [it for it in items if not (out / f'{it["key"]}.png').exists()]
        if b == 'b13':
            for start in range(0, len(pending), 64):
                canvas = Image.new('RGB', (1024, 1024), tuple(EGA[8]))
                places = []
                for n, it in enumerate(pending[start:start + 64]):
                    x, y = n % 8 * 128 + 16, n // 8 * 128 + 16
                    canvas.paste(Image.open(req / it['png']).convert('RGB').resize((96, 96), Image.NEAREST), (x, y))
                    places.append(dict(key=it['key'], rect=[x, y, 96, 96], target_size=it['target_size']))
                stem = f'atlas-{start // 64:02d}'
                canvas.save(req / f'{stem}.png')
                write(req / f'{stem}.json', dict(atlas=stem, canvas=[1024, 1024], items=places))
            (req / 'atlas-prompt.txt').write_text(PROMPT + '\n')
        else:
            for it in pending:
                w, h = it['size']
                Image.open(req / it['png']).convert('RGB').resize((w * 10, h * 10), Image.NEAREST).save(req / f'{it["key"]}-x10.png')
        print(b, '項', len(items), '沿用或純色', len(items) - len(pending), '待生成', len(pending),
              '圖集', (len(pending) + 63) // 64 if b == 'b13' else 0)


def prepare(a):
    man = json.loads((a.req / 'manifest.json').read_text())
    by = {it['key']: it for it in man['items']}
    done = 0
    for job in sorted((a.out / 'jobs').glob('*.json')):
        j = json.loads(job.read_text())
        if j.get('status') != 'generated' or not (a.out / j['raw']).exists():
            continue
        im = Image.open(a.out / j['raw']).convert('RGBA')
        W, H = im.size
        if j.get('atlas'):
            at = json.loads((a.req / f'{j["atlas"]}.json').read_text())
            places, cw, ch = at['items'], 1024, 1024
        else:
            places, cw, ch = [dict(key=j['key'], rect=[0, 0, W, H], target_size=by[j['key']]['target_size'])], W, H
        for p in places:
            if j.get('only') and p['key'] not in j['only']:
                continue
            it = by[p['key']]
            x, y, w, h = p['rect']
            arr = np.array(im.crop((round(x * W / cw), round(y * H / ch), round((x + w) * W / cw), round((y + h) * H / ch)))
                           .resize(tuple(p['target_size']), Image.Resampling.LANCZOS))
            arr[..., 3] = 255
            sw, sh = it['size']
            src = np.frombuffer((a.req / it['raw_indexed']).read_bytes(), np.uint8).reshape(sh, sw)
            arr[np.repeat(np.repeat(src == 13, 3, 0), 3, 1), :3] = GREY
            if it['kind'] == 'wall':  # 一個輸出像素寬的原版邊界固定接縫（克萊恩英豪規格 010 §7.2）
                native = np.repeat(np.repeat(np.array(EGA, np.uint8)[np.where(src == 13, 8, src)], 3, 0), 3, 1)
                border = np.zeros(arr.shape[:2], bool)
                border[0, :] = border[-1, :] = border[:, 0] = border[:, -1] = True
                arr[border, :3] = native[border]
            Image.fromarray(arr).save(a.out / f'{it["key"]}.png')
            done += 1
    print(man['batch'], '拆出', done, '現有', sum((a.out / f'{k}.png').exists() for k in by), '／', len(by))


_CAL = {}


def wall_structure(orig, hd):
    """克萊恩英豪規格 010 §7.3–7.4：來源三個固定正對照（自比、RGB ±1）有一個低於 0.40，就改用連續梯度交並比。"""
    legacy = structural_score(orig, hd)
    key = orig.tobytes()
    if key not in _CAL:
        _CAL[key] = min(structural_score(orig, np.repeat(np.repeat(np.clip(orig.astype(np.int16) + d, 0, 255)
                                                                   .astype(np.uint8), 3, 0), 3, 1)) for d in (0, -1, 1))
    if _CAL[key] >= .4:
        return legacy, legacy, 'legacy-percentile'
    lum = lambda x: x[..., 0] * .299 + x[..., 1] * .587 + x[..., 2] * .114
    h, w = orig.shape[:2]
    small = hd[..., :3].reshape(h, 3, w, 3, 3).mean(axis=(1, 3))

    def grad(x):
        p = lum(x)
        return np.abs(np.diff(p, axis=1))[:-1, :] + np.abs(np.diff(p, axis=0))[:, :-1]
    g1, g2 = grad(lowpass(orig)), grad(lowpass(small))
    den = np.maximum(g1, g2).sum()
    return (float(np.minimum(g1, g2).sum() / den) if den > 0 else 0.), legacy, 'continuous-gradient-jaccard-calibrated-source'


def validate(a):
    raw_b = (a.req / 'manifest.json').read_bytes()
    man = json.loads(raw_b)
    rows = []
    for it in man['items']:
        p = a.out / f'{it["key"]}.png'
        if not p.exists():
            rows.append(dict(key=it['key'], target_met=False, error='缺輸出'))
            continue
        arr = np.array(Image.open(p).convert('RGBA'))
        w, h = it['size']
        idx = np.frombuffer((a.req / it['indexed']).read_bytes(), np.uint8).reshape(h, w)
        raw = np.frombuffer((a.req / it['raw_indexed']).read_bytes(), np.uint8).reshape(h, w)
        orig = np.array(EGA, np.uint8)[idx]
        mask = np.repeat(np.repeat(raw == 13, 3, 0), 3, 1)
        shape_ok = arr.shape == (h * 3, w * 3, 4) and bool((arr[..., 3] == 255).all())
        off = int(np.any(arr[..., :3] != GREY, axis=2)[mask].sum()) if shape_ok else -1
        constant = it['rendering'] == 'native_exact_constant'
        if constant:
            st, legacy, method, hue = 1., 1., 'constant', 0.
            good = shape_ok and bool(np.all(arr[..., :3] == orig[0, 0]))
        else:
            st, legacy, method = wall_structure(orig, arr) if shape_ok else (0., 0., 'shape')
            hue = float(hue_score(orig, arr)[0]) if shape_ok else 360.
            good = shape_ok and off == 0 and hue < 30 and st >= .4
        rows.append(dict(key=it['key'], structural_edge_overlap=st, legacy_structural_score=legacy, structure_method=method,
                         median_hue_difference_degrees=hue, mask_difference=off, target_met=bool(good),
                         png_sha256=sha(p.read_bytes())))
    write(a.out / 'validation.json', dict(batch=man['batch'], request_manifest_sha256=sha(raw_b),
                                          all_pass=all(r['target_met'] for r in rows), items=rows))
    bad = [r['key'] for r in rows if not r['target_met']]
    print(man['batch'], '未過', len(bad), '／', len(rows), ' '.join(bad[:30]))


def redo(a):
    man = json.loads((a.req / 'manifest.json').read_text())
    table = {it['key']: it for it in man['items']}
    failed = [r['key'] for r in json.loads((a.out / 'validation.json').read_text())['items']
              if not r['target_met'] and table[r['key']]['kind'] == 'wall']
    start = len(list(a.req.glob('redo-*.json')))
    for off in range(0, len(failed), 16):
        canvas = Image.new('RGB', (1024, 1024), tuple(EGA[8]))
        places = []
        n_atlas = start + off // 16
        for n, k in enumerate(failed[off:off + 16]):
            x, y = n % 4 * 256 + 32, n // 4 * 256 + 32
            canvas.paste(Image.open(a.req / table[k]['png']).convert('RGB').resize((192, 192), Image.NEAREST), (x, y))
            places.append(dict(key=k, rect=[x, y, 192, 192], target_size=table[k]['target_size']))
            old = a.out / f'{k}.png'
            if old.exists():
                shutil.copyfile(old, a.out / f'{k}-failed-{n_atlas:02d}.png')
        stem = f'redo-{n_atlas:02d}'
        canvas.save(a.req / f'{stem}.png')
        write(a.req / f'{stem}.json', dict(atlas=stem, canvas=[1024, 1024], items=places))
    print('重畫', len(failed), '圖集', (len(failed) + 15) // 16)


def background(color, ground):
    bg = np.full((88, 88), color, np.uint8)
    m = ground != 13
    bg[40:88][m] = ground[m]
    return bg


def evidence(a):
    used, sky = load_tiles(a.orig)
    ground = np.frombuffer(sky[GROUND[0]]['raw'], np.uint8).reshape(48, 88)
    keys = {raw: v['key'] for raw, v in used.items()}
    masked = [(np.frombuffer(r, np.uint8).reshape(8, 8), k) for r, k in keys.items() if 13 in r]
    lut = {c: i for i, c in enumerate(EGA)}
    seen, screens = {}, 0
    for d in a.screens:
        for f in sorted(d.glob('*.png')):
            im = np.asarray(Image.open(f).convert('RGB').resize((320, 200), Image.NEAREST)).reshape(-1, 3)
            try:
                scr = np.array([lut[tuple(c)] for c in im], np.uint8).reshape(200, 320)
            except KeyError:
                continue
            panel = scr[24:112, 24:112]
            for color in SKY_COLORS:
                bg = background(color, ground)
                if not np.array_equal(panel[0:8, 0:8], bg[0:8, 0:8]) and panel[0, 0] != color:
                    continue
                for pos in range(121):
                    y, x = pos // 11 * 8, pos % 11 * 8
                    p, b = panel[y:y + 8, x:x + 8], bg[y:y + 8, x:x + 8]
                    for t, k in masked:
                        if np.array_equal(np.where(t == 13, b, t), p):
                            seen.setdefault(f'{pos}:{color}:{k}', dict(pos=pos, color=color, key=k, screen=f'{d.name}/{f.name}'))
            screens += 1
    a.out.mkdir(parents=True, exist_ok=True)
    write(a.out / 'evidence.json', dict(screens=screens, model='天空色＋SKY 252 地面 (0,40)', composites=list(seen.values())))
    print('畫面', screens, '觀測到的留底組合格', len(seen))


def theme(a):
    assets, specs = {}, []
    for b in ('b13', 'b14'):
        raw_b = (a.req / b / 'manifest.json').read_bytes()
        man = json.loads(raw_b)
        val = {r['key']: r for r in json.loads((a.hd / b / 'validation.json').read_text())['items']}
        rev = {r['key']: r for r in json.loads((a.hd / b / 'visual-review.json').read_text())['items']}
        for it in man['items']:
            k, p = it['key'], a.hd / b / f'{it["key"]}.png'
            ph = sha(p.read_bytes())
            if not (val[k]['target_met'] and rev.get(k, {}).get('approved')) or ph != val[k]['png_sha256'] or ph != rev[k]['png_sha256']:
                print('未收', k)
                continue
            w, h = it['size']
            raw = (a.req / b / it['raw_indexed']).read_bytes()
            assets[k] = dict(ref=np.frombuffer(raw, np.uint8).reshape(h, w), pix=np.array(Image.open(p).convert('RGBA')),
                             wall=b == 'b13', raw=raw, png=p)
            specs.append(dict(key=k, kind=it['kind'], size=[w, h], indexed=f'walls/{k}.idx', indexed_sha256=sha(raw),
                              png=f'walls/{k}.png', png_sha256=ph))

    def compose(base, layers):
        ref = np.full((8, 8), base, np.uint8)
        pix = np.empty((24, 24, 4), np.uint8)
        pix[:] = [*EGA[base], 255]
        for lk, (dx, dy) in layers:
            s = assets[lk]
            src = s['ref']
            hh, ww = src.shape
            L, R, T, B = max(0, dx), min(8, dx + ww), max(0, dy), min(8, dy + hh)
            q = src[T - dy:B - dy, L - dx:R - dx]
            m = q != 13
            ref[T:B, L:R][m] = q[m]
            big = np.repeat(np.repeat(m, 3, 0), 3, 1)
            pix[T * 3:B * 3, L * 3:R * 3][big] = s['pix'][(T - dy) * 3:(B - dy) * 3, (L - dx) * 3:(R - dx) * 3][big]
        return ref, pix

    glob, local, cells = {}, {}, []

    def add(pos, base, layers, label, complete=False):
        ref, pix = compose(base, layers)
        d = sha(ref.tobytes())
        if d in glob:
            return
        spec = dict(key=label, positions=[] if pos is None else [pos], base_color=base,
                    layers=[dict(key=k, at=list(at)) for k, at in layers], indexed_sha256=d, paint=True)
        if pos is None:
            if complete:
                spec['complete_background'] = True
            glob[d] = spec
        else:
            if (pos, d) in local:
                return
            local[(pos, d)] = spec
        cells.append(spec)
    for k, s in assets.items():  # 完整不留底的圖塊：任何位置
        if s['wall'] and 13 not in s['raw']:
            add(None, 0, [(k, (0, 0))], k)
    for k, s in assets.items():  # 留底圖塊疊在純天空色上：任何位置（完整背景契約）
        if s['wall'] and 13 in s['raw']:
            for c in SKY_COLORS:
                add(None, c, [(k, (0, 0))], f'{k}@{c}', complete=True)
    gk = f'sky-{GROUND[0]:03d}-00'
    if gk in assets:
        def bg_layers(pos):
            x, y = pos % 11 * 8, pos // 11 * 8
            return [(gk, (GROUND[1] - x, GROUND[2] - y))] if y + 8 > GROUND[2] else []
        for c in SKY_COLORS:  # 只有背景的格（天空色＋地面）
            for pos in range(121):
                if bg_layers(pos):
                    add(pos, c, bg_layers(pos), f'background-{c}-{pos:03d}')
        ev = json.loads((a.inv / 'evidence.json').read_text())['composites'] if (a.inv / 'evidence.json').exists() else []
        for e in ev:  # 已觀測的留底圖塊疊在地面上
            if e['key'] in assets and bg_layers(e['pos']):
                add(e['pos'], e['color'], bg_layers(e['pos']) + [(e['key'], (0, 0))], f'composed-{e["color"]}-{e["pos"]:03d}-{e["key"]}')
    dest = a.theme / 'walls'
    dest.mkdir(parents=True, exist_ok=True)
    for k, s in assets.items():
        (dest / f'{k}.idx').write_bytes(s['raw'])
        shutil.copyfile(s['png'], dest / f'{k}.png')
    write(a.theme / 'walls.json', dict(version=1, scale=3, kind='wall-grid', viewport=[24, 24, 11, 11, 8], assets=specs,
                                       cells=cells))
    print('素材', len(specs), '通用格', len(glob), '位置格', len(local))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('action', choices=('init', 'prepare', 'validate', 'evidence', 'redo', 'theme'))
    for k in ('orig', 'prior', 'req', 'out', 'hd', 'inv', 'theme'):
        ap.add_argument('--' + k, type=Path)
    ap.add_argument('--screens', type=Path, nargs='*', default=[])
    a = ap.parse_args()
    globals()[a.action](a)


if __name__ == '__main__':
    main()
