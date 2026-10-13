# 原始幾何QA方法

所有檢查針對交付model.stl；不以repair後的模型代替。載入時process=True只合併STL同位置頂點供拓撲統計，saved normals及原三角形另直接解讀二進位STL；射線以process=False讀取原三角形。

輪廓與opening均採0.2mm、起始0.071mm避開共面頂點。單獨輪廓與合成Polygon有效性以assert強制；無buffer(0)、make_valid或invalid fallback。

opening程式源自已核canonical fail-closed v3（上游SHA256：059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915）。本版只將pitch由1.0改0.2，並保留canonical共享邊交点原精度，刪除6位小數取整。buffer(-0.4).buffer(0.4)僅做合法輸入的opening量測，不修補invalid輸入。

首輪因窗框与凹窗邊界重合，58.271mm層出現自相交，驗證器按規定非零退出；未跳過該層、未修補。已回到建模來源把橫框加寬、框背加深並保證材料體積重疊，重新輸出STL後全610層通過。該失敗版未凍結或交付。

本模型屬局部外觀近似。背面的素平面是人工裁切。opening、單殼與射線不構成實體試印、完整最小壁厚、全面自交檢測或切片器工具路徑證明。
