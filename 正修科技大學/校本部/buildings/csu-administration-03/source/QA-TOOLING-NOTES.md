# QA 工具快照與本輪文件勘誤

`qa/` 子目錄內可執行工具是原作者執行 v1/v2 檢查時的凍結源碼，既有報告依其 SHA 綁定。`qa/run_slice.py` 的 `limits` 固定文字及 `qa/audit_gcode.py` 舊 docstring 說支撐關閉，對 auto45 是不正確的歷史敘述；不應把該快照當自動選擇正確配置的現用交接工具。現用 `qa_audit_gcode.py` 的 docstring 已改為讀取實際 embedded support config；執行邏輯沒有變，原版另存於[歷史源碼](../qa/documentation-revision-1/legacy-source/qa_audit_gcode.py)。既有 corrected-audit 綁定原版 SHA，不假稱當時執行過新 docstring；增量校驗另檢查兩者去除 docstring 後 AST 相同，並獨立重讀原 G-code。

原錯誤輸出、工具源碼與旗標保留；本輪不覆寫歷史 SHA 或失敗紀錄來假稱先前通過。正式交接請讀 [完整 QA 說明](../QA.md)、[勘誤與本輪增量校驗](../qa/documentation-revision-1/README.md)及[獨立覆核](../qa/independent-76681/INDEPENDENT-CSU-REVIEW.zh-TW.md)。新增 `validate_documentation_revision.py` 專做本次聲明修正的 raw-STL 線量測、實際 G-code 路徑／支撐重讀和固定檔案比對，並非全域製造或試印證明。
