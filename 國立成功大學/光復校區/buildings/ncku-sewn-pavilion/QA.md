# 懸鏈・榭 / Sewn Pavilion — QA

國立成功大學／光復校區／`ncku-sewn-pavilion`。本報告針對交付幾何與檔案，不是原建築結構認證或實印證書。

## 最終幾何與 raw 拓樸
- STL SHA-256：`8ddba32557e65004cd579fdf31f37f6912ed7248a9b99c53be96900c48cc899d`。
- 40,911個exact-weld頂點、82,794個三角面；外包尺寸 156.89980 × 156.96003 × 90.21072 mm；正體積 29627.97181 mm³。
- 直接讀binary STL，僅按完全相同座標合併頂點以計算關聯；**沒有fill holes、刪除退化面、修補法向、容差合點或以修復結果冒充raw**。
- 非有限值、零面積、重複面、edge incidence≠2、同向共邊、非單環vertex link、檔存法向不正向：全部0。單一連通閉殼、繞向一致。
- 生成端對實體作布林與0.02mm簡化，再float32量化並重新檢查；STL／3MF／Blend共用量化後幾何。這是生成流程，不是QA修補。逐面材質由簡化前表面轉移，實測轉移偏差另記在設計manifest。
- 完整數字：[qa-topology.json](qa-topology.json)、[design-features](qa/design-features.json)。

## 全局切層：警告不豁免
按未四捨五入的0.2mm倍數與頂部−0.001mm取樣，共452層。全部輪廓有效；採even–odd巢狀重建，包含孔內島，逐個正面積連通成分作−0.4mm侵蝕。**不是所有成分通過0.8mm門檻**：34個警告層／61個失敗成分保留在[qa-layers.json](qa-layers.json)。曲面尖端、近腳邊緣、孔邊與分片切面都不免檢。

## 局部有限空間與真厚度
[local-features.json](qa/local-features.json)直接讀最終raw STL；保留每項範圍、切片與法向／座標證據。
- 90個實體、69個空氣樣本：occupancy不符0，有限air-volume不符0。
- 三個共腳、18道曲帶、三向框片、中央三角孔、開放拱下與18條預選有限穿孔空柱皆納入檢查；234個穿孔法向ray遮蔽／不合法0，全部18索引曲帶都有已驗證通孔。
- 27個從外部起始的真mesh法向ray：曲帶18點 0.94354–0.95856 mm；中央框9點 0.93199–0.95600 mm；不足0.8mm共0。
- 中央框的近法向0.95mm是**列印用途強化，不是實測原板厚**；變動垂直厚度、近腳上限約7.92mm及底部z≥0裁切保留三向連接與小孔。取樣厚度不是全域最小厚度證明。
- 含厚度方向的有限局部切片仍保留 **10個薄樣本／10個薄成分**；主片通過不代表同一裁片內的第二成分通過，不能因其小或近腳而豁免。
- base以上向下超45°共 **11885個面／8026.65505 mm²**。這是懸挑診斷，不是自動支撐方案。

**未實際列印，不保證免支撐。** 曲帶、孔邊與薄接縫仍易折損；拱下、外伸翼與中央框須規劃支撐與拆支撐。有限取樣不等於全表面厚度、橋跨、耐久、強度或特定切片機測試。

## 交換、編輯與再開啟
- 3MF以lib3mf strict讀入0警告、合法且有向manifold；原三角座標／次序與STL逐項相同，4個具名不透明材質逐面分派。
- 修改單一材質RGB與alpha後save/reopen：其他材質與面分派不變，lib3mf六位小數writer往返座標最大差 0.0000076294 mm；往返仍有向閉殼。[exchange-validation](qa/exchange-validation.json)
- Blender重開：幾何逐三角相同、identity transform、4材質名／色／alpha一致；單頂點+0.25mm及單材質修改save/reopen，未改頂點和其他材質保留。無外部資產或內嵌script。[scene-validation](qa/scene-validation.json)
- **STL無顏色與透明資訊**；3MF／Blend可編輯不代表建築工程模型。

## 最終mesh渲染與獨立重建
五張1200×1200 PNG從最終3MF同一mesh以CPU Cycles、seed 0實渲；無替代示意幾何。保存Blend重開前視角重渲逐byte一致；所有Blender程式以`--python-exit-code 1`執行。只移除PNG文字／日期metadata，不改像素。[render-manifest](qa/render-manifest.json)、[render-reopen-validation](qa/render-reopen-validation.json)

交付`rebuild.py`在新隔離目錄重新生成；**model.stl、model.3mf、mesh.json、palette.json共4核心＋5PNG全部byte一致**。報告綁交付生成／渲染script SHA。[isolated-rebuild](qa/isolated-rebuild.json) 不要求Blend二進位位元一致，另以實際幾何、材質、編輯往返與確定性重渲驗證。

## 來源與身分範圍
[來源終審](qa/source-visual-review.json)綁最終STL及5圖SHA／bytes，審核者親看構築圖與日／夜成品及官方院落證據。這是來源支持的外觀近似，不是逐孔、逐片折曲或精密尺度復原。來源日期、場址交叉推論、成組微孔省略、上緣錯層簡化、原作框片未知細節及歷史存續界線見[SOURCES](SOURCES.md)。

八件主文／生成器／manifest的正確模型名稱，加全包文字的舊專案名稱排除與校名／校區／slug一致，由[identity-validation](qa/identity-validation.json)驗證；`verify_package.py`再查各報告對應交付bytes。`SHA256SUMS`列除自身外全部檔案；原圖、原PDF、HTML、裁圖和Python快取不交付。
