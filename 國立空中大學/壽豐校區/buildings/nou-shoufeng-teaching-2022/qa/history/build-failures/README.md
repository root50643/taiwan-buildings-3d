# Build history

- v1: failed while creating the arch solid because prism triangulation repeated disconnected vertices. No completed assembly was produced.
- v2: failed final assembly volume validation. The independent report in `../build-v2/geometry-report.json` identified the roof parapet inner corner touching along an edge, not a full solid junction. The failure is retained.
- v3: corrected roof corner overlap; complete geometry produced. Superseded by the final photo-position refinement.
- v4: moved the estimated inner-corner headhouse toward the courtyard corner. The eight floor/ceiling STL hashes stayed unchanged; roof and assembly reference hashes changed. Final QA is bound to the current STL hashes in `../../geometry-report.json` and `../../slicer-summary.json`.

Warnings and failed historical flags are evidence of prior runs, not a claim that those earlier files passed. No physical printing, support removal, or dry fit was performed.
