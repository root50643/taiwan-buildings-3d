# 國立中央大學綜教館｜有限正面彩色外觀

## 原模型與鎖定圖不變

446頂點、896三角面、transform與150×100×70.8mm完全保留；僅原三角面材質索引改變，未新增頂點／構件／孔洞。原STL、OBJ、scene.blend、建模與原預覽腳本、三張原圖與QA不動。兩README第一章加入獨立彩圖，未改首頁／校級代表選圖。這是綜教館／語言中心，非新教研綜合大樓。

## 官方外照與時間限制

- [校方校友通訊第85期校史回顧PDF](https://in.ncu.edu.tw/alumni/enews/no85/page2.pdf)：第1頁上方大外照，圓角左梯核、懸出上翼及雙高柱與原模型一致。照片拍攝日未載；文字1985完工、1988獲獎不是照片年份或原始塗裝證據。
- [校方無障礙地圖](https://love.adm.ncu.edu.tw/NCU_counsel/NCU-barrier-free/)的GEB／綜教館項目與[內院圖](https://love.adm.ncu.edu.tw/NCU_counsel/NCU-barrier-free/images/GEB/1.jpg)只作身份／內院佐證，紅磚不得泛套外殼。
- 原sources.json中的Commons圖本次一般下載403，已停止，未另路繞過或當作本次已讀色證。原幾何研究引用照與其2013日期原樣保留，不冒充本次取得。

## 配色與排除

灰綠梯核正面與圓角前緣、淡鮭粉灰前翼與可見下右牆、淺灰既有框／前簷、暗灰綠原凹窗背、灰綠既有入口柱及廊板、灰前階。僅近似sRGB展示色，不是校正測色、色票或材質鑑定。窗用不透明暗色代理，不模擬反射／窗簾／玻璃透光。

未知側後、屋頂與底座中性；高低屋頂材質不推定。大面沒有原幾何分界的照片細橫帶／磚縫／欄杆不切新面或造紋理；不加招牌金字、空調、單車、樹、道路或內裝。內縮入口仍不強稱玻璃。照片與粗化原模型比例差異不是此次補色能修正的項目。

## 重建與驗證

保持同目錄原scene.blend與model.stl，使用Blender4.3.2執行：

    blender -b -t 1 --python-exit-code 1 -P build_appearance.py

輸出appearance.blend、appearance.3mf、appearance-materials.json與appearance/五張圖；不覆蓋原scene或previews。新PNG移除text metadata。3MF保留原頂點與每面同色base material，未拆mesh；未指定AMS／耗材／機台映射，切片器是否支援須自行確認。

獨立geometry/material等價、逐視圖review與乾淨重建結果位於appearance-review；BLEND以語義驗證，不宣稱容器byte相同。原模型0.2mm共354層閉合及薄特徵抽樣等限制見原README／報告；XY形態開運算不是全向壁厚保證。入口懸板、雙層廊道、框上緣仍需切片與局部支撐評估。未實體試印，不宣稱免支撐或保證可印。

來源照片/PDF／私人工作資料不隨包公開。
