# Exact diagnosis of the 20 floating-point self-contact flags

The generic geometry report remains a failure: its original 20 flagged pairs
and exit status 1 are not changed. This supplement classifies every reported
pair using exact rational arithmetic on the actual finite STL coordinates.
It does not certify all other mesh pairs by exact arithmetic or claim a print.

## Input and result

- STL SHA-256: `4e73e7094c83de47c19bcc6121fee575c1360b285d597773d983a873f46b7f5a`.
- Generic report SHA-256: `9d7253369d81df71bdbdb40d4c0576d2452fe7eeed26d9bbf9e52c5933a94f23`.
- 20 nonempty, unique source pairs; all 20 evaluated exactly once.
- 10 pairs intersect only on their shared topological edge.
- 10 pairs intersect only at their shared topological vertex.
- No flagged pair has an intersection outside its shared topology.
- Raw STL triangle order/coordinates and `process=True` triangle order/coordinates
  are equal; all coordinates are exactly float32-representable.
- An exact degeneracy guard scanned all 2,936 input triangles: none degenerate.

`diagnosis.json` preserves the initial diagnostic output unchanged.
`diagnosis-verified.json` is the final guarded output, including input/report/script
hashes, every pair's actual triangles, shared vertex indices, exact signed plane
values, exact interval endpoints and classification. No source image is required.

All flagged pairs lie near the connector/main-body join, at x = 80 to about
82.906 mm, rather than the distant explicit cut toward the omitted Yuanzhi.
For example, faces 1560 and 1561 share vertex indices 907 and 912. Their unit
normal cross-product norm is about 8.708e-7. The two nonshared vertices lie
about 5.063e-7 mm and 6.381e-7 mm from the opposite planes. These are distinct
planes on the stored float32 mesh, yet the generic check's 1e-6 mm plane-cut
tolerance also treats the nonshared vertices as on-plane. Reconstructing an
intersection line from such tolerant cuts is ill-conditioned and generates
the reported false extra contact. The exact cuts contain only the actual
shared-edge endpoints. Faces 1547 and 1561 share only vertex 907; their exact
plane-interval intersection is that vertex alone. The per-pair evidence shows
the same two patterns repeated at ten band elevations.

The model and generic checker were not modified to avoid these flags. The
partial exact supplement is the evidence for interpreting these 20 flags;
the generic report must continue to be described as failed numerically.

## Reproduce

Python dependencies are numpy and trimesh; `fractions.Fraction` is standard
library. No bpy, render, Shapely intersection kernel or external geometry
service is used by this diagnostic.

From the model package root, after placing the two Python files in `qa/`:

```text
python qa/flag_diagnosis.py models/v1/model.stl qa/qa-report.json --json /a/new/diagnosis.json
python qa/run_diagnosis_controls.py --json /a/new/controls.json
```

`flag_diagnosis.py` exits 1 for an input/report SHA mismatch, empty flag list,
duplicate pair (including reversed duplicates), invalid/out-of-range face
indices, changed raw/processed order or coordinates, non-float32 coordinates,
degenerate triangle, uncovered flag, unexpected exact intersection, or failed
exact classifier controls. Successful diagnosis exits 0. This exit status
concerns only the supplement and cannot replace the original checker result.

The exact algorithm uses unnormalized rational plane normals, exact signed
plane cuts and one nonzero coordinate of the common plane-intersection line
to intersect closed intervals. Coplanar pairs use rational polygon clipping
with exact orientation tests. Expected contact is then checked against the
actual shared mesh vertex/edge coordinates. Rational numbers represent the
stored binary coordinates exactly; they do not recover ideal pre-export CAD
surfaces, real dimensions or historical appearance.

## Controls and actual execution

`controls.json` records eight small classifier/control expectations: disjoint
parallel triangles, legitimate noncoplanar shared edge, legitimate shared
vertex, true noncoplanar crossing, coplanar area overlap, legitimate coplanar
shared edge, near-coplanar shared edge, and degenerate-triangle rejection.
All passed. True crossing and coplanar area overlap classify as unexpected
intersections; the legitimate shared contacts are accepted.

It also records seven real CLI invocations on tiny synthetic STL/report pairs:
a valid shared edge exits 0, while mismatched SHA, empty flags, reversed
duplicate flags, out-of-range face and a degenerate mesh each exit 1 with the
expected guard reason. A genuine crossing also exits 1 based on the exact
intersection result. Tiny input and result artifacts are in `guard-controls/`.
No whole-model geometry screen or Blender render was rerun for this task.

One exploratory source-parameter read used the workstation's legacy default
text encoding and raised a UnicodeDecodeError after successfully printing
diagnostic values. It changed no artifact; final scripts explicitly read JSON
as UTF-8. The first exact model diagnosis and all subsequent exact/guard
controls completed successfully; no failed exact run is presented as passed.
