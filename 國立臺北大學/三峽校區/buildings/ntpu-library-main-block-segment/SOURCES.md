# 來源、版本及近似範圍

本次是既有 `ntpu-library-main-block-segment` 的完整圖資外觀升級，保留 identity、不增加建物套數。原完整42檔（包括21檔舊彩色）另有精確恢復證明。

## 原始來源

- [ArchDaily 作者供圖專案](https://www.archdaily.com/594432/taipei-univesity-library-liao-architect-and-associates)：LIAO Architect & Associates；攝影 Xiao Xiong Liang Yan；文章2015-02-13，project year 2014。採完成照片01–08、14、15、17、18、20、22、29、30（16張），以及作者刊載31–38 B1–7F平面（8張）。
- [建築師專案說明](https://liaoarch.wixsite.com/liaoarchitect/library)：雙高翼、後方資訊中心、通湖軸線；作者所述35.95m及B1+7層只作比例參考，不是測繪尺寸。

24張主來源由研究者、builder與獨立審查者親看；本來源摘要作者核對封存bytes及審查記錄，不冒稱重新親看全部影像。僅使用正常公開slideshow圖，沒有取得需登入的original-size或CAD。原圖、HTML、metadata及請求紀錄保持私有，不隨公開模型配送。

## 建模對應與禁止誤讀

完成照與31–34確定雙高翼、資訊中心雙低翼僅兩個使用樓層及其上露臺、2F軸線／通湖平台／端階、局部B1下沉庭院。34–38及完成照辨識**五座平橋、兩座真階橋**；下層玻璃頂投影不是新階梯，不能重複建4F5F或6F7F階橋。兩側S表皮不同；翼屋頂、中央透光罩及低翼露臺必須區分。

39–45概念圖只作排除與版本衝突辨識，不能提供最終尺寸、樓層或屋頂。45多出低翼樓層與預留PV不是建成證據；46–53 Render1–8不作實景。沒有完整RF、四立面、竣工剖面或實測尺寸。檐曲率、細框、欄杆、遮擋處為有界近似或省略；玻璃使用不透明展示外觀代理，非室內施工模型或校準RGB。橋內封閉空腔為玻璃代理的幾何結果，不能以多邊界殼冒稱多個離散固體。

## 日期

目標為**2014完成照片系列及作者公開平面**，不是2026現況保證。11張照片EXIF Original/Digitized為2014-09-25或2014-10-29，無capture timezone；05/06/14/18/29缺拍攝日，不能從鄰圖補值。2015-02-03 modification不是拍攝日。平面XMP CreateDate2015-01-06+08:00是匯出，非核定日；原JPEG部分XMP格式錯誤不修造日期。舊包2013 completion-era與文章project2014的差異保留，不新宣稱精確竣工日。

## 封存綁定

下列SHA256由實檔重新計算；完整24張來源的逐檔SHA256與尺寸見 `qa/source-validation.json`。

- `SOURCE-HANDOFF.md`：`cce6560dab13df6e7274416f4b47c25d41beaece5558c22a06a641dc0673d177`（11229 bytes）

- `source-manifest.json`：`6dbd1565e6e2d1fe4b17823c24bd719a1698d59c2a4a2024c988e11f0fa42419`（10873 bytes）

- `independent-source-review.json`：`78985bc7e505c4c8439df44065bf2f487e8ca21ab6239a2557fa4b724f56d5e7`（20346 bytes）

- 包外 `ntpu-library-drawings-source-confirmation.json`：`bbd17470d307667bd195c85080c90a9677cba1602c251a8d9fda36f8e4a7ced1`（2395 bytes）；另將最終源審綁定的47檔逐一重算bytes/SHA，全符。此是源封包閉合證明，不冒充模型完成審查。
