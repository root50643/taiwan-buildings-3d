# 重建

Python 3 + requirements.txt；Blender 4.3.2。只在複製的新目錄運行，勿覆蓋凍結包。

```sh
python build_model.py
python validate_model.py
blender -b -t 4 --python render_model.py -- --out "$PWD"
blender -b scene.blend --python verify_scene.py -- --out "$PWD"
```

Blender保存交付合併網格及隱藏的可編輯構件集合。隱藏構件尚有設計重疊，不能直接當成最終可列印網格；STL/3MF才是一體合併版本。無外部貼圖。
