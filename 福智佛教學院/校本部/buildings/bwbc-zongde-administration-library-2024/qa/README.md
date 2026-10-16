# 宗德樓 v17：獨立幾何與重現 QA

在下列有限檢查範圍內，獨立驗證已完成。**原數值射線閘門仍為 `strict_passed=false`，12 個旗標全部保留；每條另外完成原始實算射線的精確有理數判定。** 這不是全方向壁厚、力學強度、切片支撐或實體試印保證。

## 凍結模型

- STL SHA-256：`96481addb2b9ac4144cb5f012f19b57e047106021e93adb5c34df2c00770e1a3`
- 外廓：210 × 187.5 × 54.625 mm；原始三角形 37,330 張。
- 原始資料直接檢查，未焊點、修法線、刪小面、修輪廓或移動射線避開旗標。

## 實際結果

| 項目 | 結果 |
|---|---|
| 原 STL 拓樸與法線 | 封閉、有向一致、頂點連結合法、單一表面；無重複面或退化面 |
| 精確原三角形交集 | 620,769 個閉 AABB 候選全部判定；0 個違規接觸、交叉或共面面積重疊，包含相鄰面 |
| XY 切層窄根檢查 | 819 層、29,220 個原 Polygon 全部通過；0.2 mm 層距、3 個固定偏移；0.4 mm 半徑侵蝕/開運算不消失、不分裂；最大單 Polygon 面積損失約 0.540317%，低於 1% |
| 全原面數值射線 | 每面 10 點，共 373,300 條；0 條小於 0.8 mm，數值最小第一弦長 1.0 mm；保留 12 個旗標 |
| 12 個原始旗標的精確補充 | 12/12 原 run 十六進位描述子回綁完整 CSV，全部事件及區間完成精確分類；第一保守實體弦長均 ≥ 0.8 mm，最小約 1.299999237 mm |
| normal / Python `-O` | 全套幾何與控制各自執行；完整數值 CSV、旗標、切層明細、精確射線明細逐 bytes 一致 |
| 源碼重建 | STL 及色塊資料逐 bytes 一致；源碼場景與已存 Blend 選定完整狀態零差異，11 組相機定義一致 |
| 已存 Blend | evaluated 世界座標有向三角形多重集合與原 STL 完全一致；每個相機姿態重新核對；無外部照片/材質影像、替身網格或修飾器 |
| 11 張實際重渲 | 全部 RGBA bytes、尺寸/模式及保留 metadata 一致；下述純 metadata 清理後，11 張整 PNG 檔案亦逐 bytes 一致 |

12 條旗標不是同一種情形：9 條含共面邊界區間、1 條孤立相切、2 條為普通面內穿越。詳見 `results/FLAGGED_RAY_EXPLANATIONS.md`；原旗標、全部數值交點、精確接觸及 parity 證據均保留。

## PNG 重現與隱私

原 raw PNG 檔案因工作路徑及時間文字而**不具整檔位元一致性**。公開版僅移除 tEXt 白名單：`File`、`Date`、`Time`、`RenderTime`、`cycles.ViewLayer.total_time`、`cycles.ViewLayer.render_time`、`cycles.ViewLayer.synchronization_time`。

清理不重壓 IDAT、不重編像素、不改色彩；每個保留 chunk（含 CRC）逐 bytes 不變。原圖與重渲圖採相同流程。尺寸、RGBA（包括透明像素下的 RGB）、ICC/gamma/其他保留 metadata 均驗證；未知保留 ancillary chunk 也不默認忽略。完整原圖 hash、移除欄名及 payload hash、公開圖 hash 見 `preview-binding/` 與 `results/blend-rerender-audit.json`。原照片/PDF、未清理 PNG 及歷史失敗/中斷資料不在公開包。

## 證據與控制

為便於閱讀與分發，完整 2,348 份控制檔案封入 `controls.tar.xz`，未刪除任何最終反例或觀測結果。模型科學 CSV/JSON 仍直接列出，normal/`-O` 各自保留。控制索引逐成員綁 SHA；安全解包與重現入口見 `CONTROLS.md`。另附封裝工具本身的完整負控制 archive。下列控制目錄為解包後的邏輯路徑。

- `QA-RESULT.json`：從完整私人 postflight 衍生的公開結果摘要；原數值 strict=false 明確保留。
- `resume-v17/geometry/{normal,optimized}/`：兩模式完整科學報告、無損壓縮 CSV、全部旗標/相交詳證；其中合成控制子目錄另存於 archive。
- `results/`：源碼場景、Blend 重渲、逐射線解讀、分段恢復來源。
- `final-controls-v17/`：當前工具版本的 21 個包裝/例外/舊報告/缺旗標/壓縮雙 hash 控制、373 個精確幾何控制、120 條原 hex 相容控制、242 個 PNG 比較控制，均在 normal/`-O` 執行。
- `predicate-review/`：43 個 wrapper fixture 加 2 個 exit 控制/模式、18 個 PNG sanitizer 控制/模式、修正後核心及 postflight helper 控制，連同完整合成輸入和逐例結果。PNG 242 案公開報告重新產生，僅以模組 basename 識別；逐案科學結果與原審查完全相同。
- 負控制中預期的 `passed=false` 是成功拒絕證據，不能刪除。其中 6 份故意損壞/晚期變更的 gzip/XZ fixture 本就應拒絕解碼；模型本身的 CSV/詳證不使用這些例外。歷史未成功的開發嘗試另留私人。
- `PUBLICATION-BINDING.json`：原完整邏輯樹的逐檔原→公開相對路徑及 SHA，保持原 bytes；控制路徑依 `CONTROLS.md` 從 archive 解包。科學 JSON/CSV 原 bytes 不變。重複而無必要的 stdout/log 不在公開白名單，原 hash 及私人原件仍保留。
- `FILES-SHA256.json`：本目錄全部交付檔案完整性；本 manifest 本身的 hash 由外層交付 manifest 綁定。

第一次執行在 dense 階段遇到傳輸中斷。已完成的 normal raw/sections 依原 hash 明確引用，後續在全新目錄執行，並監控舊殘留輸出未變。沒有把中斷 run 宣稱完整通過；詳見 `EXECUTION-METHOD.json`。所有 68 份凍結作者輸入與工具在完成後重新核對未變。

重現指令與壓縮解碼方式見 `REPRODUCE.md`。
