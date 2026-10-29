# 國立清華大學｜王默人周安儀文學館

## 模型預覽


| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 正面與來源支持區域<br>![正面](appearance/previews/front.png) | 未知後牆中性／板帶屋坡有界延伸<br>![背面](appearance/previews/rear.png) |  |

## 5 材質外觀版（2026-10-21）


[來源界線與四視角](appearance/README.md) · [表面色 3MF](appearance/nthuwang-appearance.3mf) · [可編輯場景](appearance/scene.blend)

依白天長立面與端景限定灰混凝土、淡銀橄欖窗格、離散上窗及屋坡同系統延伸；下部混合通道和未知後牆中性，保留地形／屋形簡化。 原 STL 與歷史 QA 不變；這是外觀改善，不是新增幾何。原單色正面（歷史檔案留存，不作本頁預覽）／原單色背面（歷史檔案留存，不作本頁預覽）


第四批公開外觀近似模型，並非測繪成果。每件獨立比例，150.00 × 108.00 × 82.00mm，最長150mm含底座。全校尚未完成。

## 來源與觀察
[官方建築導覽](https://www.nthu.edu.tw/future/content_m3)；2026-10-13檢視來源實際像素。

已實看完工建築長側、下坡端面夜景及湖畔遠景照片；校方記載2024年6月落成。保留高低變化坡屋頂、厚簷、頂層深遮陽片、退縮窗面、環繞外凸陽台樓板和下層斜向扶牆。

來源照片僅列連結，不放入成果、不重新發布：
- https://attractions.site.nthu.edu.tw/var/file/515/1515/pictures/673/m/mczh-tw700x700_large56165_637767283320.jpg
- https://attractions.site.nthu.edu.tw/var/file/515/1515/pictures/673/m/mczh-tw700x700_large56166_935407683320.jpg
- https://www.nthu.edu.tw/images/hotNews_171947724298.jpg
- https://www.nthu.edu.tw/images/hotNews_171947724222.jpg

## 近似與缺口
原建築隨丘陵起伏，模型整平地形並將下層壓縮成可列印實體，並非原建築各樓層精確對位。自由曲線陽台以折角輪廓近似；屋脊變化規律化為五段，不能視作真實屋頂測繪。樓梯僅概括可見外部動線，省略細欄杆。背側未見完整立面，明示素面；未知屋面設施不加造。

僅公開訪客可見外觀，無室內、地下、敏感設備或安全配置。未下載、擷取或反編譯官方Unity或任何原始3D模型。官方3D場景沒有逐面檢視，不能視為未見部位已獲證實。

## 檔案
- `build_model.py`：可攜參數化來源。
- `model.stl` / `model.obj`：單一連通、封閉實體，單位mm；不預挖內腔。
- `scene.blend`：實際STL的可編輯三角網格與相機，不是BIM或保留布林歷史的場景。
- `previews/front.png`、`rear.png`、`elevation.png`：實際STL預覽，已看像素。正背為顯示方向，不是實測方位。
- `validation.json`：原檔法線、邊與頂點流形、正體積、單一表面、重建及Blend/STL一致等18項通過。
- `check_layers.py` / `layer-check.json`：0.2mm幾何截面與0.8mm XY薄特徵篩查。

## 列印起點與支撐
底座向下，保持150mm尺寸。可從0.4mm噴嘴、0.2mm層高、3道外牆、15–20%填充起始，但不是測試完成的參數。

深簷懸挑、陽台底面、窗凹和外階梯接樓板處需要在切片器評估局部支撐。大斜扶牆有實心背襯；窗框1.2mm、遮陽片2.3mm、陽台樓板4mm，均已加粗。

薄特徵：3個最高屋脊尖頂抽樣高度z=77.90001、79.90001、81.90001mm被0.8mm篩查標記，為厚坡屋頂最尖端，非連續薄壁；可能被切片器省略或鈍化最後一層，請檢查刀路。

## 驗證範圍
18項網格驗證通過；原始STL法線與繞向相符，所有邊連接兩面、頂點環流形、單一連通表面且沒有分離內腔殼，正體積、z=0底面與150mm最大尺寸通過。乾淨暫存目錄重建STL的SHA-256相符，Blender幾何與STL一致；驗證不自動修原檔。

0.2mm間距共410個抽樣高度，所有輪廓閉合。端點數值聚合容差0.0001mm；首層0.100013mm以避共面。0.8mm XY形態開運算標示3層超過0.2mm²警戒，最大差異面積28.17209mm²，含義見薄特徵說明。

**未正式切片、未生成G-code、未實體試印。** 抽樣幾何截面不等於刀路、擠出、支撐或橋接驗證，亦不能證明全面三維壁厚或自相交完全不存在。

## 重建
Python 3.12與Blender 4.3.2+；所有程式從本檔目錄讀寫，不依賴製作端絕對路徑。

```sh
python -m pip install -r requirements.txt
python build_model.py
blender -b -t 2 -P render_preview.py
python validate_model.py
python check_layers.py
```


## 實際STL正背並排

