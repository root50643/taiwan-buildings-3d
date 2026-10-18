# Support access review  -  old fixed candidate 9c90c8b6

Read-only geometric follow-up to `extended-checks-initial.json`. This report changes none of its 573 downward-face findings, flags, or their first-hit air-gap values. The old input is `input-original.stl`, SHA-256 `9c90c8b6b6f99076f2096783e78b793404fb81df88ee270d2eb02f21290e24b8`, 193,784 bytes, 3,874 triangles. Conclusions apply only to this input; the live generator/STL may now be under revision.

## Measurement and evidence

Read raw binary STL triangles without repair or reordering. Full-line Moller-Trumbore intersections against every triangle, duplicate hits coalesced within 1e-5 mm, paired to solid intervals. All 207 sampled lines have an even number of crossings. The attached JSON contains all origins, directions, signed line parameters, original face indices and solid intervals, plus the complete reproduction Python source. Extract `reproduction_python` to a temporary `.py`; run it with `--stl <fixed-input.stl> --output <new-report.json>`, using a distinct output path to preserve this evidence. No rendering or slicing was performed. This is finite sampling, not a clearance guarantee for every possible support shape or tool.

Rear coordinates are local to each wing: `global = Rz(theta) * local + (xc,30,0)`, with `(xc,theta)=(-30,-14 deg)` and `(30,+14 deg)`. Local +Y points into the rear wing. The externally open window direction is local -Y: global left `(-0.241922,-0.970296,0)`, right `(+0.241922,-0.970296,0)`.

## Rear window bands

Main apertures: local X `[-27.5,27.5]` (55.0 mm wide), local Y `[-11.5,-9.75]` (1.75 mm recess from wall mouth), and Z `[18.100000,24]`, `[29.100000,35]`, `[40.099998,46]`, `[51.099998,57]`: net height approximately **5.9 mm**. The lower sill projects to local Y -13 (1.5 mm beyond the wall); from that outer lip to the back wall the total setback is **3.25 mm**. The opening is an exterior blind recess with a solid back and side jambs, not a through-hole or a closed internal cavity.

Actual STL checks, both wings: X-direction lines at Y=-10, Z=21.123 give flank intervals ending/starting at X approximately -27.5/+27.5. Y-lines at X=0.123, Z=21.123 give rear solid beginning at Y~-9.74999995; the nearby ordinary wall at Z=24.001 starts at Y~-11.49999954. Vertical lines at X=0.123,Y=-10 and -11.25 show air intervals 18.10000038 to 24, 29.10000038 to 35, 40.09999847 to 46, and 51.09999847 to 57. Boundary samples X=+/-27.49 are still open and +/-27.6 are jamb material.

The combined aperture envelopes in global coordinates (includes gaps between floors) are:

| Wing | Global minimum XYZ, mm | Global maximum XYZ, mm |
|---|---|---|
| Left | (-59.465234,12.188747,18.1) | (-5.675606,27.192469,57) |
| Right | (5.675606,12.188747,18.1) | (59.465234,27.192469,57) |

Removal path: a fragment in the main recess can translate outward along local -Y through its own 5.9 mm-high mouth after detachment, then be manipulated in the exterior courtyard. Solid foreground mass limits a long straight approach at low levels: central Z=21.123 samples encounter another building after approximately **21.130 mm left / 12.235 mm right** from the nominal wall mouth, and inner-edge samples give about **13.296 mm left / 11.951 mm right**. These are enough to demonstrate an open route out of the 1.75 mm recess for small fragments; they do not establish room for a particular cutter, intact support block, or hand. Top-band Z=54.123 central rays have no foreground crossing before infinity. Lateral jaws must not be inferred open: side jambs close the slot.

**Additional unresolved narrow channel:** at Z=18.05 (also 29.05,40.05,51.05), the measured Y solid intervals are `[-13,-9.8]` and `[-9.75,11.5]`. Thus a **0.05 mm-deep, 0.10 mm-high** slit remains behind each sill's upper 0.1 mm strip across the window width. Source cause: sill back is Y=-9.8, whereas cut back is Y=-9.75. It communicates upward with the main recess; it is not a sealed cavity. A support fragment or tool cannot be claimed removable from this tiny slit. This is a separate air-channel warning, retained as evidence and not a change to the original 573 findings.

## Rear roof eaves

