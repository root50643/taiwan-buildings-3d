# Logical-layout restore and optional low-disk experiment

## Self-contained public restore

The main public entry remains the unchanged `qa/restore_scientific_layout.py`, together with the unchanged `qa/roster_primitives.py` and public `qa/PUBLIC-COPY-MAP.json`. With sufficient ordinary free disk space, it verifies canonical public bytes and writes the full declared logical layout to a fresh directory. It does not need any private receipt or original private location.

```sh
python -B PUBLIC_ROOT/qa/restore_scientific_layout.py \
  --public-root PUBLIC_ROOT --out NEW_LOGICAL_DIRECTORY
```

That command requires enough space for every logical payload plus filesystem overhead. It does not decode archives, reconstruct omitted private sources, upgrade projected public metadata, or rerun geometry or rendering.

## Optional low-disk experiment

`restore_low_disk.py` and `replay_public_restore.py` are a narrowly scoped experiment for the current disk-constrained QA run. They require an already verified official historical archive and its original private verification receipt. The receipt is authenticated in full against SHA-256 `005f25a70aceab80f36061e8b18930150d20a09807fccf99f8c75e15083da2fb`; the private receipt and physical source paths are not published. These optional tools are not independently replayable from the public package alone when that private receipt is unavailable. Use the original main public entry above instead.

The optional experiment:

1. Validates the full final map with the unchanged original validator and authenticates every canonical file with the unchanged original exact reader before restoring any logical payload.
2. Removes exactly one fixed archive alias from an in-memory sub-map. Retained descriptors remain unchanged, and the source map file is never edited.
3. Uses the original restore function to newly write every other logical file to a fresh directory.
4. Adds one regular hardlink for canonical `qa/controls-history/controls.tar.xz`, at logical `history/qa/controls/controls.tar.xz`: exactly 59,649,412 bytes, SHA-256 `e5c4465705d5e5299c5d9aa7fa7e99f5db44a61437990508ecee72d615e165b9`.
5. Checks the complete logical file/directory set, regular-file types, sizes and every SHA-256, including that hardlink. Every canonical source is authenticated again afterward.

This is newly written data plus one authenticated hardlink. It is not a wholly newly allocated copy. The archive must be on the same filesystem as the destination. A cross-filesystem link fails rather than silently copying. Creating/removing the hardlink necessarily changes source link count and ctime; the tool never applies chmod or utime to that archive, and verifies its mode, size, mtime and bytes around linking.

Every ancestor is opened FD-relative with `O_DIRECTORY|O_NOFOLLOW`; every leaf is opened with `O_NONBLOCK|O_NOFOLLOW` and required to be regular. Source and destination parent FDs are retained across `linkat`-equivalent `os.link`, with nofollow and exclusive destination creation. Post-link checks require the original inode, bytes and path ancestry. Existing destinations, symlinks, FIFOs, source replacement and ancestor drift fail closed.

The replay runs normal Python and genuine `-O` sequentially using the exact original capture tool's `BOOT` text. Private runtime captures retain the actual optimization level, CPU affinity, executable, target SHA and argv. Public summaries contain logical paths and hashes, not private receipt `restored_root` values or physical source paths. Each mode's complete logical roster is independently rechecked by the replay parent. Only a successful, fully reauthenticated derived tree created by that run is removed before the next mode. Failed derived trees are retained for diagnosis.

Allocation is estimated by filesystem allocation-unit rounding for every new payload, directory overhead, and a 2 MiB margin. Each phase measures actual available bytes and enforces at least 128 MiB remaining; both modes use the shared external heavy-work lock and one CPU. This does not reserve space against unrelated processes, so the actual checks remain mandatory.

## Current review status

The reviewed final map is pinned at SHA-256 `88c242807a32719dd3d77d2bfffb04e5cbefd48ee2d4c29ff24ba58d02e0c486`, with 550 canonical files and 1,269 logical files. The optional replay would newly write 1,268 logical files totaling 63,789,790 payload bytes, plus the single 59,649,412-byte archive hardlink. No actual public restore has been run by this preparation step. The initial unpinned source bytes and exact final-pin diffs are retained separately.

`test_low_disk.py` exercises only the newly introduced edges with tiny synthetic data. Its 25 controls passed under both normal Python and genuine `-O`, with captured CPU affinity `[0]`. Coverage includes exact regular hardlinks, wrong hash/size, source symlink/FIFO, source/destination ancestor symlinks, destination existence, unsafe destination permissions, source-leaf replacement at link, source/destination ancestor drift at link, fixed-archive partition identity, a tiny original-restorer-plus-link integration, exact fileset/corruption rejection and the projected 128 MiB floor. The archive descriptor partition tests use metadata only. This is not a replacement for actual final-package replay or for the already tested original generic helper suite.

The final pin change was checked by seven additional identity controls in each genuine runtime mode: exact map and archive alias acceptance, changed map bytes, wrong SHA/counts, unpinned identity, and replay target-source binding. The unchanged 25 hardlink/partition/roster edge controls were not repeated for this pin-only change. Actual replay remains pending the final public root and explicit authorization. Do not alter either original safe tool. Retain full per-mode runtime captures privately and publish only privacy-reviewed summaries.
