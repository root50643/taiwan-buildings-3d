# Actual STL geometry delta

Read-only comparison of the original STL at main `08604e70212673240173660584236e361221533f` and the fixed review candidate. All coordinates and measures use miniature millimetres; they are not surveyed building dimensions.

- Original: SHA-256 `801b9d6dedd0b8242dfea97938207b435c48f741a5d76195dcd7157881e29fa0`, 163,584 bytes; 3,270 faces; volume 409389.722507 mm³; bounds `[[-75.0, -62.0, 0.0], [75.0, 62.0, 68.0]]`.
- Candidate: SHA-256 `9c90c8b6b6f99076f2096783e78b793404fb81df88ee270d2eb02f21290e24b8`, 193,784 bytes; 3,874 faces; volume 406815.461779 mm³; bounds `[[-75.0, -62.0, 0.0], [75.0, 62.0, 68.0]]`.
- Input hashes unchanged during measurement: `True`.

## Horizontal sections

Triangle/plane intersections follow the existing `check_layers.py`: endpoints clustered within 0.0001 mm; every graph vertex must have degree 2; valid polygon loops are combined with even-odd nesting in Shapely. No contour repair is used. Exact-Z raw attempts and all failure reasons are retained in the JSON. A separate supplement at **Z + 0.000013 mm** avoids coplanar faces/vertices at designed heights; it is not relabelled as the exact-Z result.

The table uses the explicitly offset supplements consistently across both meshes. Added = candidate minus original; removed = original minus candidate.

| Requested Z | Measured Z | Original area mm² | Candidate area mm² | Added mm² | Removed mm² | Symmetric difference mm² |
|---:|---:|---:|---:|---:|---:|---:|
| 14 | 14.000013 | 7342.558328 | 7342.558329 | 0.000001 | 0.000000 | 0.000001 |
| 25 | 25.000013 | 7202.119780 | 7202.119777 | 0.000012 | 0.000015 | 0.000027 |
| 33 | 33.000013 | 7063.743016 | 5984.440254 | 0.000000 | 1079.302761 | 1079.302762 |
| 38 | 38.000013 | 6746.968668 | 6095.130761 | 0.000000 | 651.837907 | 651.837907 |
| 42 | 42.000013 | 4313.853765 | 4494.224249 | 506.399563 | 326.029078 | 832.428640 |
| 48 | 48.000013 | 3780.408372 | 3963.800918 | 183.392546 | 0.000000 | 183.392546 |
| 54 | 54.000013 | 2907.358364 | 2934.503979 | 27.145616 | 0.000000 | 27.145616 |

### Raw exact-Z evidence

| Z | Original raw result | Candidate raw result | Coplanar faces (original/candidate) |
|---:|---|---|---:|
| 14 | closed/valid | closed/valid | 94/94 |
| 25 | closed/valid | closed/valid | 95/105 |
| 33 | closed/valid | closed/valid | 22/22 |
| 38 | closed/valid | closed/valid | 46/18 |
| 42 | closed/valid | closed/valid | 22/22 |
| 48 | closed/valid | closed/valid | 0/0 |
| 54 | closed/valid | closed/valid | 0/0 |

## Actual 3D differences and limited crop checks

Trimesh `process=True` reconstructs shared vertices from STL triangle soup; no hole filling or winding repair is called. Manifold3D receives those STL coordinates as float64. Halfspace trims make closed crops of both input volumes; Boolean subtraction measures added and removed solid. Numerical equivalence threshold is 0.000001 mm³. Raw signed floating residues are retained, including values that round to -0.000000. This is a limited volume comparison, not a proof about every surface detail or an independent self-intersection certificate.

Global added volume: **4304.714517 mm³**; removed: **6878.975246 mm³**; symmetric difference: **11183.689763 mm³**; net change: **-2574.260728 mm³**. All Boolean statuses `NoError`: `True`.

| Crop | Original mm³ | Candidate mm³ | Added mm³ | Removed mm³ | Symmetric difference mm³ | Equal within tolerance |
|---|---:|---:|---:|---:|---:|---|
| `rear_y_ge_10` | 212969.223609 | 212969.223609 | 0.000004 | 0.000004 | 0.000009 | False |
| `entrance_x_ge_10_y_le_10` | 72130.962108 | 71960.614498 | -0.000000 | 170.347610 | 170.347610 | False |
| `entrance_x_ge_16_y_le_10_supplement` | 63721.342767 | 63721.342767 | 0.000000 | 0.000000 | 0.000000 | True |
| `stair_y_le_minus_50` | 8048.827534 | 8048.827534 | 0.000000 | 0.000000 | 0.000000 | True |

- `rear_y_ge_10`: Y >= 10 mm; all X and Z
- `entrance_x_ge_10_y_le_10`: X >= 10 mm and Y <= 10 mm; all Z. Includes a small part of the oval front body.
- `entrance_x_ge_16_y_le_10_supplement`: X >= 16 mm and Y <= 10 mm; all Z. Narrower entrance/connector zone outside the oval front roof.
- `stair_y_le_minus_50`: Y <= -50 mm; all X and Z. Outer portion of stair/cheek wall only; excludes inner treads overlapping front facade.

The rear crop's tiny nonzero Boolean residue is retained as a failed equality comparison at the stated strict tolerance. It must not be described as exact geometric identity. The JSON records full precision and every Boolean status.

The requested broad entrance crop is **not unchanged**: it includes the altered edge of the oval front body. Its difference is preserved above. The narrower X >= 16 crop separately tests the entrance/connector volume and must not be used to erase the broad crop result.

## Scope and reproduction

Only seven requested planes and the named halfspace volumes are compared. The crop at Y <= -50 verifies the outer stair/cheek wall only. It does not establish every stair tread is unchanged. These comparisons do not establish visual fidelity, minimum feature thickness, support feasibility, successful slicing, or print success. Existing raw QA failures/flags in other reports are unaffected.

Run from a Python environment with NumPy, SciPy, Trimesh, Shapely and optional Manifold3D:

```text
python qa/geometry_delta.py --original PATH/TO/original/model.stl
```

The default candidate is the package's `model.stl`; `--candidate` and `--output-dir` can select other paths. Both reports contain actual measured results; the script only reads meshes and writes its own JSON/Markdown.
