#!/usr/bin/env python3
"""G9 HD 審閱頁（#10）：把各批次的原版 3 倍參考圖與 HD 預覽並列成一份 markdown，放進 private repo 供 GitHub 上審閱。
在 sosb-img 容器內以 python3 -I 執行。

輸出 `<out>/README.md` 與 `<out>/img/`：原版 `<key>-orig.png`（最近鄰 3 倍）、HD `<key>-hd.jpg`（JPEG 品質 90 預覽；
正式主題是 workplace/hd/theme 的無損 PNG）。原版圖屬原版素材，repo 轉公開前必須連同歷史移除（AGENTS.md 第 4 節）。
每項附來源、畫面證據、數值閘門（結構分數、色相差中位）與目視狀態。畫面證據另讀 `--observed`（tools/hd_observe.py 的輸出）。
"""
import argparse
import json
import shutil
from pathlib import Path
from PIL import Image

FAMILY = [('TITLE', '標題畫面'), ('BIGPIC', '大圖'), ('PIC', '肖像與場景'), ('terrain', '戰鬥地形'),
          ('actor', '戰鬥怪物與人物'), ('encounter', '3D 遭遇圖'), ('effect', '戰鬥效果'), ('head', '頭像組件'),
          ('body', '身體組件'), ('sky', '3D 天空與地面')]
COMPACT = {'terrain', 'actor', 'encounter', 'effect', 'head', 'body', 'sky'}  # 小圖：一列三組
SHEET = {'wall'}  # 8×8 牆面圖塊：每頁 64 組拼成一張圖
# 目視時記下的差異與不收入主題的原因
NOTES = {'pic3-016@1': '原版這一幀人物被閃光照成青白色；HD 保留閃電，人物維持正常膚色',
         'sprit1-001-00-00': '前景低於呈現器下限（至少 16 點、3 色），不收入主題，維持原版'}
