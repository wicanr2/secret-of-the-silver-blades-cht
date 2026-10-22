# 《銀色匕首之謎》（Secret of the Silver Blades）dosgolem 繁體中文化與 HD

本檔是 Claude 與 Codex 共用的專案入口。回覆、文件與提交訊息預設使用繁體中文。
新工作階段先讀本檔，再讀 `CONTEXT.md`、目前 GitHub Issue 與直接相關規格。
檔案尚未建立時明列缺項，不把前作狀態當成本作進度。

## 1. 使用者授權與專案範圍

使用者於 2026-10-22 指定：

- 參考 `/home/anr2/cht/golden_box/champions_of_krynn/`（以下稱克萊恩英豪）的經驗，用 dosgolem
  執行原版 DOS《Secret of the Silver Blades》，以輸出攔截覆繪做繁體中文化。執行與呈現的整合
  介面一律用 dosgolem。
- 把原版素材做成 HD，可用 Codex 輔助。
- 建立 **private** GitHub 儲存庫，啟用 Issues。
- 修正當年中文譯本的錯譯。對象是 `珍056-銀色匕首之謎.rar` 內的軟體世界珍藏版說明書；
  說明書裡的手札修正後放進遊戲，玩家不必再查說明書。
- 授權上網取得英文手冊與 Adventurer's Journal，作為校正錯譯的原文。
- 範圍整個比照克萊恩英豪。

儲存庫名稱 `secret-of-the-silver-blades-cht`，owner 以主機 `gh auth status` 回讀的登入帳號為準。
建立前查同名庫；存在時核對用途，不接管、不覆寫。本授權含初始化本目錄 Git、設定 repo-local
身分 `wicanr2@gmail.com`、提交與推送本範圍內的文件、原創程式與建置腳本，以及建立、更新、
留言、關閉本專案 Issue。轉公開、公開 Release、上傳原版素材、加入協作者、改動前作或其他
專案、推送 dosgolem 上游及破壞性操作，另行取得授權。

下表沿用克萊恩英豪的定案（其 `AGENTS.md` 第 1 節與 `CONTEXT.md` 有效決策），使用者
2026-10-22 以「整個範圍比照克萊恩英豪」確認，不重複詢問。功能鍵指派沿用克萊恩英豪現行版本。

| 項目 | 定案 |
|---|---|
| 中文題名 | 沿用「銀色匕首之謎」（使用者指定）。Blades 與「匕首」的語意落差只記入術語表，不改題名 |
| 遊戲短名 | `sosb`，用於 dosgolem `apps/sosb/` 與程式識別 |
| 工作順序 | 先完成繁中、錯譯修正、手札與查驗題，再做 HD 與其他擴充 |
| 手札 | 修正後的說明書手札全部放進遊戲，劇情引用時自動彈出，另以前端鍵（F5）翻閱已觸發的手札。說明書有酒店傳聞等其他引用段落時一併處理 |
| 手冊查驗題 | 問句後顯示答案，預設開啟、可關閉（F9）；玩家仍要作答，判定照原版 |
| HD | HD 圖以 3 倍（960×600）為準，風格 B（奇幻插畫），配色照原版。預設 2 倍顯示原版，F2 切 3 倍，HD 圖只在 3 倍顯示 |
| HD 分工 | HD 整條（抽樣、來源辨識、請求、重繪、驗收、接入）交 Codex，以 Issue 追蹤；使用者另行指派時 Claude 才接手。介面見第 6 節 |
| 切換列 | 視窗最上方，平常隱藏，滑鼠移到頂端時出現；HD 與擴充功能切換放這裡。沒有 HD 素材時停用 HD 切換並顯示原因。F12 切回英文原版 |
| 字型 | 繁中源泉圓體（2 倍 Medium、3 倍 Bold），比照克萊恩英豪現行版本 |
| 多語系 | 繁中先交付，之後比照克萊恩英豪規格 015：简中由繁中 OpenCC 轉換加詞彙表，日、韓以英文為底機器翻譯並標註，英文以新字型重繪；第一次執行依系統語言，F8 切換 |
| 攻略面板與地圖疊層 | 遊戲內可翻頁攻略面板（F6）與地圖疊層攻略點（F7）。本目錄目前沒有雜誌攻略掃描；等使用者提供，缺的部分以 SSI 官方提示書補 |
| 配樂 | 以原版動機新編 OPL2 配樂，依地圖與戰鬥切換；使用者試聽通過才定案 |
| 作弊 | 我方無敵（F1，預設關）：HP 不減少，不進入昏迷、中毒、麻痺、睡眠等異常 |
| 推廣影片 | 故事背景字卡、HD 切換與 F12 切換示範 |
| 發行包 | 三平台（Linux AppImage、Windows zip、macOS universal zip）；可散布 patch 分原版、原版＋HD 兩包；本機另出完整版，不散布。只私下分享給持有原版的人，不公開上架 |
| 截圖入 repo | README 展示用截圖放 `docs/screenshots/`；其他截圖只留 `workplace/` |

