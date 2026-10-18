# 誠勤大樓候選 QA

這是已取得獨立覆核 GO 的發布模型；下表保留原作者方法的實際結果，另附獨立嚴格檢查的失敗及非阻擋判讀。檢查對象是 [model.stl](../models/v1/model.stl)，SHA-256 `4e73e7094c83de47c19bcc6121fee575c1360b285d597773d983a873f46b7f5a`。2,936 個三角形、1,470 個頂點；模型含底板外框約 **184.3 × 63.08 × 159 mm**。

## 已實際執行

| 項目 | 結果與範圍 |
| --- | --- |
| 流形、正體積與連通性 | 邊界／非流形邊、非流形頂點 link、退化／重複面皆 0；繞向一致、封閉、1 個 edge-connected component，正體積 1,087,844.716 mm³。 |
| 原浮點自交篩查 | 考慮全部 4,308,580 個無序三角對，其中 31,375 個 AABB 重疊對執行 narrow phase；留下 **20 個旗標，原 CLI exit 1**。不得改稱 generic 全通過。 |
| 全部 20 個旗標的精確補證 | 使用同一 STL 儲存的 binary32 座標做 Fraction 有理數演算：10 對僅共享邊、10 對僅共享頂點；20/20 覆蓋且無超出共享拓樸之交集。其餘三角對仍只有原浮點篩查，沒有全網格精確證明。 |
| 0.2 mm XY 切層 | 795 層全部非空，沒有開放或無效切層；頂端兩個屋頂箱體使局部切層最多有 2 個材料區塊，三維實體仍相連。 |
| 薄特徵篩查 | 每個切層各材料區塊向內侵蝕 0.4 mm（0.8 mm 特徵寬度）；0 層核心消失或分裂。附著尖角及薄突起可能漏檢；不等於任意位置壁厚證明。 |
| 懸垂篩查 | 45°、前層外擴 0.2 mm 支撐包絡，超過 0.01 mm² 容差的層數 0。最壞包絡外面積約 0.000233 mm²；邊界距離以 ≤0.1 mm 間距取樣，並非噴嘴路徑／橋接模擬。 |
| 控制案例 | 正常 cube 通過；缺面、反向、分離塊、重疊、頂點接觸、0.4 mm 薄條／窄頸、過陡外擴均被預期方法偵測。薄條 CLI exit 1 證明薄特徵失敗會拒絕總 gate。精確補證另有 8 個分類控制與 7 個實際 CLI 控制全部符合預期。 |
| 真正重建 | 新暫存輸出重新執行生成器，STL 逐 byte 相同；不是只重新載入同一 STL。saved Blend 的有向三角多重集合與 STL binary32 完全相同，物件轉換為 identity。另重新執行場景原碼函式，比對材質、逐面材質索引、預設相機、光源、世界及顯示／渲染設定完全相符，沒有重渲染。 |
| 場景及圖像綁定 | 八張最終 PNG、STL 與 Blend 雜湊相符，場景無參考圖片。發布版僅清理路徑 metadata，像素和場景幾何不變。七張全景的頂點投影均在畫框內；connector 為明示局部特寫。作者已實際查看八張圖；獨立覆核另重渲染前視一張並逐像素相符；未聲稱八圖全重渲染。 |

## 原報、補證與程式

