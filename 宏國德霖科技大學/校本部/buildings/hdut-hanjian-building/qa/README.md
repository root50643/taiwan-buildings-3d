# v14 科學證據與重現入口

先讀 [獨立檢查說明](INDEPENDENT-QA.md) 與 [結構化結果](independent/QA-RESULT.json)。本件 bounded 數位檢查通過，原數值 strict=false 仍為 false；未試印。

## 原始證據位置

- `v12-full/{normal,optimized}/`：作者完整原網格、切層、92,660 列 lossless CSV、flags／shorts、精確原面相交與所有接觸。
- `v12-recorded-rays/{normal,optimized}/`：作者各模式同次原 runhex 的全部精確事件補證。
- `independent/geometry/{normal,optimized}/`：獨立同範圍完整原科學資料；`exact-recorded-rays/` 為各次原 flag 的精確補證。
- `author-source-render/`、`independent/scene-state/`：完整原場景狀態 JSON；重建、重渲報告與來源綁定見 `independent/`。
- `preview-binding/` 與 `../previews/v14-public/`：九圖 PNG 原／清理 hash、RGBA、保留 metadata、IDAT 清理證明。
- `controls/controls.tar.xz`、`controls-index.json`、`replay-verification.json`：完整合成控制、逐成員 hash 與安全重建結果。
- `EVIDENCE-COVERAGE.json`：正式幾何 run 每一檔的公開原 bytes／archive／私人 routine 記錄分類。
- `PUBLICATION-BINDING.json`：精確來源→公開檔案映射與私人省略 hash。原作者 freeze 是完整私有封存的 hash 清單，並不表示全部 771 檔公開。runner 對原成員無損轉排並額外凍結原清單本身，共 772 檔；對應證明在 `independent/`。

所有原 JSON、CSV、flag、切層、接觸與精確事件均未刪欄或改值。XZ／GZIP 為無損容器。公開的 QA-RESULT 是明確標示的衍生摘要，不能替代原科學資料。歷輪失敗、routine 日誌與原照片／PDF 私存。

## 安全驗證與控制重現

以下從模型根目錄執行，Python 3.11+、C++ compiler、NumPy／Shapely／Trimesh 等版本依模型的 `REPRODUCE.md`。重渲使用 Blender 4.3.2。所有 NEW 路徑必須不存在，勿覆寫已有證據。為減少平行資源差異，令 OMP、OPENBLAS、MKL、NUMEXPR 執行緒數均為 1。

1. 先核可信 index 的 SHA-256 與公開綁定，再使用受限 USTAR/XZ 驗證器；只有全部 member、path、hash、size、格式均通過才開始解包。輸出父目錄需使用者擁有且不可讓 group/other 寫入。不要用不受限的 tar 自動解包未知 archive。

```sh
python -B qa/tools/archive_verify.py --archive qa/controls/controls.tar.xz --index qa/controls/controls-index.json --out NEW_SAFE_CONTROLS
python -B qa/tools/build_controls_archive.py --root NEW_SAFE_CONTROLS --index qa/controls/controls-index.json --out NEW_REBUILT_CONTROLS.tar.xz
python -B -O qa/tools/archive_verify.py --archive qa/controls/controls.tar.xz --index qa/controls/controls-index.json --out NEW_SAFE_CONTROLS_O
python -B -O qa/tools/build_controls_archive.py --root NEW_SAFE_CONTROLS_O --index qa/controls/controls-index.json --out NEW_REBUILT_CONTROLS_O.tar.xz
```

2. 解包後 `ARCHIVE-SCOPE.json` 列出完整成員選擇、刻意損壞的拒絕 fixture、routine／symlink 排除描述與重現方式。`observed-author` 是沿用的封裝欄位名，內容是本件獨立 fresh 控制，不是其他建築的驗證。`v12-full/`、`independent/geometry/`、`author-render/`、`author-render-tool-update/` 分別含正式控制；`final-render-controls/` 另含本件最終場景 normal/-O 正負控制。不要把預期被拒絕的 fixture 解讀成模型失敗。

```sh
python -B qa/tools/run_control_suite.py --out NEW_FRESH_CONTROLS
python -B qa/render-tools/test_png_exact_compare.py --out NEW_PNG_CONTROLS
python -B -O qa/render-tools/test_png_exact_compare.py --out NEW_PNG_CONTROLS_O
blender --background --threads 1 --python-use-system-env --python-exit-code 1 --python qa/render-tools/test_noise_mapping_state.py -- --out NEW_MAPPING_CONTROLS
PYTHONOPTIMIZE=1 blender --background --threads 1 --python-use-system-env --python-exit-code 1 --python qa/render-tools/test_noise_mapping_state.py -- --out NEW_MAPPING_CONTROLS_O
```

## 新一次模型驗證

`qa/tools/run_full_qa.py` 會重新產生一般與 `-O` 兩模式完整數值證據。對本件原 hash，預期因 3 個原 flags 而保留非零退出與 strict=false，不能把退出碼改成通過或刪 flag。

```sh
python -B qa/tools/run_full_qa.py --stl models/v14/model.stl --expected-sha256 bcfb73e933ef1f590246cfd05f6480b2a5c0d4d4d9e4e878b25bec965393002b --expected-longest-mm 222.5 --out NEW_MODEL_QA
```

然後對新 run 每模式自己的 flags／dense／raw／intersections 執行 `qa/tools/diagnose_recorded_cpp_rays.py`，不加 `--limit`，輸出必須是新目錄；一般模式用 `python -B`，optimized 用 `python -B -O`。例：

```sh
python -B qa/tools/diagnose_recorded_cpp_rays.py --stl models/v14/model.stl --flags NEW_MODEL_QA/normal/standard/dense/dense-flagged-samples.json.gz --dense-report NEW_MODEL_QA/normal/standard/dense/dense-check.json --raw-report NEW_MODEL_QA/normal/standard/raw/raw-mesh-check.json --intersections-report NEW_MODEL_QA/normal/intersections.json --expected-sha256 bcfb73e933ef1f590246cfd05f6480b2a5c0d4d4d9e4e878b25bec965393002b --out NEW_EXACT_NORMAL
```

任何新增 flag、短弦、壞對、切層失敗、原 descriptor／hash／工具差異都需要重新調查，不能繼承本次三個 flags 的補證。`case-review/` 保留固定案例的後檢原碼與政策控制；完整私人 runner 佈局含 raw PNG 與執行日誌，不應假設公開精簡佈局可直接當作該 runner 的 `--run` 輸入。

原碼重建與預覽重現依根目錄 `REPRODUCE.md`。公開不含帶動態 File／時間文字的原 raw PNG；其原 hash 及逐張清理證明已公開。再次渲染應比較解碼 RGBA、保留 metadata 與只去白名單文字的 PNG，而非要求新的動態時間文字相同。場景驗證範圍是本件使用狀態集，不是任意 Blender RNA。

本件七張外部 view 固定 ORTHO/50 mm，兩張院內 view 固定 PERSP/20 mm。完整 view set 和每張 camera_specs 必須一致；不要以任意新增相機取代。batch 及最終場景控制原碼在解包後 `independent-tests/`，最後者需完整私有 frozen-run 佈局，其原輸入／mutants／結果也保留在 archive，公開精簡模型目錄不能冒充該私有 runner 佈局。
