# Public result-binding checker, v10

This is a narrow public variant of the hash-bound private checker and its existing
test suite. It reads original evidence without editing it, rebuilding geometry,
rendering images, creating canonical CSV copies, or changing any scientific gate.

The only input-interface change replaces the fixed private source-directory prefix
with the required `--source-path-prefix` argument. The supplied prefix must be a
canonical relative directory prefix ending in a slash. Missing, absolute, traversal,
backslash, drive, whitespace and noncanonical prefixes are rejected. The true value
is not embedded, encoded or disclosed in public source or output metadata.

## Reproduction recipe

Use the already-selected Python environment and the same shared exclusive lock and
CPU0 used for the original independent run. The independent run must have finished.
The operator supplies private paths and the exact source prefix from the original
hash-bound source-binding file. Do not publish those CLI arguments or raw logs.

    export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
    unset PYTHONOPTIMIZE
    exec 9>"$SHARED_LOCK"
    flock 9
    taskset -c 0 "$PYTHON" -B "$CHECKER_ROOT/test_result_binding.py" --out "$CHECKER_ROOT/controls-normal.json"
    taskset -c 0 "$PYTHON" -B -O "$CHECKER_ROOT/test_result_binding.py" --out "$CHECKER_ROOT/controls-optimized.json"
    taskset -c 0 "$PYTHON" -B "$CHECKER_ROOT/check_result_binding.py" --author-root "$AUTHOR_ROOT" --run-root "$RUN_ROOT" --source-path-prefix "$SOURCE_PATH_PREFIX" --out "$CHECKER_ROOT/binding-normal.json"
    taskset -c 0 "$PYTHON" -B -O "$CHECKER_ROOT/check_result_binding.py" --author-root "$AUTHOR_ROOT" --run-root "$RUN_ROOT" --source-path-prefix "$SOURCE_PATH_PREFIX" --out "$CHECKER_ROOT/binding-optimized.json"

All output paths must be new. Run the binding commands only after both control
commands pass. Capture exact command arguments, actual Python optimization level,
CPU affinity, source hashes, return codes, stdout/stderr and result hashes privately.
The private helper used for the recorded executions is separately hash-bound;
these direct CLIs are sufficient to reproduce the public checking work.

## Exact boundaries

`AST-EQUIVALENCE.json` proves all 21 other original checker functions constant-fold
AST-identical, including source_schema, every scientific comparison and SHA gate.
The original source_relative body is unchanged after one configuration guard. The
original main body is unchanged after exactly three CLI configuration statements
and one explicitly declared metadata field are projected away. No scientific field
is removed by that projection.

Three generic private-root detector literals and one synthetic negative-control
literal use visibly readable string concatenation. Their exact original and new AST
locations, source-line hashes and equal constant-folded values are recorded. This is
not a whole-file scanner exception. The true private source prefix is never split
or encoded into the public files; it is supplied solely by the caller.

The first 65 control intents and code paths are preserved. Synthetic source fixtures
use `fixture-author/`; the existing prefix-impersonation test derives its wrong prefix
from that fixture. Sixteen added prefix controls bring the total to 81 per mode.

## Provenance and diff presentation

`ADAPTATION-PROVENANCE.json` records full original private code and exact raw-diff
SHA-256 values. Original code, raw diffs, old controls and old freezes remain intact.
The two public diff files are explicitly labelled display projections, not raw-byte
diffs. Only the original private-prefix literals are redacted, with exact literal and
line hashes. Generic detector and synthetic literals on original diff lines use the
same readable exact-equivalent display form, with AST-location proof.

New binding results must equal the corresponding original typed JSON after removing
only the checker identity metadata and the newly declared prefix-policy metadata.
Normal and optimized new results must differ only in their reported optimization
level. The comparison proof lists exact JSON pointers and retains all other typed
values. Logical author/run/checker references and hashes identify evidence without
copying private source-review content into public reports.

A passing binding confirms evidence identity and coverage. Original strict=false,
producer/standard exit1 and source-appearance limitations remain. It grants no
manufacturing, physical-print, privacy, licensing or publication approval.