- [原浮點報告](qa-report.json)、[stdout](geometry.stdout.log)、[stderr](geometry.stderr.log)：保留數值失敗及所有旗標，SHA-256 `9d7253369d81df71bdbdb40d4c0576d2452fe7eeed26d9bbf9e52c5933a94f23`。
- [逐旗標補證說明](flag-diagnosis/README.md)、[最終 guarded 診斷](flag-diagnosis/diagnosis-verified.json)、[精確與 CLI 控制](flag-diagnosis/controls.json)；[初始診斷](flag-diagnosis/diagnosis.json)亦原樣保留。
- [檢查器](independent_geometry_qa.py)、[方法、容差與來源](CHECKER-METHOD.md)、[合成控制](control-evidence.json)及 [控制重建腳本](run_controls.py)。
- [原碼／場景／預覽重建核對](reproducibility.json)、[尺寸與凹槽參數補充檢視](declared-feature-review.json)、[補充檢視腳本](check_declared_features.py)。
- [失敗與修正事件](validation-events.json)：含缺依賴、曲面 T 接縫、浮點旗標、首輪材質／取景錯誤及修正；[失敗曲面生成器](failed-connector-source.py)、[首輪圖像雜湊與鏡頭](first-render-manifest.json)、[首輪渲染日誌](first-render.stdout.log)均保留。沒有多存過期圖片或 .blend1。
- [最終渲染日誌](render.stdout.log)、[最終渲染 stderr](render.stderr.log)、[重建日誌](reproducibility.stdout.log)、[重建 stderr](reproducibility.stderr.log)及 [工具版本](../toolchain.json)。
- [完整重建命令](../REPRODUCE.md)及 [來源／估算界線](../SOURCE-CREDITS.md)。

## 結論與未驗證事項

基本實體檢查、切層薄核心／支撐篩查及 byte／場景綁定已通過；原浮點相交篩查仍是 exit 1，全部 20 旗標另有精確局部補證。這組原作者證據與後述獨立證據一併支持代表模型發布；不是支撐檢查全通過或試印保證。

浮點 narrow phase 不是形式證明；層間細節可能漏檢；侵蝕不能證明附著細突起或任意三維最小壁厚。參數補充顯示窗間實體寬約 3.2 mm、窗間垂直實體約 5.08 mm、連接段帶間約 7.28 mm、底板 3 mm；0.6／0.65 mm 是表面凹深，不是薄壁。凸角和帶終止處仍須判斷。沒有切片刀路、材料／冷卻／黏著／強度驗證或實體試印。照片比對屬外觀判讀；高度、箱體深度、曲面高度與細部均維持明示估算，沒有精密測繪或現況承諾。


## 已完成的獨立覆核

完整報告、原始失敗、逐旗標及逐面判讀、獨立程式和控制案例見 [release-review/README.md](release-review/README.md)。固定候選 GO 不修改原 `qa-report.json` 的 exit 1／20 旗標，也不改作者的局部精確補證範圍。

獨立另對全 4,308,580 面對以儲存 binary32 座標整數／Fraction 演算法檢查，31,375 對通過精確 AABB 後未發現共享邊／點外接觸；這是可重現演算法檢查，不是機器驗證的形式證明。1,796 個有限切層均閉合且每個區塊的 0.8 mm 核心不消失、不分裂。

**獨立嚴格支撐檢查仍為 exit 1、digital_geometry_go=false、36 個旗標。** 最大包絡外面積 0.00011894401223611881 mm²；80 個前窗名義 45° 倒角面受 binary32 量化而微超，最大角 45.0003362567°，跨完整倒角最大額外超伸精確為 1/131072 mm。工程判讀為非阻擋，原門檻及失敗值原樣保留；不能寫成嚴格支撐通過或保證免支撐。

獨立新目錄重建 STL bytes 相同，檢查保存場景與原碼狀態，並只重渲染前視一張：780,000 個 RGBA 像素完全一致。發布版只移除 PNG File 欄與場景 FileSelectParams.dir 本機目錄，[publication-metadata.json](publication-metadata.json)記錄原／新 SHA、相同 IDAT／像素及場景其餘解壓 bytes。

仍無切片／G-code／試印。159 mm 高體／3 mm 底板的黏床、翹曲和擺動，以及連接段尖端、縮放後淺凹細節均需目標機台檢查。原 `CANDIDATE-*` 是歷史凍結指紋，最新檔案清單是 [PACKAGE-MANIFEST.json](PACKAGE-MANIFEST.json)，發布狀態是 [RELEASE-BINDING.json](RELEASE-BINDING.json)。
