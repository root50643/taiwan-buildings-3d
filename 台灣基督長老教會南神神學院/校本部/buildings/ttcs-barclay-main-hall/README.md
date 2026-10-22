# 南神本館（巴克禮紀念館）｜彩色完整單棟外觀近似
台灣基督長老教會南神神學院，校本部歷史建築群北側本館。模型 ID：`ttcs-barclay-main-hall`。

採2024年修復完成外觀，並以2026年3月25日北正面局部照片交叉核對；不是1903原貌復原，也不是1957禮拜堂或西校舍。1903創建，1955–1956改為加強磚造並於1956名為巴克禮紀念館；本次工程2024-10-11竣工。

## 檔案與範圍
- `scene.blend`：可編輯網格、逐面材質與五視角設定，非單純貼圖。
- `model.3mf`：毫米、7種基礎材質，逐三角面指派；`model.stl`：相同實體幾何，STL不帶顏色。
- `previews/`：5張最終實mesh渲染，不是想像實景或AI圖。
- `build_model.py` / `render_model.py` / `rebuild.py`：可重建程式；`mesh.json`與`palette.json`為可讀資料。
- 兩層H形本體、較深兩端翼與凸出中央門廳、五座交接雙坡（3南北屋脊＋2東西屋脊）、四組成對谷線、四立面及入口均保留。北中央圈十字與尖塔、南中央四葉飾孔不鏡像混用。
- 西南二樓外接穿廊僅保留本館側實際矩形門口與短門檻，外接穿廊及西校舍排除。截斷是展示範圍，不宣稱實景存在封閉外牆；門口沒有補成對稱窗。

## 尺度、細節與製造界線
展示底座250×80mm，最高71mm。尺寸是圖比例估值，不是現地測繪；官方報告總樓板724㎡/756㎡兩種數字不一致，本模型沒有以任何一個反推精確尺度。
恢復後灰白洗石子、灰水泥瓦、深棕木框與金色圈十字採近似色，不採修復前綠框。玻璃為不透明微型化實體片；四葉孔以深色封閉凹面符號保留，不是可通風構造。門扇封閉，唯西南接口保留開口；室內只為封閉幾何/連通空腔簡化，不是房間或樓梯復原。瓦片細數、坡角、窗小分格、尖塔面數與端飾不承諾實測；未刻逐片瓦紋。尖塔尖端鈍化至約1mm。
未包含禮拜堂、西校舍、噴泉、樹木、圍牆校門。底座非完整校地。
**未實印，不宣稱免支撐或全域最小壁厚認證。** 屋簷、拱頂、接口與內樓板需要依打印方向與切片器評估支撐。0.2mm全高切片及0.8mm連通區侵蝕測試不是每個局部薄細節的厚度保證；請另讀QA與局部光線/剖面記錄。

## 重建與檢查
Python 3 + numpy/trimesh/manifold3d/shapely/rtree；Blender 4.3.2；交換驗證另需lib3mf。
```sh
python build_model.py
blender -b -t 4 --python-exit-code 1 --python render_model.py
python qa_model.py
python check_features.py
BUILD_PYTHON=/path/to/model-python /path/to/lib3mf-python verify_exchange.py
blender -b -t 4 --python-exit-code 1 --python verify_scene.py
blender -b -t 4 --python-exit-code 1 --python verify_render.py
python rebuild.py --output /new/empty/directory --blender blender --threads 4
```
詳見`QA.md`、`SOURCES.md`、`LICENSE`及`CHECKSUMS.sha256`。來源PDF與照片僅私有研究，不在模型包內。
