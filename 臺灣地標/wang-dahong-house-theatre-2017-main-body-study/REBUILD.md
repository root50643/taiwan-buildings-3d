# 復建主體研究模型重建

使用Python3及requirements.txt、Blender4.3.2。在新複製目錄執行，勿覆寫已凍結包。

```sh
python build_model.py
python validate_model.py
blender -b -t 4 --python render_model.py -- --out "$PWD"
blender -b scene.blend --python verify_scene.py
```

場景包含一個合併交付網格及隱藏可編輯構件；後者保留建構重疊，不能直接當列印網格。沒有外部貼圖/影像依賴。
