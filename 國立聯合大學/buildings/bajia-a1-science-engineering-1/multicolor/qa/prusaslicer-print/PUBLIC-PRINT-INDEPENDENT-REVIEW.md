# A1 four-tool PRINT: independent actual Prusa reopening

**GO for the four-tool PRINT demonstration at file and geometry level.** One actual PrusaSlicer 2.9.6 import/export preserved one object, four named printable volumes and tools 1 through 4. Every source and exported volume is closed under exact-coordinate vertex merging, consistently wound, positive-volume and free of exact zero-area triangles. The retained eight-region EDITABLE project and its four disclosed interface flags remain separate evidence.

Actual manufacturing remains conditional on the real printer, material and slicing setup. No GUI check, slicing, G-code or physical print was performed.

## Fixed identity and actual command

- Input: `multicolor/a1-four-tool-PRINT.3mf`, SHA256 `7cf863dd73dfa74fefd9522455cc79f01fcf0e58ca348cdda406884a760ee2df`.
- Source envelope: `model.stl`, SHA256 `f25654284af62f9f454421da0dbb1a21bcd9b0645bbfc7c6deb2df3f327f0023`.
- Actual roundtrip: SHA256 `0049cc71204eaaaa13ec5d747ee98372d0c87c0a5cabdd9a673ffa51ec2cc530`.
- Executable: PrusaSlicer 2.9.6 console, SHA256 `7fd50b52d1cc3da87dbcb71e45e764412dd45688bea028f351333e86d9769704`.

The expected input SHA was checked before the run and remained unchanged afterward. Exactly one PRINT CLI import/export was run, with exit code 0 and empty stderr. Exact executed absolute argv and raw logs are preserved locally; this public note uses relative package paths. A normalized reproduction command from the building package directory is:

```text
prusa-slicer-console.exe --datadir qa/prusa-print/native/cli-data --config-compatibility disable --load multicolor/generic-four-tool-REFERENCE.ini --dont-arrange --no-ensure-on-bed --info --save qa/prusa-print/native/effective.ini --export-3mf --output qa/prusa-print/native/roundtrip.3mf multicolor/a1-four-tool-PRINT.3mf
```

Create those separate output directories first and use the identified 2.9.6 installation. No executable is claimed to be bundled with this model. No slice, G-code, merge, split, scaling, rotation or centering action was requested.

## Four volumes and geometry

Both input and actual export have one resource mesh object, one build instance, explicit `millimeter` units and four printable volumes. Inclusive volume ranges cover all 34,556 triangles once, without gaps or overlapping ranges. Names, tools and triangle counts were retained:

| Part | Tool | Triangles before/after | Source and export closed / winding consistent / positive volume | Exact zero-area faces before/after | Export unique edges, all incidence 2 |
|---|---:|---:|---|---:|---:|
| 01-light-wall | 1 | 14,280 / 14,280 | yes / yes / yes | 0 / 0 | 21,420 |
| 02-brick | 2 | 5,600 / 5,600 | yes / yes / yes | 0 / 0 | 8,400 |
| 03-slate | 3 | 9,484 / 9,484 | yes / yes / yes | 0 / 0 | 14,226 |
| 04-glazing | 4 | 5,192 / 5,192 | yes / yes / yes | 0 / 0 | 7,788 |

The source world bounds are `[-75,-74,0]` to `[75,74,57.099998474121094] mm`: a `150 x 148 x 57.099998474121094 mm` envelope at the original coordinates. Exported bounds differ only in final z serialization, `57.0999985 mm`. The maximum measured coordinate change between corresponding triangle/vertex slots is `7.625879e-6 mm`; no face-count change or repair warning occurred. Coordinate changes are quantified, not called exact equality. Rounded triangle hashes can differ across rounding-bin boundaries even when slotwise changes are this small.

In particular, the merged slate volume has no zero-area triangles before or after actual reopening. The previously disclosed four PV/roof same-tool interface flags are absent from this PRINT geometry. This does not remove or rewrite their evidence in the eight-region EDITABLE project.

## Independent source-union comparison

The check parsed the original 10,638-triangle binary STL directly, promoted its exact float32 coordinates to float64, reconstructed the PRINT volume triangles in world coordinates, merged exact equal vertices and constructed Manifold `Mesh64` objects. All four source and exported group objects returned `Error.NoError`. Each group's triangle count was unchanged by the kernel construction; raw topology and zero-area checks were conducted separately. The group unions were compared in both boolean directions against the source.

| Comparison | Reference minus test volume (mm³) | Test minus reference volume (mm³) | Sum of absolute difference volumes (mm³) |
|---|---:|---:|---:|
| Source STL versus fixed PRINT union | 1.1368684e-13 | -1.3043039e-13 | 2.4411723e-13 |
| Source STL versus actual Prusa export union | 0.00895094055 | 0.00591236091 | 0.01486330146 |

The source and fixed PRINT union both have volume `502730.8731529508 mm³` in this computation. The actual Prusa union is `502730.870114371 mm³`. The first comparison produces tiny nonempty residual objects with signed floating-point residues; it is numerical agreement, not an exact-arithmetic emptiness proof. The later nonzero differences record the actual precision conversion rather than hiding it behind a pass threshold. Prusa's own `--info` volume is a separate summary statistic; it was not used for this independent union result.

The original envelope STL and PRINT hashes were unchanged through the comparison. Detailed statuses, residual triangle counts, signs and limitations are retained in `independent-source-union.json` and `PUBLIC-PRINT-SUMMARY.json`. No boolean result or repair was written back to the candidate.

## Profile and preserved EDITABLE data

The effective configuration saved by the actual PRINT run has four reference nozzle entries, four colors, four zero offsets and `single_extruder_multi_material=0`. Support and interface use existing tool 1. The embedded config bytes are identical to those in the fixed R2 EDITABLE project that was separately reopened successfully without an external `--load`. This PRINT run itself used the supplied reference INI; no second PRINT CLI run was performed.

The 0.4 mm reference diameters and zero offsets are placeholders for assignment checking, not calibration for the unknown four-head printer. A dedicated support material occupies one physical tool: four main colors plus a separate support material would require five tools. This four-tool project provides no fifth tool.

The preserved R2 files were independently rehashed and remain:

- `multicolor/a1-four-tool-prusaslicer.3mf`: `80e665598c3d39e0e0dfb572622b6c44fda4222613b2dea8ed07645625e454de`.
- `multicolor/a1-four-tool-core.3mf`: `a9929cb9259c3c18c87b2653af119035e35bbc26f93d72ba4332552b0d3dc5b6`.

The original eight semantic regions, color mapping and flag reports remain available for editing. The new PRINT check does not recertify the generic core file as a portable physical-extruder mapping; its earlier Prusa import produced eight separate objects without explicit tool overrides.

CLI `--export-3mf` omits the full embedded print configuration by design in the versioned exporter action. Keep the fixed original PRINT project as the deliverable; treat the actual roundtrip as model/volume evidence and `effective.ini` as a separate settings record. [Official PrusaSlicer 2.9.6 action](https://github.com/prusa3d/PrusaSlicer/blob/version_2.9.6/src/CLI/ProcessActions.cpp#L141).

The file-level checks found no new geometric blocker requiring another variant. Machine tool registration, material bonding, purge/tool-change behavior, support generation/removal and physical strength still require the actual printer profile and manufacturing validation. This review does not claim those unperformed results.
