# 可重建檢查
使用含 numpy、trimesh、manifold3d 的 Python 執行 `build_model.py`。用 `verify_rebuild.py` 在新暫存目錄重新建模，比對頂點、面、材料與 STL 雜湊。Blender 4.3.2 執行 `render_model.py` 產生六圖與 scene.blend；`verify_scene.py` 比對場景與網格並檢查完整視圖 framing。`verify_render_bindings.py` 驗證每圖與腳本／網格綁定。名義模型可重建不等於建築測繪精確。
