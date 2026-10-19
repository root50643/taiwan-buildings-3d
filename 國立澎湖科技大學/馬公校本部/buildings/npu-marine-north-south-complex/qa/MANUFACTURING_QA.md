# Manufacturing QA evidence

This candidate has **8 distinct physical STL types and 10 physical instances**.
All ten instance meshes are watertight, consistently wound, positive-volume and
single-component. No duplicate or degenerate faces were found. The all-triangle
contact check found no non-topological self-contact or surface intersection.
All 45 assembled part pairs passed the declared contact rules, with zero intersection volume reported by the original Float32 engine. Independent raw-coordinate refinement found three nonzero numerical micro-overlaps below the declared 0.002 mm³ allowance: 01/05 = 0.0000224018429593, 01/06 = 0.0000051927682726, 03/06 = 0.0000181274326767 mm³. Original engine results remain historical evidence; no mesh or transform was changed to force zero. This is a digital candidate: no print or physical fit test
has been performed.

## Exact evidence

- Final assembly manifest SHA-256: `59374202108525afdefa869474b3a786abdad592e9dcd8454341822a9c6b98e8`.
- 8,428 instance triangles and 112,401 AABB triangle-pair candidates examined, with no sampling or pair cap.
- 622 per-instance horizontal sections at 0.2 mm increments plus explicit heights.
- Full raw mesh report: `v5-raw/mesh_qa.json`; all pair, thickness and section detail files sit beside it.
- Actual PrusaSlicer 2.9.6 reports: `../slicing/v3-trial-01/slicer_qa.json` and `../slicing/v4-new-and-brim-01/slicer_qa.json`, plus `../slicing/v5-access-01/slicer_qa.json` when present.
- `final_slice_evidence.json` binds each final STL SHA-256 to the actual completed slice. New 01/02 and brimmed piers were sliced for v4; the final changed 08 was sliced again for v5. Unchanged 03–06 are bound to their identical v3 STL hashes.
- The selected actual slices all exited 0, contain extrusion and layers, remain within the 220 mm QA bed, and have no warning lines. The three v3 pier adhesion warnings remain in their original report and logs.
- `metadata_redactions.json` records before/after SHA-256 for local path metadata redaction. Warning content and G-code commands remain unchanged. Final log and G-code hashes are rebound in each slice report and final evidence record.
- `control-tests.json` records nine executed known positives/negatives for the self-contact algorithm: true closed-box and triangle crossings, coplanar overlap, non-topological point/edge contacts, legal shared edge/vertex, and ordinary/separated boxes. All nine controls passed. This validates those controls without proving every degenerate configuration.
- `contact-patches.json` records all-triangle mating surface area per contact plane for each expected adhesive pair; it is not a glue-strength or physical-fit test.
- `vertex-links.json` checks every merged vertex for a single connected degree-two link cycle, supplementing edge watertightness so pinched/disconnected local vertex fans cannot pass silently.

| Instance | Faces | Components | Minimum centroid-ray hit (mm) | Actual sliced layers | Last nominal Z (mm) |
|---|---:|---:|---:|---:|---:|
| 01-north-lower | 2010 | 1 | 0.900000 | 90 | 18 |
| 02-north-upper | 2204 | 1 | 0.900000 | 125 | 25 |
| 03-south-body | 3452 | 1 | 0.900000 | 170 | 34 |
| 04-hall-roof | 54 | 1 | 1.200000 | 20 | 4 |
| 05-bridge-tray | 436 | 1 | 1.199997 | 36 | 7.2 |
| 06-bridge-lid | 44 | 1 | 1.200000 | 6 | 1.2 |
| 07-pier-instance-1 | 28 | 1 | 1.200000 | 45 | 9 |
| 07-pier-instance-2 | 28 | 1 | 1.200000 | 45 | 9 |
| 07-pier-instance-3 | 28 | 1 | 1.200000 | 45 | 9 |
| 08-south-low-access | 144 | 1 | 1.200000 | 10 | 2 |

The thickness column is the minimum of the tested inward face-centroid normal
rays, not a proof of the minimum at every point. Exact STL dimensions and hashes
are recorded in the manifest and raw report. Nominal 0.2 mm slicing quantizes the
7.3 mm bridge tray to a last toolpath Z of 7.2 mm; the small difference must not
be misreported as physical fit validation.

## Raw flags and their limits

