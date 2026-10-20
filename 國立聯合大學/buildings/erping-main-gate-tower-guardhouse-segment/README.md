# 國立聯合大學二坪山校名柱與附連警衛亭段

NUU Erping Shan central gate-name tower and attached guard booth, approximate exterior segment.

![實際交付網格前右視角](previews/front.png)

## 範圍與檔案

此為新建幾何，不是全校門、整棟 J1 或另一座左側警衛亭。僅建中央白色細長校名柱與附連小型圓角警衛亭，附中性展示底座。柱約 120 mm 高、24 mm 寬、13 mm 深；整體含底座約 **43 × 55 × 123 mm**。所有尺寸由照片比例估算，無真實建築比例尺。

- [model.stl](model.stl)：無色毫米網格，1,520 三角面，單連通封閉外殼。
- [model.3mf](model.3mf)：同一網格七種顯示材質；非印表機工具頭／耗材對應。
- [scene.blend](scene.blend)：可編輯同網格、材質、相機與燈光。
- [build_model.py](build_model.py)、[render_model.py](render_model.py)：可重建幾何與實際網格五視角。
- [QA.md](QA.md)、[SOURCES.md](SOURCES.md)、[來源清單](sources.json)、[雜湊](SHA256SUMS)。

## 實景近似的限制

- **國立聯合大學書法及 NUU 標誌留白**，不捏造或以近似字形冒充。
- 長直凹區與側槽使用淺凹實背；照片無法確定內部或貫通關係。本包不提供室內、設備或門機構。
- 亭後側、完整頂面及平面深度不明，採中性簡化封閉；矩形側窗框與窗梃為照片支持的外觀近似，非精確窗格測繪。
- 薄磁磚縫、天線、桿件、交通設備與告示不建。灰色底座為模型展示／結構支撐，不是實測路島。
- 照片拍攝於 2025-02-28，不能視為 2026 年現況證明。原照片不隨包散布。

## 列印注意

原始 STL 拓撲、615 個全域層面，以及獨立窗梃、橫桿、帽簷邊、塔柱凹槽局部截面檢查通過本包記錄的篩查；**這不是所有細節可印或免支撐的保證**。細高柱需考慮列印穩定與強度，凹槽上緣、窗框及挑簷需依方向檢查支撐；1 mm 窗梃與 2 mm 帽簷仍受噴嘴、材料及縮放影響。未做實體試印或特定切片器支撐驗證。

## 五視角

| 前右 | 正面 | 後側簡化封閉 |
|---|---|---|
| ![](previews/front.png) | ![](previews/elevation.png) | ![](previews/rear.png) |

| 頂面近似 | 前左 |
|---|---|
| ![](previews/top.png) | ![](previews/left_oblique.png) |

## 重建

安裝 requirements.txt 所列套件後執行 python build_model.py、python qa_model.py、python check_features.py。以 Blender 4.3.2 執行 blender -b --python render_model.py；verify_scene.py 與 verify_render.py 分別核對編輯往返及重開重繪。verify_exchange.py 使用 lib3mf；BUILD_PYTHON 可指定幾何建置 Python。其餘驗證明細見 qa/。

Original model/code: [MIT](LICENSE). Source photographs remain with their respective rights holders. Material colours are approximate display colours, not certified finishes.
