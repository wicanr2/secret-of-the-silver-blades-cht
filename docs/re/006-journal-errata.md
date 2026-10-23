# 006 珍056 旅行手札錯譯校正

日期：2026-10-22。Issue：[#5](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/5)。來源見 [002](002-reference-sources.md)。

## 範圍

珍056 下冊第六章「旅行手札」第 1–72 則（下冊 p.27–57）對照 SSI 英文 Adventurer's Journal 第 1–72 則（英文手札 p.27–44）。
兩邊則號一一對應。說明書其餘章節（上冊操作說明、下冊戰鬥、魔法、怪物、法術）尚未對照。

## 方法

| 步驟 | 工具與產物 | 位置 |
|---|---|---|
| 英文逐字稿 | 第 1–37 則對頁面圖轉錄；第 38–72 則以 `tools/journal_en_ocr.py` 的 OCR 草稿為底，逐欄對頁面圖（`en-cols/p35`–`p44`）校讀成正式稿；`tools/journal_en_build.py` 合併成 `text/journal.en.tsv` | `workplace/journal/en/` |
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

## 說明書其餘章節

### 轉錄草稿

珍056 PDF 第 1–17 頁與第 18 頁上半（上冊全部、下冊 p.1–26）以 300 dpi 重轉（`pdftoppm -r 300 -gray`），
`tools/zh_manual_split.py` 依 3×2 拼版切成 106 格，PaddleOCR（同上，`dqk-ocr:ppocr5-r1`）逐格辨識，
`tools/zh_manual_draft.py` 組成逐格草稿 `workplace/manual-zh/ocr-draft.tsv`（不進 Git）。

校讀：6 批 sonnet 校讀者依 `workplace/manual-zh/proof/PROMPT.md` 逐格對頁面圖轉錄（簡體字形改回、原書錯字照留、
看不清寫〔?〕），`tools/zh_manual_merge.py` 合併成 `workplace/manual-zh/zh056-transcript.tsv`（106 格，約 11.5 萬字，不進 Git）。
頁碼取自各格頁尾；上冊 p.49–50 的密碼表是跨頁表格、沒有頁尾頁碼，左半記 49、右半記 50。
合併檢查：上冊 1–74、下冊 1–26 每頁都有，加上手札頁（下冊 27–57），珍056 轉錄頁碼連續。〔?〕共 7 處，都在螢幕擷圖裡。
校讀者回報的原書錯字（記憶→記術、體質→體值、兼職者→兼值者、True→Ture、Disintigrate、Fresh to Stone、Mammel 等）照原書保留，
不列入錯譯表（錯譯表只收譯文錯誤）。

上冊多半是安裝、硬體、控制與珍056 自撰的建隊建議，英文規則書沒有對應段落，錯譯無從比對；
對得上英文的是選單說明、戰鬥、魔法與法術、怪物章節。

### 遊戲內指涉查證（下冊怪物 p.9–14、法術 p.14–25）

`tools/zh056_names.py` 抽出條目行首的「中文名（English）」，OCR 錯字依頁面圖更正後與 `text/glossary.tsv` 比對，
結果在 `text/zh056-names.tsv`（只有名稱）：131 組，同名 54、異名 63、術語表沒有 14。術語表沒有的 14 筆中，8 筆在遊戲文字來源找得到（法術選單字串，如 Hold Monster、Charm Monster、Find Traps；ECL 的 Lizard Men），是術語表缺列；4 筆是珍056 的英文拼法與遊戲不同（Protect From Good、Disintigrate、Fresh to Stone、Charm Person or Mammel）；Megalo-Centipede、Warg 在遊戲文字來源裡查不到。

異名的來源：遊戲內譯名多數沿用克萊恩英豪（法術是共通機制）或光芒之池、青色枷，當時下冊章節還沒轉錄。
珍056 譯名本身有明顯錯誤的：

| 英文 | 珍056 | 遊戲內 | 問題 |
|---|---|---|---|
| Storm Giant | 狂暴巨人 | 風暴巨人 | Storm 是風暴，不是狂暴 |
| Cloud Giant | 煙霧巨人 | 雲巨人 | Cloud 是雲 |
| Ogre | 巨魔 | 食人魔 | 巨魔通常對應 Troll |
| Umber Hulk | 地底熊 | 土巨怪 | 不是熊 |
| Mastodon | 長毛象 | 乳齒象 | 長毛象是猛瑪象 |
| Gargoyle／Margoyle | 石像怪／石像鬼 | 石像鬼／大石像鬼 | 兩者的慣用名對調 |

其餘多是同一物的不同譯法（驚獅（原書如此，疑為鷲獅）／獅鷲、鷹頭馬／鷹馬、地獄之犬／地獄獵犬、引起輕傷／引發輕傷等）。
AGENTS.md 第 3.3 節的譯名優先序把珍056 放在前作之前，是否把遊戲內譯名改成珍056 的說法待使用者決定（WORKLOG 2026-10-23）；
改名會連動简中、攻略用語、地圖攻略點與日韓的術語表依據。

## 未做

- 說明書其餘章節已轉錄校讀，錯譯只比對了下冊怪物與法術的名稱（`text/errata-manual.tsv` 7 條，`tools/errata_check.py` 一併檢查）；
  上冊的選單、戰鬥、魔法說明與英文規則書逐段對照未做。
