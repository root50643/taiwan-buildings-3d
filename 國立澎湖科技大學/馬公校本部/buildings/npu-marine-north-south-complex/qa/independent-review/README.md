# Independent release review: NPU marine complex

Decision: **conditional GO for release as an exterior research / separate-print manufacturing candidate**. Source interpretation, model geometry, assembly, rebuild and saved-scene evidence support the stated approximation. The bounded G-code follow-up is complete with retained risks. This is **not** support-free physical-print approval, a dimensional survey, a physical fit/adhesive test, or machine-ready / four-nozzle G-code.

The fixed input was commit `c2172ad91cbfb8189d02615a03dfe2ddf3f15bc1`. On Linux, all 321 original Git blobs and six checkpoint input hashes were verified against the transferred private candidate. No geometry, transform, STL, generator, color-region or scene asset was changed. Previously completed checks were reused rather than recalculated. No new Linux slicing, Blender rendering or model rebuild was performed.

## Source, geometry and scene

- Source review covered the official north/south plans, 2018 campus arrangement and exterior photographs. Photograph dates remain unverified. North 4F / south 3F L volumes, the turning elevated 2F bridge, and the north-end single-storey hall are interpreted separately. 2F/3F hall roof projections do not establish extra rooms. Main proportions are normalized estimates, not 2026 current-condition certification.
- Eight physical STL types / ten instances are closed, consistently wound, positive-volume, single-component manifolds with valid vertex links. Completed exact checks accounted for 10,511,814 internal triangle pairs, refined 112,401 candidates, retained all 622 original section heights, and checked 70 mapped vertex-interval sections. Twenty geometry controls passed. These results were reused without changing sample heights or rounding coordinates.
- All 45 assembly pairs and eleven intended joints were checked. Three original-coordinate micro-overlaps remain: 01/05 = 0.0000224018429593, 01/06 = 0.0000051927682726, 03/06 = 0.0000181274326767 mm³. All are below the declared 0.002 mm³ allowance. Original Float32 zero-volume results remain historical engine observations. No mesh was moved to force mathematical zero.
- Six entrance pillar tops and three bridge pier tops have complete digital mating-face coverage. This is not bending strength, adhesive strength, manufacturing clearance or dry-fit evidence. Zero **design** gap is retained; actual tolerance is unvalidated.
- The earlier separate generator run reproduced all nine STL files byte-for-byte. Ten evaluated scene meshes matched the oriented print triangles and transforms. The reference assembly uses a different float serialization path: topology matches and maximum coordinate difference is 0.000003814697265625 mm; exact float32 equality was false and remains false.
- Prior Blender 5.2.2 review renders versus author 4.5.13 were not pixel-identical (maximum channel difference 6/255). No cross-version byte/pixel equality is claimed. Scene materials remain editable; colors are photographic approximations. The scene contains no reference-image pixel datablock. Ten old JPEG filename remnants in NUL-tail View3D metadata were classified as filenames, not pixels; this finite metadata finding remains, and the reviewed scene was not rewritten.

See `SOURCE-VISUAL-RESULTS.json`, `independent-geometry-results.json`, `assembly-report.json`, `rebuild-comparison.json`, `scene-exact-review.json`, `scene-pixel-review.json`, `assembly-reference-precision.json` and `scene-metadata-block-review.json`. Provenance and permitted execution-path redaction are recorded in `evidence-provenance.json`.

## Slice evidence reused

The completed binding review matched ten instances / eight distinct STL types, selected G-code/log/profile hashes and all 60 settings. Independent PrusaSlicer 2.9.6 reslices of 02 north upper and 07 pier exited 0 and matched every non-comment machine command in the author-selected runs. They were not repeated on Linux. Support was explicitly OFF; all three piers use a 3 mm outer brim. Earlier unbrimmed low-adhesion warnings remain in the original reports.

Original all-parts polygon-footprint analysis failed with `GEOS TopologyException: Ring edge missing at 127.76027756425805 120.59955491655801`. This was a derived 2D numerical-overlay failure, not a demonstrated STL defect. The original failed log remains in the private fixed review; it has not been replaced by a false all-layer pass. `retained-failure.json` binds that log and records the bounded replacement.

## Completed Linux continuation

The reviewer-owned fallback uses analytic straight-segment/capsule intervals over the unchanged G-code coordinates and each path's active nominal width. It performs no polygon union, geometry repair, coordinate snap or tolerance dilation. Seven interval controls, three segment-contact controls and the parser coordinate/extrusion fixture passed.

