# 法鼓文理學院金山校本部大願橋

**整橋完整主要外觀近似方案；不是測繪或工程內構復原。整橋升級版（2026-10-22核准發布）。**

連續變寬彎曲木橋面、單側外傾高箱梁、兩端真圓通孔、低開放欄杆/木扶手、圓橫梁與橋底細支承、兩岸各一組非共頂雙斜管；中央無落水墩。展示底板和最小端接面非實際地形。

## 可編輯檔案
- `scene.blend`：可編輯三角網格、7材質、燈光相機。
- `model.3mf`：毫米、逐面7材質，同一幾何；並非印表機耗材配置。
- `model.stl`：同一幾何，STL不保存顏色。
- 5張`previews/*.png`均為交付mesh實渲染；generator/render/rebuild與QA腳本附上。

全展示約286 × 47 × 28.1mm；橋身270mm，依建築師108m取示意1:400。細杆名義直徑0.34mm、斜撐0.40mm，已低於常見0.8mm薄件篩檢，不適合直接承諾一般FFF實印。長跨、傾牆、圓梁及欄杆需支撐或拆件；未實印、不保證免支撐。實際切層/薄處與懸挑數值見QA。

## 歷史與單一計數
本方案替代歷史 `dila-great-vow-bridge-middle-span-segment`，不是另一套現行模型，套數不增加。歷史固定commit `4e9dfa531b4b065b9ed16f88ff28bbf2fe87a3d0`；舊STL SHA256 `ab8f4bab8b9e8bf708e9bc386dbfa6b012e06ca4912daaea881dd0839d64c913`。舊片段A/B為人為裁切、不是橋台。本版從17圖新建整體，不重複延長舊gen；舊0.8mm頂層失敗與支撐風險保留在歷史QA，新版獨立重驗。本次整橋替代沿用舊canonical目錄slug避免斷鏈；slug中的middle-span-segment僅為歷史路徑，不表示新版仍為裁切片段。

[歷史片段完整來源／QA／STL](https://github.com/root50643/taiwan-buildings-3d/tree/4e9dfa531b4b065b9ed16f88ff28bbf2fe87a3d0/法鼓文理學院/金山校本部/buildings/dila-great-vow-bridge-middle-span-segment)。

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
python rebuild.py --output /tmp/dila-great-vow-clean-rebuild --threads 4
```
乾淨重建output必須不存在；比較核心4檔與五PNG byte一致。來源日期、估計與省略詳SOURCES。
