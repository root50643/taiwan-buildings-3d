# 可重建流程

以 Python 3 安裝 requirements.txt 所列已知建模依賴；Blender 4.3.2 渲染。參考照片不參與程式建構。

```sh
python build_model.py
python validate_model.py
blender -b -t 4 --python render_model.py
blender -b scene.blend --python verify_scene.py
```

請在獨立目錄複製腳本後重建，比較vertices/faces/materials三陣列及parts/STL；不要在已發布凍結資料夾內任意覆寫。沒有聲稱在實體印表機試製成功。
