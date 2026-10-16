# Printing limits and supports

This is a small exterior model, not a construction or structural document. No physical print has been made. Geometry checks cannot certify a printer, slicer, material or mechanical load case.

## Orientation and scale

Print upright on the flat210×152 mm base. Nominal scale is1:500, with a total height of approximately63.8 mm. Confirm millimetres on import; STL itself does not store units. A smaller scale can invalidate the tested feature widths.

A0.4 mm nozzle and0.2 mm layer pitch are a sensible first slicing trial, not a tested printer profile. Check the slicer preview carefully before printing. The model is an enclosed exterior solid; ordinary slicer infill may be used. It does not require100% infill merely because the mesh encloses a volume.

## Supports to review

- The raised silver cap overhangs its inset collar by approximately4.0–4.5 m in the source scale (about8–9 mm on the model). Its curved underside needs support review and likely removable supports.
- The main roof perimeter projects beyond the wall, with an engineered-for-model thick lip. Check under-eave supports and any bridge segments.
- The central west entry canopy and north entry canopy have projecting undersides. Support placement should avoid scarring the visible glass/door recesses.
- Stair flights and landings are solid-rooted; they do not reproduce unsupported hollow stair slabs. The main entry portals remain recessed and are not blocked by a print support added to the model.

Use slicer-generated supports rather than assuming the model contains removable supports. No printer-specific support geometry, brim, raft or drain holes are supplied. Resin and FDM preparation differ; a hollowed resin conversion is a new geometry requiring new checks.

## Deliberate scale substitutions

Mullions/transoms are about1.04 mm, guard panels1.2 mm. Thin actual rail wire is simplified to solid panels. Rounded roof lips and a partly flattened cap soffit preserve finite material thickness. Cap corner tops are locally raised by up to1.2 mm on the model; the outer silhouette is a documented manufacturing approximation. Fascia tips have broad flat end returns and the central band retains about1.08 mm. The model has no room interiors; window glass is represented by shallow recesses and color.

## What QA can and cannot prove

The final QA report must be read with its original flags. Raw topology, original triangle intersections, sampled face-normal chords and finite horizontal sections are bounded computational checks. A successful finite test does not prove global minimum wall thickness, strength, support-free printability or accurate architectural measurements. Numerical degeneracies remain explicitly flagged; any exact supplement examines the same recorded rays and does not rewrite the original strict result.
