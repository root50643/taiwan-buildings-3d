# 國立臺北教育大學｜行政大樓暨圖書館建築群

臺北校區。自行以Python實體布林建立外觀／量體近似，未下載第三方3D模型；不是測繪、施工圖或館內重建。

## 證據與範圍

本件合併官方A行政大樓與H圖書館，因1F平面兩側互標「往圖書館／往行政大樓」，兩翼相連圍繞真實開放院落。覆蓋2個官方命名館、交付只計1模型，沒有把相連側翼重複計件。行政入口面保留10個較窄主要窗群，圖書館入口面保留7個較寬主要窗群；頂部密直通風帶與5排主要上層窗分開，不當成8層。兩端低灰框、扁拱入口、階梯及後退玻璃面保留。樹遮部分比例與細格近似，圖書館側回轉面只做可見主要窗；內院壁面、相連側翼深側與屋頂設備缺多角度證據，保持素面。

官方文件2023年10月25日，攝影日未載；文件日期不等於拍攝日，無法保證2026全部現況。各頁及URL見 [sources.json](sources.json)。原照片與PDF只留私人核對，不隨公開包散布。

## 交付檔

- [model.stl](model.stl)：毫米，含底座最長150毫米，各件獨立比例
- [scene.blend](scene.blend)：由交付STL匯入的可編修網格
- [build_model.py](build_model.py) 與 [requirements.txt](requirements.txt)：自行建模參數；python build_model.py
- [render_preview.py](render_preview.py)：實際STL渲染；blender -b -t 2 -P render_preview.py

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 實際STL正面<br>![正面](previews/front.png) | 實際STL背面<br>![背面](previews/rear.png) |  |

[正立面](previews/elevation.png) · [側面](previews/side.png) · [俯視](previews/top.png)

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 正立面<br>![正立面](previews/elevation.png) | 側面<br>![側面](previews/side.png) | 俯視<br>![俯視](previews/top.png) |

[圖書館入口斜正立面](previews/library_elevation.png)；不把行政及圖書館同形外觀當成同一張照片重用。

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 圖書館入口斜正立面<br>![圖書館入口斜正立面](previews/library_elevation.png) |  |  |

[原STL射線空隙檢核](portal-ray-proof.json) · [重跑射線程式](check_portal_geometry.py)。直接遍歷原STL三角形，不修補或封截面。

## 列印與QA限制

底座朝下。窗格、拱形框、薄簷與雨遮均有列印粗化，懸挑及入口可能需支撐；拆支撐仍可能傷細件。模型尺度不是實際建築尺寸，勿把各件直接拼成同比例校園。沒有實體試印或Cura／Prusa工具路徑驗證，不保證免支撐或保證可印。

[validation.json](validation.json) 檢原STL水密、正體積、法向與繞序、每邊兩面、vertex link、單連通表面、無分離內腔殼、150毫米限制、重建SHA與Blend幾何一致。[contour-validity-check.json](contour-validity-check.json) 固定0.071毫米偏移，每0.2毫米逐層檢閉合與個別／合成Polygon有效，不修補後算成功。[thin-feature-check.json](thin-feature-check.json) 採canonical fail-closed v3每1毫米0.8毫米opening參考篩檢，不等於全面最小壁厚或切片模擬。

重跑：python validate_model.py；python check_contour_validity.py；python check_thin_features.py。

外觀已覆核，本件為作者凍結版本；獨立QA通過後才可由唯一發布者發布。
