# Complete local rebuild recipe

Tested Python 3.12, numpy 2.5.4, trimesh 5.2.0, manifold3d 3.5.4; Blender 4.3.2 with bundled numpy. Standard library: pathlib/json/zipfile/xml.etree.ElementTree/struct/argparse/math. Rendering uses Blender bpy/mathutils, Cycles CPU, 4 threads, 32 samples, seed 0; no fonts, image textures, external models, or network resources needed. See requirements.txt for geometry Python packages.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python build_model.py
.venv/bin/python validate_model.py
blender -b -t 4 --python render_model.py -- --out "$PWD"
blender -b scene.blend --python verify_scene.py
```

Run from the unpacked output directory. Blender is a separate system installation, not installed by pip; `numpy` needs to be available in Blender's Python. Source geometry rebuild regenerates `mesh-data.npz`, STL, 3MF, construction-parts.json, editable-parts.json and build-summary.json. Render rebuild creates scene.blend, render-manifest.json and six preview PNGs. Scene references only local relative output path, no third-party assets. Editable authored components overlap by design and are hidden; print/export the unified visible mesh, not all hidden components.

QA pass is not printability or fidelity certification. Any rebuild invalidates existing SHA256SUMS/manifest and independent visual-review hashes; rerun geometry/scene checks, inspect actual images again, then regenerate hashes/package. Renderer/hardware/library versions can change binary results; no bit-identical render promise.

Geometry uses manifold3d CrossSection extrusion; scipy is not required. All geometry and materials are authored by code. Dependencies are listed in requirements.txt; no network needed after installing dependencies.
