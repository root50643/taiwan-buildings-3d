# 大仁行政圖資大樓 A：獨立數位檢驗補充

本補充限 STL `d333eef2bd3b2deeb6493fb582ff671d1c5004bb55424ebb84ed0e689b2526f6`。數位檢驗不等於實際切片或試印；不得推定全域最小壁厚、免支撐或可任意縮小。來源跨年、未知立面與尺度估算等原限制保留。

## 原網格與原截面

4096原三角面／2046頂點的單殼、每邊兩面、原法向與vertex-link檢查通過。488個0.2mm層、793個未round原Polygon的侵蝕與opening皆存活且單核；不修補輪廓、不用理想矩形替代正式opening。整層最大損失0.0572182885895%，整層>1%為0；不能用整層低損遮掩下列局部警告。

39個西南飾帶跨層樣本的最大原opening損失為2.04675524999%，保留97.95324475001%。這不是39支實體柱。指定原面法向至少2.17742156982422mm，直下根到z0的連續實段73.370964050293mm。1861條原三角面射線及32549個高精solid-angle控制通過；另有19局部站點／38射線與744控制。

39警告子集的真轉角0.41mm區外最大損失為0.00970057453859mm²／0.131530774809%。z73.071與73.271原Polygon為4真角＋12精確共線插點的完整矩形，與矩形對稱差為0；原GEOS erosion長邊微斜，形成非四角的細長損失。z73.271南邊最深離原邊0.00529243882566mm，其中0.0000240151061331mm²在原邊0.005mm帶外，不能稱全是純角或全在該帶內。原WKT及正式opening數值保持不變，簡化共線點／理想矩形只作診斷。

全793 Polygon的真角外絕對面積最大另在z42.271/component0，為0.01575696856mm²；該大截面總opening損失僅0.01277719946%，不屬39個>1%警告。不能將警告子集最大值冒稱全體絕對最大值。

## 淺刻側緣與實背根

作者28672點（每面7點）1054短法向首段保留。獨立61440點（每面15點）共有2331短首段：東飾帶471、東玻璃840、南玻璃1020。三族原normal最短分別0.48387145996、0.29032135010、0.29032135010mm，這些原短值及後空氣未被替換。

源幾何為母牆直接淺刻，根方向預先由對應母牆軸減0.15原法向後正規化，不按射線長度挑方向。三族指定連續首實體最短分別87.75312516574、43.87248482435、51.53793536443mm，原面內向dot餘裕0.14834045293。這些是指定背接路徑，不是全向壁厚。2331原normal與背根的83916個全原三角高精控制全部符合，未跨過空氣累加遠牆。

## 完整後段沿面與原旗標

所有61440射線另從原face與barycentric重心以long double重算，首段事件無變。首實段沿面0；第一出口之後35條射線包含122段原三角外表面區間。三站雙側732控制均呈實體內1／外0。15個新增coarse旗標的after探點位在這些真外表面，只保留診斷，不判為air或bulk，也不延長成實體厚度；另45非沿面控制符合。這與作者7點抽樣零旗標是不同抽樣範圍。

獨立相反共面檢查128對候選零正面積重疊，保留容差與採樣範圍。沒有全域厚度保證。

## 重建、預覽與限制

source重建STL逐byte一致，保存Blend原有向幾何一致；不要將重存Blend檔案誤稱逐byte重現。原主正背完整。另封preview overlay修正南北完整立面相機中心，原freeze不改，其他7圖與原STL／Blend保持。修後兩立面已獨立腳本重渲及全頂點入框末核。

原作者qa-binding的passed=true及all_scripts_rerun如實保存，不捏造exit1；它不代表作者自行核准上述限定例外。柱廊、窗凹、簷底與淺刻細節仍需適當支撐、試切片及試印。


主審已接受本文件具體限定例外，正式序號402；遠端發布另行核實。

[components-independent](independent-components-independent.json) · [warning-support-independent](independent-warning-support-independent.json) · [fringe-geometry-independent](independent-fringe-geometry-independent.json) · [dense-independent-summary](independent-dense-independent-summary.json) · [exact-events-summary](independent-exact-events-summary.json) · [flag-boundary-classification](independent-flag-boundary-classification.json)
