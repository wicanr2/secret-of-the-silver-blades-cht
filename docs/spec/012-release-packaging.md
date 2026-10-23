# 012 發行包

狀態：READY（2026-10-23）。Issue：[#12](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/12)。
沿用克萊恩英豪 `docs/spec/012-release-packaging.md`（其契約取自幽靈騎士同號規格第 2 節）：Linux AppImage、Windows zip、
macOS universal zip，各分原版與原版＋HD 兩包；本機完整版另附原版遊戲。

## 1. 本作差異

| 項目 | 處理 |
|---|---|
| 腳本 | `tools/package.sh`（由克萊恩英豪移植）；完整版以 `SOSB_WITH_DATA=1` 產生，只放被忽略的 `dist-all/<版本>/full-local/` |
| dosgolem | 已推送的 `dosgolem/sosb` 分支 HEAD，`git archive` 出來建置 `cmd/sosb-play` |
| 字型 | 繁中圓體 2 倍、3 倍與切換列 12／22 像素，简中、日、韓 Unifont，英文 Courier Prime 都由 `tools/font-dev.sh` 重建後複製；繁中 Unifont（可散布包的最後備援）與倚天字型由 `tools/eten_font.py` 產生 |
| 倚天字型借字 | 譯文用到、Big5 沒有的 3 個字借同形字的倚天字模：・ 借 A145（cp950 的 ‧，置中）、裏 借「裡」、～ 借 A1E3（`BIG5_ALIAS`）；其他編不出的字照舊失敗 |
| 手札地圖頁 | `workplace/journal/maps/zh-TW/*.png`（規格 022，由英文手札衍生）只放完整版的 `journal-maps/`；可散布包檢查不得含這個目錄 |
| 讀我 | `docs/release/讀我.txt` |
| 應用程式圖示 | `tools/appicon.py` 以繁中 Unifont 字模畫「銀色匕首」 |

## 2. 冒煙

`tools/release/smoke-linux.sh`、`smoke-windows.sh`、`smoke-macos.sh`，第二個參數選 `patch` 或 `full-local`：

- Linux、Windows（Wine）：空資料目錄冷開機，自動模式第 3200 畫格送空白、3700 畫格送 p 進主選單，第 4400 畫格以 3 倍截圖；
  檢查結束碼 0、原版已匯入 `game/`、沒有缺字。Windows 截圖與 Linux 比對。
- 缺原版：拿掉原版與 `game/` 後應以錯誤結束並留下 `sosb-error.log`。Linux 完整版的原版在 AppImage 內拿不掉，這一項由 Windows 完整版與 patch 包驗。
- macOS：沒有實機，只驗結構（universal Mach-O、Info.plist、必要檔、HD 主題只在 HD 版；完整版另驗原版、倚天字型、手札地圖頁與本機自用說明）。

## 3. 收據（`v.1.0.0-20261023`，本機完整版）

`SOSB_WITH_DATA=1 tools/package.sh v.1.0.0-20261023 all`，dosgolem `d6c0a4b`，go1.24.13。產物只在 `dist-all/v.1.0.0-20261023/full-local/`（被 `.gitignore` 忽略），雜湊在同版本的 `SHA256SUMS.json`。

| 檔案 | 位元組 | SHA-256 |
|---|---|---|
| `SOSBCHT-v.1.0.0-20261023-with-data-x86_64.AppImage` | 7,100,920 | `0d8caa81dc853947c9df898a112c25687efa17d410d06c85f8700e961464f515` |
| `SOSBCHT-v.1.0.0-20261023-hd-with-data-x86_64.AppImage` | 37,231,096 | `55c745c1a1302ffc6c67d285f367f294e9d29f2d20355b0415a60938e5771985` |
| `SOSBCHT-v.1.0.0-20261023-with-data-win64.zip` | 6,708,948 | `a8de5626750677c1ed1e717213e764ec6d84d62e5984d1222f95c2e14ca2f850` |
| `SOSBCHT-v.1.0.0-20261023-hd-with-data-win64.zip` | 37,519,758 | `51a812927a7d6980e80bae688342dd3c98c7edf11ad1da66e549fdbdbb17b71c` |
| `SOSBCHT-v.1.0.0-20261023-with-data-macos.zip` | 9,999,322 | `d3496f5ea84a7cb00fae34780d397e7dec89a454fcc44b19ea106a12b74ff2ea` |
| `SOSBCHT-v.1.0.0-20261023-hd-with-data-macos.zip` | 41,025,706 | `1c9935ce5c2dc48992862328367ce0ffffcfd2ca1d4344c55277fe15a9360da1` |

冒煙（`dist-all/v.1.0.0-20261023/smoke/full-local/`）：

| 平台 | 結果 |
|---|---|
| Linux AppImage（容器內 `APPIMAGE_EXTRACT_AND_RUN`） | 兩包冷開機結束碼 0、匯入 `game/` 50 檔、缺字 0。標題截圖原版 `a7870e9f…`、HD `c4853181…`（差 560,850 像素，HD 有載入）；主選單兩包相同 `6af3a15f…` |
| Windows zip（Wine 9.0） | 兩包冷開機結束碼 0、匯入 50 檔；`-lang zh-TW` 時標題與主選單截圖都與 Linux 逐像素相同。拿掉 `original/` 與 `game/` 後結束碼 1，留下 `sosb-error.log` |
| Windows 語言自動選擇 | 不指定語言時 Wine 回報 en-US，依規格 015 選英文；遊戲畫面 `indexed_sha256` 與 Linux 相同，只有覆繪語言不同 |
| macOS zip（只驗結構） | 兩包 universal（x86_64、arm64）、執行權限、版號、必要檔、HD 主題只在 HD 版、含原版、倚天字型、手札地圖頁與本機自用說明都通過 |

未驗：macOS 實機執行、Windows 實機（只在 Wine 上跑）、可散布 patch 包（這次沒有打包，外洩掃描未跑）。
打 patch 包前要改 `docs/release/讀我.txt` 的 F5 說明：地圖手札的圖面只在本機完整版。
