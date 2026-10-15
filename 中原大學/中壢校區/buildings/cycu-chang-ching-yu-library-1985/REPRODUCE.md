# 重建與檢查

實際測試：Python 3.12.14、Blender 4.3.2。請在此建物資料夾的副本執行，以免覆寫保留交付；先建立並啟用venv，讓render_preview.py所呼叫的python3與安裝Pillow的環境一致。

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
command -v python3
python3 -c "import numpy,trimesh,manifold3d,shapely,scipy,rtree,PIL;print(PIL.__version__)"
blender --version
```

Blender由官方版本或系統套件提供；建議固定4.3.2重現PNG bytes。字型使用系統fonts-noto-cjk套件（Debian/Ubuntu可由套件管理員安裝），路徑固定 /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc，face index 3為Noto Sans CJK TC Regular。字型SHA256為b76b0433203017ca80401b2ee0dd69350349871c4b19d504c34dbdd80541690a；其他字型版本可能改變文字像素。

```sh
test -r /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc
sha256sum /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc
python3 -c "from PIL import ImageFont; print(ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',16,index=3).getname())"
python3 build_model.py
blender -b -t 3 --python render_preview.py
python3 validate_model.py
python3 check_layer_components.py
python3 check_feature_losses.py
python3 check_feature_roots.py
OPENBLAS_NUM_THREADS=1 python3 check_dense_first_chords.py
OPENBLAS_NUM_THREADS=1 python3 check_dense_parity.py
OPENBLAS_NUM_THREADS=1 python3 check_short_sections.py
python3 check_coplanar_faces.py
python3 check_thin_features.py
```

密點JSON直接gzip寫入，讀取可用json.load(gzip.open(path,'rt',encoding='utf-8'))；gzip容器時間戳可能不同，應比較完整解壓JSON值而非只比壓縮檔SHA。check_thin_features.py是保留原版1mm輔助檢查；原STL的0.2mm嚴格逐Polygon結果在check_layer_components.py。

預覽v2僅把50px繁中字幕加到原1100×850畫面下方，輸出1100×900；不裁切、不覆蓋原渲染區、不改相機。保留原scene.blend幾何，STL與舊懷恩附件位元不動。原面短首段/根證分類及角損仍以獨立審查裁定，腳本數值不代表自動准印；未試印。
