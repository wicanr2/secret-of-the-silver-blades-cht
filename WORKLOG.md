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

## 2026-10-22 G4 手札錯譯校正（#5）

- 查驗題：`START.EXE` 0xDCFC 題目表 30 筆，`tools/quiz_answers.py` 以含標題字序算出 30 題答案，長度全部相符（docs/re/005）。
- 轉錄分派 4 個子代理：英文第 1–37 則與珍056 第 41–72 則完成逐字轉錄；另兩個子代理以版權為由只交則號、標題與節錄。
  改由 OCR 補：英文用 `pdftotext -bbox-layout`（`tools/journal_en_ocr.py`），珍056 用黑暗之后的 PaddleOCR 映像與模型快取（唯讀掛載，`tools/ocr_batch.py`、`tools/zh_ocr_journal.py`），再逐頁對圖校讀。
- 逐則對照 72 則，產出 `text/journal.zh-TW.tsv`、`text/errata.tsv`（113 條）、`text/glossary.tsv`、`text/term-avoid.tsv`；`tools/errata_check.py`、`tools/term_check.py` 通過。
- 轉錄、OCR 與對照中間檔都在 `workplace/journal/`，含原文，不入 Git。

## 2026-10-22 G5 試譯（#6）

- 新增 `text/TRANSLATION-GUIDE.md`（改寫自克萊恩英豪）、`tools/font-dev.sh`（源泉圓體 16／24 格，Unifont 補字）、`tools/ecl_batches.py`；ECL 切成 22 批（`workplace/tr/ecl/`）。
- 試譯 ECL 第 01、02、06 批共 122 則（開場目標、新維地格里城鎮內、開場劇情），放 `workplace/tr/ecl/done/`；覆繪截圖 `workplace/probe/g5-trial/`，範圍外差異 0。
- 全量翻譯等使用者確認文風後再派批次。

## 2026-10-22 G5 全量翻譯與 G6 診斷路徑（#6、#7）

- 使用者確認試譯文風。ECL 19 批分給 6 個 sonnet 子代理、UI 4 批 1 個；交回後統一頭尾空白與漂移譯名，`tools/translation_merge.py` 合併 0 錯誤。
- 術語表併入克萊恩英豪的 AD&D 通用類別 491 筆（排除克萊恩專屬）；Gnome 改用「侏儒」（光芒之池），從禁用表移除「侏儒」。
- 沿用克萊恩英豪的名稱、選單母串工具、組句模板、前端文字表與音譯資料（CMUdict、維基英語人名譯音表；LICENSE 第 2 條 (d) 已列）。
- 角色紀錄性別欄判定 +0x11F；名字規則接受大小寫混合（`dosgolem/sosb`）。診斷路徑覆蓋見 `docs/re/007`。
- 使用者提供《軟體世界》第 21–25 期攻略掃描 22 張（`walkthrough/`），OCR 草稿在 `workplace/walkthrough-ocr/`。
- 一次等待迴圈用 `pgrep -f` 比對到自己而卡住，已停止；之後用背景通知等待。
- 勘誤：合併前對批次做的禁用詞替換是子字串取代，把 UI 兩列題名「銀色匕首之謎」換成「銀刃之謎」，已改回；`Secret Curse Exit` 的 Secret 改「本作」。
  教訓：禁用詞替換不得作用在題名列，替換後要另查題名。
- 新增 `docs/spec/000-index.md`：列出沿用的克萊恩英豪規格、本作差異與本作自己的狀態。

## 2026-10-22 G6–G8 收據、demo 中止、CPU 速度、字級、閃爍（#7、#8、#9、#13–#17）

- G8：《軟體世界》第 21–25 期 22 頁轉錄完成，`tools/walkthrough_build.py` 產生 40 段攻略；雜誌譯名依 `text/walkthrough-terms.tsv` 換成遊戲譯名，
  錯字以「雜誌誤植」列修正（docs/re/008）。地圖疊層位址 `DS:89CE`、`DS:89D7` 以記憶體比對與移動實測證實，17 塊地區依同號 ECL 區塊命名（docs/re/009）。
- G6、G7：sosb-play 冷開機冒煙、建角到開場、存讀檔、手札第 37 則自動彈出、攻略／手札／地圖面板互斥都有收據（docs/re/007）。
  修正記入手札片段的雙逗號；術語表補 40 個怪物名。
- 使用者新增需求：demo 可中斷（#13，規格 018 CONFORMED）、CPU 模擬速度（#14，規格 019 READY）、切換列字級（#15，規格 020 CONFORMED）、
  降低先露英文的閃爍（#16，docs/re/010）。切換列版面依使用者選定：倍率合成一項、速度只顯示倍率。
- 本作 CRT `Delay` 是 TP5 寫法，dosgolem 規格 429 擴充兩種寫法；1x 快轉開關雜湊相同。
- 無敵的位址仍是克萊恩英豪值，與 demo 控制共用寫入守衛後有寫錯位址的風險，先停用並開 #17。
- 使用者指示收據截圖抽樣即可；存讀檔與手札收據改為只在關鍵時點截圖。
- 一次收據的存檔目錄沒先建立，dockerd 以 root 建了空目錄頂替；已刪除該空目錄，腳本改為掛載前 `mkdir -p`。
- 勘誤：攻略對照曾把雜誌「12頭龍」「十六頭龍」換成「火焰九頭蛇」（依 ECL 原文只見 pyro-hydras）。怪物資料 `MON1CHA.DAX` 區塊 24、25 的名字是
  `12 HEADED HYDRA`、`16 HEADED HYDRA`，已改為「十二頭九頭蛇」「十六頭九頭蛇」。教訓：怪物譯名先查怪物資料檔，不只看 ECL 文字。
