#!/usr/bin/env python3
"""珍056 下冊怪物（p.9–14）與法術（p.14–25）章節的名稱對照（G4「遊戲內指涉查證」，docs/re/006）。在 sosb-tools 容器內以 python3 -I 執行。

用法：zh056_names.py --draft ocr-draft.tsv --glossary text/glossary.tsv --out text/zh056-names.tsv
草稿是 tools/zh_manual_draft.py 的 OCR 結果（未校對）；條目在行首寫成「中文名（English）」，以正規式抽出。
FIX、ENFIX 是逐格對 300 dpi 頁面圖確認過的 OCR 錯字更正（中文名以頁碼為鍵；英文的 1／l 混淆）；珍056 原書的英文拼錯
（Disintigrate、Fresh to Stone、Mammel）照原書保留。英文只留字母、不分大小寫比對術語表 en。
輸出：page（下冊頁碼）、kind（monster／spell）、en、zh056、game（遊戲內譯名）、game_source（術語表來源）、result（同名、異名、術語表無）。
"""
import argparse
import csv
import re
norm = lambda t: re.sub(r'[^a-z]', '', t.lower().replace('1', 'l'))
gl = {}
ap = argparse.ArgumentParser()
ap.add_argument('--draft', required=True)
ap.add_argument('--glossary', required=True)
ap.add_argument('--out', required=True)
a = ap.parse_args()
for r in csv.DictReader(open(a.glossary, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE):
    gl.setdefault(norm(r['en']), r)
LINE = re.compile(r'^\s*(?:\d{1,2}\s*[.．]?\s*)?[＊*※\u2731\u5a1f\u6e3e]?\s*([\u3400-\u9fff]{1,14})\s*[（(]\s*([A-Za-z][^）)]{1,45}?)\s*[)）]')
FIX = {('9', '巨'): '巨鱷', ('10', '牛蛛精靈'): '半蛛精靈', ('11', '驚獅'): '鷲獅', ('12', '蛇髪女妖'): '蛇髮女妖', ('13', '巨蛞鹼'): '巨蛞蝓',
       ('13', '互蛇'): '巨蛇', ('19', '搜魔法物品'): '搜尋魔法物品', ('19', '互大術'): '巨大術', ('21', '牛徑十呎的隱形術'): '半徑十呎的隱形術', ('24', '牵制之咒'): '牽制之咒', ('24', '值測魔法'): '偵測魔法'}
ENFIX = {'Hil1Giant': 'Hill Giant', 'B1ess': 'Bless', 'B1ink': 'Blink', 'S1ow': 'Slow', 'Fumb1e': 'Fumble',
         'Minor Globe of InvuInerabiIity': 'Minor Globe of Invulnerability'}
order = ['p15r2c0','p15r2c1','p16r0c0','p16r0c1','p16r1c0','p16r1c1','p16r2c0','p16r2c1','p17r0c0','p17r0c1','p17r1c0','p17r1c1','p17r2c0','p17r2c1','p18r0c0','p18r0c1','p18r1c0','p18r1c1']
rows = {r['cell']: r for r in csv.DictReader(open(a.draft, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE)}
out = ['page\tkind\ten\tzh056\tgame\tgame_source\tresult']
kind = 'monster'
for c in order:
    n = int(c[1:3]); idx = int(c[4]) * 2 + int(c[6]); page = (n - 14) * 6 + idx - 1
    for line in rows[c]['text'].split('\\n'):
        if '法術' in line and ('牧師' in line or '五' in line): kind = 'spell'
        m = LINE.match(line)
        if not m: continue
        zh, en = m.group(1), re.sub(r'\s+', ' ', m.group(2)).strip()
        zh = FIX.get((str(page), zh), zh); en = ENFIX.get(en, en)
        g = gl.get(norm(en)) or gl.get(norm(en)[:-1])
        res = '術語表無' if not g else ('同名' if g['zh'] == zh else '異名')
        out.append('\t'.join([str(page), kind, en, zh, g['zh'] if g else '', g['source'] if g else '', res]))
open(a.out, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
from collections import Counter
print(len(out) - 1, Counter(l.split('\t')[-1] for l in out[1:]), Counter(l.split('\t')[1] for l in out[1:]))
