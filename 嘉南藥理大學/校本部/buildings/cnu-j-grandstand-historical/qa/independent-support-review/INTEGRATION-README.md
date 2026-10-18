# 獨立審查證據整合說明

本目錄保存固定候選 `3a9a6041c5fde9ef2d6e9e96b02f24f025c8be5a` 的獨立審查證據副本。這是歷史審查紀錄；其中 `candidate_commit`、`passed`、雜湊與原始結果仍指向該固定輸入，不代表整合後每個檔案重新執行過相同審查。請先讀 [完整獨立報告](INDEPENDENT-REVIEW.md) 及 [切片與支撐報告](slicing-support-audit/SLICING-SUPPORT-REVIEW.md)。

## 必須保留的判定

- 四個固定列印 STL 為有條件 GO，原主體自動橋向的診斷印法不放行；不能以 exit 0 或無 warning 代替可印判定。幾何未因這次整合而改動。
- 主體必須跨平台短向橋接，並保留橋下支撐；PrusaSlicer 2.9.6 審查變體採 `bridge_angle=90`、`dont_support_bridges=0`。角度僅在本件固定方向有意義，須按真機切片逐層確認實際 XY 路徑、接觸間距及新增支撐。
- 原平台最長中心線未承托段 `174.28871912133684 mm` 與原先僅前層比較值 `179.27600218657267 mm` 均保留；短向變體同層為 `1.7040004999999963 mm`。這些是計畫擠出線承托帶的分析，不是熔融材料或實測垂墜證據。
- 修正後主體仍有 `8.22491271252096 mm` 內填充封頂空段；棚板仍有 `8.036026605238602 mm`。棚板 30 盲槽的 `2.6000110755685952 mm` 並非所有橋接的最大值。材料、冷卻與流量須具相應橋接能力，或調整局部填充／實心層後重切。
- 舊支撐 `26,586` 段／`83,924` 唯一點、新支撐 `30,369` 段／`95,890` 唯一點分別檢查，兩者仍有同一組 `580` 個八向直射線旗標。後續三段折線與半徑樣線只是有限幾何補證，未保證完整工具、支撐碎塊、其他支撐或施力可行；未見新增封閉區只限本次抽查方法。
- 組裝前由側方逐段剪碎／剝離淺窗支撐，不可整塊朝前抽或硬撬階梯、窗框。外側槽約 `4.5 × 9.4 mm`；細工具仍須轉入約 `1.2 mm` 深窗凹。實際可達性不足時應改支撐策略並重切。
- `100%` 是尺寸，參考填充為 `15% stars`。50 個接口是留隙膠合定位，須清槽、乾排及治具定位；自然肩部落座的分析高度約 `53.25 mm`，不是名義 `53.4 mm` 的實測證明。
- 未試印、未實拆支撐或 brim、未試合、未測膠強度、棚板翹曲或細框搬運強度。全部診斷 G-code 均非真機通用檔，也未分發於本目錄。

## 副本身分與清理

[integration-source-manifest.json](integration-source-manifest.json) 逐檔列出原始檔案 SHA-256／大小、整合副本 SHA-256／大小，以及語意路徑替換角色。原始私路徑值沒有包含在映射中。無私路徑的檔案直接保留位元組；有私路徑的文字檔只以 `${PACKAGE}`、`${REVIEW_ROOT}`、`${PRUSASLICER_2_9_6_DIR}` 等角色代替，沒有改變數字、門檻、原座標、失敗旗標或結論。原檔未被修改。

`delivery-manifest.json`、`slicing-support-audit/audit-evidence-manifest.json` 及幾何 `EVIDENCE-MANIFEST.json` 是上游歷史清單，所載 SHA 仍指原始審查檔案；經清理檔案以 `integration-source-manifest.json` 為準。本次沒有複製 candidate 重複本體、原始官方照片、相簿 HTML、私有 G-code、切片器隔離設定、pyc 或憑證。來源照片只留下 URL、日期與雜湊紀錄；場景重建與來源接觸表等重複影像亦未帶入。

## 重跑方式

保留的舊 Python 檔是可讀的審查演算法來源，仍採上游審查目錄結構，部分另有 `${...}` 語意角色；不要直接在固定證據目錄執行。先在新的工作副本調整相對目錄，並將角色解析成自行選定的輸入與工具位置。`modal_capsule_helpers.py` 未經路徑修改，可直接 import；其來源 SHA 與獨立審查一致。`make_helpers.py` 僅記錄此前擷取 helper 的歷史步驟，使用已附 helper 不需取得更早工作區。

[replay_support_access.py](replay_support_access.py) 提供可攜的有限支撐可達性重跑入口，直接讀所附 NPZ 與本建築固定 `main_body-assembly.stl`，不需分發 G-code。依賴 Python、numpy、trimesh 及其 ray/contains 相依套件；輸出必須指定新的檔案，拒絕覆寫。原樣點步距 `≤1 mm`、小數五位去重、八個水平向、`1e-5 mm` 射線起終裕量、三段路由及 `0.5 mm` 半徑／65 周向樣線均維持原值。

```text
python replay_support_access.py --package <building-package> --paths slicing-support-audit/main_body-selected-paths.npz --output <new-output>/original-support.json
python replay_support_access.py --package <building-package> --paths slicing-support-audit/REVIEW-ONLY-main-short-axis-selected-paths.npz --output <new-output>/short-axis-support.json
```

完整橋線承托分析另見 `all_bridge_coverage.py`／`modal_capsule_helpers.py`；需由固定 STL 與對應舊／新 profile 產生自己的診斷 G-code，再於新的審查工作副本執行。G-code 首行生成時間會變，舊雜湊是歷史綁定，不應改成新檔雜湊來假稱原檔位元組相同。

整合驗證見 [integration-validation.json](integration-validation.json)：記錄來源清單、連結、JSON 數值／布林葉節點、私路徑掃描與腳本語法核對。本輪沒有無益地重算全部橋線，也沒有把既有證據說成新實測結果。
