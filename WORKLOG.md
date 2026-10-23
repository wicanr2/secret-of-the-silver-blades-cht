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

## 2026-10-23 G9 第三階段：3D 牆面與天空（#10）

- 克萊恩英豪的 WALLDEF 符號定位規則在本作成立（950 布局有 923 個完整定位）；背景模型為天空色＋SKY 252 地面 (0,40)，鎮上 3D 121 格全可重建。
- 牆面 1,250 圖塊：748 沿用前作或純色，502 以 8 張圖集生圖；結構不足的 20 個改 4×4、最後 4 個改 2×2 重畫後全過。
- 地面第一輪畫成圓卵石，明寫長方形石板後通過。遠山 88×16 三次都畫小（灰色山與灰色遮罩分不清，改洋紅遮罩仍失敗），本作未觀測，維持原版。
- `walls.json`：通用格 2,053、位置格 152。demo 與鎮上 3 倍＋HD 閃現 0，鎮上 3D 視窗非純色格全為 HD。
- 審閱頁加入牆面拼圖頁與天空，共 1,738 項。

- 勘誤：產生 HD 審閱頁時沒先建 `review/hd` 就掛進 Docker，dockerd 以 root 建了空目錄；確認為空後已移除。這是本專案第二次同類失誤（前一次是存讀檔收據的存檔目錄）。
  教訓：腳本與一次性指令都在 `docker run` 前對每個 `-v` 的可寫目標 `mkdir -p` 並 `test -d`，不靠記得。
- HD 主題以 `tools/hd_sync.py` 同步到 repo 的 `hd/theme/`（3,477 檔，42 MB，只帶 JSON 引用的檔），沿用克萊恩英豪的位置與 AGENTS.md 第 3 節例外；
  `g16-flash-receipt.sh` 加 `HD=1` 的 3 倍＋HD 輪。

## 2026-10-23 G7 手札地圖頁與『』字形（#8）

- 使用者指示依序做 G6、G7、G8、G4、G10，做完再抽驗。
- 12 則地圖手札改顯示圖面（規格 022）：英文手札第 16–24 頁 300 dpi 裁圖，只留深藍墨線，抹掉英文標籤與圖例，中文標籤畫回原位、圖例改列右欄；
  高瘦的 4 張切成兩頁，共 16 頁。標籤座標與譯文在 `text/journal-maps.zh-TW.tsv`，圖檔由原版衍生，放 `workplace/journal/maps/zh-TW/`，不進 Git。
- dosgolem `2d914f7`：`LoadJournalMaps`、地圖頁面板 [8,312)×[8,192)、`-journal-maps`。收據 `tools/g7-journal-maps-receipt.sh`（第 1 則兩頁、第 32、72 則）。
- 『』在 16 格 50% 門檻下雙線斷成幾個點（第 64 則），`tools/rounded_font.py` 對這兩字改用 80 門檻後重建字型。
- 勘誤：新表的欄名用 `zh`，`tools/font-dev.sh` 掃 `text/*.tsv` 時找不到顯示欄而中止；改名 `label`。

## 2026-10-23 G8 地圖攻略點（#9）

- 雜誌地圖有 0–15 格線座標軸，從掃描圖讀出圖例編號的格子：新維地格里城、知識之井、黑圈幫總部、半蜘精靈基地、寒霜巨人村、孿生城堡三層，共 8 張 298 點（`text/map-guide.zh-TW.tsv`）。
- 鎮上與知識之井在遊戲內核對：開場 3,3、傳送點 3,0、傳送後 1,1 都與雜誌編號相符；疊層地圖名稱「知識之井」證實 GEO 1/21。其餘 6 張未到現場核對。
- 寒霜巨人村的雜誌座標是 69–84、80–95，表中減去位移（推論）。礦坑與地下城多層共用 GEO，待找分層指標再放。
- 雜誌「銀行」「魔法店」依招牌改「金庫」「魔法商店」，攻略面板重建。

## 2026-10-23 #17 我方無敵

