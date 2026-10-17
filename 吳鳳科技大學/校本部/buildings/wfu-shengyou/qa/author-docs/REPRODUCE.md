# 原創模型與證據重現

最終呈現版為 v13。STL、建模程式與色區均與 v12 原始幾何檢查的輸入逐位元相同；參數僅 revision 名稱變更，兩側正交相機視幅由 245 改為 280。完整對照見 qa/GEOMETRY-IDENTITY-v12-v13.json。所有 v12 原始幾何結果保留原路徑，不改成 v13，也不覆寫失敗。

軟體版本見 toolchain.json 與 requirements.txt。環境為 Python 3.12.14、Blender 4.3.2、numpy 2.3.5、manifold3d 3.5.4、shapely 2.2.0，密集檢查另需支援 C++17 的 g++。這些版本描述原執行環境；不同版本的數值或渲染差異需要重新核對。

## 建模

請在新的工作副本執行，保留 source 與 parameters.json 相對路徑。以下目的目錄必須尚不存在：

```
python -B source/build_model.py --output-dir models/rebuilt-v13
```

重建後逐位元核對 model.stl、color-regions.json、parameters.json、build_model.py、build-report.json。STL 目標 SHA-256 為 8348213614296746732da6a8024821ff48536e847419fe13545dc1ab20730ca0。沒有進行 STL 自動修補、重新三角化或以替代網格驗證。

## 場景與影像

原始場景與九張 PNG 保存於 models/v13、previews/v13。驗證工具先在獨立副本重建原碼和完整 scene-state，再檢查保存的 Blender 場景。原作者只執行 inspect-only；正式保存場景的九張重現由獨立 QA 執行一次，其結果以獨立報告為準。

如需自行重現，在新的工作副本執行以下命令；它會寫入同版場景及 PNG，因此不要在原證據目錄直接執行：

```
env -u PYTHONOPTIMIZE blender -b -t 1 --python-exit-code 1 --python source/render_preview.py -- v13
```

固定規格為 CPU Cycles、單執行緒、64 samples、seed 0、無 denoising、1000×780。七張正交全體視圖與兩張透視細節圖的相機資料寫入原 render-manifest.json。所有影像來自原 STL 三角形與原創色區，沒有使用原照片貼圖。

## 幾何原證據

qa/v12-full 保留 normal／optimized 的原始拓樸、逐層多邊形、全部密集樣本 CSV、flags、精確三角形接觸與 controls。qa/v12-recorded-rays 保留同次原 CSV actualhex 的全部 33 個 flags 精確補證；qa/v12-capture-* 保留原返回值與環境／工具綁定。原 producer exit1、strict=false 仍是原結果，不能只取補證摘要改稱嚴格通過。

幾何主流程可在新的輸出目錄以 qa/tools/run_full_qa.py 執行；它自行啟動 normal 與 -O 兩模式。原共享 capture、原工具 controls、獨立執行工具及其完整來源／雜湊清單隨完整科學封存的明確 copy-map 保存。請依原執行命令與該映射重建原相對目錄，勿改動檢查器門檻以迎合模型。

所有重型工作使用同一個排他鎖，並用 taskset 綁定一個可用 CPU。原作者來源／場景重建及 inspect 各執行一次，PNG controls 才是 normal／-O 兩模式。幾何／接觸／same-run actualhex 則各保留兩模式原始結果。

數位檢查不等於實體試印成功。模型尺寸是相對估計，不是建築工程比例；支撐、材料及切片設定需由實際列印者另行評估。
