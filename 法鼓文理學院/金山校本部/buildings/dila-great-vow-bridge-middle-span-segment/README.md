# 法鼓文理學院・大願橋中央裁切片段

**這是官方實景照片 A/B 間的局部建模，不是完整橋梁。** A/B 是研究者自選展示裁切面，並非真實伸縮縫、橋頭或量測樁號。兩端保留平切，不加入虛構端門或橋墩。

![橋內側預覽](previews/front.png)

## 可辨識幾何
- 單側高、向外傾斜的實體箱梁外形；內側垂直深色木條。
- 對側較低的開放金屬欄杆及木扶手，空隙為真穿孔，不是深色貼面。
- 橋面緩彎、向較寬一端漸變；橫向木板及實體淺板縫。
- 照片 A/B 之間約 13 根可辨識外伸橫肋；位置採均勻近似，不宣稱實測。

尺寸約 **140 × 47.984 × 25 mm**，含外伸肋。任意展示尺度，不可從整橋108m推算本段真實長度。木板、木條、欄杆柱的數量及間距為簡化視覺節奏，不是實際施工表。細部與來源註冊見 `SOURCES.md`、`qa/source-registration.json`。

## 檔案
- `model.stl`：單一連通封閉表面，無色。
- `model.3mf`：同一組三角形，5組可改顏色的基礎材質；非多擠出機設定。
- `scene.blend`：同幾何、可編輯網格和材質、相機及燈光；不是分件CAD。
- `mesh.json`、`palette.json`、`build_model.py`：可重建和調整曲線、寬高、欄杆、肋及配色。
- `previews/`：front/rear/elevation/top/side 五張由交付網格直接渲染的視圖。
- `qa/`、`QA.md`：拓樸、切片、局部損失、格式重讀及獨立視覺審查。

## 列印警告（請勿視為免支撐或試印完成）
橋身連通不代表平放即可列印：最低處只是單側箱梁下緣，橋面、橫肋及欄杆需要另行規劃支撐或改朝向。沒有添加冒充真實橋墩的展示柱。沒有實際試印、切片器路徑、強度驗證。

125層輪廓有效，但近最高點 z=24.999mm 的細小斜頂末端截面（約0.147mm²）**未通過0.8mm侵蝕**；未豁免或藏起。0.55mm木條凸起和0.28mm板縫可能被噴嘴/層高抹平。局部面積損失與支撐指標詳 `QA.md`，不能只看單殼通過即稱列印就緒。

## 重建
以 Python 安裝 `requirements.txt`，執行 `python build_model.py`、`python qa_model.py --out .`、`python check_features.py`。`verify_exchange.py` 另需 lib3mf；必要時用 `BUILD_PYTHON` 指向具備 trimesh/manifold3d 的 Python。以 Blender 執行 `blender -b --python render_model.py`、`blender -b --python verify_scene.py`。報告紀錄實際版本。來源照片不需下載即可重建模型。
