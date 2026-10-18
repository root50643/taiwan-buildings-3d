# 亞東科技大學誠勤大樓約 2021 年代表模型：獨立覆核

日期：2026-10-18。**GO，無必修阻擋事項**，限下列固定候選及已揭露的低細節代表用途。這是審查決定，不是已發布、完成切片或試印的聲明；原始數值失敗仍保留，不能寫成所有方法全面通過。

| 固定標的 | 識別 |
| --- | --- |
| 候選提交 | `4116148c135d8a67a444ce8bf33fb64aba3e06a3` |
| 基準／直接父提交 | `56c252c0207bc8af202cc8b5b9e66da1c08a028b` |
| `models/v1/model.stl` | 146,884 bytes；SHA-256 `4e73e7094c83de47c19bcc6121fee575c1360b285d597773d983a873f46b7f5a` |
| `models/v1/scene.blend` | SHA-256 `5cf2b50f83e9f897ba2aaf4e61c806f4bf3ab7b90c9174c20c6c83a160fd1b25` |
| 原浮點 `qa/qa-report.json` | SHA-256 `9d7253369d81df71bdbdb40d4c0576d2452fe7eeed26d9bbf9e52c5933a94f23` |

## 可讀性、規範與範圍

先實際讀取 `${CANDIDATE_PACKAGE}/`，再建立本任務審查副本與 Git 物件副本。原件可讀。79 個套件檔案逐一與指定提交 Git blob、原交付 bytes 及審查副本比對一致；manifest 的完整範圍與每個 SHA／長度均吻合。候選相對基準只新增這 79 檔，沒有額外改動。

已讀 repo 根 README、亞東校級／校本部 README、本模型 README、來源／估算／列印限制、重建與 QA 方法。完整提交 tree 無 AGENTS／CONTRIBUTING／POLICY 檔，task／日期祖先亦未見新增 AGENTS。根 README、模型登記及亞東兩層索引 Git bytes 均未變，公開套數仍 491；本候選未被先算入發布。候選文件相對連結完整可解析。

本輪只檢查此新增模型，不重測全庫。所有輸出在 `${REVIEW_WORKDIR}`；原候選、原失敗紀錄與遠端均未改，沒有推送。完整 79 檔指紋與比較結果見 [provenance/results.json](provenance/results.json)。

## 來源與八張預覽實際觀看

