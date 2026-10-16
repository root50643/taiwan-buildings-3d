# Complete control evidence, compact storage

`controls.tar.xz` contains all 2,348 control files from the completed independent QA, at their original logical relative paths. This includes every original positive/negative fixture, expected failure, normal/`-O` result and required baseline. Its 7,387,987 member bytes are unchanged. No scientific result was removed or repaired. Six deliberately malformed nested gzip/XZ fixtures remain malformed; the archive validator checks their stored bytes, not whether those negative inputs decode.

`packaging-controls.tar.xz` separately preserves the new archive validator's complete synthetic fixture/result files. Its layout record documents the relative symlinks and directory permissions used by the safety tests; it does not install those symlinks. Re-running the test source recreates them in fresh scratch directories. Both archive formats permit only regular files.

`controls-index.json` and `packaging-controls-index.json` bind every member's relative name, size and SHA-256, plus the compressed archive and decoded TAR hashes. Trust these indices through the package's outer integrity manifest. Matching a replaced archive and replaced index does not establish authorship.

The main `FILES-SHA256.json` lists only actually distributed outer files, excluding itself. The original `PUBLICATION-BINDING.json` is preserved byte-for-byte: its paths describe the complete logical evidence tree. Paths under `audit/`, `predicate-review/`, `tooling-patched/`, `final-controls-v17/`, and each mode's `standard/controls/` or `intersection-controls/` now resolve inside `controls.tar.xz`. Other evidence paths remain direct. `PACKAGING-RESULT.json` binds this storage change to the previous inventory. Scientific model CSV/JSON and both modes remain direct and unchanged.

## Validate and inspect

Run sequentially from `qa/` using Python 3.12. All output directories must be new; their existing parent must belong to the current user and must not be group/other writable. Do not concurrently modify the destination tree under the same user account.

```sh
python -B packaging/archive_verify.py --archive controls.tar.xz --index controls-index.json
python -B -O packaging/archive_verify.py --archive controls.tar.xz --index controls-index.json
python -B packaging/archive_verify.py --archive controls.tar.xz --index controls-index.json --out unpacked-controls
python -B packaging/archive_verify.py --archive packaging-controls.tar.xz --index packaging-controls-index.json --out unpacked-packaging-controls
```

Without `--out`, verification is read-only. Every compressed and decoded byte, TAR header/checksum, member name/size/hash and complete membership is validated before any extraction begins. The fixed profile is USTAR, sorted regular files, mode 0644, uid/gid/mtime zero, empty owner names, XZ CRC64, no links or extended headers. The parser rejects unsafe/duplicate/prefix-colliding names, unexpected members, missing content, nonzero TAR padding, trailing XZ data/streams and decompression beyond 512 MiB. Extraction uses fresh-directory creation and POSIX fd-relative `O_NOFOLLOW`/`O_EXCL` writes; existing outputs are rejected. Decoder memory has its own bounded ceiling. A disk or permission error after validation can leave a partial new output directory; retain it for diagnosis and choose a different new directory for a retry.

## Rebuild the identical control archive

```sh
python -B packaging/build_controls_archive.py --root unpacked-controls --index controls-index.json --out rebuilt-controls.tar.xz
```

The builder accepts only indexed, unchanged regular files and refuses an existing output. It fixes all TAR metadata and uses Python's single-threaded XZ preset 6/CRC64. The completed run built this archive twice independently and rebuilt it from the safely extracted files; all archive bytes matched. Different compression-library versions may change XZ bytes; such a mismatch fails rather than silently accepting a new container.

## Replay controls without overwriting observed results

The full extraction above is for reading the retained observations. Many original test scripts intentionally refuse a pre-existing output, and some write results next to their source. Prepare a separate workspace containing unchanged scripts, helper sources and the required positive baselines, excluding prior output directories:

```sh
python -B packaging/prepare_control_replay.py --qa . --out fresh-control-replay
cd fresh-control-replay
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export BWBC_VERIFICATION_DIR="$PWD/verification"
unset PYTHONOPTIMIZE
python -B audit/test_current_aggregate.py --out aggregate-normal
python -B -O audit/test_current_aggregate.py --out aggregate-optimized
python -B audit/test_exact_ray_diagnosis.py exact-predicates-normal.json
python -B -O audit/test_exact_ray_diagnosis.py exact-predicates-optimized.json
python -B audit/test_original_hex_box.py original-hex-normal.json
python -B -O audit/test_original_hex_box.py original-hex-optimized.json
python -B predicate-review/review_recorded_wrapper_final_tests.py
python -B -O predicate-review/review_recorded_wrapper_final_tests.py
python -B predicate-review/review_wrapper_final_exit_semantics.py
python -B -O predicate-review/review_wrapper_final_exit_semantics.py
python -B predicate-review/review_boundary_and_fix_tests.py
python -B -O predicate-review/review_boundary_and_fix_tests.py
python -B predicate-review/review_png_compare_public.py --module independent-tools/png_exact_compare.py --out png-compare-normal
python -B -O predicate-review/review_png_compare_public.py --module independent-tools/png_exact_compare.py --out png-compare-optimized
python -B predicate-review/review_png_sanitize_tests.py --module independent-tools/sanitize_png_previews.py --out png-sanitize-normal
python -B -O predicate-review/review_png_sanitize_tests.py --module independent-tools/sanitize_png_previews.py --out png-sanitize-optimized
python -B predicate-review/review_postflight_track_tests.py --source independent-tools/postflight_acceptance.py --out postflight-normal
python -B -O predicate-review/review_postflight_track_tests.py --source independent-tools/postflight_acceptance.py --out postflight-optimized
```

The original numerical-geometry control matrices can be rerun separately with `verification/check_controls.py --out NEW_CONTROLS` and `verification/check_intersection_controls.py --out-dir NEW_INTERSECTION_CONTROLS`, and again under `-O`. They compute synthetic geometry, so these are distinct from the packaging replay. See `REPRODUCE.md` for the actual-model checks.

Re-run the new packaging negative controls from `qa/`:

```sh
python -B packaging/test_archive_verify.py --out new-archive-tests-normal
python -B -O packaging/test_archive_verify.py --out new-archive-tests-optimized
```

All 65 cases per mode must pass their expected accept/reject outcomes, including missing/member replacement, corrupt XZ with updated container hash, TAR/header/profile errors, unsafe names/links, existing output and symlink destinations, untrusted writable output parent, and reduced-limit decompression. No optimization-dependent `assert` is used as a security gate. Full input/result evidence and both completed mode summaries are retained.

The replay-preparation helper has an additional seven controls per mode, covering late archive/index substitution, missing/changed helper inputs, changed archive input and existing output. Both modes passed; combined archive/replay-entry safety controls total 144. Replay them with:

```sh
python -B packaging/test_prepare_replay.py --out new-replay-tests-normal
python -B -O packaging/test_prepare_replay.py --out new-replay-tests-optimized
```

The real archive was also safely extracted, then rebuilt bitwise under normal and `-O`; both fresh prepared workspaces successfully ran the unchanged 21-case aggregate packaging suite. No model geometry or render was recomputed for this storage change.
