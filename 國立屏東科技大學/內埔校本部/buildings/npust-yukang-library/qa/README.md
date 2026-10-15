# 原始數值與重現

原STL不repair。每原Polygon的WKT/開運算結果、真角與0.6mm區外結果均保留。樣本數不能當真構件數：3179高損跨層樣本不是3179根柱；2996短段點不是2996根細框。

- layer-component-check.json.gz：原作者JSON逐byte無損gzip，3973原Polygon。
- warning-corners-original.json.gz：3179原WKT與真角辨識點及精確損失。
- warning-original-normal-probes.json.gz：每高損原Polygon兩代表實法向，6358 probes。
- root-sections-original.json：局部原截面與各自高程距離，保留部分支承。
- dense/all-original.csv.gz：49742原始密點CSV，無改動首段或旗標。CSV裡 inf 表示該方向後續沒有命中，即無界外部air；不是實體長度。
- dense/short-original.csv.gz：原CSV中2996短段行，數值原樣保留。
- 公開JSON一律可嚴格解析；沒有後續命中的air改用null，其無界air語義由本說明保留。portable-json-manifest.json列舊/新解壓SHA，有限數值不變。

先執行主目錄build_model.py；check_layer_components.py重算0.2mm原截面。qa/check_warning_corners.py、check_warning_normals.py、check_roots_sections.py重算局部證據。qa/dense/run_dense.py以原二進位STL轉double三角輸入並跑自含C++，逐行gzip保存，不需保留巨大未壓CSV。其後classify_short.py與check_backed_mullions.py重算薄框相反出口與既定背牆方向第一根。需g++、Python依賴與Blender。

診斷使用原面精確索引；Manifold只作射線加速，並逐三角確認映射回同一原STL面集，不將其結果代換交付幾何。7點抽樣不是全方向/全連續表面最薄證明。總檢查保留作者送審時有限例外的原false；本輪限定裁定另見上層INDEPENDENT-AUDIT.md，不以改閾值造成假全通。
