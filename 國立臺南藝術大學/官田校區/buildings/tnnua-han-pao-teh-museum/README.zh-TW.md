# 國立臺南藝術大學｜漢寶德紀念館

## 最新版：立面配置修訂 v2

**請下載 [修訂 STL](facade-layout-v2/model-v2.stl) 或 [七材質 3MF](facade-layout-v2/model.3mf)。本層 model.stl／scene.blend 與 appearance 資料夾保留的是修訂前歷史版本。**

依官方平面與實照修正外梯、雙陽臺及門洞所在立面，並修正外梯升向。以凸盒為模型正面 y−，外梯在 x− 左側往正面上升，雙陽臺在 x+ 右鄰面；不是地理方位。[來源、修訂細節、可重建源碼與新版檢查](facade-layout-v2/README.md)。原高度、細部尺寸仍是近似，不能稱為完整比例校準。

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 凸盒正面 y− 與右鄰陽臺面 x+<br>![修訂正面](facade-layout-v2/previews/front.png) | 左側外梯 x−，往正面上升<br>![修訂外梯](facade-layout-v2/previews/stairs.png) |  |

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 後面 y+ 保守中性<br>![修訂後面](facade-layout-v2/previews/rear.png) | 俯視 x− 左／x+ 右／y− 下<br>![修訂俯視](facade-layout-v2/previews/top.png) |  |

含底座仍為 150 × 142 × 98 mm；752 頂點、1524 三角面。新版重新檢查水密／流形／法線／退化面、重建一致性及 490 個截層；仍有 11 層薄特徵警示（最大局部損失 2.7367 mm²）。[新版 QA](facade-layout-v2/qa/geometry-validation.json)、[新版截層](facade-layout-v2/qa/layer-check.json)。尚未正式 FFF 切片或實體試印，不能保證免支撐。

灰混凝土、紅外伸盒側／底、深玻璃和框欄的七材質為照片近似，不是封閉多色體或機器設定。原實心平頂、未知後面與加厚欄板仍明示簡化；沒有補室內懸浮展廳、水池或屋頂設備。南藝仍為 14 包，本件不增加包數或校數。

## 保留的修訂前資料

- [原 STL](model.stl)、[原 scene](scene.blend)、[原建模源碼](build_model.py)
- [原網格驗證](validation.json)、[原截層紀錄](layer-check.json)：歷史證據，未覆寫，不能代替新版 QA
- [七材質舊幾何版](appearance/README.md)：保留配色來源與先前交換檔，其立面配置尚未修正
- [基準檔案雜湊](facade-layout-v2/baseline-manifest.json)、[原來源](sources.json)、[全包雜湊](hash-manifest.json)
