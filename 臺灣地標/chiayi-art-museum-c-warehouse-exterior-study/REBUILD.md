# 重建

在含 numpy、trimesh、manifold3d 的 Python 環境執行 `python build_model.py`，再執行 `python validate_model.py`。以 Blender 4.3.2 執行 `blender -b --python render_model.py`，再以 `blender -b scene.blend --python verify_scene.py` 重開驗證。版本記錄見 requirements.txt。重建會改寫本資料夾輸出，請在副本執行。前次 Blend 備份 .blend1 不屬發布包。
