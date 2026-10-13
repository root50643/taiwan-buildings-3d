# 國立臺中教育大學｜民生校區｜中正樓入口段

依官方公開實拍自建的局部建築外觀近似模型。不是全棟、不是測繪，也不提供真實建築比例尺。原照片不隨公開包散布。

![實際STL正面](previews/front.png) ![實際STL背面](previews/rear.png)

## 範圍與辨識特徵
兩根落地主柱、兩側大片實牆、三個門廊跨間、真正凹入的門廊空間、後退玻璃門面、橫向招牌帶和頂層連續玻璃帶。

尺寸：150 × 68 × 77.2毫米，含底座，獨立視覺縮放。入口段任意後截，不含完整大廳後殿、後部高牆及側後走廊。背面留白、頂面是截斷平頂；不是整棟屋頂測繪。主柱恰為兩根，玻璃小框不當結構主柱。

實拍拍攝日未標，資料頁更新日不等於拍攝日期。因此這是公開影像所示形體的局部研究，不保證2026現況所有外觀細節不變。浮雕式窗框、玻璃凹槽是列印簡化；沒有將窗框當主柱。未複製任何第三方3D模型。

## 重建與交付
- `build_model.py`：獨立Python參數化自建。依賴版本見`requirements.txt`。
- `model.stl`、`model.obj`：同一毫米網格；STL是正式幾何驗證標的。
- `scene.blend`：正式STL匯入的可編輯網格；`render_preview.py`由實際STL產生front/rear/elevation/top四圖。
- `validate_model.py` / `validation.json`：原STL二面邊、vertex link、單連通殼、正法向/繞序/體積、尺寸、獨立重建SHA与Blend幾何一致。
- `check_layers.py` / `layer-check.json`：起點z=0.071，每0.2毫米檢查閉合輪廓与個別及合成Polygon有效；invalid直接失敗，未修補。
- `check_thin_features.py` / `thin-feature-check.json`：canonical fail-closed v3；0.8毫米形態opening是輔助篩檢，非全面最小壁厚。
- `sources.json`、`qa-summary.json`、`SHA256SUMS`：來源限制、數位QA與逐檔雜湊。

執行順序：python build_model.py；blender -b -t 2 -P render_preview.py；python validate_model.py；python check_layers.py；python check_thin_features.py。

## 列印提醒
底座朝下，單位毫米。高門廊上方挑簷、招牌帶、玻璃框凹槽應自行檢查支撐。主柱約3.8毫米寬、窗框約1.1毫米；省略空調、細字、海報與裝飾燈。

數位QA不等於實體試印或Cura/PrusaSlicer工具路徑驗證，不宣稱保證可印或免支撐。請依噴嘴、材料與層高自行切片並檢查懸空區。

## 驗收狀態
2026-10-13外觀覆核已准，以此版本凍結交獨立QA；發布前須由獨立驗證者放行。

上層連續玻璃帶的窗面僅凹約0.4毫米，細直框為齊平淺分格，不是突出主柱。`check_portico_void.py`與`portico-void-check.json`以原STL共18條射線核對凹廊及雙主柱間淨空；射線距離是模型毫米，不能當實際建築尺寸，有限採樣不是全面空間證明。
