# 作者原網格 QA 實跑結果

結論：**normal 與 Python -O 兩模式均完整 strict pass，兩模式的科學證據逐項一致。** 這是有限幾何檢查結果，不代表已試印或免支撐。最終獨立複核另見同包 [QA 總說明](README.md)。

STL SHA-256：`f93ed0ab95e13707d390f480174f63e31086b48041fc7a7a873975cad8892a8c`

## 本件實際數值

- 原始三角形 24,112；精確座標頂點 12,058、邊 36,168；單一外表面，無內殼。
- 原始範圍 210.0 × 152.0 × 63.799999237 mm；原面有向體積 1077054.820459 mm³。
- 原法線、面向、二面邊及頂點連結檢查全過，沒有修補、焊接、重網格、四捨五入、刪面或小面排除。
- 精確閉 AABB 候選共 297,696 對，全部完成。包含鄰面及共面；不允許相交 0 對。181,078 筆真交集皆為允許的原共享邊／共享頂點，完整精確事件另有 gzip JSONL。
- 每模式 241,120 條原面法線射線，固定每面十個原重心權重；低於 0.8 mm 的弦 0 條，數值旗標 0 條，最短首段實心弦 **0.901097603 mm**。
- CSV 保留全部原 hit／event／interval／控制欄及原 run 十六進位點、法線、原點、方向。每模式重驗 241,120 列、2,893,440 個無損描述值，從完整 CSV 重算全部旗標索引／原因，沒有只核對已列旗標的缺口。
- 0.2 mm 層距，三個 offset 0.031／0.071／0.137 mm，共 957 層、957 個原 Polygon，逐 Polygon 檢查。失敗 0；最大 opening 面積損失 **0.085328%**，低於 1%。沒有平均化掩蓋小島或窄根。
- 每個完整模式均 fresh 跑 12 個通用 fixture／30 次 gate 子執行，以及 2,736 個精確幾何 predicate、36 個 AABB 暴力對照及 48 個相交子程序控制。正例須通過，反例須因預期原因拒絕。
- 聚合要求恰好四個具名階段、整數零 exit、完整 flags、目前輸入及工具雜湊。一般模式與 -O 皆重新實跑，不沿用初步診斷。

## 原始證據

- [完整 fail-closed 摘要](final-v6/full-qa-summary.json)
- [normal 拓樸](final-v6/normal/standard/raw/raw-mesh-check.json)、[切層](final-v6/normal/standard/sections/section-check.json)、[射線](final-v6/normal/standard/dense/dense-check.json)、[精確相交](final-v6/normal/intersections.json)、[完整 CSV 稽核](final-v6/normal/dense-evidence.json)
- [optimized 射線](final-v6/optimized/standard/dense/dense-check.json)、[精確相交](final-v6/optimized/intersections.json)、[完整 CSV 稽核](final-v6/optimized/dense-evidence.json)

兩模式的完整 CSV、短弦／旗標空清單、逐層／逐 Polygon 詳細紀錄、精確交集事件均保留原 byte。run 內 synthetic controls 收入可驗證 archive；公開省略項逐項列 hash，不修改原科學 JSON／CSV。工具本身另有 normal／-O 完整正負控制；公開重播與 archive 還原方式見 QA 總說明。

## 限制與歷輪

最終版沒有數值退化旗標，因此不需要對本件作精確射線補充分類。先前 v2–v5 的真薄處／小島失敗均留在私人工作證據中，透過原幾何製造修形解決，沒有移動樣本、換理想射線或加豁免。v6 診斷曾通過，但以上數字來自重新執行的正式完整兩模式。

有限的原法線取樣與三組切層不能證明全方向最小厚度、材料強度、實際噴嘴路徑或免支撐。精確相交只證明所述原三角形對條件。建築比例亦為來源約束估計。未實際試印，請先逐層切片檢查支撐；縮放、空心化或任何幾何修改需重新驗證。
