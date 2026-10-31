# 重建
Python3 with numpy, trimesh, manifold3d；Blender4.3.2。安裝requirements後：

```sh
python build_model.py
python validate_model.py
python verify_rebuild.py
blender -b -t 4 --python render_model.py
blender -b --python verify_scene.py
python verify_render_bindings.py
```

生成不需照片、不連網；程式寫入所在資料夾。verify_rebuild在新暫存資料夾重建並比對頂點/面/材質與STL SHA256。Blender以真實mesh-data渲染，不使用參考照片作紋理。
