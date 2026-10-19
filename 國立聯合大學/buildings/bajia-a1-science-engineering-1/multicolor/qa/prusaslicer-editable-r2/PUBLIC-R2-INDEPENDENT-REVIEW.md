# A1 R2 four-tool project: independent CLI review

**Conditional GO as an editable four-tool demonstration.** Actual PrusaSlicer 2.9.6 import/export retains one native object, eight named printable volumes and the intended four-tool assignments. R1's brick nonmanifold defect is absent. Four quantization-degenerate triangles remain at paired PV/roof material interfaces, so this is not a zero-degenerate or machine-ready print certification.

This public note uses paths relative to the building package. Exact executed absolute argv, raw logs and effective configuration files remain in the local independent-review evidence. No candidate file was modified.

This is the eight-region **EDITABLE** project review. It does not certify any separate merged four-volume `PRINT` project; that requires its own fixed hash and actual reopening evidence.

## Fixed candidates and actual reopening

| File | SHA256 |
|---|---|
| `multicolor/a1-four-tool-prusaslicer.3mf` | `80e665598c3d39e0e0dfb572622b6c44fda4222613b2dea8ed07645625e454de` |
| `multicolor/a1-four-tool-core.3mf` | `a9929cb9259c3c18c87b2653af119035e35bbc26f93d72ba4332552b0d3dc5b6` |
| `multicolor/generic-four-tool-REFERENCE.ini` | `dbeb712b44d1f35b81bb4764a446e0699207529ced0752d68a010c4034d22adc` |

The actual executable was PrusaSlicer 2.9.6 console, SHA256 `7fd50b52d1cc3da87dbcb71e45e764412dd45688bea028f351333e86d9769704`. Native, generic-core and embedded-profile-only reads all exited 0. No stderr diagnostic was emitted. Input hashes were checked against the fixed expected values before execution and remained unchanged after the checks.

The native file has explicit `millimeter` units, one resource mesh object, one build instance and eight inclusive volume ranges covering all 35,304 triangles exactly once. The actual native roundtrip also has one object, one build instance and eight volumes. Its SHA256 is `57ab6a537dc3edaec87f4cd408db3de36372af8f38e1823b0267e01047365965`.

Source world bounds are `[-75,-74,0]` to `[75,74,57.099998474121094] mm`, giving a `150 x 148 x 57.099998474121094 mm` envelope. The exported world bounds differ only in the final z serialization: `57.0999985 mm`. Per-volume triangle counts and corresponding vertex slots were retained. The largest measured corresponding-coordinate change is `7.625879e-6 mm`; this is quantified float precision change, not exact real-number equality. Rounded-coordinate hashes can differ when a coordinate crosses a rounding-bin boundary.

| Editable part | Tool before/after | Triangles before/after | All unique edges incidence 2 after actual export | Exact zero-area faces after export |
|---|---:|---:|---|---:|
| light_frames | 1 / 1 | 1,376 / 1,376 | yes | 0 |
| glass | 4 / 4 | 5,192 / 5,192 | yes | 0 |
| pv | 3 / 3 | 2,520 / 2,520 | yes | 2 |
| roof | 3 / 3 | 2,260 / 2,260 | yes | 2 |
| dark_facade | 3 / 3 | 5,188 / 5,188 | yes | 0 |
| plinth | 3 / 3 | 228 / 228 | yes | 0 |
| brick | 2 / 2 | 5,600 / 5,600 | yes | 0 |
| wall | 1 / 1 | 12,940 / 12,940 | yes | 0 |

All eight parts retain positive signed volume, consistent winding and exact-coordinate-merge watertight flags. Source f64 parts have no exact zero-area faces. No triangle-count change or repair warning occurred. Those observations do not erase the four degenerate faces found independently. The whole multicolor triangle soup includes internal material interfaces and is not a boolean-unioned exterior-manifold test. Prusa's overall `manifold=yes` and `number_of_parts=630` are not substitutes for the per-volume results; the latter statistic concerns mesh components rather than eight editable volumes.

## Four retained flags: paired material interfaces

Independent coordinate matching locates PV triangles 2216/2350 and roof triangles 1800/1980 (zero-based indices). In the f64 source, each PV triangle and its roof counterpart have exactly the same three vertices, opposite normals (`cos=-1`) and tool 3 on both sides. Each flagged source triangle has doubled area `2.41074167489e-6 mm²`, or actual area `1.20537083745e-6 mm²`. The smaller `2.0314e-9 mm²` figure is a minimum elsewhere in each complete source part, not the doubled area of these four flags.

