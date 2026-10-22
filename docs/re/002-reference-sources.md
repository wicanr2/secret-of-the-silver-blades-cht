# 002 參考文件來源

日期：2026-10-22。Issue：[#2](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/2)。
原檔與轉出物都在 `workplace/`，不進 Git。

## 珍056 中文說明書

`珍056-銀色匕首之謎.rar` 以 `unar -e cp950` 展開到 `workplace/input/manual-zh/`。

| 成員 | SHA-256 | 內容 |
|---|---|---|
| `遊戲手冊：銀色匕首之謎.pdf` | `4e040c3a1ec1e0d639d56775a9584e6e7cfc99d18e4bfa77ab0668be718840a7` | 24 頁 A4，2009-03-15 由骨灰集散地「軟體世界說明書補完計劃」以 Acrobat Distiller 製作；1-bit 450 dpi 掃描，無文字層 |
| `Pic0001.jpg`–`Pic0004.jpg` | 見 `workplace/input/manual-zh/` 的 sha256sum | 彩色掃描，1112–1252 像素見方，未逐張判讀 |
| `軟體世界說明書補完計劃.txt` | `3bc86e70db33f651652d8ee59595db6e5a3448a5f48d94751eceb09979bf3916` | 補完計劃說明（CP950） |

PDF 每頁拼 4 到 6 個手冊頁。頁面圖以 `pdftoppm -r 110 -gray` 轉到 `workplace/manual-zh/pages/`。

| 冊 | PDF 頁 | 內容 |
|---|---|---|
| 上冊（文字編輯柯志祥） | 1–13 | 目錄：前言、英雄的來臨、硬體配備、載入硬碟／載入軟碟、啟動遊戲、控制方法、進入遊戲、人物與冒險隊伍、如何創設一支無敵勁旅、各種場合解說、密碼表（p.49）、附錄（經驗等級表到 p.74） |
| 下冊（文字編輯黃啓禎、謝明奇） | 14–23 | 目錄：戰鬥、魔法、魔法寶藏、被遺忘國王內的生物、法術、旅行手札（p.27–57，第 1–72 則，含地圖） |
| 附加 | 24 | Andrew Schultz 的英文地圖（城堡、地城、礦坑、廢墟），不屬於說明書 |

## SSI 英文文件（mocagh.org）

2026-10-22 下載到 `workplace/input/en-docs/mocagh/`，網址 `https://www.mocagh.org/ssi/<檔名>`，
遊戲頁 `https://www.mocagh.org/loadpage.php?getgame=ssb`。全部是掃描加 Acrobat Paper Capture OCR，文字可用但有辨識錯誤；
`pdftotext -layout` 輸出在 `workplace/reference-src/txt/`。

| 檔案 | SHA-256 | 頁數 | 用途 |
|---|---|---|---|
| `ssb-journal.pdf` | `983525550d3d148a146c7201bd87531e34aae8f70fb31777503fef1fdf340280` | 33 | Adventurer's Journal：錯譯對照、查驗題答案 |
| `ssb-manual.pdf` | `b7a286c2362429495d1daff89c01b08824dbed3e18b0f55ec4c9224c8dee6cfd` | 9 | Rulebook：查驗題的規則書頁碼 |
| `ssb-refcard.pdf` | `b6063f25cb829ad8d6d3bd8fa6030e07f1b8f2c036a96fbaca6c1c6b8cc09128` | 4 | IBM 資料卡 |
| `ssb-hintbook.pdf` | `72b5c4e327b6e76af42d0fecfd40f5068fa8230106d4e75eca6805d95e8bb871` | 33 | 官方提示書：攻略面板缺來源時的補充 |
| `ssb-errata.jpg` | `53f7febe873eb2acd77bb2787ee7256f956b235435083bf3f55c408082d834cc` | 1 | 勘誤單，內容是從《青色枷的詛咒》轉移角色，與手札無關 |

英文手札版面多欄，OCR 會跨欄混排，轉錄時要對照頁面圖。
