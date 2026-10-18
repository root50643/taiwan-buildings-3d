# 實測失敗與修正紀錄

> 歷史候選執行紀錄的公開衍生副本：私人路徑已遮罩；當時狀態、失敗、數值及原候選hash保留。當前GO與公開檔案SHA範圍見[公開版本說明](../PUBLICATION.md)。

各版 STL 保留於 attempt-01、attempt-02、attempt-03；原始旗標和 exit status 不覆寫。最終版為 models/v4。

1. 初次執行在 NumPy 2.5.4 的二維 `np.cross` 呼叫拋出 ValueError，尚未輸出 STL。以明示二維 determinant 取代，並更正凹窗法向方向。這是執行失敗，不列成網格通過或失敗。
2. attempt-01：SHA `686802e548693c1f6ce816283003148211a6e373c878d48481649aea28561421`。生成報告 non-watertight、trimesh split 7 components；原 checker 另按 edge connectivity 計 6 個 components。玻璃塔下層的窗槽切入和房間合併後的隱藏面，留下五個約 -55.044 mm³ 的內腔，另有退化面。判為必須修正，沒有以微小誤差放行。
3. attempt-02：SHA `50e6b73807fa467057a1e77f20d8e17db128f4d6785d306c30624745976220e5`。只在主屋頂以上確定外露塔面切窗，消除隱藏內腔；凹窗頂斜面頂點恰停在外牆平面仍產生微小三角形，binary32 匯出後四個面退化，non-watertight、3 components。將 45° cutter 斜面延伸到牆外，避免共面端點，沒有靠放寬檢查門檻修補。
4. attempt-03：SHA `39e9697db4e67fa94cdb71480b165bc0f87a2be5c28810059a9ce197ed60d637`。網格封閉、繞序一致、單連通，獨立重建位元組一致；嚴格 0.8 mm 寬度篩檢在 z=15.1–18.1 的 16 層找到真薄頸。原座標 z=16 切面定位二樓斜翼欄牆末端 [1482,550]→[1434,604] 與房間尖角相接，0.4 mm erosion 後兩核心間隙 0.807983 mm。精確原坐標資料保留於 attempt-03，判為須修正。
5. v4：以 2.4 mm 方形局部接塊把上述欄牆接入房間角點；露台仍開放。重新生成、獨立重建、幾何與風險檢查，並由交付 STL 重新產生全部預覽與場景。最終結果與仍保留的嚴格旗標見 QA-RESULTS.md。

attempt-01、attempt-02、attempt-03 的生成器各自保留原字節雜湊；這些歷史腳本的預設根目錄解析仍依原來源位置，欲重跑應在完整臨時模型根目錄配置同版 parameters.json 與 source/build_model.py，或依獨立重建方法用 importlib 呼叫 `build(params)`。原始主程序當時實際執行結果以 build-report.json 與 checker 證據為準。
