# HD 主題

`theme/` 是 HD 版使用的完整主題（規格 [010](../docs/spec/010-hd-theme.md)），共 1,735 項：

| 檔案 | 內容 |
|---|---|
| `theme.json` | 標題、大圖、肖像與場景 89 項 |
| `combat.json`、`actors.json`、`characters.json`、`effects.json`、`encounters.json` | 戰鬥地形、怪物、頭身、效果、3D 遭遇圖 394 項 |
| `walls.json`、`walls/` | 3D 牆面 8×8 圖塊 1,250 個、太陽與地面 |

- PNG 是 3 倍重繪成品：Codex 內建 image_gen 依原版手繪重畫，或沿用克萊恩英豪來源逐位元組相同的成品；JSON 是各家族的比對與繪製規則，`.idx` 是比對用的原版圖色號。
- sosb-play 以 `-hd hd/theme` 載入，只在 3 倍顯示。
- 工作區是 `workplace/hd/`（請求、生成原圖、驗收紀錄，不進版控）；驗收通過後以 `tools/hd_sync.py` 同步到這裡再提交，只帶 JSON 實際引用的檔案。
- `.idx` 衍生自原版圖，依 AGENTS.md 第 3 節例外與成品一起放在本 private repo；repo 轉公開前要連同歷史移除。
