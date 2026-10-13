# 國立臺灣大學 應用力學研究大樓（主要前棟）

官方索引代碼 N59。公開外觀近似模型，非測繪或BIM。

## 範圍與比例
只製作中央入口與相鄰主前棟，不包括後方院落、完整側翼與附屬量體。依2010三張官方外觀及目前應力所網站大幅入口照片；背面與屋頂缺乏證據，留白，進深為目測估計。

保留辨識特徵：帶圓窗的淺弧階梯山牆、三排寬窄交替窗、大型淺弧階梯拱門、兩側較低柱廊、入口台階。門廊左右原曲線以短直段簡化；圓窗、玻璃皆實心背牆淺凹。

尺寸 [150.0, 82.0, 80.4000015258789] mm，含底座最長150 mm。各館獨立比例，不是可拼接的共同尺度校園沙盤。尺寸、厚度、窗距均為照片目測和列印簡化，不是原建物實測。

## 列印
- 底座向下，毫米單位。參考起點：0.4 mm噴嘴、0.16–0.2 mm層高、3道外牆、15–20%填充。須依自己的切片器調整。
- 大型門廊、淺拱頂與側柱廊需局部支撐；不宣稱自支撐或完整建物重建。
- 新增細浮雕名義最小約0.9 mm；這不是全模型最小壁厚的測量結果。零碎設備、文字招牌、樹木、電線及細緻裝飾沒有加入。
- 門窗背牆與實心量體避免隱藏內殼；實際填充由切片器決定。
- 未實際列印；未用PrusaSlicer、Cura等生成工具路徑。不宣稱無支撐或無風險可印。

## 驗證與檔案
- model.stl、model.obj；scene.blend是由實際STL匯入的可編修網格。
- build_model.py為獨立參數來源；Python3.12，依requirements.txt裝依賴後執行python build_model.py。
- Blender4.3.2：blender -b -t 2 -P render_preview.py。previews/front.png、rear.png、elevation.png均直接渲染交付STL。
- python validate_model.py：原始法向、水密、流形邊／頂點、單一連通表面、無分離封閉內殼、正體積、150mm、獨立重建SHA256及已儲存Blender/STL三角幾何一致性。結果validation.json。
- python check_layers.py：每0.2mm水平截面幾何檢查，共 402 層，所抽樣截面全部閉合。首層採z=0.071mm避免重合平面退化，非實際列印首層設定。
- layer-check.json另記向下超45度面積指標與各層輪廓；它不是切片器、最小壁厚測試或實體試印。閉合截面不保證擠出連續、橋接、支撐可拆、床面附著或局部細節可印。
- SHA256SUMS可核對檔案；更改參數後需重建、重繪、重驗證。

## 公開來源
查閱及圖像像素檢視：2026-10-13。來源照片未隨檔重新散布。
- [應力所本館身份及1987完工記載](https://www.iam.ntu.edu.tw/zh/intro/history)
- [應力所官方公開場地介紹（只使用館外正門）](https://www.iam.ntu.edu.tw/zh/conference-room/conference-room2/98-site)
- [實際檢視官方入口大圖](https://www.iam.ntu.edu.tw/images/stories/site/IAM.jpg)
- [2010官方外觀 6007](https://homepage.ntu.edu.tw/~cpo/2010photo/N/N59/IMG_6007.JPG)
- [2010官方外觀 6008](https://homepage.ntu.edu.tw/~cpo/2010photo/N/N59/IMG_6008.JPG)
- [2010官方外觀 6009](https://homepage.ntu.edu.tw/~cpo/2010photo/N/N59/IMG_6009.JPG)
- [臺大官方建物索引，檢索標題2026-08-17](https://cpo.ntu.edu.tw/map/C_01_list.pdf)

照片版權屬原權利人；沒有轉授原建築設計或照片權利。不同拍攝日期不等於已核實目前全部外觀。