The two source sets lie at z `48.02 mm`, near x `-57.17022286` and `47.82977714 mm`, spanning y `36.32500076` to `43.14 mm`. The actual Prusa export collapses the triangles to these lines:

| Pair | Shared x after export (mm) | Three y coordinates after export (mm) | PV z / roof z (mm) |
|---|---:|---|---|
| PV 2216 / roof 1800 | -57.1702232 | 36.3250008, 42.5433426, 43.1399994 | 48.0199966 / 48.0200005 |
| PV 2350 / roof 1980 | 47.8297768 | 36.3250008, 42.5433426, 43.1399994 | 48.0199966 / 48.0200005 |

Thus all four exported areas are exactly zero; the two exported material sides differ by `3.9e-6 mm` in z. These flags originate as paired opposing PV/roof material-interface triangles, not unpaired exterior-hole facets or a measurement of physical wall thickness. This supports retaining the candidate with a disclosed precision/interface limitation. It does not prove a slicer or machine will resolve every interface correctly. Blind deletion is not a demonstrated repair: removing these zero-area faces alone in memory opens boundaries. If a later slicer rejects them or produces a real void, the minimum next step is to retessellate the local same-tool interface or use the provided merged tool-3 group after independent checking, preserving the exterior. This review did not create a repair or retest those merged STLs.

Full source and exported flag coordinates, pairing tests and edge-incidence counts are in `independent-interface-probe.json` and `PUBLIC-R2-SUMMARY.json`.

## Profile loading and generic compatibility

Both an explicit reference-INI load and an independent native-project-only read with no `--load` produced four nozzle entries, four zero offsets, the four agreed colors and `single_extruder_multi_material=0`. This establishes that the embedded profile is actually parsed. The reference 0.4 mm diameters and zero offsets are placeholders, not the unknown physical printer's calibration. Support and interface are assigned to existing tool 1. Four main colors plus a separate support material would require five tools; within four physical tools, a dedicated support material leaves at most three main color groups.

The generic core file has eight child meshes and one components parent (nine resource objects, one build item). Actual Prusa import/export converted it to eight separate objects/build items with no explicit per-part extruder overrides. World-space geometry remains assembled through transforms, but this is not the native one-object/eight-parts editing structure. Use `a1-four-tool-prusaslicer.3mf` for the verified four-tool mapping. Display colors and core material properties do not guarantee an extruder mapping in other slicers.

The CLI model export deliberately omits the full `Metadata/Slic3r_PE.config`, consistent with the official 2.9.6 `store_3mf(..., nullptr, ...)` action. Preserve the fixed native project; treat `roundtrip.3mf` as geometry/model-metadata evidence and `effective.ini` as a separate effective-settings record. [Official PrusaSlicer 2.9.6 export action](https://github.com/prusa3d/PrusaSlicer/blob/version_2.9.6/src/CLI/ProcessActions.cpp#L141).

## Reproduction commands and limits

The following normalizes output paths for a public reproduction from the building package directory. Create the separate empty output directories first. Use the independently identified 2.9.6 console installation; these are not claims that an executable is bundled in the package.

```text
prusa-slicer-console.exe --datadir qa/prusa-r2/native/cli-data --config-compatibility disable --load multicolor/generic-four-tool-REFERENCE.ini --dont-arrange --no-ensure-on-bed --info --save qa/prusa-r2/native/effective.ini --export-3mf --output qa/prusa-r2/native/roundtrip.3mf multicolor/a1-four-tool-prusaslicer.3mf
```

To test only embedded settings, omit `--load` and export, and save settings to a separate location:

```text
prusa-slicer-console.exe --datadir qa/prusa-r2/embedded-only/cli-data --config-compatibility disable --dont-arrange --no-ensure-on-bed --info --save qa/prusa-r2/embedded-only/effective.ini multicolor/a1-four-tool-prusaslicer.3mf
```

The generic-core check used the first command shape with `a1-four-tool-core.3mf` as input and a separate `qa/prusa-r2/core` output directory. Independent inspection parsed ZIP/XML, reconstructed world-space transforms, verified inclusive ranges and tool values, and measured exact zero-area faces and edge multiplicity before and after actual export.

No `--slice` or G-code action was executed. No GUI check, machine-specific four-head configuration, physical print, color registration, bonding, purge/tool-change behavior or support-removal trial was performed. These remain manufacturing conditions, rather than reasons to silently call the candidate fully print validated or to redesign the whole building.