- **02 `THICKNESS_RAY_MISS` remains**: one exact centroid ray fell through an opposing triangle seam. Four tangential offsets of 0.0001 mm hit at approximately 34.1 mm. Original miss and supplemental ray distances are both retained in its thickness JSON. This is numerical supplemental evidence, not removal of the original flag.
- **02/03 `SECTION_THIN_OPENING_SCREEN` remains**: the 0.8 mm morphological opening removes the complete tiny section at the original sample Z 24.900000000000006 / 33.900000000000006 mm. Opened area is zero; original/removed area is 0.8228576660155709 / 0.8228602818079902 mm², not remaining material. The fins have 1.2 mm crosswise thickness but taper longitudinally near the peak. The successful last layers provide toolpath evidence; the small caps remain a detail-quality risk.
- **01/02/03/05 `SECTION_45DEG_OVERHANG_SCREEN` remains**: abrupt window headers, projecting rail bands and roof eyebrow ledges exceed the screening allowance. Regular facade window recesses are 0.8 mm deep and 3.6 mm wide. The separate north stair-strip recess headers are approximately 9.0 × 0.8 mm at print Z 7.8 / 16.8 mm; their long edge is not automatically a 9 mm unsupported transverse bridge. bridge openings are 2 mm wide; facade bands project approximately 0.45 mm. The north roof eyebrows include approximately 1.5 mm short cantilevers. No support material was requested or generated in the selected slices. These short ledges can droop or lose detail and require physical validation.
- **08 small decorative relief**: the final short steps have levels 1.2 / 1.6 / 2.0 mm, with 0.4 mm rises. They are supported by the underlying mass. Face-centroid inward rays must not be interpreted as a 0.9 mm lower bound on decorative feature height. The earlier v4 platform geometry and its results remain in history; v5 makes both sets of steps explicit and rechecks that changed STL.
- **Pier adhesion**: v3 without brim produced `Low bed adhesion`. v4 adds a 3 mm outer brim, slices with a first-layer brim, and emits no stability warning. This is a slicer mitigation; real bed adhesion remains untested.

## Assembly and support access

Each building body rests on its own flat underside in the provided STL orientation.
The north upper mass prints separately on its full footprint, then joins the lower
mass at assembled Z 18 mm. The low conference roof prints separately on its flat
underside; its reconstructed roof now remains inside the hall footprint.

The bridge prints as an upright open tray with a 1.6 mm floor and 1.2 mm walls.
Its 1.2 mm lid prints flat and is glued after any window cleanup. The tray interior
is accessible from above before lid attachment. Three piers print upright with
the recommended brim. The assembly is not printed across the courtyard in place;
there is no 40 mm airborne print span or support trapped under a closed bridge lid.
All joining faces are adhesive butt contacts without press-fit keys; no clearance
or glue-gap claim has been physically tested.

`v5-raw/assembly_sections.png` is original model geometry, visually inspected at
nine levels. Numeric probes in the matching JSON show the courtyard sample open
at all tested levels, the bridge sample open at Z 5 mm / occupied by floor at
Z 9.5 mm / hollow at Z 12.5 mm / occupied by lid at Z 16.9 mm. The entrance sample
is open at Z 5 mm and occupied by the separately printed upper mass at Z 18.5 mm.
The entrance ground tie beams occupy the Z 0.6 mm sample, which is explicitly
shown rather than calling the whole ground plane empty. These are selected point
probes plus complete planar sections, not a site-wide accessibility certification.

## Retained failures and reproduction

`v1-raw` retains the original failed component/thickness findings and the interrupted
run boundary. `history/v1-reproduction` reproduces all nine original per-instance
input hashes exactly (nine out of nine matches). The disconnected roof eyebrows
and internal recess shells were corrected, and the hall roof's sub-0.07 mm convex
hull wedges were clipped to the footprint. Both changes were rechecked in v3 and
v4. v3 raw flags and unbrimmed pier warning logs remain intact.

## QA slicing profile and reuse

Actual PrusaSlicer executable SHA-256:
`7fd50b52d1cc3da87dbcb71e45e764412dd45688bea028f351333e86d9769704`.

The generic single-material PLA QA profile uses a 0.4 mm nozzle, 0.2 mm layers,
three perimeters, 15% infill, a 220 × 220 mm bed and Arachne perimeters. Piers add
a 3 mm outer brim. The logs, profile, G-code hashes and parsed extrusion/layer
statistics are retained in each trial directory. All G-code is **QA ONLY** and
has no machine start/end sequence; it must not be sent directly to a printer.
No multi-toolhead or four-color print configuration was tested. Scene colors do
not establish multi-color manufacturing readiness.

Portable rerun sources are in `../source/qa-tools/`. Supply a local PrusaSlicer
console executable through `--slicer` or `PRUSASLICER_EXE`. No global configuration,
credentials, Library artifact or other task was modified.

## Independent continuation and publication scope

See [independent review](independent-review/README.md) for raw-coordinate assembly refinement, source/scene/rebuild findings, the retained failed polygon overlay, and the completed bounded analytic G-code coverage. Publication of this research/manufacturing candidate is conditional; it does not approve support-free physical printing. Diagnostic G-code is intentionally excluded from public delivery; its original hashes, actual slice reports and profiles remain. [Exclusion manifest](diagnostic-gcode-exclusions.json) distinguishes archived evidence from shipped files.