SKIP = {'sprit1-001-00-00'}  # 數值與目視通過，但 tools/hd_battle.py guard_ok 不收入主題


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--req', required=True, type=Path)
    ap.add_argument('--hd', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--batches', required=True)
    ap.add_argument('--observed', type=Path, help='tools/hd_observe.py 的輸出：{key: [畫格…]}')
    a = ap.parse_args()
    obs = json.loads(a.observed.read_text()) if a.observed else {}
    sheets = []
    img = a.out / 'img'
    if img.exists():
        shutil.rmtree(img)
    img.mkdir(parents=True)
    rows = []
    for b in a.batches.split(','):
        man = json.loads((a.req / b / 'manifest.json').read_text())
        val = {r['key']: r for r in json.loads((a.hd / b / 'validation.json').read_text())['items']}
        rp = a.hd / b / 'visual-review.json'
        rev = {r['key']: r for r in json.loads(rp.read_text())['items']} if rp.exists() else {}
        walls = [it for it in man['items'] if it.get('kind') in SHEET]
        for start in range(0, len(walls), 64):  # 拼圖頁：8 欄 × 8 列，每組原版 48 像素｜HD 48 像素
            page = Image.new('RGB', (8 * 104, 8 * 56), (30, 30, 30))
            for n, it in enumerate(walls[start:start + 64]):
                x, y = n % 8 * 104, n // 8 * 56
                page.paste(Image.open(a.req / b / it['reference_png']).convert('RGB').resize((48, 48), Image.NEAREST), (x, y))
                page.paste(Image.open(a.hd / b / f'{it["key"]}.png').convert('RGB').resize((48, 48), Image.NEAREST), (x + 50, y))
            name = f'{b}-sheet-{start // 64:02d}.png'
            page.save(img / name)
            keys = [it['key'] for it in walls[start:start + 64]]
            sheets.append((name, keys[0], keys[-1], len(keys)))
        for it in man['items']:
            k = it['key']
            v, r = val.get(k, {}), rev.get(k, {})
            if it.get('kind') in SHEET:
                rows.append(dict(batch=b, key=k, family='wall', status='通過' if v.get('target_met') and r.get('approved')
                                 else '維持原版', hd=True, sheet=True))
                continue
            hd = a.hd / b / f'{k}.png'
            shutil.copyfile(a.req / b / it['reference_png'], img / f'{k}-orig.png')
            if hd.exists():
                Image.open(hd).convert('RGB').save(img / f'{k}-hd.jpg', quality=90)
            ok = v.get('target_met') and r.get('approved')
            status = '通過' if ok and k not in SKIP else ('維持原版' if r.get('approved') is False or k in SKIP else
                                       '重畫中' if not v.get('target_met') else '待目視')
            if it.get('prior_theme_keys') or str(it.get('generation', '')).startswith('沿用'):
                status += '（沿用克萊恩英豪）'
            if r.get('reason'):
                NOTES.setdefault(k, r['reason'])
            fam = it.get('family') or it.get('kind')
            rows.append(dict(batch=b, key=k, family=fam, desc=it['description'],
                             w=it['size'][0] * (6 if fam in COMPACT else 3),
                             evidence='observed' if k in obs else it['runtime_evidence'], frame=obs.get(k, [''])[0],
                             status=status, hd=hd.exists(),
                             structure=v.get('structural_edge_overlap'), hue=v.get('median_hue_difference_degrees')))
    n_ok = sum(r['status'].startswith('通過') for r in rows)
    lines = ['# HD 重繪審閱', '',
             '《銀色匕首之謎》HD：第一階段（標題、大圖、肖像與場景）、第二階段（戰鬥地形、怪物、遭遇圖、效果、頭身組件）、',
             '第三階段（3D 牆面圖塊、天空與地面）。',
             '每組左為原版（最近鄰放大），右為依原版手繪重畫的 HD；小圖以 6 倍顯示。',
             '生圖由 Codex 內建 image_gen；請求、驗收與接入見 [規格 010](../../docs/spec/010-hd-theme.md)。', '',
             f'共 {len(rows)} 項，通過 {n_ok} 項。數值閘門：結構分數 ≥ 0.40、色相差中位 < 30 度；目視：第一階段逐張，戰鬥與牆面以總覽加放大抽樣（使用者 2026-10-23：抽樣驗證即可）。',
             'HD 圖為 JPEG 預覽，正式主題是無損 PNG。', '',
             '本目錄含原版圖，只放在 private repo 供審閱；repo 轉公開前必須連同歷史移除。', '']
    for fam, title in FAMILY:
        part = [r for r in rows if r['family'] == fam]
        if not part:
            continue
        if fam in COMPACT:
            lines += [f'## {title}', '', f'{len(part)} 項。', '', '| 項目 | 原版 | HD ' * 3 + '|', '|---' * 9 + '|']
            for i in range(0, len(part), 3):
                cells = []
                for r in part[i:i + 3]:
                    w = min(r['w'], 288)
                    score = f"<br>結構 {r['structure']:.2f}、色相 {r['hue']:.0f}°" if r['structure'] is not None else ''
                    note = f"<br>{NOTES[r['key']]}" if r['key'] in NOTES else ''
                    hd = f'<img src="img/{r["key"]}-hd.jpg" width="{w}">' if r['hd'] else '（尚無）'
                    cells.append(f"`{r['key']}`{score}<br>**{r['status']}**{note} | "
                                 f'<img src="img/{r["key"]}-orig.png" width="{w}"> | {hd}')
                cells += [' | | '] * (3 - len(cells))
                lines.append('| ' + ' | '.join(cells) + ' |')
            lines.append('')
            continue
        lines += [f'## {title}', '', '| 項目 | 原版 | HD |', '|---|---|---|']
        for r in part:
            w = min(r['w'], 456)
            score = (f"結構 {r['structure']:.2f}<br>色相 {r['hue']:.1f}°" if r['structure'] is not None else '')
            meta = (f"`{r['key']}`<br>{r['desc']}<br>畫面證據：{'已觀測' if r['evidence'] == 'observed' else '未觀測'}{'（推廣片 ' + r['frame'] + '）' if r.get('frame') else ''}"
                    f"<br>{score}<br>**{r['status']}**" + (f"<br>備註：{NOTES[r['key']]}" if r['key'] in NOTES else ''))
            hd = f'<img src="img/{r["key"]}-hd.jpg" width="{w}">' if r['hd'] else '（尚無）'
            lines.append(f'| {meta} | <img src="img/{r["key"]}-orig.png" width="{w}"> | {hd} |')
        lines.append('')
    if sheets:
        lines += ['## 3D 牆面圖塊', '', f'{sum(n for *_, n in sheets)} 個 8×8 圖塊，每頁 64 組，每組左為原版、右為 HD（各放大成 48 像素）。'
                  '逐項的來源、分數與沿用紀錄在 `workplace/hd/requests/b13/manifest.json` 與 `out/b13/validation.json`。', '']
        for name, first, last, n in sheets:
            lines += [f'`{first}` 到 `{last}`（{n} 組）', '', f'<img src="img/{name}" width="832">', '']
    (a.out / 'README.md').write_text('\n'.join(lines))
    print(len(rows), '項', n_ok, '通過')


if __name__ == '__main__':
    main()
