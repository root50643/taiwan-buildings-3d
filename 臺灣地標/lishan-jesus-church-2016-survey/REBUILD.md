# 可重建流程

Python 3.12、requirements.txt 所列套件、Blender 4.3.2。

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python build_model.py
.venv/bin/python validate_model.py
blender -b -t 4 --python render_model.py -- --out "$PWD"
python normalize_previews.py
blender -b scene.blend -t 4 --python verify_scene.py
```

opening-positions.json 是作者量圖控制；script 可在無網路、無原始 PDF 下產出主體、兩低翼、三面真開口門廊、鐘塔與小塔。實心外觀不代表完整室內。BLEND 可見聯集對應 STL／3MF；隱藏構件保留布林前資訊，不能當最終聯集直接印。

Cycles 40 samples、seed 0、固定4執行緒、1800×950；七整體與兩刻意裁切細節。normalize_previews.py 只去 PNG 時間／主機metadata，不改像素。相同環境以五幾何檔與九PNG逐byte比對；BLEND重開採語意及網格檢查，不要求二進位相同。不同版本／CPU可能改變網格序或像素。未物理試印。

獨立幾何檢查：於根目錄執行 `python review/check_model.py .`。此程式不取代逐張視覺與來源審查。