Measured central Y lines at Z=61.999,62.6,63.201 switch between body `[-11.5,11.5]`, eave `[-12.5,12.5]`, and body again. Therefore the roof detail at Z=62 to 63.2 has **1.0 mm front/back projection**, and the source-local width gives **0.5 mm end projection** relative to the 66 mm body (67 mm roof detail). This is a shallow external ledge, not an internal unsupported room. The detail's conservative global box, before overlap with spine/neighbour solids, is left `(-65.528931,9.766920,62)` to `(5.528931,50.233080,63.2)`, right `(-5.528931,9.766920,62)` to `(65.528931,50.233080,63.2)`.

At local Y=+12,X=0.123 both wings have only base Z=0 to 3 and ledge Z=62 to 63.2. Thus the original 59 mm vertical first-hit gap is a real air column at the sampled position, **not an automatically required 59 mm support height**. Support need depends on the 1 mm lateral projection, print settings and material. If support is generated, it is externally exposed to local +Y (back eave) or -Y (front eave); no sealed-cavity removal problem appears in these samples. At local Y=-12 the repeated window sills interrupt the vertical air column. Near the central spine there is overlap: e.g. left local X=33.25,Y=.123 is solid through Z=68, so a uniform end-eave removal path cannot be claimed. No eave support-removal success is claimed.

## Entrance wing grille and window ledges

Global front is -Y. Window envelope: X `[36,60]`, Y `[-20,-19.1]` from original facade to blind back, Z `[25,32]`, `[34,41]`, `[43,50]`; actual recessed clear height **7.0 mm**, original-facade recess **0.9 mm**. Leading sill lip is Y=-22.5, giving **3.4 mm** from lip to back. Bars at X `[36.5,37.5]`, `[42.5,43.5]`, `[48.5,49.5]`, `[54.5,55.5]`, `[60.5,61.5]` leave **5 mm clear bays at the outer grille plane**; at the recessed cut, the last bay X=55.5 to 60 is only **4.5 mm** before the right jamb, while the left cut-edge strip X=36 to 36.5 is **0.5 mm**. Combined external grille/eave envelope is X `[33.5,62.5]`, Y `[-22.5,-19.1]`, Z `[24,50]` (the building behind extends farther).

Actual STL Y-line X=37,Z=28.123 gives solid `[-21.95000076,-20.89999962]`, air `(-20.89999962,-19.10000038)`, then solid back. The cuts therefore remove the rear part of each fin within a window level; the remaining outer fin strip is **1.05 mm deep**, with a **1.8 mm-deep air slot behind it**. X=40.123 at the same Z has no leading fin: only the solid back begins Y~-19.1. X-line Y=-21.1,Z=28.123 measures the five 1 mm bars and 5 mm gaps directly. Vertical line X=40.123,Y=-19.5 has air Z=25 to 32,34 to 41,43 to 50. At Y=-20.5, the eaves stand farther out and the free vertical interval is 25 to 33 etc.; use the restrictive 7 mm back-slot height when discussing removal.

Removal path: between bars, outward -Y is unblocked to exterior. Behind an outer fin strip, an intact support piece cannot move straight out through that fin; it must be detached, reduced and shifted laterally into a 5 mm bay, then moved -Y past the ledge. The slot communicates sideways with those bays and is not sealed. No tested guarantee exists that a generated support block will fit this route. At the left cut edge, X=36 to 36.5 is only **0.5 mm** from the jamb to the first fin edge in X projection. On the right, X=60 to 60.5 is outside the window cut: X=60.1,Z=28.123 already has body beginning at Y=-20 rather than Y=-19.1, so that apparent 0.5 mm front-plane strip is not a full-depth aperture. The jambs recede relative to the fins, so neither is a uniformly bounded 0.5 mm tunnel. Do not use these edge slivers as practical removal routes.

Adjacent connector grille is distinct: X=20.123,Z=10.123 and17.123 have solid back beginning at Y~-18.29999924, verifying a **0.7 mm recess** from original face Y=-19. Details extend to Y=-20.1, with regular bay widths approximately **4.2 mm** (5 mm pitch minus0.8 mm bar) and Z gaps approximately **6.2 mm** between 0.8 mm crossbars. This is exterior relief, not a continuous enclosed passage. Finitely sampled outward paths are available between bars; no support generation or removal is verified.

## Limits and outcome

All figures are model millimetres, not dimensions of the real building. The original 573 support-screen findings remain intact and require their separate grouping/per-face interpretation. This access review supplies clear openings, projections and routes; it does not convert those findings to passes. Shallow exterior overhangs can be support-free under appropriate printing conditions, but neither support necessity nor safe breakaway is established here. No formal slicer, G-code review, support simulation, or physical print/removal test was performed.
