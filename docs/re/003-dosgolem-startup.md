# 003 dosgolem 冷啟動基線

日期：2026-10-22。Issue：[#3](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/3)。輸入見 [001](001-input-baseline.md)。

## 固定版本

| 項目 | 值 |
|---|---|
| 基底 | 克萊恩英豪 `origin/dosgolem/cok` 頂端 `8742fa96fadff249cdf3c4a2a7b8d878b9dc1526` |
| 本作分支 | `workplace/dosgolem/` 的 `secret-of-the-silver-blades-cht`，推到本 repo 的 `dosgolem/sosb`；目前頂端 `9112c61` |
| Go | go1.24.13 linux/amd64 |
| image | `dosgolem-go-ebiten:1.24-r1`（`sha256:8ed6bdee2bce1f32f804e888f942b25bbf62f2165a43344bb4587f3371de0581`） |
| 執行入口 | dosgolem `tools/go.sh`（`--rm`、`--network none`） |

選 `dosgolem/cok` 的理由：本作範圍比照克萊恩英豪，該分支已有 HD 主題、切換列、字型倍率、多語系、配樂與發行模式的通用層。
dosgolem `main`（`81c85be`）沒有這些；`san5-*` 分支的較新通用規格日後需要時再個別移植。
module cache 由克萊恩英豪 clone 的 `workplace/gomodcache` 複製，未開網路。

## 通用層修正

`cmd/probe` 的 `-program-path` 被其後的預設指派覆寫，旗標從未生效（`cc1ef56` 加旗標，`6ab4f95` 的預設指派留在後面）。
`9112c61` 改成只有旗標為空時才用預設。克萊恩英豪的工具沒有用這個旗標，既有收據不受影響。

## 首次執行設定（已證實，dosgolem 收據）

壓縮檔沒有 `blades.cfg`，程式在文字模式 03h 依序詢問：

| 順序 | 提示 | 選擇 |
|---|---|---|
| 0 | `TANDY 1000 USERS - Make sure NUMLOCK is on.` | 不需輸入 |
| 1 | `GRAPHICS ADAPTER TYPE: [1] CGA [2] EGA [3] Tandy` | `2` |
| 2 | `SOUND TYPE: [1] AdLib [2] Tandy 1000 [3] PC speaker [4] Silent` | `1` |
| 3 | `ALTERNATE INPUT TYPE: [1] JOYSTICK [2] MOUSE [3] NEITHER` | `2` |
| 4 | `PATH TO SAVE DATA (DEFAULT - <目前目錄>\SAVE):` | Enter |

寫出的 `blades.cfg` 前四行 `E`、`A`、`M`、`C:\SECRET\SAVE\`，其後 `F` 與 13 行 `0`，格式同克萊恩英豪的 `KRYNN.CFG`。
預設存檔路徑由目前目錄組成；不給 `-program-path` 時 dosgolem 的預設目錄是 `C:\RICH2`，會得到 `C:\RICH2\SAVE\`。

## 冷啟動觀察（已證實）

| 步數 | 事件 |
|---|---|
| #3,000,000 | NUMLOCK 提示（模式 03h） |
| #9,000,000 | 顯示卡選單 |
| #31,706,722 | 切到 0Dh（EGA 320×200 16 色 planar） |
| #59,000,000 | SSI／AD&D 標誌 |
| #150,000,000 | 標題圖（冰封城堡） |
| #299,000,000 | 標題字「A Forgotten Realms Fantasy Role-Playing Epic Vol. III」 |
| #399,000,000 | 建立隊伍主選單 CREATE NEW CHARACTER、ADD CHARACTER TO PARTY、LOAD SAVED GAME、INITIALIZE MOUSE/JOYSTICK、EXIT TO DOS，底列 `CHOOSE A FUNCTION SELECT` |

- 沒實作的服務：0 種。寫過的 I/O 埠：040、043、061、0C0、388、389、3C4、3C5、3CE、3CF、3D4、3D5。
- 不送鍵時標題後直接進主選單，沒有 demo 選單。
- 程式以讀寫模式開 DAX，dosgolem 把它們複製到 scratch 層（`009-scratch-writes`）；原版目錄唯讀不變。

## 收據

[`tools/g2-startup-receipt.sh`](../../tools/g2-startup-receipt.sh)：冷啟動並回答設定到 #300,000,000 存狀態，從狀態重播兩次到 #399,000,000。

| 產物 | SHA-256 |
|---|---|
| `scratch/blades.cfg` | `00cbd89ee14e59022941a6a5fe3c5107cf8d26b27dc60c096174a091d55923b3` |
| `title-300m.state` | `16a0bc0f67c66f9fd53b8a6976cfdf58d28dd733d799e379e89ef84b65a43be0` |
| 主選單色號陣列 `menu-*.bin` | `f3215354429d04c7ae82cf96c73bafd17ab43dd471a526fb51c3b686e5ec1dcd`（重播 a、b 相同） |

## 與克萊恩英豪的對照

| 項目 | 本作 | 克萊恩英豪 |
|---|---|---|
| 視訊模式 | 0Dh | 0Dh |
| overlay 魔數 | `TPOV` | `FBOV` |
| 設定檔 | 首次執行建立 `blades.cfg` | 原版附 `KRYNN.CFG`，需改 AdLib |
| 進主選單 | 不需按鍵 | 送 `p` |

## 未知

- `blades.cfg` 第 5 行 `F` 與後續 `0` 欄位語意。
- `install.com` 沒有在 dosgolem 執行過。
