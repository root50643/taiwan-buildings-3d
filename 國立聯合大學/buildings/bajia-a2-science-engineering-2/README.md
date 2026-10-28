# 八甲校區・理工二館（A2）

## 模型預覽

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| 正面與來源支持區域<br>![正面](appearance/previews/front.png) | 未見外側背面中性<br>![背面](appearance/previews/rear.png) |  |

## 八材質外觀


[來源界線與四視角](appearance/README.md) · [表面色 3MF](appearance/nuua2-appearance.3mf) · [可編輯場景](appearance/scene.blend)

中庭灰牆、淺結構、離散綠窗、灰綠屋面、既有藍灰光電板與草坪步道；未見外側中性，簡化高窗與磚帶差異明列，未增加或切分幾何。 配色對應既有 STL 幾何，未新增幾何。[單色幾何正面](previews/front.png)／[單色幾何背面](previews/rear.png)


依校方竣工空拍與官方理工學院相簿的多角度照片製作，並以校區示意圖核對三翼位置。保留 U 形中庭、三側多層量體、斜屋頂、屋頂角塔、前端較低的附屬量體，中庭步道分帶，以及屋頂太陽能板。

模型尺寸為 **150 × 145 × 58.20 mm**，包含底座。這是獨立展示小模型，**與集合內其他建築不是共同縮尺**；尺寸為照片估算，並非實測建築圖。

單色幾何預覽直接使用交付 STL 的幾何渲染。窗戶為封底凹槽，沒有用材質貼圖假造窗戶。

## 檔案

- [model.stl](model.stl)：毫米單位、底面 Z=0 的單一封閉模型。
- [scene.blend](scene.blend)：Blender 場景、實際網格及攝影棚燈光。
- [build_model.py](build_model.py)：可重新生成模型的 Python 程式。
- [render_preview.py](render_preview.py)：由 STL 渲染預覽及建立場景。
- [validate_model.py](validate_model.py)、[validation.json](validation.json)：數位網格檢查程式與結果。
- [evidence.json](evidence.json)：公開照片來源、可見特徵、推定及省略項目。

## 列印說明

- STL 以毫米為單位；底座平放列印。
- 建議從 0.4 mm 噴嘴、0.16–0.20 mm 層高、3 圈外牆及 10–15% 填充開始調整。
- 屋簷與局部線腳有小幅懸挑，請在切片預覽中檢查是否需要支撐。
- 窗戶凹槽、矮牆、屋頂及層間線條已採適合小模型的簡化尺寸；不要直接大幅縮小。
- 太陽能板使用加厚浮雕分格，省略細小支架。
- 未製作樹木、細桿燈具及金屬欄杆，以免形成容易折斷的小件。
- 已完成數位網格檢查，尚未實際列印測試。支撐、薄件和材料設定仍需配合列印機檢查。

## 重建

在本資料夾執行：

```bash
python -m pip install -r requirements.txt
python build_model.py
python validate_model.py model.stl --longest-edge 150 --output validation.json
blender -b -t 6 -P render_preview.py
```

渲染程式使用 Blender 4.3，會覆寫同名預覽與場景。所有檔案依程式所在資料夾定位，不依賴原製作電腦的路徑或外部照片。

## 驗證範圍

封閉性、法向、單一連通體、非流形邊與頂點連接、尺寸及底面接觸已檢查；在另一資料夾重建的 STL 亦與交付版本逐位元組一致。數位網格通過不代表實際列印保證，也不代表建築測繪精度。

## 參考與限制

- [校方校史：校園規劃](https://nuuarchives.nuu.edu.tw/p/16-1097-27990.php?Lang=zh-tw)
- [校方理工學院外觀相簿](https://secretary.nuu.edu.tw/p/132-1003-1097.php?Lang=zh-tw#spid=3)
- [校方八甲校區示意圖](https://www.nuu.edu.tw/var/file/0/1000/img/40/437241410.jpg)
- [校方理工二館完工後空拍照](https://nuuarchives.nuu.edu.tw/var/file/97/1097/img/828/06image045.jpg)

建築身分由官方圖說及清冊核對。空拍可見的中庭及屋頂為主要建模依據；未見背面、遮蔽轉角及窗帶採簡化配置。未重建室內、實際地下層、各系館精確分界、完整道路與植栽。另以校方相簿第 26–29 張照片補充太陽能板及入口外觀；未確認所有照片拍攝年月或其後外觀變更。

此為非官方建築詮釋。未收錄第三方原始照片；參考資料權利屬原權利人。儲存庫僅含自行渲染的模型圖片。
