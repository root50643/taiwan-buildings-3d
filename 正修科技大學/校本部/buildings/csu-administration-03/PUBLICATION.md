# 正修03A/B/C正式交付範圍

本件依[公開來源與實看紀錄](sources.md)建立綜合行政大樓03A/B/C的低細節可列印代表模型。三區是同棟，只增加一套；主體與截頂屋蓋分印，組裝STL僅供展示。04體育室及相鄰教學樓排除。照片拍攝年份未逐一核實，尺寸為相對估計，不宣稱2026現況或可測量建築平面。

固定模型由 `76681c5dcedc88d684946780e795d7914a88c075` 經[原獨立條件GO](qa/independent-76681/INDEPENDENT-CSU-REVIEW.zh-TW.md)，文書與metadata修正固定於 `54c4ad2a30e6600e85fbf054d4c384f9e5304748`，再經[最終增量GO](qa/final-incremental-54c4/FINAL-INCREMENTAL-REVIEW.zh-TW.md)。首版 `6e683682473c2d1dbdf221b47270e0c909bd6eb0` 匯入最終證據、更新交付狀態及八個必要索引，當時生成器、現用參數、全部原STL、場景、G-code與預覽保持54c4位元組。

首版發布後的完整壓縮二進位補查發現兩場景的 `FileSelectParams.dir[1282]` 存有私人存檔對話框目錄。現版僅將此UI目錄欄位置為 `//` 並NUL填補，保持解壓後其餘資料、場景物件／mesh／camera／light／render語義相同；新舊hash與逐位元比較見[scene-path-redaction-1](qa/scene-path-redaction-1/README.md)。首版Library v2及13項發布檢查保留為歷史，原排除私人路徑宣告的檢查範圍不足，不能當現版完整binary證明。全部STL、G-code、生成器、參數與預覽不因本次metadata修正而變。

整合基線為 `c4c23d900b4b55f9e0905f235af023687fa5cc14`：495總／463校園／107校；加本件後為 **496總／464校園／107校**，其中新目錄106校425套、非校園32套。正修由圖書科技大樓一套增加為兩套，並非全校完成；嘉南藥理兩套、中山四套及其他已發布套件維持原樣。

## 交付與重建

- [主體STL](models/v2/parts/body.stl)：200×72×85 mm，平底向下。
- [截頂屋蓋STL](models/v2/parts/roof.stl)：48×36×11 mm，平底向下；膠合定位見[README](README.md)。
- [組裝總覽](models/v2/assembly.stl)、[場景](models/v2/scene.blend)、[多向預覽](previews/v2/)、[生成器](source/build_model.py)、[參數語義](parameters.json)、[依賴](requirements.txt)及[QA](QA.md)均包含。
- [首版發布增量核對](qa/publication-incremental/validation.json)由[檢查程式](source/validate_publication.py)產生，固定於6e68368前的發布樹；其「scene未改」僅屬該時點。現版另用[場景metadata核對](qa/scene-path-redaction-1/README.md)銜接hash。兩者均不取代原幾何、薄特徵或切片證據。

完整模型包、八個索引、提交原始物件及逐檔清單另存同一Library項目的新版本；以官方回下載的逐檔大小、SHA與CRC核對作封存證據。Library回條與遠端逐檔核對記錄在發布工作區，避免把後來的回條寫回固定提交造成循環。既有v1失敗、原旗標、修正前後證據及歷史hash保留，不覆寫為passed。

## 延續的製造限制

封閉流形、正體積、分件連通及精確自交檢查的固定證據保留。**嚴格製造仍false，未實體試印。** 6個共面射線歧義、97個支撐層旗標與屋蓋71個真尖簷短弦未被消除或改判。普通窗凹約0.4 mm；門凹名義0.65 mm、raw實測0.650001526 mm。門頂真正懸垂路徑為16.6 mm，不能以凹深當跨度。

auto45實際有20,930段支撐及61,223段介面，共82,153段／7,273.39394 mm耗絲；門區305段、45個strata、名義gap0.2 mm。這不是支撐件數，也不證明工具可達、支撐能清除或表面無損。屋蓋接觸1120 mm²及零正體積干涉不證明膠合強度；四邊4 mm外伸不是±4 mm公差，`|Δx|+|Δy|≤1 mm`只是在無旋轉且頂台全覆蓋的純幾何條件。

尚未驗證支撐與brim拆除、尖緣手感、縮放後細節、翹曲、表面、手動對中裝配或膠合。200 mm底座加brim須核對真機可用床面；依材料、噴嘴及機器重切。附generic G-code為 **NOT-MACHINE-READY**；0.4 mm／0.2 mm／100% rectilinear是QA設定，不是實物填充建議，也不是試印完成證明。
