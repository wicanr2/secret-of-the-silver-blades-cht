# 001 原始輸入基線

日期：2026-10-22。Issue：[#2](https://github.com/wicanr2/secret-of-the-silver-blades-cht/issues/2)。
工具：`tools/inventory.py`，在 `sosb-tools:bookworm-r1`（`tools/docker/tools.Dockerfile`，Info-ZIP UnZip 6.00）內以
`--network none` 執行；輸出 `workplace/input/inventory.json`，遊戲檔展開在 `workplace/input/dos/sosb/`。

## 壓縮檔

| 檔案 | SHA-256 | 內容 |
|---|---|---|
| `secret-of-the-silver-blades.zip` | `b3147db0076bf6888f5125c80b0d9c02cbd89f82d60324b3dd85f3adcaae29f7` | `install.com`、`secret1.exe`、`secret2.exe`、BBS 廣告 `bbsad.txt`、`dsklabel.txt`（「Label of Disk 2 is - SECRET」） |
| └ `secret1.exe` | `94593b089cf553e950c55bbc5c1b70b4f660dd7c40110c553971d3ab13550b45` | PKSFX（PKWARE 1989–1990），28 個成員 |
| └ `secret2.exe` | `8818714f061b39530680207c393e4471dde74d4852b4a23d221b3c4306b8f9dc` | PKSFX，21 個成員 |

- 兩個 PKSFX 使用 PKZIP 1.x 的 implode，Python `zipfile` 無法解，改用 Info-ZIP `unzip`。兩者成員不重名，合計 49 檔。
- `install.com` 的字串引用 `secret1.exe`、`secret2.exe`，要求 1.5 MB 硬碟空間，並詢問是否使用預建隊伍。
  安裝程式本身沒有在 dosgolem 跑過；本專案以展開結果作為遊戲目錄。

## 版本與入口

| 項目 | 值 | 證據 | 等級 |
|---|---|---|---|
| 版本 | 1.30 | `START.EXE` 字串「Secret of the Silver Blades ... Version 1.30」 | 已證實 |
| 入口 | `START.EXE`＋`GAME.OVR` | `GAME.OVR` 開頭 `TPOV`（Borland Turbo Pascal overlay）；兩檔日期 1990-09-28 | 已證實 |
| 設定檔 | `blades.cfg` | `START.EXE` 字串；壓縮檔內沒有此檔，推測首次執行時建立 | 強推論 |
| 音效 | 選單有「SOUND TYPE: [1] AdLib」 | `START.EXE` 字串 | 已證實 |
| 預建隊伍 | `CHRDATA1`–`6.SAV`、`SAVGAMA.DAT`、`ITEMS` | 檔名與 `install.com` 預建隊伍提示 | 強推論 |
| 查驗題 | 問手札第 N 則第 M 個字，或規則書頁碼 | `GAME.OVR` 字串「what is word #」「of journal entry #」「(journal, page」「(rule book, page」 | 已證實 |

克萊恩英豪的 overlay 魔數是 `FBOV`，本作是 `TPOV`，overlay 管理方式不同，輸出路徑假說要另外驗。

## 遊戲檔

| 檔案 | 大小 | SHA-256 | 來源 |
|---|---|---|---|
| `8X8D1.DAX` | 22557 | `e6cf50dabff7b77b39ca0c8457ad8332bc242405104ed113e62249fce31ba1c9` | secret1.exe |
| `8X8D2.DAX` | 13375 | `9dad1339f9558b8f6ad3806fa77eaed9bc7651fa73c7ef90d8f9685c63a195fd` | secret2.exe |
| `8X8D3.DAX` | 11038 | `c1d327dd8fd9fd6fddf1d7d71fcc2a4207e46775f0197bb8668433e6e01178a9` | secret2.exe |
| `8X8D5.DAX` | 1352 | `5a2ed0104eb77c9d1890a33f9086771f52ffe453e00ff8ff62bef1cd7558210a` | secret1.exe |
| `BIGPIC1.DAX` | 36077 | `bb282c245118cfd65caf34b01b24925405c99798859dfcd1eddfab0796659c3f` | secret1.exe |
| `BIGPIC2.DAX` | 33570 | `1598d11d529f2e46da8977ca6ed6a9d2a2c1fb15bceaab8187e55979cddf6132` | secret2.exe |
| `BIGPIC3.DAX` | 68082 | `7ba997802310b3ab35ab2f1273de57eca763638d38dcbebadbaa3c996624e356` | secret2.exe |
| `CBODY.DAX` | 23889 | `0c93206b020e30eecc1f761a9408b5befc20113fde18a8b401ae2ddad2c103bd` | secret1.exe |
| `CHEAD.DAX` | 3428 | `8e61d8cf23b7094353425224f02be4423b880c5e8a7e168d478ec851bfaea568` | secret1.exe |
| `CHRDATA1.SAV` | 439 | `99084d6bb280a75bb1da6b7a874dce5c4031a1b76fc7662036b469d9ac003056` | secret2.exe |
| `CHRDATA1.SFX` | 9 | `db38c958698b142a3730cba086919e59cbb3673f42e450f5de482961d3947b7b` | secret1.exe |
| `CHRDATA2.SAV` | 439 | `7d0f45141e548ccc5fff877886368f603671f007ebbddbd1fe2dd98b99d807da` | secret2.exe |
| `CHRDATA2.SFX` | 9 | `a1211b1b6107851b47ead67928af61da8b285378cf8370267eeda743b518aee0` | secret1.exe |
| `CHRDATA3.SAV` | 439 | `c47bd5382c120fdd09717ffb1515dfcf46ad75fee02add5e3130cca329fab4ed` | secret2.exe |
| `CHRDATA4.SAV` | 439 | `8d76566a5c4c74cd80855d3a418a9767076e1b22c02d6d8abb48619ca74f9c62` | secret1.exe |
| `CHRDATA4.SFX` | 27 | `69676667f3daadc7eceed8528a7828846ba047f2dffb14303d272aa18efb32b3` | secret1.exe |
| `CHRDATA5.SAV` | 439 | `18a9e00655d48541a4f3118cff799a764ee066b6d425004be82e034928f788ef` | secret1.exe |
| `CHRDATA6.SAV` | 439 | `19d95943bca4259eebf67e8a8e74b0865d6cce359faf08fcb005f18305dfd4ce` | secret1.exe |
| `COMSPR.DAX` | 3612 | `6bff177f6776339a627be3c0199518a41330f01f462e8994f649804e488a86d5` | secret1.exe |
| `CPIC1.DAX` | 47967 | `c4584b534f25d7cf89bbe7216bc6ec26faf9ad20aad68c1323a680a71702f418` | secret2.exe |
| `DUNGCOM.DAX` | 6589 | `070a696918593c2e3c21b2db08c71e9a4d74cafe368a873fc78e3319d91b38f4` | secret2.exe |
| `ECL1.DAX` | 31457 | `0ca71650d078e401743672d7882f5c995476f36a46cd04e8c57d573514faa9c8` | secret1.exe |
| `ECL2.DAX` | 62236 | `cc16244273d36b06b32e11f58a2d6307db7e99f610f42ecbc49dc485197d5710` | secret2.exe |
| `ECL3.DAX` | 47705 | `62e2a130882bdef6b531216372533faa94887905fc1e3e7a6cf0e4182951bd21` | secret2.exe |
| `GAME.OVR` | 278528 | `9b01e970b87e32fe1de608e5c431a83bd1739b7a7fe4acea1231eebf15ff1703` | secret1.exe |
| `GEO1.DAX` | 3890 | `27efe6936da5d4a119d4b5e1cd78267360822755b0c5d417fc882a9054ae7416` | secret1.exe |
| `GEO2.DAX` | 6333 | `63576d743c1482944bf6b9da7eeecb96f79ed3a7323d542fcbbcb56f7d588087` | secret2.exe |
| `GEO3.DAX` | 5260 | `54594e9898c9867f518cee7141378c3dfc041182a3944f92ff4b7bc6ede00976` | secret2.exe |
| `ITEM1.DAX` | 3972 | `6c6cb5eadbf6f8f85bb329c9a28f991978370e0d3c76570939421cd516a616c6` | secret1.exe |
| `ITEM2.DAX` | 2413 | `eb23ac633e0e2f70e6f329bd2443342693bd6c5d70446c3e3c6908ab8e621991` | secret2.exe |
| `ITEM3.DAX` | 833 | `04c9bff4bd23393549931fa5b6ccc2f086bb2635cf9f7755888be7dc41221751` | secret2.exe |
| `ITEMS` | 2050 | `9c743c5bd11ed0f99c76a392a12b875c5514f4472fe6e0ab5c112ec4541d063f` | secret1.exe |
| `MON1CHA.DAX` | 7064 | `67513a8ce09adb74c19d17bf3cda48731eab515da20b0c79da5c6542fb73ee52` | secret1.exe |
| `MON1ITM.DAX` | 3482 | `c7246daf02d5fa7d2a049bca6cc5e45e0a508859a744ce91df914aa45955d3fd` | secret1.exe |
| `MON1SPC.DAX` | 1242 | `90aa435237e837c7e727a5e5d399b3401a95aba34cdf706ffe1eb94894b8a603` | secret1.exe |
| `PIC1.DAX` | 26434 | `571bda15babc2ee1ef7f9b049b181a76bcd08cfd0264a60981e29356502c4a5c` | secret1.exe |
| `PIC2.DAX` | 51677 | `14daa4b81abdc4a533fdfa1b99110f23144b235ebf4283f5aae5721661bc60ca` | secret2.exe |
| `PIC3.DAX` | 51870 | `09586eaf1edd65c5201a9d2c84e8267d76305a54f05d5cc92bd465de13a007bb` | secret2.exe |
| `PIC4.DAX` | 22985 | `4d1ed9171600cd889116fcba23070ae0e3a3320d5780a0e2495c7951ff43e362` | secret2.exe |
| `PIC5.DAX` | 16920 | `0342a44c10c3eef259f530613a357e483cf3934a6cba6b00105b549f620a5042` | secret2.exe |
| `SAVGAMA.DAT` | 5469 | `54296c23138b345726bf2fd36ffa207320378a2d8e15ec477098ec9b5fd49ed9` | secret1.exe |
| `SKY.DAX` | 2448 | `1ffe6b50f6d76116a9d72fbb05a94ea70160c8fad2a49b9c4b08776b16fbadf9` | secret1.exe |
| `SOUND.DAX` | 14257 | `be95d01d14a46c9d20e0b3ec9ade147dc57532d848c74d9c56a0bae0574e9b54` | secret1.exe |
| `SPRIT1.DAX` | 41341 | `d167d163cfc86eb56512a297feaae80875131b29b09f57e8e80c3fffec1c7430` | secret2.exe |
| `START.EXE` | 72097 | `b6c08c3b0a6e0a6ebac76406f2d9abba7d7a3c8d62d4b0ac121778b9c9136036` | secret1.exe |
| `TITLE.DAX` | 55760 | `a82a8fba35f0a8a32106adc707c492fa53f6cbb44cb75b5813facece6cfa91fa` | secret1.exe |
| `WALLDEF1.DAX` | 5782 | `ac67d7555f612c78b949180c1407f4a63ec67fa86ca0b9b15bb6e52e3603b392` | secret1.exe |
| `WALLDEF2.DAX` | 4266 | `6c2ee041007daceff958ddff109c4fb9b26ca7550c765b01902f8cf3fe5654c6` | secret1.exe |
| `WALLDEF3.DAX` | 3041 | `542a791dcc269ba2eea9fe2dd3e19ef9782037fcf647cf7893399a1b2efb0b11` | secret2.exe |
