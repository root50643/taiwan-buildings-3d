# 國立臺灣大學 大氣科學館B館

[返回校區圖鑑](../../README.md) · [返回臺大總圖鑑](../../../README.md)

## 實際 STL 正面與背面

| 正面 | 背面 |
|---|---|
| ![實際STL正面](previews/front.png) | ![實際STL背面](previews/rear.png) |

[下載 STL](model.stl) · [Blender 場景](scene.blend) · [參數化來源](build_model.py) · [驗證結果](validation.json)

[新增34件列印幾何補查與細節警示](../../../qa/printability-20261013/README.zh-TW.md)


官方索引代碼 S45。公開外觀近似模型，非測繪或BIM。

## 範圍與比例
1975年B館的高矩形主體，依2010官方正面與右側照片。沒有把旁邊日治氣象A館、低連接翼及浩瀚C館合併。五條正面長拱窗及3+2分組可確認；右側只保留可見長窗的簡化節奏，進深、窗距目測，背面和左側留白。

保留辨識特徵：五根跨樓層高拱窗、3+2的正面分組、厚方形門廊及相通的大拱、平屋頂和簡潔牆面。底部細格柵加厚，其餘冷氣與管線省略。

尺寸 [150.0, 105.0, 86.19999694824219] mm，含底座最長150 mm。各館獨立比例，不是可拼接的共同尺度校園沙盤。尺寸、厚度、窗距均為照片目測和列印簡化，不是原建物實測。

## 列印
- 底座向下，毫米單位。參考起點：0.4 mm噴嘴、0.16–0.2 mm層高、3道外牆、15–20%填充。須依自己的切片器調整。
- 入口門廊有相通前側大拱，跨度較大，必須在真正切片器檢視拱底與支撐可拆性；高窗橫框亦有懸垂。
- 新增細浮雕名義最小約0.8 mm；這不是全模型最小壁厚的測量結果。零碎設備、文字招牌、樹木、電線及細緻裝飾沒有加入。
- 門窗背牆與實心量體避免隱藏內殼；實際填充由切片器決定。
- 未實際列印；未用PrusaSlicer、Cura等生成工具路徑。不宣稱無支撐或無風險可印。

## 驗證與檔案
- model.stl、model.obj；scene.blend是由實際STL匯入的可編修網格。
- build_model.py為獨立參數來源；Python3.12，依requirements.txt裝依賴後執行python build_model.py。
- Blender4.3.2：blender -b -t 2 -P render_preview.py。previews/front.png、rear.png、elevation.png均直接渲染交付STL。
- python validate_model.py：原始法向、水密、流形邊／頂點、單一連通表面、無分離封閉內殼、正體積、150mm、獨立重建SHA256及已儲存Blender/STL三角幾何一致性。結果validation.json。
- python check_layers.py：每0.2mm水平截面幾何檢查，共 431 層，所抽樣截面全部閉合。首層採z=0.071mm避免重合平面退化，非實際列印首層設定。
- layer-check.json另記向下超45度面積指標與各層輪廓；它不是切片器、最小壁厚測試或實體試印。閉合截面不保證擠出連續、橋接、支撐可拆、床面附著或局部細節可印。
- SHA256SUMS可核對檔案；更改參數後需重建、重繪、重驗證。

## 公開來源
查閱及圖像像素檢視：2026-10-13。來源照片未隨檔重新散布。
- [大氣系2025概述：A氣象館、1975 B大氣科學館、C浩瀚館分開](https://www.as.ntu.edu.tw/images/Daily%20Update/C05B_114_202508.pdf)
- [實際檢視B館正面入口](https://homepage.ntu.edu.tw/~cpo/2010photo/S/S45/IMG_5829.JPG)
- [實際檢視B館右側及入口轉角](https://homepage.ntu.edu.tw/~cpo/2010photo/S/S45/IMG_5831.JPG)
- [館群旁較低舊館作辨識對照，不併入B館模型](https://homepage.ntu.edu.tw/~cpo/2010photo/S/S45/IMG_5830.JPG)
- [臺大官方建物索引，檢索標題2026-08-17](https://cpo.ntu.edu.tw/map/C_01_list.pdf)

照片版權屬原權利人；沒有轉授原建築設計或照片權利。不同拍攝日期不等於已核實目前全部外觀。
