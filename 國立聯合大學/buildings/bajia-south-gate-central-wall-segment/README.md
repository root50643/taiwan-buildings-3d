# 國立聯合大學八甲南大門中央三段門牆外觀段

![實際模型正面斜視](previews/front.png)

新增的照片導向建築外觀模型，**只包含兩車道之間中央三段實心門牆**，不是完整南大門，也不是北大門或二坪山校門。

## 檔案與實際視圖
- [可編輯彩色 Blender](scene.blend)
- [彩色 3MF](model.3mf)：6 種獨立命名展示材質，可逐項換色；不是列印機料槽指派。
- [單色幾何 STL](model.stl)
- [可重建生成器](build_model.py) · [渲染器](render_model.py) · [材質表](palette.json)
- [正面斜視](previews/front.png) · [背面](previews/rear.png) · [正立面](previews/elevation.png) · [俯視](previews/top.png) · [左斜視](previews/left_oblique.png)
- [來源與推估邊界](SOURCES.md) · [驗證及列印限制](QA.md)

## 表達範圍
保留高聳中央白色校名面、紅褐磚色直立邊、兩片較低灰色門牆、三個淺凹灰色平頂及橘紅壓頂。中央立面略向路側突出，白色面板是有實心背板的淺凹，不是可穿越門洞。書法文字刻意留白；磚與石材只以色區區分，不複製攝影紋理，不任意添加密集磚縫。

排除獨立行人小門、兩側伸縮門、警衛亭、告示、花草、車輛、道路及校園其他建築。**這個模型不將整座南大門標示為完成。** 未見背面採中性灰色封閉，中央後緣未虛構紅色橫框。

展示尺寸 **152 × 52 × 73 mm**，含另加 3 mm 底板；門牆寬 140 mm、中央高 70 mm、側牆高 57 mm，深度約 34–38.6 mm，皆為照片比例推估，非量測縮尺。側頂框寬與淺凹深 1.6 mm 是模型辨識性調整。官方來源拍攝於 **2025-03-10**，不表示 2026 現場狀態；原照片不隨包發行。

## 重建
Python 幾何環境依 `requirements.txt`；交換驗證另需 lib3mf SDK。
```sh
python build_model.py
python qa_model.py
python check_features.py
python verify_exchange.py
blender -b -t 4 --python render_model.py
blender -b -t 4 --python verify_scene.py
blender -b -t 4 --python verify_render.py
python verify_package.py
```
若 lib3mf 與幾何套件分屬不同環境，以 `BUILD_PYTHON` 指定生成器 Python。渲染採 Blender 4.3.2 CPU Cycles、seed 0、48 samples；不承諾跨版本／平台圖片位元組一致。

**沒有實際列印測試，不保證免支撐或直接可印。** 白色淺凹上緣仍有向下面，須依切片方向、線寬與設備評估。數值拓撲與切片測試不等於完整製造認證。
