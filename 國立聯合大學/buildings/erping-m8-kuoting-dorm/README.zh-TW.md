# 國立聯合大學｜二坪山 M8 第八宿舍（國鼎館）

## 6 材質外觀版（2026-10-21）

| 正面與來源支持區域 | 背牆中性／棚頂保守銀灰代理 |
|---|---|
| ![正面](appearance/previews/front.png) | ![背面](appearance/previews/rear.png) |

[來源界線與四視角](appearance/README.md) · [表面色 3MF](appearance/nuum8-appearance.3mf) · [可編輯場景](appearance/scene.blend)

暖赭磚與中央方窗、淡薄荷上窗；高窗帶混合面中性。實景 PV 已證實但原屋面未分陣列間隙，保守銀灰代理，不造整頂藍色覆蓋。 原 STL 與歷史 QA 不變；這是外觀改善，不是新增幾何。[原單色正面](previews/front.png)／[原單色背面](previews/rear.png)


這是依公開官方外觀照片製作的近似建築微縮模型，供觀賞及 FDM 列印。不是校方工程圖、實測復原或統一校園比例。只含外殼造型，不含房間、住戶、門禁、設備配置或第三方照片。

## 身分與範圍
現行地圖 M8 第八宿舍（國鼎館）與官方入口照片相符。校史記載一至五樓及其後六樓增建；這不是八甲 L1 國鼎圖書館。

## 尺寸與造型
- 最長邊 150 mm，實際 XYZ 尺寸：150.00 × 108.00 × 97.99 mm（含底座）。
- 單一連通、水密外邊界；實體建築量體與底座相連，不是需要拼合的散件。
- 正面朝 -Y、底座 Z=0；STL 本身沒有單位欄位，匯入時選毫米。
- 中央細方格窗面及旁側通高玻璃帶
- 左前低附樓、主入口長階梯
- 上層玻璃帶與淺拱形折面大屋頂

## 估計與簡化
- 照片確認正面及兩側，背面窗列無清楚證據，刻意保留素面。
- 屋頂弧線化為分段折面，太陽能面以淺刻縫示意；未製作設備。
- 總深度、部分窗格數量與階梯比例為估計；不含相鄰 M1 或 M4。

所有模型的尺寸、深度、窗距與屋頂高差皆依外觀比例估計，並無量測尺度。簡化背面以 rear.png 可直接檢視。預覽色彩只屬材質；STL 不含色彩或貼圖。

## 列印建議
- 底座平放；建議 0.4 mm 噴嘴、0.16–0.20 mm 層高、3 道外牆、10–18% 填充。
- 最小特徵：格窗之間實體格條約 1.1 mm，淺凹約 0.9 mm；窗框 0.8–0.9 mm；入口柱寬 2.5 mm；屋頂刻縫寬 0.55 mm、深約 0.25 mm。
- 支撐：實心屋頂無封閉內腔。入口局部懸挑約 4 mm、約 29 mm 橫跨，建議局部支撐；大階梯可直接朝上列印。
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
- 官方外觀相簿：https://secretary.nuu.edu.tw/p/132-1003-1108.php?Lang=zh-tw
- 歷史名稱／建物清冊（歷史資料）：https://nuuarchives.nuu.edu.tw/p/16-1097-27990.php?Lang=zh-tw
