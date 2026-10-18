# Actual STL geometry delta

Read-only comparison of the previous candidate STL at `e45f8d65989cedca7fec439ce5b6a212323c4d2b` and the fixed review candidate. All coordinates and measures use miniature millimetres; they are not surveyed building dimensions.

- Original: SHA-256 `9c90c8b6b6f99076f2096783e78b793404fb81df88ee270d2eb02f21290e24b8`, 193,784 bytes; 3,874 faces; volume 406815.461779 mm³; bounds `[[-75.0, -62.0, 0.0], [75.0, 62.0, 68.0]]`.
- Candidate: SHA-256 `00f6bbdd09196fba873d843bb9d50a1c3aad4e19e760978333dce6f49740627c`, 196,384 bytes; 3,926 faces; volume 407420.687335 mm³; bounds `[[-75.0, -62.0, 0.0], [75.0, 62.0, 68.0]]`.
- Input hashes unchanged during measurement: `True`.

## Horizontal sections

Triangle/plane intersections follow the existing `check_layers.py`: endpoints clustered within 0.0001 mm; every graph vertex must have degree 2; valid polygon loops are combined with even-odd nesting in Shapely. No contour repair is used. Exact-Z raw attempts and all failure reasons are retained in the JSON. A separate supplement at **Z + 0.000013 mm** avoids coplanar faces/vertices at designed heights; it is not relabelled as the exact-Z result.

The table uses the explicitly offset supplements consistently across both meshes. Added = candidate minus original; removed = original minus candidate.

| Requested Z | Measured Z | Original area mm² | Candidate area mm² | Added mm² | Removed mm² | Symmetric difference mm² |
|---:|---:|---:|---:|---:|---:|---:|
| 14 | 14.000013 | 7342.558329 | 7342.558329 | 0.000000 | 0.000000 | 0.000000 |
| 25 | 25.000013 | 7202.119777 | 7202.119777 | 0.000000 | 0.000000 | 0.000000 |
| 33 | 33.000013 | 5984.440254 | 5984.440725 | 0.000471 | 0.000001 | 0.000472 |
| 38 | 38.000013 | 6095.130761 | 6095.130760 | 0.000000 | 0.000001 | 0.000001 |
| 42 | 42.000013 | 4494.224249 | 4494.224249 | 0.000000 | 0.000001 | 0.000001 |
| 48 | 48.000013 | 3963.800918 | 3963.800952 | 0.000035 | 0.000001 | 0.000036 |
| 54 | 54.000013 | 2934.503979 | 3037.516537 | 103.012558 | 0.000000 | 103.012558 |

### Raw exact-Z evidence

| Z | Original raw result | Candidate raw result | Coplanar faces (original/candidate) |
|---:|---|---|---:|
| 14 | closed/valid | closed/valid | 94/94 |
| 25 | closed/valid | closed/valid | 105/105 |
| 33 | closed/valid | closed/valid | 22/22 |
| 38 | closed/valid | closed/valid | 18/18 |
| 42 | closed/valid | closed/valid | 22/22 |
| 48 | closed/valid | closed/valid | 0/0 |
| 54 | closed/valid | closed/valid | 0/0 |

## Actual 3D differences and limited crop checks

Trimesh `process=True` reconstructs shared vertices from STL triangle soup; no hole filling or winding repair is called. Manifold3D receives those STL coordinates as float64. Halfspace trims make closed crops of both input volumes; Boolean subtraction measures added and removed solid. Numerical equivalence threshold is 0.000001 mm³. Raw signed floating residues are retained, including values that round to -0.000000. This is a limited volume comparison, not a proof about every surface detail or an independent self-intersection certificate.

Global added volume: **605.225582 mm³**; removed: **0.000026 mm³**; symmetric difference: **605.225608 mm³**; net change: **605.225557 mm³**. All Boolean statuses `NoError`: `True`.

| Crop | Original mm³ | Candidate mm³ | Added mm³ | Removed mm³ | Symmetric difference mm³ | Equal within tolerance |
|---|---:|---:|---:|---:|---:|---|
| `rear_y_ge_10` | 212969.223609 | 212969.223609 | 0.000000 | 0.000000 | 0.000000 | True |
| `entrance_x_ge_10_y_le_10` | 71960.614498 | 71960.614498 | 0.000000 | 0.000000 | 0.000000 | True |
| `entrance_x_ge_16_y_le_10_supplement` | 63721.342767 | 63721.342767 | 0.000000 | 0.000000 | 0.000000 | True |
| `stair_y_le_minus_50` | 8048.827534 | 8048.827534 | 0.000000 | 0.000000 | 0.000000 | True |

- `rear_y_ge_10`: Y >= 10 mm; all X and Z
- `entrance_x_ge_10_y_le_10`: X >= 10 mm and Y <= 10 mm; all Z. Includes a small part of the oval front body.
- `entrance_x_ge_16_y_le_10_supplement`: X >= 16 mm and Y <= 10 mm; all Z. Narrower entrance/connector zone outside the oval front roof.
- `stair_y_le_minus_50`: Y <= -50 mm; all X and Z. Outer portion of stair/cheek wall only; excludes inner treads overlapping front facade.

For this R2-versus-e45 comparison, all four named crops have zero added/removed volume and equal_within_volume_tolerance=true in the retained JSON. This limited crop comparison is not a proof of identity of every surface or the whole building. The earlier e45-versus-main report's nonzero rear residue and failed strict equality remain unchanged in qa/geometry-delta.json and qa/geometry-delta.md.

## Scope and reproduction

Only seven requested planes and the named halfspace volumes are compared. The crop at Y <= -50 verifies the outer stair/cheek wall only. It does not establish every stair tread is unchanged. These comparisons do not establish visual fidelity, minimum feature thickness, support feasibility, successful slicing, or print success. Existing raw QA failures/flags in other reports are unaffected.

Run from a Python environment with NumPy, SciPy, Trimesh, Shapely and optional Manifold3D:

```text
python qa/geometry_delta.py --original PATH/TO/original/model.stl
```

The default candidate is the package's `model.stl`; `--candidate` and `--output-dir` can select other paths. Both reports contain actual measured results; the script only reads meshes and writes its own JSON/Markdown.
