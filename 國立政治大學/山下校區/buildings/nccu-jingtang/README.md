# 國立政治大學｜井塘樓

## 模型預覽


| 新版模型預覽 | 新版模型預覽 | 新版模型預覽 |
| :---: | :---: | :---: |
| ![前庭左斜](appearance/previews/front.png) | ![前庭右斜](appearance/previews/opposite.png) | ![正立面](appearance/previews/elevation.png) |
| ![背面](appearance/previews/rear.png) | ![頂面](appearance/previews/top.png) |  |

山下校區。依公開實景與官方平面外輪廓自建的完整建物外觀近似，非测绘、BIM或結構設計。


俯視（歷史檔案留存，不作本頁預覽） · 正立面（歷史檔案留存，不作本頁預覽）


## 形狀及證據限制

半圓弧四層量體、開放內彎前庭、放射狀立柱及窗格、弧形簷口、中央入口雨遮與後側突出部。曲面以80段取樣，自建外輪廓。

外側後彎立面缺完整近照，保守留白，不補造窗陣。弧半徑、後侧突出部高度與進深皆視覺近似；實際曲線可能非數學等半徑。

官方防災表内日期2021-10-01，PDF編成2026-03-04，两者不可當照片拍攝日。來源網址、頁碼與支持特徵見[sources.json](sources.json)。第三方原圖不隨包散布。

官方地面4層、地下1層。本件只建地上4層：地面入口層一排窗＋其上三排，屋簷不是第五窗層。

## 使用方式

- [model.stl](model.stl)：毫米，150.0 × 110.0 × 59.5 mm；含底座最長150 mm，各館獨立比例
- [scene.blend](scene.blend)：實際STL匯入的可編修網格，已與交付STL幾何比較
- [build_model.py](build_model.py)：獨立參數重建來源；[requirements.txt](requirements.txt)
- [SHA256SUMS](SHA256SUMS)：逐檔雜湊；STL SHA-256為 4321f4114275c766ac743e0adb1bac9d9626368a9fee920ea4734b805032453f

底座朝下。可先以0.2 mm層高、0.4 mm噴嘴作切片檢查起點，按自己的材料、機台及冷卻條件決定支撐；深凹入口、柱廊、雨遮、頂層簷口和凹窗頂尤其需檢視。窗框／柱／天井邊緣已加粗連接，不代表不需要支撐。

## Fail-closed數位QA

Python執行build_model.py；Blender背景執行render_preview.py產生實際STL預覽與scene.blend；再依序執行validate_model.py、check_contour_validity.py、check_thin_features.py，任一步非零退出都必須停止交付。

[validation.json](validation.json)全部checks=true：原始STL法向／繞序／正體積、水密、每邊2面、vertex link單一環、單一連通表面且無內腔殼、尺寸、獨立重建SHA、Blend/STL幾何一致。

[contour-validity-check.json](contour-validity-check.json)：固定z=0.071 mm起、0.2 mm層距，共298層，degree2閉合、每個與組合Polygon均有效，遇invalid不修補。

[thin-feature-check.json](thin-feature-check.json)：canonical邊內插，1 mm取樣，以0.8 mm參考寬度形態opening輔助篩檢；最大面積損失0.12927%，大於1%層數0。不是全面最小壁厚或實際工具路徑。

未做Cura/Prusa实际切片或實體試印，不宣稱保證可印或全校完成。

## 前庭有限外觀層

[三材質3MF、可編輯Blend與五視角預覽](appearance/README.md)：僅內弧白牆／柱1395面＋灰雨棚立邊9面，其餘4772面中性；非整樓全彩復原。

