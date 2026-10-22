# 56亭數位QA與保留警告

## 最終原始STL（沒有修網後冒充通過）
SHA256 `d132008d323bc951b97a9c49ca25c2df82bdc20ffc5f7da12cec30a5cc422220`。8894三角面、4291個exact-coordinate焊接頂點；正體積85147.708411mm³、1連通閉殼。0非有限值、0零面積、0重複面、0非二面邊、0方向失敗、0頂點link失敗、0逆stored-normal。只作座標完全相等的記帳焊接，未補洞、刪片、修法線或四捨五入輪廓。見[qa-topology.json](qa-topology.json)。

## 全局切層不是免支撐認證
以原始STL每0.2mm加最高點下0.001mm共**732層**；even-odd所有輪廓保留，逐正面積成分做-0.4mm侵蝕（0.8mm門檻）。所有輪廓有效，但**13層、23成分不通過薄件篩選**，沒有薄件豁免或刪除。包含斜管端、招牌／支架掠切、鋼梁頂端及單坡PC最高端。這些真警告全部保存在[qa-layers.json](qa-layers.json)。

## 局部實體／空氣／法向厚度
[check_features.py](check_features.py)直接與raw STL做有限體積交集：六柱／六腳座、開放長短側、架高平台下空氣、低端斜接切邊、梯形平台寬窄比較、四階台階、兩榀木桁架三角孔、PC法向片段及木斜腹材法向片段。

- 102實體樣本、63空氣樣本；0佔據不符、0空氣體積不符。所有局部輪廓有效。
- 局部侵蝕薄成分0，這是所列有限樣本結果，不能推廣為全模型厚度通過。
- 6條實際mesh法向射線：5條避開格肋量得PC片約0.83164–0.83165mm；另1條故意穿過格肋量得約2.09322mm，明確區分，不拿格肋厚度冒充薄板厚度。
- raw面法線向下超45°且高於底面共**1169面**、面積28345.405mm²；逐材質記錄於[qa/local-features.json](qa/local-features.json)。橋跨、強度、支撐移除及印表機切片沒有實測。

## 格式與可編輯性
- STL／3MF／mesh.json：三角座標、順序逐一相同，沒有為上色重新細分。
- lib3mf strict讀入0警告、有效manifold/oriented；8材質sRGB／alpha與逐面分派符合palette。修改1材質後save/reopen，其他材質和分派不變；writer六位小數座標誤差上限見[qa/exchange-validation.json](qa/exchange-validation.json)。
- Blender開啟交付scene：逐頂點／三角／材質正確、identity transform；修改一頂點X+0.25mm與一材質color/alpha，另存並重新開啟，驗證編輯保留及其他資料不變。無外部貼圖／字型或內嵌腳本。見[qa/scene-validation.json](qa/scene-validation.json)。
- CPU Cycles固定seed0、48samples、1200×1200，5實際mesh視角全部頂點入框。交付scene重開front重渲PNG逐byte相同；只剝除PNG文字／日期metadata，不改像素。見[qa/render-manifest.json](qa/render-manifest.json)、[qa/render-reopen-validation.json](qa/render-reopen-validation.json)。
- 獨立空白目錄重建STL／3MF／mesh.json／palette.json及5張PNG，9個檔案逐byte一致；見[qa/isolated-rebuild.json](qa/isolated-rebuild.json)。
- 獨立來源五圖終審綁定STL與5張PNG的bytes／SHA256：[qa/source-visual-review.json](qa/source-visual-review.json)。

## 文件身分一致性

[verify_identity.py](verify_identity.py)逐一讀取包內所有文字文件，拒絕前案名稱殘留；八個主要來源／授權／生成文件必須出現56亭身分，school/campus/slug另作一致性斷言。[qa/identity-validation.json](qa/identity-validation.json)記錄受檢文字雜湊。

## 未完成的製造驗證
**未實印、未使用印表機切片器、不保證免支撐。** PC材質顯示alpha112不是可變透明網格；STL無色且透明板仍為封閉實體。不得把拓樸、格式或有限空氣測試稱作物理列印認證。來源原圖未公開於本包；授權只涵蓋可處分的自建輸出權利。
