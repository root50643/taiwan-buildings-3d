# 成大未來館現存前棟：限域外觀

僅既有模型 **511 面 / 2030.7200518417367 mm²** 使用來源支持的非透明顏色代理，其餘 **4533 面維持未查證中性**。不是整樓上色、實測材質或2026現況普查。

- [五材質3MF](ncku-future-venue-front-appearance.3mf) · [可編輯Blend](scene.blend) · [重建原始碼ZIP](rebuild-source.zip)
- [前](previews/front.png) · [左](previews/left.png) · [右](previews/right.png) · [後](previews/rear.png) · [頂](previews/top.png)
- [同角度單色對照](previews/mono-front.png) · [來源及限制](SOURCES.md) · [授權](LICENSE-NOTICE.md)

372上中窗背、120淺色低窗背、2次入口門背、17突出白色U框正面。全部三點位於各個有限平面矩形並驗證實際叉積法線；白框同材質角面重疊只計一次。5044原三角形坐標、順序、朝向及STL bytes完整不變。大牆／共面細框、側背、屋頂、底座、實心梯側與底、主入口底梁、次門門檻及未選reveals保持中性，不補玻璃／窗櫺，不復原已拆T形後翼。

## 非製造修復／非可直接列印
原製造QA完整保留為歷史記錄：validation passed=true；170個0.2mm截面；34薄層形態開運算無大於1%損失、最大0.000683504635691893。形態運算不是全域壁厚保證；本次沒有重跑歷史製造QA、沒有完整自交／切片／實體列印驗證。原約28mm入口跨度可能需支撐，0.6/0.9mm格框可能簡化。前棟深度、背頂、階數與三子列窗仍為原粗略模型，不是全樓geometry升級。

## 重建
安裝 source/requirements.txt；本目錄上層需原 model.stl，執行 source/build_appearance.py、source/verify_exchange.py，再以 Blender 執行 source/render_appearance.py 與 source/verify_scene.py。測試包含strict 3MF零警告、真材質修改存讀、Blend真頂點及真材質修改存讀、交付Blend重開重繪；解包原始碼clean重建3MF/map/palette/五張PNG完全一致，Blend只主張語義一致。
