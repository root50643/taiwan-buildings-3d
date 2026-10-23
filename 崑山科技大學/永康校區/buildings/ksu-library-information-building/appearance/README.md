# 崑山科技大學圖書資訊館：歷史後窗限域外觀

僅既有模型後窗 **1,242 面 / 2066.8784524567363 mm²** 使用不透明低彩度藍綠灰代理；其餘 **16,230 面維持未查證中性**。不是整樓上色、實測材質或2026現況。

- [雙材質3MF](ksu-library-information-building-appearance.3mf) · [可編輯Blend](scene.blend) · [重建原始碼ZIP](rebuild-source.zip)
- [前](previews/front.png) · [左](previews/left.png) · [右](previews/right.png) · [後](previews/rear.png) · [頂](previews/top.png)
- [單色對照](previews/mono-rear.png) · [來源及限制](SOURCES.md) · [授權](LICENSE-NOTICE.md)

白色曲翼窗背1120、兩座梯塔64、退台36、可見高紅磚區22面。高紅磚隱蔽96面拒染；前面、所有不透明牆體、屋頂、框、窗洞側壁、八孔及白翼梁槽均不染色。精確原三角形，無分割、增添玻璃或窗櫺。每面全部三點限定在原有限平面分段且以實際叉積法線驗證；原STL bytes、坐標、順序及朝向不變。

## 非製造修復／非可直接列印
原 QA.md 與全部歷史診斷保持不變。原作者 passed=false / exceptions_independently_approved=false、run_all_checks exit1 是歷史值；後續獨立122,304點有限例外放行也保留，不可互相覆蓋。真薄唇0.599998mm、曲帽首段/階0.300003mm與後續空隙、局部圓帽61.7342%支承仍然存在。南槽精確邊探針0.1216827mm、梯芯0.5999985mm不能以較厚代表截面代替。作者101,549/有效25,092與獨立122,304/25,096短射線樣本不同，不相加；830侵蝕損失樣本非830個零件。外觀不擴大或重驗歷史有限放行，不是全域0.8mm通過，無實體列印驗證。

## 重建
安裝 source/requirements.txt；由本目錄上層保留原 model.stl，執行 source/build_appearance.py、source/verify_exchange.py，再以 Blender 執行 source/render_appearance.py 與 source/verify_scene.py。驗證包括strict 3MF零警告、真材質修改存讀、Blend真頂點與真材質修改存讀、交付Blend重開重繪，以及clean重建3MF/map/palette/五張PNG完全相同；Blend只主張語義一致。