- 記憶體傾印（鎮上、換選取、建角、demo 戰鬥）找出串列頭 `DS:7D3C`、目前角色 `DS:7D38`；紀錄 0x1B7 bytes，尾端欄位比克萊恩英豪多 0x1E，效果串列頭 +0xFB（docs/re/012）。
- dosgolem `9d2f4f2` 開啟 `CheatVerified`；`tools/g10-cheat-receipt.sh` 通過（還原 6 次，隊員 HP 與狀態不變）。
- 勘誤：`cmd/probe -dump-mem-at` 的位址寫成兩欄（`0:長度`）時是大富翁 2 的 IDA 位址，第一份傾印整段錯位 0xEF00，看起來像指標都指錯；改寫 `lin:0:長度`。
  教訓：沿用通用探針的位址格式前，先讀它的解析函式。
- sosb-explore 跑約 200 步被容器 OOM 殺掉：dos 層每次滑鼠輪詢、machine 每次埠寫入都留紀錄。加 `LogKeep`／`PortLogKeep` 上限（預設不變），session 與 sosb 工具開啟（dosgolem `4dd38d2`）。
  sosb-play 長時間遊玩同樣受影響，這是發行前必修的問題。

## 2026-10-23 G6 跨畫面盤點（#7）

- `tools/g6-service.sh`（鎮上服務，sosb-overlay-shot 送鍵）、`tools/g6-explore.sh`（sosb-explore 自動探索）、`tools/g6-misses.sh`（彙整未命中），結果在 docs/re/011。
- 補譯介面字串 44 筆、組句模板到 187 條（神殿問候、取錢提示、治療對象、戰鬥傷害、50 條 `is <狀態>`）；補譯後同路線重跑未命中 0。
- 勘誤：well1 在戰鬥子選單反覆選 Exit 原地打轉，探索器預設離開選項不適用戰鬥；從戰鬥狀態改 `-pick Quit` 重跑（well2）。
- 勘誤：重跑 temple2 時取錢那段沒走到，回頭查舊盤點才發現按鍵版本不同；另開 temple-take 專走金錢池。教訓：收據的按鍵序列存進輸出目錄，不靠對話紀錄回找。

## 2026-10-23 G10 多語系與配樂（#11）

- 多語系依克萊恩英豪規格 015 移植：简中由 `tools/zhcn_convert.py`（OpenCC tw2sp，專名保護、`text/zhcn-fixes.tsv`）從繁中產生；
  日文、韓文 14 批由 sonnet 譯者照 `workplace/tr-jako/PROMPT.md` 翻譯，`tools/jako_merge.py` 合併，前作同 key 的譯文直接沿用；
  英文是原文加 Courier Prime 字型。手札與攻略面板只有繁中、简中（日韓沒有譯本，面板停用）。
- `tools/g10-lang-receipt.sh`：四種語言同一組按鍵走到鎮上，記憶體雜湊一致（`a786f…`），ja、ko、en 缺字 0。
- 勘誤：zh-CN 缺「埃、柴、迪、•」4 字，都來自玩家名音譯表；`tools/font-dev.sh` 沒收 `text/translit-zh-CN/` 的字集（前作在 `package.sh` 才收），已補。
- 勘誤：日韓的手札編號接句（`AND YOU RECORD IT IN JOURNAL ENTRY`）譯成「旅の手記の項目」「여행 일지 번호」，接上補字後成了「項目37項」。
  前段改收在「第／제」（4 個 key），`jako_merge.py` 的 `JOURNAL_REF` 註解就是這個約定。教訓：補字規則寫進譯者提示，不只寫在合併工具。
- 配樂（規格 014）：原版標題曲三個聲道同一組音色；以 4 個動機新編 13 首（`tools/music_compose.py`，架構移植前作），
  `music.tsv` 增益對齊標題曲 RMS 的 0.7 倍。使用者試聽通過。選曲表 `text/music-cues.tsv` 的字串取自本作盤點，
  `cmd/sosb-music-cues`（dosgolem `4db8341`）重播確認戰鬥、全滅、營地、神殿切曲；勝利與強敵只有靜態字串。

## 2026-10-23 G10 推廣影片、日韓英手札（#11）

- 規格 016：dosgolem `41f6c7f` `cmd/sosb-promo`（由 cok-promo 移植）；`tools/promo.sh` 錄 8 段，`tools/promo-build.sh` 剪成 81 秒，字卡依手札第 18、37 則。
- 勘誤：標題段從第 300M 步的狀態錄，整段靜音。標題曲在第 43M 步寫入音色，狀態檔不含 OPL 暫存器，載入後只剩 key-on、音量包絡起不來。
  改從冷開機第 40M 步存的狀態起錄。教訓：要錄原版音樂的段落，狀態檔要存在該曲設定音色之前。
