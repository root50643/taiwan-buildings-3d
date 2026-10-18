# 文書修正 1：獨立覆核後，固定 v2 幾何不變

本輪以 `76681c5dcedc88d684946780e795d7914a88c075` 為原候選。修正說明／參數聲明，整合[獨立條件 GO](../independent-76681/INDEPENDENT-CSU-REVIEW.zh-TW.md)，沒有修改生成器、固定 STL、場景、G-code、原始失敗或其座標。另只清除16張原預覽PNG的私人 `File` metadata，IDAT及解碼像素不變；見[前後映射](png-metadata-redaction.json)。仍待獨立檢查者增量確認，未推送／發布或變更公開模型計數。

| 修正 | 正確讀法 |
|---|---|
| 門凹聲明 | 普通窗約 0.4 mm；門凹名義 0.65 mm、原 raw STL 實測 0.650001526 mm。原聲明 0.45 mm 不正確，且當時未控制生成器。 |
| 製造意義 | 門背約 46.55 mm 連續材料，非 0.65 mm 薄牆；門頂仍有支撐／成形意義，不能稱勘誤完全無製造影響。 |
| 真正路徑 | body G-code 唯一 Overhang perimeter 為模型 (-8.3,-28.975,20.2)→(8.3,-28.975,20.2)，16.6 mm、WIDTH0.4／HEIGHT0.4；凹深、投影外接寬及 Bridge infill=0 不免除懸垂評估。 |
| 實際支撐 | auto45 有 20930 支撐＋61223 介面＝82153 段，耗絲 7273.39394 mm；段數非塊數。門區305段／45strata，名義gap0.2mm，不是黏連、成形或清除試驗。 |
| 屋蓋定位 | 接觸1120mm²、正體積干涉0。四邊4mm名義外伸不是允許偏移；無旋轉且頂台全覆蓋的 `|Δx|+|Δy|≤1mm` 是純幾何條件，不是製造公差。 |

## 參數語義與歷史綁定

現用 `parameters.json` 另列 `parameter_semantics`。`entrance.door_recess_depth`、`relief.*`、`manufacturing.*` 與 `parapet.inset` 是聲明／設計目標，不會直接改幾何；其他列出的控制欄位才會被生成器讀取，源碼仍有固定座標，不能稱全拘束自由參數模型。門凹仍由原生成器的門廊 `depth+0.4` 與 cut `center_y=-28.9, depth=0.7` 決定，沒有為讓文件數字成立而改 STL。

[原參數快照](parameters-at-76681.json)與[原337檔身分](frozen-inputs-at-76681.json)記錄當時 bytes 的指紋。原 `models/v2/build-report.json`、render manifest、visual-source-review 及 QA 都是對該原參數與固定幾何執行的歷史證據。它們的原 SHA／旗標不改，不能宣稱當時執行了新參數聲明，或其舊 PNG SHA 就是清除 metadata 後的新檔案 SHA；新映射另核對原 PNG 指紋、現在檔案 SHA、所有 IDAT 與解碼像素一致。PNG原bytes只留私有工作紀錄，不再次包入Library。新的[增量校驗](incremental-validation.json)另比對現用參數重建三 STL、固定媒體與原記錄，並重讀 raw STL 門凹線及兩份實際 G-code；完整自交／所有切片／九張渲染沒有無理由重跑。[全包宣稱搜尋](claim-search-at-76681.md)記錄原337檔、88個壓縮payload與4個G-code註解的搜尋及分類。

## 歷史錯句與工具說明

原 `qa/v2/slicing/body-auto45/slice-summary.json` 的 `limits` 沿用 no-support 字句，原 `.../gcode-audit.json` 也曾錯寫「支撐禁用」；同 SHA G-code 的 [corrected audit](../v2/slicing/body-auto45/corrected-audit/gcode-audit.json)與[補切綁定](../v2/slicing/auto-support-evidence-validation.json)已更正配置判讀。原錯誤輸出照存，不能單獨用作無支撐結論。

`source/qa/` 的可執行程式是原已執行檢查工具的凍結快照；其中 `run_slice.py` 的固定 limits 以及 `audit_gcode.py` 的舊 docstring，不適用於 auto45 配置，並非目前製造交接的建議。它們的雜湊維持原 QA 綁定，不改成假稱當時已修好；此資料夾 README 另加勘誤。現用 `source/qa_audit_gcode.py` 的 docstring 已改為中性配置說明，原版存於 [legacy-source](legacy-source/qa_audit_gcode.py)，新校驗證明去除 docstring 後 AST 相同，演算法沒有變；舊修正 audit 仍綁原版 SHA。另見[測試工具適用界線](../../source/QA-TOOLING-NOTES.md)。嚴格製造 false 與原始全部失敗持續保留。

## 仍未實證

支撐／brim 清除、尖屋緣成形與損傷、翹曲、表面、平面膠合強度、公差及手感均未實體試驗。代表支撐小片有限掃掠不證明完整連架可原位剪開或工具可達；不要以2mm護牆／銳屋緣撬支撐。先乾組正確X/Y方向，對中並固定至膠固化。任何縮小或轉向都需重評；附 G-code **NOT-MACHINE-READY，必須按真機重切**，100% rectilinear僅為此幾何QA設定。
