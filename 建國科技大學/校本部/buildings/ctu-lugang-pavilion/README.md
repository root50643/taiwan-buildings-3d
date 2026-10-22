# 建國科技大學綠崗亭

**2013年上傳照片所示完整主亭外觀近似；非測繪、非2026現況認證。**

雙層開放亭架、四灰柱、上下轉90°的月門/月窗、單外直階與上口通路、缺口環簷、單四坡紅瓦頂、灰石台基與紅透空欄杆。範圍止於門檻；不含園林引橋或水下支承。

## 檔案
- `scene.blend`：可編輯三角網格、7材質、相機與燈光。
- `model.3mf`：同一毫米幾何及逐面多色材質；不是列印機耗材設定。
- `model.stl`：同一封閉幾何；STL不存顏色。
- 五張 `previews/*.png` 均渲染實際交付mesh，不是AI示意圖。
- 重建/驗證腳本、`QA.md`、`qa/*.json`、`SHA256SUMS`。

顯示尺寸約108 ×108 ×128.8 mm，無可靠實物比例尺。柱截面採圓形近似，尺寸/階數/瓦壟/欄杆及石紋均估值；細格與瓦紋減量、列印加厚。最細名義桿0.9 mm不等於全表面最小厚度證書。未實印，不能宣稱免支撐；月洞上緣、樓板、挑簷、屋頂及外階需依設備支撐/拆件。全域薄處切片如失敗會保留披露，不豁免或修補原STL。

## 重建
```sh
python -m pip install -r requirements.txt
python build_model.py
blender -b -t 4 --python-exit-code 1 --python render_model.py
python qa_model.py
python check_features.py
python verify_exchange.py
blender -b -t 4 --python-exit-code 1 --python verify_scene.py
blender -b -t 4 --python-exit-code 1 --python verify_render.py
python rebuild.py --output /tmp/ctu-pavilion-new-rebuild --blender blender --threads 4
```
新重建目錄必須不存在；核心四檔與五PNG比較實際bytes。Blend幾何/材料實編存回讀另驗證。
