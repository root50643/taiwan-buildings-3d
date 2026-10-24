# 東海大學 文理大道校友鐘樓

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| ![校友鐘樓模型](previews/front.png) |  |  |

**新增完整塔體幾何｜依2019官方相簿與2022攝影者照片近似；不是現場測繪，不宣稱2026現況。** 這是文理大道的校友鐘樓，並非教堂旁四牆式畢律斯鐘樓。

保留兩片深矩形牆、十一道深橫板、十個板間開口、下方高通道、往上漸增的間距、突出最高橫板的兩牆尖端、一口懸鐘和低矮矩形平台。上方鐘室包含固定加厚吊桿、喇叭鐘口、鐘舌及下板簡化小機構；非功能性可擺動鐘。

## 下載
- [可編輯 Blender 場景](scene.blend)：與 STL 同一三角網格，六種逐面可編輯顯示材質。
- [彩色 3MF](model.3mf)：顯示顏色，不是噴頭／AMS 指派。
- [STL](model.stl)：單一連通水密網格，格式本身無顏色。
- [生成器](build_model.py)、[來源](SOURCES.md)、[檢查報告](QA.md)。

設計尺寸 **102×34×152.5 mm**；塔身寬25、中央淨寬15、兩牆寬5／深14、橫板厚2.2、平台高2.5 mm。這些是照片比例與展示／加厚尺寸，**不是建築實測或精確比例尺**。兩牆上端細小裝置、線纜、精確接縫與洗石子顆粒省略；平台深度、鐘體內壁及機構簡化。僅含有界局部平台，不含整條大道或周邊草坪。

## 來源與界限
建模者逐張親看官方七張與獨立攝影者兩張，共九張完整照片。官方相簿標示2019-09-20不保證個別快門日期；攝影者文章記錄2022-01-09旅遊，圖片目錄2024/01為上傳／遷移線索，不當拍攝日期。官方影像僅303×480或640×480，無法推得細機械精度。比例取自多角度透視圖，不是正射測繪；不宣稱現今狀況不變。原始照片不隨檔再分發。

## 列印警告
水密不等於可直接列印。十一橫板下緣、懸鐘與鐘舌需要切片器支撐／方向評估；鐘壁局部低於0.8mm侵蝕門檻，詳見QA原樣保留的失敗。**無實體試印，不認證免支撐、最小法向厚度、強度或切片器相容性。**

## 五個實際交付網格視角

| 模型預覽 | 模型預覽 | 模型預覽 |
| :---: | :---: | :---: |
| ![背斜視](previews/rear.png) | ![正立面](previews/elevation.png) | ![頂視](previews/top.png) |
| ![左斜視](previews/left_oblique.png) |  |  |

## 重建與驗證
Python依賴見requirements.txt；另需lib3mf官方SDK、Blender4.3.2。
```sh
python build_model.py
python qa_model.py
PYTHONDONTWRITEBYTECODE=1 python check_features.py
BUILD_PYTHON=/path/to/model/python /path/to/lib3mf/python verify_exchange.py
blender -b --python-exit-code 1 --python render_model.py
blender -b --python-exit-code 1 --python verify_scene.py
blender -b --python-exit-code 1 --python verify_render.py
python verify_package.py
```
獨立空目錄重建比對STL、3MF、mesh、palette及五張PNG；修改後須全部重驗，不能套用舊QA。
