# 可重建流程

Python 3 + requirements.txt（numpy、trimesh、manifold3d），Blender 4.x。

```sh
python build_model.py
python validate_model.py
python verify_rebuild.py
blender -b -t 4 --python render_model.py
blender -b -t 4 --python verify_scene.py
python verify_render_bindings.py
```

`build_model.py` 不需外部照片或網路，先建立可編輯構件，再實體聯集並保留面材質。`mesh-data.npz` 為 STL/3MF/Blender/render 的同一網格基準。六圖由此網格生成；各圖旁 render.json 綁定網格及腳本 hash。重建 QA 在新暫存目錄執行程式，比對頂點、面、材質陣列與 STL hash。3MF ZIP 容器時間可不同，不作無意義的整 ZIP 位元判準。