The final scope is **182 selected post-first-layer sections, 42,398 model extrusion segments and 39,559 retained residual intervals longer than 1e-9 mm**. All 10 files were parsed; duplicate pier geometry was reused only after identical STL/G-code hashes. Coverage is every post-first-layer extrusion for 04/05/06/07/08; for 01/02/03 it is all Bridge-infill layers plus the explicitly enumerated stair-header, roof-transition and last-six-fin layers. It is not every layer of 01/02/03. No current-layer nominal-bead connected component lacked any contact with preceding-layer nominal beads within that scope. This is a final-layer contact-graph observation, not a deposition-order, molten-material, sag or strength proof.

All residuals, including sparse-infill gaps, remain in the lossless `*-all-residual-gaps.json.gz` files. Layer records are in `*-layers.json.gz`; `combined-summary.json` enumerates the scope. The fallback does not use successful G-code exit status to erase overhang flags.

Focused actual paths retain important risks:

| Region | Actual nominal Z | Retained along-path gap | Maximum sampled distance to previous nominal beads | Conservative distance upper bound |
|---|---:|---:|---:|---:|
| North stair blind-recess header (01/02) | 8.0 mm | 8.6 mm | 0.575001 mm | ≤0.600001 mm |
| North long roof edge (02) | 18.2 mm | 64.75 mm | 0.875001 mm | ≤0.900001 mm |
| North short roof eyebrow (02) | 19.2 mm | 8.55 mm | 1.275001 mm | ≤1.299856 mm |
| South roof edge (03) | 27.2 mm | 14.175 mm | 0.875001 mm | ≤0.899957 mm |
| South eyebrow (03) | 28.4 mm | 7.55 mm | 1.175001 mm | ≤1.200001 mm |
| Bridge-window header (05) | 5.8 mm | 1.6 mm | 0.975759 mm | ≤1.000001 mm |

The long along-edge residual is distinct from transverse distance to nearby backing. Neither number is a certified free-bridge length or a physical success threshold. In these highlighted straight intervals both endpoints themselves lack preceding-layer centerline coverage; surrounding same-layer paths / backing do not establish sag-free extrusion. Keep roof ledges, eyebrows and bridge-window risks visible. Selected first-layer/fin/brim plots and three focused path plots were visually inspected; no claim is made that all historical plot images were inspected during this continuation.

At the exact original fin sample heights 24.900000000000006 / 33.900000000000006 mm, 0.8 mm morphological opening leaves **zero** area. Approximately 0.8228576660 / 0.8228602818 mm² is original/removed area, not remaining material. Both actual last layers contain two extrusion moves (active width 0.38292 mm); positive previous-layer overlap does not prove tip fidelity or handling strength. The 1.2 mm crosswise fin width is not a global minimum-wall certificate.

Pier brim is external sacrificial material with measured boundary contact, not entirely disjoint from the footprint: nominal-model overlap 0.283837 mm² and printed-bead overlap 0.257902 mm². It is first-layer only with 108 positive spatial brim segments. Bed adhesion and successful removal remain untested.

## Conditions and reproduction

Retain supplied separate-print orientations, 100% size, generic 0.4 mm nozzle / 0.2 mm layer evidence and 3 mm pier brim. Configure and re-slice for the actual machine. Inspect the highlighted short ledges, window headers, fin tips, skinny pillars and glue faces; trial-print and add appropriately accessible support if required. The open bridge tray and separately flat-printed lid avoid printing a closed overhead bridge cavity; no physical cleanup/removal test was performed. No print, fit, shrinkage, gluing, brim-removal, adhesive-strength or four-toolhead test exists.

Diagnostic G-code is deliberately not shipped. Original hashes, actual selected logs, profiles and analysis remain. `../diagnostic-gcode-exclusions.json` lists all sixteen omitted files; the complete fixed evidence is preserved privately. To reproduce coverage, supply matching-hash diagnostic files locally or regenerate them with the retained slicing sources and verify the new output. Cross-platform G-code byte equality is not assumed.

Run from the package root with Python and numpy:

```text
python qa/independent-review/tools/analytic_support.py --package . --parser qa/independent-review/tools/independent_gcode_parser.py --out /your/new/review-output
```

Reproduction writes to the specified output directory and never repairs input geometry. Source/geometry/rebuild/scene evidence is separate from this bounded path audit. Re-sealing a public package is integrity checking, not a new independent model or physical approval.
