# 中央工五B棟增建翼｜有限實照彩色增補

## 範圍與原幾何保留

只研究2014–2015 B棟增建狹長翼，非舊AB圓入口複合樓、獨立C棟或工五全區。原1099頂點／2338三角面／transform／150×63×67.8mm不變。原build_model最後x鏡射已保留；材質在最終mesh定位，不二次鏡射／移動／新增頂點。

原STL、OBJ、scene.blend、建模／預覽script、三張原預覽及QA全部保留。雙README第一章增加獨立彩圖，不換首頁／校級鎖定圖，舊單色圖不冒稱已上色。

## 直接讀到的實景

[工程project23頁](https://www.infinitespace.com.tw/public/acu/commissions/23)描述中央工五B棟增建、劉致錚建築師及永祥營造，工程2014-05至2015-11；此工程期不是照片拍攝日。實讀原sources.json所列e54454b4-9ffb-40c5-b06a-5ada41ee0bff_1774514222.jpg與591b2b53-1ac6-42cf-8fe0-8140549348fb_1774514247.webp兩張已建實景，支持兩長向立面。檔名數字／頁面更新均不是拍攝年，不稱完整2026現況。

第二張右邊亮白相接舊樓不是本增建模型，不能將其亮白表面套到新增條翼；截斷接合端維持中性。

## 低飽和材質近似

深框格與原柱梁淺灰米、後凹牆灰褐、原窗背暗灰綠不透明proxy；另一長面淺灰牆與較深灰既有水平遮陽／核心直柵。低飽和多灰仍是有據外觀，不為追求鮮豔把原建物亂染。照片光線與曝光不同，色值未校正，不是官方色票／實測材料。

原斜蓋可見表面用淡灰藍近似，但原模型只是連續坡帶，不宣稱精確光電陣列／模組數／光電材質。未知平屋頂、窄端、接舊樓截面與底座中性。原深框與凹部不添加真玻璃透光／反射，不造百葉細縫、設備、樹木、電線或汽車。

建築內部、端部接合與全深估計等限制保留；材料配置不修正原量體粗化。

## 重建與驗證

Blender4.3.2，原scene.blend、model.stl與build_appearance.py同目錄：

    blender -b -t 1 --python-exit-code 1 -P build_appearance.py

另產appearance.blend／appearance.3mf／appearance-materials.json／五張appearance圖，不覆蓋scene或previews。新PNG移除文字metadata；3MF沿用原每面同色base material，不改geometry，無AMS／耗材／機台配置，切片器支援需個別核。

獨立geometry／materials／3MF與逐圖／clean rebuild報告見appearance-review；BLEND只語義驗證不稱容器byte一樣。原抽樣QA不是完整壁厚／切片／試印保證；深框、遮陽細條、坡蓋與窗上緣仍需檢查支撐及薄特徵。未實體試印，不保證免支撐可印。

來源照片／PDF及私人研究資料不公開隨附。
