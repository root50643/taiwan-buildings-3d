# Manufacturing QA tools

These scripts do not repair, simplify or rescale physical STL files. They preserve
raw flags and create evidence for later independent review. All dimensions are mm.

Python dependencies: numpy, trimesh (tested 4.12.2), shapely (tested 2.1.2),
manifold3d, rtree, scipy, and matplotlib for the section PNG. PrusaSlicer console
must be supplied with `--slicer` or `PRUSASLICER_EXE`; no host-specific path is
embedded in the portable scripts.

`manufacturing_qa.py MANIFEST --output OUTPUT --section-step 0.2`

`slice_qa.py MANIFEST --output OUTPUT --run-label trial-01`

`control_tests.py --output control-tests.json` executes nine known crossing,
coplanar-overlap, topology-contact and box controls. It exits nonzero on failure.

`vertex_links.py MANIFEST --output vertex-links.json` checks every vertex link for
a single connected degree-two cycle, detecting pinched vertex fans.

`contact_patches.py MANIFEST --output contact-patches.json` calculates actual
coplanar mating area for every declared adhesive pair. The 0.0001 mm plane
tolerance handles STL floating point roundoff only; it is not a fit tolerance.

`assembly_sections.py MANIFEST --output OUTPUT` generates original geometry
sections and selected open-void occupancy probes.

The final v5 mesh report reuses geometry QA only where the exact STL SHA-256,
thickness threshold and complete section-height list match v4; it rechecks the
changed 08 mesh and all 45 assembly pairs. Raw flags are copied unchanged.
`--reuse-report` is optional; omit it for a complete independent rerun.

The slicing script invokes the actual PrusaSlicer 2.9.6 console binary. Every trial
gets a new directory and existing trials cannot be overwritten. G-code is **QA
only**, lacks machine start/end code, and is not machine ready. Local host paths
are redacted from logs and G-code metadata. No profile or global setting is changed;
the slicer uses a task-local data directory.

Manifest schema:

```json
{
  "units": "mm",
  "parts": [{
    "id": "north",
    "stl": "print/north.stl",
    "expected_components": 1,
    "min_feature_mm": 0.8,
    "supports": "none",
    "assembly_transform": [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
  }],
  "expected_contacts": [{
    "a": "north", "b": "bridge",
    "max_intersection_mm3": 0.00001,
    "min_clearance_mm": 0,
    "max_clearance_mm": 0.35
  }],
  "section_heights_mm": [1, 5, 10]
}
```

`assembly_transform` maps physical print coordinates to assembled coordinates.
`supports` accepts `none` or `buildplate`. Every part pair is checked for contact,
penetration and clearance; the manifest makes the intended contacts explicit.
An expected contact's maximum intersection volume must be justified by the joint
design; it is not a generic collision waiver.

Mesh checks merge identical STL positions only for analysis, then inspect all
faces, components, winding, duplicates, degeneracy, and every triangle AABB pair
for crossing or non-topological contact. Triangle intersections use plane cuts
and 2D Shapely coplanar intersection, with epsilon 0.000001 mm. No triangle sample
or cap is used. Every face-centroid inward thickness ray is tested. Z sections
at 0.2 mm plus explicit heights retain loop, area, 0.8 mm morphological opening
and 45-degree outward-layer flags. Opening/thickness flags require geometric
interpretation around bevels/taper tips. They are never silently marked pass.

Assembly clearance uses every vertex against the opposite triangles plus every
edge pair whose bounding boxes could improve that minimum. This covers
vertex/face and edge/edge closest configurations. Manifold computes intersection
volume for all overlapping part bounds. Results retain any boolean uncertainty.

The scripts cannot establish arbitrary-point wall minima, safe support removal,
physical fit or successful printing. Those limits must remain explicit in the
candidate's manufacturing notes.
