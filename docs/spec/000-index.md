# 規格索引

狀態：DRAFT → 證據審查 → READY → 實作 → 同狀態驗證 → CONFORMED（`AGENTS.md` 第 7 節）。
本作沿用克萊恩英豪同號規格的契約（`/home/anr2/cht/golden_box/champions_of_krynn/docs/spec/`），
adapter 是由 `apps/cok` 複製的 `apps/sosb`。本表的狀態只算本作已有的證據；克萊恩英豪的 CONFORMED 不代表本作已驗。
本作差異寫在「差異」欄，細節在對應的 `docs/re/`。

| 規格 | 本作狀態 | Issue | 差異 | 證據 |
|---|---|---|---|---|
| 001 路徑 A：Pascal 字串覆繪 | READY | #4、#7 | 簽章遠呼叫位移 `44 06`、`55 00`；執行期 `0650:035D` | docs/re/004、007 |
| 002 路徑 B：ECL 文字視窗覆繪 | READY | #4、#7 | 游標 `DS:7DD4／7DD5`；執行期 `0650:04B9` | docs/re/004、007 |
| 003 路徑 C：底列水平選單 | READY | #4、#7 | 逐字程序 `0650:01E7`；pad 呼叫樣式 `9A 32 00` | docs/re/004 |
| 004 組句訊息 | DRAFT | #7 | 寶物訊息兩段組成；其餘模板沿用、未在本作逐一觀測 | docs/re/007 |
| 005 中文句中的半形英數 | DRAFT | #7 | 未在本作單獨驗證 | — |
| 006 手冊查驗題 | READY | #8 | 題目表 `START.EXE` 0xDCFC、30 筆；字序含標題 | docs/re/004、005 |
| 007 手札面板 | DRAFT | #8 | 72 則珍056 修正譯文；自動彈出與翻閱已在正常玩家路徑驗證；地圖則 12 則的圖面未定；酒店傳聞不適用 | docs/re/006、007 |
| 008 攻略面板 | READY | #9 | 來源《軟體世界》第 21–25 期，40 段；雜誌譯名依 `text/walkthrough-terms.tsv` 換成遊戲譯名 | docs/re/008 |
| 009 地圖疊層 | READY | #9 | GEO 指標 `DS:89CE`、位置 `DS:89D7`（已證實）；17 塊地區名稱依同號 ECL 區塊；攻略點未做 | docs/re/007、009 |
| 010 HD 主題 | READY | #10 | 生圖交 Codex，其餘 Claude；第一階段 89、戰鬥 394、牆面與天空 1,252（共 3 項維持原版）；demo 與鎮上 3 倍＋HD 閃現 0；審閱頁 `review/hd/`；標題流程 3 倍＋HD 閃現 0 | `tools/hd_*.py`、`g16-flicker-probe.sh`（`HD=1 SCALE=3`） |
| 011 切換列 | DRAFT | #10 | 未在本作驗證 | — |
| 012 發行包 | DRAFT | #12 | `cmd/sosb-play` 首次執行寫 `blades.cfg`（冷開機冒煙通過）；打包未開工 | docs/re/003、007 |
| 013 玩家名音譯 | READY | #7 | 性別欄 +0x11F（強推論）；名字接受大小寫混合 | docs/re/007 |
| 014 配樂 | DRAFT | #11 | 未開工 | — |
| 015 多語系 | DRAFT | #11 | 英文手札第 38–72 則仍是 OCR 草稿 | docs/re/006 |
| 016 推廣影片 | DRAFT | #11 | 未開工 | — |
| 017 作弊：我方無敵 | DRAFT | #11 | `partyHead DS:609A` 與紀錄位移仍是克萊恩英豪值 | — |
| 018 開場 demo 控制 | CONFORMED | #13 | 選單逾時 `DS:8A63`、demo 旗標 `67E9`、ECL 停止 `59B4`、存活數 `87CC`；比照幽靈騎士規格 015 | `tools/g13-demo-receipt.sh` |
| 019 CPU 模擬速度 | READY | #14 | 本作是 TP5 版 CRT Delay（`DS:A6E4`）；比照幽靈騎士規格 016；調節模式 8x 實得 3.5x、32x 實得 11.9x（主機負載高） | `tools/g14-delay-equiv.sh`、`g14-toolbar-receipt.sh`、`g14-perf.sh` |
| 021 不露原版 | READY（HD 部分 DRAFT） | #16 | 閃現量尺 0：demo 9000 格、手札＋鎮上 19000 格；殘影疊字處理原版還原顯存 | `tools/g16-flicker-probe.sh`（`-flash-audit`） |
| 020 切換列字級 | CONFORMED | #15 | 小、中、大；12、22 像素字模由源泉圓體渲染 | `tools/g14-toolbar-receipt.sh` |

升到 CONFORMED 的條件：本作正常玩家路徑（建角、存讀檔）的同狀態收據覆蓋該規格的行為。
