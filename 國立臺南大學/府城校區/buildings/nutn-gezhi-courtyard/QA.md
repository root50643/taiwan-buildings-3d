# QA範圍
- validate_model.py：獨立讀回STL與3MF，檢查封閉、單連通、正體積、有限頂點、非退化三角形、每邊二面以及頂點/面/材質/毫米單位一致。
- verify_scene.py：實際重開BLEND，逐頂點/面比對，單個可見統一網格、隱藏可編輯件、無外連圖片、無內嵌程式文字。
- 真實Cycles渲染六視角；主視圖yaw36.87°、elevation23.43°，其餘視圖另列render-manifest.json；不把未渲染圖片當已檢查。
- 獨立視覺比對結果見visual-review.json；幾何QA不等於照片相似度或可印認證。
- 估計、未知背立面、年代與未試印限制見README與parameters-evidence.json。
