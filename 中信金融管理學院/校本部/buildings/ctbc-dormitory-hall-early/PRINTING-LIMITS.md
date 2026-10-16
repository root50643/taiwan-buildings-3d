# Printing limits

This is an exterior study for a nominal1:400 model, with a200×125mm base and about58.25mm overall height. All building dimensions are estimates. The source-coordinate calibration is documented; no claim of surveying or as-built precision is made.

The exported STL uses millimetres and combines the base, exterior masses, steps, independent front arches and tie beams into one connected solid. Window openings are mainly blind recesses; the large upper flat arch and front arcade are genuine voids. Interior rooms and unknown structure are not reconstructed.

Tiny photographed mullions, fins, plate edges, upright bars and beams are simplified/thickened. Many exposed members are roughly0.9–1.2mm or more; this is a manufacturing choice, not an actual construction measurement. The top white arch rim is thickened and its eastern roof is left as an uncomplicated flat surface because an unverified shallow recess would create an unnecessarily thin roof skin. The source-led inner arch and its silhouette remain.

Supports will likely be needed beneath the long shallow arches, projecting western plates, entry canopy and other horizontal ledges. The long spans should not be assumed to bridge safely in FDM. Keep the base flat on the build plate. Do not scale down without rechecking thickness, spans and minimum openings. Material, nozzle, layer height, resin brittleness, support placement and slicer behavior can change the outcome.

Numerical QA uses original stored STL normals and faces, raw single-surface topology, exact triangle-contact testing, finite XY layer/Polygon checks and ten inward-normal rays per original face. These are finite geometric checks, not a proof of all possible minimum walls, a slicer approval or a physical print test. Any strict failures remain failures unless exact recorded events are separately classified; no sample relocation or mesh repair is allowed.

No physical print has been made. No guaranteed printability, support-free printing or material-specific strength is claimed.

## Authored v9 manufacturing substitutions
External glazing borders are broadened from about 0.46 to 0.91 mm. The western bottom frame and northern short-wing southeast root are thickened by changing the authored recess boundaries. The independent arcade is expanded/rounded about 0.5 mm in XY, with a 0.05 mm Z allowance; all six arches stay open. Entry supports and upper-arch uprights receive 0.5 mm plan corner fillets; courtyard step ends use 0.5 mm plan corner rounding. These are explicit shape changes before STL export, not repair or restoration claims. No numerical sample is moved to obtain a pass.

In v11 the lower window headers start at the true opening top, rather than extending slightly below it with tiny side roots. Courtyard arcs extend a small distance into the southern wall, replacing a near-tangent butt joint with reliable solid overlap. The visible open courtyard and arch openings remain.
