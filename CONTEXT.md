# 目前真相

更新：2026-10-22（Asia/Taipei）。規則見 [AGENTS.md](AGENTS.md)，歷程見 [WORKLOG.md](WORKLOG.md)。

## 儲存庫

| 項目 | 值 | 回讀方式 |
|---|---|---|
| 網址 | <https://github.com/wicanr2/secret-of-the-silver-blades-cht> | `gh repo view --json url` |
| owner | `wicanr2` | `gh auth status`、`gh repo view --json owner` |
| 可見性 | PRIVATE | `gh repo view --json visibility` |
| Issues | 啟用 | `gh repo view --json hasIssuesEnabled` |
| git 身分 | repo-local `wicanr2` <wicanr2@gmail.com> | `git config user.email` |
| 授權 | RRSAL-1.0（[LICENSE](LICENSE)） | |

## 有效決策

| 日期 | 決策 | 來源 |
|---|---|---|
| 2026-10-22 | 參考克萊恩英豪，用 dosgolem 執行原版並覆繪繁中；整合介面一律 dosgolem，不另建 remake 引擎 | 使用者指示 |
| 2026-10-22 | 範圍整個比照克萊恩英豪，定案表見 AGENTS.md 第 1 節 | 使用者回答 |
| 2026-10-22 | 中文題名沿用「銀色匕首之謎」；Blades 與「匕首」的落差只記入術語表 | 使用者回答 |
| 2026-10-22 | 錯譯修正對象是珍056 軟體世界說明書；英文手冊與手札授權上網取得 | 使用者回答 |
| 2026-10-22 | 修正後的說明書手札放進遊戲，比照克萊恩英豪自動彈出與翻閱 | 使用者指示 |
| 2026-10-22 | repo `secret-of-the-silver-blades-cht`；遊戲短名 `sosb`，adapter 在 dosgolem `apps/sosb/`，分支推到本 repo 的 `dosgolem/sosb` | 使用者回答 |
| 2026-10-22 | HD 可由 Codex 輔助，比照克萊恩英豪整條交 Codex | 使用者指示 |

## 待定

| 項目 | 何時決定 |
|---|---|
| dosgolem 基底（`dosgolem/cok` 或 dosgolem `main` 線），AGENTS.md 第 5 節 | G2 |
| 攻略來源：雜誌掃描是否提供，或以 SSI 提示書補 | G8 開工前 |

## dosgolem 基線

尚未建立。

## 中文化進度

尚未開始。沒有本作的執行收據。

## 原始輸入

| 檔案 | 狀態 |
|---|---|
| `secret-of-the-silver-blades.zip` | SHA-256 `b3147db0…29f7`；成員為安裝器（`install.com`、`secret1.exe`、`secret2.exe`）與兩個 txt；未解壓 |
| `珍056-銀色匕首之謎.rar` | SHA-256 `5ac3f9c9…c7dc`；說明書 PDF、4 張 JPG、補完計劃 txt；未解壓 |
| 英文手冊與手札 | 未取得 |

## Glossary

- 銀色匕首之謎：本作中文題名，沿用珍056，使用者指定。
- 珍056：軟體世界珍藏版第 56 號，本作的官方繁中說明書，錯譯修正的對象。
- 錯譯表：`text/errata.tsv`，記錄珍056 譯文與修正譯文的對照與證據。
- 手札：說明書中 Adventurer's Journal 的段落，遊戲內以編號引用。_Avoid_：日誌、日記
- sosb：本作遊戲短名，用於 dosgolem `apps/sosb/` 與程式識別。
- 克萊恩英豪：第一參考專案，本機 `/home/anr2/cht/golden_box/champions_of_krynn/`，短名 `cok`。
- 覆繪：在原版已輸出的畫面上清除原文墨跡、重畫中文。_Avoid_：替換、打字串補丁
- 收據：dosgolem 以固定輸入重播產生、可重現的執行證據。_Avoid_：截圖證明
- HD 批次：一組交給 Codex 重繪的原版圖塊，含請求與輸出兩個目錄。

### 待定譯名

- Silver Blades：遊戲內指涉待 G4 查證；題名不改，內文譯名另定。

### Flagged ambiguities

- 本機目錄名 `secret-of-the-sliver-blader` 拼錯（sliver、blader），與 repo `secret-of-the-silver-blades-cht` 指同一專案，不改名。
