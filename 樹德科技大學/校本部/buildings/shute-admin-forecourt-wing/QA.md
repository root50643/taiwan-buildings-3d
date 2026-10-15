# 作者 QA 與限定診斷

> 復原修訂 v3：原 STL 與建模程式已從原始內容恢復，獨立重建 SHA 完全一致。缺失的渲染程式、Blend 與四張預覽重新製作；數值檢查程式與 C++ 輔助程式保持恢復的原位元內容並重新執行。新的彙整閘門與文件另作版本記錄，v3 獨立覆核與發布決策另行記錄。恢復、重產與新寫檔案的區別見 [recovery-provenance.json](recovery-provenance.json)。

本檔說明作者證據；獨立覆核與發布決策另行記錄。沒有以「需要支撐」忽略薄連接，也沒有將直接根部證據改稱全方向最小壁厚。

## 強制幾何與重現檢查

- check_raw_mesh.py：直接讀二進位 STL 保存法向及三角面，精確座標建索引，檢查每邊兩面、反向邊序、頂點 link 單環、單一表面、正體積及最長 150 mm；不 repair、不 round、不丟面
- check_component_detail.py：process=False 原網格，固定 z=0.071 mm 起、間距 0.2 mm；共享邊固定方向求未四捨五入交點；輪廓 degree=2，個別與合成 Polygon 均須有效；每個原 Polygon 的 0.4 mm erosion 及 opening 均保留一個 Polygon，且個別面積損失不超過 1%
- check_negative_controls.py：暫存副本故意翻面、注入個別及合成 bow-tie，三種皆必須非零退出
- check_reproducibility.py：獨立子行程重建 STL SHA；重新開啟保存的 Blend，比對精確且保留三角面方向的幾何；再由實際 STL 獨立重渲染四張圖，比對像素及 PNG；只移除 Cycles 可變執行時間的文字 metadata，原始 IDAT 像素資料不變

## 未被抹去的原始法向失敗

check_dense_surface.py 保留所有原始面各十個取樣，原始結果刻意仍為 failed／退出碼 1：

- all_first_chords_ge_0p8mm = false，1,977 個短段，最小約 0.01331 mm
- all_fixed_direction_parity_codes_expected = false，3 個旗標

原始全部取樣在 dense-original.csv.gz；短段原三角形、原法向、全部交點及原 C++ 記錄在 dense-short-samples.json.gz；摘要在 dense-short-chords.json。這些結果與最終 STL SHA 綁定，不能用另一方向的長距離取代原短段。

## 限定淺凹紋根部證據

check_drum_relief_roots.py 對每個短段逐點檢查來源範圍、原第一段實心、其後空氣、進入原表面的方向、連續第一根部、第一交點為離開母體及多個近根部材質控制。每條原法向及根部的完整交點均保留在 drum-relief-root-samples.json.gz。

只容許兩個限定區域：入口前半圓的 0.55 mm 玻璃淺凹紋，以及 283–305 度的 1.0 mm 門片淺凹紋。門片標記邊界額外包含 0.1 度、不到 0.05 mm 弧長的相鄰框邊，只用於分類；不改幾何、不放寬根部連續性或材質判定。

固定根部方向朝實際實心鼓形母體的水平徑向內側。若原法向與該徑向的內積小於 -0.05，直接使用水平徑向；切向凹紋邊面才加上固定 0.15 原法向內側偏量。不是搜尋最長方向。check_drum_root_intervals.py 另外將每條完整第一根部及後續區間對全部原三角面做邊界篩檢，並以 11,862 個全原網格 winding 控制驗證沿根部的五處（含中點）與離開後空氣。所有樣本最短連續根部約 24.943 mm，原短段及最大後續空氣間隙仍明列。此證據只支持「薄表面凹紋有直接實心母體」，不支持所有方向均厚於 0.8 mm。

作者曾因檢查結果實際加深翼片根部、加寬帶狀窗轉角留實、加厚欄緣截斷端與重畫入口門框，未直接豁免這些真實薄接合。

## 原三角形邊界證據

check_full_boundary_intervals.py 將全部 57,340 條原法向線對全部原三角面檢查，沒有第一實心段沿邊界；5 條線的後續區間沿真實外表面，共 10 個三角面區間。使用 long double 嚴格交點、原平面／重心座標、兩側 1e-6／1e-5／1e-4 mm 偏移及全原面 solid-angle winding，共 250 個控制。沿表面的區間不算實心，也不冒稱純空氣；check_flag_boundaries.py 將 3 個原旗標的確切探針對應到上述區間。

## 閘門與報告

validate_model.py 及 run_checks.py 強制零未分類短段、所有直接根部／空氣／邊界控制通過、原網格與逐截面檢查通過、檔案重現及所有 SHA 綁定一致。診斷自身的 false 不會改寫成 true。限定根部／邊界處理仍需獨立覆核，且不是實際切片或實體試印。


## v3 彙整閘門負控制

check_v3_gate_controls.py 只在暫存副本依次注入未分類根部、抹去原失敗狀態、錯誤 winding、渲染來源改動及 STL 位元改動；五案均須使新 validate_model.py 明確 failed 並非零退出。這不取代原數值幾何檢查，也不新增任何薄壁豁免。
