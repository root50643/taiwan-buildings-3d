# 國立臺灣大學 地質科學館（三層前棟）

[返回校區圖鑑](../../README.md) · [返回臺大總圖鑑](../../../README.md)

## 實際 STL 正面與背面

| 正面 | 背面 |
|---|---|
| ![實際STL正面](previews/front.png) | ![實際STL背面](previews/rear.png) |

[下載 STL](model.stl) · [Blender 場景](scene.blend) · [參數化來源](build_model.py) · [驗證結果](validation.json)

[新增34件列印幾何補查與細節警示](../../../qa/printability-20261013/README.zh-TW.md)


官方索引代碼 S22。公開外觀近似模型，非測繪或BIM。

## 範圍與比例
僅2010官方兩張照片可確認的三層前棟。1937年木造地質標本館、後方舊系館及側後複合體均未納入；不可將前棟當全部S22館群。三排窗罩高度略遞減，窗組數量與進深為列印尺度近似；未見端面與背面留白。

保留辨識特徵：密集突出拱形預鑄雨罩、三層窗帶、清楚水平及垂直結構帶、薄曲線入口雨棚、屋簷下小肋。雨罩做成有實心背牆的厚框，沒有把其簡化成平牆拱洞。

尺寸 [150.0, 72.0, 48.0] mm，含底座最長150 mm。各館獨立比例，不是可拼接的共同尺度校園沙盤。尺寸、厚度、窗距均為照片目測和列印簡化，不是原建物實測。

## 列印
- 底座向下，毫米單位。參考起點：0.4 mm噴嘴、0.16–0.2 mm層高、3道外牆、15–20%填充。須依自己的切片器調整。
- 密集窗罩、屋簷小肋和入口雨棚可能需大量局部支撐；窗罩間距小，切片後要檢查細縫及支撐拆除，不能視為免支撐。
- 新增細浮雕名義最小約0.9 mm；這不是全模型最小壁厚的測量結果。零碎設備、文字招牌、樹木、電線及細緻裝飾沒有加入。
- 門窗背牆與實心量體避免隱藏內殼；實際填充由切片器決定。
- 未實際列印；未用PrusaSlicer、Cura等生成工具路徑。不宣稱無支撐或無風險可印。

## 驗證與檔案
- model.stl、model.obj；scene.blend是由實際STL匯入的可編修網格。
- build_model.py為獨立參數來源；Python3.12，依requirements.txt裝依賴後執行python build_model.py。
- Blender4.3.2：blender -b -t 2 -P render_preview.py。previews/front.png、rear.png、elevation.png均直接渲染交付STL。
- python validate_model.py：原始法向、水密、流形邊／頂點、單一連通表面、無分離封閉內殼、正體積、150mm、獨立重建SHA256及已儲存Blender/STL三角幾何一致性。結果validation.json。
- python check_layers.py：每0.2mm水平截面幾何檢查，共 240 層，所抽樣截面全部閉合。首層採z=0.071mm避免重合平面退化，非實際列印首層設定。
- layer-check.json另記向下超45度面積指標與各層輪廓；它不是切片器、最小壁厚測試或實體試印。閉合截面不保證擠出連續、橋接、支撐可拆、床面附著或局部細節可印。
- SHA256SUMS可核對檔案；更改參數後需重建、重繪、重驗證。

## 公開來源
查閱及圖像像素檢視：2026-10-13。來源照片未隨檔重新散布。
- [2010臺大官方S22館舍圖像索引](https://homepage.ntu.edu.tw/~cpo/about_campus_archeitectureimage_S.html)
- [實際檢視三層前棟長立面](https://homepage.ntu.edu.tw/~cpo/2010photo/S/S22/IMG_5857.JPG)
- [實際檢視前棟中央入口](https://homepage.ntu.edu.tw/~cpo/2010photo/S/S22/IMG_5858.JPG)
- [官方說明1937地質標本館為系館旁另一棟，本模型不含](https://booking-campus-museum.ntu.edu.tw/museum_information.aspx?museum_id=4&pid=10020&uid=10020)
- [臺大官方建物索引，檢索標題2026-08-17](https://cpo.ntu.edu.tw/map/C_01_list.pdf)

照片版權屬原權利人；沒有轉授原建築設計或照片權利。不同拍攝日期不等於已核實目前全部外觀。
