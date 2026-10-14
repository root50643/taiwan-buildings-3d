# 國立空中大學｜蘆洲校本部｜北院

紅色防漏坡屋蓋版，完整主體低細節近似。包含外環四翼、中央行政橫棟、前大後小雙庭院、內院柱廊與正門穿堂。這是一件原創外觀模型，不是測繪、歷史原貌復原、精確現況 BIM，也不表示全校已完成。

| 正面 actual STL | 背面 actual STL |
|:---:|:---:|
| ![北院正面](previews/front.png) | ![北院背面](previews/rear.png) |

[頂視](previews/top.png) · [側向](previews/side.png) · [正立面](previews/front_elevation.png) · [正門近圖](previews/gate_detail.png) · [柱廊視角](previews/courtyard_detail.png)

## 版本與依據

- 以官方北院完整配置圖、2024 出版校史資料《空大校園之美》的內院照片、2025-03-26 官方照片頁的正門照片及 Esri 完整屋頂俯瞰交叉建模。
- 2024 為資料出版年、2025-03-26 為網頁日期，均不保證照片攝影年。Esri 影像於 2026-10-14 讀取，拍攝年未知。本件不宣稱是 2026 精確現況。
- 保留照片中的後加紅色低坡防漏屋蓋；未去除屋蓋來推造歷史平屋頂。北院建造年在校內來源間有矛盾，僅稱源自道南中學時期、後經整建。
- 正面寬約 62 m、進深約 90 m 僅由屋簷外包絡影像估算，至少 ±5% 不確定；不是牆軸尺寸。高度、坡度與局部深度按照片比例近似。
- 中央橫棟在官方配置中列行政辦公室、4010 服務台及 4011–4013；未有可證實的中央穿越通道，本件不虛構中穿堂。

## 幾何與列印

- 單位：毫米。含底座 106 × 150 × 11.1 mm，最長邊 150 mm。底座厚 1.8 mm，底座朝下列印。
- 屋簷外包絡 99.2 × 144 mm，名義約 1:625；各館獨立比例，模型尺寸不代表建築測量精度。
- 大院屋簷間開放區約 67.0 × 64.8 mm；小院約 67.0 × 25.4 mm。兩院都通空至底座上表面，沒有封頂或填成樓體；不穿透底座。
- 柱廊有實際空間：典型牆至柱背淨深約 3.1 mm；廊地坪頂 2.23 mm，梁下 6.15 mm，最小淨高約 3.92 mm。柱斷面加粗為 1.5 × 1.5 mm，與廊地坪及屋面梁相接。
- 正門穿堂淨寬 7.4 mm、淨高約 5.69 mm；沿 Y 向穿越前翼，直接通向大院。水平射線已核實。
- 低坡屋頂保留至少 1.8 mm 平頂脊；屋簷底層厚 0.9 mm。門樓屋簷厚 0.85 mm、白色背女兒牆厚 1.3 mm。浮雕塊約 0.6 mm 深，完全背靠門樓牆，不是懸空細件。
- 柱廊、門洞與屋簷有懸挑或跨距；切片時需檢查橋接與支撐，尤其 7.4 mm 門洞及柱間。未做 Cura／PrusaSlicer 工具路徑或實體試印，不保證無須支撐或必然可印。
- PNG 與 Blend 的紅、灰白、黑色只是方便看形的預覽著色；STL 本身不含顏色，並非多色列印檔。

## 已揭露簡化

外牆未有完整背窗證據，使用中性牆面，沒有把正面窗格複製到背面。柱廊後方門窗以照片支持的單層低窗分組淺凹概括，不是逐窗測繪。正門車馬、渦紋與文字以厚實淺浮雕塊概括。精細屋頂折線、瓦紋、空調、植栽、內院景觀棚架、家具、其他校舍與地下構造省略。教室內部為可列印實體量體，庭院與柱廊才是本件驗證的空間。

## 檔案

- [model.stl](model.stl)：實際交付單殼列印網格
- [scene.blend](scene.blend)：直接由同一 STL 匯入的可編修網格、預覽材質及相機
- [build_model.py](build_model.py)：原創參數幾何；[requirements.txt](requirements.txt)
- [sources.json](sources.json)：公開來源、日期限制與特徵依據；不附第三方原照片／PDF
- [qa-summary.json](qa-summary.json)、[validation.json](validation.json)：完整檢查總結及原網格檢查
- [layer-component-check.json](layer-component-check.json)：0.2 mm 每層、每個原始 Polygon 的 erosion／opening 結果
- [layer-opening-check.json](layer-opening-check.json)、[thin-feature-check.json](thin-feature-check.json)：形態篩檢原始數值
- [open-space-check.json](open-space-check.json)：雙院、柱廊、正門真通空射線
- [preview-check.json](preview-check.json)、[render-manifest.json](render-manifest.json)：實際 STL／Blend 與圖片一致性
- [SHA256SUMS](SHA256SUMS)：逐檔雜湊，清單不雜湊自身

## 重建與驗證

使用 Python 3.12、requirements.txt 與 Blender 4.3.2。於本資料夾執行：

```sh
python build_model.py
blender -b -t 3 -P render_preview.py
python sanitize_previews.py
python run_all_checks.py
```

驗證程式採 fail-closed：原始三角形法向與繞序、每邊兩面、vertex-link 單環、單一連通表面、正體積、尺寸、獨立腳本重建 STL SHA、Blend 與 STL 三角形、PNG 從保存 Blend 再渲染逐像素一致均檢查。0.2 mm 層高以 z=0.071 mm 避開共面退化；每層輪廓 degree-2 閉合、每一個與組合 Polygon 合法，絕不先 repair 再判通過。以 0.8 mm 參考寬度逐原始 Polygon 檢查 erosion 與 opening，零消失、零分裂；這不是全方向最小壁厚保證。

0.2 mm 共 56 層、1,200 個原始 Polygon 均通過。最大 opening 損失 0.6641914251449216%，位於 z=10.671 mm 的門樓白色背女兒牆（16 × 1.3 mm 截面）四角；女兒牆底 z=9.35 mm 與門樓實體坡屋頂相交連接，沒有零件消失或頸部斷裂，未採薄件例外放行。

外觀經來源核圖審核後封存；正式 freeze 後不覆寫，後續修訂應另立版本。此資料夾只包含自製模型、渲染與引用，第三方來源原圖僅用於私下核對。