- 勘誤：字卡段的墊底配樂直接用渲染 WAV（增益 1），比遊戲內小 10 dB；改乘 `music.tsv` 的 gain。
- 換語言收據發現：切到日韓英再切回繁中，隊員名停在英文，直到遊戲重印。疊字在新語言查不到時被移除，切回來不會補回；記在規格 016 §5 與 #11。
- 英文手札第 38–72 則對頁面圖校讀完，`tools/journal_en_build.py` 合併成 `text/journal.en.tsv`；英文字型補破折號。
- 日韓手札與攻略：sonnet 譯者依 `workplace/tr-jako/AUX-JOURNAL-GUIDE-PROMPT.md` 從繁中定稿翻譯（前作手札從英文翻，本作繁中已對英文頁面圖校正）。
  回報的「＋45 長劍」、兩個「第七個謎題」、「112」都與雜誌原刊一致，照原刊保留。
- 勘誤：新增的 `text/music-cues.tsv` 沒有顯示欄，`tools/font-dev.sh` 掃 `text/*.tsv` 時中止；加進略過清單（第二次同類，前一次是 journal-maps 的 `zh` 欄）。
- 勘誤：日韓攻略目錄標題顯示「クリンの勇者たち／크린의 용사들 攻略」。`tools/jako_aux_prep.py` 沿用前作譯文只比 key，本作改過繁中的 `guide.toc` 也被沿用。
  改成前作繁中與本作相同才沿用（三種表都套），`guide.toc` 重譯。教訓：沿用譯文的條件是「原文與繁中都相同」，key 相同不夠。

## 2026-10-23 G4 說明書其餘章節、最後抽驗

- 珍056 PDF 第 1–18 頁以 300 dpi 重轉、切成 106 格、PaddleOCR 出逐格草稿（`tools/zh_manual_split.py`、`zh_manual_draft.py`）。
  勘誤：切線第一版在頁高 25–42% 找空白，抓到安裝說明頁的頁內留白，把上一頁頁碼切進來；改成均分線前後 80 像素內找。
  勘誤：PaddleX 要在 HOME 寫暫存，HOME 設在容器內 `/tmp/h` 時掛載點父目錄由 docker 以 root 建立、不能寫；改用工作區自建的 paddle-home 並先建好掛載點。
- 下冊怪物與法術清單的「中文名（English）」逐格對圖後與術語表比對（`tools/zh056_names.py`、`text/zh056-names.tsv`）：131 組，異名 63。
  遊戲內譯名多沿用前作，當時下冊章節未轉錄；是否改用珍056 譯名待使用者決定。
- 最後抽驗（使用者：做完再抽驗）：`tools/g7-journal-receipt.sh` 的手札自動彈出、攻略、手札翻閱截圖雜湊與 docs/re/007 相同，
  地圖頁因 G8 攻略點而改變；`tools/g16-flash-receipt.sh` demo 與進金庫兩條閃現 0；四語收據缺字 0、記憶體雜湊一致。

## 2026-10-23 剩餘項目（使用者：完成剩下的、打包三平台完整版）

- 使用者對建議清單回「ok 可以喔」：遊戲內譯名維持現狀，推廣影片接受（CONTEXT 決策表）。
- 換語言缺陷：dosgolem `41a0a7e`，xlate 新增 `Stamp.Hidden`（spec 202 §2.10），sosb 路徑 A 換語言查不到時隱藏而非移除；
  重錄換語言段，切回繁中後隊員名恢復音譯。
