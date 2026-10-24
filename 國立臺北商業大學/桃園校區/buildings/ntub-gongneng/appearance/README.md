# 北商桃園公能樓：既有PV頂面與正面雙塔窗的有限純色外觀

既有模型有限辨識改善，非新增建築、全樓彩色復原或新測量。僅144完整原面／5651.247314568758 mm²：48既有中央PV頂三角與96正面雙塔玻璃背面；5150原中性面與原材質保留。

- [3MF](ntub-gongneng-appearance.3mf)／[可編輯Blend](scene.blend)：5294原三角、2567原頂點，座標及有向面exact。原STL完全不改。
- [正面](previews/front.png)・[左側](previews/left.png)・[右側](previews/right.png)・[背面](previews/rear.png)・[俯視](previews/top.png)
- [可重建來源ZIP](rebuild-source.zip)：解壓後依序python appearance/source/build_appearance.py、verify_exchange.py，Blender -b --python appearance/source/render_appearance.py、verify_scene.py。numpy／lib3mf2.5.0／Blender4.3.2；model.stl和original-scene.blend保持同層。

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 正面<br>![正面](previews/front.png) | 左側<br>![左側](previews/left.png) | 右側<br>![右側](previews/right.png) |
| 背面<br>![背面](previews/rear.png) | 俯視<br>![俯視](previews/top.png) |  |

原Blend唯一Warm stone preview only材質datablock真保留，linear RGBA不改；3MF原色是最近8-bit sRGB換算，不是新判斷的實景色。新增低飽和、不透明深藍灰PV及較淺灰藍玻璃代理，非光譜測色、透明玻璃或反射模擬。交付不含來源照片／貼圖。

## 嚴格有限範圍
只按source/source-selection.json三個有限域，以每個原面的全部3點及實叉積法向驗證，容差3e-5mm；不採只看中心點、不切面、不重建網格。PV原頂平面z55.1，x−35..35、y−29.5..41.5；前塔窗背面y−53，xcenter±52±7.7、z7.2..55.2。PV48原三角不是48真實太陽能板！70×71mm、4×5淺刻組是既有列印粗化，不是實景板數或新核定精確PV邊界。251×188來源只支持中央PV存在及大概位置，不證明周界、排數、斜率、支架高度、遮蔽或整個現況屋頂。此次只賦予既有近似平面材質，不修正或認證其幾何。

所有PV刻溝／垂直邊牆、機房、檐蓋、女兒牆、磚／白牆、上層開廊、入口與雨棚、其他窗、側背與未知面均不染不改；不外推鄰棟弘毅樓。界線是證據／顯示限制，不是新增真實材料縫。純色辨識收益只在這兩類既有特徵，不宣稱2026現況。

## 原幾何與製造限制完整保留
全部22個原始文件另存私有原始完整備份，含原STL、Blend、README、QA與來源，位元不改。原150×150×68.69999694824219mm是模型尺度，不是建築實測。原估計翼深、檐坡、高度、比例、中央PV及機房細節仍近似，未拍側留白、不虛構天井，不是室內模型。

原validation passed=true，單連通表面、體積792738.4242823463mm³、底接觸22500mm²。歷史344輪廓層（pitch0.2、zoffset0.071）closed/valid不等於完整自交／切片證明；69薄篩層（pitch1.0、zoffset0.071）0層>1%openingloss，maxfraction0.0007231792786070074＝0.07231792786070074%。0.8mm參考／形態半徑0.4是抽樣輔助，不是最小壁厚或實印保證。原凹口ray通過只證明模型射線幾何，不證明真實建築深度。本輪不重跑或冒稱新製造QA。開廊、屋檐、雨棚、凹口懸垂、細框、支撐、噴嘴和工具路徑警示全保留；未實體試印，未Cura／Prusa路徑驗證，沒有全域可列印保證。

實做3MF strict import＋頂點／材質edit-save-reopen、Blend真edit-save-reopen及5全物件圖；source ZIP cleanextract實建core與5圖byteexact。SDK隔離編輯副本float32微量化見qa/exchange-validation.json；交付STL／3MF座標仍exact。技術完成不代表第三方權利清除。

來源及權利見[SOURCES.md](SOURCES.md)、[LICENSE-NOTICE.md](LICENSE-NOTICE.md)。