獨立實看 [官方誠勤 4F 原圖](https://icd.aeust.edu.tw/var/file/44/1044/img/500/136405119.jpg)、[官方命名照片](https://eng-rp.aeust.edu.tw/var/file/1/1001/pictures/60/m/mczh-tw700x700_large14_881871915270.jpg) 及 [2021-01-12 次級照片頁](https://mhztravel.blogspot.com/2021/01/2021112_12.html) 的 DSC_0078、0080、0083 五張原圖，另逐張觀看八張候選 PNG。五原圖 SHA 均與 `public-sources.json` 相符；沒有以先前兩份 GO 或作者人工勾選替代本輪看圖。

web 實訪官方平面／命名／樓層頁成功。官方 JPEG 直連未由 web 取得可用像素，部落格直訪受到 redirect／抓取限制，故原圖實看使用本機可讀且 SHA 一致的原檔；部落格原 HTML 的日期與三個圖鏈亦核對同 SHA 保存內容。沒有宣稱被阻擋路徑成功重新下載。第三方原圖／HTML 留在 private 目錄，不納入候選或本證據封存。

來源與模型相符的關鍵量體是 12 層直板、兩條長外緣、淺突出端核心、平屋頂及兩端屋頂箱體，並有較低的多層曲面連接段。主板與端核心輪廓受官方 4F 圖約束；沒有加入未知後翼。屋頂箱體存在與位置有照片支持，深度明示估算，且限制在端核心平面內，沒有虛稱設備用途。曲面段在朝元智的兩端點間明確截斷，截斷面明示為模型邊界，不是假稱現場獨立端牆；元智本體沒有納入。

約 2021 年的時間定位、沒有實測公尺／1:N、145 mm 主體高度、箱體深度、曲面深度／高度／垂直對位及 10 個模型窗帶均有明示估算。10 個窗帶未被宣稱為實際恰有十層；未見後側採中性牆面，沒有鏡射前窗；3 mm 底板未冒稱地下裙房。上述為合理且已揭露的代表簡化，無須因未見某面而要求精密測繪才放行。

七張全景合計顯示前、後、兩端、屋頂與完整底座；第八張 connector 是明示局部特寫。所有圖片可解碼且 SHA 綁定，七張全景所有模型頂點位於影像與 clipping 範圍；特寫裁切不作全景保證。沒有用取景隱藏鄰棟或額外量體，也沒有誤導性試印成功文案。見 [視覺報告](visual-review/VISUAL-REVIEW.md)、[來源／八圖結果](visual-review/visual-review.json) 與 [八圖接觸表](visual-review/eight-preview-contact-sheet.jpg)。

## 原 20 旗標：逐索引、逐座標的真正獨立補證

原浮點自交報告仍為 **exit 1／20 旗標**，`self_intersections.passes_numerical_pair_screen=false`、`passes_bounded_geometry_screen=false`；沒有改寫為 generic 全通過。作者 Fraction 補證仍只涵蓋這 20 對，不因本次 GO 變成作者全網格精確證明。

本輪另寫標準函式庫 struct／Fraction 檢驗，不匯入作者 classifier：直接讀取原始 STL binary32 三角形，對原報告全部 20 對求未正規化精確平面與帶號值。各對皆為非平行平面，三角形非零帶號頂點同側；與另一平面的交集恰為零帶號頂點凸包。獨立得到 **10 對只共享邊、10 對只共享頂點**，沒有共享拓樸外的交集。

原 report 的完整 flag 值、face index、兩三角形的實際 STL 座標、共享座標、STL／report SHA，與初始及 guarded 兩份診斷逐項一致。另核對 raw 與 processed 三角面順序／座標相同，兩份診斷共 40 列共享索引及座標也相同。沒有移點、以理想面代替儲存座標、縮小旗標集合或放寬容差。作者診斷原樣重跑的完整 pairs 陣列亦一致。

重跑作者 8 個分類控制與 7 個實際 CLI 控制，另增 6 個真 CLI 非法索引／pair guards 及 6 個自寫正負分類控制，均符合預期；真正穿越、共面重疊及不合法輸入不會被誤接受。這些是局部演算法與 guards 測試，不能算成新的建築模型或試印完成。見 [旗標報告](flag-audit/FLAG-AUDIT.md)、[完整逐對結果](flag-audit/flag-audit-results.json)、[共享索引核對](flag-audit/shared-index-results.json)。

## 全模型獨立幾何與列印風險

另一套自行編寫的 binary STL 檢查不呼叫作者生成器、QA、trimesh 或作者例外清單作拓撲／面對判定；只合併精確相等的儲存頂點，不容差焊接或修補。

- 1,470 頂點、2,936 面、4,404 邊；每邊兩面、每點 link 單環，零邊界／非流形／重複／退化面，繞向一致。單一封閉面連通殼，Euler 2，正體積 `1087844.71637497 mm³`。
- 外包 `184.3000030518 × 63.0800018311 × 159 mm`，含底板。
- 全枚舉 **4,308,580** 面對，精確 AABB 排除 4,277,205，餘 **31,375** 對用整數／Fraction 邊－閉三角面演算法檢驗，零超出共享邊／點的接觸。作者 20 對沒有被跳過。這是全配對的精確儲存座標演算法檢查，不是經形式化驗證的完整數學證明。
- 另作 **1,796** 截層：0.1 mm 中點格網、71 個實際頂點 Z 事件之間中點及事件上下 1e-6 mm。所有截面閉合有效；每個材料區塊各自向內侵蝕 0.4 mm，核心均未消失或分裂。z>148 mm 出現兩個屋頂箱體截面是合理形狀，三維 STL 仍單連通，各箱體受下方主體支承。
- 8 種三角對、6 種實體正負控制，以及 5 種截層控制均符合預期；薄條／窄頸／過陡外擴會被偵測，兩個各有穩定核心的截面區塊正確接受。

### 本輪嚴格支撐失敗仍保留

本輪主檢查沿用更嚴的 `1e-5 mm²` 支撐面積門檻，**實際 exit 1、`digital_geometry_go=false`、36 個微量截層旗標原樣保留**；沒有改門檻或覆寫結果。最大外擴面積 `0.00011894401223611881 mm²`。

另對全部 462 個非底面向下面逐面分析，只有 80 個前窗倒角面嚴格超過 45°，最大 `45.0003362567°`。以原 binary32 整數座標直接求差，跨完整約 0.65 mm 倒角的最大超伸精確為 **`1/131072 mm = 0.00000762939453125 mm`**。其他向下面沒有超過 45°。這是附著主板的名義 45° 倒角量化偏差，不是懸空板、橋或自由薄牆，對本件不構成實質結構阻擋。人為 GO 判讀與 strict gate 分列，不能回填為嚴格支撐通過。

見 [幾何報告](geometry-review/GEOMETRY-REVIEW.md)、[原始完整結果](geometry-review/independent-stl-results.json)、[微量旗標判讀](geometry-review/print-risk-analysis.json)。原作者 20 浮點旗標及本輪 36 支撐旗標屬不同方法、不同範圍，兩者都須繼續保留。

### 尖端、薄特徵與未驗證範圍

曲面段切面 A/B 端點與宣告參數在 binary32 誤差內相符；實際凸角約 68.24–85.14°，0.8 mm 核心在端點退縮約 0.59–0.71 mm。這是附著實心連接段的局部數學尖端，可能被噴嘴圓化或捨去；核心未消失不等於每點厚於 0.8 mm。沒有發現分離小件或無核心薄橋。見 [切面尖端結果](geometry-review/connector-tip-review.json)。

0.6／0.65 mm 是填實主體表面凹深，不是自由薄壁。有限 795／1,796 截層都不能證明連續 Z 或任意方向最小壁厚；支撐幾何包絡不模擬擠出、橋接、冷卻、收縮、強度或拆支撐。159 mm 高體與 3 mm 大底板仍有黏床、翹曲及擺動風險，184.3 × 63.08 mm 底面還需 brim／skirt／機台邊界餘量。凹槽、端角及縮放後細節需實際切片確認。**沒有切片器刀路、G-code、材料／機台設定或實體試印驗證。**

## 重建、Blender 與一次獨立重渲染

主審自行編寫的 orchestration 實際呼叫原生成器輸出至新目錄，STL 完整 bytes 與固定候選一致。此項證明原碼可重現，仍使用作者建模演算法；與上面另寫的獨立幾何判定分列，沒有把重建冒充第二套獨立建模。

以 bpy 5.2.2 LTS 停用載入腳本讀固定 scene，不儲存回原檔。列印物件 evaluated world-space 的 2,936 有向三角多重集量化到 binary32 後與 STL 完全一致，變換 identity、無 modifier／constraint；實讀單位 METRIC／MILLIMETERS、scale_length 約 0.001。場景其他 mesh 只有明示 render ground，無來源圖紋理、連結 library 或腳本文字。

另外只執行渲染原碼的 `create_scene()`，不呼叫它的 save/render main，比對實際物件／世界變換、單位、完整逐面材質、shader 顏色、相機、燈光、world、渲染及顯示設定；與保存場景完全一致。原碼的八個 literal view 定義也與 manifest 完全相同。八 PNG、scene／STL manifest SHA 全匹配。

僅用已存前視相機與設定獨立重渲 **一張**，1000×780 解碼 RGBA 共 780,000 像素與候選完全相同，差異像素 0、最大通道差 0。PNG bytes 因 Date／File／RenderTime metadata 不同而不同；未把這說成八圖全部重渲染或 Blender byte 重建。見 [場景／重建結果](scene-evidence/rebuild-scene.json)、[像素比較](scene-evidence/independent-front-pixel-comparison.json)、[獨立前視](scene-evidence/independent-front.png)。

## 失敗留存、交付與決定

候選仍保存原曲面 T 接縫失敗程式、依賴失敗、首輪材質／取景錯誤及修正、首輪 manifest／logs、原 float exit 1、初始與 guarded 診斷；相關文案沒有改成全面通過。獨立旗標審查者第一次誤讀不存在的總 gate 欄名，該錯誤摘要亦保留並另列 auditor_error，更正後重跑，不能當作候選修改。打包器首次把巢狀 self_intersections 欄位當頂層讀取而 KeyError，中止於輸出整理，更正路徑後重新核對；紀錄在 `delivery-initial-check-failure.json`。新嚴格支撐失敗同樣原樣留存。

- [決策摘要](decision.json)、[79 檔固定指紋](provenance/results.json)。
- 分項原碼、逐層／逐對數值、guards 與實際 stdout／stderr 分別保存在 `geometry-review/`、`flag-audit/`、`visual-review/`、`scene-evidence/`。
- 主審可重跑腳本：`audit_provenance.py`、`audit_rebuild_scene.py`、`compare_preview_pixels.py`；使用 Python 3.13.9 及釘選庫。bpy 使用先前已存在的可讀 runtime 副本及任務內 `BLENDER_USER_RESOURCES`，未安裝或修改依賴。
- 證據封存排除第三方來源圖／HTML、候選複本、Git 物件及 runtime，保留原創獨立渲染、報告、測試碼與結果。

**上述固定提交與 STL SHA 可 GO；沒有待處理的實質結構、驗證或來源阻擋。GO 必須與本報告保留的數值失敗、估算和未試印界線一起使用。未執行發布或推送。**
