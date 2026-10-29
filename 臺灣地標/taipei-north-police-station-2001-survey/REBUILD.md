# 可重建流程

Python 3.12；套件版本見 `requirements.txt`；Blender 4.3.2。

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python build_model.py
.venv/bin/python validate_model.py
blender -b -t 4 --python render_model.py -- --out "$PWD"
blender -b scene.blend -t 4 --python verify_scene.py
```

`opening-positions.json` 為作者量圖控制，不是原圖。`build_model.py` 內保留每層獨立平面尺度、來源頁碼、來源尺寸／圖尺值／展示代理區分。幾何腳本不用網路或原PDF。

單一可見聯集網格與STL／3MF一致；BLEND另存隱藏可編輯構件及來源文字。隱藏構件為布林前建構資料，不能直接當成已布林的完整成品。入口及車道先對主體扣除，之後補柱；底層帶在車道處也中斷。門窗不透明面不代表室內玻璃或真實洞深。

Cycles 40 samples、seed 0、固定4執行緒，1800×950、七張完整視圖加兩張刻意裁切細節。PNG用 `normalize_previews.py` 移除主機路徑／時間metadata。對相同環境的乾淨重建比較五項幾何資料與九張PNG逐byte；BLEND做語意、網格、來源、外部影像檢查，不要求二進位檔逐byte一致。

不同Blender／Manifold版本、CPU或平台可能改變像素／布林三角形順序；請以本包 `REBUILD-QA.json` 記錄的環境為準。未做物理試印。
