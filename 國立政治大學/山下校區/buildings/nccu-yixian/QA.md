# Technical QA / bounded results

Geometry revision v10; STL SHA256 `626168f728c356d1fb73e9d1bede2ea69a5177cf5198a5d87da6de438cc0690f`.

- Raw binary STL: 6556 triangles, 3252 exact-coordinate vertices; one connected watertight, consistently oriented surface; positive volume598871.751 mm³. No nonfinite values, zero-area faces, duplicate faces, bad edges or vertex links. No healing in QA.
- Nonadjacent triangle SAT: 55647 broad-phase pairs, zero contacts; shared-vertex incidence excluded. This does not certify all adjacent-face foldovers.
- 412 sampled sections in total, including the near-top sample; ordinary sections use unrounded 0.2 mm spacing: all contours valid. **23 layers retain sub-0.8 mm positive components**. No exemption, thin-warning reset, rounding or wall guarantee.
- 1800 triangle-centroid inward normal ray samples; 540 below0.8 mm; minimum sampled0.389899 mm. This samples fine frame intersections and tips; it is not a full minimum-wall proof.
- Ten solid/air probes confirm central occupied-room mass, continuous roof, both end access volumes, true under-canopy/entry air, absent separate bridge span and real rear terrace setback.
- 3MF strict readback and actual material-alpha edit/save/reopen preserve other material values and triangle assignments; STL/3MF triangle order/coordinates agree; deterministic geometry rebuild.
- Blender editable-mesh/material and saved-camera reopen tests, clean-directory byteexact rebuilding, and independent reviewer results are tracked separately in qa reports. Do not infer an unperformed test from this checklist.

## Fabrication limitations
All source colors are opaque proxy materials, including glazing. Enclosed interior rooms are solid exterior-study masses; open entry recess and canopy void are real mesh boundaries. There is no included enclosed inter-building bridge and therefore no fabricated bridge interior cavity. White screen gaps are shallow exterior recesses backed by simplified solid room mass, not asserted full interior voids.

No machine-specific toolpath, physical print, strength or support-free certification. Fine mullions, sloped red canopy ribs, screen edges, balconies/terraces and entrance overhangs need actual slicer-specific analysis and support settings.

## Scope/safety
Historical technical verification was performed on private files without staging, commit, push, navigation or main changes. Temporary-pack union metadata is directory-scoped only. Offline publishing-safety regression is12/13, with one known stale hard-coded script-count assertion9 vs observed28; not a green regression suite and not a model-geometry failure. No cleanup authorization is inferred.
