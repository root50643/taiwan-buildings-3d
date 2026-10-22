# 國立東華大學壽豐校區景觀橋

**2019修復後四透空格柵亭的完整主要外觀近似模型；非測繪、非工程內構復原。**

中央平車道＋兩側各一獨立窄拱步橋，四角亭、內外欄杆、灰色外露拱帶與向外挑的金色卷托；短橋台和展示底板。橋下透空；底板不是水面測量，長岸牆於邊界截斷。

## 檔案
- `scene.blend`：可編輯三角網格、11材質、燈光與相機。
- `model.3mf`：同一幾何、毫米與逐面材質；可編輯多色，不是印表機耗材分配。
- `model.stl`：同一封閉幾何；STL本身不存顏色。
- `build_model.py`、`render_model.py`、`rebuild.py`：可重建；五張預覽均渲染交付mesh，不是AI示意圖。
- `QA.md`、`qa/*.json`、`SHA256SUMS`：實際檢查與限制。

顯示尺寸約202 × 92 × 62.62 mm，無可靠實物比例尺。細欄杆名義0.85 mm、亭格柵0.9 mm；尖端與接面切片可能更薄，不保證0.8 mm全層通過。未實印，非免支撐保證；橋跨、亭頂、卷托與欄杆懸挑需依設備規劃支撐／拆件。

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
python rebuild.py --output /tmp/ndhu-bridge-new-rebuild --blender blender --threads 4
```
`--output` 必須不存在。重建比較STL/3MF/mesh/palette和五PNG實際bytes；Blend由幾何、材質實編存回讀另驗證。

## 限制
照片外觀近似；不是2026現況認證。NLSC2024只是浮水印，未確認實際航拍年。隱蔽肋數、橫梁和節點省略，灰色不代表驗證RC配筋。欄杆／格柵數、石面紋理、亭尺寸、卷曲細形皆估值；遠側卷托為對稱近似。
