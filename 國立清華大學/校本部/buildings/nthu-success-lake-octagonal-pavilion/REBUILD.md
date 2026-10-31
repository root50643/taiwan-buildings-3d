# 重建

Python3安裝requirements.txt後依序執行：
```
python build_model.py
python validate_model.py
python verify_rebuild.py
blender -b -t 4 --python-exit-code 1 --python render_model.py
blender -b --python-exit-code 1 --python verify_scene.py
```
Blender需支援NumPy。渲染使用Cycles32samples固定seed0，六視角同一mesh-data.npz；無外部貼圖。
生成器先以雙精度輸出布林網格，再量化0.01mm座標、移除退化面並重新檢驗拓樸，避免STL單精度使極細碎面崩潰。最大座標量化偏差0.005mm/軸；這不是建築精度宣稱。
