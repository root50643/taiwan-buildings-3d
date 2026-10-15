# 玉崗紀念圖書館（圖書與會展館）

國立屏東科技大學內埔校本部。以公開平面、跨年代照片及完整頂視建立的**有界外觀近似**，不是精確測繪或1991年原貌復原。審核與限定例外紀錄見 [QA](QA.md)，是否正式發布以統一發布清單為準。

| 正面 | 背面 |
|---|---|
| ![正面](previews/front.png) | ![背面](previews/rear.png) |

[頂視](previews/top.png) · [北端](previews/left.png) · [南端](previews/right.png)

## 內容及比例
- 保留兩側四層高體、中央三排窗低帶、中央低幅曲蓋、前後柱廊、北端不均分組X斜撐與寬梯台。
- 官方館史為**地上4層＋地下1層**；1991年5月竣工與同年7月啟用是不同時間口徑。地下層未虛構成全圈外露。
- 含底 **150 × 96 × 29.62000084 mm**，毫米、底座朝下。名義1m對1.2mm；頂外投影約116×50m、主牆約114×42m均為圖像配準近似。主屋面試配22m，參考界19–25m；分層高度、中央曲頂16–17.6m及北框高程均未測繪。
- 來源跨1991、2012、105學年度、2024標記正射及2026年1月官方前照；不聲稱所有立面與設備同年。來源證據及限制見 [sources.json](sources.json)。

## 列印化簡與風險
- 北鋼框、柱梁及PV已加粗/厚板化；上方長窄玻璃帶採**背接淺刻細框**。107根細框的側向真首段約0.264mm，外凸最多約0.192mm，與厚背牆相連；不是0.8mm自由立柱。小比例列印時細框可能合併或消失，不適合任意再縮小。
- 北框上端接屋頂投影交集約36.3639%，中央曲蓋下方約89.5855%，不是全覆蓋支承。大柱廊、鋼框孔與懸挑簷須自行檢查切片方向、橋接與支撐。
- 南短端細窗與服務構件未知而省略；背面中央精細窗跨粗化。PV僅粗分板，不含細設備、欄杆或安裝年代復原。階梯級數/踏面與基座是列印及場地近似。
- **未實體試印、未產生Cura/Prusa工具路徑，不保證無支撐可印。** 原網格與逐層數位檢查不能證明全方向最小厚度或全部自交情況。

## 檔案及重建
[原創參數源](build_model.py) · [STL](model.stl) · [可編輯Blend](scene.blend) · [依賴](requirements.txt) · [逐檔SHA](SHA256SUMS.txt)

執行 build_model.py 重建；render_preview.py 使用實際STL產生五張預覽及Blend。validate_model.py 檢查原法向/拓撲、重建SHA及Blend同幾何；check_preview_rebuild.py 檢查五PNG逐byte一致。細部原值見 [qa說明](qa/README.md)。

此件是既有學校新增一棟；[返回校區](../../README.md)。舊述耘堂模型維持原樣，尚未完成全校。

## 已獨驗的重跑環境
Python 3.12；requirements另含scipy 1.17.0（trimesh圖連通引擎）與Pillow 12.3.0（預覽字圖）。Blender 4.3.2、g++另行提供；Linux需Noto Sans CJK Regular，原渲染腳本固定讀取 /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc。更換字型或Blender可能改變PNG位元，不能仍宣稱相同bytes。

在模型目錄依序執行：

    python3 -m venv .venv
    . .venv/bin/activate
    python3 -m pip install -r requirements.txt
    python3 build_model.py
    blender -b -P render_preview.py
    python3 validate_model.py
    python3 check_preview_rebuild.py

啟動Blender前維持venv的bin在PATH首位，因caption子程序呼叫python3。原完整薄件步驟見qa/README.md；check_all.py彙總已存在的報告，不能代替先重跑各檢查。原兩false與exit1保留，限定裁定不等於所有嚴格門檻通過。字型/套件安裝依使用者環境另行處理。

[獨立覆核與限定例外](INDEPENDENT-AUDIT.md) · [獨立密面原值](independent-dense.csv.gz)
