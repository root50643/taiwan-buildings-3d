# 國立中央大學科學三館｜150 mm 外觀模型

## 模型預覽

| 新彩色斜視 | 新彩色低角度 | 新彩色正面 |
| :---: | :---: | :---: |
| ![彩色斜視](appearance/front.png) | ![彩色低角度](appearance/source-angle.png) | ![彩色正面](appearance/elevation.png) |
| 新彩色背面 | 新彩色上視 | 彩色下載 |
| ![彩色背面](appearance/rear.png) | ![彩色上視](appearance/top.png) | [彩色3MF](appearance.3mf) · [彩色Blender](appearance.blend) |


### 照片近似彩色預覽

依完整正面實景與校方入口近照交叉核對：原前牆／柱／凹口粉灰、窗背暗灰綠、中央凹窗稍淺、既有排氣柱淺灰與帽灰；未知側背與屋頂中性。灰綠水平細帶無獨立原面界，省略不切面。


原三圖、geometry／尺寸／STL／OBJ／scene與首頁／校級選圖不變；詳[來源與重建限制](APPEARANCE.md)。

此為公開外觀資料研究模型，非測繪、施工或正式切片檔。每棟獨立縮尺，含底座最長150 mm，不能直接當作同一比例校園拼圖。本檔尺寸約 150 × 104 × 66 mm。

## 保留的識別特徵
- 左側兩層高度的挑空柱廊與深凹入口
- 跨越上方的連續頂層量體及水平窗帶
- 屋頂可見的粗化通風塔群

## 證據與簡化
- 校方斜側與Commons正面共同核對前側大凹口，但後面與深度仍目測、素面簡化。
- 左廊中段樓板、入口窗帶以可列印幾何近似，不保證柱距、開孔數量或樓層標高。
- 屋頂排氣塔保留辨識分組，位置與尺寸粗化；未完整重建機電。
- 2013照片不代表2026每一項設備與外牆現況，且實際樓宇不一定簡單矩形完整後段。

全部來源及照片/設計圖區分見 sources.json。來源原照片、PDF、內部對照圖不隨模型發布。照片年代不同，不聲稱完整2026現況。

## 檔案與重建
- model.stl：單一連通列印實體，單位毫米
- scene.blend：由交付STL匯入的可編輯網格（不是參數化BIM）；預覽材質只供展示
- build_model.py：可攜參數化量體來源，無需來源照片即可重建
- previews/front.png、rear.png、elevation.png：從實際STL渲染，不是設計效果圖；名稱為相機視角，非精確方位

使用 Python 3.12，依 requirements.txt 準備相依套件，Blender 4.3.2。

    python build_model.py
    blender -b -t 2 -P render_preview.py
    python validate_model.py
    python check_layers.py
    python check_thin_features.py

## 幾何檢查及列印限制
原始STL法線與繞序一致、水密、每邊兩面、頂點鏈單環、單連通表面、無分離內腔殼、正體積、乾淨重建同SHA-256、已存Blender/STL三角幾何一致，詳 validation.json（passed=True）。

0.2 mm幾何截面共 330 層，全部閉合=True。另以1 mm間距檢查0.8 mm XY形態開運算薄特徵，0 層損失面積超過1%；尖角也會被計入，見 thin-feature-check.json。這不是全域壁厚保證，也不是正式切片或試印。

底座平放。大挑空頂板、深凹口及廊道楼板必須評估支撐與可移除性。建議先以0.4 mm噴嘴、0.2 mm層高在實際切片軟體檢查外壁、橋接、支撐可移除性與底板附著，再決定列印設定。小窗框、曲面尖端與薄簷口可能不完整重現；不得將幾何通過寫成「免支撐、保證可印」。

SHA256SUMS含可發布檔案雜湊。尚未實體試印。此為全校持續研究中的一件，不代表全校完成。

## 檔案下載與實際模型預覽

[STL](model.stl) · [可編輯 Blender](scene.blend) · [Python 來源](build_model.py) · [完整驗證](validation.json) · [來源](sources.json)


以上展示為交付彩色外觀模型的渲染；rear所示未知背側簡化，不代表有同視角實景佐證。相機視角不是精確地理方位。

## 截面數值方法修訂與補查

本發布包已直接採用canonical-edge-v2薄篩工具與結果，固定共邊插值方向，要求節點度數2、閉環及各Polygon有效，再做1 mm間距的0.8 mm XY開運算。舊版可能因共邊端點分開計算後取整而漏環，不能沿用舊面積值。這項修正不改STL、Blender或重建來源；真實薄特徵警示照常保留。

另以0.2 mm間距逐層補查閉環及Polygon有效性，共 330 層通過，見[有效性報告](contour-validity-check.json)與[可攜檢查程式](check_contour_validity.py)。這項較密補查沒有做薄篩開運算；薄篩採樣間距仍是1 mm。兩者都不是正式切片、試印或全域壁厚保證。
