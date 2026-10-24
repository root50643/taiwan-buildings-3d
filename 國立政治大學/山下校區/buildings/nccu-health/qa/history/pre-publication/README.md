# 國立政治大學 健康中心大樓 — private exterior study v5

完整地上1F–4F、R露臺及屋頂梯房條、右側不對稱尖翼與附屬入口階梯的多色比例模型。不是單入口局部；不是量測竣工圖、2026現況調查或可列印保證。新建identity，未替換或發布任何舊模型。

## Files
- `scene.blend`: editable Blender 4.3.2 mesh and six editable opaque materials.
- `model.3mf`: one connected mesh with per-triangle six-material assignments, millimetres.
- `model.stl`: identical raw triangles, monochrome STL (no material or transparency).
- `previews/`: five 1200px actual-mesh views; studio background is not delivered geometry.
- Python generators, validators, `mesh.json`, `palette.json`, QA evidence, source/rights notes.

Main dimensions approximately **138.316 × 58.800 × 68.880 mm** including low outline-following display plinth. Design units were proportionally traced from emergency plans, not verified metres; no claimed real-world scale. 4 mm/design-unit is an output sizing choice.

## Evidence fidelity and bounded simplification
The asymmetric body follows registered 2F–4F/R outlines. The 1F principal rectangular return and horizontal wing edge form a **deep triangular open entrance recess** under the upper diagonal enclosure, not an upper-floor outline extended solidly to ground. A low triangular landing and four coarse attached steps occupy only the floor zone. Door proxies are on the real X=20 return, and the photographed low triple windows at both ends are approximately placed on the corresponding Y=9 wing return and X=20 main return, not floating on a fictitious diagonal ground wall. This prioritizes the plan; exact photo window-to-plan correspondence remains inferred.

The small opposite stair projection exists at 1F–3F and is omitted at 4F/R. The R access/room strip is modeled with approximate height. The small R-sheet inset is **B1**, not an extra roof building. Unexposed basement interior and internal room partitions are omitted; the solid interior exterior proxy is not a claim that the real building lacks rooms. Open terrace and entrance void are preserved.

Only the photographed diagonal entry carries dense black louver relief, two approximate vertical columns of three framed openings, lower glazing, projecting top cap and cream tiled-end proxies. Exact blade/tile counts, floor heights, roof-room height and inaccessible facade fine windows are unknown; back/far faces remain neutral rather than mirror-invented windows. No source image pixels or textures are embedded.

Coordinates: X=(original raster Y−125)/20, Y=(original raster X−125)/20. Accounting for image Y-down this is a proper90° rotation, not a reflection. Axes are not surveyed compass directions. Identity is 健康中心大樓 (photo also 身心健康中心), official inventory60-15. Campus sublabel and full building address remain unverified; photograph117 alone is not a full address. Do not use the historical unverified 指南 label.

## Manufacturing warning
Raw topology and SAT checks are geometric checks, not printer qualification. 345 unrounded horizontal sections include **11 warning layers** with positive thin islands under0.8mm erosion. Small frames/louver relief nominal0.4mm, parapet nominal0.8mm. 512 normal-ray samples have190 below0.8mm and minimum sampled0.399898mm (not exhaustive). Step safety nosings and backed fine relief are small details. Deep entrance soffit and projecting cap need slicer/support review. No physical print, load/strength test, support-free assertion, global minimum-wall certification or machine-specific slicing has been performed.

## Rebuild
Use Python dependencies in `requirements.txt` and Blender4.3.2. `python build_model.py` rebuilds STL/3MF/mesh/palette. `blender -b -t 4 --python-exit-code 1 --python render_model.py` rebuilds five PNGs and Blend. `python qa_model.py`, `python check_features.py`, `python verify_exchange.py`, Blender `verify_scene.py`, and Blender `verify_render.py` run detailed checks. `python rebuild.py --output NEW_EMPTY_DIRECTORY` generates all geometry and five views in a new isolated directory and byte-compares all nine deterministic artifacts. Blend bytes are not claimed deterministic because scene paths/session metadata can differ.

Private study only. See `LICENSE.txt` and `SOURCES.md`; no broad CC license selected. No main/navigation changes, Git stage/commit/push or public release.
