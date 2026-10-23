#!/usr/bin/env python3
"""從珍056 轉錄草稿抽出「中文名（English）」對照，與本作術語表比對（G4「遊戲內指涉查證」，docs/re/006）。在 sosb-tools 容器內以 python3 -I 執行。

輸入 tools/zh_manual_draft.py 的草稿 TSV（cell、page、text、status）與 text/glossary.tsv（en、zh、category、source、note）。
英文只留字母、不分大小寫比對術語表的 en（OCR 常吃掉英文的空白，例 StormGiant）；複數 s 結尾查不到時再試單數。
輸出 TSV：cell、page、zh056、en、glossary_zh、category、result（同名、異名、術語表無）。
OCR 草稿未校對：中文名可能有錯字，列為異名的候選要對頁面圖確認後才寫進錯譯表。
"""
import argparse
import csv
import re
from pathlib import Path

PAIR = re.compile(r'([㐀-鿿·・]{1,12})\s*[（(]\s*([A-Za-z][A-Za-z\s\'’\-.]{1,40}?)\s*[)）]')


def read(p):
    with open(p, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--draft', required=True, type=Path)
    ap.add_argument('--glossary', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    a = ap.parse_args()
    norm = lambda t: re.sub(r'[^a-z]', '', t.lower())
    gl = {}
    for r in read(a.glossary):
        gl.setdefault(norm(r['en']), r)
    out, seen = ['cell\tpage\tzh056\ten\tglossary_zh\tcategory\tresult'], set()
    counts = {}
    for r in read(a.draft):
        text = r['text'].replace('\\n', '')
        for zh, en in PAIR.findall(text):
            en = re.sub(r'\s+', ' ', en).strip(" .-'")
            key = norm(en)
            g = gl.get(key) or (gl.get(key[:-1]) if key.endswith('s') else None)
            if (zh, key) in seen:
                continue
            seen.add((zh, key))
            res = '術語表無' if not g else ('同名' if g['zh'] == zh else '異名')
            counts[res] = counts.get(res, 0) + 1
            out.append('\t'.join([r['cell'], r['page'], zh, en, g['zh'] if g else '', g['category'] if g else '', res]))
    a.out.write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(f'{len(out) - 1} 組對照 → {a.out}；{counts}')


if __name__ == '__main__':
    main()
