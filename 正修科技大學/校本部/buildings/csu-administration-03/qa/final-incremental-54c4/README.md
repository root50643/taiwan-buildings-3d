# 54c4 最終增量覆核：安全匯入副本

請讀 [完整最終增量覆核](FINAL-INCREMENTAL-REVIEW.zh-TW.md) 與 [原最終驗證](final-verification.json)。固定覆核提交為 `54c4ad2a30e6600e85fbf054d4c384f9e5304748`，比較基線為 `76681c5dcedc88d684946780e795d7914a88c075`；其增量結論為 GO，先前門凹／參數聲明必修已解除。整體仍是有製造條件的代表模型 GO，沒有改成實印、免支撐、清除或膠合驗證通過。

本目錄只增加證據記錄，不修改既有模型、場景、G-code、參數或舊 QA。原報告的 377 個追蹤檔、22 個既有修改、40 個新增及當時 Library v1 回條等都屬固定覆核時點，並非加入本目錄後的最新檔案數或 Library 版本。

[evidence-manifest.json](evidence-manifest.json) **僅描述覆核者的原始位元組（source-only）**。已先核對其中全部 10 檔的大小及 SHA，再匯入全部獨立證據，另保留原交付回條。原 ZIP、重建資料夾、重複 STL、來源照片及環境未放入本目錄。

[import-manifest.json](import-manifest.json) 逐檔記錄原／交付大小與 SHA、遮蔽類別、原／新行號及 JSON pointer。私人主機路徑以 `<MODEL_ROOT>`、`<REPO_ROOT>`、`<FINAL_REVIEW_ROOT>`、`<AUTHOR_TASK_ROOT>` 等明示標記取代；這些是遮蔽標記，不是假裝存在的路徑。遮蔽前原檔留在作者工作區的非公開 `private-logs/final-incremental-54c4/`，沒有放入公開模型包。

匯入對所有原 JSON 做遞迴型別、鍵、陣列長度及值比較；數字、座標、布林、null、原旗標、結論及記錄的歷史 hash 完整保留，只變更六個路徑字串。覆核來源整個目錄匯入前／後的大小與 SHA snapshot 一致。報告所記腳本 SHA 仍是原執行版本；路徑遮蔽與停止保護後的交付腳本有另列新 SHA，不冒稱兩者位元相同。

三支原腳本 `independent_incremental_check.py`、`check_imported_evidence.py`、`finalize_incremental.py` 為 **historical provenance-only**，不是目前發布樹的重驗入口。它們依賴當時 HEAD、舊整包 snapshot、封裝外原始覆核及 Library 回條，且會重建或覆寫報告；已加明示停止保護。不能清空新增目錄造成的 changed，也不能把歷史 54c4 整包檢查冒稱已覆核日後的 Git HEAD。此匯入未執行這些歷史流程，沒有重跑完整 QA、切片或渲染。

可從模型根以 Python 標準庫重做本次**匯入完整性**檢查，輸出需使用尚不存在的檔名：

```text
python -B qa/final-incremental-54c4/verify_import.py --output FRESH_IMPORT_VALIDATION_JSON
```

它只核交付檔案、原清單映射、相對連結、私人路徑與固定三件 STL 的 SHA，不改任何舊報告，也不把匯入完整性 true 當作嚴格製造或實體試印 true。
