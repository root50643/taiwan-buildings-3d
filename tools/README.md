# 校園主圖鑑發布檢查

新增模型不能只把連結附在 README 頁尾的「新增」紀錄；已列入主圖鑑後也不要再附同件頁尾卡片。使用本工具把缺少的卡片補進學校／校區**頂部現行主圖鑑**，再執行檢查；歷史批次清冊、模型本體與來源不會改寫。

```sh
# 新模型檔案及 model-packages.json 現行件數準備完成後：
python tools/school_gallery.py --sync
python tools/test_school_gallery.py
python tools/school_gallery.py --check --report navigation-check.json
# 檢查 diff，再提交與發布；--check 失敗時不可宣稱導航核對通過。
```

- 套件以 `buildings/<slug>` 為單位，不把 appearance、歷史版本、parts 或 QA 中的 STL 重複計件；另涵蓋臺灣地標與國衛院既有分類。路思義教堂也提供東海校級入口，但全庫只計一件。
- 主圖鑑可能是空行分隔的連續表格群、標題／圖片／下載多列，或原有非表格目錄；不把同模型正背視圖當兩件，不為格式一致而改寫完整原目錄。
- 缺卡以三欄加入同一主圖鑑群；末列留白。原有卡片與歷史更新紀錄保留。新增卡片取模型說明標題，保留局部、年代及範圍限定。
- 優先既有 `appearance/previews` 同視角圖片；否則保留原模型預覽。特別製造衍生版不擅自改成一般外觀版。
- 已在主圖鑑的模型又出現在「新增／補建」頁尾導航時，檢查會失敗。請直接更新主圖鑑，不要先 append 頁尾再期待工具刪除。既有詳細 `<details>`、獨立 QA／修版／歷史紀錄保留；來源、限制與 QA 必須留在模型詳頁，刪摘要前需人工核對。
- 檢查主入口套件集合、產生卡片唯一性、表格結構、相對圖／連結、預覽版本與現行統計。不是只搜尋整篇是否出現連結。
- 模型件數不等於獨立完整建築數，也不表示全校完成或實體試印通過。

## 稀疏 checkout

工具自動禁止 Git lazy fetch，避免為少量文字下載大量模型歷史。完整 Git index 用於路徑核對；未落地的 README 可從 Git 已有物件讀取。缺文字時可提供同版本 UTF-8 JSON `{ "repo/path/README.md": "原文" }`：

```sh
python tools/school_gallery.py --check --text-cache verified-text-cache.json
```

工具逐一核對缺少本機檔案的快取文字之 Git blob SHA-1 是否等於 index；不接受來源不符的文字。快取只是操作環境資料，不必提交。圖片路徑存在性不等於圖片解碼或瀏覽器呈現驗證，發布時應另外確認實際影像與介面。
