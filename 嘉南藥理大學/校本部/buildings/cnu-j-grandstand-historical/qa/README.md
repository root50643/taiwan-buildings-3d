# Independent geometry review

`geometry-review.json` is the final acceptance report for the frozen candidate,
with `model.stl` SHA-256
`a759a7e25e8a4818e1802668d51c1d21db88b312200ddc1406dbb968aee5343f`.
It reports `pass: true` and confirms the inputs did not change during review.

Run `python qa/check_geometry.py` with the package's `requirements.txt` installed.
The script reads the generator in memory and never invokes its file-writing main
routine. It does not modify STL, parameters, assembly placement data, or the
generator. It rewrites only `qa/geometry-review.json`.

The triangle test independently checks actual face contact in the original STL
coordinate system. It permits ordinary shared edges/vertices, records unexpected
contact with original face coordinates, and checks coplanar overlap explicitly.
Assembly collision tests use solid intersections, rather than only bounding boxes.
The JSON preserves thresholds, versions, hashes, bounds, counts, and limitations.

`geometry-review-superseded-pre-freeze.json` preserves the first run as evidence.
Its final `pass: false` was caused by `input_sha256_unchanged_after_review: false`
when the model author made the last appearance correction during the run. Its
individual geometry checks passed. This superseded file is not the acceptance
report; the subsequent frozen-input review passed.

These checks do not certify a physical print, glue strength, material tolerance,
printer calibration, or support removal. Manufacturing review is separate.

`scene-review-superseded-coordinate-sort.json` preserves an initial scene check
whose rounded lexicographic row matching rejected identical geometry at decimal
bin boundaries. The corrected `check_scene.py` keeps original coordinates and
the original 1e-5 mm threshold, checks bidirectional nearest coordinates and exact
mapped triangle sets. `scene-review.json` passes with 0 mm maximum coordinate
error, equal triangle sets, and no external images or linked libraries.

`tool-failures.json` records the failed OpenGL Workbench render. Delivered
previews use CPU Cycles and are bound to the final STL in render-manifest.json.
