# Independent visual source review — NUU Erping gate segment

Review date: 2026-10-20 22:09 UTC.
Decision: **LIMITED VISUAL PASS for a bounded exterior approximation**, conditional on retaining the documented scope/unknowns below in public README and evidence. This is not a printability, engineering, exact-dimension, or photographic-reproduction certification.

## Reviewed evidence and artifact
Personally inspected complete official entrance photographs (1) and (2), both 3072×2048, captured 2025-02-28 at 10:33:33 and 10:34:50 +08:00 according to OriginalDateTime. Their URLs and identity chain are recorded below. Two different near-front/right viewpoints support this bounded model; they do not show a complete back elevation.

- https://secretary.nuu.edu.tw/p/132-1003-1091.php?Lang=zh-tw
- https://secretary.nuu.edu.tw/var/file/3/1003/gallery/91/1091/gallery_1091_6368587_24416.jpg
- https://secretary.nuu.edu.tw/var/file/3/1003/gallery/91/1091/gallery_1091_2039372_24416.jpg

Personally inspected the actual mesh renders `front.png`, `rear.png`, `elevation.png`, `top.png`, `left_oblique.png` together at sufficient resolution for silhouette, relative placement, cap and recess checks. Recomputed actual STL SHA-256:
`fa9b2d9bd1be1dda8fe49c479cede65c0f2a938046bcba48813c278da154dc80`.
This review is bound to that mesh, not any future modified geometry.

## Visual findings
- PASS identity/scope: tall central white school-name tower and its attached small gate booth, not the separate broad booth attached to J1 on photo left. The existing J1 model explicitly excludes the gate and guard booths, so this does not duplicate that package.
- PASS approximate mass ratios: tower 120 mm tall × 24 mm front width has the observed slim roughly five-to-one silhouette. Booth cap height 46.8 mm is roughly 39% of tower height, consistent with the two sources. No absolute real-world dimension is established.
- PASS sign-tower relief: front long recess, broad upper cap and narrow right rebate convey the observed facade depth. Solid shallow backing is an admitted conservative substitute; the photographs do not establish complete slot through-opening topology. It must not be described as an accurately recovered interior/void.
- PASS booth relation: small low mass behind tower, outward side glazing, pale cap with modest overhang and ochre fascia are consistent. Rounded rear/cap footprint is a plausible simplified closure, not a surveyed full floor plan. No unseen rear windows have been invented.
- PASS material hierarchy: warm white tower/booth, light frames and dark desaturated glazing, subdued fascia remain source-consistent. Fine wall tiles are simplified rather than fabricated detailed texture.
- Tower inscription is deliberately blank. This substantially reduces literal sign recognition but is acceptable when explicitly called out; no false calligraphy has been invented.

## Mandatory retained limits
1. Scope is ONLY central tower and attached booth, not the entire entrance, surrounding J1, roadway or an interior/security reconstruction.
2. Inscription 國立聯合大學 / NUU is omitted; do not label blank model a faithful lettering reproduction.
3. Deep slots use backed recesses, with original through-opening topology unconfirmed.
4. Rear and roof footprint, depth, exact window/frame subdivisions and ground level are approximate; plain rear is an evidence-limited closure, not observed truth.
5. Base is neutral display/printing support, not a measured traffic island.
6. Source capture is February 2025, not certified October 2026 condition. Reference photographs must not be copied into public package.
7. Thin frames, eaves and tall slender tower still require independent mesh, local-feature and slicing checks; visual pass does not replace them and does not promise successful physical printing.

No visual HOLD identified for this disclosed bounded exterior approximation. If geometry changes, repeat rendered-mesh visual review and update the hash.
