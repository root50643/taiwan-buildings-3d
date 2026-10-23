# 嘉大蘭潭圖資前棟截段 — 雙端上圓筒與錐頂限域配色

本層僅為既有前棟截段的附加材質，不是完整館舍；背緣是人為截斷，不是真實後牆。原 STL bytes、6510 三角座標及面序完全不變，沒有移點、切面或新增幾何，不增加模型套數。

依官方正面照片（拍攝日未知）及官方斜角照片（EXIF Original/Digitized、XMP CreateDate 為 2018-05-30），僅對雙端上圓筒前半外皮 264 面使用暖白 #DDDCD2，前半錐屋面 128 面使用銀灰 #969DA0。共 392 個完整原面約 688.827637 mm²。兩筒中心 (-62,-4)/(62,-4) mm，採原 64 邊柱/錐每扇段支承平面與全部三頂點判定，且 y≤-4；白筒 z47–60.2，錐頂 z60.2–66.2。不是 bbox 或面心選面。側面及頂視可見的前後半色界是證據範圍邊界，不是真實建築材料接縫。

其餘 6118 面 #AAA79F 為未確認中性代理，不代表實景色；包括兩筒背半、灰環帶、窗洞及回折、水平頂盤、下筒磚面、主樓混界立面、中央窗及屋頂。色值為不透明、非鏡面視覺代理，非官方色號或測色。主立面紅磚與白窗框混界、中央窗白色不透明細格沒有足夠幾何分材界，不整面紅牆/綠玻璃。

原窗孔、柱柵、錐頂比例與截段尺寸仍是近似，不宣稱逐格測繪、完整復原或 2026 現況。未做實體列印，原歷史製造 QA 不重算。

## 檔案
- [彩色 3MF](ncyu-lantan-library-front-section-appearance.3mf)、[Blender](scene.blend)
- [色票](palette.json)、[原面對照](face-materials.json)
- 五圖：[正斜](previews/front.png)、[後斜](previews/rear.png)、[正立](previews/elevation.png)、[側面](previews/side.png)、[頂面](previews/top.png)
- [來源](SOURCES.md)、[許可](LICENSE-NOTICE.md)

原 model.stl 與 appearance 同父層。Python（numpy 2.3.5、lib3mf 2.5.0）依序執行 source/build_appearance.py、source/verify_exchange.py、source/verify_material_boundaries.py；Blender 4.3.2 執行 source/render_appearance.py、source/verify_scene.py。乾淨重建核 3MF、maps、五 PNG bytes；Blend 核語義，不宣稱二進位確定性。驗證含 strict lib3mf 真材質修改存讀、Blender 真材質/頂點修改存讀及重開渲染。
