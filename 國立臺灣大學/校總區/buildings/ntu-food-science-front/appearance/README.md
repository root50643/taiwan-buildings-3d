# 臺大食品科技館前部：四材質外觀版

沿用原 **2,010 三角面／955 頂點**，不改原 STL 位元、座標、面序或幾何；這是既有模型外觀改版，不增加模型包數。

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 正面<br>![正面](previews/front.png) | 背面保持中性<br>![背面](previews/rear.png) | ![正立面](previews/elevation.png) |
| ![頂視](previews/top.png) |  |  |

[表面色 3MF](ntufood-appearance.3mf) · [可編輯 Blender](scene.blend) · [材質色表](palette.json) · [逐面指派與依據](face-materials.json) · [原 STL](../model.stl)

## 來源與配色邊界

親自核對臺大官方[左前照 5837](https://homepage.ntu.edu.tw/~cpo/2010photo/S/S48/IMG_5837.JPG)、[正面 5838](https://homepage.ntu.edu.tw/~cpo/2010photo/S/S48/IMG_5838.JPG)與[入口近照 5839](https://homepage.ntu.edu.tw/~cpo/2010photo/S/S48/IMG_5839.JPG)。三照 EXIF DateTimeOriginal 分別為 2010-10-09 15:27:25／15:28:04／15:28:12；時鐘與時區未獨立核實，5837／5838 的修改欄與原始時間相同，5839 的 2010-12-31 修改日期不當拍攝日。原照解析度僅 448×336 或 336×448，配色為大材料家族代理，非校準 RGB。[來源覆核與雜湊](qa/source-review.json)，不代表 2026 現況，原照不入包。

- 正面與來源支持左端低飽和紅褐磁磚牆、原窗檯凸帶與左端柱肋，保留原粗化窗距；不加磚縫紋理或壁面污漬。
- 僅原離散窗凹背與入口玻璃帶採灰綠，原窗梃銀灰。原玻璃照片有窗簾、反射及空調遮擋，本版不複製其圖像，也不假稱逐窗透明度一致。
- 入口實心招牌橫帶與原凸出入口框均紅褐，**橫帶不是玻璃，不加校名字體**；其小頂面與側回折面採同一磁磚構件有界材料延伸，並非逐面照片證實。
- 原 S48 前部模型不包含鄰接 S49 研發館；未知右側、背面、主屋頂及底座中性，不加設備、樹木、車輛或新附翼。
- 原 STL、原場景、建模腳本與歷史 QA 不變，配色不增加模型數、不宣稱實體列印成功。

[原幾何與歷史來源限制](../README.zh-TW.md)

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

尺寸仍為 150 × 86 × 70.5 mm；原 STL、建模程式、場景及歷史 QA 保留。原層檢與薄特徵檢查本次未重跑，不能由材質 QA 代替。

3MF 是同一網格的表面色，不是各材質各自封閉的分色實體、切片專案、噴頭映射或 G-code。切片 GUI、多材料路徑與實體列印未測；柱頭、屋簷、窗框及薄邊仍須評估材料、支撐及拆除風險，沒有保證可印或免支撐。
