# 國立清華大學｜學習資源中心（旺宏館）

2026-10-18 **待獨立覆核候選**。這是同一既有建築套件的改版，沒有新增建築、改公開計數或推送。公開照片外觀近似，非測繪模型；涵蓋前後主要量體、入口翼與外梯。未正式切片、未產生經驗證 G-code、未實體試印。

## 本次實際改變

- 前棟原有左右兩坡三角屋蓋改成沿模型後方 +Y 到前方 −Y 曲降的分段屋面，前端另有較低屋段。模型座標不代表地理北向。
- 下部橢圓體頂面改至 Z31.8 mm、露台頂 Z32.8 mm；第四層退縮到半徑 28.5 × 18.5 mm，下部半徑仍是 35 × 25 mm。外露弧形帶代表照片可見露台，不宣稱露台全圈連通。
- 1.3 mm 屋面皮及高側窗帶輪廓代表照片的大形狀；高側窗帶不是設備或新增樓層。其曲率、尺寸與進深均為桌上模型估計；窗帶目前較照片窄，端點與後棟交接仍有限制。
- 後棟、入口翼、外梯與底座保留。官方 6F 證實更深的 L 形轉折及內凹弧，但 1F 與 6F 不同；本候選先不改後棟，跨層輪廓與既有座標對應列為下一版缺口。

## 檔案與尺寸

- `model.stl`：150 × 124 × 68 mm，含 3 mm 底座；3,874 三角面、單一連通表面、正體積 406,815.4618 mm³。
- `scene.blend`：從實際 STL 匯入的一個三角網格，單位 mm，可編輯；參數化重建使用 `build_model.py`。無 BIM 或室內構造。
- `model.obj`：輔助交換網格。
- `previews/front.png`、`rear.png`、`elevation.png`、`roof.png`：實際 STL 的四個渲染視角；配色僅供讀形，不證明玻璃分格或實際材質。
- `sources.json`、[獨立來源覆核](qa/INDEPENDENT-SOURCE-REVIEW.md)：來源對應、年代與限制；只附 URL 與雜湊，不散布原照片或圖面。
- `validation.json`、`layer-check.json`、`qa/`：候選實跑記錄，原始失敗與精確補證分檔保留。`hash-manifest.json` 涵蓋本套件檔案，排除自身與 Python 快取。

## 來源及不確定性

實際查看建築師 R-03、B-02 照片及官方 1F／6F 像素。兩側照片均支持後高前低屋面、前端低屋段、退縮頂層及弧形露台。[建築師項目頁](https://www.archasia.asia/projects/nthu-learningcenter)列 2005–2011，正文另記 2013 啟用；照片 EXIF/XMP 自述 R-03 為 2012-02-13、B-02 為 2012-04-11，未驗相機原檔。2025 修訂日期不等於拍攝日期。

[官方 6F 圖](https://www.lib.nthu.edu.tw/library/image/6F.jpg)只約束該樓層。[導覽頁](https://www.lib.nthu.edu.tw/library/libtour.html)的 2026-07-23 更新日不是製圖日期。本件不宣稱 2026 全棟現況、逐層精確輪廓或實測尺寸。原校方照片來源保留於 `sources.json`。

後棟 ±14° 淺開書形仍為估計；未知背面素面、穿廊實心、設備省略均沿用原件已揭露的簡化。未取得可定位證據的屋頂設備不補造；沒有室內、地下、設備系統或校方原始 3D 資產。

## 真實檢查與剩餘風險

`validation.json` 的 `passed=true` 僅表示其列出的原始 STL 法線／非退化面、邊及頂點流形、封閉、單殼連通、正體積、尺寸、乾淨重建同 SHA-256 與場景幾何一致。它不代表所有列印篩查合格。

- 0.2 mm 幾何截面共 340 層均封閉；0.8 mm XY opening 篩查仍有 **156 層警示**，完整高度與面積保留在 `layer-check.json`。
- 浮點自交初報有 **37 筆**並保留 `hard_geometry_checks_passed=false`。另檔精確補證按儲存的 float32 有理值檢查 45,366 個 AABB 交疊面對，未見非法相交；12 個控制案例符合預期。這是該候選 STL 的幾何證據，不是切片或機台證明。
- 向內法線弦取樣 **198／3,874** 小於 0.8 mm，最短約 **0.00625 mm**，包含新屋頂／高側窗帶端部的尖薄區。這是實際未解警示，不能以單殼或無自交結果消除；三角面取樣也不是全域最小壁厚證明。
- 朝下超過 45° 面積約 **2,661.31 mm²**，最大取樣垂直空隙 59 mm。含原件檐下凹槽，也有新屋面邊；沒有生成支撐或驗證橋接。

請先獨立覆核新增屋面端部及懸垂，再以實際切片器評估。正立、底座朝下是評估起點；0.4 mm 噴嘴／0.2 mm 層高僅為篩查尺度，尚無已驗證列印參數。

## 乾淨重建

本輪實際使用 CPython 3.13.9、`requirements.txt` 所列版本及 bpy 5.2.2 LTS。於新的虛擬環境執行：

```sh
python -m pip install -r requirements-render.txt
python build_model.py
python render_preview.py
python validate_model.py --bpy-module
python check_layers.py
```

額外檢查的實際命令及初報／補證關係請見 [EXTENDED-QA.md](qa/EXTENDED-QA.md)。安裝 Blender 應用程式的使用者也可用 `blender -b -t 4 -P render_preview.py`，並將驗證改為 `python validate_model.py --blender <path>`。來源程式不依賴製作機器的絕對路徑。

## 實際模型預覽

| 正面 | 屋面高視角 |
|---|---|
| ![正面](previews/front.png) | ![屋面](previews/roof.png) |

| 背面 | 正投影 |
|---|---|
| ![背面](previews/rear.png) | ![立面](previews/elevation.png) |
