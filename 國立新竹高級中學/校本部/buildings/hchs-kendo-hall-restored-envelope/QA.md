# 檢查範圍

`QA.json`：14項網格與格式檢查，含有限頂點、正面積、封閉、法向一致、正體積、單連通、每邊兩面、STL逐三角一致、3MF頂點/面/材質/毫米單位一致，以及STL重新載入封閉及正面積。

`REBUILD-QA.json`：全新目錄程序重建，頂點/面/材質逐元素相等與STL SHA256一致。

`BLEND-QA.json`、`FRAMING-QA.json`、`RENDER-BINDING-QA.json`：Blender網格一致、無參考影像內嵌、六視角取景和產圖時的網格/腳本/PNG雜湊綁定。

`SOURCE-VISUAL-QA.json`：獨立來源外觀審核；未見背面配置依文獻推定，不是測繪重建。通過幾何檢查不等於完成實體試印或證明每項建築細節正確。
