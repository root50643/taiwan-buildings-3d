# 行政大樓連體群

## 模型預覽

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 前斜視（實際 STL）<br>![前斜視](previews/front.png) | 後斜視（實際 STL）<br>![後斜視](previews/rear.png) |  |

國立中正大學・民雄校本部｜公開實拍外觀近似模型｜單位：毫米（mm）。


[正立面](previews/elevation.png) · [上視圖](previews/top.png)

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 正立面<br>![正立面](previews/elevation.png) | 上視圖<br>![上視圖](previews/top.png) |  |

## 模型範圍

金字塔主體、兩側低廊、開放中央院落與後側鐘鼓樓的整體量體近似；不是精密測繪。

保留斜縮主體、粗化雲牆、帶側向尖拱的深門廊、兩側柱廊、屋頂開放中庭、後部雙塔的四角柱間大開口、橫梁與厚實層疊簷冠。

各部尺度、院落進深、雲牆連續曲線及完整後側窗格沒有實測；依官方照片與2026修繕公告附圖的上視關係估計。主體朝院落一面細部簡化，未臆造鐘鼓內部及室內空間。

## 來源年代與限制

官方導覽照片未標攝影日期；20週年校史第109頁為2009年前後歷史佐證。2026-07-23公告修繕期2026-07-31至11-17，本件描述公開照片所示修繕前形態，不表示2026-10-13施工現況。

[官方建物介紹](https://ccu-navigation.ccu.edu.tw/p/426-1253-7.php?Lang=zh-tw)。完整原始網址、實際查看的照片及支持特徵請見 [sources.json](sources.json)。第三方原照片和 PDF 不隨模型再散布。

## 下載與重建

- [model.stl](model.stl)：含底座 98.00 × 150.00 × 81.20 mm，最大尺寸 150 mm，各建物獨立比例，不是校園統一比例尺。
- [scene.blend](scene.blend)：匯入實際交付 STL 的可編修三角網格；場景單位毫米。
- [build_model.py](build_model.py)：獨立參數與布林幾何建構來源，無外部網格或照片依賴。
- [requirements.txt](requirements.txt)：Python 3.12 套件版本；另需 Blender 4.3.2+。
- [SHA256SUMS](SHA256SUMS)：逐檔雜湊。

重建：先安裝 requirements.txt，執行 python build_model.py，再執行 blender -b -t 2 -P render_preview.py。渲染器讀取 model.stl，預覽不是另一份外觀替身。

## 列印與數位檢查

底座朝下、毫米匯入切片器。門廊與柱廊橫梁跨距、塔樓窗洞上緣及簷冠可能需要支撐；雲牆已粗化為連接主體的實心輪廓。 請自行在 Cura／PrusaSlicer 等確認支撐、跨橋與工具路徑；沒有實體試印，也沒有實際切片器驗證，不能保證無支撐列印或保證成功。

- [validation.json](validation.json)：原始二進位 STL 面法向／繞序、每邊兩面、頂點 link 單環、單一連通表面、正體積、底座與尺寸；獨立重建 STL SHA 及 saved Blend 幾何一致。
- [contour-validity-check.json](contour-validity-check.json)：起點 z=0.071 mm、間距 0.2 mm，共 406 層；每節點 degree 2、個別閉合輪廓及組合 Polygon valid，失敗即中止、不修補吞錯。
- [layer-check.json](layer-check.json)：同間距閉合及向下表面篩檢。
- [thin-feature-check.json](thin-feature-check.json)：canonical shared-edge thin-v2，z=0.071 mm 起、1 mm 間距、0.8 mm參考寬度 morphology opening；最大面積損失 0.357%，高於1%為 0 層。此值也包含尖角，不是全模型最小壁厚或實際擠出測試。

重跑 python validate_model.py、python check_layers.py、python check_contour_validity.py、python check_thin_features.py。每支程序均需 exit 0；輪廓檢查禁止使用 buffer(0) 修補輸入問題。

模型為建物外觀研究縮景，並非施工、結構、無障礙或防災分析模型。
