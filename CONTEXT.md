# 目前真相

2026-11-11 空間維護：清除可重建的快取、編譯執行檔，移除 6,958 個檔案，合計約 0.661 GiB。原始輸入、程式來源、正式素材、存檔、研究紀錄、影片與現行封包保留。舊版封包的 manifest 與驗收紀錄保留；歷史封包路徑不代表實體檔案仍存在。詳見 [WORKLOG.md](WORKLOG.md)。

更新：2026-10-23（Asia/Taipei）。規則見 [AGENTS.md](AGENTS.md)，歷程見 [WORKLOG.md](WORKLOG.md)。

## 儲存庫

| 項目 | 值 | 回讀方式 |
|---|---|---|
| 網址 | <https://github.com/wicanr2/secret-of-the-silver-blades-cht> | `gh repo view --json url` |
| owner | `wicanr2` | `gh auth status`、`gh repo view --json owner` |
| 可見性 | PRIVATE | `gh repo view --json visibility` |
| Issues | 啟用；初始 G0–G11 為 #1–#12；之後的需求 #13–#17 | `gh issue list` |
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
| 2026-10-22 | dosgolem 基底選克萊恩英豪 `dosgolem/cok`（`8742fa9`），理由見 docs/re/003 | G2 |
| 2026-10-22 | 攻略來源：使用者提供《軟體世界》第 21–25 期掃描 22 張，放 `walkthrough/`（不進 Git） | 使用者提供 |
| 2026-10-22 | 譯文文風依試譯 122 則確認，全量翻譯 | 使用者回答 |
| 2026-10-22 | HD 可由 Codex 輔助，比照克萊恩英豪整條交 Codex（2026-10-23 改為只有生圖交 Codex） | 使用者指示 |
| 2026-10-22 | demo 中止與 CPU 速度照幽靈騎士規格 015、016 | 使用者回答 |
| 2026-10-22 | 切換列字級小中大（3 倍 16／22／24、2 倍 12／16／16）；倍率合成一項、速度只顯示倍率 | 使用者回答 |
| 2026-10-22 | 必要時可修改原版 EXE 降低閃爍；目前以覆繪層處理即可，未改原版 | 使用者指示（#16） |
| 2026-10-22 | 收據截圖抽樣即可，不逐張全看 | 使用者指示 |
| 2026-10-23 | 閃爍目標改為完全不先露原版字或原版圖（所有語言、HD 模式），規格 021 | 使用者指示（#16） |
| 2026-10-23 | 驗證抽樣即可，不窮舉畫面與路線 | 使用者指示 |
| 2026-10-23 | HD（G9）改由 Claude 處理；只有生圖一步交 Codex（依原版手繪重畫，不用濾鏡）。取代 2026-10-22「HD 整條交 Codex」 | 使用者指示（看過濾鏡比較頁後選定） |
| 2026-10-23 | 可用 Artifact 與使用者溝通（原型並列、取捨確認） | 使用者指示 |
| 2026-10-23 | 遊戲中配樂 13 首（規格 014）試聽通過 | 使用者試聽 |
| 2026-10-23 | 遊戲內怪物、法術譯名維持現狀；珍056 的說法只記在 `text/zh056-names.tsv` 與說明書錯譯表 | 使用者回答（「ok 可以喔」，對建議清單） |
| 2026-10-23 | 推廣影片 81 秒（規格 016）看過、接受 | 使用者回答（同上） |
| 2026-10-23 | 完成剩下的項目後 commit、push，打包三平台本機完整版 | 使用者指示 |
| 2026-10-23 | README 截圖可含手札地圖頁與大圖、事件圖的原版／HD 對照（展示成果） | 使用者指示 |
| 2026-10-23 | 結案：Issue #5、#7–#12 註明缺口後關閉；workplace 清掉打包暫存、Go 快取與推廣片錄製畫格（保留 mp4） | 使用者回答 |

## 結案（2026-10-23）

