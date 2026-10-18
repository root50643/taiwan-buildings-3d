# Reviewed short-axis support route — conditional diagnostic only

This route replaces acceptance of the original main-body automatic bridge
direction. The four fixed print STLs are unchanged. The original diagnostic
main profile and results remain under `qa/manufacturing-review/` as rejected
main-route evidence, not a recommended printing process.

`main-short-axis-support.ini` is byte-identical to the independent review's
short-axis feasibility profile. Relative to the original profile, only
`bridge_angle=90` and `dont_support_bridges=0` changed; see profile-diff.json.
It contains no validated printer start/end sequence and is not machine ready.

Use PrusaSlicer 2.9.6 at **100% size**, PLA, 0.4 mm nozzle, 0.2 mm layer,
nominal 0.45 mm width, 3 perimeters, **15% stars infill**, 250 × 210 mm bed.
The diagnostic has skirt only and no brim. Keep supports below bridges.
Verify actual lines cross the platform's short direction: copying angle 90
alone is insufficient after rotating the model or changing slicer conventions.

Set `PRUSA_SLICER` and `PRIVATE_SLICE_DIR` outside the model package and run
`python manufacturing/reviewed-support/slice_reviewed_parts.py`. This re-slices
only the changed main route by default. `--all` also re-slices roof, column and
frame using the unchanged support-off profile; four unique geometries are not
22 separate piece tests. Each run uses its own settings directory. Diagnostic
G-code stays outside the deliverable and must never be sent directly to a printer.

The integrated rerun is bound by STL/profile/G-code SHA and line-by-line
comparison with the independent corrected diagnostic, excluding only its
generated-time comment. This carries forward the exact toolpath evidence,
not evidence of a physical print. The independent numerical method and all
original failure flags remain in
`qa/independent-support-review/slicing-support-audit/`.

- Platform centerline uncovered interval: original approximately 174.288719 mm;
  corrected approximately 1.704001 mm. This is planned-path capsule coverage,
  not a material sag or heat simulation.
- Other bridges remain: main internal infill closure about 8.224913 mm, roof
  about 8.036027 mm. The 2.600011 mm roof-slot bridge is not the maximum.
  Demonstrate about 8.3 mm bridge capability for the actual material/machine,
  or change infill/solid layers and re-slice/review the affected geometry.
- Corrected support has 30,369 extrusion segments and 95,890 unique sampled
  points. Of these, 580 points in two shallow front windows require staged
  side routes. No added sealed area was seen by these finite checks; this is
  not a complete tool, support-block, adhesion or removal-force simulation.
- Clear support before assembly. Break support into small pieces and remove
  laterally through the 4.5 × 9.4 mm exterior slot; do not pull window blocks
  straight forward behind the stairs. If a fine tool cannot safely enter the
  approximately 1.2 mm deep recess, revise supports or use a compatible soluble
  support process and re-slice. Do not lever against stairs or close support in.
- The 50 interfaces are glue alignment, not snaps. Clean sockets and elephant
  foot, dry-align ten columns with the roof, and use suitable gap-filling glue
  and a temporary alignment jig. Nominal 53.4 mm assembly height differs from
  an estimated 53.25 mm if shoulders settle naturally; neither is a fit test.

No print, physical support removal, dry fit, adhesive strength or transport
strength has been tested. Roof warping/bed adhesion and frame handling remain
risks. Read the package README and complete independent report before use.
