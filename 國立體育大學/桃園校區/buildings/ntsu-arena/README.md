# 國立體育大學｜綜合體育館

## 模型預覽


| 有限材料左前斜視 | 有限材料正立面 | 後側玻璃維持未知中性 |
| :---: | :---: | :---: |
| ![綜合體育館有限材料示意](appearance/previews/front.png) | ![綜合體育館正立面材料示意](appearance/previews/elevation.png) | ![後側玻璃維持中性](appearance/previews/rear.png) |

**範圍：既有外觀全形近似（後勤細節未核）。此為自建可列印外觀近似，不是测繪成果。**

## 原三角面的有限材料色系示意

[有限材料外觀、九視角與可編修檔](appearance/README.md)：原 **30,648 個三角面、面序、角點順序與 float32 座標完全保留**，只對 **23,862 面**指定主拱頂淡黃綠、水平屋頂唇邊暖白與前側幕牆灰藍材料家族，**6,786 面維持未知中性**。不是整棟配色完成、歷史精準原色、2017完整復原或2026現況，也不新增建物／幾何；未知中性不表示實物灰色。


下載[可編修 Blender](appearance/ntsu-arena-appearance.blend)、[逐面材質3MF](appearance/ntsu-arena-appearance.3mf)；[公開Python重建](appearance/source/rebuild.py)只需原公開STL、數值參數、色盤與程式，不需照片。來源照片攝影日期未定，活動標誌、PDF metadata及上傳路徑都不當精確拍攝日；色碼未校正。白色只到水平唇邊，不延伸至垂直環梁／簷底／V柱；後玻璃、環臺、凸橫帶與其餘面不推色。原STL、Blend、4張預覽、幾何QA與支撐限制全部保留，未新增實體或多色試印驗證。

## 原始幾何與既有無色預覽


## 幾何與來源界線
保留環形主體、48個V型支撐節奏、低拱屋頂、環狀平台、前側深入口。屋頂多圈細構造、設備與細密玻璃分格已簡化；單一八角凹線不表示完整屋頂設備重建。

來源有132m（租借平台／建築師）與122m（體育處簡介PDF）直徑差異；高度亦存在47.61／47.71m文字差異。本模型不採固定測繪縮尺，不由任一數字宣稱真實比例。

官方2023年9月校圖確認本校為桃園市龜山區文化一路250號的國立體育大學（NTSU），不是臺中的國立臺灣體育運動大學（NTUS）。來源照片攝影日期未載；PDF、頁面與上傳日期不能代替拍攝日期。2026工程文件是預定進度，不證明當日施工或完成狀態。後側未知的出入口與後勤附屬物均未補造。

## 檔案與重建
- [model.stl](model.stl)：毫米，底座朝下；最長含底座150 mm，各館独立近似比例。
- [scene.blend](scene.blend)：由交付STL匯入，可編修的網格；不是外觀照片的合成效果。
- [build_model.py](build_model.py)：參數化Python原始碼，自建形體，未下載第三方3D模型。
- [requirements.txt](requirements.txt)：重建環境套件版本；Blender 4.3.2用於渲染。
- [render_preview.py](render_preview.py)：由實際STL生成front、rear、elevation、top PNG與Blend。
- [sources.json](sources.json)：URL、可支持特徵與來源年代限制。第三方原照片、PDF不在公開包。

執行 Python build_model.py；再執行 blender -b -t 2 -P render_preview.py。

## 列印限制
V柱、平台懸挑、入口橫梁與屋簷視切片設定可能要支撐。外柱已加粗；屋頂八角線改為約2mm寬、0.5至0.8mm深的背襯凹線，避免獨立細圈。

支撐是否需要及放置位置須由切片軟體與印表機設定判斷。此模型有實體內芯以避免封閉內腔，並不模擬室內觀眾席或可進入建築空間。細部與玻璃以加粗浮雕／實體凹槽表達。建議先看實際工具路徑，再試印小範圍。**數位QA不等於Cura／Prusa工具路徑或實體試印，不保證免支撐或保證列印成功。**

## 可重跑QA
- [validate_model.py](validate_model.py) → [validation.json](validation.json)：原始STL法向／繞序、每邊兩面、vertex link單環、水密、正體積、單一表面殼、來源重建SHA與Blend/STL幾何一致。
- [check_contour_validity.py](check_contour_validity.py) → [contour-validity-check.json](contour-validity-check.json)：z=.071起，每0.2mm檢查閉合degree2及個別／組合Polygon valid，遇到invalid直接失敗，無repair fallback。
- [check_thin_features.py](check_thin_features.py) → [thin-feature-check.json](thin-feature-check.json)：canonical fail-closed v3，每1mm、0.8mm opening參考寬度篩檢。這不是全面最小壁厚或切片分析。
- [qa-summary.json](qa-summary.json)：逐程式退出碼与數位QA摘要。
- [SHA256SUMS.txt](SHA256SUMS.txt)：此件交付逐檔校驗。

- [check_depth_rays.py](check_depth_rays.py) → [depth-ray-check.json](depth-ray-check.json)：原始二進位STL射線，驗證入口深凹與V柱到後玻璃面距離；僅為模型幾何量測，非實建測量。
