# 艋舺龍山寺｜150 mm 桌上外觀模型

依臺北艋舺龍山寺官方照片與公開建築配置圖重新建立。這一件聚焦寺廟主建築群：前方三川殿及龍虎門廳、兩側六角三層鐘鼓樓、中殿重簷屋頂、後殿群及左右護龍。不是鹿港、淡水或鳳山的同名龍山寺。

## 模型預覽

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 正面<br>![正面](previews/front.png) | 背面<br>![背面](previews/rear.png) |  |

## 檔案與尺寸

- `model.stl`：毫米單位，最長邊 150 mm，底座約 142 × 150 mm。精確尺寸、面數及體積見 `validation.json`。
- `editable.blend`：最終 STL 的可編輯網格；已選取可列印物件，STUDIO ONLY 集合只作預覽，不要一同匯出。
- `build_model.py`：可調整各殿量體、曲面屋頂、殿宇位置及簡化程度的原始程式。
- `previews/front.png`、`previews/rear.png`：直接渲染最終 STL，無額外非列印裝飾；材質僅供展示，STL 不含顏色。
- `validate_model.py`、`validation.json`、`SHA256SUMS.txt`：檢查程式、結果與檔案雜湊。

模型前方為 −Y。這是依照片判讀的桌上外觀模型，各棟是相互比較的近似比例，沒有建築測量圖，未宣稱真實比例尺。

## 保留的辨識特徵

- 三川殿中央高起的大曲線屋頂，兩旁較低的龍、虎門廳。
- 中殿前方突出平台、左右簡化臺階與兩重簷。
- 前側鐘樓與鼓樓採六角扁平樓閣輪廓，保留三層屋簷；沒有套用一般四角塔。
- 中、前、後三進與左右護龍形成的院落關係。
- 翹起的屋角、屋脊剪黏以粗化燕尾／龍飾輪廓表現；屋瓦以整合在屋面上的凸紋表現。

## 150 mm 尺寸的必要簡化

- 列印用殿身都是實心外觀量體；門、窗、柱廊用淺凹與附壁柱，不製作室內或封閉空腔。
- 庭院是上方完全開放的空間，所有殿宇由同一實體底座連接。不得把露天庭院當作需要填滿的網格破洞。
- 密集剪黏、龍鬚、角草、斗栱、文字與人物雕像無法在本尺寸可靠重現，合併為厚約 1.4 mm 的穩固輪廓；不是逐尊雕像的複刻。
- 小欄杆與細柱加粗或貼合殿身，沒有鏤空迴廊。屋面瓦紋約 0.38 mm 起伏；極細細節可能在 0.4 mm 噴嘴上弱化。
- 本件範圍不含最南端獨立山門、外部廣場、瀑布、植栽及香爐；完整呈現的範圍是主要三進殿宇。
- 背側外牆及精確屋架未取得完整測繪，採照片與官方配置圖能支持的量體簡化；未發明室內配置。

## 列印注意

建議 0.4 mm 噴嘴、0.16–0.20 mm 層高、PLA，以底座朝下試印；可由切片器設定 3 圈牆、12–20% 填充。幾何實體不代表必須 100% 填充。

屋簷、脊飾、鐘鼓樓伸出屋角有局部懸垂。請在切片器檢查薄壁、橋接及支撐，必要時用樹狀支撐並減低拆除力度。大型平底座可依附著力加 brim。未實際切片或試印，不能保證無支撐即可成功。

## 公開來源與核對（2026-10-11）

實際檢視以下寺方公開照片及建築配置圖後建模，照片只作造形參照，不包含在交付套件：

1. 三川殿：https://www.lungshan.org.tw/tw/03_1_4_art.php
   照片：https://www.lungshan.org.tw/tw/images/img03_1_4.jpg
2. 中殿：https://www.lungshan.org.tw/tw/03_1_5_art.php
   照片：https://www.lungshan.org.tw/tw/images/img03_1_5.jpg
3. 後殿：https://www.lungshan.org.tw/tw/03_1_6_art.php
   照片：https://www.lungshan.org.tw/tw/images/img03_1_6.jpg
4. 鐘鼓樓：https://www.lungshan.org.tw/tw/03_1_7_art.php
   照片：https://www.lungshan.org.tw/tw/images/img03_1_7.jpg
5. 建築配置：https://www.lungshan.org.tw/tw/03_1_9_art.php
   圖：https://www.lungshan.org.tw/tw/images/img03_1_9.jpg
6. 觀光署英文介紹：https://eng.taiwan.net.tw/m1.aspx?id=93&sNo=0002016

照片及圖像版權歸原權利人。本模型為重新建立的簡化幾何，非寺方提供的模型，亦未宣稱官方認可。不可作為工程、保存修復或建築測繪資料。

## 重建與驗證

Python 3.12 及 `requirements.txt` 中的套件；Blender 4.x 供預覽與 .blend：

    python build_model.py
    python validate_model.py
    blender -b -t 4 -P render_preview.py

驗證項目包含有限座標、非退化三角形、封閉性、單一連通邊界、每邊兩面、每頂點單一閉環鄰域、儲存法線、正體積、Euler 特徵數 2、底面及 150 mm 尺度，並獨立重建比對三角面。結果以 `validation.json` 為準。使用 manifold3d 實體布林運算，未另外執行三角形互交檢測或物理試印。

另附 `check_blend.py` 與 `blend_validation.json`，驗證 .blend 中可列印物件的每一個三角面與最終 STL 一致。重跑方式：

    blender -b editable.blend -P check_blend.py
