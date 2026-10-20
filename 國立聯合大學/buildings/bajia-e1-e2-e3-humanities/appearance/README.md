# 聯大八甲 E1／E2／E3 人文與社會學院：九材質外觀版

沿用原 **6,918 三角面／3,453 頂點**，不改原 STL 位元、座標、面序或幾何；這是既有模型外觀改版，不增加模型包數。

| 正面 | 背面保持中性 |
|---|---|
| ![正面](previews/front.png) | ![背面](previews/rear.png) |
| ![正立面](previews/elevation.png) | ![頂視](previews/top.png) |

[表面色 3MF](nuue-appearance.3mf) · [可編輯 Blender](scene.blend) · [材質色表](palette.json) · [逐面指派與依據](face-materials.json) · [原 STL](../model.stl)

## 來源與配色邊界

親自核對官方 [人文與社會學院相簿](https://secretary.nuu.edu.tw/p/132-1003-1096.php?Lang=zh-tw) 的完整 [照片 1](https://secretary.nuu.edu.tw/var/file/3/1003/gallery/96/1096/gallery_1096_402695_25754.jpg)、[照片 8](https://secretary.nuu.edu.tw/var/file/3/1003/gallery/96/1096/gallery_1096_6639094_25755.jpg)。EXIF DateTimeOriginal **2025-03-02 15:10:48／2025-03-10 13:44:30**，日期與時區未獨立核實，不代表 2026 現況。來源照片不隨包散布。

- 原 E2 中棟正面採冷灰、樓梯塔外框暖淺色，已見左側下部整片端牆紅磚色。E3 後棟來源左端只有狹窄磚帶，而原面未分開，該端牆保持中性，不擴大染整面紅磚。
- 原 E2 離散窗凹背及 E1 曲面前窗凹背灰藍，既有黏合窗梃深灰；E2 原網格把實景的門、窗與部分實牆簡化成規則小窗，這只是原窗色彩代理，不能宣稱逐扇復原。不補紅門、細玻璃框、空調或字樣。
- E3 寬深凹是混合走廊，不整片當玻璃；樓梯內背也保留中性。既有 E3 前置框採淡藍灰**混凝土色**，不是透明窗。
- 原加厚實欄帶只採褐灰欄杆色代理，並非實景透空細欄；露台和梯踏面灰色，不把整片露台染欄杆色。原模型的階高與通行尺寸不是無障礙或安全認證。
- 僅原獨立光電板頂面藍灰，屋頂底板及板間縫保留中性。未見外側、背牆及跨材質長面保守中性，來源中設備、庭園與鄰棟均未增加。
- 原 STL／面序／座標不變，不增加模型數，不宣稱物理列印成功。

[原幾何與來源限制](../README.zh-TW.md) · [來源覆核](qa/source-review.json)

## 重建與核驗

安裝 [依賴](source/requirements.txt)，Blender 使用 4.3.2。由本資料夾上層提供原 model.stl：

1. `python appearance/source/build_appearance.py`
2. `python appearance/source/verify_exchange.py`
3. `blender -b -t 3 --python-exit-code 1 -P appearance/source/render_appearance.py`
4. `blender -b -t 3 --python-exit-code 1 -P appearance/source/verify_scene.py`

[獨立重建 ZIP](rebuild-source.zip)含原 STL、四支程式及依賴，不含第三方照片；不取代原建模腳本。[逐檔 SHA256](SHA256SUMS)

[交換／拓撲 QA](qa/exchange-validation.json)核對原座標與面序、全部面材質、單連通、有向水密邊、頂點 link 單環、正體積與零退化／重複面；lib3mf 嚴格讀取零警告，實際編輯單材質再存讀，其他材質及面指派不變。SDK 六位小數量化誤差另列。

[Blender 存讀與編輯](qa/scene-validation.json) · [渲染記錄](qa/render-manifest.json) · [獨立重建](qa/rebuild-validation.json)

## 製造限制照舊

尺寸仍為 150 × 120 × 61 mm；原 STL、建模程式、場景及歷史 QA 保留。原層檢與薄特徵檢查本次未重跑，不能由材質 QA 代替。

3MF 是同一網格的表面色，不是九個封閉分色實體、切片專案、噴頭映射或 G-code。切片 GUI、多材料路徑與實體列印未測；柱頭、屋簷、窗框及薄邊仍須評估材料、支撐及拆除風險，沒有保證可印或免支撐。
