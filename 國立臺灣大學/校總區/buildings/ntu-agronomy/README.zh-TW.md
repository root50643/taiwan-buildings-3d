# 國立臺灣大學 農藝館

## 模型預覽


| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 正面與來源支持區域<br>![正面](appearance/previews/front.png) | 未見外側背面中性<br>![背面](appearance/previews/rear.png) |  |

## 5 材質外觀版（2026-10-21）


[來源界線與四視角](appearance/README.md) · [表面色 3MF](appearance/ntuagron-appearance.3mf) · [可編輯場景](appearance/scene.blend)

依 2010 官方照片保守標示灰混凝土肋與門廊、淺灰窗間牆、白框及灰綠凹窗；未建模端窗不補造，兩側與後屋面中性。 原 STL 與歷史 QA 不變；這是外觀改善，不是新增幾何。原單色正面（歷史檔案留存，不作本頁預覽）／原單色背面（歷史檔案留存，不作本頁預覽）


官方索引代碼 M13。公開外觀近似模型，非測繪或BIM。

## 範圍與比例
依官方2010正面與左側端部照片，表現主要長形前館。屋頂小突出物僅目測外輪廓，未知用途；側面、背面及進深缺少充分證據而留白或概略化，不加入未確認附屬館舍。

保留辨識特徵：成列垂直混凝土肋柱、五層窗組、四支巨柱入口大門廊、出挑簷緣。窗框與肋線加粗，設備與招牌省略。

尺寸 [150.0, 77.0, 74.0] mm，含底座最長150 mm。各館獨立比例，不是可拼接的共同尺度校園沙盤。尺寸、厚度、窗距均為照片目測和列印簡化，不是原建物實測。

## 列印
- 底座向下，毫米單位。參考起點：0.4 mm噴嘴、0.16–0.2 mm層高、3道外牆、15–20%填充。須依自己的切片器調整。
- 大型入口門廊需支撐；細肋柱保持與量體融合，底座平放。
- 新增細浮雕名義最小約0.9 mm；這不是全模型最小壁厚的測量結果。零碎設備、文字招牌、樹木、電線及細緻裝飾沒有加入。
- 門窗背牆與實心量體避免隱藏內殼；實際填充由切片器決定。
- 未實際列印；未用PrusaSlicer、Cura等生成工具路徑。不宣稱無支撐或無風險可印。

## 驗證與檔案
- model.stl、model.obj；scene.blend是由實際STL匯入的可編修網格。
- build_model.py為獨立參數來源；Python3.12，依requirements.txt裝依賴後執行python build_model.py。
- Blender4.3.2：blender -b -t 2 -P render_preview.py。previews/front.png、rear.png、elevation.png均直接渲染交付STL。
- python validate_model.py：原始法向、水密、流形邊／頂點、單一連通表面、無分離封閉內殼、正體積、150mm、獨立重建SHA256及已儲存Blender/STL三角幾何一致性。結果validation.json。
- python check_layers.py：每0.2mm水平截面幾何檢查，共 370 層，所抽樣截面全部閉合。首層採z=0.071mm避免重合平面退化，非實際列印首層設定。
- layer-check.json另記向下超45度面積指標與各層輪廓；它不是切片器、最小壁厚測試或實體試印。閉合截面不保證擠出連續、橋接、支撐可拆、床面附著或局部細節可印。
- SHA256SUMS可核對檔案；更改參數後需重建、重繪、重驗證。

## 公開來源
查閱及圖像像素檢視：2026-10-13。來源照片未隨檔重新散布。
- [臺大農藝系館身份](https://agron.ntu.edu.tw/cp_n_24262.html)
- [臺大官方2010照片索引](https://homepage.ntu.edu.tw/~cpo/about_campus_archeitectureimage_M.html)
- [官方正面與端部實景 5933](https://homepage.ntu.edu.tw/~cpo/2010photo/M/M13/IMG_5933.JPG)
- [官方正面與端部實景 5935](https://homepage.ntu.edu.tw/~cpo/2010photo/M/M13/IMG_5935.JPG)
- [臺大官方建物索引，檢索標題2026-08-17](https://cpo.ntu.edu.tw/map/C_01_list.pdf)

照片版權屬原權利人；沒有轉授原建築設計或照片權利。不同拍攝日期不等於已核實目前全部外觀。
