# 可重建流程

Python 3.12、`requirements.txt` 所列套件、Blender 4.3.2。

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python build_model.py
.venv/bin/python validate_model.py
.venv/bin/python review/check_model.py .
blender -b -t 4 --python render_model.py -- --out "$PWD"
python normalize_previews.py
blender -b scene.blend -t 4 --python verify_scene.py
```

腳本不需網路或原 PDF，即可重建整個連接 A 棟外觀、展示底座、材質、九視圖與可編輯建構零件。尺寸來源與不確定性見 `parameters-evidence.json`；開口控制見 `opening-positions.json`。隱藏零件尚有建構重疊，不可直接當最終聯集印製；`scene.blend` 可見網格才對應 STL／3MF。

Cycles 40 samples、seed 0、固定4執行緒、1800×950。七整體與兩刻意裁切細節；PNG normalizer 只移除時間／主機路徑 metadata，不改像素。同環境以五個幾何檔與九 PNG 逐 byte 比對；BLEND 採重開語意及網格相等檢查，不要求二進位檔相同。不同套件／CPU 可能改變網格序或像素。本模型未物理試印。
