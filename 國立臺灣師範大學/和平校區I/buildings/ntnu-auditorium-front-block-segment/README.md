# 禮堂前棟入口段

國立臺灣師範大學 · 和平校區I · 校圖 H113  
這是依公開外觀照片自建的局部近似模型，**不是完整單棟、測繪模型或2026現況複製品**。未使用第三方3D mesh。

| 正面（實際 STL） | 背面／截斷面（實際 STL） |
|---|---|
| ![正面](previews/front.png) | ![背面](previews/rear.png) |

[俯視](previews/top.png) · [正立面](previews/elevation.png)

## 下載與重建

- [可列印網格 model.stl](model.stl)
- [可編輯 Blender 網格 scene.blend](scene.blend)
- [參數化來源 build_model.py](build_model.py) · [requirements.txt](requirements.txt)
- [STL 渲染腳本](render_preview.py)
- 含底座外框：**150 × 76 × 96 mm**；每件獨立比例，不是各館等比校園。STL 無內建單位，匯入請指定毫米。
- Python 3.12 安裝 requirements.txt 後執行 build_model.py；接著用 Blender 4.3.2+ 執行 render_preview.py。scene.blend 是實際交付 STL 匯入的可編輯網格，參數調整請改 Python 來源重建。

## 保留特徵

- 兩側方形衛塔與中央高三角山牆
- 三組雙聯半圓窗、共用桃形輪廓、頂部窄窗與圓形壁飾
- 真實挑空的三開間前門廊、深退後入口、四根粗化柱
- 衛塔下方長矩形飾板與側面拱形出入口（非正面多加門洞）

## 證據範圍與簡化

- 只取前棟門面與短側返，沒有製作長條講堂與音樂系館。
- 後面是模型的截斷面，不是禮堂現況背牆；沒有把舊圓龕與後來打通連接處擅自補成現況。
- 來源照片拍攝日期未標明；2022刊物與百年校慶頁面僅可確定出版時存在，不能宣稱2026現況測繪。
- 盾飾、花飾與窗框簡化／加粗，門廊橫梁等懸垂需要真切片評估支撐。

- 別名：臺北高等學校講堂、禮堂、Assembly Hall。
- [2026-09-23官方校圖](https://www.ga.ntnu.edu.tw/ntnu_map/)只核名稱、位置與棟界，不能用校圖符號當實拍外觀。
- 逐條來源、年代、支持特徵見 [sources.json](sources.json)。來源原照／PDF不隨此公開模型包重新散布。

## 列印與QA限制

- 底座朝下，建議先以 0.4 mm 噴嘴、0.2 mm 層高在自己的切片軟體預覽；這只是參考，不是已驗證設定。
- 入口、廊道與橫梁有挑空，請檢視懸垂與支撐可拆性；窗框、圓窗、女兒牆等細件需注意速度、材料、比例及脆弱處。
- 原STL硬檢：[validate_model.py](validate_model.py)／[validation.json](validation.json)，不使用 repair 修掉原始失敗證據。
- 0.2 mm逐層有效輪廓：[check_contour_validity.py](check_contour_validity.py)／[contour-validity-check.json](contour-validity-check.json)。固定起點 z=0.071 mm 避免共面退化，檢查 degree 2、單圈及組合多邊形有效，不吞 invalid。
- thin-v2：[check_thin_features.py](check_thin_features.py)／[thin-feature-check.json](thin-feature-check.json)，0.8 mm參考寬度形態 opening，採 canonical shared-edge interpolation，1 mm取樣間距。這不是全面最小壁厚量測。
- **數位幾何QA不是Cura／Prusa真切片、實際工具路徑或實體試印，不能宣稱保證可印或免支撐。**
- 檔案校驗：[SHA256SUMS](SHA256SUMS)。

研究截至 2026-10-13。這件只涵蓋已標示局部，學校其餘建物仍待續接。
