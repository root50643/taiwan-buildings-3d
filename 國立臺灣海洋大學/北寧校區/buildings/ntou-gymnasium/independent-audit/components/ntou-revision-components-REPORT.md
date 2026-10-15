# NTOU gym revision: independent original-Polygon and actual-surface evidence

## Status and scope

This is a limited independent evidence candidate, not approval of an exception or printability. The frozen mesh and original author's reports remain unchanged. Original per-Polygon 1% opening-loss status stays false. No repair, coordinate rounding, triangle replacement, maximum-component selection, or whole-layer averaging was used.

Original model.stl SHA-256: 752b4c147bd18874b1c49890596c260e58015520f71f60cebc6ee6144700ef49.

## Original sections and true corners

- 210 sections at z = 0.071 + 0.2k mm; all 432 original Polygons, including the six containing holes, were independently reconstructed from the binary STL's exact float32 coordinates promoted to double. Shared original edges use canonical unrounded interpolation.
- Every original Polygon survives erosion radius 0.4 mm and subsequent dilation radius 0.4 mm as exactly one component. Default opening discretization is Shapely quad_segs=16.
- 60 original Polygons exceed 1% loss: 24 end ribs at z20.071–22.271 and 36 top ribs at z41.271–41.871. Maximum individual loss is 0.05151342534917864, retaining 0.9484865746508213. No averaging substitutes for these warnings.
- Original per-Polygon losses exactly match the author's reported numbers. Reopening all author WKT independently differs from the reported fraction by at most 6.805537036691511e-16. Author-WKT versus freshly reconstructed Polygon symmetric-difference area is at most 2.672439512927297e-17 mm².
- True-corner masks include outer and hole rings. Turns above 0.1 degree select original vertices; no simplified polygon replaces the original opening input. Each warning has four actual corners. Independent radius0.41/quad_segs64 disks and the author's separately recreated simplify1e-5/quad_segs16 mask give the same warning residual maximum: 1.1247493746173426e-19 mm², in one end-rib Polygon. Other 23 end-rib warnings and all 36 top-rib warnings have zero computed residual. The nonzero residual is preserved, not stated as absolute zero.
- This corner-localization statement is limited to the 60 warnings. Across all 432 Polygons, ten have nonzero corner-external residual and the maximum is 0.015312598079694841 mm², at z16.271 on a non-warning Polygon (loss fraction 0.00024828306373885937).
- Every Polygon above the first layer has positive-area overlap with a previous-layer Polygon. All 436 explicit positive-area links are retained; every sampled Polygon has an overlap path to the base layer. This is finite sectional-connectivity evidence, not proof of continuous vertical support between layers or support-free printing.

## Warning-family original-face thickness and roots

Every true side of each warning Polygon was probed at its midpoint. The initial original triangle supplies a geometric normal computed from its actual vertex winding, then a separate inward 3D normal ray locates the first material interval. All original intersections, face IDs, barycentrics, and winding controls are retained.

- End ribs: 24 Polygons, 96 side probes. Minimum actual-normal first chord 1.6999969482421875 mm; maximum 5.852221750639498 mm.
- Top ribs: 36 Polygons, 144 side probes. Minimum actual-normal first chord 1.5775726376852184 mm; maximum 42.23784278141174 mm.
- All 240 first entry/exit orientations and outside/inside-midpoint/after-first-exit full-original-face winding controls pass. Their independent XY first chords also have valid entry/exit orientation and minimum 1.5775726376852184 mm.
- Representative-point down/up first material spans were independently checked for all 60 warnings. End-rib downward exits are at z18.796163338653102–19.798923163965647, and minimum local continuous vertical span is 16.80215329059898 mm. The minimum downward first exit distance from an end-rib representative point is 0.9803598068680678 mm. Top-rib downward exits range z0–14.399999618530273, and minimum local continuous vertical span is 27.367162837418967 mm. The minimum downward first exit distance from a top-rib representative point is 26.871000381469727 mm. These do not mean that every warning is directly supported to the bed.

## The 162 authored probes: numeric reproduction and target mismatch

All 162 authored seed rays were independently regenerated. Every first original face matches. Maximum source-point displacement is 2.842170943040401e-14 mm. Recomputing normals from original triangles rather than the saved float32 normals changes first-chord length by at most 7.038198717168598e-7 mm. All 162 normal measurements remain above 0.8 mm, with valid first entry/exit orientations and all winding controls passing.

However, 31 labels do not establish the claimed local target:

- Three continuous_support_to_base records hit the upper curved roof and then use an oblique normal, not a vertical support ray.
- Six local_canopy_plate records hit curved-roof undersides at z16.34–16.84, not the canopy at z11.7–12.7.
- Nine local_canopy_posts records first hit façade backing, not a post.
- Thirteen curved_rib_width records at z40.671 measure the full merged 139.6999969482422 mm roof span; an isolated rib width is not present along those rays at that height.

The complete original author records are preserved inside each reconstructed record. Classification is separate from the valid numerical measurement. Corrected same-target probes retain explicit counterpart_author_index links; the merged-roof records are not silently relabeled as isolated widths.

## Additional actual-target probes and vertical support

86 source-located, original-surface probes avoid unrelated first hits:

- Six actual canopy top points: all first-normal thicknesses exactly 1.0 mm.
- 36 actual canopy-post points: 1.1897321451365104–1.1897339073066056 mm.
- 18 actual entrance-column points: 2.875190194942499–2.8751912080758766 mm.
- 26 actual isolated-rib points: 1.6999969482421875–1.7000007629394531 mm.

All target-coordinate checks, first entry/exit orientations, and full-original-face winding controls pass. Maximum control winding deviation over all 488 normal probes is 8.003498656447528e-16. The additional 360 warning vertical-root controls pass as well.

Five independent vertical lines retain every material and air interval, with top-down and bottom-up original rays:

- At the entrance-column footprint (0.173, -26.369), the first roof-to-base material span is continuous from z41.56233309134264 to z0; bottom-up agrees.
- At left/right canopy-post footprints (-41.327, -31.469) and (-35.327, -31.469), the actual canopy-plus-post is continuous from z12.699999809265137 to z0; bottom-up agrees. Above it, the curved roof is separated by real air: z12.699999809265137–16.740005682388755 on the left and z12.699999809265137–16.142510741306587 on the right. That air is not skipped to claim a continuous roof-to-base post.
- Between the posts, the canopy is a 1.0 mm plate at z11.699999809265137–12.699999809265137, with air below down to the base top at z2.799999952316284. The plate needs its actual posts/back connection and may require printing supports; a vertical bed support is not invented at those midspan points.

## Reproduction and evidence

Place this folder at model/independent-audit/components. The programs read ../../model.stl, ../../true-corner-mask.json and ../../designated-roots.json without duplicating those original inputs. They use relative paths only, disable bytecode writes, and write separate ntou-revision-components-*.json.gz evidence beside themselves. From this components folder run:

    python ntou-revision-components-independent.py
    python ntou-revision-components-roots.py

Dependencies tested: Python3.12.14, NumPy2.3.5, Shapely2.2.0 / GEOS3.14.1. No Trimesh processing is used. The relative-path programs were rerun in a separate temporary directory containing copied read-only inputs; all reported results were reproduced. Frozen STL SHA remains unchanged.

Evidence includes original/reopened/eroded/lost WKT, all original author records, original normals and ray intervals, corrected-target counterpart mappings, full winding controls, and exact per-layer intersection links. It does not establish global minimum wall thickness, absence of all self-intersections, all possible support contacts, slicer toolpaths, or physical print success. Dense whole-surface analysis and exception approval are outside this evidence candidate.
