# 006 珍056 旅行手札錯譯校正

日期：2026-10-22。Issue：[#5](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/5)。來源見 [002](002-reference-sources.md)。

## 範圍

珍056 下冊第六章「旅行手札」第 1–72 則（下冊 p.27–57）對照 SSI 英文 Adventurer's Journal 第 1–72 則（英文手札 p.27–44）。
兩邊則號一一對應。說明書其餘章節（上冊操作說明、下冊戰鬥、魔法、怪物、法術）尚未對照。

## 方法

| 步驟 | 工具與產物 | 位置 |
|---|---|---|
| 英文逐字稿 | 第 1–37 則對頁面圖轉錄；第 38–72 則以 `tools/journal_en_ocr.py` 由 OCR 逐字座標組成草稿，對照時改看頁面圖 | `workplace/journal/en/` |
| 珍056 文字 | 第 41–72 則對頁面圖轉錄；第 1–40 則以 PaddleOCR（`tools/ocr_batch.py`，黑暗之后的 `dqk-ocr:ppocr5-r1` 映像與模型快取，唯讀掛載）加 `tools/zh_ocr_journal.py` 組成草稿，再對頁面圖校讀 | `workplace/journal/zh056/` |
| 逐則對照 | `tools/re/journal_pair.py` 並列兩邊；珍056 譯對的句子保留原文，只改錯處 | `workplace/journal/fix/` |
| 正式譯文 | `text/journal.zh-TW.tsv`（entry、title、body、source） | repo |
| 錯譯表 | `text/errata.tsv`，`tools/errata_check.py` 檢查 | repo |
| 舊譯殘留 | `text/term-avoid.tsv`，`tools/term_check.py` 檢查全部 `text/*.zh-TW.tsv` | repo |

修正原則：
- 意思錯、漏譯、主客顛倒、專名誤譯才改；語感上可接受的意譯保留珍056 原文。
- 珍056 留英文的人名地名（Eldamar、Oswulf、Derf、Vala、Marcus 等）依 `text/glossary.tsv` 換成中文，不逐則列入錯譯表。
- 「智慧之井」「知識之井」並存，統一為字面的「知識之井」。
- 題名「銀色匕首之謎」依使用者決定保留，正文的 Silver Blades 改譯「銀刃」。

## 統計

錯譯表 113 條：

| 類別 | 條數 |
|---|---|
| 誤譯 | 83 |
| 專名 | 17 |
| 錯字 | 5 |
| 漏譯 | 5 |
| 譯名不一致 | 2 |
| 語氣 | 1 |

## 系統性錯誤

| 原文 | 珍056 | 修正 | 影響 |
|---|---|---|---|
| Bane／Banite | 毒教、毒神、毒教士 | 班恩、班恩教徒 | 第 11、16、22、31、46、67 則；把神名當成「毒」 |
| Silver Blades | 銀色七首（「七」為「匕」的排印錯字）、銀色匕首 | 銀刃 | 第 18、53、56、63、67 則；Blade 不是匕首，是奧斯沃夫召集的英雄團 |
| clerk | 牧師 | 書記 | 第 51、69 則；疑與 cleric 混淆 |
| mad | 憤怒 | 瘋 | 第 64、67 則 |
| glowing mouse | 紅面關公、水落下的聲音 | 發光的老鼠 | 第 8、59 則；劇情伏筆被改掉，第 48 則揭曉時前後接不起來 |

## 影響劇情理解的誤譯

| 則 | 原文 | 珍056 | 修正 |
|---|---|---|---|
| 5 | extended our lower tunnels — and uncovered the monsters | 且避過怪物 | 結果挖出了怪物 |
| 13 | were nearly to the top when the Black Circle sprung their ambush | 幾乎避開黑圈幫所埋設的陷阱 | 就快到達頂端時，中了黑圈幫的埋伏 |
| 18 | I am now bound to this temple and cannot take the battle to them | 我現在準備趕到神殿去 | 我已被束縛在這座神殿，無法親自出戰 |
| 26 | the dungeons beneath the castle | 城堡上方的地下城 | 城堡下方的地下城 |
| 34 | He can possess anything of flesh | 它嗜吃肉類 | 它能附身在任何血肉之軀上 |
| 40 | General Strike—no work | 一般攻擊——無效 | 全面罷工——停工 |
| 42 | We have been cheated of our rightful place | 我們已騙取…… | 應有的地位被騙走了 |

## 未做

- 英文第 38–72 則的逐字稿仍是 OCR 草稿，英文版手札面板（多語系，G10）前要校讀成正式稿。
- 說明書其餘章節未對照。
