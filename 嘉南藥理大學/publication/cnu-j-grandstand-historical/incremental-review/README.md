# Fixed-candidate incremental review evidence

This directory preserves the independent incremental review of fixed candidate
`7cf0563a06858137f51751600348a35198c8f6f2` against base
`1976d60d5e1621dac2ce6a5d904e74796c38be0e`. Its **GO remains conditional on the
fixed STL and manufacturing limitations in the original report**. It does not
claim that a later publication commit or index changes received the same review.

Start with [INCREMENTAL-REVIEW.md](INCREMENTAL-REVIEW.md) and
[review-summary.json](review-summary.json). The report retains the rejected
original main-body automatic bridge route, corrected short-axis bridge setting
with support below bridges, approximately 8.3 mm internal bridging requirement,
staged lateral support removal, clearance glue positioning, and absence of
physical print, removal, fit, glue or strength tests. Finite sampling remains
finite evidence rather than a complete support removal guarantee.

The 22 source reports, JSON results, patch and historical scripts are copied from
the review's top level, `docs-audit` and `evidence-audit`. The duplicate 145-file
candidate snapshot and `repo-context` snapshots are excluded. The original
[building package](../../../校本部/buildings/cnu-j-grandstand-historical/README.md)
is retained separately, without changes to those 145 files by this integration.
The publication workflow adds a status preface to its README and recomputes its
MANIFEST; these two metadata changes are outside the original fixed-candidate GO
and are handled separately by publication preflight. The other 143 package files
remain byte-identical to the reviewed candidate. Exact candidate copies of the
[original README](../candidate-README.md) and
[original MANIFEST](../candidate-MANIFEST.sha256) preserve that boundary.
No source photographs, HTML, raw G-code, Git data, credentials or bytecode are
included. `author-delivery.json` and `delivery.json` are historical receipts, not
current publication or Library-version receipts.

Only host-specific absolute paths were replaced with explicit `${ROLE}` strings.
These placeholders name historical inputs, not downloadable files or runnable
paths. The exact per-file source SHA, copied SHA, role counts and role meanings
are in [integration-source-manifest.json](integration-source-manifest.json).
Source manifest files such as `delivery-manifest.json` and
`evidence-audit/EVIDENCE-AUDIT-MANIFEST.json` intentionally retain their original
hashes and sizes, including references to excluded context. They describe the
original review archive, not this sanitized copy. Use the new integration
manifest for the current copied bytes; original source hashes were not rewritten
to pretend that sanitized copies are byte-identical.

[integration-validation.json](integration-validation.json) records strict JSON
structure, type, key order, numeric/boolean/null leaf and non-path string
preservation, Python syntax parsing and local Markdown link checks. The historical
scripts still require their original private inputs and directory layout; they
were parsed, not executed as a new geometry, slicing or manufacturing audit.
Run `python verify_integration.py` here to validate current payload hashes and
numeric/boolean/null leaf digests without those private inputs. The integration
does not repeat the original geometry, collision, interface, slicing, bridge,
support-ray, photographic or physical checks.
