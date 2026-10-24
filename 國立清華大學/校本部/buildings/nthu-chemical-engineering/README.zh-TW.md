# 國立清華大學｜化工館

第三批公開外觀近似模型，並非測繪成果。每件獨立比例，150.00 × 118.00 × 92.00mm，最長150mm含底座。全校尚未完成。

## 來源與觀察
[官方建築導覽](https://attractions.site.nthu.edu.tw/p/406-1515-187011,r8697.php?Lang=zh-tw)；2026-10-13檢視來源實際像素。

已實看官方正面與正右側外觀照片。可辨識中央上方微尖山牆、凸出中央塊、貫穿中央細脊、下方有柱式山牆門廊、樓層水平線。模型以實際前後深度表現兩組山牆及門廊。

來源照片僅列連結，不放入成果、不重新發布：
- https://attractions.site.nthu.edu.tw/var/file/515/1515/pictures/400/m/mczh-tw700x700_large38204_476810677262.jpg
- https://attractions.site.nthu.edu.tw/var/file/515/1515/pictures/400/m/mczh-tw700x700_large38205_941567177262.jpg

## 近似與缺口
建築深度、側面開間、窗位置與階數為照片估計；高植栽遮擋部分不虛構細節。後面／左側未見完整照片，素面包絡。門口雕塑、玻璃、欄杆及字牌省略。

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

突出上部前塊及柱廊檐下請評估局部支撐；門廊柱直徑3mm，與底座/檐融合。

薄特徵：唯一警戒在z=91.90001mm的山牆尖頂截面，尖角最後0.1mm的小區域窄於0.8mm；下方為連續厚山牆，不是薄壁。切片器可能省略/鈍化尖端，需檢查最後一層，不能保證尖角完整。

## 驗證範圍
18項網格驗證通過；原始STL法線與繞向相符，所有邊連接兩面、頂點環流形、單一連通表面且沒有分離內腔殼，正體積、z=0底面與150mm最大尺寸通過。乾淨暫存目錄重建STL的SHA-256相符，Blender幾何與STL一致；驗證不自動修原檔。

0.2mm間距共460個抽樣高度，所有輪廓閉合。端點數值聚合容差0.0001mm；首層0.100013mm以避共面。0.8mm XY形態開運算標示1層超過0.2mm²警戒，最大差異面積4.77078mm²，含義見薄特徵說明。

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


## 發布補充
請併讀[本輪版本與範圍](../../../audits/amendments/round-status-20261013.zh-TW.md)、[首批薄特徵警示與方法](../../../audits/amendments/layer-audit-20261013.zh-TW.md)及[化工館年代說明](../../../audits/amendments/chemical-engineering-era-clarification.zh-TW.md)。旺宏館保留原幾何；台達館及校友體育館採列印修正版，不重複計數。


## 實際STL正背並排

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 正面<br>![正面](previews/front.png) | 背面（未見部分按詳頁明示簡化）<br>![背面](previews/rear.png) |  |
