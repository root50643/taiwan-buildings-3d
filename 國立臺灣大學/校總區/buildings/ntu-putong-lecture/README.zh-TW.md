# 國立臺灣大學 普通教學館

## 3 材質外觀版（2026-10-21）

| 正面與來源支持區域 | 未見外側背面中性 |
|---|---|
| ![正面](appearance/previews/front.png) | ![背面](appearance/previews/rear.png) |

[來源界線與四視角](appearance/README.md) · [表面色 3MF](appearance/ntuputong-appearance.3mf) · [可編輯場景](appearance/scene.blend)

依2010官方照片，只處理中央拱窗淡灰玻璃代理及藍灰細框；外圈建築飾邊、紅灰混合牆面、開放走廊與簷棚中性，不冒充完整立面復原。 原 STL 與歷史 QA 不變；這是外觀改善，不是新增幾何。[原單色正面](previews/front.png)／[原單色背面](previews/rear.png)


官方索引代碼 N11。公開外觀近似模型，非測繪或BIM。

## 範圍與比例
依官方2010年四張公開外觀照片的五層主體研究；不宣稱2026立面設備現況。背面與實際進深缺證據而簡化，不含連往博雅館的空橋。

保留辨識特徵：中央高拱玻璃窗及山牆圓孔、突出的側翼、上層橫向廊道節奏、底層大拱入口。

尺寸 [150.0, 98.0, 58.0] mm，含底座最長150 mm。各館獨立比例，不是可拼接的共同尺度校園沙盤。尺寸、厚度、窗距均為照片目測和列印簡化，不是原建物實測。

## 列印
- 底座向下，毫米單位。參考起點：0.4 mm噴嘴、0.16–0.2 mm層高、3道外牆、15–20%填充。須依自己的切片器調整。
- 入口雨棚、大拱頂及較長的凹窗上緣可能需支撐；所有凹窗與拱廊均保留背牆，沒有室內細節。
- 新增細浮雕名義最小約0.9 mm；這不是全模型最小壁厚的測量結果。零碎設備、文字招牌、樹木、電線及細緻裝飾沒有加入。
- 門窗背牆與實心量體避免隱藏內殼；實際填充由切片器決定。
- 未實際列印；未用PrusaSlicer、Cura等生成工具路徑。不宣稱無支撐或無風險可印。

## 驗證與檔案
- model.stl、model.obj；scene.blend是由實際STL匯入的可編修網格。
- build_model.py為獨立參數來源；Python3.12，依requirements.txt裝依賴後執行python build_model.py。
- Blender4.3.2：blender -b -t 2 -P render_preview.py。previews/front.png、rear.png、elevation.png均直接渲染交付STL。
- python validate_model.py：原始法向、水密、流形邊／頂點、單一連通表面、無分離封閉內殼、正體積、150mm、獨立重建SHA256及已儲存Blender/STL三角幾何一致性。結果validation.json。
- python check_layers.py：每0.2mm水平截面幾何檢查，共 290 層，所抽樣截面全部閉合。首層採z=0.071mm避免重合平面退化，非實際列印首層設定。
- layer-check.json另記向下超45度面積指標與各層輪廓；它不是切片器、最小壁厚測試或實體試印。閉合截面不保證擠出連續、橋接、支撐可拆、床面附著或局部細節可印。
- SHA256SUMS可核對檔案；更改參數後需重建、重繪、重驗證。

## 公開來源
查閱及圖像像素檢視：2026-10-13。來源照片未隨檔重新散布。
- [臺大校務資訊：正式館舍身份](https://ntuinfo.ntu.edu.tw/p1_3_6.html)
- [臺大校園規劃小組：2010年多角度外觀](https://homepage.ntu.edu.tw/~cpo/about_campus_archeitectureimage.html)
- [實際檢視照片 5910](https://homepage.ntu.edu.tw/~cpo/2010photo/N/N11/IMG_5910.JPG)
- [實際檢視照片 5912](https://homepage.ntu.edu.tw/~cpo/2010photo/N/N11/IMG_5912.JPG)
- [實際檢視照片 5915](https://homepage.ntu.edu.tw/~cpo/2010photo/N/N11/IMG_5915.JPG)
- [實際檢視照片 5922](https://homepage.ntu.edu.tw/~cpo/2010photo/N/N11/IMG_5922.JPG)
- [臺大官方建物索引，檢索標題2026-08-17](https://cpo.ntu.edu.tw/map/C_01_list.pdf)

照片版權屬原權利人；沒有轉授原建築設計或照片權利。不同拍攝日期不等於已核實目前全部外觀。
