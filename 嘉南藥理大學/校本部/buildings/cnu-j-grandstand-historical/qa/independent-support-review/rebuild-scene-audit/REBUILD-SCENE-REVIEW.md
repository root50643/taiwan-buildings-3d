# 嘉南藥理 J 司令台候選：獨立重建、場景及預覽子審查

固定提交：`3a9a6041c5fde9ef2d6e9e96b02f24f025c8be5a`。本範圍 **GO，無重建或場景不一致阻擋**。這是總審查的一個子項，不以幾何／影像一致性推論可列印、接口實配或支撐可移除。

## 實際執行及固定檔案

已確認本機原目錄及主審唯讀副本可讀。在獨立 `rebuild-workcopy/` 只複製 `build_model.py`、`parameters.json`、`requirements.txt`，實際執行生成器，exit 0。原候選及主審副本的輸入雜湊在檢查前後相同，沒有執行原目錄生成器、另存原 Blend 或推送遠端。

實際重建的 **8 個零件 STL、組裝 model.stl 及 assembly.json 全部逐位元組相同**，不是只用記憶體幾何及 1e-5 mm 容差判定。每個 STL 另做保留繞序、重複三角形計數的有向 binary32 三角形比較，也完全相同。明細、固定／重建 SHA 和原始執行 log 見 `results.json`、`rebuild.stdout.log`、`rebuild.stderr.log`。

| 列印檔 | 數量 | 固定 SHA-256 |
|---|---:|---|
| `parts/main_body-print.stl` | 1 | `64205a0515ec83e40e56a2f855a256556490a1d759481741cef177d42b0b133c` |
| `parts/roof-print.stl` | 1 | `dbb9dfc7850219f8d40213cfb6c0cd944c1f30225dec2f6f3ae358370a9166cb` |
| `parts/column-print.stl` | 10 | `010e3512e0b420d9f40ae1ad7679314cfd841a931aa30a4d6e9ae05a8dd169da` |
| `parts/mast_brace_frame-print.stl` | 10 | `a0cb933ab1bdf6a26ccc20b573a1ea9a5f8a22df93868f6395885c8be3d80cef` |

組裝總覽 `model.stl`：`a759a7e25e8a4818e1802668d51c1d21db88b312200ddc1406dbb968aee5343f`；場景 `scene.blend`：`d7317f777f1c1a5e541ae7f70d505fa0d9dad72fd6b79385c76a848d3c77a048`。

## 實際 Blend

以 Blender 5.2.2 LTS 開啟交付場景並取 evaluated mesh，只有一個可見組裝 mesh 物件，identity 世界矩陣、scale 1，沒有 modifier。2,738 頂點／5,396 三角形的世界座標與原始 binary STL 的 **有向 binary32 三角形多重集合精確相同，最大座標差 0 mm**；沒有使用 nearest-point 容差替代此比較。世界界限為 `[-107,-51,0]` 到 `[107,39,53.400001525878906]` mm，最後一值是 STL binary32 表示，與標示 53.4 mm 相符。

場景 units 為 METRIC／MILLIMETERS、scale_length 約 0.001；物件自帶的 assembly SHA、22 件、歷史照片組合及勿直接列印總覽警語相符。單一 mesh datablock 含 22 個分體是總覽的合理表示，不能因此當作一個可直接列印連通實體；22 件、231 組碰撞與接口由另一獨立子審查處理。

目前場景沒有外部 Library、FILE 型圖片或 packed 圖片；僅有 Render Result／Viewer Node。檔案瀏覽器當前路徑為 `//`，輸出路徑相對，uncompressed Blend 中作者清理器所用的私有 user-directory 字節模式匹配為零。已獨立確認清理後仍能開啟及幾何精確一致。**未提供清理前 Blend，因此不獨立聲稱重現了 privacy-review.json 的「原先 1 段」數量或清理前 SHA**；歷史紀錄保留為作者證據。

## 預覽範圍及一次獨立重渲

實際有 **5 張組裝預覽**（front、rear、side、front-low、top）及 **1 張 unique-print-parts**。六張都是 1100×760，實際 SHA 均符合 render-manifest；manifest 的 model／scene SHA 也符合實檔。已實看六張接觸表及全尺寸正面／獨立正面。前、後、側、低視點與俯視涵蓋大棚、10 組上構、開放棚下、階梯、側梯、中央平台與後側兩層／玻璃組成，沒有裁掉主要建築。低正面看不到斜撐深度是視角結果，其他角度補足。

直接閱讀 renderer 可見五張組裝圖均匯入交付 `model.stl`。`unique-print-parts` 則在總覽隱藏後，從四個 `*-print.stl` 各匯入一個，展示四種類型及印向，**不是 22 件完整份數配置，亦不應拿它跟組裝總覽做 mesh 相等判定**。它未顯示支撐，README 將它標為零件及印向，並另文保留主體需支撐，未發現把它標成免支撐成品的文案。

Saved Blend 在加入四件印向展示前已儲存，所以其中只有組裝總覽；相機為正面，ortho_scale 特意重設為 250。交付 front.png 的自動包框為 257.6317700195313。這只是儲存的開場框幅不同，並非模型不一致或無法重現。獨立重渲使用交付場景現有幾何／材質／燈光，恢復 renderer 的正面相機及自動包框；**只渲這一次，像素逐通道完全相同**。清除本次 PNG 的 Blender text/EXIF 後，檔案 SHA 也與交付 front.png 相同：`3987eae649e5e3565dcf8426291cda0537c0399babe154b510d0f791741f2e79`。

其餘五圖是實看、SHA 綁定、renderer 相機及範圍檢查，沒有假稱獨立重渲全套或從雜湊反推歷史製圖過程。沒有重新研究官方來源或做無關全庫測試。

## 交接限制

本子審查無環境或讀檔阻擋。列印支撐、50 接口、實配間隙及膠合強度須結合其他子審查後定案。仍須保留未實際試印、未試合、未拆支撐與未驗證膠強度，及真機重切的限制。`review.py` 遇既有 rebuild-workcopy 會停止，以免覆蓋已保存的重建證據；重跑請改用新的審查輸出目錄。
