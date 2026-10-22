# 019 CPU 模擬速度

狀態：READY（§4 第 1–3 項通過；第 4 項已量測，主機負載高，數字偏保守）。Issue：[#14](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/14)。
由幽靈騎士規格 016 移植（`/home/anr2/cht/golden_box/death_knight_of_krynn/docs/spec/016-cpu-speed-draft.md`）；
通用層契約見 dosgolem `docs/spec/429-runtime-clock-and-idle-skip-draft.md`。

## 1. 需求

使用者要求（2026-10-22）：CPU 模擬速度可以調整，照幽靈騎士的定案做。

| 項目 | 定案 |
|---|---|
| 倍率 | 1x、2x、4x、8x、16x、32x，由切換列下拉選單設定；記住上次倍率（偏好檔 `sosb-speed.txt`） |
| 語意 | 加快 CPU 模擬：遊戲時鐘、訊息停留、動畫照原版，只有運算密集處變快 |
| 主機跟不上 | 30fps 優先，自動調節實際倍率，下拉選單第一列顯示實際倍率 |
| 快速鍵 | 不加 |
| 切換列文字 | 只顯示倍率（例「8x」）；倍率項合成一項、不另列「無HD」（使用者 2026-10-22 選定） |

## 2. 本作差異

| 項目 | 內容 | 等級 |
|---|---|---|
| CRT Delay | 本作是較舊版 Turbo Pascal CRT：`Delay` 在鎮上記憶體線性 `0CB2E`，`DelayCnt` 在 `DS:A6E4`；DelayLoop 為 `cmp al,es:[di] / jne / loop`，每圈 3 步，ES:DI＝0000:0000 | 已證實（記憶體傾印反組譯） |
| 通用層擴充 | dosgolem `tpcrt.FindDelay` 認 TP7 與 TP5 兩種簽章；`Machine.SetTPDelay` 依迴圈位元組判斷寫法（規格 429 §2.2、§2.4） | 已證實（單元測試：TP5 快轉與逐條執行在每個邊界狀態相同） |
| 登記 | sosb-play 綁定覆繪後以簽章找到 `Delay`，登記後才套用設定倍率（開機以 1x 校準 `DelayCnt`） | 已證實（收據 log「TP Delay 登記 true」） |

## 3. 契約

同幽靈騎士規格 016 §3：倍率 `m` 的時脈為 `-clock × m`（上限 1600%）；大於 1x 時每格以 1x 預算分段推進，
單格模擬超過 25 ms 不再推進；指數平均調節實際倍率；自動模式（`-frames`）固定為設定倍率；
旗標 `-speed`、`-delay-accel`、`-perf`、`-speed-adaptive`；腳本動作 `speed=m`、`speeds`。

## 4. 驗收

1. 單元測試：machine（TP5 快轉等價）、tpcrt（TP5 簽章）、session、mixer、sosb-play（速度控制、偏好檔、選單、腳本、選單不超出右緣）。通過。
2. 實機等價性 `tools/g14-delay-equiv.sh`（2026-10-22 通過）：1x、手札收據同一路徑跑到第 15000 格，快轉開與關的
   記憶體 SHA `62a78270…`、色號畫面 SHA `260c82fb…`、截圖 SHA `8dcab529…` 相同；快轉 78,659,145 步（約占 5%），
   這條路徑牆鐘 262 秒對 251 秒，差距在主機負載誤差內。
3. 切換列收據 `tools/g14-toolbar-receipt.sh`（2026-10-22 通過目視）：速度項顯示「8x」「32x」；下拉第一列灰色實際倍率、
   目前設定青色；3 倍 32x 時選單在右緣往左移、完整顯示。log 記「TP Delay 登記 true」。
4. 調節模式量測（`tools/g14-perf.sh`，2026-10-23）：自動模式加 `-speed-adaptive`，3 倍、開場 demo 6700 格，Docker＋Xvfb 2 核，序跑。
   當時本作還沒有 HD 主題，3 倍只放大原版。

   | 設定 | 模擬平均 / p50 / p90 | 每秒畫格 | 平均實際倍率 | 牆鐘 | 主機負載（開始 → 結束） |
   |---|---|---|---|---|---|
   | 1x | 11.6 / 11.4 / 22.1 ms | 47.1 | 1.00x | 142 秒 | 6.5 → 19.3 |
   | 8x | 21.3 / 17.3 / 45.7 ms | 24.2 | 3.54x | 277 秒 | 19.3 → 46.8 |
   | 32x | 26.4 / 18.7 / 58.5 ms | 18.7 | 11.91x | 359 秒 | 46.8 → 33.3 |

   - 每秒畫格是自動模式的更新次數（`updatefps`）。自動模式在 Xvfb 下不呼叫 Draw，`drawfps` 為 0，畫出 fps 沒有量到。
   - 8x、32x 執行時主機負載升到 30–47（其他專案的工作），實際倍率受主機限制；空閒主機與實體顯示卡未量測。
