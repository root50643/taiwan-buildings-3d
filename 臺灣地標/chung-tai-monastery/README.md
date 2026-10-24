# 中台禪寺｜150 mm 外觀列印模型

依建築師事務所與觀光署的正、背面照片重建的桌上外觀詮釋，非實測複製。單一連通封閉實體、無室內空腔；不含寺內佛像、院內其他建築及植栽。

## 模型預覽

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 正面<br>![正面](previews/front.png) | 背面<br>![背面](previews/rear.png) |  |

## 模型
- 整體 150 × 108 × 132 mm，含 3 mm 平底底座；毫米制 STL。
- 保留中軸高塔、前後大型蓮瓣狀窗框、四角菩薩殿、左右斜升的大天梯量體、重簷、頂部八片抽象蓮瓣與摩尼珠輪廓。
- 前方兩側法杖加粗為直徑約 2.3–2.7 mm；小環改實心浮雕盤。尖頂最細處約 1.8 mm。窗格及門窗做附著於實心牆的淺浮雕／淺凹。
- 蓮瓣有實體厚度並與中央冠基正體積交疊，避免獨立漂浮薄片。

## 已檢視的參考來源
查閱日期：2026-10-11。照片未隨模型散布。
1. 中台禪寺，交通部觀光署：https://www.taiwan.net.tw/m1.aspx?id=R32&sNo=0001016
2. 正面實景照片：https://www.taiwan.net.tw/att/1/big_scenic_spots/pic_R32_2.jpg
3. 李祖原聯合建築師事務所官方作品頁：https://www.cylee.com/project/Chung-Tai-Zen-Monastery?lang=tw
4. 建築師所刊夜間另一側實景：https://www.cylee.com/uploads/default/NS_project_relates/raw/dda0f6ec1833ea336737d6c58781e14f.jpg

官方事務所列建築高 136 m，但本模型含縮略基地、局部厚化和估計尺寸，因此不宣稱統一比例尺。正面及帶三角斜翼的背面輪廓有照片支持；側牆、完整屋頂平面、塔後低層量體與樓梯配置缺少正投影資料，為低可信度估形。各窗列數量、飛簷曲度、飾件與雕刻均簡化；並非精確宗教圖像復刻。未用相近寺廟代替本建築。

## 列印建議與未驗證事項
平底向下。建議 PLA、0.4 mm 噴嘴、0.16–0.20 mm 層高、3 道壁。屋簷、蓮瓣及法杖附近可能需局部支撐；切片後檢查細杆、懸垂與支撐可拆除性。蓮瓣的設計剖面徑向厚約 2 mm、橫向厚 6 mm，但邊緣收尖，這不是完整自動最小厚度量測。兩側法杖直杆最細約 2.3 mm，末端短節約 1.7 mm；高寬比遠大於主體，搬動、剝離支撐或掉落時容易折斷。請只握底座，勿捏冠飾、法杖或尖頂，運送時保護凸出件。不要因網格通過便宣稱無支撐可印。尚未實際切片、試印、做掉落或強度測試；縮小尺寸可能使法杖脆弱、窗格消失。

## 交付及重建
model.stl 為最終列印實體；scene.blend 為匯入該 STL 的可編輯網格，展示地板與燈光不是列印件，另嵌入原始 build_model.py。

安裝 requirements.txt 後依序執行：
1. python build_model.py
2. python validate_model.py model.stl --output validation.json
3. blender -b -t 4 -P render_preview.py

previews/front.png、rear.png 都由實際 STL 算繪；重跑算繪程式可另生成 elevation.png；這些預覽並非概念圖。validation.json 檢查法向、邊雙面、點單環鏈結、體積、連通、底面及最大尺寸；rebuild_check.json 記錄重建前後 SHA-256。checksums.sha256 包含交付檔案校驗碼。使用實體布林且外殼單連通，沒有獨立封閉內殼；數位檢查不獨立證明所有自交，也不代表實物列印保證。

重建自檢可執行 python verify_rebuild.py；scene_check.json 另核對 blend 中的列印網格面數、尺寸，以及嵌入來源是否與交付程式一致。
