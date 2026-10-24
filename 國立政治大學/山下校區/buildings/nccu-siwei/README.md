# 國立政治大學｜四維堂（修復前外觀近似）

山下校區。本件為依公開實拍與官方平面外輪廓自建的完整建物外觀近似模型，不是測繪、BIM或結構工程資料。

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 正面（實際 STL）<br>![正面](previews/front.png) | 背面（實際 STL）<br>![背面](previews/rear.png) |  |

[俯視圖](previews/top.png) · [正立面](previews/elevation.png)

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 俯視圖<br>![俯視圖](previews/top.png) | 正立面<br>![正立面](previews/elevation.png) |  |

## 特徵與證據限制

完整長跨距禮堂外輪廓、突出中央入口、三組高窗、側面深直柱與高窗、側出入口雨遮；不以普通教室層窗替代禮堂立面。

官方現況主照2023年；防災表填表2021-10-01；截至2026年仍有修復再利用場勘，非修復完成版。

背面舞臺與服務空間僅按官方平面輪廓近似，留白不造窗；屋頂採淺坡保守體量，未測繪預力屋面實際曲率。2026修復案未作成品現況推定。

第三方照片/PDF不隨包散布。完整網址、頁碼與各自支持的特徵見 [sources.json](sources.json)。不將來源網頁更新日視為攝影日。

## 3D列印檔案

- [model.stl](model.stl)：毫米，88.0 × 150.0 × 45.8 mm，含底座最長150 mm，各館獨立比例
- [scene.blend](scene.blend)：從交付STL匯入的可編輯網格；形狀與STL經比較一致
- [build_model.py](build_model.py)：獨立參數化重建來源；[requirements.txt](requirements.txt)
- [SHA256SUMS](SHA256SUMS)：逐檔校驗；STL SHA-256：b8c7c0d959a7c39c1ac9f647ffc4c9daf9f25accd5c33a1a34eb653d8b01619e

底座朝下列印。建議先以0.2 mm層高、0.4 mm噴嘴在自己的切片軟體檢視，確認簷口、雨遮、門楣與深凹窗的支撐需求。細窗框已加粗，仍須依材料、噴嘴及散熱調整。不要把數位QA解讀成免支撐保證。

## 可重現數位QA

1. Python執行 build_model.py 重建模型。
2. Blender背景執行 render_preview.py 生成實際STL正背、正立面、俯視與scene.blend。
3. Python依序執行 validate_model.py、check_contour_validity.py、check_thin_features.py；任何非零退出必須停止交付。

[validation.json](validation.json) 全部checks通過：原始STL法向、繞序、正體積、水密、每邊兩面、vertex link單環、單一連通表面、無分离内腔壳、重建SHA一致、Blend幾何一致與150mm限制。

[contour-validity-check.json](contour-validity-check.json)：以z=0.071mm起、0.2mm逐層，共229层，輪廓degree2闭合、单个與組合Polygon有效；不修補或吞掉invalid。

[thin-feature-check.json](thin-feature-check.json)：0.8mm參考寬度形態opening、1mm取样，最大損失比例0.02395%，超过1%層數0。此為輔助幾何篩檢，不是全面最小壁厚或工具路徑。

尚未做Cura/Prusa实际切片或實體試印，不宣稱保證可印。
