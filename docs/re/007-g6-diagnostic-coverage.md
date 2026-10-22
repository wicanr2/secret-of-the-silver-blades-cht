# 007 繁中接入：診斷路徑覆蓋

日期：2026-10-22。Issue：[#7](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/7)。路徑與定位見 [004](004-output-paths.md)。

## 譯文

| 表 | 筆數 | 來源 |
|---|---|---|
| `text/ui-text.zh-TW.tsv` | 891 | 658 筆與克萊恩英豪雜湊相同沿用；233 筆新譯（另 174 筆判為雜訊） |
| `text/ecl-text.zh-TW.tsv` | 1,498 | 22 批新譯（30 筆判為雜訊），使用者 2026-10-22 確認試譯文風 |
| `text/name.zh-TW.tsv` | 788 | 由 `text/glossary.tsv` 的怪物、人物、地名、物品、法術產生 |
| `text/journal.zh-TW.tsv` | 72 | 珍056 修正譯文（[006](006-journal-errata.md)） |
| `text/composed-templates.tsv`、`host-text.zh-TW.tsv` | 96、34 | 沿用克萊恩英豪，另加寶物訊息模板 |

合併由 `tools/translation_merge.py` 逐列驗 key 與格式；`tools/term_check.py` 擋舊譯與批次漂移（Umber Hulk 曾出現四種譯法，統一為「土巨怪」）。

## 覆蓋（dosgolem 收據，`cmd/sosb-overlay-shot -text-dir`）

診斷路徑：讀預建隊伍 → 開始冒險 → 查驗題（SILVER）→ 開場 → 鎮長對白 → 寶物 → 3D 冒險選單 → 紮營。

| 畫面 | 覆繪筆數 | 範圍外差異 |
|---|---|---|
| 隊伍選單 | 19 | 0 |
| 查驗題（含答案顯示） | 11 | 0 |
| 開場劇情 | 7 | 0 |
| 鎮長對白 | 16 | 0 |
| 寶物訊息 | 4 | 0 |
| 寶物選單 | 9 | 0 |
| 3D 冒險選單 | 20 | 0 |
| 營地選單 | 23 | 0 |

路徑上的印字盤點：路徑 A 未命中只剩數字（AC、HP、經驗值）與查驗題作答時逐字回顯的字母，路徑 B、C 與逐字程序全部命中。

## 本作與克萊恩英豪不同之處

| 項目 | 本作 | 證據 | 等級 |
|---|---|---|---|
| 角色紀錄性別欄 | +0x11F（0 男、1 女） | 原版 6 個預建角色檔只有 EPONA、MORGAINE 為 1；音譯後 EPONA 用女性用字「埃波娜」 | 強推論 |
| 預建角色名 | `Guy de Valois` 大小寫混合、結尾帶空白 | 路徑 A 盤點 | 已證實 |
| 寶物訊息 | `The party has found ` 與 `treasure!` 兩段組成 | 路徑 A 盤點 | 已證實 |

adapter 的名字規則改為接受大小寫混合，音譯一律以大寫查（dosgolem `dosgolem/sosb`）。

## 未做

- 正常玩家路徑（建角、存讀檔不殘字）、戰鬥、商店、神殿、訓練、地下城與其他地區的盤點。
- 手札面板的地圖則圖面。
