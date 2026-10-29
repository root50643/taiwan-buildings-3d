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

腳本不連線、不需來源PDF、圖片或憑證。單一可見融合網格是匯出成品；隱藏編輯構件包含預期重疊與逐件來源證據。所有圖由同一最終網格渲染，沒有貼入照片。3MF逐面色；STL無色。

固定隨機種子及ZIP時間，PNG helper只移除文字／時間／EXIFmetadata，不改像素或重壓IDAT。Blender原生檔可能有環境差異，重建比較幾何和逐圖像素。簡化容差0.01mm，未任意刪除斷開構件。

獨立驗證可執行 `.venv/bin/python review/check_model.py`，只依requirements套件，不需scipy或networkx。獨立source gate見 `review/source-preflight.json`。

乾淨重建結果見REBUILD-QA.json：STL/3MF/NPZ/兩份構件JSON與八張PNG逐位元相同，兩邊場景重開核對均通過。