可逆的讀取、整理、文件修正與已授權測試自主進行。改變目標、架構、原版忠實度、正式資料
格式、玩家操作、授權或公開方式時，先依第 10 節共同決策。

## 2. 初始化順序與基線

初始化依序完成：本檔 → `.gitignore` → 私人儲存庫與 Git → 初始 Issue → 證據與規格 → 實作。
建立 Issue 前不解壓原版、不跑遊戲、不寫產品程式。遠端 Issue 是可執行工作狀態的權威，本機
不建 `WORKLIST.md`。未建立的 Issue 不填編號或完成狀態。

| 項目 | 2026-10-22 初始觀察 |
|---|---|
| 原始輸入 | 根目錄兩個壓縮檔；只讀取成員清單與 SHA-256，尚未解壓（第 3 節） |
| 英文原文 | 尚未取得 |
| 雜誌攻略 | 尚未提供 |
| 程式與驗證 | 沒有本作程式、執行收據或中文化證據 |

初始工作已登錄為 [#1–#12](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues)，狀態只在遠端維護。之後使用者新增的需求另開 Issue（#13 demo 中止、#14 CPU 速度、#15 切換列字級、#16 閃爍、#17 無敵位址驗證），不改下表。規格編號以克萊恩英豪 `docs/spec/001`–`017` 為對照，本作規格另行編號。

| 階段 | 依賴 | 完成條件 |
|---|---|---|
| [G0 協作治理／#1](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/1) | 本檔 | `.gitignore`、`LICENSE`、`CONTEXT.md`、`WORKLOG.md`、`CLAUDE.md` 就位；private 與 Issues 回讀 |
| [G1 原始輸入／#2](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/2) | G0 | 壓縮檔與成員 SHA-256；安裝器展開方式、完整版或試玩版、版本、入口 EXE 與啟動參數；珍056 頁序與缺頁；英文手冊與手札的來源網址、取得日期、SHA-256 |
| [G2 dosgolem 基線／#3](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/3) | G1 | 選定並固定 dosgolem 基底（第 5 節）；正常入口到第一個可操作畫面；缺服務與重播收據 |
| [G3 輸出路徑／#4](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/4) | G2 | 印字、清除、捲動與選單掛勾的原始定位與證據等級；驗證第 4 節的待驗假說 |
| [G4 說明書轉錄與錯譯校正／#5](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/5) | G1 | 珍056 逐頁轉錄；與英文原文逐段對照；錯譯表（第 3.2 節）與檢查腳本 |
| [G5 譯文與字型／#6](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/6) | G3、G4 | 術語表、TSV catalog、字型與檢查工具；先試譯一批給使用者看文風再全量 |
| [G6 繁中接入／#7](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/7) | G3、G5 | 每條路徑 READY 規格、覆繪、A/B 收據與正常玩家路徑；含組句、英數半形、玩家名音譯 |
| [G7 手札與查驗題／#8](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/8) | G3、G4 | 手札引用與查驗題的輸出證據、修正後譯文、自動彈出與翻閱、答案顯示的收據 |
| [G8 攻略面板與地圖疊層／#9](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/9) | G6、使用者提供掃描或提示書 | 攻略轉錄、術語對齊、面板與地圖疊層收據 |
| [G9 HD 與切換列／#10](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/10) | G6、G7 | 交 Codex：來源與遮擋證據、批次重繪、接入、F2 與切換列收據 |
| [G10 配樂、多語系、作弊、推廣片／#11](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/11) | G6、G9 | 各自規格與收據；配樂經使用者試聽 |
| [G11 封包驗收／#12](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/12) | G6、G9 | 乾淨目錄啟動、manifest 與 SHA-256、存檔位置；明列未驗平台 |

## 3. 原始輸入與資料保護

| 根目錄檔案 | SHA-256 | 成員 | 尚待確認 |
|---|---|---|---|
| `secret-of-the-silver-blades.zip` | `b3147db0076bf6888f5125c80b0d9c02cbd89f82d60324b3dd85f3adcaae29f7` | `install.com`、`secret1.exe`、`secret2.exe`、`bbsad.txt`、`dsklabel.txt` | 遊戲檔包在安裝器內，不能直接取用。展開方式、完整性、版本與入口 EXE 由 G1 確認 |
| `珍056-銀色匕首之謎.rar` | `5ac3f9c9382c6a52bb7eb7b0bd92e385bdf764ccf0ed849a9adf920993b2c7dc` | `遊戲手冊：銀色匕首之謎.pdf`、`Pic0001.jpg`–`Pic0004.jpg`、`軟體世界說明書補完計劃.txt` | RAR 4 格式。頁序、缺頁、掃描與 PDF 的關係 |

- 原始壓縮檔保留原位、不覆寫，只在 Docker 內唯讀掛載。解壓、OCR、雜湊與探針產物寫入
  `workplace/`。
- `.gitignore` 在 `git init` 前排除上述檔名、`workplace/`、`dist-all/`、存檔、憑證與本機快取；
  G1 盤點後補原版副檔名。提交只列明確檔案，不用 `git add .`。
- 原版遊戲、手冊與攻略掃描、英文原文 PDF、存檔與擷取的原版素材不進 Git、GitHub 或可散布
  發行包。需要原版的測試缺檔時明確 skip。
- 例外（沿用克萊恩英豪）：譯文 TSV（含修正後的手札）、英文手札逐字稿、翻譯批次與提示詞、
  HD 主題、攻略與提示書轉錄提交到 private repo 保存。repo 轉公開前必須移除這些內容並清理歷史。

### 3.1 英文原文取得

- 下載在 Docker 內進行，只對該次下載開網路。每個來源放在 `workplace/input/en-docs/<來源>/`
  的獨立空目錄，記錄網址、取得日期、檔名與 SHA-256。
- 下載物是不可信資料：不執行、不從其目錄啟動直譯器，讀取它的 Python 以 `-I` 執行。
- 優先找 SSI 原版掃描（手冊、Adventurer's Journal）。來源不明或為重打字版時標明，只作輔助。

### 3.2 錯譯修正

- 珍056 的轉錄維持原書用字，校正不改轉錄本身。方法參照光芒之池的說明書 corpus
  （`/home/anr2/cht/golden_box/pool_of_radiance/docs/spec/054-softworld-manual-journal-corpus.md`
  與同專案 `docs/reference/manual/glossary.md`）。
- 錯譯以資料表記錄：`text/errata.tsv`，欄位為 key、頁碼、英文原文摘錄、珍056 譯文摘錄、修正譯文、
  類別（誤譯、漏譯、異名、專名不一致等）、理由、證據等級、出處。
- 遊戲內手札與其他玩家可見譯文的正式來源是 `text/` 下的 TSV，以修正後版本為準。
- 檢查腳本驗證欄數、key 唯一、頁碼存在、證據等級合法，並確認每條修正都已出現在正式 TSV；
  不一致時結束碼非 0。「已修正錯譯」只指表中通過檢查的條目。
- 英文原文與遊戲內實際字串衝突時，以遊戲內字串為準，並在錯譯表註明。
- 題名「銀色匕首之謎」保留，不列入修正。

### 3.3 譯名與文風

本作是 Forgotten Realms 系列 Gold Box（光芒之池、青色枷的詛咒之後），不是克萊恩世界。
克萊恩英豪與幽靈騎士的術語表只沿用遊戲機制與共通物品，地名、人名、神祇不從那裡取。

譯名優先序：

1. 本作遊戲內原文語境。
2. 珍056 譯名，經第 3.2 節修正後的版本。
3. 同系列前作譯名：`/home/anr2/cht/golden_box/pool_of_radiance/docs/reference/manual/glossary.md`、
   `/home/anr2/cht/golden_box/curse_of_the_azure_bonds/docs/knowledge/coab-glossary.md`。
4. 本作自譯，在術語表註明。

- 文風比照克萊恩英豪：忠實正式、奇幻古典語氣；敘述對隊伍用「你們」；玩家須輸入的字寫成
  「中文（ENGLISH）」；英文雙關謎語附英文原句與答案；物品名加值置後（例「長弓 +3」）。
- 自動比對只產生待核對候選。異譯保留來源與選用理由，不改動前作檔案。

## 4. 參考來源與知識路由

每次開工、兩輪同類失敗、形成完成結論、建立文件或目錄前，核對
`/home/anr2/.codex/knowledge-base/knowledge-router.md`，只讀本次命中的入口。

| 來源 | 可沿用的方法 | 必須在本作重驗 |
|---|---|---|
| 克萊恩英豪 `AGENTS.md`、`CONTEXT.md`、`docs/spec/`、`docs/re/`、`tools/` | 第一參考：輸出覆繪、規格 001–017 的架構、收據腳本、TSV 與字型管線、手札與查驗題、HD 批次與 Codex 介面、切換列、多語系、配樂、作弊、封包 | 位址、bytes、座標、字串、callsite、重播輸入、素材數量、完成狀態 |
| 光芒之池 `docs/spec/054-*`、`docs/reference/manual/` | 軟體世界說明書轉錄、跨冊譯名定案、原書誤譯註記 | 本作頁數、譯名與錯譯 |
| `/home/anr2/cht/golden_box/curse_of_the_azure_bonds/`、`golden-box-remake-engine/` | Forgotten Realms Gold Box 的 DAX／ECL 格式、TPOV overlay 逆向、術語 | 只當格式與術語參考，不採用其 remake 引擎 |
| `/home/anr2/cht/dosgolem/`（`README.md`、`CLAUDE.md`、`docs/spec/006-layering.md`） | 能力矩陣、`cmd/probe`、Docker 入口 `tools/go.sh` | 本作 binary 是否可執行與實際缺服務 |

**待驗假說**：本作 1990 年發行，與克萊恩英豪同代，克萊恩英豪的輸出路徑家族（Pascal 字串、
文字視窗、底列水平選單、組句訊息、手冊查驗題、手札引用）可能有對應。這是 G3 的起點；
對到本作 callsite 與 bytes 之前不當成已知。

| 觸發 | 入口 |
|---|---|
| 老遊戲逆向與中文化規則路由 | skill `re-retro-cht-rulebook` |
| 中文高解析畫布 | `~/.claude/rulebook/81-retro-cjk-hires-canvas.md` |
| Gold Box `.OVR`／TPOV | `~/.claude/knowledge-base/retro/borland-tpov-overlay-re.md` |
| IDA Pro 9.4 | `~/.claude/knowledge-base/retro/ida-pro-9.4.md`、`~/.codex/skills/use-ida-pro-9-4/SKILL.md` |
| 翻譯與顯示隔離 | `~/.codex/knowledge-base/local/localization-display-semantic-isolation.md` |
| 中文版面與 Gold Box 畫面比較 | `~/.codex/skills/research-pc98-golden-box-ui/SKILL.md` |
| 建立文件或新目錄 | `~/.codex/knowledge-base/local/project-document-responsibilities.md` |
| 授權 | `~/.codex/knowledge-base/local/rrsal-1.0.md`（RRSAL-1.0，已定案） |
| 正式版號與交付目錄 | `~/.codex/knowledge-base/local/retro-remake-release-versioning.md`、`retro-remake-dist-all-output.md` |

## 5. dosgolem 分層

- 不另建 remake 引擎。執行、畫面、輸入、虛擬時間、中文覆繪與 HD 呈現都經 dosgolem。
- 本作位址、畫面狀態、輸出攔截點、重播與 HD 素材對應屬遊戲專屬層，放在 dosgolem
  `apps/sosb/`。通用 CPU、DOS、BIOS、VGA、輸入與音訊屬通用層，不寫入本作名稱或位址。
  判準見 dosgolem `docs/spec/006-layering.md`。
- 研究與開發在 `workplace/dosgolem/` 的隔離 clone，分支 `secret-of-the-silver-blades-cht`，推到本專案
  private repo 的 `dosgolem/sosb` 分支保存。本專案 `main` 只放文件、譯文、字型來源與工具。
- 不改動 `/home/anr2/cht/dosgolem` 工作樹，不推送 dosgolem 遠端，不推送前作儲存庫。
- 基底由 G2 選定。2026-10-22 以 `git for-each-ref` 回讀的候選：
  - 克萊恩英豪 repo 的 `origin/dosgolem/cok`，`8742fa9`（2026-10-21）。含 HD 主題、切換列、字型倍率、
    多語系、配樂、發行模式等已修正的通用層。
  - `/home/anr2/cht/dosgolem` 的 `main`，`81c85be`（2026-10-15），也是前作 `dosgolem/dkk` 線的起點。
    同庫 `san5-mixer`（`f79eab6`，2026-10-18，領先 `main` 19 個 commit）等分支有較新的通用規格，
    尚未併回 `main`。
  選定前重新回讀各分支頂端。選定理由、commit、Go 版本與 Docker image ID 記入 `CONTEXT.md`。
  `apps/cok/` 只當參考實作，其中位址、座標與字串在本作全部視為假說。從前作分支帶來、
  實屬通用層的程式留在通用層。
- Go 不允許外部 module 引用 dosgolem `internal/`，adapter 必須在 dosgolem module 樹內。
- dosgolem 是原版行為、畫面與虛擬時間的權威執行器，正式收據由它產生。DOSBox／DOSBox-X
  只作診斷與交叉基準，擷取明標輔助。

## 6. 繁中與 HD 契約

- 原版 EXE、資料、規則、亂數、條件比較、檔名、腳本鍵值與存檔保持原樣。本專案不翻譯 EXE。
- 英文原文、呼叫位置與畫面座標用於辨識輸出。譯文只影響顯示，不進入比較、查找、序列化、
  檔名或存檔。共用字串函式須盤點顯示與語意呼叫者。
- 原版要求查閱手冊時，辨識該題的輸出事件再覆繪中文；不繞過驗證、不改判定。
- 玩家可見譯文以 UTF-8 TSV 為唯一正式來源；catalog 檢查 key 唯一、欄數、控制碼、placeholder、
  漏譯、孤兒 key、行寬與字型覆蓋。字型子集由正式譯文重建，不為缺字改譯。
- 術語表、手札、攻略面板與地圖點的譯名一致性用檢查腳本驗證（比照克萊恩英豪
  `tools/term-check.sh`），不一致時結束碼非 0。
- 中文字依 `rulebook/81`：拉高輸出畫布，原版底圖整數倍最近鄰放大，中文用正常尺寸字型。
- 未辨識、歧義或失配的輸出保留原版並記錄缺口。

### HD：Codex 的工作介面

| 階段 | 產出 |
|---|---|
| 來源辨識 | 本作繪圖來源、繪製時機、遮擋與動畫相位證據；DRAFT 規格 |
| 匯出原版圖塊 | `workplace/hd/requests/<批次>/`：原版 PNG 與 `manifest.json`（來源檔、offset、SHA-256、尺寸、色盤、透明色、規格編號） |
| 重繪 | `workplace/hd/out/<批次>/`：重繪 PNG 與 `manifest.json`（來源 key、輸出尺寸、風格批次、生成方式、權利註記） |
| 驗收與接入 | 張數、尺寸、alpha、對位檢查；原版／HD 同狀態比較；接入 dosgolem 呈現層 |

- 每個批次先開 Issue，寫明請求目錄、規格、風格定案、完成條件，以及 Codex 可否 commit、push。
  Issue 沒寫明時不 commit、不 push。
- Claude 以主機 `codex exec` 委派，這是繼 `gh` 之後第二個主機工具例外。克萊恩英豪第 6 節記錄的
  旗標為 `-C`、`-s workspace-write`、`-o`、`--add-dir`；首次使用前以 `codex exec --help` 重新核對。
  prompt 明寫可讀與可寫的目錄。
- Codex 只改 Issue 指定的目錄與檔案，不改其他規格或 `CONTEXT.md` 的有效決策。轉檔、縮放、
  建置與批次腳本一律在 Docker 內。輸出無法符合請求 manifest 時在 Issue 說明，不自行改規格。
- Codex 產出的素材視為可放進原版＋HD patch，權利分類仍記在 manifest 與 Issue。
- HD 只改呈現。來源、繪製時機、遮擋、清除與動畫依本作證據辨識；失配、撤除或遮擋未知時
  回退原版。切換不得重開遊戲、改亂數或重寫存檔。

## 7. 規格與驗證閘門

正式接入依序走：`原版證據 → DRAFT → 證據審查 → READY → 實作 → 同狀態驗證 → CONFORMED`。
未達 READY 的探針與原型不進產品路徑。

- 每項研究記錄輸入檔名與 SHA-256、工具版本、dosgolem 位址空間、callsite、暫存器、字串位址、
  字型、座標、顏色與清除時機。證據等級用「已證實、強推論、假說、未知」。反組譯名稱只供導覽。
  引用前作結論註明出處，等級最高為「假說」，直到本作重驗。
- 原文／繁中、原版／HD 比較固定資料、初始狀態、輸入與 seed，差異只能出現在批准的呈現範圍。
  另走正常玩家路徑：冷啟動、建角或載入、探索、對話、選單、戰鬥、存讀檔，驗證捲動、清除、
  返回與殘字。快照與狀態注入只供診斷。
- HD 另驗原版記憶體、暫存器、畫面緩衝與存檔不受影響，並用失配來源與撤除素材建立負對照。
- 只有被 dosgolem 同狀態收據覆蓋的路徑，才能稱為「已中文化」；其餘標示未知。

## 8. Docker、Git 與主機衛生

- 分析、解壓、搜尋、OCR、下載、建置、測試、執行遊戲與 GUI 自動化只在 Docker 內進行。使用
  `--rm`、`--memory`、`--cpus`、`--pids-limit`、外層逾時、`-u "$(id -u):$(id -g)"`、
  `--log-opt max-size=10m --log-opt max-file=3`，預設 `--network none`。
- 掛載前確認 host 來源存在且型態正確。每批工作後在容器內執行
  `find <工作根> -user root -o -type d -name '*.md'`。不碰其他專案的 image、volume 與 container，
  禁止任何 prune 與 `rmi`。
- 主機工具例外只有 `/home/anr2/.local/bin/gh` 與 `codex`。第一次使用 gh 先執行 `gh auth status`。
- `workplace/` 是唯一可寫研究工作區，整個目錄 gitignore。不另建同義目錄。
- 前作、dosgolem 原始工作樹與 `~/.claude/`、`~/.codex/` 只讀。
- `LICENSE` 依 RRSAL-1.0 範本在第一個 commit 前就位。正式交付根為 `dist-all/<版本>/`。
- 本機目錄名 `secret-of-the-sliver-blader` 拼錯，但不改名；它與 repo `secret-of-the-silver-blades-cht`
  指同一專案。

## 9. 文件職責

以下除本檔外按需建立。新增文件時同步更新此表或子目錄索引。

| 路徑 | 職責 |
|---|---|
| `AGENTS.md` | 協作規則與專案路由，即本檔 |
| `CLAUDE.md` | 指回本檔的薄入口、常用指令與資料索引 |
| `CONTEXT.md` | 有日期的現況、有效決策、glossary、dosgolem 基線與證據入口 |
| `WORKLOG.md` | 按時間追加的操作、驗證結果與 Docker 清理狀態 |
| `README.md` | 用途、穩定入口與現況摘要 |
| `docs/re/` | 輸入雜湊、位址、實驗與證據等級；`docs/re/README.md` 為索引 |
| `docs/spec/` | DRAFT、READY、CONFORMED 規格，回鏈 Issue |
| `text/` | 譯文 catalog、手札、`glossary.tsv`、`errata.tsv` |
| `font/` | 字型來源與字元清單 |
| `reference/` | 攻略與提示書轉錄（private，轉公開前移除） |
| `tools/` | 可重現的 Docker、盤點、驗證與打包入口 |
| `workplace/` | 解壓輸入、英文原文、轉錄、探針、IDA、dosgolem clone、HD 批次；不入 Git |
| `dist-all/` | 正式交付根；含原版產物不入 Git |

## 10. 共同決策與停止線

- 第 1 節與第 3 節已定案事項不重複詢問。
- HD 美術與操作取捨先展示並列原型，每次只問目前最早會阻塞的決定。
- 能由 bytes、程式、規格或測試查出的事實自行查證。實質改變規則、存檔格式、原版忠實度、
  版面、平台範圍或散布方式時先確認。
