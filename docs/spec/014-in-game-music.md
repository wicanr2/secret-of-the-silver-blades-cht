# 014 遊戲中配樂

狀態：READY（2026-10-23；同日使用者試聽 13 首通過，遊戲內錄音待推廣影片規格 016）。Issue：[#11](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/11)。
沿用克萊恩英豪規格 014（以原版標題曲動機新編 OPL2 配樂，依地圖與戰鬥切換，預設開、可在切換列與 F4 關閉）。
`AGENTS.md` 第 1 節定案表：使用者試聽通過才定案。

## 1. 原版證據

| 項目 | 內容 | 等級 |
|---|---|---|
| 原版音樂 | 只有 AdLib 標題曲：1,726 筆 OPL 寫入、34.8 秒（`cmd/probe -adlib -dump-vgm`，`workplace/probe/g10-music/boot.vgm`） | 已證實 |
| 聲道 | 只用第 0–2 聲道。第 0、1 聲道是旋律與八度、六度和聲，第 2 聲道是低音（第 9.39 秒起） | 已證實 |
| 音色 | 三個聲道同一組：調變 `20=03 40=5B 60=F0 80=1F E0=00`，載波 `20=01 40=81 60=F0 80=1F E0=00`，`C0=0A`（FM、回授 5、衰減率 0 的持續音）。曲中不換音色、不改音量 | 已證實 |
| 節奏 | 十六分音符約 0.193 秒，四分音符約 0.77 秒（約 78 BPM） | 強推論 |
| 調性 | G 小調；第 3.54 秒的終止句用 E 還原（多利安的大六度），第 16.42 秒有 C♯ 鄰音，第 23.48 秒有 F♯ 導音 | 已證實音高；調式名稱是分析者的判斷 |
| 遊戲中 | 沒有背景音樂（克萊恩英豪同一引擎；本作未另做讀檔盤點） | 強推論 |
| 戰鬥結束字串 | `GAME.OVR` 內有 `The party has won`、`The party has fled`、`The monsters rejoice for the party has been destroyed`、`The party makes camp` | 已證實（靜態） |

### 動機

音高取自第 0 聲道（`tools/music_compose.py` 的 `MOTIFS`，以 G 為 0 的半音數記錄）。

| 動機 | 位置 | 音高 | 用法 |
|---|---|---|---|
| A 下行瀑布 | 第 0 聲道第 1–6 音（0.03 秒起） | B♭5 A5 G5 D5 B♭4 G4 | 十六分音符，原曲連降四個八度 |
| B 同音號角 | 第 0 聲道 9.80 秒起 | D4 D4 D4 D4 E♭4 B♭3 | 四個同音後上鄰音拉長，再落三度 |
| C 多利安終止 | 第 0 聲道第 19–24 音（3.54 秒起） | E3 D3 C3 G2 C2 G2 | 大六度下行到 IV 和弦根音 |
| D 導音上行 | 第 0 聲道 23.48 秒起 | F♯3 G3 A3 B♭3 | 和聲小調導音解決後上行 |

## 2. 曲目

| key | 曲名 | 用途 | 循環 |
|---|---|---|---|
| `town` | 新維地格里城 | 鎮上（GEO 1/10） | 是 |
| `ruins` | 舊城廢墟 | 舊維地格里城廢墟（1/20）、黑圈幫總部（1/22） | 是 |
| `well` | 知識之井 | 知識之井地區（1/21） | 是 |
| `mines` | 礦坑 | 礦坑三塊（2/30–2/32） | 是 |
| `depths` | 地下城 | 孿生城堡地下城（2/40–2/42）、半蜘精靈基地（2/44） | 是 |
| `glacier` | 冰河 | 西、東冰河裂縫（3/50、3/52）、寒霜巨人村（3/51） | 是 |
| `finale` | 孿生城堡 | 城堡入口、中層、恐怖魔王的老巢（3/60–3/62） | 是 |
| `battle` | 戰鬥 | 一般戰鬥 | 是 |
| `battle-boss` | 強敵 | 白龍、恐怖魔王、巫妖 | 是 |
| `victory` | 勝利 | 戰鬥勝利訊息 | 否（播完回區域曲） |
| `defeat` | 全滅 | 隊伍全滅 | 否 |
| `camp` | 紮營 | 營地選單 | 是 |
| `sanctuary` | 神殿 | 神殿選單 | 是 |

標題畫面維持原版音樂，不替換。地區對應依 `docs/re/009` 的 GEO 表；礦坑、地下城多層共用一塊 GEO，同一首曲子涵蓋，不需分層。
提爾神殿沒有獨立 GEO（推測與礦坑第一層共用），進去時沿用 `mines`，神殿選單出現時換 `sanctuary`。

## 3. 素材契約（`tools/music_compose.py`，sosb-tools 容器；輸出 `workplace/music/out/`，不進 Git）

- 每首：`<key>.opl`（OPL2 寫入序列，每行 `秒 暫存器 值`，十六進位）、`<key>.wav`（dosgolem `cmd/cok-opl-render` 48 kHz 立體聲，與遊戲內同一顆 Nuked OPL）。
- 只用 OPL2：9 旋律聲道、波形 0–3，不用節奏模式（BDh bit 5）與 OPL3 暫存器。主旋律用原曲音色原樣；
  其他角色（號角、木管、長音、撥弦、低音）由原曲音色改 20h、40h、60h、80h、C0h 衍生，改了哪些寫進 manifest 的 `instruments`。
- 每首由第 1 節的動機發展，manifest 逐次記錄引用的動機、起始拍、實際音高與變化方式。
- 同一聲道不重疊（重疊視為編曲錯誤，產生時中止）。
- 循環曲長度為整數小節（`小節數 × 拍數 × 60 ÷ BPM`），`loop_start` 0、`loop_end` 等於長度；短曲 3–12 秒。
  循環時 bgm 重設合成器並重放循環點前的音色暫存器（克萊恩英豪規格 014 §4），接縫不靠 WAV 交疊。
- 響度：`music.tsv` 的 gain 使各曲 RMS 等於原版標題曲渲染 RMS 的 0.7 倍；渲染峰值不削波。
- 權利註記：衍生自 SSI 原版標題曲的新編曲，隨可散布包私下分享，不公開上架。

## 4. 播放接入

沿用 `apps/sosb/music.go`（`MusicDirector`）與 `apps/sosb/bgm`（由 apps/cok 複製）。觸發表 `text/music-cues.tsv`，
字串取自本作實機盤點（`workplace/probe/**/inv*.tsv` 的路徑 C 整列與路徑 A、B 原文）。

| kind | pattern | 來源 | 等級 |
|---|---|---|---|
| map | GEO 地圖鍵（第 2 節） | `text/map-geo.tsv` 17 塊 | 已證實鍵值；地區名稱強推論 |
| leave | `Move Area` | 3D 移動選單 `Move Area Cast View Encamp Search Look`（盤點 81 次） | 已證實 |
| leave-text | 座標列正規式 `^[0-9]+,[0-9]+ [NESW] [0-9]{2}:[0-9]{2}$` | 路徑 A `3,3 E 00:00`（town1 盤點） | 已證實 |
| battle | `Move View Aim Quick Done`、`Guard Delay Quit` | 戰鬥選單（盤點 484、479 次） | 已證實 |
| battle-text | `Attacks`、`Hitting for`、`and Misses`、`Casts a Spell` | 路徑 B 戰鬥訊息（well2 盤點） | 已證實 |
| boss | `DRAGON`、`DREADLORD`、`LICH` | ECL 原文的怪物名；戰鬥中的顯示名尚未在盤點出現 | 強推論 |
| end | `The party has won`、`The monsters rejoice` | `GAME.OVR` 字串；全滅在 well2 盤點以路徑 B 出現（`The monsters rejoice for the party has been destroyed`） | 全滅已證實；勝利只有靜態字串 |
| menu | `Save View Magic Rest` | 營地選單 `Save View Magic Rest Alter Fix Exit`（盤點 17 次） | 已證實 |
| menu | `Heal View` | 神殿選單 `Heal View Pool Appraise Exit`、`Heal View Take Pool Share Appraise Exit` | 已證實 |

收據：

- `cmd/sosb-music-cues -cues text/music-cues.tsv <inv.tsv>…` 以盤點序列重播選曲（盤點沒有地圖鍵，地圖曲由 AutoMap 提供）。
  well2：戰鬥選單切 `battle`、全滅訊息切 `defeat`；g3-3d、g6-walk、g6-saveload、g6-service 的 camp 與 view：營地選單切 `camp`；
  g6-service 的 temple、temple2：神殿選單切 `sanctuary`。
- `sosb-play -music-dir workplace/music/out` 冷開機 600 畫格正常結束（`workplace/probe/g10-music/load`），13 首的 `music.tsv` 與 `.opl` 讀取無誤。
- 開關關閉時不混入樣本：`apps/sosb/bgm` 單元測試（由 apps/cok 帶來）。
- 遊戲內錄音（鎮上、戰鬥）併入推廣影片規格 016 的錄製流程。

試聽頁：`workplace/music/preview/`（MP3 已套 `music.tsv` 增益，附原版標題曲對照），由 `tools/music_compose.py` 的輸出轉出。

## 5. 已知限制

- 原版只有一組音色，衍生角色是新設計，不是原版音色。
- 強敵與戰鬥勝利的觸發字串只有靜態證據，等 G6 探索走到強敵戰與勝利時補實機盤點。
