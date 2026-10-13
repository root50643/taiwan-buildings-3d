# 驗證方法與限制

檢查原始交付STL，無repair。原saved normals直接由二進位讀出，拓撲檢查僅合併同座標頂點；射線用process=False保留原始三角面。

0.2mm輪廓及opening均從0.071mm起，所有節點degree2、每一Polygon與合成Polygon有效性強制assert。canonical fail-closed v3上游SHA：059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915。本版把1mm抽樣改0.2mm並使用不取整的共享邊交點；buffer(-0.4).buffer(0.4)僅在valid輸入上量測opening，無buffer(0)、make_valid或invalid fallback。

13條原三角面射線只驗證模型的真空隙及高差，不代表實際建物尺寸。頂部人工裁切，沒有把未知屋面做成實心全館方盒。低視角source-angle仍是actual STL，不是示意重畫。

沒有實體試印、全面最小壁厚、全面自交及切片器路徑驗證。門廊頂板跨度需依機台與材料設定支撐。
