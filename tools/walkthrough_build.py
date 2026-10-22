#!/usr/bin/env python3
"""由雜誌攻略轉錄（reference/walkthrough-zh/softworld-*.md）產生 text/walkthrough.zh-TW.tsv（克萊恩英豪規格 008）。

由克萊恩英豪 tools/walkthrough_build.py 移植：來源改為《軟體世界》第 21–25 期，沒有 SSI 提示書；
章與地圖依出現順序排列，讓各章的地圖圖例緊接在該章之後。
- `## 第 N 章 標題`、`## 結語` 開新章；正文段落（空行分隔）照錄，跨頁接續。
- 地圖圖例另成一段「地圖：名稱」：`> 地圖：名稱。…`、短的 `> 圖說：名稱` 開新圖，其後的引用列是圖例條目；
  `--map-pages` 指定的雜誌頁整頁都是地圖（第 30 期轉錄成一般列），頁首第一列是圖名、`N.` 列是條目。
- 刪去頁首重複的雜誌標題、作者署名、待續、HTML 註解。
輸出欄位 chapter（1 起連號）、title、body（段落以字面 \\n 分隔）、source（期數與雜誌頁碼）。
"""
import argparse
import re
from pathlib import Path

PAGE = re.compile(r'<!-- page: .+?（雜誌頁碼 (\d+)） -->')  # 掃描檔名可能含空白，例「46 (1).jpeg」
CHAPTER = re.compile(r'^## (第 ?\d+ ?章|結語)\s*(.*)$')
SKIP = re.compile(r'^((解開)?銀色[匕七]首之謎.*|／.*|待續.*)$')
ITEM = re.compile(r'^\d+[.．]')
# 雜誌的異體字換成標準字，全形空白換半形（轉錄檔保留原貌）
NORM = str.maketrans({'爲': '為', '强': '強', '眞': '真', '裏': '裡', '啓': '啟', '脚': '腳', '着': '著', '衆': '眾', '‧': '·', '\u3000': ' ', '—': '－', '–': '-'})


def load_terms(path):
    """雜誌譯名 → 術語表譯名（text/walkthrough-terms.tsv：from、to、en、reason）。轉錄檔保留原貌，只在產生面板文字時換。

    from 等於 to 的列用來保護較長的字串（例「奧斯沃夫」不再被「奧斯沃」換成「奧斯沃夫夫」）。
    """
    if not path or not path.exists():
        return {}
    out = {}
    for line in path.read_text(encoding='utf-8').splitlines()[1:]:
        c = line.split('\t')
        if len(c) >= 2 and c[0]:
            out[c[0].translate(NORM)] = c[1]
    return out


def apply_terms(text, terms):
    """一次掃過、最長者優先，換過的字不再被換。單一註記的括號（例「卡拉瑪（Kalaman）」）保留原文；含逗號的括號是清單，照換。"""
    if not terms:
        return text
    pat = re.compile('( ?)(' + '|'.join(re.escape(k) for k in sorted(terms, key=len, reverse=True)) + ')( ?)')

    def sub(m):
        # 雜誌在英文名前後留的空白：換成中文後，旁邊不是英數字就去掉
        s = m.string
        lead = m.group(1) if m.start() > 0 and s[m.start() - 1].isascii() and s[m.start() - 1].isalnum() else ''
        tail = m.group(3) if m.end() < len(s) and s[m.end()].isascii() and s[m.end()].isalnum() else ''
        return lead + terms[m.group(2)] + tail
    parts = re.split(r'(（[^（），]*）)', text)
    return ''.join(p if i % 2 else pat.sub(sub, p) for i, p in enumerate(parts))


class Section:
    def __init__(self, title, issue, page):
        self.title, self.issue, self.pages, self.paras, self.cur = title, issue, [page], [], []

    def add_page(self, page):
        if page not in self.pages:
            self.pages.append(page)

    def line(self, text):
        self.cur.append(text)

    def end_para(self, force=False):
        # 跨欄、跨頁的斷句：段落沒有以句尾標點結束就接著下一列（轉錄時頁標記前後有空行）
        if self.cur and (force or ''.join(self.cur)[-1] in '。！？」』…）)：'):
            self.paras.append(''.join(self.cur))
            self.cur = []

    def source(self):
        p = self.pages
        span = f'p.{p[0]}' if len(p) == 1 else f'p.{p[0]}-{p[-1]}'
        return f'軟體世界 {self.issue} 期 {span}'


def build(path, issue, map_pages):
    chapters, maps, order = [], [], []
    chap = mp = None
    page = 0
    map_page_first = False
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = re.sub(r'<!--(?! page).*?-->', '', raw).strip()
        if m := PAGE.match(line):
            page = int(m.group(1))
            for s in (chap, mp):
                if s:
                    s.end_para()
            map_page_first = page in map_pages
            if chap and not map_page_first:
                chap.add_page(page)
            continue
        if not line:
            if chap:
                chap.end_para()
            if mp:
                mp.end_para()
            continue
        if SKIP.match(line):
            continue
        if m := CHAPTER.match(line):
            if chap:
                chap.end_para()
            head = m.group(1).replace(" ", "")
            chap = Section(f'{head}　{m.group(2).strip()}' if m.group(2).strip() else head, issue, page)
            chapters.append(chap)
            order.append(chap)
            continue
        if page in map_pages:  # 整頁地圖（一般列）
            if map_page_first and not line.startswith('>'):
                mp = Section(f'地圖：{line}', issue, page)
                maps.append(mp)
                map_page_first = False
                continue
            text = line.lstrip('> ').removeprefix('圖說：').strip()
            if mp and text and not text.startswith('KEY'):
                mp.line(text)
                mp.end_para(force=True)
            continue
        if line.startswith('>'):
            text = line.lstrip('> ').strip()
            if m := re.match(r'^地圖：([^。]+)', text):
                mp = Section(f'地圖：{m.group(1)}', issue, page)
                maps.append(mp)
                order.append(mp)
                continue
            body = text.removeprefix('圖說：').strip()
            if text.startswith('圖說：') and not ITEM.match(body) and len(body) <= 12:
                mp = Section(f'地圖：{body}', issue, page)
                maps.append(mp)
                continue
            if mp and body and not body.startswith('KEY'):
                mp.line(body)
                mp.end_para(force=True)
            continue
        if chap:
            chap.line(line)
    for s in order:
        s.end_para(force=True)
    return order


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True, type=Path, help='轉錄目錄')
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--terms', type=Path, help='雜誌譯名對照（text/walkthrough-terms.tsv）')
    a = ap.parse_args()
    terms = load_terms(a.terms)
    plan = [(f'softworld-{i}.md', i, set()) for i in range(21, 26)]
    rows = ['chapter\ttitle\tbody\tsource']
    n = 0
    for name, issue, map_pages in plan:
        for s in build(a.src / name, issue, map_pages):
            body = apply_terms('\\n'.join(p.replace('\t', ' ') for p in s.paras if p).translate(NORM), terms)
            if not body:
                continue
            n += 1
            # 章號與章名分開換詞：譯名前的空白不是英數字旁的空白，整段換會被吃掉
            head, sep, rest = s.title.partition('　')
            title = f'{head} {apply_terms(rest.translate(NORM), terms)}' if sep else apply_terms(head.translate(NORM), terms)
            rows.append(f'{n}\t{title}\t{body}\t{s.source()}')
    a.out.write_text('\n'.join(rows) + '\n', encoding='utf-8')
    print(f'{n} 段寫到 {a.out}')


if __name__ == '__main__':
    main()
