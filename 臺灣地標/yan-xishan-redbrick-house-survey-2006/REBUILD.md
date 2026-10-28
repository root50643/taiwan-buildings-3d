# 從原創腳本重建

建議複製正式包到新目錄後執行，避免覆蓋審核凍結版本：

```sh
python build_model.py
python validate_model.py
blender -b -t 4 --python render_model.py
blender -b scene.blend --python verify_scene.py
```

驗證環境為Python3、numpy2.5.4、trimesh5.2.0、manifold3d3.5.4、Blender4.3.2。相依列於requirements.txt；腳本不會自行安裝、下載、上傳或存取原始PDF／照片。Blender內建numpy供渲染。輸出毫米、名義1:100；STL無材質，3MF保留色彩。Blender的隱藏EDITABLE構件仍互相重疊，僅唯一可見融合模型可直接拿作列印網格。

`validate_model.py`重新讀STL／3MF，與mesh-data.npz逐面比對；`verify_scene.py`重新開scene比對頂點、面與全部evidence。3MF ZIP時間戳和Blender容器可因重建時間改變；網格陣列／STL／XML內容比較才是重建依據。六圖由同一融合網格實際渲染，前正視是微俯角正交視圖而不是嚴格立面投影。
