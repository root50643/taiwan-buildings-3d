# QA紀錄

2026-10-14外觀核准：18寬板／交替深縫、中央細框及主要屋頂比例修正獲接受；以有界推定近似版封存，獨立數位審核已通過。原型作者已實看官方正面、歷史前側和z19航照。

原始STL、重建與Blend：見validation.json，所有checks必須true。
0.2mm逐層：見layer-component-check.json，每層原始Polygon先確認有效，再做erosion與opening；每件原Polygon均不能消失或分裂。另保留canonical v3 check_thin_features.py原檔及check_all_layers.py全層篩檢。

作者曾遇到端柱與端牆的窄頸在0.8mm erosion分裂，已將凹廊端界收至±46mm，讓端柱與端牆有實際重疊。沒有修補驗證資料、放寬閾值或吞小碎片。屋面共面交界亦改源幾何為實際重疊後重跑。

預覽由實際交付STL產生，check_preview_rebuild.py在隔離暫存資料夾重渲染六張PNG，逐檔SHA完全一致才通過。照片／PDF只在私人核對，不放本交付資料夾。PNG為渲染，非現場照片。

數位QA不取代實際切片或試印。外觀已核；封存後已由獨立審核者於副本重跑驗證，原凍結檔不變。

PNG重現僅移除Blender每次變動的Date/RenderTime文字metadata；PNG壓縮像素IDAT資料未改。逐檔SHA比較涵蓋實際像素資料。
