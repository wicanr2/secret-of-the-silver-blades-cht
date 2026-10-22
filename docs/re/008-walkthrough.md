# 008 遊戲內攻略

日期：2026-10-22。Issue：[#9](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/9)。契約沿用克萊恩英豪規格 008（攻略面板）。

## 來源

《軟體世界》第 21–25 期〈銀色匕首之謎〉攻略，作者 Lord Jean，共 22 頁。掃描在 `walkthrough/`（不進 Git），
逐頁對圖校讀的轉錄在 `reference/walkthrough-zh/softworld-21.md`–`softworld-25.md`，雜誌原用譯名與錯字照原樣保留。

| 期 | 雜誌頁碼 | 章 |
|---|---|---|
| 21 | 61–64 | 新維地格里城、知識之井、龍之寶庫 |
| 22 | 42–48 | 黑圈幫總部、提爾神殿、礦坑 1–10 層 |
| 23 | 45–48 | 孿生城堡地下城 10–1 層 |
| 24 | 22–24 | 半蜘精靈基地、西冰河裂縫、寒霜巨人村 |
| 25 | 24–27 | 東冰河裂縫、孿生城堡入口、中層、恐怖魔王的老巢、結語 |

## 產生

`tools/walkthrough_build.py`（由克萊恩英豪移植）把轉錄檔轉成 `text/walkthrough.zh-TW.tsv`：14 章、25 張地圖圖例、結語，共 40 段。
各章的地圖圖例緊接在該章之後。

```
docker run --rm ... sosb-tools:bookworm-r1 python3 -I tools/walkthrough_build.py \
  --src reference/walkthrough-zh --out text/walkthrough.zh-TW.tsv --terms text/walkthrough-terms.tsv
```

雜誌譯名在產生時依 `text/walkthrough-terms.tsv` 換成遊戲譯名，轉錄檔不動。對照的依據是術語表，術語表沒有的以遊戲英文原文
（`workplace/text-src/ecl-text-source.tsv`）判斷：

| 雜誌 | 遊戲 | 依據 | 等級 |
|---|---|---|---|
| 煙霧巨人 | 雲巨人 | 原文 `the cloud giants and white dragons`，雜誌同處寫煙霧巨人與白龍 | 強推論 |
| 狂暴巨人 | 風暴巨人 | 原文 `storm giants`；雜誌寫巨人不斷射出閃電 | 強推論 |
| 長毛象 | 乳齒象 | 原文 `giants and mastodons` | 強推論 |
| 火焰蟲 | 雷莫哈茲 | 原文 `remorhaz burst through the walls`；雜誌寫一口吞下隊員 | 強推論 |
| 地底熊 | 土巨怪 | 原文 `umber hulks burst from the walls`；礦坑圖例代號 U | 強推論 |
| 12頭龍、十二頭龍、十六頭龍 | 火焰九頭蛇 | 原文只出現 `pyro-hydras` 與一次 `hydra` | 強推論 |
| 莎迦莎 | 薩加莎 | 原文 `the medusa Sargatha` | 已證實 |

雜誌的「巫師」與「魔法師」在同一句並列（例「七名雙頭怪，三名魔法師和一名巫師」），不合併。

## 面板收據

`tools/g8-guide-receipt.sh`：sosb-play 冷開機到主選單，以腳本動作 `guide`、`next` 開攻略面板（dosgolem `cmd/sosb-play` 新增，
不改 F 鍵名在腳本裡送進 DOS 的行為）。

| 組合 | 畫面 | 截圖 SHA-256 |
|---|---|---|
| open | 目錄第 1／2 頁 | `3812d4e7…` |
| next | 第 1 段 | `5e109cbc…` |
| far | 第 25 段（地下城 4～1 層圖例），頁尾「軟體世界 23 期 p.48」 | `b47365e6…` |

字型由 `tools/font-dev.sh` 重建，攻略的 `source` 欄也收字（頁尾顯示出處）。三組合都沒有缺字。

遊戲中（新維地格里城）開關面板、與手札互斥的收據在 [007](007-g6-diagnostic-coverage.md) 的正常玩家路徑一節。

雜誌錯字（例「要霧巨人」「寒寒巨人村」「Forgotton Realm」）在 `walkthrough-terms.tsv` 以 reason「雜誌誤植」標記，
產生時先整段替換，括號內的英文也修。

## 未做

- 各章對應的遊戲地區（克萊恩英豪規格 009 地圖疊層的攻略點）。
