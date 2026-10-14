# 數位QA與列印限制

作者八支驗證程式全部exit0，checks全true；外觀已核為跨年有界近似。已完成獨立數位審核；未進行實體試印，不構成印製認證。

- STL SHA256：`01277bf8746a2ae19b5abe792d334756caa2e22db1252f5d586e1951069ec7a0`
- 尺寸：109.09091186523438 × 150 × 29.899999618530273 mm；7854原三角面，原始精確座標單一表面殼，無分離浮件／獨立封閉內殼。
- 原面法向、每邊2面、頂點link單環、水密／正體積全過。原STL不修補、不吞面、不容差焊接。validate_model也採原三角精確座標索引。
- 來源獨立重建STL SHA相同；已存Blend中單一mesh與交付STL三角幾何一致（座標比較至0.00001mm）。
- 原STL 0.2mm pitch、固定z=.071mm起，共150層、967個原Polygon；degree2、每原Polygon及合成有效，erosion(-0.4mm)與opening(+0.4mm)全保留單一Polygon，零消失／分裂。
- 整層最大opening損失0.36227077671700148%；逐原Polygon最大0.9508479905529508%，無一超1%。全層逐構件原面積、損失與連通性見component-detail.json。
- 指定原三角射線97筆法向厚度、67筆根接、5筆淨空；六柱連基座和遮棚、橋欄連橋板、G框及右白牆、主館東框、脊帽根接均過。橋中央淨空及獨立庭院開放有效。
- 最小指定值0.625mm是G背接橫向淺浮雕的Z高，並非獨立薄牆。0.8mm opening為XY形態篩檢，不能稱任何方向皆≥0.8mm；其餘指定射線詳見feature-rays.json。沒有全模型最小壁厚或任意點保證。
- 八張實際STL PNG逐張非空、1200×900，獨立副本重渲染pixels及PNG bytes均相同。正背左右頂、空拍、兩立面均實看；三層README同件正背並排。

## 可重跑證據

run_all_checks.py固定核准STL SHA，依序執行check_raw_mesh.py、validate_model.py、canonical check_thin_features.py、check_all_layers.py、canonical check_layer_components.py、check_component_detail.py、check_feature_rays.py、check_render_rebuild.py。任一失敗立即非零退出。canonical兩支SHA分別固定為059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915、365e437af0d3d6defc2f52adf3e8601ac3643a14e15e03c8c8610b10bb8061a5。

詳見qa-summary.json、validation.json、raw-mesh-check.json、component-detail.json、feature-rays.json與render-manifest.json。所有原Polygon資料保留，不只整層平均／最大值。原面射線只覆蓋明列特徵，不代替全方向壁厚測試。

## 支撐與來源限制

底座朝下；遮棚、連橋、陽台及細凹面需評估支撐，拆除時保護細框／欄杆，勿任意縮小。數位檢查沒有Cura／Prusa工具路徑或實體試印，不能聲稱保證可印／免支撐。高度地形與屋脊有界推估、跨年同側窗面差與西南細窗證據不足詳見sources.md。來源照片與PDF不在公開包。

獨立原面補充：150層967原Polygon皆單核心、零消失或分裂；整層最大0.362270776717%，構件最大0.950847990553%，本次採樣無超過1%項目。97指定射線另以實際三角面法線重核且起點全部位於實體內，67根與5淨空重現。G橫框18指定點的Z高0.625mm是淺浮雕高度，往內連續背接實體至少14.4370831mm，非獨立懸空薄牆；此內向距離也不是全域壁厚。仍保留C跨年窗面差原因未知、地坪3.2m與建築高度有界推估及未試印／支撐限制。
