# 來源與配色依據

2026-10-22親看完整官方正前實拍、斜側照、原灰模preview及generator/native。官方頁未標攝影日期，但原檔EXIF有拍攝時間metadata；存取日不當攝影日，來源照片僅研究，不隨包散布。

- [中正官方大禮堂導覽](https://ccu-navigation.ccu.edu.tw/p/426-1253-4.php?Lang=zh-tw)
- [正前完整實拍637202457.jpg](https://ccu-navigation.ccu.edu.tw/var/file/253/1253/img/1556/637202457.jpg)：640×480，中心下層三角山牆內灰藍分格玻璃、灰石框可辨；只支持本次唯一前向背板表面。
- [斜側柱廊完整實拍629279318.jpg](https://ccu-navigation.ccu.edu.tw/var/file/253/1253/img/1556/629279318.jpg)：640×480，82147 bytes；只顯示柱廊/磚牆/窗，不含所選玻璃，不能當玻璃側背交叉證據。

原generator的三角凹槽由(-28,55),(28,55),(0,74)、y=-13.5、depth2.7定義，背平面為y=-12.15；框另有面。面選擇逐三頂點檢查完整三角範圍。磚牆混灰色帶不擴塗，未知朝向中性。

固定原始tree b5fad7b30b570adb9bf356ede62230eed681a1e7；原STL SHA256 6916e17e798b646ea36eaca7d8e1cf5867fa49d5eb6d31a6b9db8e5122b0bf79。原7檔實bytes與Git blob已自核，原native 619872 bytes、3522面，僅Warm stone單材料，indices[0]。配色不改幾何，模型身份只限前門廊段。

## 原JPEG日期metadata勘核
正前637202457.jpg：EXIF DateTimeOriginal與DateTimeDigitized均為2003:08:09 17:18:21；DateTime修改值2005:12:04 18:33:17。側照629279318.jpg：Original與Digitized均為2003:10:25 12:17:24；修改值2005:12:04 18:33:36。未有時區offset，不轉UTC；相機時鐘未獨立核實，修改日不作攝影日，亦不稱2026現貌。
