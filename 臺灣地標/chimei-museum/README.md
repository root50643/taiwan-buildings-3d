# 奇美博物館：主館外觀

## 模型預覽

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 正面<br>![正面](previews/front.png) | 背面<br>![背面](previews/rear.png) |  |

## 模型範圍

平展對稱的雙層館翼、中軸六柱門廊與三角山牆、後置中央圓頂與肋線、加粗的頂部天使剪影、兩端突出亭閣與拱形冠部。

- 尺寸：150 × 76 × 43.3 mm，模型單位為毫米，底面 Z=0。
- 正面方向：模型 -Y；這是展示座標，不是測量用方位。
- 單一連通、封閉、布林合併的可列印實體；不含室內、地下或安全設施。
- 每棟獨立以底座長邊 150 mm 設計，不代表所有模型採同一真實比例尺。

## 已知限制與推定

官方景點頁提供正面全長約 150 公尺、高約 42 公尺，作為量體比例的合理性檢查；本模型含底座且有印製加粗，並非嚴格 1:1000。屋頂平面、側背面、館體深度與端部細部依有限可見照片推定；背面保守簡化，未造出內部展廳。

小型欄杆、窗格、瓦紋、人物與字樣不按真實尺度逐件複製。省略樹木、周邊城市、臨時設施及完整園區配置。預覽中的顏色僅用於看清形狀，STL 本身沒有材質。

## FDM 建議

底座厚 2.4 mm。門廊柱身最細直徑約 1.5 mm，柱基直徑約 2.3 mm；六柱與屋梁、臺階連接為同一實體，柱間是真實外部開放空隙，可能需要局部支撐。圓頂肋線以連續網格直接整合於實心圓頂，浮起約 0.22 mm，避免分件細條。天使僅為根部加粗的約略剪影，不是原雕塑精細複製；細翼需小心拆支撐。

建議先用 0.4 mm 噴嘴、0.16–0.20 mm 層高、3 道外牆、約 12–18% 填充在切片器檢查；平底朝下。這些是起始設定，不是已驗證機台參數。縮小會使細節更脆弱。未進行實體試印、完整支撐生成、耗材或列印時間實測。

## 檔案

- model.stl：最終列印幾何
- scene.blend：毫米設定的可編輯網格、相機及預覽場景
- build_model.py：原始參數化建模程式；優先在此調整尺寸/細節後重建
- render_preview.py：直接匯入 model.stl 產生前、後與正面立視圖，沒有另外加上假立面
- previews/front.png、rear.png：實際 STL 的前後視角渲染（程式重跑另產生 elevation.png）
- validate_model.py、verify_rebuild.py、verify_blend.py：檢查程式
- validation.json、rebuild_validation.json、blend_validation.json：最終檢查報告
- requirements.txt：Python 依賴版本
- sources.md：官方來源與判讀方式
- SHA256SUMS.txt：交付檔案校驗值

Blender 場景的「Printable building」是唯一列印物件；Studio floor、Camera 與燈光均不是模型。STL 為三角網格；.blend 可編輯頂點，而 build_model.py 保留較方便的參數化來源。

## 重建方式

已使用 Python 3.12、Blender 4.3.2。安裝 requirements.txt 指定套件後，在本資料夾依序執行：

```sh
python build_model.py
python validate_model.py model.stl --output validation.json
python verify_rebuild.py
blender -b -t 4 -P render_preview.py
blender -b scene.blend -P verify_blend.py
```

預覽使用 Workbench 實體網格光照，沒有紋理貼圖或非列印的建築裝飾。

## 數位驗證涵蓋範圍

最終報告檢查：封閉網格、一個連通元件、每邊恰接兩面、每個頂點連結為單一循環、法線與繞序一致、無退化面、正體積、平底、150 mm 長邊、重建 SHA-256 完全一致、原始 STL 法線、單一閉合邊界且沒有獨立的負體積內腔殼，以及每 0.2 mm 取樣層皆有截面。欄杆、柱間及外部溝槽可形成穿通空隙，因此不要求球面拓樸。Blender 的模型三角形已與 STL 逐面對照至 0.00001 mm。

以上為數位檢查，不是獨立的全面三角形自交證明，也不取代切片預覽與試印。

## 來源

見 sources.md。原始官方照片不隨 ZIP 散布。
