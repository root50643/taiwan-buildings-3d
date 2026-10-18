# 正修03A/B/C：54c4最終增量確認

固定提交：**`54c4ad2a30e6600e85fbf054d4c384f9e5304748`**。比較基線為前次獨立覆核的 `76681c5dcedc88d684946780e795d7914a88c075`。本輪只讀原候選，在本目錄保存新證據，未修改、推送、發布或操作憑證。

**結論：增量 GO，先前文件必修已解除；未發現尚待修正的必修發布阻擋。整體仍為有製造條件的代表模型 GO，不升格為實印、免支撐或清除／膠合驗證通過。** 本次不要求改幾何、再切片或重渲染。

## 實際diff及固定幾何

自行讀取兩提交Git樹與實際blob，核對本機全部 **377個追蹤檔案**逐位元組符合54c4。相較原337檔，**22個既有檔案變更、40個新增、0刪除；套件以外0變更**。既有變更只有16個PNG及6個README／QA／參數／audit說明檔；新增為勘誤、匯入獨立證據和增量／metadata工具。原生成器及所有原有STL、場景與G-code均逐位元組相同。

| 固定v2幾何 | SHA-256（不變） |
|---|---|
| body | `e388dff1247334ec5e79530e45a1b7e5e85d1a630aff0a9d6d53720f1362ee6c` |
| roof | `7d1c8840ee11649ec4c57984ff1a0cc2c2a3916f37fc21888e7ead0f631fed04` |
| assembly，僅展示 | `6d3a8796831cd83bd7e012664dd8f094b6e700998031e71db38567fc1ecff416` |

現用參數的既有值僅兩項從0.45改為0.65：`entrance.door_recess_depth` 與 `manufacturing.maximum_shallow_facade_recess`；另新增 `parameter_semantics`。實際幾何控制欄位未改，兩項深度及其他聲明欄位被明確標為不直接控制尺寸，源碼仍有固定座標，不宣稱全拘束自由參數模型。

在新的reviewer目錄複製**現用參數＋未變生成器**重建，body／roof／assembly三STL再度與固定版逐位元組相同。現用audit僅docstring修正；去除module docstring後AST與基線相同，沒有改解析演算法。完整diff分類、逐檔SHA及重建結果見[獨立增量證據](independent-incremental-evidence.json)。

## 16張PNG與獨立證據匯入

不用作者PNG解碼程式，另以PNG chunk解析／CRC驗證及Pillow解碼比較基線Git原bytes與現在檔案：

- 16張均只改一個 `tEXt/File` 值，將私人主機路徑改成套件相對場景路徑；不是重新壓縮圖像。
- 其他非File chunks逐位元組相同；全部IDAT壓縮資料亦逐位元組相同。
- 尺寸、模式及全部解碼像素逐位元組相同；前後PNG CRC有效。

因此可以沿用原外觀／場景判讀，但**PNG整檔SHA已改**，必須經原／新映射銜接。現用README、勘誤及QA-NOTES已明示歷史render manifest不改、舊SHA不當現檔指紋，不是假稱16張新檔仍與原bytes相同。

另將匯入的23個有來源檔案對照本覆核者前次原目錄及匯入清單：來源／交付SHA綁定均相符，JSON數字／布林／null值完整保留，Markdown原報告逐位元組不變，新增獨立渲染的像素也不變。路徑遮蔽檔另有交付hash，歷史腳本停止保護／新reproduce入口的界線已明示。沒有藉匯入把原判定、原旗標或歷史hash改成通過。見[匯入交叉核對](imported-evidence-crosscheck.json)。

## 文字與語義的最終確認

已逐項讀實際diff及現用README、QA、QA-NOTES、parameters、工具說明、勘誤與匯入README；另有[獨立文字覆核](agent-text/TEXT-SEMANTICS-INCREMENTAL-REVIEW.zh-TW.md)。

| 前次必修／宣稱界線 | 54c4確認結果 |
|---|---|
| 門凹深度 | 現用入口一致區分普通窗約0.4 mm、門凹名義0.65 mm／raw實測 **0.650001526 mm**，指出舊0.45為未控制生成器的錯誤聲明。 |
| 深度、壁厚與懸垂 | 門背約46.55 mm限定同線材料，不當全域厚度；實際門頂起訖及 **16.6 mm** 路徑完整揭露，不把凹深、投影寬或Bridge infill=0當橋跨／免評估證明。 |
| 真實支撐 | 20930支撐＋61223介面＝82153段、7273.39394 mm耗絲；門區305段／45strata、名義gap0.2 mm，不被說成實際成形、黏連或清除力成功。段數不是支撐件數。 |
| auto45舊錯句 | 現用文件明確把原audit／slice-summary的no-support字串標為歷史錯誤，指向corrected audit與實際配置；不要求覆寫凍結原始證據。 |
| 有限檢查 | 代表小片外退不等於完整骨架已分離、所有工具可達或表面無損；嚴格false、6共面歧義、71真尖緣短弦及v1失敗保持。 |
| 屋蓋接合 | 1120 mm²接觸／0正體積干涉不代表膠強度；4 mm外伸不是±4 mm公差，`|Δx|+|Δy|≤1 mm`限定無旋轉且頂台全覆蓋的純幾何條件。 |
| 歷史必修原文 | 匯入報告固定在76681，現用勘誤已解除當時聲明問題；保留原報不是新候選仍有未解除必修，不需篡改原判斷。 |
| 歷史參數／圖像SHA | 原build/render/QA綁原參數快照；新參數有另立重建與SHA，PNG有metadata映射。未假稱舊執行已用新聲明。 |

作者 `incremental-validation.json` 的14項均true，和本輪獨立差異／重建／像素檢查相符；其中 `strict_manufacturing_passed=false`、`physical_print_performed=false` 保持。原失敗JSON、原auto45錯誤／修正audit及其G-code均與76681原blob相同。**14項增量true不等於整體嚴格製造true。**

## 延續的製造條件與Library回條

交付仍是一套03A/B/C、body／roof各自平底分印；assembly只展示。200 mm底座及brim、縮放／轉向、門頂16.6 mm路徑、外部支撐分離／工具／拆力、屋簷尖緣、翹曲、表面與手動對中膠合均依前次條件保留。**未實體試印、未清除驗證，generic G-code NOT-MACHINE-READY，須按使用者真機重切。** 本輪不重跑全量碰撞、支撐解析或來源研究；其固定輸入未變，前次結果適用界線未擴張。

已讀作者更新的 `delivery.json` 與 `library-backup/library-verification.json`：同一項目 `libfile_2c2d4cd4e1988191b0451cc967251490` **v1**，38,615,220 bytes，SHA `63d0e0616f9661a76da0f49f6852fec60a7ab086a8be2ba8f45e3e0607372d82`，固定提交54c4、382項大小／SHA／CRC及377模型Git blob核對成功的回條相符。**正式替換／官方回下載核對由作者完成；本輪只核回條，沒有重下載或上傳。**

無剩餘必修發布阻擋或待批准操作。這是發布前增量覆核結論，不表示本覆核已執行發布；原候選未改、未推送、未發布。
