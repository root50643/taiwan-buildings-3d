# 本輪研究終端狀態（2026-10-13）

11件外觀模型已通過本地完整幾何驗證與父QA：首批3件、第二批4件、第三批3件、第四批1件。剩餘45項資產中的33項evidence-gap及7項partial詳見inventory.json；這不是全校完成，也不宣稱網路上不存在其他照片。本輪在目前可讀來源下結束，盤點freeze。

## 已讀且實際檢視像素的主來源
- [校方2014新校區文章](https://enews.nttu.edu.tw/p/406-1045-36360,c4248-1.php)：逐一核對照片相鄰標題。news4為鏡心、news6為師範，未混稱。
- [校方校園環境照片](https://nshcm.nttu.edu.tw/p/412-1059-8230.php?Lang=zh-tw)：高解析主樓、宿舍與餐飲中心。
- [校方知本配置圖](https://ndga.nttu.edu.tw/p/412-1008-9291.php?Lang=zh-tw)：頁面及圖像成功讀取，並非失敗來源。
- [校方臺東配置圖](https://dga.nttu.edu.tw/p/412-1008-9696.php?Lang=zh-tw)：圖像成功讀取；需和年報拆除紀錄交叉核對，不能以舊標記證明現存。
- [校方首頁空拍](https://nwww.nttu.edu.tw/)：成功檢視校本部空拍；高空像素不足以代替小型建物的近距離立面。
- [官方宿舍介紹](https://wdsa.nttu.edu.tw/p/406-1009-96178,r669.php?Lang=zh-tw)：僅用外觀，不建室內。
- [英文網站工廠照片](https://english.nttu.edu.tw/)及[工廠介紹](https://pebc.nttu.edu.tw/p/412-1061-11129.php?Lang=zh-tw)：工廠身份与两角外觀核實；年報對應原中正堂。
- [113年報](https://irpub.nttu.edu.tw/Files/113%E5%AD%B8%E5%B9%B4%E5%BA%A6%E7%B5%B1%E8%A8%88%E5%B9%B4%E5%A0%B1.pdf)：成功下載、文字抽取，45項資產；第46列為合計。
- [102年報](https://www.nttu.edu.tw/var/file/0/1000/img/622/190330802.pdf)：成功下載，補鏡心A/B/D/E分列資料，不能忽略後來拆樓現況。

## 取得失敗的明確來源
下列為本次讀取結果，不宣稱網站永久失效，也沒有以未見像素推測幾何。
- 官方導覽頁 https://gke.nttu.edu.tw/UnifiedPortal/campus_guide/ 可讀，以下四張其頁面實際列出的照片均以urllib讀取回HTTP502：
  - https://gke.nttu.edu.tw/UnifiedPortal/campus_guide/uploads/points/p4.jpg（餐飲中心導覽）
  - https://gke.nttu.edu.tw/UnifiedPortal/campus_guide/uploads/points/p20.jpg（資源回收站）
  - https://gke.nttu.edu.tw/UnifiedPortal/campus_guide/uploads/points/p22.jpg（污水處理廠）
  - https://gke.nttu.edu.tw/UnifiedPortal/campus_guide/uploads/points/p23.jpg（綠建築）
- https://dga.nttu.edu.tw/var/file/8/1008/attach/10/pta_94778_2298123_09705.pdf（太陽光電屋頂初勘）：搜尋索引有臺東校區標名航照線索，urllib502，web讀取timeout；未檢視原圖。
- https://dga.nttu.edu.tw/var/file/8/1008/attach/15/pta_99861_1484096_70099.pdf（忠孝樓招牌規劃）：搜尋索引可見文字，web讀取cache miss；且模擬招牌圖也不能直接作現況竣工外觀。

## 有來源但不足以建新模型的主要情況
- 鏡心D：[第三方導覽](https://popworld.cc/guide/24560/webView)標D的照片含雙排棟群，可能混入已建A/B；官方空拍與資產分列只能確認有D，尚不能確認該照片所指範圍。暫存模型已隔離，不公開、不計數。E亦僅資產名，缺定位與外觀。
- 臺東科學館、綜合大樓、行政大樓、心動館、兒研所、教學大樓、體育系、游泳池及職務宿舍：已查兩校圖、年報、場地介紹與名稱搜尋；未取得可核實身份的足量正側外觀。面積/樓層文字與地圖方塊不足以建真實外形。
- 臺東學生活動中心：[官方會議](https://coce.nttu.edu.tw/var/file/5/1005/img/1046/344184598.pdf)確認現称創育大樓；工廠照片背景只有局部立面，缺整棟輪廓與深度。
- 臺東圖書館及擴建：兩資產須釐清相連範圍，搜尋大多導向知本新館，不能錯用新館照片。
- 臺東體操館：2024整修與2026啟用新聞可查，但需完整整修後外觀。舊木造館回憶文章不能直接代替現況。
- 臺東忠孝樓：官方住宿介紹主要寢室圖；不使用室內推测外殼。
- 候車亭：2014校聞及2017遊記早於109.12資產完工，缺現存亭身份與改建後照片。
- 投打練習場：搜尋大量結果屬附屬體育高中，不能移用作大學本部建物。
- 各車棚、廁所、回收設施、機電中心等：以校圖與年報確認名稱，缺逐一可核實的外觀/屋頂和所在校區定位。沒有蒐集或建模設備、室內、安防配置。
- 校圖額外名稱電算中心、幼兒探遊館、教研所：須釐清與年報資產別名，不任意增加棟數。

原始照片与含照片對照圖均未放入公開套件。已有公開來源網址可供後續補證；取得新來源後再續作。
