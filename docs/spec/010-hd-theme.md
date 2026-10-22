# 010 HD 重繪主題

狀態：READY（2026-10-23；使用者確認 b01 畫風後全量；第一階段 TITLE、PIC、BIGPIC）。Issue：[#10](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/10)。
架構沿用克萊恩英豪規格 010（`/home/anr2/cht/golden_box/champions_of_krynn/docs/spec/010-hd-theme.md`）§1、§5；
來源、位置與色號以本作原版重驗。

## 1. 需求與分工

| 項目 | 定案 | 來源 |
|---|---|---|
| 畫風 | 依原版手繪重畫，風格 B（奇幻插畫），配色照原版；不用演算法放大 | 使用者 2026-10-23（看過濾鏡比較頁後） |
| 倍率 | 3 倍（960×600）；2 倍顯示原版，HD 只在 3 倍 | AGENTS.md 第 1 節 |
| 分工 | 盤點、請求、前處理、驗收、接入由 Claude；生圖由 Codex 內建 `image_gen` | 使用者 2026-10-23 |
| 不露原版圖 | HD 模式下不能先顯示原版圖再換 HD（規格 021） | 使用者 2026-10-23 |

## 2. 來源（`tools/hd_inventory.py` → `workplace/hd/inventory/inventory.json`）

第一階段為 TITLE、PIC、BIGPIC。以（寬、高、色號 SHA-256）去重；動畫以第 0 幀為底，後續幀與第 0 幀 XOR 成狀態。

| 家族 | 尺寸 | 來源區塊 | 去重狀態 | 與克萊恩英豪主題逐位元組相同 |
|---|---|---|---|---|
| TITLE | 320×200、288×88、248×88 | 4 | 4 | 0 |
| PIC | 88×88 | 38 | 77 | 7（PIC4 區塊 6 的 7 幀 ＝ 前作 `pic3-022@0..6`） |
| BIGPIC | 304×120 | 8 | 8 | 0 |

畫面位置（家族契約，以本作截圖驗證）：

| 來源 | 位置 | 證據 | 等級 |
|---|---|---|---|
| PIC1 區塊 83（金庫店員） | (24,24) 88×88 | 鎮上進金庫第 19734 格 | 已證實 |
| PIC1 區塊 82（神殿祭司） | (24,24) 88×88 | 鎮上進神殿第 20496 格 | 已證實 |
| 標題 ＝ TITLE 區塊 2 背景 ＋ 區塊 4 字樣貼在 (40,40) | (0,0) 320×200 | 冷開機第 2400 格，全幅逐色號相同 | 已證實 |
| 其餘 PIC、BIGPIC | PIC (24,24)、BIGPIC (8,8) | 未觀測 | 家族契約 |

未觀測的來源只做條件式覆蓋：畫面上該位置整塊色號吻合才換圖。

## 3. 流程與工具

| 步驟 | 工具 | 產出 |
|---|---|---|
| 盤點 | `tools/hd_inventory.py` | `workplace/hd/inventory/inventory.json` |
| 請求 | `tools/hd_request.py` | `workplace/hd/requests/<批次>/`：1 倍、3 倍參考、`.idx`、動畫遮罩、`manifest.json`（含提示詞） |
| 生圖 | `codex exec`，提示詞 `workplace/hd/prompts/<批次>.md` | `workplace/hd/out/<批次>/<key>-rN-raw.png`、`jobs/<key>-rN.json` |
| 前處理 | `tools/hd_prepare.py` | 整幅 LANCZOS 縮到 3 倍、不透明 RGBA；動畫只取遮罩外擴 6 像素；前作相同來源直接沿用 |
| 數值驗收 | `tools/hd_validate.py`（`hd_compare.py`） | 結構分數 ≥ 0.40、色相差中位 < 30 度、尺寸、alpha、遮罩外差異 0 |
| 目視 | 並列比較頁 | 綁定 PNG SHA-256；未目視或雜湊改變不得接入 |
| 主題 | `tools/hd_theme.py` | `workplace/hd/theme/theme.json`（第一階段 89 項） |
| 審閱頁 | `tools/hd_review_md.py` | `review/hd/README.md`：原版 3 倍與 HD 預覽並列，private repo 審閱用 |

風格參考圖：克萊恩英豪已定版的 `workplace/hd/out/b01/camp.png`（複製到 `workplace/hd/style/krynn-b01-camp.png`），只取筆觸。

## 4. 接入與不露原版圖

- dosgolem `apps/sosb/hd.go` 的圖面 watcher（由克萊恩英豪移植，已在本作分支）：整塊原版色號吻合才畫 HD，只在 3 倍。
- 主題圖 watcher 設 `Sticky`（dosgolem 規格 204 §6），並以 `Hold`（202 §2.8）保留正在畫的已知圖，見規格 021 §4.1。
- 主題由 `tools/hd_theme.py` 組成 `workplace/hd/theme/`，sosb-play `-hd` 載入。

## 5. 驗收

1. 數值閘門與逐張目視全部通過才進主題。
2. 3 倍＋HD 收據：證據畫面改變；2 倍同輸入與原版相同；原版記憶體與色號雜湊不受 HD 開關影響。
3. 規格 021：3 倍＋HD 跑 `tools/g16-flash-receipt.sh` 的路線，閃現 0。

## 6. 進度

| 批次 | 內容 | 狀態 |
|---|---|---|
| b01 | 標題、金庫店員、神殿祭司、BIGPIC1 區塊 112 | 數值與目視通過；使用者 2026-10-23 確認畫風 |
| b02–b05 | 其餘 PIC 75 狀態（含沿用前作 7）、BIGPIC 7 | r0：69 張通過；13 張未過（動畫非第 0 幀紋路跟著第 0 幀、矮人改成寫實配色），r1 加強提示詞重畫後全過 |
| b06 | SSI 片頭（TITLE 1）、背景（TITLE 2）、背景＋Forgotten Realms 字樣（TITLE 2＋3 @ (16,40)） | 數值與目視通過；冷開機第 300、800、1500 格為證據 |
