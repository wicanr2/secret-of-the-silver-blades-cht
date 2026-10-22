#!/usr/bin/env python3
"""G9 HD 審閱頁（#10）：把各批次的原版 3 倍參考圖與 HD 預覽並列成一份 markdown，放進 private repo 供 GitHub 上審閱。
在 sosb-img 容器內以 python3 -I 執行。

輸出 `<out>/README.md` 與 `<out>/img/`：原版 `<key>-orig.png`（最近鄰 3 倍）、HD `<key>-hd.jpg`（JPEG 品質 90 預覽；
正式主題是 workplace/hd/theme 的無損 PNG）。原版圖屬原版素材，repo 轉公開前必須連同歷史移除（AGENTS.md 第 4 節）。
每項附來源、畫面證據、數值閘門（結構分數、色相差中位）與目視狀態。
"""
import argparse
import json
import shutil
from pathlib import Path
from PIL import Image

FAMILY = [('TITLE', '標題畫面'), ('BIGPIC', '大圖'), ('PIC', '肖像與場景')]
# 目視時記下、仍核可的差異
NOTES = {'pic3-016@1': '原版這一幀人物被閃光照成青白色；HD 保留閃電，人物維持正常膚色'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--req', required=True, type=Path)
    ap.add_argument('--hd', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--batches', required=True)
    a = ap.parse_args()
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
        for it in man['items']:
            k = it['key']
            v, r = val.get(k, {}), rev.get(k, {})
            hd = a.hd / b / f'{k}.png'
            shutil.copyfile(a.req / b / it['reference_png'], img / f'{k}-orig.png')
            if hd.exists():
                Image.open(hd).convert('RGB').save(img / f'{k}-hd.jpg', quality=90)
            ok = v.get('target_met') and r.get('approved')
            status = '通過' if ok else ('重畫中' if not v.get('target_met') else '待目視')
            if it.get('prior_theme_keys'):
                status += '（沿用克萊恩英豪）'
            rows.append(dict(batch=b, key=k, family=it['family'], desc=it['description'], w=it['size'][0] * 3,
                             evidence=it['runtime_evidence'], status=status, hd=hd.exists(),
                             structure=v.get('structural_edge_overlap'), hue=v.get('median_hue_difference_degrees')))
    n_ok = sum(r['status'].startswith('通過') for r in rows)
    lines = ['# HD 重繪審閱', '',
             '《銀色匕首之謎》HD 第一階段（標題、大圖、肖像與場景）。左為原版（最近鄰 3 倍），右為依原版手繪重畫的 HD。',
             '生圖由 Codex 內建 image_gen；請求、驗收與接入見 [規格 010](../../docs/spec/010-hd-theme.md)。', '',
             f'共 {len(rows)} 項，通過 {n_ok} 項。數值閘門：結構分數 ≥ 0.40、色相差中位 < 30 度；另逐張目視。',
             'HD 圖為 JPEG 預覽，正式主題是無損 PNG。', '',
             '本目錄含原版圖，只放在 private repo 供審閱；repo 轉公開前必須連同歷史移除。', '']
    for fam, title in FAMILY:
        part = [r for r in rows if r['family'] == fam]
        if not part:
            continue
        lines += [f'## {title}', '', '| 項目 | 原版 | HD |', '|---|---|---|']
        for r in part:
            w = min(r['w'], 456)
            score = (f"結構 {r['structure']:.2f}<br>色相 {r['hue']:.1f}°" if r['structure'] is not None else '')
            meta = (f"`{r['key']}`<br>{r['desc']}<br>畫面證據：{'已觀測' if r['evidence'] == 'observed' else '未觀測'}"
                    f"<br>{score}<br>**{r['status']}**" + (f"<br>備註：{NOTES[r['key']]}" if r['key'] in NOTES else ''))
            hd = f'<img src="img/{r["key"]}-hd.jpg" width="{w}">' if r['hd'] else '（尚無）'
            lines.append(f'| {meta} | <img src="img/{r["key"]}-orig.png" width="{w}"> | {hd} |')
        lines.append('')
    (a.out / 'README.md').write_text('\n'.join(lines))
    print(len(rows), '項', n_ok, '通過')


if __name__ == '__main__':
    main()
