#!/usr/bin/env python3
"""G9 HD 第二階段（#10，本專案規格 010 §6）：戰鬥地形、CPIC、頭身、COMSPR、SPRIT 的證據、請求、拆圖與主題。
規則沿用克萊恩英豪 tools/hd_battle_inventory.py、hd_battle_art.py 與其規格 010 §6.2、§6.3。在 sosb-img 容器內執行。

  evidence --inv <inventory/battle> --screens <PNG 目錄>：畫面逐張比對來源，寫 evidence.json
  init     --inv … --prior <克萊恩英豪 workplace/hd> --req <requests> --out <out>：b07 地形、b08 CPIC、b09 頭身、b10 COMSPR、
           b11 SPRIT 的請求；與前作同色號的直接沿用前作成品；其餘等尺寸 16 件拼一張 4×4 圖集（每格 256，來源置中於 192 內）
  prepare  --req … --out …：jobs/ 裡生成的圖集或單張拆回各件，縮到 3 倍，背景色號 8 的區域精確補回 RGB (85,85,85)
  theme    --req … --hd <out> --theme <theme>：數值與目視都通過的批次寫成 combat.json、actors.json、characters.json、
           effects.json、encounters.json（dosgolem apps/sosb 讀取）
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dax_pics import EGA, png  # noqa: E402

BATCH = {'terrain': 'b07', 'actor': 'b08', 'head': 'b09', 'body': 'b09', 'effect': 'b10', 'encounter': 'b11'}
KINDS = {'b07': 'combat-terrain', 'b08': 'combat-actors', 'b09': 'combat-characters', 'b10': 'combat-effects',
         'b11': 'encounter-sprites'}
THEME = {'b07': 'combat.json', 'b08': 'actors.json', 'b09': 'characters.json', 'b10': 'effects.json',
         'b11': 'encounters.json'}
SWAP = [8, 1, 2, 3, 4, 5, 6, 7, 0, 9, 10, 11, 12, 13, 14, 15]  # 人物家族來源 0／8 互換
ENC = [8, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 0, 14, 15]   # SPRIT：來源 0 為背景（灰），13→0
GREY = np.array(EGA[8], np.uint8)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def write(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def rgb_png(path, idx, w, h, s, pal=EGA):
    a = np.array(pal, np.uint8)[np.frombuffer(idx, np.uint8).reshape(h, w)]
    a = np.repeat(np.repeat(a, s, 0), s, 1)
    png(path, w * s, h * s, a.tobytes())


def screen_indexed(path):
    im = Image.open(path).convert('RGB')
    s = im.width // 320
    a = np.asarray(im.resize((320, 200), Image.NEAREST)).reshape(-1, 3)
    lut = {c: i for i, c in enumerate(EGA)}
    try:
        return np.array([lut[tuple(c)] for c in a], np.uint8).reshape(200, 320) if s * 320 == im.width else None
    except KeyError:
        return None


def load(inv):
    rows = json.loads((inv / 'inventory.json').read_text())['items']
    for r in rows:
        w, h = r['size']
        r['array'] = np.frombuffer((inv / r['indexed']).read_bytes(), np.uint8).reshape(h, w)
    return rows


def evidence(a):
    rows = load(a.inv)
    by = {k: [r for r in rows if r['kind'] == k] for k in BATCH}
    terrain = {r['indexed_sha256']: r for r in by['terrain']}
    chars = {}
    for b in by['body']:
        for hd in by['head']:
            p = b['array'].copy()
            q = hd['array']
            p[:q.shape[0]][q != 8] = q[q != 8]
            for flip in (False, True):
                v = p[:, ::-1] if flip else p
                chars.setdefault(sha(np.ascontiguousarray(v).tobytes()), []).append((hd['key'], b['key'], flip))
    found = {}

    def hit(key, rec):
        found.setdefault(key, [])
        if len(found[key]) < 6:
            found[key].append(rec)
    n = 0
    for f in sorted(a.screens.glob('*.png')):
        scr = screen_indexed(f)
        if scr is None:
            continue
        n += 1
        tiles = 0
        for y in range(8, 153, 24):
            for x in range(8, 153, 24):
                r = terrain.get(sha(np.ascontiguousarray(scr[y:y + 24, x:x + 24]).tobytes()))
                if r:
                    tiles += len(r['colors']) > 1
                    hit(r['key'], dict(screen=f.name, x=x, y=y, method='完整矩形'))
        if tiles >= 3:  # 戰鬥畫面守衛：至少三格非純色地形（克萊恩英豪規格 010 §6.2）
            for y in range(8, 153, 24):
                for x in range(8, 153, 24):
                    for hk, bk, flip in chars.get(sha(np.ascontiguousarray(scr[y:y + 24, x:x + 24]).tobytes()), []):
                        for k in (hk, bk):
                            hit(k, dict(screen=f.name, x=x, y=y, flip=flip, method='頭身完整 24×24'))
            for r in by['actor'] + by['effect']:
                h, w = r['array'].shape
                for flip in (False, True):
                    p = r['array'][:, ::-1] if flip else r['array']
                    m = p != 8
                    if m.sum() < 8:
                        continue
                    for y in range(8, 177 - h, 24):
                        for x in range(8, 177 - w, 24):
                            if np.array_equal(scr[y:y + h, x:x + w][m], p[m]):
                                hit(r['key'], dict(screen=f.name, x=x, y=y, flip=flip, method='全部前景'))
        for r in by['encounter']:
            hx, hy = r['aliases'][0]['header_xy']
            x, y = 24 + 8 * hx, 24 + 8 * hy
            h, w = r['array'].shape
            if not (24 <= x and x + w <= 112 and 24 <= y and y + h <= 112):
                continue
            raw = r['array']
            m = raw != 0
            want = np.array(ENC, np.uint8)[raw]
            if m.sum() >= 8 and np.array_equal(scr[y:y + h, x:x + w][m], want[m]):
                hit(r['key'], dict(screen=f.name, x=x, y=y, method='SPRIT 前景（13→0）'))
    write(a.inv / 'evidence.json', dict(screens=n, items=found))
    for k in BATCH:
        keys = {r['key'] for r in by[k]}
        print(f'{k}：命中 {sum(1 for x in found if x in keys)}／{len(keys)}')
    print('畫面', n)


def init(a):
    rows = load(a.inv)
    ev = json.loads((a.inv / 'evidence.json').read_text())['items'] if (a.inv / 'evidence.json').exists() else {}
    groups = {b: [] for b in KINDS}
    for r in rows:
        b = BATCH[r['kind']]
        req, out = a.req / b, a.out / b
        req.mkdir(parents=True, exist_ok=True)
        out.mkdir(parents=True, exist_ok=True)
        key, (w, h) = r['key'], r['size']
        idx = r['array'].tobytes()
        extra = {}
        if b == 'b11':
            raw = idx
            idx = bytes(ENC[c] for c in raw)
            (req / f'{key}.raw.idx').write_bytes(raw)
            (req / f'{key}.mask').write_bytes(bytes(int(c != 0) for c in raw))
            hx, hy = r['aliases'][0]['header_xy']
            extra = dict(raw_indexed=f'{key}.raw.idx', raw_indexed_sha256=sha(raw), foreground_mask=f'{key}.mask',
                         position=[24 + 8 * hx, 24 + 8 * hy])
        (req / r['indexed']).write_bytes(idx)
        rgb_png(req / f'{key}.png', idx, w, h, 1)
        rgb_png(req / f'{key}-x3.png', idx, w, h, 3)
        it = dict(key=key, kind=r['kind'], description='、'.join(f'{s["file"]}:{s["block"]}#{s["record_index"]}'
                                                                 f'@{s["frame"]}/{s["item"]}' for s in r['aliases']),
                  size=[w, h], target_size=[w * 3, h * 3], png=f'{key}.png', reference_png=f'{key}-x3.png',
                  indexed=r['indexed'], indexed_sha256=sha(idx), sources=r['aliases'],
                  runtime_evidence='observed' if key in ev else 'unobserved', evidence=ev.get(key, []),
                  preserve_native_colors=[8], background_index=8, rendering='native_exact_constant'
                  if len(set(idx)) == 1 else 'painted', reuse_candidate=r['reuse_candidate'],
                  palette_mapping=SWAP if b in ('b08', 'b09', 'b10') else ENC if b == 'b11' else list(range(16)), **extra)
        dst = out / f'{key}.png'
        if r['reuse_candidate']:
            old = r['reuse_candidate']
            src = a.prior / 'out' / old['batch'] / f'{old["key"]}.png'
            if sha(src.read_bytes()) != old['png_sha256']:
                sys.exit(f'{key}：前作成品雜湊不符')
            shutil.copyfile(src, dst)
            it['generation'] = f'沿用克萊恩英豪 {old["batch"]}/{old["key"]}（完整色號相同）'
        elif it['rendering'] == 'native_exact_constant':
            Image.open(req / it['reference_png']).convert('RGBA').save(dst)
            it['generation'] = '原版純色保真'
        groups[b].append(it)
    for b, items in groups.items():
        req, out = a.req / b, a.out / b
        write(req / 'manifest.json', dict(batch=b, issue='#10', spec='docs/spec/010-hd-theme.md §6', kind=KINDS[b], scale=3,
                                          palette=dict(name='EGA 預設 16 色', rgb=[list(c) for c in EGA]), items=items))
        pending = [it for it in items if not (out / f'{it["key"]}.png').exists()]
        bysize = {}
        for it in pending:
            bysize.setdefault(tuple(it['size']) if b != 'b11' else 'mixed', []).append(it)
        n = 0
        for size, group in sorted(bysize.items(), key=lambda kv: str(kv[0])):
            for start in range(0, len(group), 16):
                part = group[start:start + 16]
                canvas = Image.new('RGB', (1024, 1024), tuple(EGA[8]))
                draw = ImageDraw.Draw(canvas)
                places = []
                for k, it in enumerate(part):
                    w, h = it['size']
                    s = min(192 // w, 192 // h)
                    W, H = w * s, h * s
                    x, y = k % 4 * 256 + (256 - W) // 2, k // 4 * 256 + (256 - H) // 2
                    canvas.paste(Image.open(req / it['png']).convert('RGB').resize((W, H), Image.NEAREST), (x, y))
                    draw.text((k % 4 * 256 + 6, k // 4 * 256 + 6), str(k + 1), fill=(255, 255, 255))
                    places.append(dict(key=it['key'], rect=[x, y, W, H], target_size=it['target_size']))
                stem = f'atlas-{n:02d}'
                n += 1
                canvas.save(req / f'{stem}.png')
                write(req / f'{stem}.json', dict(batch=b, atlas=stem, canvas=[1024, 1024], items=places))
        print(b, '項', len(items), '沿用或純色', len(items) - len(pending), '待生成', len(pending), '圖集', n)


def prepare(a):
    man = json.loads((a.req / 'manifest.json').read_text())
    by = {it['key']: it for it in man['items']}
    done = set()
    for job in sorted((a.out / 'jobs').glob('*.json')) if (a.out / 'jobs').exists() else []:
        j = json.loads(job.read_text())
        if j.get('status') != 'generated' or not (a.out / j['raw']).exists():
            continue
        im = Image.open(a.out / j['raw']).convert('RGBA')
        W, H = im.size
        if j.get('atlas'):
            parts, bw, bh = json.loads((a.req / f'{j["atlas"]}.json').read_text())['items'], 1024, 1024
        else:
            parts, bw, bh = [dict(key=j['key'], rect=[0, 0, W, H], target_size=by[j['key']]['target_size'])], W, H
        for p in parts:
            if j.get('only') and p['key'] not in j['only']:
                continue
            it = by[p['key']]
            x, y, w, h = p['rect']
            tile = im.crop((round(x * W / bw), round(y * H / bh), round((x + w) * W / bw), round((y + h) * H / bh)))
            arr = np.array(tile.resize(tuple(p['target_size']), Image.Resampling.LANCZOS))
            arr[..., 3] = 255
            sw, sh = it['size']
            idx = np.frombuffer((a.req / it['indexed']).read_bytes(), np.uint8).reshape(sh, sw)
            arr[np.repeat(np.repeat(idx == 8, 3, 0), 3, 1), :3] = GREY
            Image.fromarray(arr).save(a.out / f'{it["key"]}.png')
            done.add(it['key'])
    print(man['batch'], '拆出', len(done), '現有', sum((a.out / f'{k}.png').exists() for k in by), '／', len(by))


def guard_ok(b, req, it):
    """與 dosgolem apps/sosb 各家族載入器的前景下限一致（actor_hd.go、effect_hd.go、encounter_hd.go）。"""
    if b == 'b08':
        idx = (req / it['indexed']).read_bytes()
        return len(set(idx)) >= 3 and sum(c != 8 for c in idx) >= 144
    if b == 'b10':
        idx = (req / it['indexed']).read_bytes()
        return len(set(idx)) >= 3 and sum(c != 8 for c in idx) >= 12
    if b == 'b11':
        ink = [0 if c == 13 else c for c in (req / it['raw_indexed']).read_bytes() if c != 0]
        return len(ink) >= 16 and len(set(ink)) >= 3
    return True


def theme(a):
    a.theme.mkdir(parents=True, exist_ok=True)
    for b, fname in THEME.items():
        raw = (a.req / b / 'manifest.json').read_bytes()
        man = json.loads(raw)
        val = json.loads((a.hd / b / 'validation.json').read_text())
        rev = {r['key']: r for r in json.loads((a.hd / b / 'visual-review.json').read_text())['items']}
        if val['request_manifest_sha256'] != sha(raw):
            sys.exit(f'{b}：請求在驗收後改變')
        vrow = {r['key']: r for r in val['items']}
        items, staged = [], []
        skipped = []
        for it in man['items']:
            k = it['key']
            p = a.hd / b / f'{k}.png'
            ph = sha(p.read_bytes())
            if rev.get(k, {}).get('approved') is False:  # 目視明確退回（附原因）：不收，這項維持原版
                skipped.append(f'{k}（{rev[k].get("reason", "")}）')
                continue
            if not guard_ok(b, a.req / b, it):  # 低於呈現器的安全下限，載入會整個失敗；這項維持原版
                skipped.append(f'{k}（前景低於呈現器下限）')
                continue
            if not (vrow[k]['target_met'] and rev.get(k, {}).get('approved')) or ph != vrow[k]['png_sha256'] \
                    or ph != rev[k]['png_sha256']:
                sys.exit(f'{b}/{k}：未通過數值或目視，或驗收後圖片改變')
            idx = a.req / b / (it['raw_indexed'] if b == 'b11' else it['indexed'])
            staged.append((p, idx))
            row = dict(key=k, size=it['size'], png=f'{k}.png', png_sha256=ph, indexed=idx.name,
                       indexed_sha256=sha(idx.read_bytes()), runtime_evidence=it['runtime_evidence'])
            if b == 'b11':
                row['position'] = it['position']
            items.append(row)
        for p, idx in staged:
            shutil.copyfile(p, a.theme / p.name)
            shutil.copyfile(idx, a.theme / idx.name)
        t = dict(version=1, scale=3, kind=KINDS[b], grid=[8, 8, 7, 7, 24], background_index=8,
                 request_manifest_sha256=sha(raw))
        if b == 'b09':
            t['heads'] = [r for r in items if r['key'].startswith('chead')]
            t['bodies'] = [r for r in items if r['key'].startswith('cbody')]
        else:
            t['items'] = items
        write(a.theme / fname, t)
        print(fname, len(items), '未收：' + '、'.join(skipped) if skipped else '')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('action', choices=('evidence', 'init', 'prepare', 'theme'))
    for k in ('inv', 'screens', 'prior', 'req', 'out', 'hd', 'theme'):
        ap.add_argument('--' + k, type=Path)
    a = ap.parse_args()
    globals()[a.action](a)


if __name__ == '__main__':
    main()
