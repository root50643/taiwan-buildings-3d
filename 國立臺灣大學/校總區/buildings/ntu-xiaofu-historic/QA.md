# QA scope and corrections

Geometry/format tests in QA.json: finite vertices, nondegenerate triangles, consistent normals, positive volume, one connected component, two faces per edge, STL exact exported triangles, 3MF vertices/faces/material-index consistency and mm units. Current mesh has 2350 triangles. See JSON for computed values.

Corrections during local development:
1. Intersecting courtyard floor-band endpoints produced float-rounded degenerate triangles. Extended boolean overlap rather than deleting faces; rebuilt geometry, all 12 tests pass.
2. First image inspection found a courtyard parapet continuing inward across the roof beyond the bevel. Shortened north-wing parapet to actual bevel endpoint, regenerated all images and Blender scene.

Source evidence independently reviewed. Visual QA is separate and explicitly conditional on the historical simplification scope. No claim of exact rear facade, exact bay count or measured scale. No real-world trial print, slicer validation, structural analysis, or current-condition survey performed.

Clean-directory geometry rebuild compares mesh arrays and STL exactly. Blender checker compares visible geometry with NPZ and confirms no external reference images/text blocks. Reference photographs are not included in the package. Hidden editable meshes overlap; only the visible union is the printable/exportable body.
