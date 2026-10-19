# 發布 metadata 與歷史 QA 綁定

固定驗收輸入為 `347ab012d32f6fd7252cd5073e7966e79b12e2f0`。它保留在本機；公開提交採清理後的新版本，不把含舊本機路徑的候選歷史帶入 GitHub。

本次沒有重新建模、切片或重跑未變更的碰撞／全量薄截面計算。十個 STL（九列印件及整體參考）、十九份歷史與最終 G-code 都與驗收輸入逐位元相同。二十五張 PNG 的解碼 RGBA 像素完全相同；主預覽只清理非必要 metadata，沒有重渲染。場景只清理明確的路徑字元欄位及其 NUL 後尾端；幾何、全部材質（含原孤立材質）、相機、燈、毫米單位與數值快照完全不變。細節見 [asset map](publication-asset-metadata-map.json)。

五十四份 QA JSON／log 只將私人執行路徑換成中性標記；原數值、布林判定、順序、失敗旗標與二百九十一個歷史 SHA 值保持。細節見 [text map](publication-text-privacy-map.json) 及 [verification](publication-text-privacy-verification.json)。原報告內的 SHA 仍屬原候選／當次歷史資產，不會因發布清理而偽裝成重新執行的結果。

[current-binding.json](current-binding.json) 將原候選 SHA 對應到目前檔案；原驗收 manifests 另保留於 [accepted-candidate](history/accepted-candidate/)。目前套件檔案清單以 [PACKAGE-SHA256.json](../PACKAGE-SHA256.json) 為準，[SHA256SUMS](../SHA256SUMS) 是目前十個 STL 與場景的 SHA。

原 opening residual 26／1／892／0、完整 1.6×1.6 mm 柱 proxy FAIL、淺窗唇懸伸、未試印／拆支撐／試合等限制都保留。核心補證沒有抹去旗標，也沒有證明連續全域最小三維厚度。Library 未上傳、未官方回下載、未驗證；使用者已取消額外備份作本次發布門檻，這不構成備份成功聲明。本次沒有呼叫 Library helper、相容 wrapper 或替代流程。
