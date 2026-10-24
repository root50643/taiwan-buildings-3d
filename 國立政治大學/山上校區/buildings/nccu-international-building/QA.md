# Technical QA — not print-ready

Revision v8 raw STL SHA256 `5a1e22d6d987582f54867345d099b31a632d9104dcb2113d0089aeda0b9a60f3`.

- Raw exact-equality weld only; no repair, normal fix, filling, threshold face deletion or rounded contours.16,120triangles/8,050vertices. Zero nonfinite values, degenerate/duplicate faces, bad edge incidence/orientation, vertex-link failures or reversed stored normals. Watertight and consistent winding.
- **Two boundary shells, one connected material body**: positive outside and fully contained negative12-face B1-slot/slope cavity proxy, signed inner volume−951.825005mm³; total signed material volume334,276.004024mm³. Cavity is produced by a plan-evidenced B1 recess plus approximate external terrain covering its mouth, not proof of a real sealed room. No arbitrary tunnel/drain or cavity fill was used to force a single shell.
- Closed-triangle17-axis SAT on raw coordinates reports zero nonadjacent contacts, including all cross-shell candidate contacts. Shared-vertex pairs excluded; this is not exhaustive adjacent-face foldover certification.
- 374 sampled sections in total, including near-top; ordinary sections use unrounded0.2mm spacing: contours valid; **18warning layers** contain positive components failing0.8mm erosion. No thin-component exemptions.
- 512normal-ray samples all finite;245below0.8mm, minimum sampled0.224891mm. Samples are not a global wall-thickness proof. Nominal fine frame width0.225mm, parapet0.55mm, solid platform rim1.75mm.
- Explicit raw-mesh probes verify B1 recess/above1F enclosure, lower back-core versus3F setback, both6F low-roof voids,610band/rightwing/roof, right rear stair, supported ground, platform recessed air, limited portal opening/top and outside air. Rays hit both low roof decks and platform soffit as expected.
- Cavity six-axis first material-wall segments from its center: left28.682275/right56.75/front6.968751/back18.75/down1.8/up44.174999mm. These are local directional checks, not exhaustive cavity-wall minima. All inner shell vertices strictly inside outer shell; cross-shell contact absent.
- Native lib3mf strict import:0warnings, oriented manifold, exact original triangles/material indices. Actual single vertex+0.25mm edit and separate materialRGBA edit/write/read preserve other data; writer coordinate difference ≤0.000015259mm. Seven materials opaque; STL has no colour/alpha. Same-material construction primitives are coalesced before the final seven-material Boolean, preserving direct material-run provenance rather than nearest-face repainting. Known non-source slope-top/corner micro-lips were corrected in generator interfaces before this revision; no raw face deletion or relaxed QA.
- Blend/PNG native validation and clean-sourceZIP reconstruction are required before private final handoff; see bound generated reports for executed results rather than treating this checklist as completion.

## Unresolved manufacturing risks
No physical print, machine-specific slicing, support removal, resin drainage, strength or load tests. Enclosed cavity may trap SLA resin; FFF internal supports may be inaccessible. Fine surface relief can be lost at common nozzle scales. Platform/portal soffits need support consideration. Do not label this print-ready, support-free or guaranteed printable.

## Source/rights limits
Proportional emergency-plan tracing, approximate heights/windows/slope; photo dates unknown, not verified2026 condition. Unseen fine windows neutral. Source photos/PDF/overlays remain separate/private. No explicit actual-PDF reuse license located, no broadCClicense granted. The historical technical verification did not perform Git stage/commit/push.
