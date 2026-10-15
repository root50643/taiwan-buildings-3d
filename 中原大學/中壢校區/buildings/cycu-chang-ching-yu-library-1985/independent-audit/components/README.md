# CYCU Chang Ching Yu Library: component, local-root and boundary supplement

This supplement accompanies the unchanged original `model.stl` for `cycu-chang-ching-yu-library-1985`.

Required model SHA-256: `76939c4a6901112a66b76a6c87de5b76829de584bcac9b61e2d5b2a301a36e86`.

The static reports preserve the independent audit's original facts and status. In particular, the per-original-Polygon 1% condition remains false, and the reports' `exception_approval: false` records that the audit itself did not grant an exception. Any later specific exception decision is separate; it does not convert the failed strict condition into a pass.

## Findings and the two polygon conventions

The independent calculation reconstructs the original float32 STL's XY sections at z = 0.071 + 0.2k mm, without rounding, repair or simplification. Every original Polygon is opened separately with radius 0.4 mm. Bounds are used only to match author records, never as replacement opening geometry. All 695 Polygons across 273 layers survive erosion/opening without splitting. There are 47 warning samples above 1%; these are cross-layer samples, not 47 physical columns.

| Warning family | Samples | Independent maximum loss | Independent minimum retained | Minimum sampled original-face normal first chord |
|---|---:|---:|---:|---:|
| Roof grid cells | 32 | 6.689107046674% | 93.310892953326% | 1.437126159668 mm |
| Roof outer rings | 8 | 2.167611275417% | 97.832388724583% | 1.077842712402 mm |
| Sloped parapet | 7 | 2.283668789571% | 97.716331210429% | 2.155691146851 mm |

The author rounds section XY coordinates to 1e-6 mm and reports a maximum individual loss of 6.689108533024%. That convention is retained separately. Under author rounding, the family maximum loss / minimum retained values are: cells 6.689108533024% / 93.310891466976%; outer rings 2.167611416766% / 97.832388583234%; sloped parapet 2.283668978663% / 97.716331021337%. All 47 author warning WKTs and their independent original-STL counterparts are preserved in `components-evidence.json.gz`; reopening each author WKT exactly reproduces its reported loss. The maximum loss-fraction difference is 3.1681505294200996e-8 among warnings, and 7.619386591591862e-5 across all 695 records. The latter occurs in a low-loss Polygon at z = 53.071 mm. Neither convention is substituted for the other.

All 47 warning losses lie inside the 0.41 mm disks around actual outer/hole ring turns greater than 0.1 degrees. This statement applies only to those 47 samples. Across all 695 Polygons, 331 have a strictly nonzero outside-mask residual, including 308 above 1e-8 mm²; their maximum is 0.04417537599911031 mm². Those records remain below the 1% warning threshold. The true-corner mask is not a bounding-box mask or a mask made from every triangulation vertex. Each warning outer ring has 4 outer corners and 44 hole corners.

## Local original-face normals and roots

There are 540 paired XY/actual-original-face normal probes over all 47 warning samples. Their original first-entry/first-exit intervals are retained. All orientation controls pass. The seven probes on the actual sloped original face have first chords of 16.129531258689–17.396994915976 mm; these are distinct from XY chords and are not substituted for shorter directions.

All 47 original-Polygon representative-point downward rays first exit at z = 0. Complete original-triangle solid-angle controls check each root start, midpoint before the first downward exit, and point after that exit. These are sampled local roots and chords. They do not prove global minimum wall thickness, contact everywhere, support-free printing, or successful physical printing.

## Post-exit surface-boundary rays

The prior full original-face screen selected 18 rays with 41 post-first-exit triangle intervals. The portable verifier reconstructs these 18 rays directly from the original STL triangles and the same documented barycentric weights; it does not require the full parent CSV, a private audit directory, or a precompiled binary.

Exact rational original-weight points and source-normal relations prove all 41 horizontal original-surface intervals are coplanar. Independently recast first-material lengths equal the original exact-event results. The 1,328 complete-mesh winding controls comprise 18 source-outside, 162 first-material, 574 inward-side and 574 outward-side checks. At seven stations per boundary interval, both 1e-5 and 1e-6 mm normal offsets are checked. All pass; the reference maximum winding error is 1.2434497875801753e-13.

These intervals remain **boundary**, not air and not an extension of the first material segment. The verifier covers this selected set of 18 rays; it does not independently rediscover the entire dense screen or establish a global thickness minimum.

The embedded prepared-query witness retains a parsing diagnostic: pandas' default CSV parser displaced 24 intervals on 12 rays by one coordinate ULP. The original exact C++ computation used face/sample indices to reconstruct its actual rays and ignored those prepared coordinates, so this diagnostic did not affect its results. The primary geometry verification here likewise uses original triangles and weights.

## Portable rerun

Place this directory at `model/independent-audit/components/`, beside the original model's `model.stl` and `feature-loss-locations.json.gz` two directories above it. Inputs are read-only. Do not copy any private audit workspace into this package.

Reference environment: Python 3.12.14, NumPy 2.3.5, Shapely 2.2.0, GEOS 3.14.1. The boundary verifier additionally needs a C++17 compiler with OpenMP support (`g++` by default). The complete winding source is included in `winding_controls.cpp`; compilation and triangle/point buffers use a runtime temporary directory.

From this directory:

```sh
python audit_components.py
python audit_boundaries.py
```

The model directory defaults to `Path(__file__).resolve().parents[2]`. Fresh results go under `recheck/components/` and `recheck/boundaries/`; static reference evidence is not overwritten. Explicit relative paths are also supported:

```sh
python audit_components.py --model-dir ../.. --output recheck/components
python audit_boundaries.py --model-dir ../.. --output recheck/boundaries --cxx g++
```

Both scripts verify the STL hash. The component run also reads the original author `feature-loss-locations.json.gz`; its required hash is in `provenance.json`. The boundary run embeds only the selected ray/event/witness seeds and recomputes all geometry and winding controls from the original STL. No network access is needed. Gzip timestamps and script/compiler hashes can differ on rerun; compare decoded numerical/WKT/ray payloads rather than gzip bytes alone. Different geometry-library versions can produce slightly different numerical buffer results; use the reference versions for exact reproduction.

## Files and provenance

- `components-summary.json`, `components-evidence.json.gz`: all original Polygons, author warning WKTs, original opening/erosion/loss WKTs and true-corner residuals
- `normals-roots-summary.json`, `normals-roots-evidence.json.gz`: all 47 warning samples, 540 probe pairs, original face IDs, barycentrics, first intervals and root controls
- `boundary-summary.json`, `boundary-evidence.json.gz`: the selected 18 rays, 41 intervals, exact geometry relations and 1,328 winding controls
- `audit_components.py`, `audit_boundaries.py`, `winding_controls.cpp`: portable rerun source
- `provenance.json`: raw audit basename/SHA to public file/SHA mapping, transformations, embedded environment and required inputs
- `reproduction-check.json`: independent execution comparison for the portable source
- `SHA256SUMS`: public-file integrity manifest

The six static report/evidence files are byte-identical copies of the raw audit outputs and contain no private absolute paths. The portable source changes only dependency/path/bootstrap handling; the original audit reports and the original model were not modified.
