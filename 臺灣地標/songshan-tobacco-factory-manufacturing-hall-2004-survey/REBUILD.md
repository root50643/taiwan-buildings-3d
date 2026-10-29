# 可重現重建

Python3.12、requirements.txt、Blender4.3.2。

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python build_model.py
.venv/bin/python validate_model.py
blender -b -t 4 --python render_model.py
blender -b scene.blend -t 4 --python verify_scene.py
```

腳本讀同目錄geometry-controls.json與opening-controls.json，不下載來源或依賴私人文件。成品只有一個可見融合網格；隱藏構件附證據，未融合構件預期重疊，不能當已驗證成品列印。

固定種子與ZIP時間。PNG helper只剝除文字／時間／EXIF，不改像素；BLEND原生檔不主張逐位元組一致。幾何簡化容差約0.000833mm，沒有刪除分離零件湊合驗證。
