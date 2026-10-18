# 歷史證據的路徑對照

原始執行報告、命令與清單按執行時的位元組保留，因此仍可能出現工作暫存目錄名稱。這些名稱是執行歷史，不是交付包內的可攜式入口。

| 報告中的原名稱 | 本交付包中的位置與用法 |
| --- | --- |
| `manufacturing-qa-staging/run_six_parts_qa.py` | 原協調程式封存在 [qa/bounded-check/coordinator-executed.py](qa/bounded-check/coordinator-executed.py)，供追溯原執行。請依 [README 的重建與檢查指令](README.md) 直接呼叫保留的原始 checker；此歷史協調程式含原工作目錄，不是可攜式重跑入口。 |
| `slicer-review-staging` | 即 [slicing/gyroid15-exploration](slicing/gyroid15-exploration/SLICE-REVIEW.md) 的 15% gyroid 探索紀錄。實心切片報告所稱的原 sibling，對應此歸檔目錄。 |
| `slicer-review-solid-staging` | 即 [slicing/solid100-confirmed](slicing/solid100-confirmed/SLICE-REVIEW.md) 的 100% rectilinear 建議路徑紀錄。 |

兩次切片各自的 `STAGING-MANIFEST.json` 記錄原執行證據的大小與 SHA-256；[套件稽核](qa/manufacturing-package-audit.json) 校驗其全部凍結檔案。本文提供映射，不改寫歷史報告、失敗狀態、檢查旗標或門檻。
