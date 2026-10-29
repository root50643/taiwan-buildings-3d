# 中央行政大樓｜正面有限配色增補

## 保留原幾何與代表圖

原 2,748 頂點、5,500 三角面、transform及150×87×47.1mm不變。原STL、OBJ、scene.blend、build_model.py、render_preview.py、三張原預覽和原QA全部保留；不改學校／校區／首頁代表圖。兩份README均加新彩色比較；原灰米色圖不冒稱已上色。新增appearance.blend、appearance.3mf、五張appearance/圖與可重現script。

## 已實讀色彩來源

[校方無障礙地圖](https://love.adm.ncu.edu.tw/NCU_counsel/NCU-barrier-free/)的AdmiB項目以中文「行政大樓」連到[行政大樓照片](https://love.adm.ncu.edu.tw/NCU_counsel/NCU-barrier-free/images/Administration_building/1.jpg)。照片可辨橫長四層、錯位方格陣、凸出雨庇等特徵。頁面英文部分誤植 Chung Cheng Auditorium，本件不沿用該英文誤名；依中文選項、圖路徑與實物特徵交叉確認。拍攝日期未標，不把下載時間當拍攝時間，也不稱完整2026現況。

本次未成功直接檢視原sources.json中的2025防災PDF第13頁：正常下載HTTP503，web screenshot cache miss。因此不以該PDF未讀照片當本次色彩證據。原建模來源記錄仍保留。公開包不附來源照片、PDF或私人工作檔。

正面格陣淺灰米近白；上緣可見深灰褐只配正面條帶，未知平屋頂中性。孔後為不透明深綠灰代理，不等同逐孔玻璃證明；四個較大凹底及入口暗藍灰，不補不存在的細框、字牌、室內或反射紋理。雨庇、柱與階近灰米，現有頂牌面暗灰但不新增字。未看清的側後面、原三條左側凹帶與屋面保持中性，原底座不畫成真實地坪或草坡。sRGB是照片外觀近似，非校準施工色卡；渲染正確轉linear。

## 重建與格式

以 Blender 4.3.2，原scene.blend/model.stl與script置於同目錄：

```sh
MALLOC_ARENA_MAX=2 LP_NUM_THREADS=1 OMP_NUM_THREADS=1 blender -b -t 1 --python-exit-code 1 -P build_appearance.py
blender -b --python-exit-code 1 -P verify_color_geometry.py -- scene.blend appearance.blend appearance-geometry-QA.json appearance.3mf
```

只寫新增appearance檔，不寫回原件。Cycles CPU32 samples/seed0/單執行緒，PNG剔除全部文字metadata並保留IDAT；3MF用原面base-material與完整double座標，不重採樣、拆面或Boolean。兩獨立重建對script/3MF/materials JSON/PNG做byte比較，BLEND比語義而非容器byte。3MF讀取端須支援材質，不附AMS或多噴頭耗材設定。

## 原QA與範圍不變

尺寸、孔數和深度是照片估計，後面刻意素面，不是測繪或完整現況。此番只驗證同幾何／材質對應／視圖及重建，不取代原QA。原1mm層切、半徑0.4mm（直徑0.8mm）的XY形態開運算不是全面全向最薄壁或切片工具路徑驗證，屋簷／雨庇／細格仍需支撐和縮尺檢查；未實體試印，不保證免支撐、必然可印或結構安全。
