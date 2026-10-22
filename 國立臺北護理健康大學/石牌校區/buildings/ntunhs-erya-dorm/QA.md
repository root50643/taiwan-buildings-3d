# 爾雅樓：最終實mesh檢查

- STL SHA256 `ed345624f0940e0071ee8adb03d279c60fc5239f5e7ac0ccb9183e7032ce1180`；12,962 triangles、6,431 exact-weld vertices。
- Raw binary STL：零非有限、零零面積、零重複面、零非二邊、零方向錯、零vertex-link失敗；單一正體積封閉連通外殼。僅精確坐標相等合併，不修補、刪面或法線修復。
- 951層、0.2mm間距及最高處-0.001mm，全部輪廓合法，各連通正組件可承受-0.4mm侵蝕，無豁免。這不是所有局部最薄處證書。
- 局部真實射線厚度與屋頂凹口／階梯平面／斜切裙房剖面見`qa/feature-validation.json`。薄處例值：[('rear_window_closed_envelope', [84.75]), ('PV_panel', [189.39999389648438]), ('roof_screen_post', [1.4000015258789062]), ('roof_parapet', [1.3000030517578125]), ('rear_upper_white_frame', [2.6000003814697266]), ('rear_ground_entrance_mullion', [1.1999969482421875]), ('front_stair_rail_post', [1.4000015258789062]), ('front_window_parapet', [88.5])]。
- 向下超過45°面 2293，面積 19067.17 mm²。階梯、窗格、屋頂邊緣須支撐評估；無免支撐或實印認證。
- 3MF與STL逐三角坐標一致；lib3mf strict無警告，材質顏色/alpha真編輯後寫出重讀，其他顏色與分派保留。
- Blend真頂點＋材質編輯、存檔、重讀；場景沒有外部素材、嵌入腳本或源照片。五PNG由同mesh實際渲染且相機全框驗證。
- 乾淨目錄重建core四檔與五張PNG逐bytes一致（結果見`qa/isolated-rebuild.json`）。

重跑（替換相應解譯器路徑）：
```
/path/to/modeling-python run_all_checks.py --lib3mf-python /path/to/lib3mf-python --blender blender
/path/to/modeling-python rebuild.py --output /new/empty/output --blender blender
```

八材質：展示底、灰白、灰、深凹框、玻璃替代色、植栽、PV、欄杆。透明度皆1，STL不含材質。前後中上窗與小設備並非竣工逐格復原；來源終審不替代製造驗證。
