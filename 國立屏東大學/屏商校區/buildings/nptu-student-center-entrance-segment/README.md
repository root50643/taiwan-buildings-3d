# 國立屏東大學｜屏商校區｜學生活動中心入口段

這是依公開完成照片自建的局部外觀模型，非全館測繪、全校模型或精確比例復原。所屬實體建物：**活動中心**。

| 實際 STL 正面 | 實際 STL 背面 |
|---|---|
| ![正面](previews/front.png) | ![背面](previews/rear.png) |

![實際STL頂視](previews/top.png)

## 外觀範圍

- 連續折面遮陽板的深淺變化與上層框架
- 入口深凹柱廊及寬階梯
- 立面背後玻璃帶與側邊低層通風口

## 未知與簡化

- 本件是入口立面與後方短量體的研究段，不是整座活動中心
- 屋頂後方禮堂的造型、實際進深與背立面未有足夠資料，背部是簡化截段面
- 模型屋頂為截段所需的平蓋，不代表全館真實屋頂形式
- 不以校圖活動中心示意圖推定真實屋頂；照片攝影日期未標

## 下載與重建

- [可列印 STL](model.stl)，單位為**毫米**；含底座 150.00 × 105.00 × 53.00 mm，最長150mm。各件獨立估算比例，不可直接拼成等比例全校。
- [可編輯 Blender 場景](scene.blend)：由交付STL匯入的一個網格，不是完整建築CAD/BIM；參數建模來源為 [build_model.py](build_model.py)。
- [套件版本](requirements.txt)、[渲染腳本](render_preview.py)、[來源與限制](sources.json)、[檔案SHA](SHA256SUMS.txt)。
- Python 3.12：pip install -r requirements.txt，接著 python build_model.py。
- Blender 4.3.2：blender -b -t 2 -P render_preview.py。圖像皆從實際交付STL渲染，沒有示意mesh替代。

## 列印與驗證

底座朝下放置。上層突出立面與柱廊需檢查支撐；折面遮陽片以2.0mm厚自建並連接主體。 使用0.4mm噴嘴、0.2mm層高只能作初始評估，仍要自行預覽工具路徑與支撐；數位驗證不等於Cura/Prusa實際切片或實體試印，沒有保證可印、強度或免支撐。

- [原始STL、獨立重建、Blend幾何驗證](validation.json)：全部checks為true；水密、每邊兩面、vertex link單一環、單一連通表面、原檔法向／繞序、正體積、底面與150mm尺寸均通過。
- [0.2mm逐層輪廓](contour-validity-check.json)：265層，起始z=0.071mm，degree2閉合、個別及合成Polygon valid均通過；invalid即失敗，不作repair。
- [canonical v3 0.8mm參考薄特徵篩檢](thin-feature-check.json)及[嚴格摘要](strict-thin-check.json)：1mm取樣，最大opening損失比例 0.0547%，每層均小於1%。這只是XY形態篩檢，非全面最小壁厚。
- [原檔驗證程式](validate_model.py)、[輪廓驗證程式](check_contour_validity.py)、[canonical v3](check_thin_features.py)、[strict執行程式](check_thin_strict.py)。依序執行python validate_model.py、python check_contour_validity.py、python check_thin_strict.py，任一非零退出都不能判通過。
- canonical v3 SHA256：059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915。
- 原始與獨立重建STL SHA256：76196ab0f25795798da178fef416d2bc39d3dd968e7e33f4032a1b263c258673。

資料查核：2026-10-13。官方原照片版權屬各權利人，本包不重新散布。
