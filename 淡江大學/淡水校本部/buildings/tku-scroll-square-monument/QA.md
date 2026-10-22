# 書卷廣場竹卷雕塑：數位QA與真警告

## 原始輸出STL拓樸
SHA256 `4214da7aaacec82c21e9ee9ba9dd0de94995d5c8170654c1b7efaa452d2e62fe`。11292面、5648個exact-coordinate頂點、1連通閉殼，正體積222661.515285mm³。0非有限數／零面積／重複面／非二面邊／方向失敗／頂點link失敗／反向stored-normal。檢查只作完全相等座標記帳焊接，**不補洞、修法線、刪面或四捨五入輪廓**，見[qa-topology.json](qa-topology.json)。

## 全局與局部切層
原始STL以0.2mm間隔加最高點下0.001mm共**641層**；保留全部even-odd輪廓及正面積成分，逐一-0.4mm侵蝕。所有輪廓有效，但**11層／11成分**不過0.8mm薄件篩選，集中於四片斜頂的自由高端；全部真警告保留於[qa-layers.json](qa-layers.json)，沒有薄件豁免。

[qa/local-features.json](qa/local-features.json)直接交集原始STL與有限探測體積：
- 4片×3弧向位置×3高度＝36個板面點，每點3層在**含板法向厚度**的切面檢查，不用平行板面的切層掩蓋厚度。
- 加入5個窄階、外寬台、斜鼓座與薄唇，共132實體切層樣本；16空氣切層樣本。**0佔據不符、0空氣交集體積不符**，所有輪廓有效。
- 中心半徑6mm、跨最高片高度的有限圓柱為真空；相鄰四組曲片最靠近中心線之間的有限空氣柱都通過，非只取模型上方空點。
- 底座以上三個高度各實測**4個互不相連板片截面**。整個模型由底座連成單殼，不代表上方被填滿。
- 36條從模型外出發的實際mesh法向射線量厚；0法向佔據錯誤、0個低於0.8mm。結果只適用抽樣點，不是全表面最小厚度保證。
- 局部**0樣本／0成分**侵蝕失敗仍保留。探測盒有限高度本身可限制可侵蝕寬度，不把這些警告刪掉或當實物缺陷定論。

## 懸挑與實印
raw面法線向下超45°且高於底面共**512面／129.174mm²**，出現在薄凸頂緣下方。板面雖直立，高片與自由上緣仍易晃動／折斷。**未實印、未跑印表機切片器，不保證免支撐或支撐能移除**；這不是橋跨、材料強度或製程認證。

## 格式與可編輯往返
- STL、3MF及mesh.json逐三角座標和順序完全相同；5材質逐面分派完整，沒有上色時另細分幾何。
- lib3mf strict讀取0警告、有效manifold/oriented；更改一材質RGBA另存重開，其餘材質與分派保持，writer座標誤差見[qa/exchange-validation.json](qa/exchange-validation.json)。
- Blender讀回逐頂點／面／材質一致、identity transform。更改1頂點X+0.25mm與1材質RGBA另存重開，其他資料不變；無外部或內嵌來源資產，見[qa/scene-validation.json](qa/scene-validation.json)。
- 4執行緒CPU Cycles、seed0、48samples、1200×1200；5圖均全部頂點入框。保存scene重開front重渲byte一致；只除PNG文字／日期metadata，不改像素，見[qa/render-manifest.json](qa/render-manifest.json)、[qa/render-reopen-validation.json](qa/render-reopen-validation.json)。
- 隔離新目錄重建4核心檔＋5PNG，共9檔byte一致，見[qa/isolated-rebuild.json](qa/isolated-rebuild.json)。
- 獨立來源五圖終審綁STL與PNG bytes／SHA256：[qa/source-visual-review.json](qa/source-visual-review.json)。全部文字身分一致性（含LICENSE）：[qa/identity-validation.json](qa/identity-validation.json)。

來源原拍日期未知；本次只聲明舊完整圈階外觀近似，非2026現況或1986原貌認證。弧心／半徑／斜頂與1.35mm板厚是模型參數，不是實物測繪。
