# 國立政治大學風雩樓 — private exterior study

完整主矩形、附著入口階梯／門廊與可見圓設備；實體三層對應 B1、1F、2F。不是四維堂，不包含整片歷史庭園、網球場或校園長廊。

本模型為官方完成照所記錄的外觀近似，官史舊照互證主框，不代表2026測繪現況或歷史花園復原。道路短面在 -X、相鄰庭園四跨長面在 -Y，B1 後退鏡牆前保留真空柱廊。v2以歷史近正視照片修正庭園長向40→28（道路向22維持），不以應急圖示異比硬定長寬。兩上層共用矩形；應急圖的異比不當作樓層退縮。未唯一配準的室內梯端不建；未知背窗中性簡化，不複製可見面。

RF 圖缺：屋頂為平頂近似閉合，設備只保留已見粗輪廓，不造塔樓／使用樓層。展示色不是實測 RGB。模型不含原圖、來源紋理或可辨識像素。

## Files and rebuild
- `model.stl`: monochrome print geometry (no material support).
- `model.3mf`: editable seven-material surface with same triangles.
- `scene.blend`: native editable Blender scene, millimetres.
- `previews/`: five actual-mesh views; no generated imagery.
- `build_model.py` + `render_model.py`: deterministic source geometry and previews.

Python dependencies: `requirements.txt`; Blender 4.3.2 used. Run `python build_model.py`, then `blender -b -t 4 --python-exit-code 1 --python render_model.py`. `rebuild.py --output /new/empty/path` checks exact STL/3MF/mesh/palette/five PNG bytes. QA scripts do not repair meshes.

Private technical study only. Source rights unresolved; no public release, commercial use permission or broad model license inferred. Not physically printed; see QA.md for numeric tests and manufacturing limitations.
