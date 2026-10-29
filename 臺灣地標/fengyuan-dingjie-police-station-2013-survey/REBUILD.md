# 可重建流程

Python 3.12、requirements.txt 所列套件、Blender 4.3.2。

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python build_model.py
.venv/bin/python validate_model.py
blender -b -t 4 --python render_model.py -- --out "$PWD"
blender -b scene.blend -t 4 --python verify_scene.py
```

opening-positions.json 為作者量圖控制，不是原始圖。腳本包含調查時期五邊形主體、各面獨立窗位與東側一／二層鐵皮附建，不需網路或原始PDF即可重建。幾何為實心外觀代理，屋梯間盲門凹槽不代表完整室內樓梯。BLEND可見聯集網格對應STL／3MF；隱藏構件保留布林前編輯資訊，不能直接作為最終聯集成品。

Cycles 40 samples、seed 0、固定4執行緒，1800×950；七張整體加兩張刻意裁切細節。PNG用normalize_previews.py移除主機及時間metadata而不改像素。相同環境乾淨重建比對五項幾何檔與九張PNG逐byte；BLEND以重開後語意、網格、來源欄位檢查，不要求二進位完全相同。不同CPU或套件版本可能改變像素或三角形順序。未物理試印。

獨立38項幾何控制可從本包根目錄執行 `python review/check_model.py .`。結果寫入review/model-independent-check.json，視覺審查仍須另讀九張圖，不可用程式結果代替。
