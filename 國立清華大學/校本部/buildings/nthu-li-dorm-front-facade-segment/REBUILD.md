# 重建

Python3、requirements.txt依賴，Blender4.3。所有模型可從程式重建，不需來源照片。

```sh
python build_model.py
python validate_model.py
python verify_rebuild.py
blender -b -t 4 --python render_model.py
blender -b --python verify_scene.py
```

生成檔寫回本目錄，先備份再執行。局部正面是-y，不主張地理方位。verify_rebuild在新暫存目錄重建比對。