Issue #1–#17 全部關閉。交付：repo `main`、dosgolem 分支 `dosgolem/sosb`、本機 `dist-all/v.1.0.0-20261023/full-local/`
三平台完整版（不散布）、`workplace/promo/sosb-promo.mp4`。已知缺口：

| 項目 | 缺口 | 對應 |
|---|---|---|
| 地圖攻略點 | 礦坑與孿生城堡地下城多層共用地圖，攻略點未標；冰河裂縫、廢墟一帶的雜誌地圖沒有格線 | 規格 009、#9 |
| 切換列 | 發行包顯示已驗；滑鼠移到頂端顯示與逐項點擊未在本作驗證（規格 011 DRAFT） | #10 |
| HD | 第一階段 89 項中 10 項有執行期證據，其餘依家族契約位置接入；透明牆格只收已觀測的 120 種 | 規格 010 |
| 多語系 | 日文、韓文為機器翻譯，未經母語者校對；日韓沒有隊員名音譯表，名字顯示原文 | 規格 015、#11 |
| 組句與半形英數 | 規格 004、005 仍 DRAFT，未在本作逐一觀測 | #7 |
| 發行 | 可散布 patch 包未打、外洩掃描未跑；macOS 只驗結構；Windows 只在 Wine 上跑 | 規格 012、#12 |
| 說明書轉錄 | 7 處字跡不清標〔?〕；轉錄稿只在 workplace | docs/re/006、#5 |

清理後重新打包會重建 `workplace/pkg-stage`、`pkg-gocache`；重剪推廣片要先以 `tools/promo.sh` 重錄畫格。

## 待定

| 項目 | 何時決定 |
|---|---|

## dosgolem 基線

| 項目 | 值 |
|---|---|
| commit | 基底 `8742fa9`（克萊恩英豪 `dosgolem/cok`）；本作分支頂端 `d6c0a4b`，推到本 repo 的 `dosgolem/sosb` |
| Go／image | go1.24.13；`dosgolem-go-ebiten:1.24-r1` `sha256:8ed6bdee2bce…` |
| 冷啟動 | 0 種缺服務；mode 0Dh；首次執行回答 EGA、AdLib、MOUSE、預設存檔路徑，`-program-path 'C:\SECRET\START.EXE'`；空白鍵跳過標題、`p` 進主選單，見 [docs/re/003](docs/re/003-dosgolem-startup.md) |

## 中文化進度

| 路徑 | 狀態 |
|---|---|
| 印字程序 | resident 段 `0650`：路徑 A `035D`、逐字 `01E7`、路徑 B `04B9`，與克萊恩英豪同函式（docs/re/004） |
| 路徑 A／B／C | 已接通；診斷路徑 8 個畫面全部覆繪、範圍外差異 0，非數字未命中 0（docs/re/007） |
| 譯文 | UI 935、ECL 1,498、名稱 868、組句模板 187 筆；字型源泉圓體（`tools/font-dev.sh`） |
| 玩家名音譯 | 性別欄 +0x11F（強推論），預建 6 人全部音譯 |
| 查驗題 | 字序含標題，已證實 2 題（docs/re/004） |
| 手札引用 | 鎮長對白後手札第 37 則自動彈出、F5 翻閱已有收據（docs/re/007）；12 則地圖手札顯示圖面（規格 022） |
| 攻略與地圖 | 攻略 40 段、F6 面板收據（docs/re/008）；地圖疊層 F7 位址已證實、17 塊地區名，攻略點 8 張地圖 298 點，礦坑與地下城待分層（docs/re/009） |
| 前端功能 | sosb-play 冷開機、存讀檔、demo 中止、CPU 速度 1x–32x、切換列字級；我方無敵（F1，docs/re/012） |
| 發行包 | `tools/package.sh`；`v.1.0.0-20261023` 三平台本機完整版只在 `dist-all/`，Linux、Wine 冒煙截圖相同、macOS 驗結構；patch 包未打（規格 012） |
| 閃爍 | 規格 021：閃現量尺 `-flash-audit`；demo 9000 格、手札＋鎮上進金庫 19500 格皆 0；殘影疊字處理原版還原顯存（docs/re/010、規格 021） |
| 手札譯文 | 第 1–72 則修正譯文 `text/journal.zh-TW.tsv`；錯譯表 113 條通過 `tools/errata_check.py`（docs/re/006） |
| 說明書其餘章節 | 上冊 1–74、下冊 1–26 逐格校讀完成、頁碼連續（轉錄稿只在 workplace）；說明書錯譯表 7 條（`text/errata-manual.tsv`）；下冊怪物與法術名稱 131 組與遊戲內對照，異名 63（`text/zh056-names.tsv`，docs/re/006） |
| 查驗題答案 | 30 題 `text/quiz-answers.tsv`，長度全與題目表相符（docs/re/005） |
| 跨畫面盤點 | 鎮上 8 條服務路線、3D 探索 700 步、知識之井戰鬥到全滅，補譯後未命中 0（docs/re/011） |
| 多語系 | 简中、日、韓、英（規格 015）；四語收據記憶體雜湊一致、缺字 0；手札面板五語都有（英文為原版逐字稿），攻略面板沒有英文 |
| 配樂 | 13 首（規格 014），`tools/music_compose.py` 產生，選曲表 `text/music-cues.tsv` |
| 推廣影片 | 81 秒（規格 016），`tools/promo.sh` 錄製、`tools/promo-build.sh` 組裝，成品 `workplace/promo/sosb-promo.mp4` |
| catalog | ui 1,453 筆（658 筆與克萊恩英豪雜湊相同）、ECL 1,528 筆 |

