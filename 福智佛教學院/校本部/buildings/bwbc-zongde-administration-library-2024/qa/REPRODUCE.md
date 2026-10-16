# Reproduction and integrity

The supplied scientific reports are unchanged producer outputs. Full numeric CSVs use lossless XZ; detail/flag/intersection records use gzip. Each dense report binds both compressed and decoded CSV SHA-256. Do not treat an XZ filename as an uncompressed CSV or use only the compressed hash.

Tested environment: Python 3.12.14, g++ 14.2, Blender 4.3.2; numpy 2.3.5, manifold3d 3.5.4, trimesh 5.1.1, shapely 2.2.0. Blender used CPU Cycles, one thread, 64 samples, seed 0, animated seed disabled, no denoising, exposure 0.35. Different renderer/library versions are not promised to reproduce identical pixels.

All outputs below must be **new directories**. Keep existing evidence unchanged. Run commands sequentially, with:

```sh
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
unset PYTHONOPTIMIZE
```

Use the package's original `model.stl`, source/parameter files and `scene.blend`. The STL expected SHA-256 is:

```text
96481addb2b9ac4144cb5f012f19b57e047106021e93adb5c34df2c00770e1a3
```

## Original STL gates and exact supplement

From this QA directory, select your Python executable and absolute or relative input/output paths:

```sh
python -B verification/run_qa.py --stl MODEL_STL --out NEW_NORMAL --expected-longest-mm 210
python -B -O verification/run_qa.py --stl MODEL_STL --out NEW_OPTIMIZED --expected-longest-mm 210
```

For this exact frozen STL these aggregate commands deliberately return **1**, retaining the 12 numerical flags and original strict=false. Do not mask arbitrary errors with `|| true`. Verify that raw, sections and controls explicitly pass, that all expected keys/source hashes/artifact hashes are present, and that dense has only its documented interval/control failure, 373,300 samples and zero short rays. An exception, missing report, changed count or other failure is not the expected outcome.

For each mode, with `-O` added for the optimized mode:

```sh
python -B verification/check_original_intersections.py --stl MODEL_STL --expected-sha256 STL_SHA --out NEW_INTERSECTIONS.json --progress
python -B verification/check_intersection_controls.py --out-dir NEW_INTERSECTION_CONTROLS
python -B independent-tools/diagnose_recorded_cpp_rays.py --stl MODEL_STL --flags NEW_NORMAL/dense/dense-flagged-samples.json.gz --dense-report NEW_NORMAL/dense/dense-check.json --raw-report NEW_NORMAL/raw/raw-mesh-check.json --intersections-report NEW_INTERSECTIONS.json --expected-sha256 STL_SHA --out NEW_EXACT_RAYS
```

`STL_SHA` means the literal hash above. All three commands must return zero. The exact supplement requires the complete CSV and exact descriptors emitted by the original C++ execution; ideal/recreated rays or rounded decimal values cannot substitute. Its original numeric strict result remains false. Inspect complete selection, row coverage and exact chord fields, not just process exit.

Decode/verify a dense CSV without altering its source:

```python
import hashlib, json, lzma
from pathlib import Path
base = Path('resume-v17/geometry/normal/standard/dense')
r = json.loads((base/'dense-check.json').read_text())
p = base/r['csv_file']
if hashlib.sha256(p.read_bytes()).hexdigest() != r['csv_compressed_sha256']:
    raise RuntimeError('Compressed CSV mismatch')
with lzma.open(p, 'rb') as f:
    if hashlib.file_digest(f, 'sha256').hexdigest() != r['uncompressed_csv_sha256']:
        raise RuntimeError('Decoded CSV mismatch')
```

For text inspection, `xz -dc dense-original.csv.xz` or `gzip -dc FILE.json.gz` reproduces all original bytes. Avoid overwriting the compressed originals.

## Source, Blend and public PNGs

The main model package documents its source build command and matching directory layout. The independent run executed the frozen build source and compared rebuilt STL/color-region file bytes. The saved Blend was additionally compared against the actual source-created scene state by `independent-tools/compare_source_scene.py`; only the unchanged scene-construction prefix was executed, with the exact source-line/AST boundary recorded in the source-scene audit. It did not duplicate the eleven source renders.

To inspect and rerender the saved Blend, use its 11-camera manifest and the matching PNG directory:

```sh
blender --background --threads 1 --python-exit-code 1 --python independent-tools/inspect_and_rerender_blend.py -- --blend SCENE_BLEND --stl MODEL_STL --manifest PUBLIC_PREVIEW_DIR/render-manifest.json --expected-sha256 STL_SHA --out NEW_RERENDERS
```

The public preview manifest binds already-cleaned images. Using it produces a new reproduction report tied to the public images; it is not the original private raw-image audit. The inspector applies the same whitelist cleanup to both sides and requires exact RGBA/presentation-metadata agreement. The retained raw private audit additionally binds the original uncleaned PNG hashes. All eleven cleaned files actually matched bitwise in the completed independent run, while raw PNG files did not.

The cleanup CLI can be replayed on a fresh raw-image manifest and matching raw PNGs:

```sh
python -B independent-tools/sanitize_png_previews.py --manifest RAW_PREVIEW_DIR/render-manifest.json --expected-manifest-sha256 RAW_MANIFEST_SHA --expected-stl-sha256 STL_SHA --out NEW_PUBLIC_PREVIEWS
```

It only copies retained PNG chunks and removes the explicit tEXt whitelist; no image recompression occurs. Do not rewrite the frozen original raw manifest to point at cleaned bytes.

## Small controls

First read `CONTROLS.md`. The complete observed control subtrees are stored in `controls.tar.xz`, with a per-member SHA index. Verify and extract the archive into a new directory; prepare a separate fresh replay workspace before running scripts that write next to their source. The published model science files remain directly available.

Each control output is retained with per-case input/result evidence. Run the scripts against fresh output paths. The public PNG comparison harness is `predicate-review/review_png_compare_public.py`; its 242 outcomes per mode are identical to the original reviewed cases, while its report identifies the module by basename rather than an execution-machine path.

For aggregate packaging controls, set `BWBC_VERIFICATION_DIR` to this directory's `verification/`. `audit/test_current_aggregate.py` explicitly injects already-computed genuine positive-fixture reports to test packaging behavior; it does not claim another physical-geometry run. Its negative cases cover exceptions, stale/no reports, missing flags, wrong source/input hashes, and compressed plus decoded hash failures.

The recovery/postflight scripts retain their original private-layout expectations as forensic replay sources. For a public-only replay, use the component commands above; private raw PNGs and the interrupted historical run are intentionally not required for geometry or cleaned-image reproduction.
