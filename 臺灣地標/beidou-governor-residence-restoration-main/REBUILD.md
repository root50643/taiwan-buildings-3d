# 重建

使用 requirements.txt 已列套件及 Blender 4.3.2：

```sh
python build_model.py
python validate_model.py
blender -b -t 4 --python render_model.py --
blender -b scene.blend --python verify_scene.py
```

建模為確定性參數程序；六視圖取實際統一網格。Blender另保留隱藏可編輯來源構件，其重疊不等於可直接列印網格。未試印。來源原件不需作執行依賴。
