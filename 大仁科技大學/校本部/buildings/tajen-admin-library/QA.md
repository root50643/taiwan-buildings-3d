# 作者 QA 與審核邊界

所有報告針對交付原 STL；詳 qa-binding.json。狀態為 author_hard_checks_pass_independent_exceptions_pending。

- validation.json：原4096面／2046精確頂點、單連通水密殼、edge2及vertexlinks、原法向與面積、無重面／內閉殼；源重建、Blend、9PNG exact。
- detailed-component-check.json：process=False、不round交點、488層／793原Polygon，半徑0.4侵蝕與開運算全部保留單一構件；39損失>1%的原資料逐筆保留。
- thin-feature-check及layer-component-check：既有canonical輔助篩檢使用process=True與round6，不能替代上述無repair原面版本；兩口徑分開。
- dense-samples.csv.gz：4096×7=28672原面點，直接gzip保存原數值；dense-sampling-binding保存原CSV及gzip SHA。1054短首段不刪除，四內外控制零異常。
- backed-relief-roots.json：三族1054全量源定位，原短normal／air與另背根方向分列；每根5近起點控制。這是局部背接證據，非所有方向厚度。
- support-paths.json：55條柱、屋面／翼、階梯實根與9柱廊真凹深射線。
- warning-post-check.json：39西南飾帶原法向caliper與到底根，真角外非零損失。
- coplanar-original-face-check.json：4096原面皆軸向，412保存坐標平面群、16852bbox候選對，正面積共面交疊零。不是一般任意斜面全自交證明。

局部>1%損失及淺浮雕短首弦須獨立審核與根裁定；報告passed僅代表各檢查明列條件，並不自動批准局部例外。未試印，未宣稱全域最小壁厚。

## 相機overlay

原立面各228點出框（其中215點高於底座），修正兩相機中心後全2046點入框；elevation-framing-check.json記錄邊界。執行 `blender -b -P check_elevation_framing.py` 可獨立重算。source/STL/保存Blend未替換；validation重驗源、相同Blend幾何和9PNG。其他幾何QA沿用同一STL SHA原結果，沒有冒稱重跑密點。
