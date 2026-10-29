# 可重現重建

需要Python3.12、requirements.txt所列套件及Blender4.3.2或相容版本。

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python build_model.py
.venv/bin/python validate_model.py
blender -b -t 4 --python render_model.py
blender -b scene.blend -t 4 --python verify_scene.py
```

腳本只讀寫同資料夾，不下載、不需憑證或來源圖片。八圖直接渲染融合網格，3MF保留逐面色；STL不保留色彩。所有正構件先融合，再扣除標記subtract的缺門/孔洞/煙囪口刀模。作者盲孔深度及暗色內面不是完整室內。隱藏構件可編輯，顯示後會有預期重疊；唯一可見融合物件才等於最終網格。

簡化容差模型0.0025mm，未用刪除不連通構件方式湊合檢查。固定3MF ZIP時間與渲染種子；Blender檔可能含存檔環境差異，幾何和逐圖像素才是乾淨重建的等值檢查對象。

`render_model.py` 呼叫同包 `normalize_previews.py`，只剝除PNG文字／時間／EXIF附加欄位，不重壓影像或改變像素，避免公開主機路徑。

獨立構件查核：`.venv/bin/python review/check_model.py`。乾淨重建結果見 `REBUILD-QA.json`；STL、3MF、NPZ與兩份構件資料逐位元相同，八圖像素相同。
