# 國立政治大學｜果夫樓

## 模型預覽


| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| ![主前坡與左翼內坡灰綠瓦代理](appearance/previews/front.png) |  |  |

## 兩個可見瓦坡限域配色（2026-10-22）

[五視角、來源與限制](appearance/README.md) · [彩色3MF](appearance/nccu-guofu-appearance.3mf) · [可編輯Blender](appearance/scene.blend)


僅主屋前庭坡10面、左翼內坡9面，共19完整三角面採歷史照片支持的低飽和灰綠瓦proxy。所有屋脊、簷、其他坡、牆窗、入口及底板中性；中性表示未確認，不代表實物灰色。官方記憶網正/側圖說2009，正面EXIF DateTime 2009-05-08，側面無日期EXIF；2025僅輔照，不稱跨年色值不變或2026現況。原1020面座標/面序/STL/歷史QA不變，不增套數。非分色封閉體或G-code，未實體試印；第三方照片不分發。


山下校區。本件為依公開實拍與官方平面外輪廓自建的完整建物外觀近似模型，不是測繪、BIM或結構工程資料。


俯視圖（歷史檔案留存，不作本頁預覽） · 正立面（歷史檔案留存，不作本頁預覽）


## 特徵與證據限制

完整C字形二層量體、兩翼及開口前庭、三段高窗中央入口、框狀門面、兩翼四坡屋頂與加厚簷口。

正面新照2025年；廣角照片2009年；防災表填表2021-10-01，照片拍攝日期未標。

背立面缺乏完整現況影像，以官方平面外輪廓保守留白；進深、高度、窗距皆視覺估算。原照片植栽遮挡處不增造细部。

第三方照片/PDF不隨包散布。完整網址、頁碼與各自支持的特徵見 [sources.json](sources.json)。不將來源網頁更新日視為攝影日。

## 3D列印檔案

- [model.stl](model.stl)：毫米，150.0 × 82.0 × 31.2 mm，含底座最長150 mm，各館獨立比例
- [scene.blend](scene.blend)：從交付STL匯入的可編輯網格；形狀與STL經比較一致
- [build_model.py](build_model.py)：獨立參數化重建來源；[requirements.txt](requirements.txt)
- [SHA256SUMS](SHA256SUMS)：逐檔校驗；STL SHA-256：be0b31f7f6546fccaf51c47a811cf4c8425e1c426e31bed020e71cb6d59fcf29

底座朝下列印。建議先以0.2 mm層高、0.4 mm噴嘴在自己的切片軟體檢視，確認簷口、雨遮、門楣與深凹窗的支撐需求。細窗框已加粗，仍須依材料、噴嘴及散熱調整。不要把數位QA解讀成免支撐保證。

## 可重現數位QA

1. Python執行 build_model.py 重建模型。
2. Blender背景執行 render_preview.py 生成實際STL正背、正立面、俯視與scene.blend。
3. Python依序執行 validate_model.py、check_contour_validity.py、check_thin_features.py；任何非零退出必須停止交付。

[validation.json](validation.json) 全部checks通過：原始STL法向、繞序、正體積、水密、每邊兩面、vertex link單環、單一連通表面、無分离内腔壳、重建SHA一致、Blend幾何一致與150mm限制。

[contour-validity-check.json](contour-validity-check.json)：以z=0.071mm起、0.2mm逐層，共156层，輪廓degree2闭合、单个與組合Polygon有效；不修補或吞掉invalid。

[thin-feature-check.json](thin-feature-check.json)：0.8mm參考寬度形態opening、1mm取样，最大損失比例0.16814%，超过1%層數0。此為輔助幾何篩檢，不是全面最小壁厚或工具路徑。

尚未做Cura/Prusa实际切片或實體試印，不宣稱保證可印。
