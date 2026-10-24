# 國立臺北教育大學｜北師美術館

臺北校區，自行以Python實體布林建立的外觀近似模型。沒有下載第三方3D模型；不是測繪、施工圖或館內重建。

## 證據與範圍

三面實拍及屋頂俯視支持的整體量體近似。

保留臨路雙層高玻璃面與連續斜置垂直遮陽片、校內側磚牆及底層柱列、東側梯間凹槽、可辨識的轉角突出耳形框，以及屋頂低槽與高梯間／機房量體。遮陽片密度及厚度為可列印近似；「隔牆有耳」曲面改成厚化折線輪廓，不是原藝術品精確複刻。四周玻璃只作有底凹面，不假稱透明或重建室內。

官方文件日期2023年10月25日，實拍攝影日未載。博物館另有2017、2020實拍和館方供圖。資料更新日不視為拍攝日；這些來源不能保證2026全部現況。完整來源頁碼與URL見 [sources.json](sources.json)。原照片與PDF只留私人核對，不隨公開包散布。

## 交付檔

- [model.stl](model.stl)：毫米，含底座最長150毫米，每件獨立比例
- [scene.blend](scene.blend)：由交付STL匯入的可編修網格
- [build_model.py](build_model.py) 與 [requirements.txt](requirements.txt)：參數重建來源，執行 python build_model.py
- [render_preview.py](render_preview.py)：以Blender讀取實際STL渲染；執行 blender -b -t 2 -P render_preview.py

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 實際STL正面<br>![正面](previews/front.png) | 實際STL背面<br>![背面](previews/rear.png) |  |

[入口側](previews/side.png) · [正立面](previews/elevation.png) · [俯視](previews/top.png)

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 入口側<br>![入口側](previews/side.png) | 正立面<br>![正立面](previews/elevation.png) | 俯視<br>![俯視](previews/top.png) |

## 列印與檢查限制

底座朝下，勿直接把不同館的比例拼為同一校園。挑簷、入口框、百葉及柱廊可能需要支撐；粗化的片、柱、框仍有拆支撐損壞風險。沒有實體試印或Cura/Prusa工具路徑實測；不保證免支撐或保證可印。

[validation.json](validation.json) 驗證原STL法向／繞序、正體積、水密、每邊兩面、vertex link單環、單一連通表面、無分離內腔殼、最長尺寸，以及獨立重建SHA和Blend幾何一致。

[contour-validity-check.json](contour-validity-check.json) 使用固定z偏移0.071毫米，每0.2毫米檢驗原STL閉合degree2輪廓、個別及合成Polygon有效，不修補失效輪廓後算成功。

[thin-feature-check.json](thin-feature-check.json) 使用canonical fail-closed v3每1毫米抽樣0.8毫米opening輔助篩檢；這不是全面最小壁厚或切片器模擬。

驗證命令：python validate_model.py；python check_contour_validity.py；python check_thin_features.py。三者須exit0且所有檢查為真才可凍結；獨立審核通過前不可發布。

外觀已覆核，本件為作者凍結版本；須經獨立幾何審核通過後由唯一發布者發布。
