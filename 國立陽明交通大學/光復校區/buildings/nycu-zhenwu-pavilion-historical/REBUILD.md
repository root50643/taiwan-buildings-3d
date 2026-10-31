# 重建

使用 requirements.txt 的 Python 套件，執行：
```
python build_model.py
python validate_model.py
python verify_rebuild.py
blender -b -t 4 --python render_model.py
blender -b -t 4 --python verify_scene.py
python verify_render_bindings.py
```
完全不需下載或嵌入來源照片。verify_rebuild 在新暫存目錄獨立重建，逐項核 vertices/faces/materials 與 STL SHA256；圖片用各自 camera/hash binding核對，不以檔名判新舊。
