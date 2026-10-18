# Independent manufacturing review

The frozen candidate passes the analytical checks below for the documented split-and-glue workflow. This is not a physical print or fit test.

- Inventory: 22 pieces, four unique geometries: body 1, canopy 1, column 10, upper mast/brace frame 10.
- Each exported assembly STL is closed, consistently wound, one connected component and positive volume. Manifold3D accepts each with `Error.NoError`.
- All 231 pairs of placed assembly pieces were intersected in their original coordinates. Maximum overlap is 0 mm³; failure threshold is 0.0001 mm³.
- Direct triangle-ray measurements on exported STL give brace widths 1.7999997–1.8000002 mm, frame side thickness 2.2000000 mm, column thickness 2.8000000 mm, canopy field thickness 2.4000015 mm, and 2.0000000 mm web between aligned upper/lower sockets.
- All 50 sockets were independently measured. Total X/Y key clearance is approximately 0.4 mm, within STL float precision. Body key bottoms have a 0.30 mm gap; canopy key bottoms/ceilings have 0.15 mm gaps. Shoulders clear by 0.05 mm. These are adhesive positioning joints. They require a suitable gap-filling adhesive and an unglued fit check.

Print the body upright, canopy top down, and columns/upper frames on their flat side. Assemble body → ten columns → canopy → ten upper frames. This order leaves all sockets accessible and avoids threading braces through the canopy. The side-flat frame and column STLs retain a common flat face over their complete shapes.

The main body has a measured 5 mm front balcony projection. A conservative automatic-support profile was used for that piece; support also appears in some shallow front/back window reliefs. These reliefs open to the exterior, but removal may need fine cutters. Support removal and adhesive fit remain untested physical operations.

The top-down canopy has thirty bed-facing blind sockets. Their 2.6 × 3.8 mm openings close with short bridge paths at print Z=1.00 mm. The originally lower sockets face up during printing. The canopy, column and upper frame were sliced with supports disabled. The assembled overview STL is not the manufacturing orientation.

PrusaSlicer 2.9.6 exited successfully for all four unique pieces with no warning/error/repair lines. Object extrusion heights are 140 / 18 / 14 / 11 layers at 0.2 mm for body / canopy / column / frame. The body has 189 total layer-change records because independent support layers are interleaved; it still has 140 distinct object extrusion heights and reaches Z=28.0 mm. Each part used a separate new settings directory. The explicit diagnostic profiles assume 0.4 mm nozzle, 0.45 mm extrusion width, 3 perimeters, 15% infill and generic PLA at 205/60 °C on a 250 × 210 mm bed.

`geometry-review.json` records raw coordinates, thresholds, measurements and all collision/clearance results. `slicing-summary.json` records STL/G-code hashes, commands, toolpaths, support bounds and layer evidence. `slice-evidence.png` shows actual balcony-support and canopy bridge paths. Full logs and reproducible scripts/profiles are included. Executable G-code is deliberately outside this deliverable; its checksums remain in the summary, and it is not a validated machine profile.

This review does not substitute for the package's separate triangle self-intersection QA. The caliper rays are explicitly located feature checks, not a claim of a complete arbitrary-direction wall-thickness proof. No physical trial print, adhesive test, or machine-specific thermal/warping test has been performed. The broad canopy may need bed adhesion tuning on the selected printer.
