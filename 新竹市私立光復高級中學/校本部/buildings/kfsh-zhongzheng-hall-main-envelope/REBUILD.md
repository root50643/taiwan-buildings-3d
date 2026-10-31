# 重建

Python環境安裝 requirements.txt 後：
```
python build_model.py
python validate_model.py
python verify_rebuild.py
blender -b -t 4 --python render_model.py
blender -b -t 4 --python verify_scene.py
python verify_render_bindings.py
```
build_model.py 在自身目錄重建STL/3MF/幾何資料；Blender渲染六圖並保存場景。verify_rebuild.py 於全新暫存目錄只複製程序重新生成，逐項比較vertices/faces/materials與STL SHA256。原始參考影像不是重建相依項。
