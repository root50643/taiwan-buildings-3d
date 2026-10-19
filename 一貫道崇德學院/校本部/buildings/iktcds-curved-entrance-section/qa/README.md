# 數位檢查索引

- [來源與預覽實看](source-appearance-review.json)：兩張原圖、限定七柱／六柱間／三門，四視圖及裁切說明。
- [建模摘要](build-geometry.json)：四種原型、十實例、八材質與估計尺寸。
- [STL、四十五組接觸與截面篩檢](geometry-validation.json)：柱原型2與弧簷2旗標保留，非真正FFF切片。
- [Core 3MF嚴格匯入／材質編輯](exchange-validation.json)：原型面序、面色、十實例變換及編輯重存量化。
- [乾淨重建](rebuild-validation.json)：同一套既有依賴，幾何、四STL與五3MF的SHA比較。
- [場景重開](scene-validation.json)：十網格物件、四原型、八材質、組裝變換，無原圖或外部庫。
- [渲染紀錄](render-manifest.json)及[PNG像素與metadata](preview-validation.json)。

本包數位驗證只支持有界外觀、幾何、配色及資產一致性；測繪精度、真機切片、支撐、實印、試合、膠合與全校完成均未聲稱。

## 使用既有工具重建

在具有所列依賴的 Python 環境執行 source/build_model.py、source/build_exchange.py；再以 Blender 4.3.2 執行 source/render_preview.py。對應 verify_geometry.py、verify_exchange.py、verify_rebuild.py 以 Python 執行，verify_scene.py 以 Blender 執行，sanitize_previews.py 僅清除PNG非像素metadata。工具版本由各報告記錄；不同工具版本不保證位元一致。來源原圖不參與重建，也不需要字型檔。
