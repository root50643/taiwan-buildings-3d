# 重建方式

既有測試環境：Python3、trimesh5.2.0、manifold3d3.5.4、numpy；Blender4.3.2。

```sh
python build_model.py
python validate_model.py
blender -b -t 4 --python render_model.py
blender -b scene.blend --python verify_scene.py
```

用既有環境或自行依requirements.txt建立環境；腳本不下載照片或網路資料。source geometry uses100internalunits/m,then scales0.1tooutputmm; numericalrobustness normalization only. All screenshots generated from final mesh.