- 勘誤：demo 控制照搬幽靈騎士「進入點與返回點都是遠呼叫」的檢查，本作返回點是 `cmp`，綁定失敗、收據第一輪全數沒有控制紀錄。改為只檢查進入點。
  教訓：移植簽章條件前，先在本作執行期記憶體看實際位元組。
- 勘誤：切換列收據在第 1 格就設 32x，自動模式固定照設定倍率跑全程，1,200 格超過 10 分鐘逾時。改為最後 10 格才切倍率。
- demo 收據中止後只送一次空白加 `p`，訊息、行走兩組停在選單；原版中止後要經開頭圖、標題兩次按鍵。改為每隔 520 格送三次 `p`。

## 2026-10-23 不露原版：閃現量尺與殘影疊字（#16）

- 使用者把 #16 的目標從「降低」改為「完全不先露原版字或原版圖」，所有語言與 HD 模式都適用。新增規格 021，
  dosgolem 規格 202 加 §2.6 閃現量尺、§2.7 殘影疊字、§2.8 保留呈現（DRAFT，HD 用）。
- 量尺 `xlate.FlashAudit` 只比對呈現畫面與原版畫面：某格原版墨跡原樣呈現，8 格內同樣內容被替換，就是一次閃現。
  sosb-play `-flash-audit`；`tools/g16-flicker-probe.sh` 一律帶上。
- 量到 demo 戰鬥訊息區 55 格閃現：原版不經印字常式把同一段訊息整塊還原，sosb 偵測到呼叫外寫入就移除路徑 B 疊字。
  以殘影疊字修正（原版墨跡與某筆疊字顯示時完全相同就照畫），路徑 B 疊字另標 Early。修正後 demo 9000 格、手札＋鎮上 19000 格都是 0。
- 勘誤：殘影第一版只收 Layer 算過指紋的疊字，路徑 B 是 sosb 自管（Frozen）沒有指紋，修正前後同為 55 格。改為每幀替顯示中的疊字記下底下的原版內容。
  教訓：共用層的新機制要先列出哪些呼叫端繞過了它的狀態機（Frozen、直接改 `Layer.Stamps`）。
- 勘誤：背景收據跑的期間改了同一支腳本，bash 邊讀邊執行，結束時讀到半行，log 被截斷。之後背景跑中的腳本不改。
- HD：本作還沒有 HD 主題，HD 的閃現無法量測；保留呈現元件以合成資料測過，接進 sosb 等 G9。

## 2026-10-23 G9 HD 起步（#10）

- 使用者看過濾鏡比較頁後指示：不用濾鏡，依原版手繪重畫；生圖交 Codex，其餘由 Claude。規格 010 DRAFT。
- 盤點：TITLE 4、PIC 77 狀態（38 區塊）、BIGPIC 8；PIC4 區塊 6 的 7 幀與克萊恩英豪 `pic3-022@0..6` 逐位元組相同，可沿用。
- 證據：金庫店員 PIC1 區塊 83、神殿祭司 PIC1 區塊 82 在 (24,24)；標題 ＝ TITLE 2 背景＋TITLE 4 字樣 (40,40)，全幅逐色號相同。
- 工具：`tools/hd_inventory.py`、`hd_request.py`、`hd_prepare.py`，自克萊恩英豪複製 `dax_pics.py`、`hd_compare.py`、`hd_validate.py`。
- b01 四張由 Codex 內建 image_gen 各生一次，數值閘門全過，比較頁給使用者確認畫風。
- 一次 ffmpeg 濾鏡原型在 `--pids-limit 32` 下建立執行緒失敗（EAGAIN 顯示成濾鏡設定錯誤）；改 `-threads 1` 並放寬到 128。

## 2026-10-23 G9 第二階段：戰鬥圖層與 HD 不露原版（#10、#16）

- 盤點：地形 30、怪物 104、頭 25、身 128、效果 26、遭遇圖 83；頭身與效果全數與克萊恩英豪同色號，直接沿用（179 項）。
- demo 戰鬥 181 張畫面重驗格線 (8,8) 24 步長、0／8 互換、SPRIT 位置 `(24+8x, 24+8y)` 與 13→0；隊員在本作是 CPIC 圖示，頭身組合沒有畫面證據。
- 16 張圖集交 Codex 生圖，拆回後數值全過；遭遇圖 3 張單張重畫，其中 8×57 遠距小圖三次都不過色相閘門，維持原版。
- 呈現器對遭遇圖有前景下限，低於下限的一張會讓整個主題載入失敗；主題工具改為預先排除並註明。
- 3 倍＋HD demo 量到 118 格閃現，加 HD 鎖存與「直接畫確定的 HD 格」後為 0；HD 開關不影響原版記憶體雜湊。
- 審閱頁 `review/hd/` 擴充到 485 項。
