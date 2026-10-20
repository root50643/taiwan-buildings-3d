# 國立成功大學｜臺灣文學系E101棟（原軍方辦公室048）

第十批，力行校區。尺寸 150 × 86 × 43 mm，底座最長邊150 mm，每件比例獨立。

## 最新七材質外觀版（2026-10-20）

| 正面原幾何配色 | 背面與未見面保持中性 |
|---|---|
| ![正面](appearance/previews/front.png) | ![背面](appearance/previews/rear.png) |

[來源界線與四視角](appearance/README.md) · [表面色 3MF](appearance/e101-appearance.3mf) · [可編輯場景](appearance/scene.blend)

依官方 2017／2010 歷史照片登錄七拱磚牆、原白肩飾與灰綠窗格、前坡灰棕屋面；深廊口不是整片玻璃，中央門口中性。後面及小突出未知面保留中性，不捏造山牆斜飾邊。原STL與歷史QA不變，不是新增幾何。[原單色正面](previews/front.png)／[原單色背面](previews/rear.png)


## 來源與像素檢視

- [校方踏溯課程：臺灣文學系館](https://exptainan.liberal.ncku.edu.tw/index.php?id=2616&index=2&lang=cht&option=module&task=pageinfo)：已檢視較新正面照片：中央山牆、七個拱口、四個三角老虎窗及兩側對稱長面。
- [校方GIS：中央與轉角](https://db.nckumap.ncku.edu.tw/nckugis/public/uploadfiles.htm?action=listImg&q=36471)：已檢視紅磚拱廊、山牆白色肩飾及坡屋頂。
- [校方GIS：另一側角度](https://db.nckumap.ncku.edu.tw/nckugis/public/uploadfiles.htm?action=listImg&q=36470)：交叉檢視單層拱廊與屋頂長向；舊照片車輛、樹木遮擋處由新正面核對。
- [校方GIS公開外框](https://nckumap.ncku.edu.tw/map.php)：以E003外部輪廓標示的舊軍方建物號核對財產；不使用樓層、室內配置。
- [2026/1/30財產清冊](https://prop-oga.ncku.edu.tw/var/file/59/1059/img/4743/218075103.pdf)：力行校區R1E-11-0，同名古蹟單棟，不將群棟合併。

## 範圍與近似

只作GIS E003／館舍E101這一棟原軍方辦公室048，不是整組台文系館或整座原衛戍病院。保留七拱口、中央凸山牆、四老虎窗與長向斜屋頂。拱下窗格加粗，拱廊採有實體後牆淺凹，不建室內或貫通走廊。底層小通風口與肩飾簡化；西側小突出依公開外框加簡單低體，屋頂形狀未見清楚像素屬近似。背面留素面；不加旗桿、植栽、紀念碑、刻字。

## 交付與重建

- `model.stl`：毫米單位，與底座合成的單一實體。最長邊為 150 mm（含底座）；各棟獨立縮放，不適合直接拼成等比例校園。
- `build_model.py`：完整可攜參數化原始程式，無外部貼圖、私有路徑或參考照片依賴。
- `scene.blend`：由交付 STL 匯入，只有一個建築網格，可在 Blender 編輯頂點；細部參數請修改 Python 後重建。
- `previews/front.png`、`rear.png`、`elevation.png`：由實際交付 STL 產生。
- `validate_model.py`、`validation.json`：可重跑的幾何與重建驗證。

建議 Python 3.12，在虛擬環境執行：

```sh
python -m pip install -r requirements.txt
python build_model.py
blender -b -t 2 -P render_preview.py
python validate_model.py
```

已使用 Blender 4.3.2。驗證器在獨立臨時目錄重建 STL 並比較 SHA-256，讀取 Blender 場景的網格後比較三角形幾何。它檢查原始二進位 STL 儲存法線、面積、封閉性、邊恰有兩面、頂點連結為單一環、表面只有一個連通分量、正體積、底面位於 Z=0、最長邊 150 mm。單一封閉表面也排除獨立藏在內部的空腔殼；沒有宣稱完成所有自交的窮舉檢測。

## 製作原則與限制

這是依公開照片觀察製作的外觀近似收藏模型，不是測繪、修復、工程或精確 BIM 資料。牆身為實體，門窗、拱廊通常改成淺凹浮雕；不含室內、設備或安全配置。屋頂、深度、窗距及後側比例沒有測量基準，不能視為實際尺寸。原始參考照片未收錄、未重新授權或隨套件發布。來源權利屬原作者／校方；原創模型與程式可沿用儲存庫授權，不涵蓋外部參考照片。

## 列印說明

底座平貼平台，Z 軸向上。可從 0.4 mm 噴嘴、0.16–0.20 mm 層高、3 道外牆與 12–18% 填充開始試切片；這是設定建議，並非已測參數。小於約 0.8 mm 的淺浮雕可能因噴嘴或縮放消失。STL 是封閉實體，切片器仍會依填充率產生內部填充。

未實體試印、未執行切片器列印驗證，沒有保證免支撐。請依下列模型特有支撐需求檢查切片預覽。

拱洞上半及簷下可能需局部支撐，屋頂老虎窗斜面通常較易列印但未作切片驗證。

## 新增幾何輔助檢查

`validate_sections.py`以固定共享邊方向求交，0.20mm抽樣輪廓閉合，結果見`cross_sections.json`。`check_thin.py`先斷言輪廓閉合有效，再以1.0mm間距及0.8mm參考寬度作形態開運算；見`thin-feature-check.json`。尖屋頂/銳角也會出現面積差，不能直接當作壁厚失敗。兩項都不是實際切片器工具路徑、支撐驗證或實體試印。

查核日期：2026-10-13；GIS照片未標攝影日期，不宣稱每一細節代表2026最新現況。


## 整合版截面與薄特徵補充驗證

本整合版使用固定共同邊方向後插值的 `validate_sections.py` 與 [0.2 mm 截面結果](cross_sections.json)，避免同一邊浮點方向差異造成假斷環。原始 STL 幾何未修改。舊截面程式有閉合斷言，既有通過結果不代表曾有破面；此處以新版重跑結果為準。

另提供 `check_thin.py` 與 [新增 0.8 mm 薄特徵輔助篩查](thin-feature-check.json)：每 1 mm 水平取樣，先確認輪廓閉合與有效，再作半徑 0.4 mm 形態開運算。這不是切片器、完整壁厚分析或實體試印，尖屋頂、銳角也會造成損失，不能據此宣稱無支撐或列印成功。執行前請安裝 requirements.txt。
