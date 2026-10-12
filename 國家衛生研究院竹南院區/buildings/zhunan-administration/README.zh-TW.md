# 國家衛生研究院竹南院區｜行政大樓

依公開院區配置圖、北側與迎賓廣場外觀照片製作的可列印概念模型。此為外觀辨識縮模，並非測繪、竣工圖或精確比例復刻；不包含室內、實驗室、設備或保全資訊。

## 尺寸與檔案

- 成品外框（含底座）：150 × 56 × 42.75 mm。
- 單件模型最長邊固定為 150 mm；不同建築不共同比例，不能直接拼成同比例院區。
- `model.stl`：單一連通實體，毫米單位；直接匯入切片軟體。
- `model.obj`：同一可列印網格的替代格式。
- `scene.blend`：實際 STL、相機及燈光場景。地面平面僅為攝影棚，不屬於列印模型。
- `previews/front.png`、`previews/rear.png`：直接渲染實際 STL，沒有另加不可列印裝飾。
- `build_model.py`：參數化生成原始碼；`render_preview.py`：Blender 渲染程式。
- `validation.json`：網格驗證；`SHA256SUMS`：檔案校驗值。

## 外觀判讀與簡化

保留行政大樓長向略彎折的主體、錯落屋頂與高低石色端牆、深窗格節奏、北側低矮柱廊。照片 753 左側被截切的高樓不直接算進行政大樓；圖資及研究大樓另建模型。

照片有透視與遮蔽，無測量尺寸。因此量體深度、高度、轉折角、窗格數及階梯位置均為近似。背側缺乏完整實照，採保守連續牆體與推估窗格，不代表已核實背面。屋頂小塊僅作簡化量體，無任何設備語義。廣場、水景、藝術品、植栽及跨棟連橋不納入單棟列印件。

窗戶是約 0.55 mm 的凹槽，而非穿孔。柱廊柱截面約 1.6 × 1.8 mm；橫梁厚約 1.1 mm，柱間淨跨度約 4.5 mm。為列印保留連續底座，雨遮與窗台只作淺凸出。這些是列印工程取捨，不能用作建築尺寸資料。

## 列印建議

建議 PLA、0.4 mm 噴嘴、0.16–0.20 mm 層高、3 圈壁、10–15% 填充，底座平放。淺窗槽通常不需支撐；柱廊短橋依機器橋接表現決定局部支撐。先在切片預覽檢查柱廊橫梁、雨遮、窗緣及首層。不要宣稱全機型免支撐。模型未實際試印；網格驗證不能替代試印、強度或懸空檢查。縮小模型會降低細節厚度，不建議任意縮小。

## 重建與檢查

在 Python 環境安裝 `requirements.txt`，執行 `python build_model.py`；接著執行 `python validate_model.py model.stl --longest-edge 150 --output validation.json`。預覽使用 Blender 4.2 以上執行 `blender -b -t 6 -P render_preview.py`。

驗證涵蓋封閉性、法向一致、正體積、單一連通網格、邊與頂點流形、無退化三角形、平底及目標尺寸。不獨立證明所有自相交或列印可行性。

## 公開來源（2026-10-11 核對）

- [官方竹南院區配置圖頁](https://iben.nhri.edu.tw/tw_us/tw_us_map/)
- [官方外部配置圖](https://iben.nhri.edu.tw/wp-content/uploads/2024/11/map_cht.jpg)；上傳路徑年份不是底圖年份，不代表最新完整現況。
- [臺灣綠建築發展協會：國家衛生研究行政、圖資、研究大樓](https://www.taiwangbc.org.tw/tw/modules/news/article.php?storyid=206)
- [行政大樓北側實照，753](https://www.taiwangbc.org.tw/tw/modules/news/visit.php?fileid=753)
- [迎賓廣場實照，752](https://www.taiwangbc.org.tw/tw/modules/news/visit.php?fileid=752)
- [互助營造公開工程頁](https://www.futsu.com.tw/p_public.html)
- [互助營造院區廣角照片](https://www.futsu.com.tw/images/images/portfolio/public/public_04.jpg)

此專案只提供來源連結及自行生成之模型預覽，不再散布原始第三方照片。建築設計、照片及其他第三方內容的權利仍屬原權利人；本專案不授予其商用或再散布權利，相關適用性未另行評估。
