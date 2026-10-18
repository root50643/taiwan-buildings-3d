# 固定 76681 候選的獨立覆核證據匯入

請先讀 [完整獨立總覆核](INDEPENDENT-CSU-REVIEW.zh-TW.md)。它針對固定提交 `76681c5dcedc88d684946780e795d7914a88c075`，結論為有製造條件的低細節代表模型 GO；主體、屋蓋與組裝 STL 的固定 SHA 仍相同。它不是對後續說明修正或新 Git HEAD 的整包重新覆核。

本目錄包含總覆核、三份來源／幾何／製造報告與 JSON、場景／重建證據、新獨立渲染、實際使用的算法與封裝 helper。未匯入第三方原照、來源 PDF／raster、執行環境、重建重複 STL 或舊 ZIP。

來源清單 [evidence-manifest.json](evidence-manifest.json) **只描述覆核者原始位元組**。含私人路徑的交付檔案已遮蔽；原 hash 並未改成新 hash。[import-manifest.json](import-manifest.json) 逐檔列出來源／交付 SHA、大小、遮蔽類別與位置；遮蔽前原檔留在作者工作區的非公開 private-logs，未放入模型包。`<MODEL_ROOT>`、`<REVIEW_ROOT>`、`<REFERENCE_SOURCE_ROOT>` 等是明示遮蔽標記，不是假裝存在的路徑。

所有原始數字、座標、旗標、判斷及報告所記原腳本 hash 保留。路徑被遮蔽的腳本因而有新的交付 hash，其對應關係以匯入清單為準。六條共面射線歧義、71 條真屋簷薄邊、原嚴格 false、0.650001526 mm 門凹與 16.6 mm 門頂路徑、82,153 段／7,273.39394 mm 支撐等均未覆寫。

獨立新渲染 PNG 的 `File` 附加文字 tag 亦含本機場景路徑，已單獨遮蔽。只改該 PNG ancillary text chunk 與其 CRC；所有 IDAT 壓縮像素資料及解碼像素 SHA 均與原圖相同。歷史場景 JSON／原 manifest 仍記錄未遮蔽原 PNG 的 SHA，交付 PNG 的新 SHA 及像素一致證據見匯入清單，沒有改歷史 hash 來假裝原始位元相同。

`verify_identity_rebuild.py`、`finalize_review.py` 是**歷史流程來源**，不是目前候選的重驗入口：它們依賴當時 HEAD、包外 Library 回條及整個舊 snapshot。匯入新增 QA 檔案後重跑原 finalizer 本來就會出現 changed；不能硬清此結果。兩檔加了明示停止保護，避免覆寫封存證據。兩個 verification helper 保留原算法；其舊 NTHU 專用 `__main__` 亦不是 CSU 入口。

如需重跑，使用新的 `reproduce.py`。它先核實兩個固定分件 SHA，要求輸出到模型包以外的新目錄，僅在暫存腳本中綁定讀取／輸出路徑及封裝 helpers，不改算法或舊報告：

```text
python -B qa/independent-76681/verify_import.py --output FRESH_IMPORT_CHECK_JSON
python -B qa/independent-76681/reproduce.py --mode controls --output FRESH_REVIEW_DIRECTORY
python -B qa/independent-76681/reproduce.py --mode geometry --output FRESH_GEOMETRY_DIRECTORY
python -B qa/independent-76681/reproduce.py --mode manufacturing --output FRESH_MANUFACTURING_DIRECTORY
python -B qa/independent-76681/reproduce.py --mode scene --output FRESH_SCENE_DIRECTORY
python -B qa/independent-76681/reproduce.py --mode rebuild --output FRESH_REBUILD_DIRECTORY
```

在模型根執行。controls 需 Python 標準庫；geometry 另需 NumPy；manufacturing 需 NumPy、Shapely、Manifold3D；scene 需 bpy；rebuild 需 Git 中仍有固定提交物件與原生成器所用 NumPy、Trimesh、Manifold3D。重建入口從固定 Git 提交讀原生成器／參數，與目前固定 STL 比較，避免把後續文件參數修正誤當原覆核輸入。

重跑結果屬新的執行紀錄，腳本 hash 因路徑綁定會不同，不能冒稱覆核者原始執行。完整來源像素視看是歷史覆核記錄；第三方來源未隨包再分發。此匯入只做證據完整性、必要 helper 控制／原始拓樸的輕量核對，沒有重跑完整製造／場景覆核或實體試印。
