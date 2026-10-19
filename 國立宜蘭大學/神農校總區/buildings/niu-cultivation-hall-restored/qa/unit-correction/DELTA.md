# Blender 單位修正增量

> 歷史 QA 紀錄：保留下列原判定與失敗，不改寫為通過。最新單位覆核與已取消的額外 Library 發布門檻見模型包 PUBLICATION.md；Library 仍未官方回驗。

原審提交為 `7d334d942bcb56b02e5c77c970e61591720a9296`。本次只修場景與生成腳本單位，強化驗證並整合獨立製造限制；沒有修改 STL／OBJ／G-code、來源形體或其他學校檔案。原整包 NO-GO 沒有被作者自行解除，仍待本增量覆核及官方 Library 身分寫回／下載回驗。

保存場景和 renderer 均明設 `METRIC`、`scale_length=0.001`、`MILLIMETERS`。直接保存前後的網格座標、面索引、物件 scale／matrix、座標尺寸、面材質索引相同；沒有縮放網格。Blender 保存可移除未使用 datablock，不宣稱整檔只改三個二進位欄位，檢查範圍見 saved-scene-unit-correction.json。

新驗證器讀取未修補的原始 STL，核對 evaluated 世界座標的 binary32 有向三角形，只允許循環頂點起點差異，沒有 rounding、反射或頂點合併。保存重開場景及隔離新生成場景皆通過毫米物理尺寸與全1,832三角形比對。原公尺場景負對照仍有相同幾何，但單位／真實尺寸檢查返回預期失敗 exit 1，見 original-scene-negative-check.json。

隔離執行原幾何生成器及更新 renderer：STL／OBJ bytes 完全相同；六視圖全部解碼 RGBA bytes 相同。新 PNG 的日期、File 和 render timing metadata 使封裝 bytes 不同，因此保留原交付 PNG，而不是冒稱 PNG 檔案逐位元相同。更新 render-manifest 並保存各圖兩份 SHA。沒有重跑未變更 STL 的完整碰撞、截面、切片或支撐演算法，其作者與獨立證據沿用且不刪除旗標。

獨立報告綁定、4.719216 mm 內填充封頂、入口 8.1 mm 淺凹橫框走線、5 條嚴格差異、304 條 1 mm 探入受阻與分段剪剝條件已整合至 PRINTING-LIMITS.md、qa/INDEPENDENT-REVIEW-INTEGRATION.md 和 qa/independent-review-summary.json。未試印，未實拆支撐。舊 Library 身分只對應舊包；新場景／文件未上傳，沒有重試或繞過官方 helper。
