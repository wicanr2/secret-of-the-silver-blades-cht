# 011 G6 跨畫面盤點

Issue：[#7](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/7)。日期：2026-10-23。
接續 [007](007-g6-diagnostic-coverage.md)（診斷路徑與正常玩家路徑），補鎮上服務、3D 探索與城鎮外戰鬥。
使用者指示驗證抽樣即可（CONTEXT 決策表 2026-10-23），本輪不窮舉每家店與每種戰鬥。

## 方法

| 工具 | 做法 |
|---|---|
| `tools/g6-service.sh <名稱> "<鍵…>"` | `sosb-overlay-shot` 從鎮上狀態（`g3-receipt/town.state`，3,3 面南）依序送鍵，記全程印字盤點；`SHOTS=0` 不截圖 |
| `tools/g6-explore.sh <名稱> <狀態檔>` | `sosb-explore` 深度優先走遍格子，戰鬥以瞄準近戰推進，選單照 `-pick` 或預設離開，`-yes` 的訊息答 Yes |
| `tools/g6-misses.sh <inv.tsv>…` | 盤點中 `rejected` 含「未命中」的印字，排除純數字、骰子、單一字母、預建隊員名、題名與版本列 |

盤點只留工作區（`workplace/probe/g6-service/`、`g6-explore/`），含原文，不進 Git。

## 鎮上服務

| 路線 | 內容 | 印字 | 未命中 |
|---|---|---:|---:|
| temple-r2 | 走到神殿、答 Yes 進神殿選單、治療選單 | 139 | 0 |
| temple2-r2 | 神殿治療、檢視、金錢池 | 329 | 0 |
| temple-take | 神殿金錢池取錢（選幣種、輸入數量） | 261 | 0 |
| view-r2 | 檢視角色，施放治療與解除（`Heal whom?`、`Cure whom?`） | 317 | 0 |
| camp | 紮營選單：魔法、修改隊伍（次序、剔除、速度、造形、難度）、休息 | 192 | 0 |
| shop | 商店：購買清單（武器、防具、箭、雜貨）、估價 | 332 | 0 |
| tavern | 酒店：點酒選單 | 104 | 0 |
| train | 訓練所：隊伍與建角主選單 | 404 | 0 |

`-r2` 與 temple-take 是補譯文後重跑的同一組鍵（temple-take 少一個 Return，直接進金錢池）。
補譯前的同路線曾出現 6 種未命中，都已補進表：

| 原文 | 處理 |
|---|---|
| `<名字> , how can we help you?` | 模板 `{name} , how can we help you?` |
| `How much Gold  will you take?`、`Gold 4` | 模板：7 種幣 × 4 種動詞的數量提示、`{coin} {n}` 金額列 |
| `Heal whom?`、`Cure whom?`、`<名字>  feels better` | 模板（尾端兩個空白照原文） |

## 3D 探索與戰鬥

| 路線 | 起點 | 送鍵 | 印字 | 未命中 | 結果 |
|---|---|---:|---:|---:|---|
| town1 | 鎮上 3,3 | 700 | 2,090 | 0 | 走過 146 格；路徑 A 1,186、B 183、C 707 |
| well1 | 鎮上，答 Yes 走進傳送門 | 391 | 1,450 | 0 | 卡在戰鬥子選單 `Guard Delay Quit Speed Exit` 反覆選 Exit，停掉 |
| well2 | well1 的戰鬥狀態，子選單改選 Quit | 350 | 6,265 | 2 種 | 與黑圈幫（`BC VETERAN`、`BC NECROMANCER`）交戰後全滅，路徑 B 印 `The monsters rejoice for the party has been destroyed` |

well2 的未命中是 `is Slowed`（6 次）、`is Protected`（2 次），跑到一半時補了 50 條 `is <狀態>` 模板
（Slowed、Protected 已觀測，其餘同式推測），這兩句已在表內。

補譯的介面字串 44 筆（`text/ui-text.zh-TW.tsv`）：神殿、戰鬥、狀態與隊伍次序選單（`Order Drop Speed Icon Level Exit` →「次序 剔除 速度 造形 難度 離開」）等。
戰鬥訊息模板：`takes {n} points of damage`、`breathes Fire` 等（`text/composed-templates.tsv`，共 187 條）。

## 未覆蓋

- 礦坑、地下城、冰河、孿生城堡：需要中後期存檔或傳送，本輪沒有。
- 戰鬥勝利訊息 `The party has won`、強敵戰：只有 `GAME.OVR` 靜態字串（規格 014 §4）。
- 商店只走一家；其他店的商品清單走同一條路徑 A 名稱表，未逐店盤點。酒店傳聞未走。
