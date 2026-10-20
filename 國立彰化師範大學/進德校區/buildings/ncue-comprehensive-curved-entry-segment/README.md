# 國立彰化師範大學・綜合中心弧形入口屏牆與階梯段

這是進德校區綜合中心的**歷史影像參考、局部入口建築段模型**，不是整棟劇場，不是實測建築圖，也不代表 2026 年現況。以弧形屏牆、左右各四道通長狹縫、中央門洞、上方五個小方孔與弧形前階作為辨識特徵；孔洞是真幾何挖空，中央門洞後方另有後退的實心玻璃面與框架。

![前方透視](previews/front.png)

## 範圍與誠實限制
- 展示尺寸 **170 × 90 × 88 mm**，未經測量，不可當作固定建築比例尺。弧度、厚度、階高、窗格、扶手與開口相對位置依照片簡化。
- 只做前方屏牆／中央後退玻璃入口／寬弧形階梯／兩側簡化扶手。後方短牆是展示截斷邊界，不是劇場的真實背面或完整外殼。
- 未模型化側翼、屋頂、側方坡道及紅色外梯、文字布條、植栽。官方 PDF 的光電配置屬規劃，**沒有加入光電板**。
- 淺灰米色磁磚、深灰階梯、灰金屬與深綠灰玻璃為歷史照片的相對色感；不宣稱標準色票、精確材質反射或透明度。

## 檔案
- `model.stl`：單連通封閉三角面幾何，STL 本身無色。
- `model.3mf`：相同三角形與座標；7 組逐面顯示材質，不是多噴頭/耗材配置。
- `scene.blend`：可編輯 Blender 場景與 7 材質，單一建築 mesh；燈光／相機不是交付幾何。
- `mesh.json`, `palette.json`：公開頂點、面與材質索引，便於換色。
- `build_model.py`, `render_model.py`, `qa_model.py`, `check_features.py`, `verify_exchange.py`, `verify_scene.py`：可重建及檢查原始碼。
- `previews/`：前透視、後方截斷、正面、頂面、低視角門洞共五視圖。
- `SOURCES.md`, `sources.json`, `QA.md`, `qa*/`：來源、幾何與交換驗證。

## 重建
Python 依 `requirements.txt` 安裝；Blender 4.3.2。依序執行：
```sh
python build_model.py
python qa_model.py --out .
python check_features.py
python verify_exchange.py
blender -b -t 4 --python render_model.py
blender -b -t 4 --python verify_scene.py
```
生成階段使用 Manifold 布林、0.0001 mm 簡化容差再輸出 float32 STL；QA 直接讀最後原始 STL，僅精確座標焊接，不修洞、不刪退化面、不豁免細節。細柱稍加粗至 1.3 mm，避免共面布林／float32 退化；不隱藏模型修改。

## 製造警告
440 層整個連通截面均能承受 0.4 mm 內縮，**不代表所有局部細節可印**。另逐層量測局部 morphological opening 損失，保留完整報告。0.9 mm 扶手橫桿高度、1.0 mm 窗框及門洞／狹縫上緣跨距均需依機器、方向與支撐評估；沒有實際切片機路徑或列印測試，不宣稱免支撐。

本校其他建築並未因此全部完成。

模型／生成程式採 `LICENSE` 所示授權；來源照片僅作參考，不打包、不嵌入貼圖。
