# 降臨堂｜約2014主堂外觀近似版

[回淡水校區](../../README.md)

| 正面 | 背面 |
|---|---|
| ![正面](previews/front.png) | ![背面](previews/rear.png) |

## 範圍與可信度

依校方較新正面、2014南側施工背斜照片、NLSC正射屋簷外包絡自建。完整主堂量體包含低層退縮牆體、四向曲殼、方頸、十字架與2003改造後門廳近似。不是測繪、不是1973竣工復原，也不是全校完成。鄰近鐘塔及南側關懷中心不在本件範圍。

- 屋簷邊長以約29m建模，正射合理區間28–30m；這是屋頂投影，不能當牆基足跡。
- 牆高4.4m（推估3.6–5.2m）；屋頂升高10m（8.5–12.5m）；短方頸0.6m（0.3–1.1m）；十架2.6m（2–3.4m）。採用總高17.6m，推估包絡14.4–22.2m。沒有可驗證權威總高。
- 牆至簷口退縮取2.4m（1.5–3.5m）；角落凹入取3.9m（2.8–5.2m）。後牆與正門不對稱，但完整牆線仍為照片近似。
- 四曲面用連續方形截面上收形成；曲率指數2.55（候選2.1–3.1）只是外觀擬合，不援引數學論文冒充實測。
- 上部每面三窄窗以淺凹表達。細窗格、彩繪、管線、空調與內部省略。十架與柱加粗並根連接；實心外觀模型不表達實際混凝土殼厚。
- 早期026-1照片沒有明確年代；只有026-3團照明確為1973-02-17。這版不套用舊門廳。

來源、日期、假設邊界與省略項目見 [sources.json](sources.json)。第三方原圖不在本包。

## 檔案與使用

- [model.stl](model.stl)：毫米；含底座150 × 150 × 83.08mm。比例約1:219.8，底座厚3mm。
- [scene.blend](scene.blend)：由實際STL匯入的可編修網格；[build_model.py](build_model.py)是參數重建來源。
- [頂視](previews/top.png)、[西側](previews/west.png)、[東側](previews/east.png)、[正面低視角](previews/front-low.png)、[背面低視角](previews/rear-low.png)。全部PNG取自交付STL。
- [requirements.txt](requirements.txt)、[render_preview.py](render_preview.py)、[run_all_checks.py](run_all_checks.py)、[validation.json](validation.json)、[qa-summary.json](qa-summary.json)、[SHA256SUMS](SHA256SUMS)。

底座朝下。外簷與門廊有懸挑，須依實際切片評估支撐；細十架須留意搬運。0.2mm逐層幾何與0.8mm形態篩檢不是Cura/Prusa工具路徑，也未實體試印，不保證免支撐。切片前確認STL單位與方向。

## 重建與數位QA

Python安裝requirements後執行build_model.py，再以Blender執行render_preview.py，最後執行run_all_checks.py。檢查原始STL單一水密表面、每邊二面、vertex-link單環、法向與繞序、正體積、重建SHA、Blend幾何、重繪PNG及所有0.2mm截面。原Polygon逐一erosion/opening須零消失零分裂；invalid直接失敗，沒有repair fallback。完整數值見QA檔；面積損失不得替代逐構件連通檢查。416層、800個原Polygon均無消失或分裂；52整層與436個跨層原Polygon樣本opening損失超過1%，包含四角柱與十字架。此警告不是零，也不能全歸為四角；詳下方補充與 [細件說明](thin-feature-review.json)。

外觀已於2026-10-14核准，作者數位QA通過並凍結v1；獨立硬性幾何與9張PNG重現檢查通過；薄損具體例外已核准，本說明補充仍待最終文件核對，尚未發布。


## v1文件補充：局部薄損例外

這次只補文件與可重跑驗證器，原STL、Blend、參數源及9張PNG完全不變；原始凍結文件不覆寫。本節取代原先「全部高損僅十架／純圓角」的不完整說明。

- 52整層opening損失>1%；436個跨層原Polygon樣本>1%，包含四角柱與十字架，不是436個實體構件。
- 最差z=83.071mm，原面積2.53605625mm²，損失0.1475368442830866mm²，損失5.81756986987519%，保留94.18243013012481%。排除0.41mm頂點鄰域後仍損失0.004540467122641696mm²（0.17903653054389848%），非零，不能稱全是四角。
- 436個高損截面核為完整矩形；原STL局部X/Y法向caliper最小1.5925mm，角柱約2.093002×2.73mm。這是指定截面的局部量測，並非全方向或全域最小壁厚掃描。
- 十架3根向下射線全部連至底座；4柱各向下連底、向上連屋面。所有800原Polygon erosion/opening均零消失零分裂。基於這些限定證據接受本尺度的具體薄損例外，並非放寬一般驗收閾值。
- 浮點、截面量化、GEOS版本與buffer圓弧離散可能令末位數值微變。保留完整原值，不修復invalid，不吞小構件或更改閾值。
- 不得任意縮小；縮放後需全QA重跑。屋簷、門廊及十架仍須實際切片評估支撐，未實體試印，無工具路徑或免支撐保證。

證據：[逐構件完整數據](detailed-component-check.json)、[局部caliper與根射線](local-caliper-root-check.json)。在模型同目錄依序執行 [check_detailed_components.py](check_detailed_components.py) 及 [check_local_calipers_roots.py](check_local_calipers_roots.py) 可重現，均自包含相對路徑，不依賴其他學校資料。原hardQA仍依run_all_checks.py執行；本補充只解釋非零形態警告，不替代硬性檢查。
