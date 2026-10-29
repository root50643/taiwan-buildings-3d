# 從原創腳本重建

需Python3.12相容環境、`requirements.txt`所列三套件，及Blender4.3.2或相容版本。

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python build_model.py
.venv/bin/python validate_model.py
blender -b -t 4 --python render_model.py
blender -b scene.blend -t 4 --python verify_scene.py
```

腳本只讀寫同資料夾，不下載、不讀私有來源檔、不需要網路、憑證或材質圖片。`build_model.py`產出融合STL、彩色3MF、mesh-data及逐構件JSON；`render_model.py`從同一融合網格產生七圖並存可編輯native場景。3MF ZIP固定時間戳；幾何中間簡化容差為模型0.003mm，只消除數值退化，不以刪除不相連真構件補PASS。

Blender的隱藏`EDITABLE authored parts`群組包含融合前原構件；需自行顯示該群組再編輯，會有預期重疊，並不等於單一列印網格。唯一可見的融合物件才與STL／3MF等值。源證與當前模型限制見README；尚未實體試印。

3個隱藏編輯構件標`construction_operation=subtract`，為非史實底座／廊地板檢查孔的刀模；不可將它們當一般union構件加回。程式重建已明確先融合正構件再扣除刀模。
