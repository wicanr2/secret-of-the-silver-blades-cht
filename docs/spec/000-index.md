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
| 009 地圖疊層 | DRAFT | #9 | `geoPtrOff`、`partyXOff` 仍是克萊恩英豪值；本作沒有 `map-geo.tsv`、`map-guide.zh-TW.tsv`，F7 不啟用 | docs/re/007 |
| 010 HD 主題 | DRAFT | #10 | 未開工 | — |
| 011 切換列 | DRAFT | #10 | 未在本作驗證 | — |
| 012 發行包 | DRAFT | #12 | `cmd/sosb-play` 首次執行寫 `blades.cfg`（冷開機冒煙通過）；打包未開工 | docs/re/003、007 |
| 013 玩家名音譯 | READY | #7 | 性別欄 +0x11F（強推論）；名字接受大小寫混合 | docs/re/007 |
| 014 配樂 | DRAFT | #11 | 未開工 | — |
| 015 多語系 | DRAFT | #11 | 英文手札第 38–72 則仍是 OCR 草稿 | docs/re/006 |
| 016 推廣影片 | DRAFT | #11 | 未開工 | — |
| 017 作弊：我方無敵 | DRAFT | #11 | `partyHead DS:609A` 與紀錄位移仍是克萊恩英豪值 | — |

升到 CONFORMED 的條件：本作正常玩家路徑（建角、存讀檔）的同狀態收據覆蓋該規格的行為。
