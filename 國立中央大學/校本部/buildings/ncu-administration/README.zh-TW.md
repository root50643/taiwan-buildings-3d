# 國立中央大學行政大樓｜150 mm 外觀模型

## 模型預覽


| 新彩色斜前 | 新彩色來源相近角度 | 新彩色正立面 |
| :---: | :---: | :---: |
| ![新彩色斜前](appearance/front.png) | ![新彩色近來源角度](appearance/source-angle.png) | ![新彩色正面](appearance/elevation.png) |
| 新彩色背面（未知中性） | 新彩色上視（未知屋面中性） | 彩色下載 |
| ![新彩色背面](appearance/rear.png) | ![新彩色上視](appearance/top.png) | [彩色 3MF](appearance.3mf) · [彩色 Blender](appearance.blend) |

### 新增正面有限配色（本頁顯示新版配色圖，原圖檔留存）

依校方無障礙地圖的行政大樓實照補色：淺灰米格陣、深綠灰孔後、暗藍灰大窗、灰米雨庇／柱／階及深灰褐正面上緣。**孔後顏色只是遮陽格陣後方的深色代理，不是宣稱每孔都是玻璃。** 未知側面、背面及屋頂維持中性灰，不加遠處總圖書館的塔。


原三圖、原 STL／scene.blend／幾何尺寸與首頁、校級選圖均保留；新彩圖另存，原 STL 不帶色。照片日期未知，不代表2026現況。詳[配色來源、勘誤及重建](APPEARANCE.md)。

此為公開外觀資料研究模型，非測繪、施工或正式切片檔。每棟獨立縮尺，含底座最長150 mm，不能直接當作同一比例校園拼圖。本檔尺寸約 150 × 87 × 47.1 mm。

## 保留的識別特徵
- 橫長四層量體、错位方形遮陽格陣
- 非均勻大窗穿插與前方突出入口雨庇
- 左右入口支柱、前階及左側水平帶

## 證據與簡化
- 主要照片為正面與斜正面，深度及側後量體為概略估計，後面素面。
- 樹木遮住兩端部分立面；格孔節奏保留但數目和尺寸非測繪。
- 照片遠處總圖書館不是行政樓屋頂設施，未合併進此模型。

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

0.2 mm幾何截面共 236 層，全部閉合=True。另以1 mm間距檢查0.8 mm XY形態開運算薄特徵，0 層損失面積超過1%；尖角也會被計入，見 thin-feature-check.json。這不是全域壁厚保證，也不是正式切片或試印。

底座平放。入口雨庇與格孔上緣需評估支撐。建議先以0.4 mm噴嘴、0.2 mm層高在實際切片軟體檢查外壁、橋接、支撐可移除性與底板附著，再決定列印設定。小窗框、曲面尖端與薄簷口可能不完整重現；不得將幾何通過寫成「免支撐、保證可印」。

SHA256SUMS含可發布檔案雜湊。尚未實體試印。此為全校持續研究中的一件，不代表全校完成。

## 檔案下載與實際模型預覽

[STL](model.stl) · [可編輯 Blender](scene.blend) · [Python 來源](build_model.py) · [完整驗證](validation.json) · [來源](sources.json)


以上皆由交付STL渲染；rear所示未知背側簡化，不代表有同視角實景佐證。相機視角不是精確地理方位。

## 截面數值方法修訂與補查

本發布包已直接採用canonical-edge-v2薄篩工具與結果，固定共邊插值方向，要求節點度數2、閉環及各Polygon有效，再做1 mm間距的0.8 mm XY開運算。舊版可能因共邊端點分開計算後取整而漏環，不能沿用舊面積值。這項修正不改STL、Blender或重建來源；真實薄特徵警示照常保留。

另以0.2 mm間距逐層補查閉環及Polygon有效性，共 236 層通過，見[有效性報告](contour-validity-check.json)與[可攜檢查程式](check_contour_validity.py)。這項較密補查沒有做薄篩開運算；薄篩採樣間距仍是1 mm。兩者都不是正式切片、試印或全域壁厚保證。
