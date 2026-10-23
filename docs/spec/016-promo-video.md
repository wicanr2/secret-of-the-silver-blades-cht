# 016 推廣影片

狀態：READY（2026-10-23，待使用者觀看）。Issue：[#11](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/11)。
沿用克萊恩英豪規格 016（使用者 2026-10-19 指示：60–90 秒精華，3 倍畫面加 HD，原版 AdLib 聲音，MP4（H.264），放 `workplace/promo/`，不進 Git；
2026-10-21 加故事背景字卡與 HD 切換示範）。

## 1. 錄製

dosgolem `cmd/sosb-promo`（`41f6c7f`，由 cok-promo 移植，加 `-journal-maps`）從狀態檔續跑，逐格輸出覆繪後的 3 倍畫面（PNG）與音訊
（48 kHz 立體聲 s16le），另寫 `receipt.json`。時間基準同 sosb-play：每秒 `VGAFrameEvery×70` 步，本作狀態檔是每秒 11,550,000 步。
`tools/promo-rec.sh` 包一段的 docker 執行，`tools/promo.sh` 錄全部段落再呼叫 `tools/promo-build.sh`。

本作與前作不同的地方：

| 項目 | 處理 | 等級 |
|---|---|---|
| 標題曲 | 標題曲在第 43M 步讀 `SOUND.dax` 時寫入音色；狀態檔不含 OPL 暫存器，從第 300M 步的狀態錄，音色全為 0、整段靜音（-85 dB）。改從冷開機第 40M 步存的狀態起錄（`workplace/probe/g10-promo/boot-40m.state`，cmd/probe 回答設定後 `-save-state`） | 已證實 |
| 隊伍欄 | 狀態檔載入前印的隊伍欄沒有覆繪；鎮上先紮營再離開讓遊戲重印 | 已證實 |
| 戰鬥 | 知識之井的黑圈幫戰鬥（`g6-states/well-fight`），每 15M 步送 Q（電腦控制） | 已證實 |

## 2. 分鏡

| 段 | 狀態檔 | 步數 | 內容 |
|---|---|---|---|
| title | `probe/g10-promo/boot-40m.state` | 41M–460M | SSI、冰封城堡、Forgotten Realms、銀色匕首標題（HD），原版標題曲 |
| open | `probe/g3-receipt/intro.state` | 835M–1,720M，Enter 從 840M 每 40M | 山谷旁白、市長對白、手札第 37 則自動彈出、選單 |
| town／town-nohd | `probe/g3-receipt/town.state` | 1,722M–2,290M；E、E、M 後走 13 步 | 鎮上 3D、地圖疊層全圖與攻略點、攻略第 1 章 |
| battle／battle-nohd | `probe/g6-states/well-fight/fight.state` | 10,826M–11,030M | 戰鬥 HD 圖塊與中文戰鬥訊息 |
| f12 | 同 open | 955M–1,045M，982M 切原版、1,015M 切回 | 市長對白的中文與英文原版切換 |
| langs | 同 open | 955M–1,045M | 依序換成简中、日文、韓文、英文 |

剪輯（`tools/promo-build.sh` 剪輯表）：標題 9 秒 → 故事字卡四張各 3.6 秒（內容依手札第 18、37 則繁中定稿，配 `ruins`）→
開場四片段 → 3D 探索 → 3D 的 HD 切換（原版段與 HD 段同時間軸，40% 處擦除）→ 地圖疊層 → 攻略 → 戰鬥 → 戰鬥的 HD 切換 → F12 → 換語言 → 片尾 6 秒（`finale`）。
開場的山谷旁白沒有遊戲配樂，墊 `well`；墊底的渲染檔乘上 `music.tsv` 的 gain，與遊戲內同響度。

## 3. 編碼

同前作：2 倍最近鄰放大到 1920×1200，30 fps，libx264 `-preset slow -crf 18`、yuv420p，AAC 192 kb/s，字卡 Noto Sans CJK TC，映像 `cok-ffmpeg:r1`。

## 4. 收據（2026-10-23）

- 成品 `workplace/promo/sosb-promo.mp4`：81.0 秒，H.264 1920×1200 30 fps 加 AAC。
- 各段 `audio_seconds` 等於 `video_seconds`，缺字 0；HD 段載入 1,735 項，原版段 0 項。
- 全片每 4 秒平均音量 -19 到 -30 dB，沒有靜音片段。
- 分鏡檢查（`tools/promo-sheet.sh`）：隊伍欄、戰鬥面板、劇情與選單都是覆繪後的中文；各段第 0 格是狀態檔載入前的英文，剪輯不取。

## 5. 已知限制

- 換語言後再換回繁中，隊員名維持英文原文，直到遊戲重印隊伍欄（日韓英沒有隊員名音譯，切過去時疊字被移除，切回來不會補回）。成片在切回繁中前結束。
- 鎮上段的手札面板顯示「尚未記錄」：錄製器不讀已讀手札紀錄，這段不剪入。
