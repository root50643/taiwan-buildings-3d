# A1 實照近似配色展示主版

展示與建模不受四色或印表機工具數限制。此版以已核實照支持的七個細材質身分，呈現米白牆／淺框、磚橘紅貼面、灰立面、灰綠屋面、深藍太陽能板、青綠玻璃與獨立深灰展示底板。八個語意網格保留，材質可繼續編輯、細分；七種是目前資料支持的分組，不是日後色數上限。

| 正面 | 背面 |
|---|---|
| ![多材質展示正面](previews/front.png) | ![多材質展示背面](previews/rear.png) |

![屋面與太陽能板分色](previews/roof.png)

[可編輯展示場景](scene.blend) · [來源與配色界線](../multicolor/COLOR-EVIDENCE.zh-TW.md) · [已公開細材質表](../multicolor/color-evidence.json) · [另選四色列印合併方案](../multicolor/README.zh-TW.md)

- 灰綠金屬外觀屋面、深藍／藍紫PV及灰立面分開顯示，沒有為四工具預算合為同色。
- 顏色是人工視覺選擇的 sRGB 近似值，無色卡、油漆規格或校準反射率。照片所標日期未核驗，不能當成2026全棟現況。未知面、玻璃反射／窗簾、細窗框色差仍有簡化。
- 底板是展示選擇，並非實地地坪色。原有外觀近似幾何與全部列印檔未變；本次沒有用配色重造未知建築細節。
- `scene.blend` 使用八個原語意網格、七個可編輯材質、毫米單位。來源 core 3MF 只提供既有幾何；本展示主版不按其中四工具材料表合併顯示。
- 原四色 PRINT 仍作獨立可選製造衍生版。展示材質數不等於已配置或驗證的噴頭數；本次未重切片、未試印。原無支撐 NO-GO、支撐清除、黏結及真機設定限制繼續適用。

## 重建與這次檢查

在模型根目錄執行：

```text
blender -b --factory-startup --python appearance/source/render_appearance.py -- --three-mf multicolor/a1-four-tool-core.3mf --output appearance --samples 64 --threads 6
```

此次使用Linux Blender 4.3.2，不宣稱與舊平台或其他版本逐像素相同。生成時及另行重開都檢查八區原 float32 幾何、三角形與場景變換；只改展示材質，原 3MF／STL／單色與四色場景均不回寫。PNG另外移除metadata並確認像素不變。實際結果及輸入雜湊見 `validation.json` 與 `render-geometry-check.json`。重建輸出後須重新清理PNG metadata，不能把重新渲染當作新的製造驗證。
