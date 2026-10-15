# Original-triangle dense normal audit

Run in a writable copy of this package using its pinned Python environment:

```
python check_dense_surface.py --out dense_evidence --stl output/model.stl
```

No geometry is edited. If `--stl` is omitted, the input is `--out/model.stl`.
The default minimum is 0.8 mm. Default source direction is the unit cross
product of the exact original float32 face vertices, calculated in long double.
`--normal-mode stored` instead uses the unit-normalized raw stored STL normal.
Both modes independently validate stored normal orientation and alignment.
The chosen definition is explicitly recorded; never mix their cached events.

## Required coverage and evidence

Every original raw face is kept with its original zero-based STL record index.
The ten barycentric samples are the centroid and all distinct permutations of
(0.98, 0.01, 0.01), (0.495, 0.495, 0.01), and (0.49, 0.49, 0.02).
No face repair, welding for rays, normal repair, simplification, remeshing,
Manifold accelerator, root-chord substitution, or geometric exception is used.
Exact coordinate welding is used only for a separate topology diagnostic.

`dense_original.cpp` directly indexes the unchanged original triangles in a
BVH. Long-double Moller–Trumbore predicates retain every positive intersection,
including coincident original faces and their IDs/barycentric coordinates/
orientation. A projected half-plane clip separately retains positive-length
coplanar triangle boundary spans. Grouping is only for interval logic; raw
records remain intact. Any mixed/tangent/nonalternating crossing is a failure.
A positive boundary overlap in first material or next air is a failure; a
positive overlap below the numerical boundary tolerance is unclassified and
also fails. There is no thickness tolerance allowance.

The source normal line is checked with two independent oblique parity rays at
five points: immediately before entry, just inside entry, material midpoint,
immediately after exit, and next-air midpoint. Every short or otherwise flagged
sample additionally gets compensated whole-original-mesh solid-angle winding
at all five points. No sign/absolute-value correction is applied to winding.
If a complete first interval cannot be established, the row remains
unclassified even when no meaningful control points can be constructed.

## Outputs

- `dense-audit.json`: definitive aggregate gate; exit 0 only when all gates pass
- `dense-source.json`: original STL SHA, face count, mode, sampling, triangle
  binary hash, and C++ helper hash, checked before reusing existing events
- `dense-events.txt.xz`: complete high-precision event stream for every sample in the release (the private archive retains this lossless xz container, without duplicating the original gzip)
- `dense-intervals.npz`: source face/sample IDs, all first/next interval lengths,
  status bitmask, and raw hit/boundary counts, including every failed row
- `dense-flagged-intervals.jsonl.gz`: every short/unclassified row, complete
  events/boundaries, independent controls and their winding results
- `dense-work/`: exact promoted original vertex/normal arrays, executables,
  and independent winding inputs/results for reproducibility

Each raw event line has three pipe-separated fields. The first is
`face,sample,point_x,point_y,point_z,normal_x,normal_y,normal_z,source_valid`, then
10 parity values (two directions for each of the five controls). The second is
semicolon-separated hits `t,original_face_id,u,v,normal_dot_ray`. The third is
semicolon-separated boundary intervals
`start_t,end_t,original_face_id,plane_residual,normal_dot_ray`.
Distances are measured from the original surface point plus 0.00001 mm outward.

`--screen-only` leaves any required independent winding stage explicitly
pending and failing. It is useful during geometry iteration.
`--reuse-events` verifies source/mode/helper identity and completes/repeats
classification and independent winding without repeating the dense BVH scan.
`--face-limit N` is only a mechanics diagnostic and cannot pass the all-faces
gate unless N includes the entire original mesh. `--threads N` controls the
whole-mesh winding workers (default 4).

The audit is a finite original-normal sample screen. It does not certify a
mathematical global minimum wall thickness. An unbounded next-air interval is
recorded as infinity in NPZ and null plus an explicit unbounded flag in JSON;
its near-exit and midpoint controls are within one millimetre after the exit.
All longer rays and their boundary spans are nevertheless retained.

## Lossless delivery compression and reuse

After an initial complete run, `dense_transcode_events.py --out AUDIT_DIRECTORY`
transcodes the complete gzip event bytes into xz/LZMA2 (preset 9, SHA256
container check). It compares decompressed SHA256 and byte count, updates
only packaging metadata in `dense-audit.json`, and keeps the original gzip
privately. No hits, IDs, intervals, digits, or line breaks are changed.
`dense-transcode.json` records both container sizes and the common
decompressed-content hash. Release packaging may omit the original gzip
and the reconstructible `dense-work/` binaries/raw arrays; retain the xz,
NPZ, source manifest, final audit, full flagged-row file, original STL,
source scripts and helpers, and these instructions.

For independent reclassification of delivered evidence, use the normal
command with `--reuse-events`. The script prefers the complete xz stream
when present and accepts the original gzip otherwise. The original source
STL, geometric-normal mode, sample count, and C++ helper hash must still
match the source manifest. Status/interval results are recomputed, and
any flagged/short rows again require the independent winding stage.

## Regression tests

Run `check_dense_tests.py` with the same Python environment. It checks a sound
cube, thin slab with independent winding, stored-normal mode, finite next-air
gap, coplanar overlapping boundaries, an open mesh, and a partial-coverage
failure, plus sub-float64 thickness and sub-tolerance positive-boundary
failures. All nine cases pass. Tests are mechanics evidence, not building approval.

Generic BVH, projected coplanar clipping, and compensated solid-angle formulas
were adapted from the Shute release helpers; no Shute/NYCU building-specific
qualification or exception was copied.

## Lean public delivery and complete private preservation

The enormous all-pass raw-event and NPZ caches may be preserved separately in
the complete private audit archive. The public set retains the exact STL-bound
summary, source manifest, every actual flagged/short row (empty for version1.1),
validator and helper sources, regression evidence, and hashes/byte sizes of
all private caches. Absence of the private cache from the public download is
not absence of the validation: the public validator regenerates every source
ray and control directly from the exact public STL. No actual failed sample
is omitted. The complete private archive retains the smaller lossless xz event container and dense NPZ arrays. The redundant original gzip is not duplicated in that archive; its container hash and the verified shared decompressed-content hash remain recorded.

Fresh reproduction (no private cache required):

```
python check_dense_surface.py --out AUDIT_DIRECTORY --stl output/model.stl
python check_dense_minimum_winding.py --out AUDIT_DIRECTORY --stl output/model.stl
python dense_transcode_events.py --out AUDIT_DIRECTORY
```

The optional second command independently evaluates compensated solid-angle
winding at five material/air points for each of the 30 shortest passing
intervals. This supplementary check does not replace, relax, or exempt any
of the full dense gates. The script reads the full private/reproduced stream
and original triangles. For the version1.1 evidence, all 150 controls pass.
