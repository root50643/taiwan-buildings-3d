# 原碼重建

在新的工作目錄保留 source/build_model.py、source/render_preview.py、parameters.json 與 requirements.txt 的原 bytes。參數 revision 為 v10。使用 Python 3.13 與 requirements.txt 中的固定套件版本，建模命令為：

    python -B source/build_model.py --output-dir models/v10

此步產生原創真 CSG 聯集與差集後的 STL、材質分區及參數／源碼快照。不要先對 STL 自動修補、重網格化或縮放再宣稱與原檔相同。

渲染使用 Blender 4.3.2，單 CPU、單執行緒、Cycles 64 samples、1000 × 780、seed 0、不使用去噪。七張全景用正交相機，兩張細節用 20mm 透視相機。原 render_preview.py 會保存 scene.blend 與九張預覽及綁定 manifest；圖像沒有載入來源照片當貼圖。

機器檔名 east、west、south、north 不表示地理方位；courtyard-gallery 是外架近景，courtyard-arcade 是 B 端屋面平台近景。中文說明以 VIEW-CAPTIONS.zh-TW.json 為準。

作者來源重建、完整場景狀態比較與 saved-Blend inspect-only 各執行一次，PNG 控制測試分 normal / -O；唯一正式 saved-Blend 九圖重播由獨立 QA 執行。完整命令、原結果、flags、修正歷史與精確範圍另見科學證據。
