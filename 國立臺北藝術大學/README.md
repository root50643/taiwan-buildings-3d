# 國立臺北藝術大學 TNUA

[關渡校本部](關渡校本部/README.md) · [逐項續接](remaining-building-work.zh-TW.md) · [機器可讀清單](remaining-building-work.json)

<table><tr><td width="33%"><a href="關渡校本部/buildings/tnua-art-technology/"><img src="關渡校本部/buildings/tnua-art-technology/previews/front.png" width="300" alt="科技藝術館實際STL"></a><br><a href="關渡校本部/buildings/tnua-art-technology/">科技藝術館</a></td><td width="33%"><a href="關渡校本部/buildings/tnua-kuandu-museum-upper-section/"><img src="關渡校本部/buildings/tnua-kuandu-museum-upper-section/previews/front.png" width="300" alt="關渡美術館入口暨曲牆屋頂段實際STL"></a><br><a href="關渡校本部/buildings/tnua-kuandu-museum-upper-section/">關渡美術館入口暨曲牆屋頂段</a></td><td width="33%"><a href="關渡校本部/buildings/tnua-teaching-bell-tower-section/"><img src="關渡校本部/buildings/tnua-teaching-bell-tower-section/previews/front.png" width="300" alt="教學大樓鐘樓段實際STL"></a><br><a href="關渡校本部/buildings/tnua-teaching-bell-tower-section/">教學大樓鐘樓段</a></td></tr><tr><td width="33%"><a href="關渡校本部/buildings/tnua-research-downhill-section/"><img src="關渡校本部/buildings/tnua-research-downhill-section/previews/front.png" width="300" alt="研究大樓下坡端量體段實際STL"></a><br><a href="關渡校本部/buildings/tnua-research-downhill-section/">研究大樓下坡端量體段</a></td><td width="33%"></td><td width="33%"></td></tr></table>

目前累計4件模型：1件主要外觀近似、3件局部段。**全校仍未完成，這不是4棟完整建築測繪。** 各件獨立縮放、含底座最長150mm；底座朝下。

- 科技藝術館：L形高差量體、四核心架空與偏置開口；屋頂機電及金屬網細格簡化。
- 關渡美術館入口暨曲牆屋頂段：只含入口與三層曲牆／天窗，不含下坡樓層與研究大樓，背牆截斷。
- 教學大樓鐘樓段：通透鐘廊、三孔側牆、三窄窗、曲牆與雙坡頂；鐘吊桿加粗，不含完整教學長翼，截斷背面平簡。
- 研究大樓下坡端量體段：六窄窗頂列，下三列各六加二，磚座寬窄分組與高低肩牆；只含端部及左側前三組短翼，後方及右側連體界面平簡。

## 列印與數位檢查

模型皆為自行建立的單殼實體，非第三方3D網格。各件含生成腳本、STL、匯入該STL的可編修Blend、由actual STL渲染的正背／立面／頂面PNG、來源、QA腳本與SHA。

原STL原始法向與繞序、每邊兩面、頂點連結單環、單一表面殼、正體積、最長150mm、獨立重建SHA及Blend一致皆檢查。逐層輪廓與個別／合成Polygon採0.2mm、自z=0.071mm開始。canonical fail-closed v3 不以修補無效輪廓掩蓋錯誤。

科技館320層／關渡段280層／鐘樓段750層／研究端651層；0.8mm參考寬度形態opening最大面積損失依序約0.1914%、0.3985%、0.5712%、0.3608%。形態opening不是全面壁厚檢測；數位QA亦不是實體試印或Cura／PrusaSlicer工具路徑驗證。鐘樓吊鐘／通廊跨梁、科技館大懸挑及挑簷尤其須檢查可移除支撐，不能保證免支撐。

## 校圖、去重與未完成範圍

已查看北藝大製作、芳苑國中公開轉載的[115學年度招生簡章校圖（PDF第27頁／印刷頁25）](https://fsjh.chc.edu.tw/storage/074521/posts/6091/files/1141004310-0-0.pdf)，並與[112年官方計畫配置圖（PDF第24頁）](https://ws-proj.moe.edu.tw/001/Upload/568/relfile/13271/12988/d95e8a4f-fa4e-4d65-9fd9-193872248e2e.pdf)相核。115圖是最新取得的學年度配置插畫，仍不是測繪／2026全面現況。[113招生校圖](https://admissionex.tnua.edu.tw/wp-content/uploads/2024/04/113_cac_map.pdf)只有文字可讀、圖像取用遇issuer certificate錯誤，未繞過。

[2024官方會議記錄](https://sec.tnua.edu.tw/wp-content/uploads/2024/10/113.10.01_%E6%9C%83%E8%AD%B0%E7%B4%80%E9%8C%84.pdf)確認原藝大會館2–4樓轉教學的動畫與新媒體大樓、2024年9月5日揭牌；也列圖書館外牆／屋頂與綜合宿舍修繕。這些更名、用途與修繕不等於新增多棟。圖書館尚缺修繕後側背證據，繼續暫緩全棟建模。

[2022官方會議記錄](https://sec.tnua.edu.tw/wp-content/uploads/2022/10/111.04.19.pdf)明寫文資書苑位於研究大樓4樓；[學生手冊](https://student.tnua.edu.tw/upload/files/guidance/TNUAhandbook.pdf)確認地下美術館位於圖書館。鐘樓歸教學大樓、鼓樓另在活動中心。地圖標籤、使用單位與OSM多邊形均不能直接當作獨立棟數。

逐項續接維持36個研究條目，包含早期26個名稱、補查設施與校外合作場地。實體建築分母未確定，不能計算全校完成率。華山、C-LAB、國際藝術村與剝皮寮等合作學堂仍待核現行教室／使用範圍，不另宣稱新校區。

原照片／PDF與私人研究對照圖不在公開包內；sources.json只保留可回查URL、年代、支持特徵與限制。
