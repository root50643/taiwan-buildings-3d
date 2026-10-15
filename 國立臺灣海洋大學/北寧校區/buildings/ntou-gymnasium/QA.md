# 原始幾何與可重現檢查

所有資料指向本包model.stl；不以process=True、repair、buffer(0)或取最大Polygon掩蓋問題。SHA見qa-summary與每份報告。

- raw-mesh-check.json：原binary、原法向、精確座標邊、頂點link單圈、單表面、正體積與150mm。
- opposing-faces.json：全部原面AABB候選、相反共面正面積重疊有限精度篩查；不是全域自交定理。
- component-detail.json：210層、432每原Polygon，60角損strict false/exit1，均保持單核。24端肋+36頂肋；峰面積2.681868669695249mm²、loss0.13815224151264724mm²、5.151342534917864%。
- true-corner-mask.json：原WKT、與前層交集；僅mask去共線simplify1e−5，原opening不換。警告真角0.41mm外最大1.1247493746173426e−19mm²，不寫絕對零。全層保存可覆核。
- dense-original.csv.gz / dense-short-chords.json：每面10點共56300；1227短、8原flags，strict false/exit1。最短3.35533604338e−5mm。
- dense-corner-backing.json與vertex-roots.json：早期只用同法向平面/最近頂點的補證失敗原值保留，不用其遠邊替代真根。
- curved-patch-roots.json.gz：1227短點實際入/出面之內向合成根，原facet adjacency局部路徑；全部路徑三角距點≤1mm、法向差<12°。真邊距max0.7826560592651362mm、normal差max5.288988101219061°、首連續根min6.653930959847953mm。每筆7個longdouble全原面solid-angle控制全過，非跨空氣找背牆；原作者數值保留，獨立15點覆核與限定裁定見補充。
- root-full-intervals.json：全部1227根第一段與完整下一段對所有5630原三角檢查，零正長度沿面。
- boundary-witnesses.json.gz / exact-source-boundary-events.txt.gz / all-boundary-overlaps.csv.gz：全56300法向第一段及完整下一區間，12後區間射線、24原三角沿面段，第一段零沿面。exact-source從原面權重longdouble重建（centroid真1/3），避免double位移誤判。600控制中528非邊界全過，72面上數值只診斷。
- flag-winding.json原結果保留；check_flag_boundaries.py以精確after位置分類全部8 flags為正長度外表面，不能把其中7個數值吻合叫真空氣或正常parity誤報。
- designated-roots.json：162原指定射線數值通過，但獨立核對發現31筆名稱與實際命中錯配；不以錯名宣稱覆蓋，原值保留，真正目標86點及上下根補證見獨立報告。有限點不是全域壁厚。
- validation.json與render-manifest.json：獨立源重建同SHA、Blend原面幾何、全部7PNG同bytes及pixels。局部圖有意裁切，front/rear/elevation/top保留全館。

獨立覆核與本次有限例外裁定已完成；原嚴格結果保持不變。未試印，需支撐評估與拆除小心；不得任意縮小。

[獨立修版覆核與可重現證據](INDEPENDENT-REVISION-AUDIT.md)
