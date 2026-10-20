# QA 與限制

## 原始輸出
[qa-topology.json](qa-topology.json)：原始二進位 STL 逐面讀取，只按完全相等座標焊接以建立鄰接，沒有事後補洞、刪除退化面或修正法線。33,874 三角面；單一封閉連通表面，正體積。非有限值、零面積、重複面、非雙邊、方向錯誤及頂點 link 失敗皆 0。

[qa-layers.json](qa-layers.json)：每 0.2 mm 加頂緣下 0.001 mm，共 531 切片；多邊形有效、每個正面積分量皆通過向內 0.4 mm 侵蝕，沒有薄件豁免。

## 局部細節與支撐，不隱藏損失
[feature-validation.json](qa/feature-validation.json)：九跨各三高度共 27 條前屏風空氣線；九片各四高度共 36 個局部片厚探針；三條入口退縮空氣線。所有切片另作先內縮再外擴 0.4 mm 開運算。最差**單切片局部面積損失 0.2863%**，發生 z=47.0 mm；不是整體體積損失，也不是細節完全保留。逐切片數值與損失範圍已保存。

相鄰切片 +0.2 mm 緩衝外新增面積最大約 2734.9 mm²，在懸挑板起始 z=41 mm，明確提示直立方向的大幅懸空。這只是幾何診斷，不是切片器支撐或擠出路徑模擬。翼片底、橫肋、頂緣也可能需要支撐／重定向／拆件。未實印。

## 交換與編修
[exchange-validation.json](qa/exchange-validation.json)：3MF 與 STL 完整三角座標/順序一致；五材質全使用。以 lib3mf 嚴格讀取、實際單材質改色寫出重開，其他色彩及面指定不變。生成器重建 STL／3MF／mesh／palette SHA 應完全一致。

[scene-validation.json](qa/scene-validation.json)：Blender 幾何、面材質與單位對照，實際改色儲存重開；無外部圖片、內嵌腳本或連結庫。[render-manifest.json](qa/render-manifest.json) 記五視圖的鏡位與無裁切檢查。

生成器內有 0.0001 顯示 mm 的布林簡化以避免極小片段；最終 STL 仍接受未修補的原始拓撲檢驗。曲面採密集取樣、橫肋整合於葉片而非重疊薄殼。

[reproducibility.json](qa/reproducibility.json)：相同生成／渲染程式執行兩輪，五張 PNG SHA-256 逐一完全一致；不宣稱 Blender 檔二進位確定性。

來源與外觀獨立審查記錄見 [visual-review.md](qa/visual-review.md)。檢查不能補足未知實尺、穿孔、省略屋頂或展示背板的來源限制。
