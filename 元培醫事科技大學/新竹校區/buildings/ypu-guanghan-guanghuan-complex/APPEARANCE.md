# 元培光瀚／光寰連體｜有界跨年配色

## 範圍及保留

原2488頂點／5028三角面、transform及150×102×33.7mm不變，只有原三角面材料。原STL、scene、build腳本、全部五張原預覽、原診斷證據保留；另增appearance場景／3MF／五彩圖及可重建腳本。原README第一章仍先原表，再彩表，另加同內容繁中README；學校／校區／首頁代表圖不變。

## 已讀來源及時期

[元培2022永續報告](https://hespo.ypu.edu.tw/var/file/63/1063/img/2022YUMTSustainabilityReport.pdf) PDF第45及64頁實際渲染閱讀。45頁右中長弧連體與原模型內院、入口凸弧、端核相符；64頁為反向屋頂。報告2022年不等於拍攝日，兩張日期皆未知；45未見光電、64有光電，不能混為同日現況或宣稱2026現況。

原校方內院JPEG本輪503，沒有讀到，不拿原檔描述當重讀證據，也未繞過失敗。2008落成年份記錄／原正射／其他平面不另作本輪已驗色證。兩報告照片有印刷網紋／漸白，只支持粗略色家族，不作精確色票。源照片及PDF均不公開包入。

## 色域與未知

只已辨內院原牆米灰、原凹窗灰綠、入口凸弧原窗背深藍綠不透明proxy；依原plan-registration轉換與原面支持平面／原cut深度限定，不再對成品網格套轉換。原粉褐格架限定既存relief／柱／軌，未新增格網。H橢圓端體只朝原寬橫槽的可見半圈外facet米灰，十片存活寬槽凹底灰綠；另一半圈、頂環與內孔中性，原腳本窄條沒有存活凹底面，不造新色條。

未充分證實的L外弧窗背、H外側、廣大屋頂、人工基座／前院／坡地、地下露出分界中性；不能把整頂塗成照片後期光電。沒有新增PV、設備、地形、樓層或磁磚縫。跨年近似、原配準殘差與尺度／高程推估不因配色而消失，背面未知窗仍省略。

## 重建與檢查

Blender4.3.2：`blender -b -t 1 --python-exit-code 1 -P build_appearance.py`，需原scene.blend、model.stl、plan-registration.json同目錄。新appearance移除原繼承燈，只用受控Key/Fill/world；原scene照明不變。CyclesCPU32samples seed0；clean重建校驗script/3MF/materialJSON/5PNG共8檔byteexact，BLEND做語義驗證而非容器byte相同。PNG無文字metadata；見[補色審核](appearance-review/)。原面材料區域可另用 `blender -b -t 1 --python-exit-code 1 -P appearance-review/check_material_regions.py` 重驗，所需純派生數值控制同目錄material-plan.json已附，不需私有PDF。

原QA、179root診斷、薄特徵與接點警告仍以原文件為準；補色不等於修正原幾何或全面切片認證。未試印，不保證免支撐，3MF不提供特定AMS映射。
