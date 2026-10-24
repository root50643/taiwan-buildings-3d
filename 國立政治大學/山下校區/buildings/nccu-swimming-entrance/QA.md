# 數位品質檢查與列印限制

**結論：局部、推估外觀模型的數位封閉／材質格式檢查通過；不是整棟復原、實測模型、支撐免用保證或實機試印。**

## 幾何與格式

- 原創 CSG 量體 → conforming 三角化 → STL／3MF／Blender；**1108 vertices、2212 triangles**。
- 毫米整件尺寸 **212 × 32.4 × 31.4**；含展示底座。封閉實體幾何體積約 **122318.994 mm³**，不是切片耗材量。
- 母網格、STL重讀、3MF strict重讀、3MF修改一個材質再寫出重讀：均 **1 shell、watertight、winding consistent、Euler 2、0 非雙面鄰接邊、0 低於1e-8 mm²之退化面**。
- 所有格式的每一三角面頂點配對到母網格後，相同面集合，最大坐標差低於 **0.00001 mm**。這是數位格式精度，不是建築準確度。
- lib3mf **2.5.0** strict：0 warnings、object valid、1 mesh object、1 build item；7 色、材質名稱、逐面材質指派全部吻合。
- lib3mf 真正改動粉褐材質一色 → 預設6位小數寫檔 → strict重開：顏色保存、面索引及材質指派不變；最大坐標改動約 **7.63e-6 mm**，不宣稱編輯存檔幾何 bitwise 不變。
- Blender **4.3.2** fresh-process讀回：坐標、面索引、逐面材質、7材質槽核驗；**0 file/packed images**。真的修改材質、另存、重開亦保留改色且幾何不變。臨時編輯檔不進交付。

獨立模型審查：[independent-review.md](qa/independent-review.md)，結論為本明示局部近似範圍 PASS，無 blocking；不涵蓋未來發布／備份。

機讀證據：[geometry-qa.json](geometry-qa.json)、[format-geometry-qa.json](qa/format-geometry-qa.json)、[3mf-strict-roundtrip.json](qa/3mf-strict-roundtrip.json)、[blend-readback-edit.json](qa/blend-readback-edit.json)。

## 切片／細節篩查

實際使用**匯出的 STL**作平面交線與閉合多邊形分析：底座朝下，0.2 mm層高，以0.01337 mm錯位避免恰落共面面上；**157層全數閉合有效，每層只有一個相連區域，無新增懸空島**。

45°逐層外擴的簡化支撐篩查在 **5層**標示新增外伸：入口遮雨棚、下層通風凹槽頂、上層玻璃凹槽頂、兩道上方深色淺槽頂。這些沒有被隱瞞成「列印無警告」。

| 100%模型特徵 | 尺寸 | 提醒 |
|---|---:|---|
| 底板 | 2.4 mm | 大長邊仍須依材質／熱床處理翹曲 |
| 上層窗框／入口門分隔 | 0.9 mm | 非懸空薄片，後面連接實體；縮小會消失 |
| 遮雨棚 | 厚0.9 mm、外伸3 mm | 請在實際切片器檢查局部支撐或橋接 |
| 玻璃淺凹 | 0.6 mm | 為浮雕表意，不是透明窗或中空室內 |
| 深色上帶淺槽 | 深0.45 mm、高0.8 mm | 小尺度時可能被線寬／層高吃掉 |
| 入口階 | 高約0.667 mm、踏面1.1 mm | 簡化6階，不是現地精確階數 |

整件長212 mm；若兩端各加5 mm brim即需222 mm，會超過標稱220 mm床寬，請確認實際可用列印區、夾具與裙邊空間。不要為了塞進床面就直接縮放而沿用原細節檢查。

參照0.4 mm噴嘴／0.2 mm層高僅為篩查假設。**未執行指定 Cura/Prusa/Orca 切片器、未產生 G-code、未試印、未做樹脂排液／吸附／收縮驗證，也沒有全面物理最小壁厚認證。** 幾何檢查不替代機台、線寬、材料、橋接、支撐、附著與後處理設定。50%縮放會把0.9 mm變成0.45 mm，不能直接沿用100%結論。

機讀證據：[slice-feature-screen.json](qa/slice-feature-screen.json)、[157層逐層數據](qa/slice-layers.json)。

## 來源一致性與視覺檢查

已實際看原始照片700/701、native平面圖703/704及最終入口正面、入口右斜視、池廳切面、頂視、短端局部五圖。核對入口翼窄長比例、兩層窗帶／深色頂帶、暖粉褐正面、深色勒腳、入口位置與兩處局部包覆量體。未見高池廳、未知屋頂列板、假的方位或具體年份標籤混入。

可接受的**明示簡化**不等於來源證實：兩個局部樓梯包覆量體的完整外皮／高度、規則窗格與通風口節奏、6級前階、服務翼頂蓋、未觀測表面的封閉。真實坡道可見但配準不足，故省略。中性切面不是後立面。色碼不代表經校色材質。

## 可重建性與檔案內容

清空輸出目錄重新執行幾何 builder，`mesh.json`、`model.stl`、`model.3mf`、`construction.json`、`geometry-qa.json` **五檔 SHA-256逐位元相同**：[geometry-rebuild.json](qa/geometry-rebuild.json)。3MF ZIP使用固定時間戳，無網路或來源影像依賴。Blender重建以語義一致為驗收，不承諾整檔位元相同。

模型識別碼為 `nccu-swimming-entrance`。交付僅含原創模型、材質、預覽、重建程式、來源 metadata 與驗證資料；不含來源影像、私人比較裁圖、`.blend1`、中間圖或臨時改色模型。

## 0.1.1 場景可攜性

可編修場景的輸出與檔案瀏覽目錄改為包內相對路徑，固定字串尾端亦清除原本位置殘片。幾何、7個模型材質、展示地板材質、相機、燈光與五張交付預覽不變；Blender重存自動移除一個沒有被任何物件引用的預設空材質。新舊場景各自完整1600×850／64 samples重新渲染，解碼後像素完全相同；PNG時間metadata不同，未宣稱重渲染PNG檔案hash相同。此比對是新舊同相機渲染彼此比較，不是把重渲染與交付短端視圖混為一談。見 [path-portability-delta.json](qa/path-portability-delta.json)。

[0.1.1獨立差異審查](qa/independent-delta-review-0.1.1.md)：PASS；獨立完整重新渲染的像素一致，並確認固定路徑字串尾端無原位置殘留。
