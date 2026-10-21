# 檢查及限制

## 原始 STL 拓樸
原始二進位 STL 僅完全相等座標焊接記帳，不修法線、不補洞、不移除小面：110848 面，54298 點，連通殼 1；退化面 0、重複面 0、異常邊 0、頂點鏈失敗 0。尺寸 244.00 × 196.00 × 97.73 mm。生成階段布林、幾何簡化及 float32 構造回讀去除量化零長邊是建模流程，原始輸出 QA 不修補。

## 薄截面、局部、懸垂：保留失敗
0.2 mm 全域層距加最高點下0.001 mm，共 489 層；119 層未通過 0.8 mm 截面侵蝕篩檢；輪廓有效性 True。沒有尖端豁免。8 個局部區域、29 平面，5 平面有薄截面失敗。空開口的空截面不當厚度通過。詳見 qa-layers.json 與 qa/local-features.json。

z>3.01 mm，向下超45°面 12534，面積 16007.93 mm²。只是表面啟發式，不是支撐／切片模擬。0.9 mm 膜、細竹帶、椅面和彎肋可能需支撐或加厚。**未實際列印、試裝、載重；不保證免支撐或直接可印。**

## 可重現驗證
最終驗證紀錄在 qa/：lib3mf 嚴格讀取、單材質修改保存重開；Blender 同網格／材質讀回及修改保存重開；前視重新渲染；獨立目錄由程式重建模型與五張圖。執行 Blender 使用 --python-exit-code 1；每圖雜湊必須與 manifest 一致，避免舊圖混入。此環境 Blender 不支援 OpenImageDenoise，使用固定種子 CPU Cycles、64 samples、無降噪；影像雜訊不是幾何缺陷。

STL 與3MF各三角形一致。顏色以原始布林表面候選48面的最近點距離轉移到簡化網格，微小交界色面為近似；Blender 的膜半透明 shader 不是實物材料量測。藍色展示底板不代表現地鋼基梁。來源審查只涵蓋觀察近似，不是工程認證。

重跑：requirements.txt、Blender4.3.2；build_model.py → qa_model.py／check_features.py → render_model.py／verify_scene.py／verify_render.py → verify_exchange.py。qa/ 的結果須對應本次 STL 雜湊，不得沿用舊結果。
