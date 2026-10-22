# 004 輸出路徑盤點

日期：2026-10-22。Issue：[#4](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/4)。基線見 [003](003-dosgolem-startup.md)。
位址為 dosgolem 執行期 `段:位移`；「克萊恩英豪」欄引自 `/home/anr2/cht/golden_box/champions_of_krynn/docs/re/004-output-paths.md`。
adapter 是 dosgolem `apps/sosb/`（由 `apps/cok` 複製，`dosgolem/sosb` 分支），覆繪收據用 `cmd/sosb-overlay-shot`。

## resident 印字程序

以克萊恩英豪 adapter 的位元組簽章在 `START.EXE` 找到（`tools/re/sigscan.py`），再以 dosgolem `-find` 在主選單時的記憶體取得執行期位址，
並以呼叫它們的遠呼叫 `9A <位移> <段>` 反推段值 `0650`（路徑 A 81 處、路徑 B 26 處）。三者都在同一個 resident 段。

| 程序 | 本作 `START.EXE` | 執行期 | 克萊恩英豪 | 等級 |
|---|---|---|---|---|
| 路徑 A Pascal 字串印字 | 0x571D | `0650:035D`（線性 `0685D`） | 0x552A／`0631:0353` | 已證實：主選單、隊伍選單、查驗題、角色畫面經過此處 |
| 逐字程序 | 0x55A7 | `0650:01E7`（線性 `066E7`） | 0x53B6／`0631:01DF` | 已證實（`-regs-at` 命中） |
| 路徑 B 文字視窗 | 0x5879 | `0650:04B9`（線性 `069B9`） | 0x5683／`0631:04AC` | 已證實：開場劇情經過此處並重排成中文段落 |

- 路徑 A 簽章前 23 bytes 在 `START.EXE` 另有一處（0x6425，第 28 byte 為 `8A`），`GAME.OVR` 0xA264 也有一處；
  兩處的第 23–29 byte 都不同。本作兩個遠呼叫位移為 `44 06`、`55 00`（克萊恩英豪 `DE 0A`、`51 00`），adapter 簽章已改。
- `tools/re/fn_diff.py` 逐 byte 對齊三個函式：差異只在遠呼叫的位移與段、資料段位移與少數近呼叫。
  路徑 B 的游標欄、列 `DS:6134／6135` 在本作每一處都是 `DS:7DD4／7DD5`；逐字程序的 `DS:6128／612A／612C` 對應 `7DC8／7DCA／7DCC`。
  等級：靜態對齊為強推論；路徑 B 在開場劇情實際以 `7DD4／7DD5` 定位並重排成功，升為已證實。
- 路徑 B 函式尾段（+0x28D 起）與克萊恩英豪不同，但開場劇情的重排與換頁正常；其他視窗形狀待 G6 抽驗。
- 資料段：主選單時 `DS=0EF2`，路徑 A 進入時的 DS 也是 `0EF2`（`-regs-at`）。

## 路徑 C：底列水平選單（已證實）

選單模組在 overlay 執行期段 `43E6`（寶物、角色、冒險畫面時）。返回位址前是 `9A E7 01 <段>`，返回位址後的 bytes 分辨四種呼叫：

| 種類 | 呼叫端 | 返回位址後 | 克萊恩英豪 |
|---|---|---|---|
| selected | `43E6:0276` | `E9 95 00` | `E9 95 00` |
| hotkey | `43E6:02D0` | `EB 3C` | `EB 3C` |
| normal | `43E6:030E` | `8A 46 FF 3A 46 FE` | `8A 46 FF 3A 46 FE` |
| pad | `43E6:037E` | `9A 32 00 <段>`（只比前 3 bytes） | `9A 30 00 <段>` |

同段 `43E6:0EFB` 另有一處呼叫，返回位址後 `C4 7E FC 26 C4 45 2A`，用途未知。
覆繪實測：冒險選單 `MOVE AREA CAST VIEW ENCAMP SEARCH LOOK`、營地選單、寶物選單 `VIEW TAKE POOL SHARE EXIT` 的詞都被辨識並覆繪，範圍外差異 0。

## 診斷路徑：預建隊伍到冒險畫面

正式收據仍要走建角。這條路徑只供盤點，收據 [`tools/g3-party-receipt.sh`](../../tools/g3-party-receipt.sh)。

1. scratch 層的 `SAVE/` 放入原版的 `CHRDATA*`、`SAVGAMA.DAT`，等同安裝程式回答「use our ready-made characters」。
   不放時 `LOAD SAVED GAME` 找不到存檔，回主選單，scratch 只多一個空的 `SAVE/`（程式自建存檔目錄）。
2. 標題畫面送空白鍵到 `PLAY DEMO` 選單，`p` 進主選單；`Down Down Enter` → `LOAD WHICH GAME:` → `A`，6 人隊伍
   （GUY DE VALOIS、PAINE、EPONA、MALACHITE、DOMINIC、MORGAINE）。
3. 隊伍選單 9 項，移到 `BEGIN ADVENTURING` 後 Enter，第一個畫面是手冊查驗題。
4. 答對後是開場劇情（路徑 B），接著鎮長對白、寶物（`EACH CHARACTER RECEIVES 2500 EXPERIENCE POINTS.`、`THE PARTY HAS FOUND TREASURE!`）、
   寶物選單，離開後進 3D 冒險畫面，座標列 `3,3 S 00:00`。

## 手冊查驗題（已證實 2 題）

| 題目 | 答錯 | 答對 |
|---|---|---|
| 手札第 18 則第 4 個字（手札第 30 頁） | `A`（正文第 4 字）→ 換一題 | `SILVER`（含標題 STORY OF THE SILVER BLADES） |
| 手札第 47 則第 3 個字（手札第 37 頁） | `AGO`（正文第 3 字）→ 換一題 | `YULASH`（含標題 MAYOR RELATES YULASH EXPERIENCES） |

- 字序從標題第一個字算起，與克萊恩英豪「從正文算起、不含標題」不同。答錯會換題，不會立刻結束遊戲（試過一次）。
- 題目以路徑 A 印出（`WHAT IS WORD # 4`、`OF JOURNAL ENTRY # 18`、`(JOURNAL, PAGE 30)?`），底列 `ENTER`。
- `GAME.OVR` 另有「(rule book, page」字串，規則書題型尚未出現。

## 手札引用（已證實 1 則）

鎮長對白以兩則路徑 B 字串印出 `HE CONTINUES, AND YOU RECORD IT IN JOURNAL ENTRY ` 與 `37.`，
沿用的 adapter 把單獨的 `37.` 補成「37 則。」，手札面板觸發機制可沿用；面板內容待 G7。

## 組句訊息

寶物畫面的 `EACH CHARACTER RECEIVES 2500 EXPERIENCE POINTS.` 由多段輸出組成，屬規格 004 組句範圍，待 G6 盤點。

## 文字 catalog

`tools/ui_text_catalog.py`、`tools/ecl_text_catalog.py`（移植自克萊恩英豪）：

| catalog | 筆數 | 備註 |
|---|---|---|
| `text/ui-text-events.tsv` | 1,453 | `START.EXE`、`GAME.OVR` 的 Pascal 字串；658 筆與克萊恩英豪已譯字串雜湊相同 |
| `text/ecl-text-events.tsv` | 1,528 | `ECL1`–`3.DAX`，73,675 字元；開場劇情 `ecl.2.17.*` 共 17 段 |

## 未驗證的沿用常數

下列常數仍是克萊恩英豪值，原始碼註解標「克萊恩英豪值」，對應階段前不啟用依賴它的功能：

| 常數 | 用途 | 重驗時機 |
|---|---|---|
| `players.go recordSexOff 0x109` | 玩家名音譯的性別 | G6 |
| `automap.go geoPtrOff、partyXOff` | 地圖疊層 | G8 |
| `cheat.go partyHead DS:609A` 與紀錄位移 | 作弊 | G10 |

## 未知

- 規則書查驗題的出題與答案。
- 戰鬥、商店、神殿、訓練等畫面的呼叫端盤點。
- `43E6:0EFB` 呼叫端的用途。
