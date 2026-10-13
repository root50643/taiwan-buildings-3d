# 國立臺北藝術大學｜關渡校本部

[學校入口](../README.md) · [未完成逐項清單](../remaining-building-work.zh-TW.md)

<table><tr><td width="33%"><a href="buildings/tnua-art-technology/"><img src="buildings/tnua-art-technology/previews/front.png" width="300" alt="科技藝術館實際STL"></a><br><a href="buildings/tnua-art-technology/">科技藝術館</a></td><td width="33%"><a href="buildings/tnua-kuandu-museum-upper-section/"><img src="buildings/tnua-kuandu-museum-upper-section/previews/front.png" width="300" alt="關渡美術館入口暨曲牆屋頂段實際STL"></a><br><a href="buildings/tnua-kuandu-museum-upper-section/">關渡美術館入口暨曲牆屋頂段</a></td><td width="33%"><a href="buildings/tnua-teaching-bell-tower-section/"><img src="buildings/tnua-teaching-bell-tower-section/previews/front.png" width="300" alt="教學大樓鐘樓段實際STL"></a><br><a href="buildings/tnua-teaching-bell-tower-section/">教學大樓鐘樓段</a></td></tr><tr><td width="33%"><a href="buildings/tnua-research-downhill-section/"><img src="buildings/tnua-research-downhill-section/previews/front.png" width="300" alt="研究大樓下坡端量體段實際STL"></a><br><a href="buildings/tnua-research-downhill-section/">研究大樓下坡端量體段</a></td><td width="33%"></td><td width="33%"></td></tr></table>

目前累計4件模型：1件主要外觀近似、3件局部段。**全校仍未完成，這不是4棟完整建築測繪。** 各件獨立縮放、含底座最長150mm；底座朝下。

- 科技藝術館：L形高差量體、四核心架空與偏置開口；屋頂機電及金屬網細格簡化。
- 關渡美術館入口暨曲牆屋頂段：只含入口與三層曲牆／天窗，不含下坡樓層與研究大樓，背牆截斷。
- 教學大樓鐘樓段：通透鐘廊、三孔側牆、三窄窗、曲牆與雙坡頂；鐘吊桿加粗，不含完整教學長翼，截斷背面平簡。
- 研究大樓下坡端量體段：六窄窗頂列，下三列各六加二，磚座寬窄分組與高低肩牆；只含端部及左側前三組短翼，後方及右側連體界面平簡。

## 列印與數位檢查

模型皆為自行建立的單殼實體，非第三方3D網格。各件含生成腳本、STL、匯入該STL的可編修Blend、由actual STL渲染的正背／立面／頂面PNG、來源、QA腳本與SHA。

原STL原始法向與繞序、每邊兩面、頂點連結單環、單一表面殼、正體積、最長150mm、獨立重建SHA及Blend一致皆檢查。逐層輪廓與個別／合成Polygon採0.2mm、自z=0.071mm開始。canonical fail-closed v3 不以修補無效輪廓掩蓋錯誤。

科技館320層／關渡段280層／鐘樓段750層／研究端651層；0.8mm參考寬度形態opening最大面積損失依序約0.1914%、0.3985%、0.5712%、0.3608%。形態opening不是全面壁厚檢測；數位QA亦不是實體試印或Cura／PrusaSlicer工具路徑驗證。鐘樓吊鐘／通廊跨梁、科技館大懸挑及挑簷尤其須檢查可移除支撐，不能保證免支撐。

[校圖、去重與範圍限制](../README.md#校圖去重與未完成範圍)