- 說明書錯譯表 `text/errata-manual.tsv` 7 條（Storm Giant、Cloud Giant、Ogre、Umber Hulk、Mastodon、Gargoyle／Margoyle 對調），`errata_check.py` 加 `--manual`。
- 珍056 上冊與下冊 p.1–26 校讀完成，頁碼連續（docs/re/006）。
- 勘誤：名稱表把 p.11 的「驚獅」當 OCR 錯字改成「鷲獅」；校讀者放大確認原書就印「驚獅」，改回照原書。教訓：「OCR 錯字」與「原書錯字」要放大到能分辨再改。
- 校讀者回報讀圖時工具結果附帶避免重製受著作權內容的提醒；轉錄稿只在 workplace（不進 Git、不進發行包），供錯譯比對。
- 發行包：`tools/package.sh` 由前作移植（規格 012），`SOSB_WITH_DATA=1` 打出 `v.1.0.0-20261023` 三平台本機完整版，只在 `dist-all/`。
  倚天字型第一次建置因譯文有 Big5 沒有的 ・、裏、～ 中止；`tools/eten_font.py` 加明列的借字表。・ 先借 A150，字模的點偏左，改借置中的 A145。
- 冒煙：Linux、Wine 冷開機到主選單，兩平台截圖逐像素相同；HD 版標題與原版不同，確認 HD 有載入。
  勘誤：第一輪 Wine 截圖與 Linux 差 1.8 萬像素，原因是 Wine 預設語系 en-US，依設計選了英文；比對改明指 `-lang zh-TW`。
  第一輪兩包截圖相同，是主選單本來就沒有 HD 圖；加截第 2400 格的標題。教訓：驗 HD 載入要截有 HD 圖的畫面，驗跨平台相同要先固定語言。
- 切換列（使用者：工具列也要確定有）：新增 `tools/release/smoke-toolbar.sh`，發行包在 Linux 與 Wine 都顯示切換列，兩平台逐像素相同。
  勘誤：讀我檔沿用前作「沒有 HD 時顯示『無HD』」；本作 2026-10-22 已改成倍率項直接顯示「3倍」或「3倍HD」（規格 019）。讀我與 F5 地圖頁說明更正後重新打包、重跑全部冒煙。
- README：遊戲介紹、故事背景（開場劇情與手札第 18、25、26、37 則）、成果表與 12 張截圖（`docs/screenshots/`；2 倍取自手札、地圖收據，3 倍取自推廣片錄製與發行包冒煙）。

- README（使用者：手札地圖頁截圖可以放；優化過的 BIGPIC 與事件圖也要放）：加「大圖與事件圖」一節，BIGPIC 8 張與事件圖 38 個區塊的原版／HD 對照（`docs/screenshots/bigpic*.jpg`、`hd-07-pics.jpg`，取自 `hd/theme/` 與 `review/hd/`）。
  備註：`hd/theme/theme.json` 的 bigpic2-119 標未觀測，但推廣片開場畫格已以 HD 顯示這張山谷；標記沒有更新（改了要重新打包），先記在這裡。
- HD 執行期證據（使用者：補上標記並重新打包，推廣片不重錄）：新增 `tools/hd_observe.py` 掃推廣片 9 段 7,528 格，HD 圖逐像素吻合的項目補為已觀測：開場山谷 bigpic2-119、鎮長 pic1-080、紮營夜景 pic4-059、寶物 pic4-060（第一階段 89 項中已觀測 10 項）。
  `hd_theme.py`、`hd_review_md.py` 加 `--observed`；請求清單不動（`hd_theme.py` 會核對清單雜湊與數值驗收一致）。重組的 theme.json 與原本相比只有證據欄位不同；審閱頁只有 README 改變。
  勘誤：第一次重組照 b01–b06 的順序，項目順序與原檔不同；原本的批次順序是 b01、b06、b02–b05，從現有 theme.json 推回後重跑。
- README 加推廣文「重返冰封山谷」（使用者：這是光芒之池第三作），出處為開場劇情、手札第 25、47、48 則與攻略章節。重新打包三平台完整版，全部冒煙通過。

## 2026-10-23 結案

- Issue #5、#7–#12 留結案說明（完成項與缺口）後關閉，#1–#17 全部關閉；缺口表記在 CONTEXT「結案」一節。
- workplace 清理（使用者選定）：刪 pkg-stage、pkg-gocache、readme-shots、play-smoke、根目錄 log，推廣片錄製畫格 promo/seg、build、check；保留 sosb-promo.mp4（雜湊 f6e0dbac… 與規格 016 相同）。5.5 GB → 2.6 GB。
- CONTEXT 勘誤：dosgolem 分支頂端由 41f6c7f 更正為 d6c0a4b。
