# 嘉藥 J 司令台：獨立證據整合增量覆核

判定：**GO — 僅就歷史證據整合忠實性；無此分項必修阻擋。**

固定候選提交：`7cf0563a06858137f51751600348a35198c8f6f2`。上游獨立審查固定輸入為 `3a9a6041c5fde9ef2d6e9e96b02f24f025c8be5a`。此分項沒有重新計算幾何、橋接或支撐射線，也沒有切片、試印、實拆支撐、試合或測膠強度。整體固定 STL 仍須遵守既有有條件 GO；此分項不放行原主體自動橋向診斷印法。

## 實際核對

直接讀取本機舊獨立審查輸出及新候選 `qa/independent-support-review/`，沒有僅採信整合檢查的 `passed` 欄位。

- 來源清單 69 檔，整合目錄共 73 檔。新增四檔為 `INTEGRATION-README.md`、`integration-source-manifest.json`、`integration-validation.json`、`replay_support_access.py`。
- 69 檔來源及整合 SHA-256／大小全部重新計算，均符合逐檔映射清單。
- 52 檔逐位元組相同；17 檔只套用明列的私有絕對路徑 → 語意角色替換。核對採嚴格的預期替換後整檔位元組相等，並逐檔核對替換角色及次數；沒有容許一般文字重寫、數值變更或任意忽略行。
- 重新遞迴比較全部 JSON 結構、型別、非路徑文字及 **898,548 個數值／布林／null 葉節點**，均一致。原先的數值、座標、門檻、判定與失敗紀錄未被改寫。
- 73 檔全部與新固定提交的 Git blob 位元組相同，路徑集合亦相同。此核對未寫入原候選。
- 原始四份 QA 說明／失敗紀錄另外與舊候選核對：`qa/README.md`、凍結前幾何失敗、座標排序場景失敗與 OpenGL 工具失敗，皆逐位元組相同。凍結前 `pass:false`／`input_sha256_unchanged_after_review:false` 和座標排序 `pass:false` 均保留。
- 所附五份 NPZ 通過 ZIP CRC 檢查且與來源位元組相同。所附 Python 檔通過語法解析；這只證明可解析，沒有冒充演算法重新執行。

## 支撐及短向修正證據

原主體支撐 26,586 段／83,924 個唯一樣點，修正變體為 30,369 段／95,890 個唯一樣點，兩組各自保留完整 JSON 與 NPZ。兩組都有 580 個八向水平直射線受限旗標，實際座標清單各有 580 點且相等；沒有刪掉這批旗標，再把後續折線路徑解釋當成原直線檢查通過。

長橋接覆蓋 JSON、短向橋接 JSON、兩組支撐可達性 JSON 與路由補證都與上游來源位元組相同。上游報告及摘要仍保留 `as_delivered_main_slicing_process: NOT_ACCEPTED`、`unconditional_package_GO:false` 和 `CONDITIONAL_GO_FIXED_STLS`。

整合說明清楚區分舊平台約 174.289 mm 的中心線未承托段、短向變體約 1.704001 mm，以及仍保留的主體 8.224913 mm／棚板 8.036027 mm 內填充封頂空段。約 2.600011 mm 的棚板盲槽跨度沒有被用來掩蓋較大的內部橋接。

新增 `replay_support_access.py` 的原始碼已與舊 `analyze_support.py`、`support-route-followup.py` 對讀：保留同一 G-code→組裝座標偏移、最大 1 mm 樣點步距、小數五位去重、八方向、1e-5 mm 射線端點裕量、三段側向路由，以及 0.5 mm 半徑／65 周向樣線。新入口提供明確輸入、輸出與拒絕覆寫；本分項沒有執行此有限射線重跑。該入口及說明仍明列不涵蓋其他支撐、完整工具、碎塊轉向、黏附或施力，沒有宣稱完整拆除驗證。

## 增量與格式紀錄

`qa/revision-delta-review.json` 的 `pass:true` 明確限於整合完整性、固定輸入不變及既有修正路徑身分；其 `old_main_route_accepted:false`、製造有條件限制與未重新執行橋接／射線／實測的範圍保留。它沒有把自己的增量核對說成全量幾何或製造驗證。

`qa/revision-whitespace-check.json` 保留 **exit_code:2**、非空原診斷文字與「未藉改輸入／門檻隱藏」的欄位。說明只把空 INI 值行尾空白和封存證據 EOF 空行列為非阻擋格式問題，沒有重新分類成 passed；本分項亦沒有把該失敗當作通過。診斷中的非 ASCII 路徑文字已有編碼失真，但行號、空白類型、退出碼與相關實際檔案清楚，未影響製造判定；它不是新的幾何／切片成功證據。

## 可重現資料

機器結果：[evidence-audit-results.json](evidence-audit-results.json)。逐檔結果含來源／副本 SHA、替換次數、JSON 葉節點計數、NPZ CRC、73 檔 Git blob 綁定及明確範圍。核對腳本：[audit_evidence.py](audit_evidence.py)。工具暫時失敗紀錄：[attempt-log.json](attempt-log.json)。

在新審查輸出位置執行：

```text
python audit_evidence.py --source <old-independent-review> --package <new-building-package> --output <new-review-output>/evidence-audit-results.json
```

腳本僅讀取來源／候選／Git 物件，輸出至指定新審查檔案。沒有修改原候選或遠端，沒有 Library 下載或發布。其 GO 限於本分項；總判定應合併固定 STL、設定及實際 G-code、公開文案和封存身分的其他增量核對。
