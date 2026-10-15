# Original-STL support-root and opening-loss linkage evidence

## Frozen source and status

- Final geometry SHA-256: `0ff3e1a65202e528f2328a9372a058a0d1c79639c7ace4aa93fcd55e5ef4cea2`.
- Final `parameters.json` version: `1.1`; SHA-256 `60e2c8ea174ff3bef56bdd8a6b0595569f029220b9f0625a4efc5601f350d027`.
- 85,464 unchanged original STL triangles. No repaired, filtered, healed, remeshed, rounded, or resampled replacement mesh is used.
- All 26 source-declared column-to-shell roots have certified continuous material cores at least 0.8 mm in diameter. The minimum proved diameter is **0.918651631 mm**.
- The original strict morphology result is still **false**: 98 opening-loss failures remain. Supplemental linkage evidence is not a global normal-thickness claim or a print guarantee.

The actual exposed column caps stand approximately 0.2000 mm above the source-declared shell valleys. This fabrication geometry is retained explicitly. In detailed root records, the legacy field `actual_valley_top_z_mm` is the measured exposed head top, not a claim that the internal shell valley is exposed. The same records state `actual_head_top_above_declared_shell_valley_mm` and `head_top_interpretation`.

## What is proved

### 1. Continuous three-dimensional original-material core

Each source head has a vertical stem path and four connected paths entering the actual curved shell. Every complete path is bounded away from the entire original boundary by at least 0.4 mm, using original-triangle closest-point distances at no more than 0.04 mm spacing, the distance function's 1-Lipschitz bound, and a 0.000001 mm numerical guard. Spatially omitted triangles have a conservative 1.5 mm bounding-box lower bound, rather than a feature mask.

A separate long-double all-original-triangle BVH implementation verifies all 5,784 distance stations on all 130 paths. Its maximum disagreement with the primary calculation is 2.06e-14 mm. Whole-mesh compensated long-double winding establishes material side. The support evidence retains 1,976 direct original-triangle interval rays, 338 original-triangle section neighborhoods, and 6,668 material/air controls. First solid, next air, original face IDs, raw intersections and boundary overlaps remain available.

### 2. Every strict failed section and every lost piece

All 98 exact original section Polygons are tied individually to their source support heads. All 2,006 unchanged positive lost pieces are retained. Every source head lies strictly inside the kernel of its complete original Polygon, checked against every original boundary-edge interior half-plane. The minimum kernel margin is 0.526303987 mm. This proves complete radial coverage, not just pointwise coverage or a head bounding-box match.

Each Polygon contains a radius-0.4 mm section disk. All 5,587 original boundary-edge midpoint radial rays are checked against actual original triangles, with all material/air intervals retained and 16,761 whole-mesh winding controls. No narrow or unclassified ray was discarded.

### 3. Exact section height to three-dimensional core

All 98 radius-0.4 mm disks at their actual section heights fit completely within the already certified stem capsules. The highest section is 0.172800446 mm above its stem-axis endpoint; its complete disk requires a ball radius of only 0.435729267 mm. Certified stem capsule radii are at least 0.705550488 mm. The minimum full-disk containment margin is 0.269823372 mm. This explicitly links every section to the three-dimensional material graph; matching head indices alone is not used as proof.

### 4. Strict and numerical diagnostics remain separate

- All 98 stored complete lost-region WKB byte strings are identical to recomputed `original.difference(opened)` WKB. Both byte hashes are recorded.
- 395 lost pieces lack positive exact boundary overlap. Those diagnostics remain false. The pieces are not renamed boundary pieces or removed; complete containment and complete-Polygon radial coverage supply the linkage.
- 1,326 direct `covers()` results remain false. Re-intersection produces 1,254 minute excursion fragments affecting 948 pieces. Every complete fragment, WKB, vertex projection, original segment, and original face ID is retained.
- The largest measured complete-fragment distance to its identified unchanged original segment is 5.128e-12 mm. Including the 1e-9 mm numerical guard, the maximum bound is 1.005128e-9 mm.
- A declared 1e-8 mm envelope applies **only** to these individually bounded Boolean excursions after exact lost-region construction identity has been verified. It is not a general geometry tolerance, buffer, waiver, or morphology exemption.

## Final report gates

All reports below are in `root_evidence/`, with separately hashed compressed details.

1. `root_support_report.json`: `passed` must be true.
2. `root_clearance_report.json`: `passed` must be true.
3. `root_loss_report.json`: preserve `bounded_radial_evidence_passed=false` and all 395 exact-boundary-overlap diagnostics. This older stronger boundary-identity diagnostic is intentionally not the complete-linkage gate.
4. `root_section_connection_report.json`: `passed` must be true; exact case keys are retained in `root_section_connection_details.json.gz` under `disk_connections`.
5. `root_complete_loss_linkage_report.json`: `complete_loss_piece_linkage_evidence_passed` must be true. Complete case keys, source WKB, original-edge kernel distances and lost-region byte hashes are in `component_fan_proofs`; all 2,006 unchanged piece proofs are in `all_loss_piece_linkage_proofs`.
6. `root_tests/root_controls_report.json`: eight source-preserving ray/clearance controls must pass, including a 0.79 mm thin box and a genuine air gap that cannot be chained into material.

Section-connection negative controls reject an unlinked disk and a failed root certificate. Complete-linkage negative controls reject an outside piece, failed root, unlinked exact-height disk, and failed complete-Polygon fan. Strict morphology remains false in every relevant final report.

## Reproduction

Use the pinned project requirements and a C++17 compiler with OpenMP. Run from this directory after `build.py` and `qa_sections.py` have generated the unchanged STL, manifest, and full exact section WKB:

```sh
python check_root_supports.py --stl output/model.stl --manifest output/build-manifest.json --parameters parameters.json --out root_evidence
python check_root_clearance.py --stl output/model.stl
python check_root_loss_polygons.py --stl output/model.stl --sections output/qa-sections-full.json.gz --out root_evidence
# The preceding diagnostic intentionally exits 1 because 395 exact overlaps are absent.
python check_root_section_connections.py
python check_root_complete_loss_linkage.py
python check_root_controls.py
```

The actual source normals and rays are implemented by `root_rays.cpp`; whole-mesh winding by `root_winding.cpp`; independent distances by `root_clearance.cpp`. All preserve original triangle order and IDs. The final package needs one shared `output/model.stl`; duplicate working snapshots are unnecessary.

Initial failed root-path seeds, pre-final-version trials, and exploratory one-edge/two-edge diagnostics, including unresolved cases, are retained separately in the complete private audit archive. None replaces a failed diagnostic or supplies a blanket exception.