## 原始輸入

| 檔案 | 狀態 |
|---|---|
| `secret-of-the-silver-blades.zip` | DOS v1.30，兩個 PKSFX 展開 49 檔；入口 `START.EXE`＋`GAME.OVR`（`TPOV`）；附預建隊伍；查驗題問手札字與規則書頁碼。見 [docs/re/001](docs/re/001-input-baseline.md) |
| `珍056-銀色匕首之謎.rar` | 24 頁掃描 PDF，上冊規則、下冊含旅行手札第 1–72 則（下冊 p.27–57）；無文字層。見 [docs/re/002](docs/re/002-reference-sources.md) |
| 英文手冊與手札 | mocagh.org 的 journal、manual、refcard、hintbook、errata，OCR 品質中等。見 [docs/re/002](docs/re/002-reference-sources.md) |

## Glossary

- 銀色匕首之謎：本作中文題名，沿用珍056，使用者指定。
- 珍056：軟體世界珍藏版第 56 號，本作的官方繁中說明書，錯譯修正的對象。
- 錯譯表：`text/errata.tsv`，記錄珍056 譯文與修正譯文的對照與證據。
- 手札：說明書中 Adventurer's Journal 的段落，遊戲內以編號引用。_Avoid_：日誌、日記
- 銀刃：Silver Blades 的正文譯名；珍056 作「銀色七首／銀色匕首」。_Avoid_：銀色匕首（只用於題名）
- 字序含標題：本作查驗題「第 N 則第 M 個字」從手札標題第一個字算起（docs/re/004）。
- sosb：本作遊戲短名，用於 dosgolem `apps/sosb/` 與程式識別。
- 克萊恩英豪：第一參考專案，本機 `/home/anr2/cht/golden_box/champions_of_krynn/`，短名 `cok`。
- 覆繪：在原版已輸出的畫面上清除原文墨跡、重畫中文。_Avoid_：替換、打字串補丁
- 收據：dosgolem 以固定輸入重播產生、可重現的執行證據。_Avoid_：截圖證明
- HD 批次：一組交給 Codex 重繪的原版圖塊，含請求與輸出兩個目錄。

### 待定譯名

尚無。

### Flagged ambiguities

- 本機目錄名 `secret-of-the-sliver-blader` 拼錯（sliver、blader），與 repo `secret-of-the-silver-blades-cht` 指同一專案，不改名。
