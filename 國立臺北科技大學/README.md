# 國立臺北科技大學校園建築模型

目前 **4件**：紅樓與億光大樓完整外殼近似，以及一大川堂南端六開間、先鋒大樓北向前側兩個局部段。**不是全校完成**；兩個局部段也不是整棟。

各件含底座最長150毫米，獨立比例。依公開照片自建，未取用第三方3D網格；原照片不在公開包。

## 模型圖鑑

| 紅樓 | 一大川堂南端段 | 先鋒大樓前側段 |
| --- | --- | --- |
| [![紅樓](臺北校區（西校區）/buildings/ntut-red-house/appearance/previews/front.png)](臺北校區（西校區）/buildings/ntut-red-house/) | [![川堂局部](臺北校區（西校區）/buildings/ntut-yida-south-section/appearance/previews/front.png)](臺北校區（西校區）/buildings/ntut-yida-south-section/) | [![先鋒局部](臺北校區（南校區）/buildings/ntut-pioneer-north-section/previews/front.png)](臺北校區（南校區）/buildings/ntut-pioneer-north-section/) |
| [臺北工業學校紅樓](臺北校區（西校區）/buildings/ntut-red-house/) | [一大川堂校史館南端六開間段](臺北校區（西校區）/buildings/ntut-yida-south-section/) | [先鋒國際研發大樓臨忠孝東路前側段](臺北校區（南校區）/buildings/ntut-pioneer-north-section/) |

| 億光大樓 | 後續 | 後續 |
| --- | --- | --- |
| [![億光大樓](臺北校區（東校區）/buildings/ntut-everlight/previews/front.png)](臺北校區（東校區）/buildings/ntut-everlight/) | 尚未交付更多模型 | 尚未交付更多模型 |
| [億光大樓](臺北校區（東校區）/buildings/ntut-everlight/) | [其餘建物續接](coverage/) | [其餘建物續接](coverage/) |

[東校區](臺北校區（東校區）/) · [西校區](臺北校區（西校區）/) · [南校區](臺北校區（南校區）/) · [模型索引](model-index.json) · [全校範圍與續接](coverage/)

## 校區、別名與範圍

續接涵蓋西、東、南、林森、建啤，以及校外宿舍、虎頭山進駐基地與各未開發校地。研究清單40項不是實體棟數，更不是已完成數量。新校圖平台本次讀取未成功，不能稱最新可視化配置已全核。

2025西校區中正紀念館已改名學生活動中心，與東校區多功能中心工地不同。校史館2024遷入一大川堂，紅樓、宏裕三樓的舊用途不另計棟。先鋒新建工程名精勤樓，不把拆除的舊樓另外當现存；隆玉為原林森誠樸樓改建新樓。建啤只有部分基地撥用，南港宿舍僅敬業樓5樓，均需區分使用與整棟界線。

## 資料年代

億光按2017、2020及校方未標攝影日的多向實拍近似，首層樹遮與屋頂小設備仍有精度限制，不是2026現場測繪。其餘各件亦請依自己的來源年代理解，不能把網頁查閱日當拍攝日。

## 試印限制

底座朝下。原始網格、重建SHA、Blend一致性、全部0.2毫米有效輪廓與0.8毫米參考opening篩檢已執行；沒有實際切片器工具路徑或實體試印，不保證可印或免支撐。各件README載有懸挑、門廊及細框警示。

## 驗證程式修訂

四件均使用canonical-v3 fail-closed輔助篩檢，無效組合Polygon即非零退出，不再走buffer(0)修補。4件重跑成功、篩檢數值完全不變；這是驗證程式與文件修訂，所有STL/OBJ/Blend幾何附件保持不變。詳見[逐檔替換對照與重跑結果](validator-revision-v4.json)。

[一大川堂南段修復外觀限定配色外觀與來源界線](臺北校區（西校區）/buildings/ntut-yida-south-section/appearance/README.md)
