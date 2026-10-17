# WFU original-coordinate lattice correction

The prior candidate accidentally retained AEUST's 2^30 lattice. This overlay
changes only the helper's fixed LATTICE and expected intersection power to 2^56.
Generic arithmetic, validation gates, thresholds and original strict=False stay
unchanged. The original candidate, author helper/test, frozen 53-input set and
failed review remain intact. Original bytes and complete diffs are in provenance.

## Source and evidence identities

provenance/ADAPTATION.json binds all six current Python sources, the four source
originals/diffs, unchanged author/frozen helper and test, preserved failure, and
completed controls/proof evidence. provenance/SOURCE-BINDINGS.json binds the four
adapted files. INITIAL-SOURCE-BINDINGS.json is a retained provisional snapshot;
use ADAPTATION.json and SOURCE-BINDINGS.json for final identities.

The tests retain 13 methods and 69 original subtests and add 10 lattice rejection
subtests (old 2^30, wrong power and falsely typed values). Fixtures use power56
and half-lattice origin 0x1p-57. The launcher requires all 13 methods/79 subtests.

The independent stdlib proof decodes all 188514 original float32 vertex
coordinates from the SHA-bound binary STL, computes their reduced-denominator
LCM using as_integer_ratio(), and checks exact Fraction and binary32 byte
round trips. It imports neither producer reports nor the candidate parser.
The completed proof found LCM=72057594037927936 (2^56), with a minimality witness
77/72057594037927936 at face9170, vertex1, x (byte458608). Exactly 121 original
coordinate values are not representable on the old 2^30 lattice.

## Completed controls

The parent executed the serial driver under the shared single-CPU QA lock.
Output root: wfu-shengyou-independent-qa/lattice56-controls-v1

- controls-summary.json and executions.json
- parser-normal/{results.json,unittest.log}
- parser-optimized/{results.json,unittest.log}
- coordinate-proof-normal.json and coordinate-proof-optimized.json
- parser-normal, parser-optimized, coordinate-proof-normal and
  coordinate-proof-optimized each have .stdout.log and .stderr.log

All four stages exited zero. Each parser mode passed 13 methods/79 subtests.
The two coordinate proofs match except for actual optimization level.
controls-summary.json SHA256:
e426308df08de89b34d8c20c2301cdafd105593c030591f560d500ed41224807

The driver takes --stl <exact original STL> --out <fresh directory>. It requires
one-CPU affinity and caller ownership of the shared QA lock, removes inherited
PYTHONOPTIMIZE, runs explicit normal/-O children, and authenticates all six
sources before/after. Do not reuse the completed output path.

## Fresh full-artifact review

review_artifact_structure.py compiles the authenticated sibling helper bytes.
External helper identity is recorded in postflight_overlay_inputs; scientific
inputs remain in the existing run-relative evidence_inventory. Both are
rehashed before success. The parent uses run_postflight_lattice56_v13.py with
fresh r3 outputs; prior case/complete sources remain candidate-tools-v12.

This is a case-constant correction and evidence preparation. Controls/proof do
not themselves establish model acceptance or science freeze. Fresh postflight,
source binding, privacy and packaging still require their own completed checks.
