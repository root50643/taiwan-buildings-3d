# 重建

Python 依 requirements.txt 安裝依賴後執行 build_model.py、validate_model.py，再以 Blender 執行 render_model.py；以 verify_scene.py 重開 scene.blend 驗證。獨立目錄重建 STL 與原檔 SHA256 完全一致。3MF ZIP 時間戳不主張位元一致；以頂點、三角面和材質索引逐一相等驗證。
