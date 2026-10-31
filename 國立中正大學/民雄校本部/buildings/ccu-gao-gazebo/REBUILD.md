# Rebuild

Requires Python with numpy, trimesh, manifold3d (see requirements.txt), plus Blender with numpy.

```sh
python build_model.py
python validate_model.py
blender -b -t 4 --python render_model.py -- --out "$PWD"
python check_framing.py
```

The generator creates the unified mesh, STL, face-colored 3MF, source component JSON and build summary. The renderer uses the actual unified mesh, saves scene.blend with hidden editable overlapping source components, then renders six views without source textures. Do not print the hidden overlapping construction collection as a finished mesh. Render hashes can differ between Blender versions/hardware; numerical geometry checks remain separately recorded. No measured scale or trial-print claim.
