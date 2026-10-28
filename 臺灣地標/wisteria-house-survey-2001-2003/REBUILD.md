# 重建

在獨立目錄以Python 3及requirements.txt所列依賴，執行：
```sh
python build_model.py
python validate_model.py
blender -b -t 4 --python render_model.py
blender -b scene.blend --python verify_scene.py
```
Blender4.3.2。不要在已發布凍結包內覆寫。參考原圖不參與生成，網路不是重建依賴。
