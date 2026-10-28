# 重建

既有Python環境：trimesh5.2.0、manifold3d3.5.4、numpy；Blender4.3.2。

```sh
python build_model.py
python validate_model.py
blender -b -t 4 --python render_model.py
blender -b scene.blend --python verify_scene.py
```

建構先用100內部單位/m，輸出乘0.08，結果8mm/來源公尺。數值正規化不增加測繪精度。無網路下載依賴，來源影像不嵌入輸出。
