# Geometry QA evidence

Model SHA-256: `d78cce5eac6db4f9a1e1cfb739a4ee37fd5306ddec6cc4ef70186ed3b45cdf76`

Raw binary STL: 1824 triangles; 914 exact-coordinate vertices. Topology checks: PASS; 0 bad edges; 0 bad vertex links; 0 degenerate faces; 1 face-connected component(s). Signed volume 578640.464397 mm³.

Exhaustive pair screening: 1662576 pairs, 21796 inclusive-AABB candidates refined, 0 unexpected intersections. This is floating-point numerical refinement, not an exact-arithmetic proof. Controls: PASS.

All 272 horizontal layer-centre planes at 0.2 mm spacing: 272 legal contours; component histogram {1: 272}; hole histogram {0: 272}. Section-integrated volume differs from mesh volume by -0.002850%. Raw contour graphs are checked before polygon construction and are not repaired.

Actual section polygons were opened and closed at 0.6, 0.8, 1.0 and 1.2 mm diameters. At 0.8 mm, maximum opening loss is 39.467198 mm² (100.000000% maximum per-section loss); 5 sections lose more than 0.01 mm². Losses are observations of narrow details/tips; they are not hidden or treated as an unconditional pass. Opening/closing controls: PASS, including a deliberately 0.4 mm finger and 0.4 mm slot, and a retained 2 mm finger.

See `geometry-report.json` for all pair results, controls, tolerances, limitations and morphology summaries, `geometry-layer-sections.csv` for every measured plane, and `geometry-layer-sections.png` for selected polygon sections.

This does **not** establish complete quality, support removability, printer readiness or physical printing success. The separate slicer/support checks and independent review remain necessary.
