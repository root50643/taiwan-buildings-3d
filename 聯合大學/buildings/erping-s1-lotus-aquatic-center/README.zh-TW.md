# 國立聯合大學 二坪山蓮荷水世界游泳館

依官方外觀照片製作的近似列印模型。最長邊獨立設定150 mm，並非全校統一縮尺或實測模型。正面朝-Y。只建外觀，不建內部配置。

## 外形與來源
長條低坡雙坡泳館、側窗帶、較低入口館、右側高牆與半圓門楣、綠色平簷。

官方相簿：https://secretary.nuu.edu.tw/p/132-1003-1089.php?Lang=zh-tw

完整照片標題與原圖來源見evidence.json。照片只用於研究，未收入交付檔。預覽直接渲染實際STL；顏色為材質，STL無顏色。

## 證據限制
只建館舍外觀，未建泳池內部、機械設備及管線。館側與後緣被樹木遮擋，深度與後牆採明示簡化。照片內旁邊高樓屬教職員宿舍，未合併。
所有長寬高、深度與樓層比例均為照片估計，未見部分不視為可靠復原；相簿發布／拍攝年代不等於2026現況。

## 列印
窗框1.2 mm；入口簷外挑約2.5 mm。屋頂為實體，底座平放；半圓門楣為附牆浮雕。
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
82.0 × 150.0 × 35.0 mm（X × Y × Z，含底座）。
