> 本文保留 e45f8d6 原候選的結果。R2 最新修訂及風險請讀 [RISK-FOLLOWUP.md](risk-followup-e45f8d6/RISK-FOLLOWUP.md)；文中舊 layer-check 對應 `risk-followup-e45f8d6/input-layer-check.json`，根目錄檔案已更新為 R2。

# 固定候選覆核入口

本次只修訂既有 `nthu-macronix-building` 前棟屋面、退縮頂層與露台。後棟 6F 的深 L／內凹弧已核實，但跨層與現有座標對應仍列為缺口；本版不改後棟。套件身分、根索引與公開計數均未變。

請先讀 `../README.zh-TW.md`、`CANDIDATE-SOURCE-CHECK.md`、`EXTENDED-QA.md`、`geometry-delta.md`。來源 URL、像素雜湊與年代限制在 `../sources.json`，沒有附第三方原照片或平面圖。

幾何：150 × 124 × 68 mm；STL SHA-256 `9c90c8b6b6f99076f2096783e78b793404fb81df88ee270d2eb02f21290e24b8`。可重建性、場景幾何、原始 STL 拓樸檢查通過。自交浮點初報 false 原樣保留，另立精確補證；薄特徵與支撐警示仍是未解風險。高側窗帶比來源窄；新增端部有 0.00625 mm 薄弦樣本。不得把本件當作完成切片或試印。

本候選沒有推送。提交身分及外部封存 SHA 在工作目錄交付記錄中固定，避免把提交自己的雜湊寫入自身檔案形成循環。原版完整套件另保存在自足備份的 `original-08604e7/`，可直接比對與重建。

請獨立覆核來源大形狀、端部薄尖、支撐與截面；本次協作來源／幾何檢查不是發布核准。
