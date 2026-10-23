#!/usr/bin/env python3
"""日文、韓文附表的翻譯輸入（#11，克萊恩英豪規格 015 §5）。在 sosb-tools 容器內以 python3 -I 執行。

組句模板、選單母串、前端文字：克萊恩英豪 <表>.<語言>.tsv 有同 key 的直接沿用（寫進 <work>/aux-<語言>/reuse-*.tsv），
其餘列進 <work>/aux-input/<表>.tsv 交給譯者。地圖名稱與地圖攻略點是本作專有，全部列入。
選單母串附英文詞（由 workplace/text-src/ui-text-source.tsv 的母串切詞）與格數上限。含原文，只放工作區。
"""
import argparse
import csv
import re
from pathlib import Path


def read(p):
    with open(p, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE))


def write(p, header, rows):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write('\t'.join(header) + '\n')
        for r in rows:
            assert not any('\t' in c or '\n' in c for c in r), r
            f.write('\t'.join(r) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--prior', type=Path, required=True, help='克萊恩英豪 text/（唯讀）')
    ap.add_argument('--work', type=Path, required=True)
    a = ap.parse_args()
    T, W = a.root / 'text', a.work
    src = {r['key']: r['original'] for r in read(a.root / 'workplace/text-src/ui-text-source.tsv')}
    inp = W / 'aux-input'
    # 組句模板
    # 沿用前作譯文的條件：同 key，而且前作的繁中與本作相同（本作改過繁中的列重譯，例：guide.toc 的題名）
    zt = read(T / 'composed-templates.tsv')
    pzt = {(r['template'], r['translation']) for r in read(a.prior / 'composed-templates.tsv')}
    same = {r['template'] for r in zt if (r['template'], r['translation']) in pzt}
    for L in ('ja', 'ko'):
        prior = {r['template']: r['translation'] for r in read(a.prior / f'composed-templates.{L}.tsv')}
        write(W / f'aux-{L}' / 'reuse-composed-templates.tsv', ['template', 'translation'],
              [[r['template'], prior[r['template']]] for r in zt if r['template'] in prior and r['template'] in same])
    pj = {r['template'] for r in read(a.prior / 'composed-templates.ja.tsv')} & same
    write(inp / 'composed-templates.tsv', ['template', 'zh', 'note'],
          [[r['template'], r['translation'], r.get('note') or ''] for r in zt if r['template'] not in pj])
    # 選單母串
    zm = read(T / 'menu-masters.tsv')
    pz = {(r['master'], r['index'], r['translation']) for r in read(a.prior / 'menu-masters.tsv')}
    same_m = {(r['master'], r['index']) for r in zm if (r['master'], r['index'], r['translation']) in pz}
    for L in ('ja', 'ko'):
        prior = {(r['master'], r['index']): r['translation'] for r in read(a.prior / f'menu-masters.{L}.tsv')}
        write(W / f'aux-{L}' / 'reuse-menu-masters.tsv', ['master', 'index', 'translation'],
              [[r['master'], r['index'], prior[(r['master'], r['index'])]] for r in zm
               if (r['master'], r['index']) in prior and (r['master'], r['index']) in same_m])
    pm = {(r['master'], r['index']) for r in read(a.prior / 'menu-masters.ja.tsv')} & same_m
    rows = []
    for r in zm:
        if (r['master'], r['index']) in pm:
            continue
        words = re.split('[ @]', src[r['master']])
        rows.append([r['master'], r['index'], words[int(r['index'])], r['translation'], r['original_length'], src[r['master']]])
    write(inp / 'menu-masters.tsv', ['master', 'index', 'en', 'zh', 'max_cells', 'en_line'], rows)
    # 前端文字
    zh = read(T / 'host-text.zh-TW.tsv')
    pzh = {r['key']: r['translation'] for r in read(a.prior / 'host-text.zh-TW.tsv')}
    same_h = {r['key'] for r in zh if pzh.get(r['key']) == r['translation']}
    for L in ('ja', 'ko'):
        prior = {r['key']: r['translation'] for r in read(a.prior / f'host-text.{L}.tsv')}
        write(W / f'aux-{L}' / 'reuse-host-text.tsv', ['key', 'translation'],
              [[r['key'], prior[r['key']]] for r in zh if r['key'] in prior and r['key'] in same_h])
    ph = {r['key'] for r in read(a.prior / 'host-text.ja.tsv')} & same_h
    write(inp / 'host-text.tsv', ['key', 'zh', 'note'],
          [[r['key'], r['translation'], r.get('note') or ''] for r in zh if r['key'] not in ph and r['key'] not in ('journal.ref', 'journal.refdot')])
    # 地圖名稱、地圖攻略點
    write(inp / 'map-titles.tsv', ['map', 'zh'], [[r['map'], r['title']] for r in read(T / 'map-titles.tsv')])
    write(inp / 'map-guide.tsv', ['map', 'n', 'x', 'y', 'label', 'summary', 'source'],
          [[r[c] for c in ('map', 'n', 'x', 'y', 'label', 'summary', 'source')] for r in read(T / 'map-guide.zh-TW.tsv')])
    for p in sorted(inp.glob('*.tsv')):
        print(p.name, sum(1 for _ in open(p, encoding='utf-8')) - 1, '列待譯')
    for L in ('ja', 'ko'):
        for p in sorted((W / f'aux-{L}').glob('reuse-*.tsv')):
            print(L, p.name, sum(1 for _ in open(p, encoding='utf-8')) - 1, '列沿用')


if __name__ == '__main__':
    main()
