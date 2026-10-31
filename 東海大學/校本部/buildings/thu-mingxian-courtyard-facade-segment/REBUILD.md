# 重建

Python3、requirements.txt依賴，Blender4.3。所有模型可從程式重建，不需來源照片。

```sh
python build_model.py
python validate_model.py
python verify_rebuild.py
blender -b -t 4 --python render_model.py
blender -b --python verify_scene.py
```

輸出覆寫本目錄生成檔；先另存舊版。前方為局部-y，不表示地理南北。verify_rebuild在全新暫存目錄重建再逐項比較，不修改原交付檔。
