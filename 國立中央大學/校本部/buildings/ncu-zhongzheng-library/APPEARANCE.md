# 中央中正圖書館｜有限彩色外觀增補

## 原幾何及代表圖不變

原1,060頂點／2,292三角面／transform／150×142×42mm完全保留。原STL、OBJ、scene.blend、build_model.py、render_preview.py、三張原預覽與QA證據不動；不改學校／校區／首頁代表圖，不新增建築或構件。兩份README同加新彩圖，原單色圖仍明示保留。新增appearance.blend／appearance.3mf／五張appearance圖與重建腳本。

## 真照片與年代範圍

配色來自[校方中正圖書館整修募款頁](https://give.ncu.edu.tw/project_/42)兩張實景照片：[白米柱廊與花格](https://give.ncu.edu.tw/uploads/20250527214830360.jpg)、[另一面灰綠牆／內院合圖](https://give.ncu.edu.tw/uploads/WEB%E8%88%8A%E5%9C%96114-0604.png)。不是設計效果圖。頁面刊登2025-05-27、更新2025-06-04不等於拍攝日期，更不是修復完工證據；照片拍攝日未明。本件不聲稱呈現翻修後或2026現況。來源URL／照片雜湊見appearance-sources.json；不附照片/PDF公開副本。

照片可見白米柱廊、白米細花格、灰色階及灰綠暗色後方。原模型花格已粗化為有背襯凹槽，只於現有凹底用低飽和灰綠proxy，不造新孔、不稱每格是玻璃、不把照片陰影當校準材料。周圍既有同類柱廊採相同白米色，為同類材料延伸推定，側後逐孔未核。另一面灰綠實牆的照片沒有驗證方位，不能任意塗上整個側/背面。

未知屋頂水平面、院內牆/地、側後填牆和人工底座中性灰，不添加綠草、園景拱牆、石獅、冷氣、金色字或時鐘指針。原無標記時鐘圓片保留淡中性色，未由新照片確證錶面。sRGB只作照片近似，渲染轉linear，不是校準塗裝規格或透光物性。

## 重建及QA

Blender4.3.2，原scene.blend/model.stl與script同目錄：

```sh
MALLOC_ARENA_MAX=2 LP_NUM_THREADS=1 OMP_NUM_THREADS=1 blender -b -t 1 --python-exit-code 1 -P build_appearance.py
blender -b --python-exit-code 1 -P verify_color_geometry.py -- scene.blend appearance.blend appearance-geometry-QA.json appearance.3mf
```

只寫新增appearance檔，不覆寫原件。Cycles CPU32samples/seed0/單執行緒；PNG移除所有文字metadata並保留IDAT，3MF用原頂點與面索引／逐三角base材料，完整double座標且固定ZIP時間。兩次獨立重建比較script/3MF/materialJSON/PNG byte；BLEND按語義驗證不保證容器byte。3MF軟體需支援材質，不附AMS耗材/多噴頭工具映射。

原天井比例、屋面厚度與側後柱廊是有界估計，不是測繪。這次只驗同幾何、配色、視圖與重建，不改寫原QA警示。原42層1mm pitch／半徑0.4mm（直徑0.8mm）XY開運算不是全向最薄壁或slicer工具路徑保證；挑廊、柱、屋緣需縮尺支撐檢查，未實體試印，不保證免支撐、必然可印或真實結構安全。
