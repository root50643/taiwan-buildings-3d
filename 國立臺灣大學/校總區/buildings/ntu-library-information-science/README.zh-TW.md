# 國立臺灣大學 圖書資訊學系館

官方索引代碼 M9。公開外觀近似模型，非測繪或BIM。

## 範圍與比例
依2010校方三角度照片及系網2014正面照片的外觀近似。主要七跨正面、長邊高肋柱與平屋簷有照片支持；進深、被樹遮住的側面開口與背面未完全確認，背面留白，不重建室內。

保留辨識特徵：抬高入口的長外階梯、七跨垂直柱列、最高窗組微尖頂、下層窗帶與側面高肋、薄平屋簷。外梯為實心台階與加厚側牆，窗框為加粗背牆浮雕。

尺寸 [150.0, 108.0, 79.19999694824219] mm，含底座最長150 mm。各館獨立比例，不是可拼接的共同尺度校園沙盤。尺寸、厚度、窗距均為照片目測和列印簡化，不是原建物實測。

## 列印
- 底座向下，毫米單位。參考起點：0.4 mm噴嘴、0.16–0.2 mm層高、3道外牆、15–20%填充。須依自己的切片器調整。
- 入口雨棚、平屋簷及橫向窗框可能需要支撐；側牆和窗距都是列印簡化。
- 新增細浮雕名義最小約0.9 mm；這不是全模型最小壁厚的測量結果。零碎設備、文字招牌、樹木、電線及細緻裝飾沒有加入。
- 門窗背牆與實心量體避免隱藏內殼；實際填充由切片器決定。
- 未實際列印；未用PrusaSlicer、Cura等生成工具路徑。不宣稱無支撐或無風險可印。

## 驗證與檔案
- model.stl、model.obj；scene.blend是由實際STL匯入的可編修網格。
- build_model.py為獨立參數來源；Python3.12，依requirements.txt裝依賴後執行python build_model.py。
- Blender4.3.2：blender -b -t 2 -P render_preview.py。previews/front.png、rear.png、elevation.png均直接渲染交付STL。
- python validate_model.py：原始法向、水密、流形邊／頂點、單一連通表面、無分離封閉內殼、正體積、150mm、獨立重建SHA256及已儲存Blender/STL三角幾何一致性。結果validation.json。
- python check_layers.py：每0.2mm水平截面幾何檢查，共 396 層，所抽樣截面全部閉合。首層採z=0.071mm避免重合平面退化，非實際列印首層設定。
- layer-check.json另記向下超45度面積指標與各層輪廓；它不是切片器、最小壁厚測試或實體試印。閉合截面不保證擠出連續、橋接、支撐可拆、床面附著或局部細節可印。
- SHA256SUMS可核對檔案；更改參數後需重建、重繪、重驗證。

## 公開來源
查閱及圖像像素檢視：2026-10-13。來源照片未隨檔重新散布。
- [圖資系官方交通與館舍身份](https://www.lis.ntu.edu.tw/?page_id=682)
- [實際檢視系網正面照片](https://www.lis.ntu.edu.tw/wp-content/uploads/2014/09/NTULISb.jpg)
- [2010官方照片索引](https://homepage.ntu.edu.tw/~cpo/about_campus_archeitectureimage_M.html)
- [官方外觀 5770](https://homepage.ntu.edu.tw/~cpo/2010photo/M/M9/IMG_5770.JPG)
- [官方外觀 5771](https://homepage.ntu.edu.tw/~cpo/2010photo/M/M9/IMG_5771.JPG)
- [官方外觀 5773](https://homepage.ntu.edu.tw/~cpo/2010photo/M/M9/IMG_5773.JPG)
- [臺大官方建物索引，檢索標題2026-08-17](https://cpo.ntu.edu.tw/map/C_01_list.pdf)

照片版權屬原權利人；沒有轉授原建築設計或照片權利。不同拍攝日期不等於已核實目前全部外觀。
