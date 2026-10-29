# 國立聯合大學｜二坪山 M7 第七宿舍（雙電樓）

## 模型預覽


| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 正面與來源支持區域<br>![正面](appearance/previews/front.png) | 未見外側背面中性<br>![背面](appearance/previews/rear.png) |  |

## 8 材質外觀版（2026-10-21）


[來源界線與四視角](appearance/README.md) · [表面色 3MF](appearance/nuum7-appearance.3mf) · [可編輯場景](appearance/scene.blend)

灰牆與淺色直柱、離散窗背、青藍電梯塔與綠帽；兩翼 PV 由官方高位照確認，上表面深藍，未知短端與背牆中性。 原 STL 與歷史 QA 不變；這是外觀改善，不是新增幾何。原單色正面（歷史檔案留存，不作本頁預覽）／原單色背面（歷史檔案留存，不作本頁預覽）


這是依公開官方外觀照片製作的近似建築微縮模型，供觀賞及 FDM 列印。不是校方工程圖、實測復原或統一校園比例。只含外殼造型，不含房間、住戶、門禁、設備配置或第三方照片。

## 身分與範圍
現行校園地圖 M7 第七宿舍（雙電樓）與官方相簿、入口 Dorm 7 一致；不可與八甲 B1 電機系混淆。

## 尺寸與造型
- 最長邊 150 mm，實際 XYZ 尺寸：150.00 × 122.00 × 90.20 mm（含底座）。
- 單一連通、水密外邊界；實體建築量體與底座相連，不是需要拼合的散件。
- 正面朝 -Y、底座 Z=0；STL 本身沒有單位欄位，匯入時選毫米。
- 折角雙翼、內角入口與階梯
- 長立面五排窗列與連續豎向構件
- 兩片屋頂棚與高出屋面的玻璃外塔輪廓

## 估計與簡化
- 相對翼長、厚度及高差由斜視照片估計，並非原始建築平面。
- 未清楚拍到的後牆保留素面；部分轉角簡化為直角。
- 屋面棚架與窗框加粗，未複製設備、管線或室內配置。

所有模型的尺寸、深度、窗距與屋頂高差皆依外觀比例估計，並無量測尺度。簡化背面以 rear.png 可直接檢視。預覽色彩只屬材質；STL 不含色彩或貼圖。

## 列印建議
- 底座平放；建議 0.4 mm 噴嘴、0.16–0.20 mm 層高、3 道外牆、10–18% 填充。
- 最小特徵：棚板 1.4 mm、柱寬 1.5 mm；立面豎條 1.3 mm；窗楣 0.85 mm，附壁而非懸空。
- 支撐：兩片棚下約 3.5 mm 空隙，跨度隨柱距約 16 mm；外側入口凸出與棚板需於切片器檢查局部支撐。
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
- 現行校園地圖與代碼：https://www.nuu.edu.tw/p/426-1000-10.php?Lang=zh-tw
- 官方外觀相簿：https://secretary.nuu.edu.tw/p/132-1003-1109.php?Lang=zh-tw
- 歷史名稱／建物清冊（歷史資料）：https://nuuarchives.nuu.edu.tw/p/16-1097-27990.php?Lang=zh-tw
