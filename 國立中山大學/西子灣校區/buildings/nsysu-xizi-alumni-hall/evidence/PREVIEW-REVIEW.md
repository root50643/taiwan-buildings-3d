# 西子樓 v4 最終預覽與來源範圍覆核

覆核日期：2026-10-18 UTC。已實際查看 v4 全部八張圖：front、rear、elevation-positive-y、elevation-negative-y、end-negative-x、end-positive-x、top、terraces。最後 terraces 重新放寬視野後也再次實看。完整逐圖雜湊、輸入指紋、座標證據與 main 計數核對見 `previews-v4-review.json`。

## 結果

未發現重大來源 GO 範圍錯誤。三層主量體、連接矩形與斜向翼、二三樓開放露台、二樓矩形露台更外伸、三樓斜翼房間退縮、平屋頂與較高玻璃菱形角塔均保留。未將所有樓板最外輪廓拉成封閉房間。新增 2.4 mm 局部護欄接點是列印加厚，沒有形成新房間或填滿露台。

第 1 頁右上額外廳與川堂連接、另繪廁所棟、地下室內部、細地形擋土牆及未證實細後立面依約定明示省略。省略不表示原物不存在。

## 最終檔案指紋

- STL：`05c1714f8b363075a2eb72cde39d21ef06eb0720f1b46336579eb48edbb1444f`
- Scene：`7e36ff21f3a234d528f16ca17f8f58658dbdfa8a8fa3e91f52ee39ee591cdd0a`
- Parameters：`465a3b0b02a12ed00fb0bb269985411e72e6df6b176b883b146e425ed1b3ed31`
- Render manifest：`6a2bcb11882f196d3e178948081b7f5bf1196d57472cc225654c243ecbbb1ec0`

八張實際 PNG 的 SHA-256 均與最新 manifest 符合；STL 與 scene 也與 manifest 符合。Parameters 與 build report 指紋相符。此核對只確認來源一致性，不取代獨立網格檢查。

## 保留的預覽失敗與修正

原 terraces 相機 orthographic scale 185 確有底座左邊裁切。以原相機位置 `(160,240,220)`、目標 `(0,5,22)`，將底座八角點 `x=±75,y=±50.730709075927734,z=0或3` 投影到 960×720，可獨立重算左界 `-4.4610618 px`。只將該張相機 scale 改為 195 後重繪，左界成為 `20.3830952 px`；右界約 911.91 px、下界約 673.99 px。替換圖已再次實看，底座完整留有邊界。其餘七張未變；此次修正未改 STL 或 scene bytes。

## main 與計數核對

獨立執行遠端 `git ls-remote origin refs/heads/main` 成功，main 為 `08604e70212673240173660584236e361221533f`，與本地 origin/main 一致。Git tree 直接數到 421 個 `school/campus/buildings/slug` 目錄，涵蓋 106 個新增目錄學校；`model-packages.json` 學校表也是 106 項、count 合計 421。

該 main 的索引為 492 套總模型（71 舊套 + 421 新目錄套）、460 套高教模型、32 套其他模型、全 repo 107 校。國立中山現有 administration、library-information、yatsen-hall 三件，沒有 xizi 重複。候選尚未公開，本覆核沒有增加公開計數。

## 剩餘限制

高度是照片推估，無公尺立面尺寸與精密測繪比例。照片拍攝日期未知，不能宣稱已驗證 2026 現況；PDF 的 2022-07-29 是文件 metadata。護欄、玻璃與細柱有列印加厚或簡化，各樓圖面原有像素對應殘差仍需披露。露台長跨距與懸垂需要切片支撐規劃；本覆核未執行或宣稱切片、實體試印，也不代替獨立幾何 QA。

本子任務只寫入此檔與 `previews-v4-review.json`，模型、參數、生成器、預覽、QA 及公開計數均未修改。
