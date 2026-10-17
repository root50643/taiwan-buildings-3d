# 狀態

發布副本更新：2026-10-17 10:25 UTC。

v15為已完成有限獨立驗收的發布版本。47,770個原三角形，219×107×119毫米，STL SHA256：46649566e965a049e6e333e9d82b075407c8e926e55c9034f11fbe3dbdf15a5d。

- v0／v1四面宏觀來源條件審核已完成。
- D七帶／高低玻璃／上盒與C十帶／上白體小窗已經來源端逐圖核對。
- v14完成巨框內既有B端退縮面的玻璃材質修正；v15只調小天井相機，STL與v12／v13／v14逐byte相同。
- v14小天井視角因過近綠面被HOLD；v15修相機後完整九圖已重新出圖、逐檔凍結。
- v15已取得SOURCE-APPEARANCE-GO：九張原創圖逐張檢視，scene與原STL的47,770個三角形逐序同一。此項不代表製造通過。
- 作者全量normal／-O已完成：各1,785截層、22,364原多邊形通過；477,700原射線零短線；851,184候選原面對精確檢查無不合法相交。各26個數值flags仍在，因此原strict=false及實際exit1保留。
- 全部26條同次actual-hex射線在兩模式均完成精確分類、實際exit0；作者r2有界補證與兩模式比較通過，原generic strict=false仍保留。
- 原碼重建STL逐byte、完整scene-state與saved Blend檢查通過；24場景控制全過。作者未重做九圖replay；唯一完整CPU64九圖重現已由獨立QA執行，逐圖及saved Blend原面身份綁定見[完整QA](qa/README.md)。
- 獨立normal／-O原網格全量、同run actual-hex精確分類和完整scene／九圖重現已完成，結論僅為bounded GO，原generic strict=false及各26個flags／實際exit1均保留。
- 未實體試印。這份狀態檔描述受驗版本；實際發布由包含本檔的repository commit建立，本文不是remote上傳收據。

先前失敗與修訂證據保留在qa/BUILD-DIAGNOSTICS.md及分版報告；不得將前版局部診斷冒稱本版全量通過。

## 發布副本註記

此README／STATUS更新只發生在發布副本，作者3690項科學freeze及來源原件未修改。完整原資料、失敗flags、actual-hex補證、工具與控制皆按精確allowlist保留；摘要不能取代原證據。製造、支撐移除及尺度限制見[PRINTING-LIMITS.md](PRINTING-LIMITS.md)。

一份舊版WORK-STATE進度metadata（3,814 bytes，SHA256 6e3f0b0e1e31a2e0385ecf3b66bad84158d4d1afaa0a231e60096740f8f17faf）原bytes不可還原；此項非科學資料或必需依賴，all_historical_retained=false如實保留。參見[精確缺口註記](qa/independent/publication-chain/metadata-gap-acknowledgment-result.json)。
