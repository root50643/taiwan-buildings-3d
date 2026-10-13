# 修後v2數位驗證

原始STL未經驗證器修補。所有指標以交付STL與其SHA鎖定；開孔與屋頂均另作原STL射線檢查。

- 原STL：[validation.json](validation.json)。水密、每邊2面、vertex link單環、原檔法向/繞序、正體積、唯一連通表面、尺寸150mm、獨立重建SHA及Blend幾何一致。
- [contour-validity-check.json](contour-validity-check.json)：z=0.071mm起、0.2mm共750層，節點degree2、個別及合成Polygon均valid，invalid直接失敗，不用buffer(0)或make_valid修補。
- [thin-feature-check.json](thin-feature-check.json)：同750層0.8mm opening輔助篩檢，最大整層面積損失0.897851%，沒有超過1%的層。並非全局最小壁厚保證。
- [component-opening-check.json](component-opening-check.json)：每層每個連通輪廓獨立檢查，opening無元件消失或分裂；最差元件保留97.7867%，位於z136.871mm四個鈍化翹端，其最小外接矩形寬2.080625mm。外接矩形寬不是任意位置的局部壁厚，僅與射線及參數厚度共同解讀。
- [recess-ray-check.json](recess-ray-check.json)：原STL process=False射線實測。兩山牆各3mm厚；脊頂z149.99截線寬5.01mm；z136.99上翹端至少2mm；外簷角垂直厚度4.9mm。另查窄窗退縮、欄板實際穿孔、陽台開放槽底與未知留白面。

薄件校核使用專案已核canonical fail-closed v3為起點（參考原稿SHA256：059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915），本件將1mm取樣改為0.2mm，增加原STL SHA及逐元件保留檢查。量測opening的buffer(-0.4).buffer(0.4)只作用在已assert valid的原截面，不是輪廓修補。

所有預覽為實際STL網格渲染；正背、正立、頂視、屋頂低視角均重生於此成對山牆版。舊四坡錐頂及舊1.083%報告不屬此版本。

本驗證不等同切片或實體試印，亦不宣稱已完成窮盡式自交檢查。屋簷与陽台懸挑需自行檢查支撐。
