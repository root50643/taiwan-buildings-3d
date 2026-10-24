# Manufacturing / technical QA limits

Private proportional model, not engineering/cadastral measurements; not physically printed. No support-free or universal printer guarantee.

v3 retains v2 corrected garden width from40 to28 proportional units while retaining road width22 and roof height12.8; near-frontal historical photo supports roughly2.2 width/whole-façade-height rather than v1's3.28. Source emergency raster aspect is not a scale drawing. Present PDF photos determine glazing style, historical photos only main-frame relations. Native model uses mm, nominal design multiplier3.8.

Raw STL (final counters in qa-topology.json): 2826 triangles,1401 vertices, one connected boundary shell; exact coordinates only, no healing/rounding. Directed edge incidence, vertex links, zero degenerates/duplicates, winding and signed positive volume tested. Non-vertex-adjacent17-axis SAT has zero contacts. Shared-vertex pairs are excluded; this is not an exhaustive adjacent-triangle foldover certificate.

303 total sections:0.2mm intervals including an additional top-minus0.001 sample: all contours valid, no positive component vanished under0.4mm erosion. **This does not certify minimum wall width:** the narrowest garden vertical frame's nominal width is0.399mm, other frames0.57mm; connected details may disappear with a given nozzle/slicer. Five colonnade piers are nominally2.394mm wide, canopy slab2.47mm thick. B1 column-free void and recessed mirror mass are verified with explicit raw-mesh inside/outside probes, not filled for single-shell convenience. Upper interiors are solid exterior-study proxies, not surveyed room models.

B1 ceiling span and attached entry canopy are overhangs requiring slicer/support planning. Steps and fine mullions need process-specific evaluation. Circular equipment is only a visible coarse outline. Source-free previews and 3MF opaque glass are display colors, not physical transparency.

`qa/` records executed gates, 3MF native material+vertex edits/save/reopen, Blender mesh/material edits/save/reopen and front rerender. Independent reviewer evidence is in the private parent folder. Tests are bound to exact SHA256; rerun when geometry changes.

v3 narrows the tall road window to2.8 proportional units and entrance width by0.78, guided by both official photos (not measured survey). Roof edge is0.04 design units proud and garden piers0.08 proud to retain real surface/material boundaries, preventing large coplanar triangle color spill. Automated raw-mesh/material check confirms zero white roof triangles on the original garden wall plane.
