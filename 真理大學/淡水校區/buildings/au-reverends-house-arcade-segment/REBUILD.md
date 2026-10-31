# Rebuild

Python 3.12 with packages in requirements.txt:

    python build_model.py
    python validate_model.py
    blender -b -t 4 --python render_model.py -- --out /absolute/path/to/package

The build writes model.stl, model.3mf, mesh-data.npz, editable-parts.json, construction-parts.json and build-summary.json. Geometry is authored from nominal photographic proportions, not measured building dimensions.

A deterministic exact-coordinate weld removes repeated float32 vertices from Boolean output; zero-area triangles are removed while preserving face material IDs. QA checks the resulting topology and the exact STL/3MF correspondence. Rebuild verification must compare mesh values and not rely on ZIP timestamps.

Blender renders the actual output mesh, stores editable pre-union components hidden, and saves scene.blend. Reference photos are not embedded. The hidden construction parts overlap by design; only the visible union mesh is the validated printable representation.

Front faces negative local Y. The geographical orientation is not asserted.
