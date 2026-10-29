# 可重現重建

Python3.12、requirements.txt及Blender4.3.2。

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python build_model.py
.venv/bin/python validate_model.py
blender -b -t 4 --python render_model.py
blender -b scene.blend -t 4 --python verify_scene.py
```

不下載或依賴原圖／PDF／憑證。最後融合網格同時輸出STL、3MF、NPZ；場景只有一個可見成品網格，所有隱藏編輯構件逐件附證據。顯示編輯構件時有預期重疊，不應拿未融合構件直接當已驗證成品。

固定渲染種子、ZIP時間；PNG helper僅剝除文字／時間／EXIFmetadata，不改影像像素。Blender原生檔可有存檔環境差異，重建對照幾何及影像。簡化容差約0.00167mm，未以刪除不連通零件湊合驗證。
