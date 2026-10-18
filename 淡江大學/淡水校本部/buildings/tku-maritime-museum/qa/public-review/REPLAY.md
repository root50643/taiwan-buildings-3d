# 獨立數值覆核腳本的重跑方式

數值證據的受審 STL SHA-256 固定為 `42097fab9a62dccd4042ba18bc49d3c5b9a44e66ff71e91962e68b56d74bc8b1`。本包中的四個 Python 腳本為審查原檔位元組副本，不匯入作者的 QA 判定函式，僅使用相對路徑或明確輸入參數；不是支撐生成器或切片器。

請在新的暫存資料夾重跑，避免覆寫已保留的審查結果。先安裝模型 `requirements.txt` 的固定依賴版本；原審查環境為 Python 3.13.9、numpy 2.5.4、trimesh 4.12.2、shapely 2.1.2、rtree 1.4.1。重建模型另需 manifold3d 3.3.2；場景數值由 Blender Python 5.2.2 LTS 測得。

相對資料夾配置：

```text
scratch/
  candidate/                  ← 模型套件完整副本，含 model.stl 與 qa/history/v1、v2
  geometry-audit/             ← 本包同名資料夾的三個 .py 腳本副本
  print-audit/                ← 本包同名資料夾的 .py 腳本副本
```

從 `scratch` 執行：

```sh
python geometry-audit/independent_exact_mesh.py
python geometry-audit/independent_thickness.py
python geometry-audit/historical_regression.py
python print-audit/independent_support_audit.py --candidate candidate --out print-audit/replayed-support-results.json
```

前三個腳本將結果寫入暫存副本的 `geometry-audit`。歷史回歸會讀 `candidate/qa/independent/candidate-v1.json` 原始失敗旗標及各版 STL；不覆寫它們。支撐腳本拒絕覆寫已存在的 `--out`，並產生同名 CSV。

幾何腳本對有限 STL 全面對作精確整數格／有理數自交檢查，並附控制算例。厚度是每面心一條內法線射線及定位探線，仍不是全域壁厚證明。支撐腳本只重算懸垂及理想工具通道，不生成支撐、不模擬拆除，不等於支撐可移除性或試印驗證。

本公開包未包含覆核者獨立重渲圖或 contact sheet，也未包含私人研究照片及其讀取腳本。重建／場景的原始數值與有向面控制結果留存，未冒稱所有十張圖皆獨立重渲。
