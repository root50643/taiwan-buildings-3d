# Geometry QA evidence

Model SHA-256: `0827a741ec86c047708d5698c540d353a223347f25a1d883256b236bf495b70c`

Raw binary STL: 1832 triangles; 918 exact-coordinate vertices. Topology checks: PASS; 0 bad edges; 0 bad vertex links; 0 degenerate faces; 1 face-connected component(s). Signed volume 579817.648514 mm³.

Exhaustive pair screening: 1677196 pairs, 22225 inclusive-AABB candidates refined, 0 unexpected intersections. This is floating-point numerical refinement, not an exact-arithmetic proof. Controls: PASS.

All 272 horizontal layer-centre planes at 0.2 mm spacing: 272 legal contours; component histogram {1: 272}; hole histogram {0: 272}. Section-integrated volume differs from mesh volume by 0.001164%. Raw contour graphs are checked before polygon construction and are not repaired.

Actual section polygons were opened and closed at 0.6, 0.8, 1.0 and 1.2 mm diameters. At 0.8 mm, maximum opening loss is 0.090615 mm² (0.000739% maximum per-section loss); 3 sections lose more than 0.01 mm². Losses are observations of narrow details/tips; they are not hidden or treated as an unconditional pass. Opening/closing controls: PASS, including a deliberately 0.4 mm finger and 0.4 mm slot, and a retained 2 mm finger.

See `geometry-report.json` for all pair results, controls, tolerances, limitations and morphology summaries, `geometry-layer-sections.csv` for every measured plane, and `geometry-layer-sections.png` for selected polygon sections.

This does **not** establish complete quality, support removability, printer readiness or physical printing success. The separate slicer/support checks and independent review remain necessary.
