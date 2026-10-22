# 驗證與列印限制

- 原始STL不修補、不刪退化、不重排法線，只exact-coordinate welding統計：16462三角、單閉殼、正體積；邊/頂點鏈/繞向/法線、重面與零面檢查見qa-topology.json。
- 全局290個0.2mm水平切層與top−0.001mm均有效；205個截層有不足0.8mm水平小島，所有警示在qa-layers.json保留。這不是最小壁厚、支撐或實印通過。
- 實際STL空實點、無遮斷射線及局部切層見qa/feature-validation.json；廊下補充圖不切網格。
- strict lib3mf材質改動/存檔/重讀、Blender真頂點/材質改動/存檔/重開，分別記錄於qa/exchange-validation.json及qa/scene-validation.json。
- 原Blend重開渲染與乾淨目錄4 core＋5PNG byte一致，見qa/render-reopen-validation.json及qa/isolated-rebuild.json。獨立來源/幾何終審以qa/independent-model-review.json為準。
- 需支撐：東廊與南端拱、北接段拱與梁板、雨庇、簷口；小落水管、窗格、瓦紋非承重件且需微型列印設定。沒有G-code、試印或免支撐保證。
