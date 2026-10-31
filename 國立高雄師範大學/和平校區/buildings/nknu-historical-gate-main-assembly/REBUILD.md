# 重建

Python 3、numpy、trimesh、manifold3d；渲染使用 Blender 4.3.2。

```sh
python build_model.py
python validate_model.py
python verify_rebuild.py
blender -b -t 4 -P render_model.py
blender -b scene.blend -P verify_scene.py
python verify_render_bindings.py
```

`build_model.py` 中的名義數值、`P` 與構造函式可編輯；`parameters.json` 是本次主要參數摘要，不是外部輸入設定檔。不需要下載原始照片。布林結合後先消除微小共面接縫，再於 0.01 mm 網格以 manifold3d 重新建構連通拓樸；顏色按原施工面三角形中心的最近鄰確定性映射。此清理不是量測精度宣稱。隱藏施工分件保留原始重疊關係，不當作可直接列印的獨立零件集合。
