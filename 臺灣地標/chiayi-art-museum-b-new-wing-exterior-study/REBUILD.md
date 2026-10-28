# 重建

使用 requirements.txt 所列 Python 套件執行 `python build_model.py`、`python validate_model.py`。使用 Blender 4.3.2 執行 `blender -b --python render_model.py -- --out /absolute/output`，再 `blender -b scene.blend --python verify_scene.py -- --out /absolute/output`。來源原圖不是重建依賴。

所有尺寸與省略限制見 README；重建相同不等於建築實測正確。
