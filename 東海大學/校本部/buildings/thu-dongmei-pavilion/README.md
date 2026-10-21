# 東海大學東美亭｜歷史照片外觀近似模型

![東美亭實際網格透視](previews/front.png)

以東海大學官方牧場相簿與兩位獨立攝影者的2017–2019照片，建立東海湖旁的**完整東美亭外觀**，不是金門同名八角亭，也不是東海兩座鐘樓。校區沿用既有圖鑑「校本部」分類；活動頁亦稱二校東美亭。

## 交付內容
- `model.stl`：單一閉合連通網格，毫米；無色。
- `model.3mf`：相同三角面與座標、6組逐面可編輯顏色；顏色不是已設定的實體耗材／多料列印配置。
- `scene.blend`：同一真實網格、可編輯材質、燈光與相機；無參考照片、貼圖、外部依賴或嵌入執行腳本。
- `previews/`：五張1200×1200實際網格圖，前／後透視、開放長邊立面、頂視、短邊月洞正立面（檔名`left_oblique.png`為圖鑑既有欄位，實際相機為正立面）。沒有使用AI想像圖片代替網格預覽。
- `build_model.py`、`render_model.py`、`rebuild.py`：參數幾何、實際網格渲染、隔離重建比對。
- `qa*`與`verify_*.py`：原始拓樸、切層、局部負空間／薄件、交換格式、材質改色重存、渲染和重建紀錄。

## 外觀與推估邊界
兩端橘色格狀磁磚月洞牆、四角奶白支柱、兩側無中央柱的開放長邊、曲線雙坡橘瓦頂、白色彎曲山牆緣、山牆小圓洞、圓角階梯面板周圍真正的空隙、局部紅色三級平台均有照片依據。月洞開到地面，周邊狹縫保持中空，未把透空處填牆。頂部以規則39道瓦肋及簡化瓦縫呈現，並非逐片復原。

展示尺寸176×114×80.300mm，**全部長度、曲線、厚度和平台邊界是照片比例推估，沒有測量比例或圖說**。面板2.8mm、屋頂垂直厚2.5mm等為展示/製作近似；四角腳座、梁端和接合均簡化。另一端小圓洞與第二面無字匾額採對稱推估；牌匾原文不可辨識所以留白。未建湖面、島岸、樹木、整段步道或夜景前景大階梯。

**這不是實印驗證或免支撐保證。**屋頂下緣、飛簷、月洞拱冠、小圓洞、梁與懸掛牌匾需支撐／擺向評估；瓦肋與浮雕可能小於實際機器可可靠解析的細節。全部薄件警告保留於QA，不因網格閉合而宣稱可直接印。

## 重建
需Python套件`requirements.txt`及Blender4.3.2（驗證版本）。
```sh
python -m pip install -r requirements.txt
python build_model.py
blender -b -t 8 --python-exit-code 1 --python render_model.py
python qa_model.py
python check_features.py
python verify_exchange.py
blender -b -t 8 --python-exit-code 1 --python verify_scene.py
blender -b -t 8 --python-exit-code 1 --python verify_render.py
python rebuild.py --output ../rebuilt-dongmei
python verify_package.py
```
重建比對STL、3MF、mesh/palette及五張PNG全部bytes；Blend容器本身不要求跨次byte一致，但幾何、材質與重新渲染已驗證。修改模型後須重作來源終審及hash報告，不能繼續使用原QA當成新版證據。詳見[SOURCES](SOURCES.md)與[QA](QA.md)。
