# 重建
安裝 requirements.txt 所列套件後：
```sh
python build_model.py
python validate_model.py
python verify_rebuild.py
blender -b --python render_model.py -- --out "$PWD"
blender -b --python verify_scene.py
python verify_render_bindings.py
```
全部幾何與材料由程式產生，不依賴參考照片或網路。`verify_rebuild.py` 在乾淨暫存目錄重新執行生成器，逐一比較頂點、面、材料索引與 STL SHA256；不是只重複讀取原檔。

局部單位為作者名義比例，1 單位 = 7 模型 mm，非1:真實量尺。展示底板為作者支撐；實際建築尺寸不由模型比例反推。
