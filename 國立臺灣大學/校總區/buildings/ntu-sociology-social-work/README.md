# 國立臺灣大學 社會及社工館

## 模型預覽

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 正面<br>![實際STL正面](previews/front.png) | 背面<br>![實際STL背面](previews/rear.png) |  |

[返回校區圖鑑](../../README.md) · [返回臺大總圖鑑](../../../README.md)

## 實際 STL 正面與背面


[下載 STL](model.stl) · [Blender 場景](scene.blend) · [參數化來源](build_model.py) · [驗證結果](validation.json)

[新增34件列印幾何補查與細節警示](../../../qa/printability-20261013/README.zh-TW.md)


官方索引代碼 E9。公開外觀近似模型，非測繪或BIM。

## 範圍與比例
依2010官方兩張主入口與左側斜角照片。這是E9社會社工館，不是外型相近的E10國發所大樓；主山牆圓飾與低弧入口分別處理。未見右側和背面留白；進深與樹遮窗格節奏近似。

保留辨識特徵：中央階梯狀低三角山牆與圓飾、三段中央窗帶、寬淺弧入口、底層圓窗、左側上層結構格柵。沒有把國發所的高半圓拱門複製到本館。

尺寸 [150.0, 88.0, 74.5] mm，含底座最長150 mm。各館獨立比例，不是可拼接的共同尺度校園沙盤。尺寸、厚度、窗距均為照片目測和列印簡化，不是原建物實測。

## 列印
- 底座向下，毫米單位。參考起點：0.4 mm噴嘴、0.16–0.2 mm層高、3道外牆、15–20%填充。須依自己的切片器調整。
- 淺弧入口與密集格窗上緣可能需局部支撐；窗格皆有背牆，門廊空間縮成淺凹以免形成內殼。
- 新增細浮雕名義最小約0.9 mm；這不是全模型最小壁厚的測量結果。零碎設備、文字招牌、樹木、電線及細緻裝飾沒有加入。
- 門窗背牆與實心量體避免隱藏內殼；實際填充由切片器決定。
- 未實際列印；未用PrusaSlicer、Cura等生成工具路徑。不宣稱無支撐或無風險可印。

## 驗證與檔案
- model.stl、model.obj；scene.blend是由實際STL匯入的可編修網格。
- build_model.py為獨立參數來源；Python3.12，依requirements.txt裝依賴後執行python build_model.py。
- Blender4.3.2：blender -b -t 2 -P render_preview.py。previews/front.png、rear.png、elevation.png均直接渲染交付STL。
- python validate_model.py：原始法向、水密、流形邊／頂點、單一連通表面、無分離封閉內殼、正體積、150mm、獨立重建SHA256及已儲存Blender/STL三角幾何一致性。結果validation.json。
- python check_layers.py：每0.2mm水平截面幾何檢查，共 373 層，所抽樣截面全部閉合。首層採z=0.071mm避免重合平面退化，非實際列印首層設定。
- layer-check.json另記向下超45度面積指標與各層輪廓；它不是切片器、最小壁厚測試或實體試印。閉合截面不保證擠出連續、橋接、支撐可拆、床面附著或局部細節可印。
- SHA256SUMS可核對檔案；更改參數後需重建、重繪、重驗證。

## 公開來源
查閱及圖像像素檢視：2026-10-13。來源照片未隨檔重新散布。
- [社會學系官方交通資訊：社會社工館身份與位置](https://sociology.ntu.edu.tw/intro-2/map/)
- [實際檢視2010官方外觀 6010](https://homepage.ntu.edu.tw/~cpo/2010photo/E/E9/IMG_6010.JPG)
- [實際檢視2010官方外觀 6011](https://homepage.ntu.edu.tw/~cpo/2010photo/E/E9/IMG_6011.JPG)
- [實際檢視2010官方外觀 6012](https://homepage.ntu.edu.tw/~cpo/2010photo/E/E9/IMG_6012.JPG)
- [臺大官方建物索引，檢索標題2026-08-17](https://cpo.ntu.edu.tw/map/C_01_list.pdf)

照片版權屬原權利人；沒有轉授原建築設計或照片權利。不同拍攝日期不等於已核實目前全部外觀。
