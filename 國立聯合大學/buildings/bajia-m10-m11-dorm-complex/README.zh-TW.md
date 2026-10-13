# 國立聯合大學｜八甲 M10 第十宿舍＋M11 第十一宿舍（連通建築群）

這是依公開官方外觀照片製作的近似建築微縮模型，供觀賞及 FDM 列印。不是校方工程圖、實測復原或統一校園比例。只含外殼造型，不含房間、住戶、門禁、設備配置或第三方照片。

## 身分與範圍
現行八甲地圖分列 M10、M11；官方外觀相簿以第十、十一宿舍合併標題。兩翼與中央連接在空拍照片中可直接核對，故保留為同一完整列印件。

## 尺寸與造型
- 最長邊 150 mm，實際 XYZ 尺寸：150.00 × 106.00 × 65.90 mm（含底座）。
- 單一連通、水密外邊界；實體建築量體與底座相連，不是需要拼合的散件。
- 正面朝 -Y、底座 Z=0；STL 本身沒有單位欄位，匯入時選毫米。
- 張開雙翼與保留的中央連通框架
- 密集豎向遮陽翼片、底層柱廊
- 外側高端牆、屋頂突起量體、淺浮雕圓形前庭

## 估計與簡化
- 這是一件 STL、代表兩個現行校園建物代碼；未任意切斷中間實際連通部分。
- 靠近 M6／圓廳一翼為 M10，較遠一翼為 M11；依官方地圖定位。
- 翼角、進深、窗格數與中央弧面作可列印近似；中央弧面以直段連通框簡化。
- 屋頂僅保留建築量體，不含水槽、設備或管線；不含圓廳及周邊道路細節。

所有模型的尺寸、深度、窗距與屋頂高差皆依外觀比例估計，並無量測尺度。簡化背面以 rear.png 可直接檢視。預覽色彩只屬材質；STL 不含色彩或貼圖。

## 列印建議
- 底座平放；建議 0.4 mm 噴嘴、0.16–0.20 mm 層高、3 道外牆、10–18% 填充。
- 最小特徵：豎翼片寬 1.0 mm；中央框架立柱 1.05 mm；主柱直徑 2.1 mm；樓板 1.2 mm；附壁窗凹深 0.8 mm。
- 支撐：中央連通框及底層柱廊有開口。中央樓板厚 1.2 mm、最大局部橋接約 15 mm；建議中央框架及底層雨遮使用局部支撐並預先檢查拆除空間。
- 此為 150 mm 獨立微縮件，不建議等比縮小至 100 mm 以下；細節會低於常見噴嘴的可靠表現。
- 實心在此指封閉可切片的量體，不要求 100% 填充。未進行實體試印或切片器驗證；請自行檢查支撐、首層與機台公差。

## 隨附檔案與重建
- model.stl：毫米列印網格
- scene.blend：可編輯 Blender 網格、材質、相機；模型為實際 STL 匯入，非額外裝飾版
- build_model.py：原始參數化造型程式；所有可列印幾何可由此重建
- render_preview.py：由 STL 直接渲染 front.png / rear.png，並儲存 Blender 場景
- requirements.txt：Python 依賴版本
- validate_model.py、validation.json：原始 STL 法向、邊、頂點連結、水密性、連通數、內腔殼等檢查
- rebuild-check.json：再次重建後的 SHA-256 一致性
- blender-geometry-check.json：STL 與 Blender 全部三角面座標一致性
- evidence.json：完整外觀圖說、網址、身份和估計說明
- SHA256SUMS：所有公開檔案雜湊

在獨立 Python 環境執行：

    pip install -r requirements.txt
    python build_model.py
    python validate_model.py model.stl --output validation.json
    blender -b -t 4 -P render_preview.py

建議 Blender 4.x。Python 使用 numpy、trimesh、manifold3d、scipy。重建不依賴原作者資料夾或網路照片。數位檢查通過並不等於實體試印成功。

## 公開來源
查核日：2026-10-11。照片版權歸原權利人；本包不重製參考照片。
- 現行校園地圖與代碼：https://www.nuu.edu.tw/p/426-1000-9.php?Lang=zh-tw
- 官方外觀相簿：https://secretary.nuu.edu.tw/p/132-1003-1118.php?Lang=zh-tw
- 歷史名稱／建物清冊（歷史資料）：https://nuuarchives.nuu.edu.tw/p/16-1097-27990.php?Lang=zh-tw
