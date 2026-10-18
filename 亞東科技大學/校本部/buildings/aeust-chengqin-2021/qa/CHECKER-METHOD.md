# Bounded numerical geometry screening

This package uses the following checker for the Chengqin candidate. Synthetic
control reports concern only their tiny test meshes; candidate results are in
[qa-report.json](qa-report.json).

## Provenance

Adapted from `root50643/taiwan-buildings-3d`, verified source revision supplied to
this task: `56c252c0207bc8af202cc8b5b9e66da1c08a028b`.
Original path:
`吳鳳科技大學/校本部/buildings/wfu-apollo/qa/independent_geometry_qa.py`.
Original SHA-256:
`e4efdced79746debbc33df030de77c94053fa119d6bfe8f92e89de7a4452f61c`.
The original checker and the repository root and APOLLO QA README limitations
were read; the original program was not run against its building model.

The adaptation preserves the original floating-point intersection algorithm and
topology algorithm. Changes are per-material-component erosion tests, inclusion
of thin-feature results in the overall fail gate, thin/support synthetic
controls, nonempty-section/input guards, and transparent STL loading notes.

## Use

Dependencies: Python with `numpy`, `trimesh`, and Shapely 2.x. Blender is not
imported or required. Tested locally with Python 3.13.9, numpy 2.5.4,
trimesh 4.12.2, and shapely 2.1.2.

```text
python independent_geometry_qa.py /path/to/model.stl --json /path/to/new-report.json --negative-controls
python run_controls.py
```

Default layer height is 0.2 mm, overhang angle is 45 degrees from vertical,
and feature width is 0.8 mm (erosion radius 0.4 mm). Flags can be changed but
must be reported with results. JSON contains per-layer values, tolerances,
dependency versions and input SHA-256. A failed overall screen exits with 1;
the JSON is still saved for an ordinary geometric failure. A tool exception
does not constitute a valid completed report.

## What the pass means

- Loaded STL is one positive-volume, consistently oriented edge-connected
  closed solid; boundary edges, nonmanifold edges, duplicate/degenerate
  triangles and non-cycle vertex links are rejected.
- Every unordered triangle pair is considered by its axis-aligned bounding
  boxes. All overlapping AABB pairs get a numerical narrow-phase check.
  Contacts confined to genuinely shared mesh-index edges or vertices are
  permitted. AABB pair enumeration is not sampled.
- At all sampled layer midpoints, sections are nonempty closed material
  regions, and no reported unsupported area above 0.01 mm2 lies beyond the
  previous layer buffered by `layer_height * tan(angle)`.
- Each material component of each sampled section retains exactly one core
  after inward erosion by half feature width. Loss or splitting of even one
  component core now rejects the bounded screen. The previous whole-section
  counts remain in the report for comparison.

`trimesh` uses `process=True` to reconstruct shared vertices from STL triangle
records. The reported topology therefore concerns the loaded mesh; original
file SHA-256 preserves input identity. The checker does not fill holes, apply
booleans or call a normal-repair operation.

## Limits that must remain in the model package

This is a numerical mesh screen, not formal exact-arithmetic proof. AABB
enumeration is complete, but narrow-phase tests use floating point (default
1e-6 mm tolerance, near-parallel normal threshold 1e-9), and section endpoint
keys round to seven decimals. Extremely small contacts, degeneracies and
near-coincident geometry remain tolerance-sensitive.

All triangle pairs are enumerated in Python: time complexity is quadratic in
face count. Vertex-link checks also scan incident faces per vertex. This is
reasonable for low-face-count representative massing; do not quietly replace
it with random pair samples for a detailed mesh. If runtime becomes large,
use a reproducible spatial acceleration preserving all overlapping pairs and
state that change explicitly.

Horizontal sections are sampled, not continuous in Z. Details lying between
0.2 mm sample planes may be missed. Erosion checks component core stability;
it does not measure minimum wall thickness at every point, and attached thin
projections can disappear under erosion without emptying or splitting the
remaining core. Convex corners and tapered tips also need judgment. It does
not establish adequate Z thickness/layer count for facade relief. Review the
generator's declared minimum feature dimensions and sloped transitions too.

The first sampled section is assumed plate-supported; the interval from the
actual bottom to that section is not compared. Confirm the model's intended
orientation, flat bottom and Z bounds. Support comparison uses section areas
and 0.01 mm2 reporting tolerance; the boundary-distance diagnostic samples at
at most 0.1 mm spacing (distance underestimation at most 0.05 mm by Lipschitz
distance). It models neither bridge capability nor extrusion/nozzle paths,
adhesion, cooling, strength, shrinkage or material. A feature can fail this
conservative screen yet be printable with a bridge or support strategy.

The repository root README also requires the distinction between digital QA,
slicer inspection and physical printing. No slicer preview, G-code or actual
print is performed here. The model's historical identity, source fidelity,
unknown facade and dimensions need separate evidence review. Do not add
third-party reference images to the public package.

## Control evidence

`control-evidence.json` records the checker hash and all executed small checks.
All current control expectations passed:

- A clean 2 mm cube passes the CLI with exit 0.
- A topologically valid 0.4 mm wide bar has vanished cores in 10 layers and
  exits 1 despite passing topology, numerical self-contact and support tests.
  This specifically verifies that a thin-only failure rejects the full gate.
- A 0.4 mm neck between wider ends splits the eroded core in 10 layers.
- A convex frustum widening 2 mm per 1 mm Z exceeds the 45 degree envelope
  in 4 sampled layer comparisons.
- Overlapping cubes yield 18 unexpected contact/intersection pairs; cubes
  sharing only a vertex yield one nonmanifold vertex link. The clean cube
  produces no unexpected intersections.
- Existing missing-triangle, reversed-face and detached-cube controls are
  included by `--negative-controls` and all are detected in both CLI cases.

The tiny `control-artifacts/` input STLs and full JSON/stdout/stderr are retained
as evidence, including the expected thin-bar rejection. The files are synthetic,
not candidate models. There was no failed executed synthetic-control run to hide; a degenerate
triangle in a proposed negative-control triangulation was corrected by code
inspection before the first execution. No building or render was executed.
