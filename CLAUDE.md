# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

所有工作規則以 [`AGENTS.md`](AGENTS.md) 為單一權威。本檔只保留使用者最初需求、常用指令與資料索引。
目前狀態見 `CONTEXT.md`（G0 建立）。

## 原始目標（2026-10-22）

1. 參考 `/home/anr2/cht/golden_box/champions_of_krynn/`（克萊恩英豪），用 dosgolem 執行原版 DOS
   《Secret of the Silver Blades》，以輸出攔截覆繪繁體中文化；整合介面一律用 dosgolem。
2. 把原版素材做成 HD，可用 Codex 輔助（`AGENTS.md` 第 6 節）。
3. 建立 private GitHub 儲存庫 `secret-of-the-silver-blades-cht`，Issue 先行。
4. 修正軟體世界珍藏版 056 說明書的錯譯，英文原文上網取得（`AGENTS.md` 第 3.1、3.2 節）；
   修正後的手札放進遊戲，不必再查說明書。
5. 範圍整個比照克萊恩英豪（`AGENTS.md` 第 1 節定案表）。

## 常用指令

全部在 Docker 內執行，腳本開頭的註解說明前置條件。

| 用途 | 指令 |
|---|---|
| 重建字型（含切換列 12、22 像素） | `tools/font-dev.sh` |
| 開繁中視窗試玩（需主機 X11） | `tools/play.sh` |
| 無頭冒煙：冷開機到主選單 | `tools/play-smoke.sh` |
| 建角到開場、存讀檔、手札與面板收據 | `tools/g6-create-receipt.sh`、`tools/g6-saveload-receipt.sh`、`tools/g7-journal-receipt.sh` |
| 攻略面板、demo、切換列、速度等價性 | `tools/g8-guide-receipt.sh`、`tools/g13-demo-receipt.sh`、`tools/g14-toolbar-receipt.sh`、`tools/g14-delay-equiv.sh` |
| 閃爍逐格量測 | `FROM=… TO=… tools/g16-flicker-probe.sh`，再以 `tools/g16_flicker_scan.py` 掃描 |
| 文字檢查 | `tools/term_check.py`、`tools/errata_check.py`（在 `sosb-tools:bookworm-r1` 內以 `python3 -I` 執行） |

dosgolem 的建置與測試走其 clone 內的 `tools/go.sh`（例：`tools/go.sh test ./apps/sosb/`；需要 X 的套件加
`DOSGOLEM_GO_CMD=xvfb-run tools/go.sh -a go test …`）；自動模式跑 sosb-play 時 `docker run` 要帶 `--init`。

## 資料索引

| 項目 | 位置 |
|---|---|
| 原版遊戲（安裝器形式） | `secret-of-the-silver-blades.zip`（唯讀，不進 Git） |
| 軟體世界珍藏版 056 說明書 | `珍056-銀色匕首之謎.rar`（唯讀，不進 Git） |
| 英文手冊與手札 | `workplace/input/en-docs/`（G1 下載，不進 Git） |
| 研究工作區 | `workplace/`（gitignore） |
| dosgolem 隔離 clone | `workplace/dosgolem/`，adapter 在 `apps/sosb/`，推到本 repo 的 `dosgolem/sosb` |
| 主要參考 | 克萊恩英豪、黑暗之后、光芒之池說明書 corpus（皆只讀，見 `AGENTS.md` 第 4 節） |
