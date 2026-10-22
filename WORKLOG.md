# 工作歷程

## 2026-10-22 G0 啟動

- 目標：依使用者指示，參考克萊恩英豪建立治理文件、private 儲存庫與初始 Issues。
- 讀取：克萊恩英豪 `AGENTS.md`、`CLAUDE.md`、`CONTEXT.md`、`README.md`、`.gitignore`、`LICENSE`；黑暗之后 `AGENTS.md`；
  光芒之池 `CONTEXT.md` 的說明書 corpus 段落。
- 原始輸入：在 `python:3.13-slim`（`--network none`、唯讀掛載）內計算兩個壓縮檔 SHA-256，列出 zip 成員，
  以 RAR 4 標頭解析列出 rar 成員。未解壓。
- 使用者決定：錯譯對象是珍056 說明書，授權上網抓英文版；題名沿用「銀色匕首之謎」；範圍先選黑暗之后模式，
  後改為整個比照克萊恩英豪，修正後手札放進遊戲；repo `secret-of-the-silver-blades-cht`、短名 `sosb`。
- dosgolem 候選以 `git for-each-ref` 回讀：克萊恩英豪 `origin/dosgolem/cok` `8742fa9`；dosgolem `main` `81c85be`、
  `san5-mixer` `f79eab6`。
- 變更：新增 `AGENTS.md`、`CLAUDE.md`、`.gitignore`、`LICENSE`（由克萊恩英豪 RRSAL-1.0 改填本作名稱、網址、權利人與灰色地帶）、
  `CONTEXT.md`、`WORKLOG.md`、`README.md`。
- GitHub：`gh auth status` 為 `wicanr2`；同名 repo 不存在；建立 private repo 並推送，回讀 PRIVATE、Issues 啟用；建立 #1–#12（G0–G11），連結回填 AGENTS.md 第 2 節。
- 清理：容器皆 `--rm`，未寫入本目錄。

## 2026-10-22 G1 原始輸入盤點（#2）

- 新增 `tools/docker/tools.Dockerfile`（Debian bookworm 固定 digest，加 python3、unzip、unar、poppler-utils、curl），建 `sosb-tools:bookworm-r1`
  （`sha256:b9b6c754…`）。建置時開網路。
- 新增 `tools/inventory.py`：兩個 PKSFX 用 implode，`zipfile` 不支援，改用 Info-ZIP `unzip`；展開 49 檔到 `workplace/input/dos/sosb/`。
  結果見 `docs/re/001-input-baseline.md`：v1.30，`START.EXE`＋`GAME.OVR`（`TPOV`），設定檔 `blades.cfg`，查驗題問手札字與規則書頁碼。
- 珍056 以 `unar -e cp950` 展開；PDF 24 頁、無文字層，旅行手札第 1–72 則在下冊 p.27–57；第 24 頁是英文同人地圖。見 `docs/re/002`。
- 依使用者授權從 mocagh.org 下載 journal、manual、refcard、hintbook、errata（容器開網路一次），`pdftotext -layout` 轉文字。
- LICENSE 灰色地帶補上「為辨識版本與查驗題引用的少量原版英文字串」與檔名清單；`.gitignore` 補 `*.DAT`、`*.SFX`、`ITEMS`。
- 清理：容器皆 `--rm`；`workplace/` 無 root 擁有檔（見下行檢查）。
