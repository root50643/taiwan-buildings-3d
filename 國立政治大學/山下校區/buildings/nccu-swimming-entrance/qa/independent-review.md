# Independent artifact review — NCCU entrance service-wing segment

Reviewed 2026-10-24, approximately 11:28–11:33 UTC. Reviewer is separate from the model builder. Read-only review of the model/source files; this report is the only file written by the reviewer. No downloads, repository writes, source-pack edits, or publication were performed.

## Decision

**PASS for the explicitly bounded, approximate exterior segment. No blocking issue remains in the reviewed geometry, materials, README or QA scope.** No blocking contradiction requiring a geometry change was found in the inspected version. This is not a validation of the whole swimming hall, a measured reconstruction, a confirmed roof form, a date-specific appearance, or physical print success.

Use the exact display title **游泳館入口側服務翼節段（校方調查資料參考外觀；照片年代未定）** wherever the model is listed. Do not shorten it to an unqualified whole-building “游泳館” entry.

## Sources and visual comparison

Independently read `new-building-final-scope/FINAL-SCOPE.md` and `new-building-scope-addendum/SCOPE-CORRECTION.md`. Viewed the actual retained photo streams 700/701 and native plan streams 703/704, not just thumbnails or the builder's descriptions. Also viewed the five final model renders: front, front-right, rear-cut, top and right-end.

- The narrow, two-storey strip and the two stair-location projections are compatible with the bounded plan interpretation. The taller pool hall and its entire roof are omitted, as required. The solid model intentionally has no interior.
- The service-front proportions, continuous dark upper glazing/louver bands, lower ventilation bands, dark plinth and tan/pink wall family are recognizable approximations of photo700. The exact repeated bay count, window arrangement, entrance-door divisions, step count and dimensions are not recoverable from the source and must remain explicitly schematic.
- The two lower-storey front projections are **not** source-verified complete stair towers. The current closed blocks preserve local enclosure rather than inventing two exposed symmetrical flights. Their full outer skin and uniform height remain an assumed printable envelope. README now says this plainly; keep that qualification in the release.
- The central entry position is broadly compatible with the plans. Photo700 visibly includes a partly obscured ramp; omitting its unregistered geometry is acceptable under the binding scope, only because the model/README explicitly says it is omitted. The modeled entry steps are not evidence that the site lacks an accessible route.
- The neutral rear face is the cut at the omitted pool-hall connection, not a real back elevation. Neutral top and unobserved short-end surfaces are appropriate. The flat cap is a modeling closure, not proof of a flat real roof.
- Photo701 provides context for the omitted hall and complex roof only. It cannot establish photo date, a pre-2023 condition, a panel count or current-2026 appearance. No such claims were found in the inspected README, parameters or sources metadata.
- A nominal approximately 1:300 scale, inferred from the official 50 m pool and raster-plan ratios, is adequately distinguished from measured dimensions. The printed S=1/150 is not used as a valid resized-PDF ruler. Local X/Y view labels are not compass directions.

## Independently executed digital checks

The following were executed separately from the builder's reported QA:

- Exported `model.stl`: **1,108 vertices, 2,212 triangles, one watertight shell, consistent winding, Euler characteristic 2**, zero edges with a face incidence other than two. Minimum triangle area approximately 0.00021845 mm²; none below the declared 1e-8 mm² degeneracy threshold.
- Vertex-link topology on `mesh.json`: every vertex has a single connected cycle; **zero non-manifold vertex links**.
- Bounds from exported STL: approximately **212 × 32.4 × 31.4 mm**, including the display/print base. Geometric volume approximately 122,318.99 mm³; this is not a filament estimate or infill prescription.
- `model.3mf` opened with **lib3mf 2.5.0 strict mode: zero warnings, valid mesh**. Face indices and all 2,212 per-triangle material assignments matched `mesh.json`. Seven real base materials were present; this is not merely an STL renamed as 3MF.
- The 3MF archive contains only its content-types file, relationship file and model XML: no photographs, textures or other image files.
- `scene.blend` reopened in **Blender 4.3.2**. The designated export mesh has the same 1,108 vertices / 2,212 triangles and seven named material slots. The scene has millimetre unit scaling; its object properties preserve the partial scope and exact title. No external-file or packed image datablocks were found.
- All **82 triangles on the rear connection/cut plane** use the neutral material. The highest cap plane also uses neutral material.

Reviewed geometry hashes:

- STL SHA-256: `5d4275a5d0f5a6b0e574a09bb89eab4e1401b3ae7f6f6e26a9f4317550d3f533`
- 3MF SHA-256: `b57fe2de524f9253f9bf5749a06aecfddf59a51fb5dd38dab023b87c3de54a60`

## Builder QA reviewed and its limits

Reviewed the builder's format-geometry, lib3mf material-edit roundtrip, Blender material-edit/reopen, clean geometry rebuild, and 157-layer horizontal-section reports, plus the format/section scripts. The reports distinguish a real material edit/write/reopen from a simple XML inspection. They record float32/serialization differences rather than claiming bitwise-identical edited geometry. The section script checks the exported STL, not only an unexported Boolean object.

The 0.2 mm section screen reports one valid connected region at every tested level and no new isolated regions. It also identifies **five overhang-growth levels**, including the entrance canopy and recess heads. This is a useful screen, **not an actual Cura/Prusa/Orca toolpath or physical print test**. Do not label it “slicer passed,” “support-free,” or “print guaranteed.” A 3 mm canopy projection and 0.9 mm canopy/frame features need printer-specific support, line-width and scale review. At 50% scale those 0.9 mm features become 0.45 mm. The 212 mm model length leaves only 4 mm per side on a nominal 220 mm usable bed; a 5 mm all-around brim would require at least 222 mm, before other clearances.

The topological checks do not constitute structural-strength testing, dimensional metrology, an exhaustive triangle-intersection proof, a machine-specific material test or accessibility validation. The original simple-solid Boolean construction and successful closed-surface tests support digital mesh usability within these limits.

## Final documentation recheck / package hygiene

1. Preserve the current prominent README scope, uncertainty, scale, date and ramp-omission disclosures. Its full text was reviewed after the builder's update.
2. `scene.blend1`, present at the initial directory inspection, was confirmed absent from the package at 11:32 UTC. All five inspected final previews have the corrected, non-overexposed materials. Keep rejected/intermediate renders out of the release.
3. At 11:32 UTC, re-read the completed QA.md, dependency/version record, five-file byte-identical clean geometry rebuild report and Blender edit/reopen report. The QA text includes the five overhang flags, explicit absence of machine slicing/physical testing, unknown minimum-wall certification, and 212 mm / brim bed-clearance warning. These limitations are now adequately documented. Final manifest/checksums and freeze verification remain the builder/publisher responsibility; this review does not attest to future files.
4. Keep the source archives/private review images out of the public package. Source URLs/hashes may be included, but the reviewed source material carries no established photo/plan redistribution license.
5. This reviewer did not re-perform WebDAV transfer verification or GitHub publication verification. The pre-model source gate was accepted from the binding archived receipts; final durability/publication remain the parent publisher's responsibility.

No unrelated model, homepage representative or existing package was modified during this review.
