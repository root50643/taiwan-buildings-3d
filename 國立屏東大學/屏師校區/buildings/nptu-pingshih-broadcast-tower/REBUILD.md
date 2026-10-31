# 重建
Python 3、numpy、trimesh、manifold3d（實際環境版本見 requirements.txt）與 Blender 4.3.2。

```sh
python build_model.py
python validate_model.py
python verify_rebuild.py
blender -b -t 4 --python render_model.py -- --out "$PWD"
blender -b -t 4 --python verify_scene.py
python verify_render_bindings.py
```

建模由程式與名義參數重建，不需要原始參考圖片。SCALE=1 表示程式座標使用模型毫米，並不表示實物 1:1。Fresh-directory rebuild 驗證 vertices/faces/materials 精確一致及 STL SHA256 相同；3MF zip 容器時間戳不作位元一致要求，另檢查其幾何與面色。

六圖均實際渲染同一成品網格，PNG 綁定 mesh/script SHA256；沒有後製拼貼或虛構未生成預覽。
