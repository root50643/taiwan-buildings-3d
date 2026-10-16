# Manufacturing scope and limits

Nominal scale 1:400; source-constrained main bar length 205 mm, excluding projecting shade edges, base 220 × 70 × 2.4 mm. Overall highest model point is approximately 38.65 mm above the base bottom, using estimated roof/wingwall/elevator elevations. Source values and estimates are separated in parameters.json and README.

Dense original concrete fins approximately 0.1 m thick would be only 0.25 mm at nominal scale. The authored model uses 77 merged bars 1.2 mm wide; the exact original count is unknown. Slabs, parapets, columns, roof rails and ramps are also thickened/merged. These are finite geometry choices rather than a globally proven minimum wall thickness.

The central covered passage, open SW corridor, deep NW shade recesses and bridge undersides create substantial overhangs. Supports will probably be required depending on orientation, process and printer; do not interpret a watertight mesh as support-free. The mesh has not been sliced on a named printer, structurally tested or physically printed. Resin cleanup and trapped support removal, and FDM bridging limits, need printer-specific review. Small railings are merged into solid raised edges for durability; U stairs are stout ramps instead of individual fine treads.

Author normal and optimized original-mesh checks are complete for v3: topology/normals/one surface, all 465,075 closed-AABB candidate triangle pairs and all 580 section layers / 4,737 original Polygons pass. All 157,340 finite original-face ray samples have tested chords at least 0.8 mm (minimum approximately 1.18509 mm). One numerical flag remains and original numerical strict_passed=false is retained. Exact classification of this same original-run hexfloat ray succeeds in both modes with a conservative first solid chord approximately 31.95000 mm; no sample was moved. This bounded diagnosis does not rewrite the numerical strict result. Final independent release scope is documented in qa/independent/QA-RESULT.json when present.

Even successful bounded finite section/ray tests do not establish every arbitrary direction, physical material strength or print success.
