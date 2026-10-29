# 國立臺灣大學 知武館

## 模型預覽


| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 正面原幾何配色<br>![正面](appearance/previews/front.png) | 背面與未見面保持中性<br>![背面](appearance/previews/rear.png) |  |

[返回校區圖鑑](../../README.md) · [返回臺大總圖鑑](../../../README.md)

## 最新六材質外觀版（2026-10-20）


[來源界線與四視角](appearance/README.md) · [表面色 3MF](appearance/tomatake-appearance.3mf) · [可編輯場景](appearance/scene.blend)

依官方歷史正面及右斜面影像登錄赭棕磚、原灰構造帶、原窗梃與凹背玻璃。只配可分離外凸門柱磚面，連體拱額不畫假對角分界；原入口盲凹背中性，不假造玻璃門。左側、後方與屋頂中性。原STL與歷史QA不變，不是新增幾何。原單色正面（歷史檔案留存，不作本頁預覽）／原單色背面（歷史檔案留存，不作本頁預覽）


[下載 STL](model.stl) · [Blender 場景](scene.blend) · [參數化來源](build_model.py) · [驗證結果](validation.json)

[新增34件列印幾何補查與細節警示](../../../qa/printability-20261013/README.zh-TW.md)


官方索引代碼 E22。公開外觀近似模型，非測繪或BIM。

## 範圍與比例
依2010官方正面及左右側斜角。知武館E22與農機館E21為分棟，不混為一館；四排可見窗帶、低門廊與側牆橫帶保留。深度、門廊進深及窗格分組為目測，背面與屋頂設備留白。

保留辨識特徵：粗水平灰帶、連續細直柱、分組玻璃窗、中央圓形頂飾、低弧門廊及實心低女兒牆、兩側近乎無窗的條帶牆。

尺寸 [150.0, 81.0, 61.5] mm，含底座最長150 mm。各館獨立比例，不是可拼接的共同尺度校園沙盤。尺寸、厚度、窗距均為照片目測和列印簡化，不是原建物實測。

## 列印
- 底座向下，毫米單位。參考起點：0.4 mm噴嘴、0.16–0.2 mm層高、3道外牆、15–20%填充。須依自己的切片器調整。
- 門廊、凸出女兒牆及連續窗橫框需支撐評估；四排窗帶不含室內樓層配置。兩側條帶加厚連接實心牆。
- 新增細浮雕名義最小約0.9 mm；這不是全模型最小壁厚的測量結果。零碎設備、文字招牌、樹木、電線及細緻裝飾沒有加入。
- 門窗背牆與實心量體避免隱藏內殼；實際填充由切片器決定。
- 未實際列印；未用PrusaSlicer、Cura等生成工具路徑。不宣稱無支撐或無風險可印。

## 驗證與檔案
- model.stl、model.obj；scene.blend是由實際STL匯入的可編修網格。
- build_model.py為獨立參數來源；Python3.12，依requirements.txt裝依賴後執行python build_model.py。
- Blender4.3.2：blender -b -t 2 -P render_preview.py。previews/front.png、rear.png、elevation.png均直接渲染交付STL。
- python validate_model.py：原始法向、水密、流形邊／頂點、單一連通表面、無分離封閉內殼、正體積、150mm、獨立重建SHA256及已儲存Blender/STL三角幾何一致性。結果validation.json。
- python check_layers.py：每0.2mm水平截面幾何檢查，共 308 層，所抽樣截面全部閉合。首層採z=0.071mm避免重合平面退化，非實際列印首層設定。
- layer-check.json另記向下超45度面積指標與各層輪廓；它不是切片器、最小壁厚測試或實體試印。閉合截面不保證擠出連續、橋接、支撐可拆、床面附著或局部細節可印。
- SHA256SUMS可核對檔案；更改參數後需重建、重繪、重驗證。

## 公開來源
查閱及圖像像素檢視：2026-10-13。來源照片未隨檔重新散布。
- [臺大校訊：知武館與農機館分開敘述](https://sec.ntu.edu.tw/epaper/article.asp?num=1408&sn=17190)
- [生機系官方館舍名稱](https://www.bime.ntu.edu.tw/cp_n_64627.html)
- [實際檢視2010官方入口正面](https://homepage.ntu.edu.tw/~cpo/2010photo/E/E22/IMG_5969.JPG)
- [實際檢視2010官方側面 5974](https://homepage.ntu.edu.tw/~cpo/2010photo/E/E22/IMG_5974.JPG)
- [實際檢視2010官方側面 5975](https://homepage.ntu.edu.tw/~cpo/2010photo/E/E22/IMG_5975.JPG)
- [臺大官方建物索引，檢索標題2026-08-17](https://cpo.ntu.edu.tw/map/C_01_list.pdf)

照片版權屬原權利人；沒有轉授原建築設計或照片權利。不同拍攝日期不等於已核實目前全部外觀。
