# 005 手冊查驗題題目表

日期：2026-10-22。Issue：[#5](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/5)、[#8](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/8)。
題目的輸出路徑與字序見 [004](004-output-paths.md)。

## 題目表（已證實）

`START.EXE` 0xDCFC 起 30 筆、每筆 5 bytes，到 0xDD92 結束：

| byte | 意義 | 證據 |
|---|---|---|
| 0 | 語意未確認（第 2 筆起單調遞增，第 1 筆為 8） | 未知 |
| 1 | 第幾個字 | 實機題目「word # 4 of journal entry # 18 (journal, page 30)」對到 `04 12 1E` |
| 2 | 第幾則 | 同上 |
| 3 | 英文手札頁碼（28–44） | 同上；第 47 則一筆對到實機第 37 頁 |
| 4 | 答案字母數 | SILVER、YULASH 皆為 6；30 筆全部與逐字稿算出的長度相符 |

`tools/quiz_answers.py` 以「第 18 則第 4 字第 30 頁長度 6」找唯一錨點，前後延伸到欄位不合範圍為止，不寫死檔案位置。
第 1 筆 `(8, 5, 3, 28, 5)` 的答案 `BLACK` 長度相符，算作有效題目。

## 答案（text/quiz-answers.tsv）

- 字序從標題第一個字算起；只含標點的記號（如 `—`）不算字；答案取字中的英數字轉大寫。
- 英文手札來源：第 1–37 則是對頁面圖的逐字轉錄，第 38–72 則是 OCR 逐字座標組出的草稿（`tools/journal_en_ocr.py`），
  兩者都在 `workplace/journal/en/`。30 題的答案長度全部與題目表相符。
- 實機作答通過 2 題：第 30 頁第 18 則第 4 字 `SILVER`、第 37 頁第 47 則第 3 字 `YULASH`（`tools/g3-party-receipt.sh`）。

## 與克萊恩英豪的差異

| 項目 | 本作 | 克萊恩英豪 |
|---|---|---|
| 位置 | `START.EXE` 0xDCFC | `START.EXE` 0xB99A |
| 筆數 | 30 | 49 |
| 字序 | 含標題 | 正文第一個字起算 |
| 題型 | 只有手札（規則書題型字串存在但未見於表中） | 手札與酒店傳聞 |
