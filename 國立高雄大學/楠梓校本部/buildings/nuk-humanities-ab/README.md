# 國立高雄大學人文社會科學院 A/B 主樓

國立高雄大學｜楠梓校本部｜`nuk-humanities-ab`

完整相連 A/B 主樓的彩色外觀近似：A 三層大 U 與 B 二層小 U 在角部連接，庭院開口相差 90°。另棟 C 低長體、池、草坡、全院地景、地下室與室內配置不在範圍（左後車道僅保留地上可見下坡入口）。不是將連續主樓任意切半。

## 下載與編輯
- `scene.blend`：單一可編輯三角網格、5 個可改色材質；無嵌入腳本或外部圖片。
- `model.3mf`：相同三角網格、逐面基礎材質；保留彩色與毫米單位。
- `model.stl`：相同單一封閉網格；STL 格式本身無顏色。
- `previews/`：5 張由交付網格直接渲染的 1200×1200 PNG，非 AI 示意圖。

尺寸 242 × 256 × 34 mm。比例由正式發包設計圖縮略（名目 2 mm / 設計米），不是成屋測量或比例測繪保證。底座只是有界展示底板，不是校園地形。房間採實心列印代理，兩個中庭、開放柱廊與框架保留真空隙；不表示室內也已復原。

## 保留特徵
不同高度的錯向 U 形院落、向內下降且轉角斜接的屋面、各棟三個凹入可達屋頂平台（共六處）、A/B 各一日用水箱服務區、高低灰框、細柱與水平梁、內庭樓廊、灰色格片、玻璃角接、真階梯教室斜頂突出部、入口外階與左後停車場車道可見凹入口。左後條紋突塊依原CAD文字「地下停車場車道」判讀為車道，非教室或升樓階；地下延伸省略。圖紙移出樓梯框沒有誤建為外塔；平台不是玻璃天窗或貫穿樓層的洞。

## 版本與近似界線
根據校方正式發包設計圖及早期官方影像，不是竣工測繪或 2026 現況模型。背面細窗、平台設備、門窗分格依設計近似；不宣稱四面逐格竣工實拍確認。淺黃土牆、深灰屋面、淺灰框與不透明玻璃色代理取自官照，非現場校色。微型柱、屋緣、欄板與格片加厚；細瓦紋、室內及機電管線省略。

## 列印注意
需支撐評估，尤其長水平框梁、廊板、遮陽片及屋緣。未實體試印，不保證無支撐。0.2 mm 分層連通區檢查與局部厚度探針不等於全域最薄處證明；詳細真實結果見 QA.md 與 qa/。

## 重建
Python 需 numpy、trimesh、manifold3d、shapely、rtree；Blender 4.3.2，lib3mf 檢查可用另一 Python。
```sh
python build_model.py
blender -b -t 4 --python-exit-code 1 --python render_model.py
python qa_model.py
python check_features.py
BUILD_PYTHON=python python_with_lib3mf verify_exchange.py
blender -b -t 4 --python-exit-code 1 --python verify_scene.py
blender -b -t 4 --python-exit-code 1 --python verify_render.py
python rebuild.py --output /new/empty/path
```
原 CAD、官方照片、PDF 與完整研究圖紙不包含在本模型包；來源與權利見 SOURCES.md / LICENSE。
