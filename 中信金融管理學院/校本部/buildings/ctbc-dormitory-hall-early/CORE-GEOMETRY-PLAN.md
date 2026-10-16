# Core geometry, revised after independent source review

Scope: MOE1151125, former Hsing Kuo girls dormitory and lecture hall, early completed exterior of architect's2001 project. Photo capture dates are unknown. This is a source-constrained finite-detail model; source review and numerical verification have distinct, hash-bound scopes.

## Sources actually viewed
The complete1080×1635 architect plan/two elevations, plan crop, all six original photographs(565172989ac249c,537517298c604c40,555172990c7234a,319517298e3aa633,9775172996327f72,5795172998c5fad0), north-up NLSC orthophoto detail and dimension overlay. All remain separate private references, not textures or public files.

## Correction to the original68m starting cue
Independent re-reading identified a mixed-roof endpoint: original L1 ended around(756,525), while the main high southern roof ends near x716 and northern high roof near x802. The plan places the southern high service end around axis9 and the low entrance/northern group around axis10; the upper elevation also has a low eastern extension after the high end. Therefore the initial aligned-east-end68m southern block was rejected before final QA.

Current proportional choices: south high wing62m long; northern short wing X47.5..71m,23.5m wide; northern/low eastern end about9m beyond south high end. The overall group is roughly71m long. These are cross-source estimates, not surveyed coordinates; orthophoto roof relief displacement remains a limitation. An initial±2m cue is not an accuracy guarantee.

## Same-datum vertical recalibration
The main upper elevation runs approximately x165–928 and y166–441:275/763=0.3604. At a62m high-wing length this implies22.35m, rounded in prose to22.3m. The former24.5m assumption depended on the now-rejected68m high-roof length. Northern high top is proportionally about21.4m and low hall top about6.6m; these remain photo-tested estimates. No floor count or basement depth is certified.

The generator retains the documented first-draft source-coordinate grid and explicitly applies62/68 to southern X and architectural Z before nominal1:400 conversion. Y depths stay independently estimated. North/east placement and the room-band rear step are independently adjusted to the physical coordinates above. This calibration is geometry generation, not a mesh repair. parameters.json records both the source-grid factor and physical estimated envelopes.

## Topology
X east,Y north,Z up. Southern room-band rear depth16m; eastern high service end rear depth9m. The rear step is fixed at aboutX47.5m: matching plan and same-roof orthophoto ratios put it at0.766of the62m high-wing length. It is not obtained by rescaling the old mistaken step. North high short wing is Y24..38m; low auditorium/connector spans the eastern gap and supports it. Northwest remains an open courtyard with simplified curved steps. Northern and southern high wings are nearly parallel, not perpendicular or an equal-height solid L. There is no invented high bridge.

## Source-led facade details
South:12 principal bays; lower grouping1wide+8narrow+3wide;8small upper-wall vertical slots; two broad upper recessed rows with set-back glazing and parapets; lower narrow deep openings, wider end groups and simplified ground louvers; long slender fins and continuous ledges. Top arch black opening is only the upper approximately10% of height, above a broad pale solid lower band; approximate opening bottom0.88H/top0.98H follows the near-frontal photo rather than a large tunnel cut to0.82H. It has restrained thickened internal uprights.

Six foreground shallow arches remain separated from the facade and physically tied/rooted. West-end projecting window/plate block differs from eastern low entry. East entrance uses broad canopy, tall pier, wide steps and a recessed doorway. North short-wing eastern end has photo-supported broad recesses/partial parapet blocks and stacked plates, without invented fine pane counts.

Main long-wing courtyard face is independently organized from the inferred reverse design elevation:12bays, broader top and base rows, narrower middle rows, eastern stair/glass strip above the low roof. It is not photographically verified. North short-wing north wall is an explicit unknown simplified blank wall, not a mirrored facade. Roofs are conservative recessed flat fields/parapets only; no photovoltaics, renovation canopy, unseen equipment or neighbor.

## Manufacturing approach
Nominal1:400, physical base200×125×2.4mm; estimated overall height58.25mm. Broad base connects arches and stairs. Thin exposed items are generally about0.9–1.2mm or more; these are manufacturing choices rather than as-built dimensions or a global minimum guarantee. The white upper arch rim is thickened to about1.1mm. The unverified eastern high-roof inner recess is omitted, leaving its flat outline intact and avoiding a roughly0.57mm skin above the arch. Windows are blind recesses into solid exterior mass, not a hidden invented interior. No physical printing has occurred and support needs remain disclosed.

Early draft images use CPU8samples at70% resolution. Formal v11 images use CPU64samples,1thread,1000×780 and no unavailable OIDN.

The v11 window headers start at the top of the true openings, with solid roots. Courtyard step ends extend slightly into the south wall to avoid tangent micro-gaps. These changes do not relocate the main axes or change the inner high-arch opening.
