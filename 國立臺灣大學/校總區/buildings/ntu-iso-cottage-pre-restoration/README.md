# 國立臺灣大學 磯永吉紀念室（2026修繕前外觀）

## 模型預覽

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 正面<br>![實際STL正面](previews/front.png) | 背面<br>![實際STL背面](previews/rear.png) |  |

[返回校區圖鑑](../../README.md) · [返回臺大總圖鑑](../../../README.md)

## 實際 STL 正面與背面


[下載 STL](model.stl) · [Blender 場景](scene.blend) · [參數化來源](build_model.py) · [驗證結果](validation.json)

[新增34件列印幾何補查與細節警示](../../../qa/printability-20261013/README.zh-TW.md)


官方索引代碼 S62。公開外觀近似模型，非測繪或BIM。

## 範圍與比例
明確為修繕前外觀近似，不預測完工形貌。臺大總務處2026文資頁仍列施工中，並公開改善前外觀；與博物館群另一側斜角交叉比對。前後木窗/門分組、屋身深度及低附棟比例目測，細木斜撐、瓦片、構件腐朽和內部均不重現。

保留辨識特徵：長切妻屋頂、抬高木廊、連續廊柱、單層長窗門、山牆端粗木板格紋，以及另一長面末端的低附棟。前後立面不同，沒有複製同一排窗。

尺寸 [150.0, 76.0, 31.0] mm，含底座最長150 mm。各館獨立比例，不是可拼接的共同尺度校園沙盤。尺寸、厚度、窗距均為照片目測和列印簡化，不是原建物實測。

## 列印
- 底座向下，毫米單位。參考起點：0.4 mm噴嘴、0.16–0.2 mm層高、3道外牆、15–20%填充。須依自己的切片器調整。
- 廊下有真實外部開口，屋簷大懸垂與廊柱間跨距需支撐；細柱名義1.7mm，粗木板浮雕約0.8mm。低附棟與主體相交成一個實心連通體。
- 新增細浮雕名義最小約0.8 mm；這不是全模型最小壁厚的測量結果。零碎設備、文字招牌、樹木、電線及細緻裝飾沒有加入。
- 門窗背牆與實心量體避免隱藏內殼；實際填充由切片器決定。
- 未實際列印；未用PrusaSlicer、Cura等生成工具路徑。不宣稱無支撐或無風險可印。

## 驗證與檔案
- model.stl、model.obj；scene.blend是由實際STL匯入的可編修網格。
- build_model.py為獨立參數來源；Python3.12，依requirements.txt裝依賴後執行python build_model.py。
- Blender4.3.2：blender -b -t 2 -P render_preview.py。previews/front.png、rear.png、elevation.png均直接渲染交付STL。
- python validate_model.py：原始法向、水密、流形邊／頂點、單一連通表面、無分離封閉內殼、正體積、150mm、獨立重建SHA256及已儲存Blender/STL三角幾何一致性。結果validation.json。
- python check_layers.py：每0.2mm水平截面幾何檢查，共 155 層，所抽樣截面全部閉合。首層採z=0.071mm避免重合平面退化，非實際列印首層設定。
- layer-check.json另記向下超45度面積指標與各層輪廓；它不是切片器、最小壁厚測試或實體試印。閉合截面不保證擠出連續、橋接、支撐可拆、床面附著或局部細節可印。
- SHA256SUMS可核對檔案；更改參數後需重建、重繪、重驗證。

## 公開來源
查閱及圖像像素檢視：2026-10-13。來源照片未隨檔重新散布。
- [臺大總務處：2026修繕中與改善前外觀](https://ga.ntu.edu.tw/main_ch/docDetail/2626/2604/44558/20260106)
- [實際檢視官方改善前長面與低附棟照片](https://ga.ntu.edu.tw/upload/cont_att/0961381d-37b5-42fe-9995-582275dfc664.jpg)
- [臺大博物館群官方小屋身份](https://booking-campus-museum.ntu.edu.tw/museum_information.aspx?museum_id=12&pid=10020&uid=10020)
- [實際檢視官方另一側廊道與山牆外觀](https://booking-campus-museum.ntu.edu.tw/upload/museum/ac709a52-851f-4f11-8fec-729b9c8e7b38.jpg)
- [臺大官方建物索引，檢索標題2026-08-17](https://cpo.ntu.edu.tw/map/C_01_list.pdf)

照片版權屬原權利人；沒有轉授原建築設計或照片權利。不同拍攝日期不等於已核實目前全部外觀。
