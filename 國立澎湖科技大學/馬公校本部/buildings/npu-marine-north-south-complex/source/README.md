# Rebuild and inspect

All paths are package-relative; no private reference pixels are required to rebuild original geometry. Numeric traces and parameters are embedded in build_model.py / plan-trace.json. Dependency versions observed during this candidate are in toolchain.json.

1. From a compatible Python environment with numpy, trimesh, manifold3d and shapely, run `python source/build_model.py`. This replaces the current main models and assembly.json; it does not touch audit history.
2. Run `blender -b --factory-startup --python source/build_scene.py` with Blender4.5.13 or a compatible build. This writes scene.blend and eight images from exactly the STL meshes. Re-run `source/verify_scene.py` through Blender to reopen and compare vertex sets, triangle counts and physical mm extents.
3. Follow [QA tool instructions](qa-tools/QA-METHODS.md) for full mesh, section, thickness, assembly and actual-slice QA. The generic CLI needs an explicitly supplied local PrusaSlicer executable. The [control tests](qa-tools/control_tests.py) exercise real crossing, contact and legal mesh adjacency cases.
4. `python source/compare_plans.py` regenerates original linework only. It does not copy source images. Source-consistency review and per-revision seals are separate evidence, not regenerated approvals.
5. Strip all PNG text metadata after rendering and rebind preview SHA256 values. The delivered PNGs have already been scrubbed; Blender output may add host metadata on a fresh run. Keep scene.render.filepath relative and clear all FILE_BROWSER directories (included in both Blender scripts).
6. After refreshing report/input SHA bindings, `python source/seal_package.py` verifies the current evidence, private-path scan, links and file inventory. Original raw failures must remain under qa/history and earlier raw/trial directories. Rebuilding geometry alone does not update independent QA or source review seals.

The assembly reference STL is a concatenated placement reference, not a physical print object. Main print files are only models/01 through08, with07 repeated three times. Scene colors remain editable; no color textures or source pixels are embedded. All G-code is QA ONLY and not machine-ready.

Public delivery omits sixteen QA-only diagnostic G-code files and preserves their hashes in qa/diagnostic-gcode-exclusions.json. Rehydrating a matching private file or generating a newly checked slice is required before rerunning the independent path audit. source/seal_package.py validates disclosed omissions against that manifest; it does not claim to read omitted bytes.
