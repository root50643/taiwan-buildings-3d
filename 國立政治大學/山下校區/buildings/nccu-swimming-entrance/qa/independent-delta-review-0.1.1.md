# Independent narrow delta review — NCCU service-wing segment 0.1.1

Reviewed 2026-10-24. **PASS** for the bounded path-portability/document-cleanup delta relative to independently reviewed 0.1.0. This is not a new whole-building, date-specific, measured-dimension or printability review.

## Independently executed checks

- Opened old and final revised scenes in Blender 4.3.2 and extracted all 44 objects: mesh vertices/edges/polygons/material assignments, transforms/visibility, camera, lights, world, used material node inputs and render settings. All used-scene semantics are identical: SHA256 `7a8fe0e67d76cea3b1f27e22f09f76ca47d3524a21269ac96007e4a91395f8db`.
- Saved render output is package-relative `//previews/right-end.png`; file-browser directory is `//`. No external libraries, packed images or source-image datablocks. Empty runtime Render Result is not a photo texture.
- Resave also removes the unused zero-user factory material named Material, assigned to no object. All seven model materials and the presentation-floor material are unchanged. This harmless orphan removal is explicitly included, not hidden as a two-field-only assertion.
- Independently rendered both old and final revised saved scenes at full 1600 × 850 resolution and 64 Cycles samples. Their 5,440,000 decoded RGBA8 bytes are identical: `8d828be43780cdfe354202315d52074a2ec14050f473c2a24aa2cd619628e98b`.
- All five delivered preview files remain byte-identical to 0.1.0. These are a separate evidence claim: the delivered right-end preview pixel hash differs from the fresh saved-scene rerender hash, already in 0.1.0. This review does **not** claim rerender equals delivered preview or PNG file hashes are deterministic. It establishes no old-to-new rendering regression.
- Original STL, 3MF, mesh.json, construction.json and geometry builder are byte-identical. parameters.json changes only version 0.1.0 → 0.1.1. Source URLs, dates, observations and hashes are unchanged; only private gate metadata is removed.
- README/QA edits remove archive/process narration without removing the exact partial-segment title, unknown photo dates, omitted high hall/roof/ramp, inferred scale/materials, neutral closure explanation, overhang/thin-feature/bed-clearance warnings or no-slicer/no-physical-print limitations. build_scene.py now saves portable paths for future rebuilds.
- Raw scan of all revised candidate files found no complete or known residual executor-workspace, temporary-directory, agent-home, private archive-host or credential markers. The fixed-length path buffers were also checked for old tail fragments, not only the new effective RNA values.

## Exact scene binding

- 0.1.0 scene SHA256: `09619e8028ee82bcd0f8c004fecaa272a4eb45ca0b346f4d9c785d720893b6af`
- Final reviewed 0.1.1 scene SHA256: `8128ea80af0cc0c7250ba358a64ac36748f7e4ff79dacf49b66e1e13d563b090`
- Unchanged model STL SHA256: `5d4275a5d0f5a6b0e574a09bb89eab4e1401b3ae7f6f6e26a9f4317550d3f533`
- Unchanged model 3MF SHA256: `b57fe2de524f9253f9bf5749a06aecfddf59a51fb5dd38dab023b87c3de54a60`

Final freeze manifest/checksum verification and a new artifact backup receipt remain required before publication. No geometry or source files were edited by this reviewer; only independent test outputs and this report were written.
