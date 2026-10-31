# 重建

Python3安裝requirements.txt後：
```
python build_model.py
python validate_model.py
python verify_rebuild.py
blender -b -t 4 --python-exit-code 1 --python render_model.py
blender -b --python-exit-code 1 --python verify_scene.py
```
Blender需NumPy。Cycles32samples固定seed0，無外部貼圖。六視角均由mesh-data.npz實際網格渲染。雙精度布林網格量化0.01mm後清理退化面，以避免STL單精度塌陷；最大每軸0.005mm量化位移不是實體測量誤差。
