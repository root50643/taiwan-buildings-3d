# 國立聯合大學 八甲生活館圓廳

## 八材質外觀版（2026-10-20）

| 正面與已見露台 | 未見背面保守中性 |
|---|---|
| ![正面](appearance/previews/front.png) | ![背面](appearance/previews/rear.png) |

[來源界線與四視角](appearance/README.md) · [表面色 3MF](appearance/nuuround-appearance.3mf) · [可編輯場景](appearance/scene.blend)

依官方 2025 影像登錄前半鮭粉磚牆、奶白內女兒牆、藍灰頂沿及灰褐露台；未見外側背牆中性。原方盒附量體仍為簡化，不添加缺少的細馬賽克帶、設備或招牌。原 STL 與歷史 QA 不變；這是外觀改善，不是新增幾何。[原單色正面](previews/front.png)／[原單色背面](previews/rear.png)


依官方外觀照片製作的近似列印模型。最長邊獨立設定150 mm，並非全校統一縮尺或實測模型。正面朝-Y。只建外觀，不建內部配置。

## 外形與來源
橢圓雙層主體、平頂女兒牆、偏左高直立塔、前凸低入口、兩側外梯。

官方相簿：https://secretary.nuu.edu.tw/p/132-1003-1116.php?Lang=zh-tw

完整照片標題與原圖來源見evidence.json。照片只用於研究，未收入交付檔。預覽直接渲染實際STL；顏色為材質，STL無顏色。

## 證據限制
M6第六宿舍不屬本模型。圓廳完整外圈有局部遮擋；背側窗位採簡化規律近似，不宣稱逐窗實測；橢圓比例及樓高皆為照片估計。
所有長寬高、深度與樓層比例均為照片估計，未見部分不視為可靠復原；相簿發布／拍攝年代不等於2026現況。

## 列印
女兒牆2.5 mm，入口細框1.2 mm，樓梯寬10 mm；平屋頂與實心樓梯容易列印，門簷懸挑約3 mm需切片檢查。
建議0.4 mm噴嘴、0.16–0.20 mm層高、底座平放、先在切片器檢查支撐與橋接。布林合併為單一封閉連通實體，保留外露孔洞／廊道。不含封閉內腔殼。未做實際列印或切片驗證。

## 內容與重建
- build_model.py：原創參數化外觀來源，Python 3.11+
- model.stl：毫米單位可列印網格
- scene.blend：與STL一致的可編輯網格場景（另含攝影棚地面）
- previews/front.png、rear.png：實際STL全幅前後視圖
- validate_model.py、validation.json：原始法線、邊、頂點連結、連通與尺寸檢查
- rebuild-check.json、blender-stl-agreement.json、SHA256SUMS：重建與交付核對

安裝requirements.txt後執行python build_model.py；再執行python validate_model.py model.stl --longest-edge 150 --output validation.json。Blender 4.3.2執行blender -b -t 2 -P render_preview.py可重建預覽與場景。

## 實際模型尺寸
150.0 × 135.0 × 79.8 mm（X × Y × Z，含底座）。
