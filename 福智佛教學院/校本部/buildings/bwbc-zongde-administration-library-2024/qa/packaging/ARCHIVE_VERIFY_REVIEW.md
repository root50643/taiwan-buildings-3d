# Controls archive validator and small controls

## Entrypoints

Read-only verification:

```sh
python archive_verify.py --archive controls.tar.xz --index controls-index.json
```

Verification followed by extraction:

```sh
python archive_verify.py --archive controls.tar.xz --index controls-index.json --out fresh-controls
```

The index has exactly these keys:

```json
{"format":"bwbc-controls-ustar-xz-v1","archive_sha256":"64 lowercase hex digits","tar_sha256":"64 lowercase hex digits","members":[{"path":"relative/path","bytes":123,"sha256":"64 lowercase hex digits"}]}
```

Members must be nonempty, unique, sorted by path, and free from file/directory prefix collisions. Tar order must equal index order. Paths are UTF-8 POSIX-relative paths; absolute, drive-prefixed, backslash, empty, dot, dot-dot, and control-character components are rejected.

The validator checks the full compressed SHA256, exactly one complete XZ stream with no following bytes, the full decompressed tar SHA256, unsigned header checksums, POSIX USTAR magic/version, and every indexed member's name, byte count, and SHA256. Only typeflag `0` ordinary files are allowed. Metadata requires mode 0644, uid/gid/mtime zero, empty uname/gname/linkname, and zero device/reserved fields. Member padding must be zero. At least two zero tar terminator blocks are required; the remaining tail must be zero and the complete tar block-aligned. PAX, links, directories, missing/extra/duplicate members, nonzero tails, and concatenated XZ streams fail. Inner fixture contents, including intentionally invalid `.gz`/`.xz` files, are opaque bytes and are never decoded.

The decompressed tar ceiling is 512 MiB. The XZ decoder also has a separate 512 MiB memory ceiling. All acceptance checks are explicit and remain active with Python `-O`.

No output directory is created until verification succeeds. Extraction requires Linux/POSIX fd-relative operations, an existing parent owned by the current user and not group/other writable, and a completely new final directory. Every traversal uses `O_DIRECTORY|O_NOFOLLOW`; every file uses `O_CREAT|O_EXCL|O_NOFOLLOW`. Files are mode 0644 and mtime zero. Directories are private mode 0700. Archive uid/gid are validated but extraction does not change operating-system ownership. A partial directory from an I/O failure is retained for inspection and will be refused on retry.

The current user must not concurrently mutate the destination tree or its ancestry. The index must be trusted independently. These hashes establish integrity against that index, not authorship or protection against simultaneous replacement of the archive and its trusted index.

## Import API

- `verify(archive, index_path)` is read-only and returns `(result, tar_bytearray, records)` after full validation. Each record is `(path, start, end)` into the validated tar bytes. The result includes actual archive, tar, and index SHA256 values.
- `extract_new(out, payload, records)` extracts supplied records safely; it does not authenticate arbitrary caller-supplied bytes or revalidate a tar. The caller must first verify all source material and construct trusted records. The CLI enforces this order automatically.
- When another program first checks the archive/index against a package manifest and then calls `verify`, it must compare `result['archive_sha256']` and `result['index_sha256']` with the manifest-approved hashes. This binds the bytes actually consumed by verification and closes a second-read replacement window.

## Reproducible synthetic controls

```sh
PYTHONDONTWRITEBYTECODE=1 python test_archive_verify.py --out controls-normal
PYTHONDONTWRITEBYTECODE=1 python -O test_archive_verify.py --out controls-optimized
```

Both output directories must be new. Observed results: **65 cases in each mode, 130 successful checks total**, including positive read-only validation/extraction, corruption and truncation, archive/tar/member hash mismatch, missing/extra/replaced/duplicate members, wrong ordering, duplicate JSON keys, traversal and drive paths, prefix collisions, all required fixed metadata, forbidden link/PAX types, tar padding/termination, existing output and symlink refusal, unsafe output-parent refusal, and a reduced-ceiling streaming decompression limit control. The last test uses a tiny output ceiling rather than allocating a 512 MiB fixture.

Validator SHA256: `428fcd7e70d936eb831b9ad455da4eb5ea523bac57ee4a50fabe552f02441c4a`.

Public evidence comprises the validator, control script, this explanation, and all ordinary fixture/result files from both complete final control directories inside `packaging-controls.tar.xz`. Unnecessary stdout logs remain private. Symlink controls should be represented in any ordinary-file-only evidence archive by their exact relative link/layout descriptions, with the executable control script retaining the reconstruction procedure. Expected rejection reports are successful negative-control evidence and must remain present. Earlier harness-development attempts named `private-initial-*` are excluded from the public final-control evidence.

The reviewer ran only these tiny synthetic controls. Validation and extraction of the real controls archive are separate operations owned by the release assembler and are not claimed by this report.

## Builder and replay-entry review

Static review of `build_controls_archive.py` at SHA256 `684adb9307abe50c9f9ce3f8ba68669dc9a276bb31432b9a6ddb4d7f7b526e13` found no remaining blocker within the frozen-source workflow. It reads only regular, non-symlink source members, checks each source byte count and SHA256, writes fixed USTAR metadata in indexed order, requires both regenerated tar and XZ hashes to equal the index, and creates its output exclusively. Its explicit comparisons are active under `-O`. Exact compressed reproduction can depend on the compression implementation; a differing compressed hash causes rejection even if uncompressed content matches.

Static review of `prepare_control_replay.py` at SHA256 `f79ad7652d1c889e549a6b99337f8f76097d89bf606a15291db509bb4beb69fd` identified and then verified correction of a second-read integrity window: the actual archive/index hashes returned by `verify` now must match the package-manifest-approved hashes before extraction. Fourteen required helpers must appear in the manifest. Every selected direct helper is checked against its manifest byte count/SHA256, and collisions are rejected. The program validates the entire original archive, selects scripts and the declared positive-baseline trees, adds checked helpers, and builds a new replay directory through `extract_new`; previous observed-run directories remain in the original archive.

`test_prepare_replay.py` adds **7 tiny cases in each mode, 14 successful checks total**: a successful fresh replay; mocked late archive substitution; mocked late index substitution; missing helper; helper-content mismatch; direct archive-content mismatch; and refusal of an existing output directory. The two late-substitution cases deliberately mock the verification result's actual-input hash rather than attempting a timing-dependent filesystem race. Both are rejected before any extraction call. The positive case also checks selected membership, absence of the old observed-result directory, and exact helper bytes. The existing-directory case preserves its sentinel unchanged.

```sh
PYTHONDONTWRITEBYTECODE=1 python test_prepare_replay.py --out replay-controls-normal
PYTHONDONTWRITEBYTECODE=1 python -O test_prepare_replay.py --out replay-controls-optimized
```

This control script is distributed directly. All ordinary fixture/result files from both complete `replay-controls-*` directories are preserved inside `packaging-controls.tar.xz`, with relative layout descriptions for non-file safety scenarios. Unnecessary stdout logs remain private. All final control reports were checked to contain no private workspace/home/temp absolute paths. Combined archive-validator and replay-entry controls total **144 successful checks**. No real model, Blender, or real controls-archive computation was performed by this reviewer.
