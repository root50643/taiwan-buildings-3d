# 清華大學創新育成中心 — 限域外觀配色

本層是既有近似模型的附加材質，不是新建築套數、全棟材質復原或現況實測。原 STL、8666 三角與面序完全不變。依九典官方完工作品照片，只選可完整分離的湖側高棟磚框正向面 12 面（973.47537 mm²）與低翼深灰簷板前臉 2 面（290.40009 mm²），合計 1263.87546 mm²。

**磚框配色刻意不完整**：內退角面、內側窄框與其他未確證範圍維持中性，不能把這份配色視為完整磚牆位置圖。玻璃、彩色葉片、草頂、水平簷頂／底、側背及下層未知面全部中性。未補磚紋、細金屬收邊或玻璃透明材質；鄰清華實驗室、台積館及跨棟空橋均不屬本模型。

色票 #B7866D 與 #424A4D 是未經儀器測色的視覺代理，不是施工規範。來源照片拍攝日未知；作品 2011–2016、URL 2024/11 與 XMP toolkit 2012/02/06 皆不是拍攝日期。

既有兩翼深度、低層邊界、梯形斜玻璃、平蓋屋頂與減量加粗遮陽葉片皆為歷史近似；本批不修幾何。未做實體列印或重算歷史製造 QA。

## 檔案與重建
- [彩色 3MF](nthu-innovation-incubation-appearance.3mf)：原三角完整面材質，可編輯。
- [Blender 原生場景](scene.blend)、[色票](palette.json)、[面對照](face-materials.json)。
- 五圖：[正斜視](previews/front.png)、[後斜視](previews/rear.png)、[前立面](previews/elevation.png)、[側面](previews/side.png)、[頂面](previews/top.png)。
- [來源](SOURCES.md)、[許可說明](LICENSE-NOTICE.md)。

將原 model.stl 與 appearance 資料夾置於同一父層；Python（numpy、lib3mf）執行 source/build_appearance.py、source/verify_exchange.py、source/verify_material_boundaries.py；Blender 4.3.2 執行 source/render_appearance.py 與 source/verify_scene.py。獨立乾淨重建需驗 3MF、maps、五張 PNG bytes 相同；Blend 驗語義而不宣稱二進位確定性。
