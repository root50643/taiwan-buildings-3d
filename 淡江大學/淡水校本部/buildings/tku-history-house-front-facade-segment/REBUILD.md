# 重建

Python 3.12，套件版本見 requirements.txt。

    python build_model.py
    python validate_model.py
    blender -b -t 4 --python render_model.py -- --out /absolute/path/to/package

build_model.py 產生幾何、STL、彩色3MF與構件資料。validate_model.py 檢查拓撲及格式一致性。render_model.py 使用實際輸出網格渲染，並將原始構件保留在 Blender 隱藏集合。隱藏構件允許原始建模重疊，不是正式列印輸出。

座標以正面朝負Y，並非實測方位。每個名義單位轉為7毫米模型尺寸，不代表真實建築比例尺。未試印。
