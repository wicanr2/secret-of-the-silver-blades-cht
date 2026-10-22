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

產品工具尚未建立，G2 完成 dosgolem 基線後補上。目前唯一驗證過的操作是在 Docker 內唯讀
盤點原始輸入：

```sh
test -f secret-of-the-silver-blades.zip && timeout 120 docker run --rm --network none -u "$(id -u):$(id -g)" --memory 512m --cpus 1 --pids-limit 64 \
  --log-opt max-size=10m --log-opt max-file=3 -v "$PWD:/in:ro" python:3.13-slim \
  python3 -I -c 'import zipfile; [print(i.file_size, i.filename) for i in zipfile.ZipFile("/in/secret-of-the-silver-blades.zip").infolist()]'
```

dosgolem 的通用入口是其 clone 內的 `tools/go.sh run ./cmd/probe ...`；參數與 scratch 層用法參考
克萊恩英豪 `CLAUDE.md`，本作設定檔名與入口 EXE 待 G1、G2 確認。

## 資料索引

| 項目 | 位置 |
|---|---|
| 原版遊戲（安裝器形式） | `secret-of-the-silver-blades.zip`（唯讀，不進 Git） |
| 軟體世界珍藏版 056 說明書 | `珍056-銀色匕首之謎.rar`（唯讀，不進 Git） |
| 英文手冊與手札 | `workplace/input/en-docs/`（G1 下載，不進 Git） |
| 研究工作區 | `workplace/`（gitignore） |
| dosgolem 隔離 clone | `workplace/dosgolem/`，adapter 在 `apps/sosb/`，推到本 repo 的 `dosgolem/sosb` |
| 主要參考 | 克萊恩英豪、黑暗之后、光芒之池說明書 corpus（皆只讀，見 `AGENTS.md` 第 4 節） |
