# 國立金門大學｜楊清廉圖資大樓銃樓段

本件僅為圖資大樓的**銃樓局部外觀近似**，不是獨立建物、全館測繪或全校完成。以建築師實拍、校方簡報和2019年記者實拍交叉核對，自行以 Python / manifold3d 建立；沒有擷取第三方3D網格。

| 實際STL正面 | 未知背面留白 |
|---|---|
| ![正面](previews/front.png) | ![背面](previews/rear.png) |

[正立面](previews/elevation.png) · [頂視](previews/top.png) · [屋頂低視角](previews/roof-detail.png)

## 範圍與版本
- 核可外觀版本：v2 成對曲線山牆、橫向屋脊版。舊四坡錐頂未核可且不在此包。
- 保留主塔身三列單窄窗、最上雙窄窗，另一已見立面的三列單窄窗，外挑欄板正面2孔／側面3孔、環繞陽台凹槽、屋頂成對曲線山牆。
- 山牆曲線、相對比例、進深為照片近似；為列印加厚山牆板至3.0mm，脊頂保留約5.0mm寬平台、上翹端保留至少2.0mm端面，並非原建築測量尺寸。
- 未知背面、另一側窗組與接主館段留白，不推造。主館、階梯廣場、山牆主屋群、後翼與室內皆未製作；底座是人工列印底座。
- 不以館內圖書館、李奇茂美術館或電算中心另算建物。圖資大樓正式别名由2025年7月館方樓層導覽確認為楊清廉圖資大樓。
- 建築師記載2008年竣工；照片多未標攝影日期。已查校方現行頁面、2025簡報及修繕關鍵字，未取得能證明2026全棟外牆／屋頂改造完成的資料。未查獲不代表沒有施工。

## 檔案與重建
- [model.stl](model.stl)：毫米，70 × 70 × 150 mm，含底座
- [scene.blend](scene.blend)：由交付STL匯入的可編輯網格，非另造展示模型
- [build_model.py](build_model.py)：獨立參數重建；[requirements.txt](requirements.txt)
- [render_preview.py](render_preview.py)、[render_roof_detail.py](render_roof_detail.py)：由實際交付網格渲染
- [來源與限制](sources.json)、[QA說明](QA.md)、[SHA256](SHA256SUMS.txt)

安裝 requirements 後執行 python build_model.py；用 Blender 4.3+ 執行 blender -b -P render_preview.py，再執行 blender -b -P render_roof_detail.py。驗證可用 python run_checks.py。

## 列印提醒
底座朝下。外挑陽台、屋簷與屋頂山牆需在切片軟體檢視支撐，細孔、窄窗及壁角石條不宜再任意縮小。這裡的數位網格與0.2mm截面檢查，不是 Cura／PrusaSlicer 工具路徑驗證，也沒有實體試印；不保證免支撐或任何機種均可直接成功。

所有原照片、PDF及CAD參考只用於私下覆核，未隨公開包散布。
