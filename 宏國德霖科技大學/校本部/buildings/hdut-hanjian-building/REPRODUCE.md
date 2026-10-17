# 重現與檢查

工具版本：Python 3.12.14、numpy 2.3.5、manifold3d 3.5.4、shapely 2.2.0；Blender 4.3.2 / Cycles CPU，dense checker 使用 g++ 14.2.0 / C++17。依 requirements.txt 安裝。全程單執行緒，正式渲染 64 samples，未啟用降噪。原碼沒有外部貼圖或來源圖讀取。

## 原始模型

建立新的工作根目錄，複製本件 source/ 與 parameters.json；不要直接覆寫已有 models/v14。

```sh
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python source/build_model.py --output-dir models/v14
blender --background --threads 1 --python-exit-code 1 --python source/render_preview.py -- v14
sha256sum models/v14/model.stl
```

候選原始 STL SHA256：bcfb73e933ef1f590246cfd05f6480b2a5c0d4d4d9e4e878b25bec965393002b。原始 CSG 輸出前的座標規整、union 與 simplify 是原碼建模步驟；輸出的二進位 STL 不做後續修補或取代。Blend 由它逐面建立，沒有增減建築幾何。

上述完整渲染需產生正好九圖。前七圖是 ORTHO / 50mm，院內 courtyard-gallery 和 courtyard-arcade 是 PERSP / 20mm；精確位置、目標及 ortho_scale 綁 source 與逐圖 manifest。PNG 文件級 hash 可因 File／時間文字而異，視覺重現另外要求 IDAT、RGBA 與保留色彩 metadata 一致。

## 正式原件幾何 QA

在有完整 qa/verification 和 qa/tools 的根目錄執行，out 必須是新的目錄：

```sh
python -B qa/tools/run_full_qa.py \
  --stl models/v14/model.stl \
  --expected-sha256 bcfb73e933ef1f590246cfd05f6480b2a5c0d4d4d9e4e878b25bec965393002b \
  --expected-longest-mm 222.5 --out qa/fresh-full
```

此既有通用 runner 分別跑一般 Python 與 -O，保留所有子程序與失敗結果。原件 dense 的任何 flags 仍使 strict=false；不要把精確補證結果寫回原報告，也不要以整體 false 省略其他檢查。

若原始報告有 flags，必須先確認同一模式的 raw 與完整 exact intersections 真正合格，才可用 qa/tools/diagnose_recorded_cpp_rays.py，指定該模式的 dense-report、flags、raw-report、intersections-report、同一 STL hash 及新的輸出目錄。工具逐 byte 綁完整 CSV 和 flags，分類當次實際記錄的 lossless hex origin/direction，不能自行重造射線或換用其他模型例外。

## 場景與預覽

作者 source-state / inspect-only 檢查由既有 runner 完成。完整獨立九圖 replay 使用同一工具的 --rerender，而非另造簡化檢查。

```sh
python -B qa/render-tools/run_source_render_verification.py \
  --author-root "$PWD" --version v14 \
  --expected-stl-sha256 bcfb73e933ef1f590246cfd05f6480b2a5c0d4d4d9e4e878b25bec965393002b \
  --out "$PWD/qa/render-check/fresh" --rerender
```

工具有本件兩個院內視圖名稱與固定 projection/lens 的最小適配。原／新 hash 綁定保留於 qa/render-adaptation/ADAPTATION-BINDING.json；原工具與完整 diff 以原 byte 收在 qa/controls/controls.tar.xz 的 author-render-tool-update/。它不接受任意相機值；projection、lens、缺圖、多圖變造控制須拒絕。已驗 Noise mapping／ColorMapping、內建色帶集合狀態保留，雖然此件僅用純色 Principled。

公開 PNG 以 qa/render-tools/sanitize_png_previews.py 的白名單處理，不能轉檔、重壓、改 gamma、RGBA 或其他色彩 chunks。metadata-cleanup-binding.json 保留原／公開 hash 及逐圖視覺資料不變證據。

來源外觀核、作者檢查及獨立 QA 分別綁 hash，互相不能代替。所有有限幾何與重現檢查均非實際試印、承載或設備相容保證。

公開包只提供清理後 PNG 與原 raw manifest 的 hash 綁定，不散布含 File／時間欄位的原 PNG。上面的場景審計 runner 供保有完整原 PNG 的私人審計目錄使用；公開重現請先在新工作根目錄從 source 生成本次九張 raw PNG，再以相同白名單工具清理，逐張以 png_exact_compare.compare 對照公開 manifest 的 PNG hash 與 RGBA。不要將公開圖片改名冒充原 raw hash。

## 完整控制證據封裝

大量控制 fixture 與觀測以無損 controls.tar.xz 提供，包含作者與獨立檢查的正／負例，不以摘要取代原數據。qa/controls 的 index、packaging-result 與 author-archive-coverage-v14.json 逐檔列出邏輯來源、member、bytes／SHA256；作者另以 qa/publication/AUTHOR-ARCHIVE-COVERAGE-VERIFICATION.json 核對 413 份原件與 archive member 完全同 byte。控制摘要保留直接檔案；正式原模型的 raw、每層 Polygon、dense CSV、flags、exact contact、原 hex 補證則直接保留在原路徑。需讀取封裝內容時，使用隨包已驗的安全解包工具與 index，勿未檢驗就直接展開任意 tar。
