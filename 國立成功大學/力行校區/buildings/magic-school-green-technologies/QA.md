# QA範圍與保留告警

## 原始拓撲與切片

`qa-topology.json`直接讀二進位STL：81,412三角、39,040精確焊點、單連通閉殼，非有限、零面積、重面、非雙邊、方向錯與頂點link錯均0。不補洞、不修法線、不刪退化面、不對切線四捨五入來藏錯。

`qa-layers.json`：0.2mm間距及最高點下0.001mm，共715層；輪廓有效。保留576層／4620個0.8mm侵蝕薄島告警。這是每個正連通區的檢測，**不是全部壁厚通過**。未給細件豁免。

`qa/feature-validation.json`按交付STL做空/實點、穿透射線、局部剖面和實際射線厚度。中庭入口、PV/廳頂之間留空、82陽台凹深與外階空隙，必須與外觀來源一起核，不以可列印性替代建築真形。

## 格式與重建

`qa/exchange-validation.json`：lib3mf strict讀取、warnings0、實改單材質色彩與alpha後存檔再讀；其餘色/alpha/逐面指派不變。STL/3MF座標和面序相同，未細分或重造幾何。

`qa/scene-validation.json`：Blend實開比對頂點、面序、材質、單位；實際修改單頂點與單材質色/alpha，存檔重開確認變更及未改部分。`qa/render-reopen-validation.json`重開交付場景再渲染front，PNG bytes相同。

`qa/isolated-rebuild.json`只在完成後產生：乾淨隔離目錄、4執行緒Blender、4核心資料檔和5張PNG共9檔bytes一致。`qa/independent-model-review.json`為獨立源形審核；缺報告或hash不匹配不能視為完成。後續改幾何必重跑相關QA/渲染/重綁獨審。

## 製造限制

細格約0.275mm、風機葉片0.55mm、欄杆0.65mm；需依印表機/材料放大、支撐或拆件。PV與背架、雨水與維修外階、曲船陽臺、折紙棚、廊簷有懸伸，不宣稱免支撐。無實體FFF/SLA試印、無工程受力驗證。玻璃採不透明深色展示代理，不宣稱可透光印製。

所有私有來源照片/PDF不入公開包，只有來源URL、原創幾何/程式和自製渲染。ZIP/checksum在獨審後封定；2026-10-23 獲准以既有身份整棟替代發布，現行發布狀態以儲存庫 commit 歷史為準。
