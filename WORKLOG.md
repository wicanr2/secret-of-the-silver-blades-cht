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

## 2026-10-22 G2 dosgolem 基線（#3）

- 由克萊恩英豪工作 clone 的 `champions-of-krynn-cht`（`8742fa9`，等於其遠端 `dosgolem/cok`）本機 clone 到 `workplace/dosgolem/`，
  開分支 `secret-of-the-silver-blades-cht`，repo-local 身分 `wicanr2@gmail.com`；歷史含前作的 `codex@openai.com` commit，未改寫。
  module cache 由克萊恩英豪 clone 複製，未開網路。
- 首次執行在文字模式問設定；`-dump-mem-at` 傾印 B8000 讀出各題。存檔路徑預設帶出 `C:\RICH2\SAVE\`，
  追到 `cmd/probe` 的 `-program-path` 被覆寫，修正為 `9112c61`，推到本 repo 的 `dosgolem/sosb`。
- 新增 `tools/g2-startup-receipt.sh`：冷啟動到標題存狀態，重播兩次到主選單，雜湊一致。見 `docs/re/003`。

## 2026-10-22 G3 輸出路徑盤點（#4）

- 以克萊恩英豪簽章在 `START.EXE` 找到路徑 A（0x571D）、逐字（0x55A7）、路徑 B（0x5879）；執行期段 `0650`。`fn_diff` 顯示同函式，DS 位移整體平移。
- dosgolem `apps/sosb` 由 `apps/cok` 複製，`cmd/sosb-play`、`sosb-overlay-shot`、`sosb-explore` 由對應 cok 指令複製；
  換簽章、游標 DS、逐字程序位移 `01E7`、pad 呼叫樣式 `9A 32 00`、`defaultDS 0EF2`；未驗常數標「克萊恩英豪值」。刪除只驗克萊恩英豪 HD 夾具的 4 個測試。
- 新增 `tools/ui_text_catalog.py`、`tools/ecl_text_catalog.py`、`tools/eten_font.py`、`tools/re/`（移植自克萊恩英豪），產生 `text/ui-text-events.tsv`、`text/ecl-text-events.tsv`。
- 新增 `tools/probe.sh` 與 `tools/g3-party-receipt.sh`。查驗題 2 題證實字序含標題（`SILVER`、`YULASH`），與克萊恩英豪不同。
- 覆繪驗證暫借克萊恩英豪的 `ui-text.zh-TW.tsv` 與倚天字型，放在 `workplace/text-src/trial/`、`workplace/font/placeholder-*`，不是本作譯文；開場 16 段試譯同放該處。
- 勘誤：G2 寫「不送鍵時標題後直接進主選單」不成立。當時 #400M 的主選單畫面來自另一次執行：scratch 已有 `blades.cfg`，
  原本要回答設定的 `212\r` 改被標題畫面吃掉而跳過標題。收據改為從標題狀態送 ` p`，主選單雜湊改為 `5fe4bff7…`；docs/re/003 已更正。
