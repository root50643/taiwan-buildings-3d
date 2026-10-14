# 實踐大學 C棟民生學院教學大樓

2016–2017更新版完整外部主體近似，非2026測繪；本件不代表全校已完成。往D棟橋廊僅建C棟側4m截段，不含D棟。

| 南西正面 | 北東背面 |
|---|---|
| ![正面](previews/front.png) | ![背面](previews/rear.png) |

## 下載與重建
- [model.stl](model.stl)：毫米，150×53×32.923mm，底座朝下；主體約1:357.14，底座厚2.4mm
- [scene.blend](scene.blend)：由交付STL直接匯入的可編輯網格；[build_model.py](build_model.py)是原創參數來源
- Python 3.12，pip install -r requirements.txt；python build_model.py；blender -b -t 3 -P render_preview.py
- python check_thin_features.py；python check_layer_components.py；python check_screen.py；python validate_model.py
- [頂視](previews/top.png)、[西側](previews/west.png)、[東側](previews/east.png)、[南立面](previews/south-elevation.png)、[北立面](previews/north-elevation.png)

## 建模依據與限制
採建築師2017年刊公開1–3F完整平面、8m比例尺、木桁架雙坡屋頂剖面、南西竣工照片與C棟10.9m數字。模型保留南面柱廊、大漏窗屏、中央教室雙坡屋頂、西端屋頂平台、東端梯間、北側橋廊及階梯平台凸出。[來源與描摹控制點](sources.json)。

比例尺177px=8m，主體約50.53m長、8.85m深，西端約12.35m深。按可見主體外緣估算約491㎡，未強行以刊物661㎡逆推改寬；兩者口徑（完整橋廊／計入空間等）未獨立核定，是尺度不確定性。10.9m解讀為高屏頂；樓層與屋脊比例由剖面近似。木桁架以外部雙坡包絡表示，無假造內部桁架。北側無完整竣工正照，僅窗樣簡化，不省略已知凸出主體。

## 列印警示
最長150mm，底座朝下。南側長柱廊樓板、漏窗屏底端、橋廊與北側上層平台存在水平懸挑／橋接，請在切片軟體檢視支撐及橋接，必要採局部支撐；數位檢查不是Cura/Prusa工具路徑或實體試印，不保證無支撐可印。

柱根一般1.34mm、北橋墩1.68mm、平台板約1.20mm、高屏厚約1.32mm。漏窗孔列大幅粗化，最窄橫向連接約1.02mm；屋脊加1.26mm寬平頂，避免尖脊最後數層消失。細件連接靠源幾何加厚，未用repair補網格。

[validation.json](validation.json)檢查原始STL單殼、水密、每邊兩面、vertex link單環、法向／繞序、獨立重建SHA與Blend/PNG一致；[layer-component-check.json](layer-component-check.json)逐0.2mm截面、每原Polygon erosion/opening不消失不分裂。0.8mm opening只是輔助篩檢，非全方向壁厚或列印保證。opening有顯著局部面積損失，詳見下方數值例外。[細構件說明](thin-feature-review.json)。[漏窗104孔實際STL逐孔量測](screen-check.json)：孔間最薄1.015274mm，下緣最薄1.042439mm。

## 漏窗薄屏：opening高損失例外與列印警示

這件是有明確限制的近似模型，不宜把「輪廓保持連通」讀成「細節無損」或「保證可印」。原始STL的0.8mm參考opening（0.4mm erosion後再膨脹）在0.2mm逐層檢查中，有7層（z=29.671–30.871mm）整層面積損失超過1%，整層最大8.042467189442443%。2853筆跨層原Polygon樣本中2272筆損失超過1%；2272是截面樣本次數，不是實體柱數。單一樣本最大損失15.08524758268949%，最差保留84.91475241731051%。全部原Polygon依然各保留一個，沒有消失或分裂。

以原輪廓頂點0.41mm鄰域檢視，鄰域以外損失最高仍為原構件面積的0.132081786906%；因此並非全由四角造成，也不能宣稱尖角以外完全不變。保留原始分數及全層明細，沒有用共線點精簡、重算低分或修補網格替代原結果。

獨立檢查涵蓋104孔的實際STL孔間距離與法線射線：孔間最薄1.015274mm，法線實體厚度取樣最小1.3216mm；另12條孔間垂直根部射線證明與下方樓板相連。這些是漏窗屏指定位置的證據，不是整模型、全方向最小壁厚證明，也不保證所有切片設定皆保留細節。

請維持150mm最長尺寸，不任意縮小；薄屏與孔間細根可能受噴嘴、線寬、材料及取向影響。柱廊、屏底、橋廊和平台需在切片軟體逐處檢視支撐、橋接及拆支撐風險。尚未實體試印，也沒有Cura/Prusa實際工具路徑驗證；這是保留高損失數值後的具體例外，不等同全面可列印認證。

[原始STL逐層逐構件完整明細](independent-opening-detail.json) · [104孔厚度及12根部射線](independent-screen-probes.json) · [未處理STL獨立檢查](independent-raw-stl-check.json) · [補充摘要](opening-warning-supplement.json) · [獨立審核精確七層摘要](independent-thin-warning-summary.json)

## 權利與狀態
模型由公開圖原創參數建造。蘇富源建築師事務所＋嶼山工房／建築師雜誌及校方來源僅列URL署名，原照片與PDF不在此交付包。外觀已獲來源限定近似版核准；原STL維持凍結。本文件補充opening高損失例外及獨立證據，須與原檔案一同閱讀，待文件覆核納入正式包。
