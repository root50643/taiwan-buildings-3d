# 前入口局部模型重建

Python3及requirements.txt，Blender4.3.2；在複製新目錄執行，不覆蓋凍結包。

```sh
python build_model.py
python validate_model.py
blender -b -t 4 --python render_model.py -- --out "$PWD"
blender -b scene.blend --python verify_scene.py -- --out "$PWD"
```

場景有一個合併交付網格及隱藏可編輯構件（仍有設計重疊，不能直接當列印網格）。沒有外部影像或貼圖依賴。
