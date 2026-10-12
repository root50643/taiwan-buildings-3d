"""Photo-derived NHRI station-48 exterior mass; standalone miniature in millimeters.

Only the publicly visible rectangular tower exterior is represented.  The bridge,
interior, equipment, systems, and security features are deliberately omitted.
Run with the pinned packages in requirements.txt: python build_model.py
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold

OUT = Path(__file__).resolve().parent
parts, cuts, details = [], [], []

def box(x, y, z, w, d, h):
    return Manifold.cube((w, d, h)).translate((x-w/2, y-d/2, z))

def add(x, y, z, w, d, h):
    parts.append(box(x, y, z, w, d, h))

def cut(x, y, z, w, d, h):
    cuts.append(box(x, y, z, w, d, h))

# Display plinth; it is not a surveyed portion of the site.
add(0, 0, 0, 116, 82, 3)
# The main tall white mass and shorter right-hand glazed bay seen at station 48.
# Depth and unseen walls are conservative closed approximations, not a floor plan.
add(-12, 0, 2.8, 80, 64, 144.2)
add(40, 0, 2.8, 28, 64, 128.2)
# The broad largely blank central plane and the slightly lower left vertical pier.
add(-5, -32, 2.8, 58, 2.6, 147.2)
add(-49, -32, 2.8, 8, 2.6, 144.2)
# Raised outer edge of the lower right bay, visible in the reference photograph.
add(51.5, -31.7, 2.8, 5, 3.2, 131.2)
# Narrow recessed glass slot. Broad separator bands are exterior facade relief.
for z, h in [(4, 37), (44, 24), (71, 26), (100, 39)]:
    cut(-39.5, -32.1, z, 9, 1.7, h)
# Large right panel, split into the two photo-observed glazing zones.
for z, h in [(43, 38), (84, 44)]:
    cut(37, -32.1, z, 19.5, 1.8, h)
    details.append(box(37, -31.75, z, 1.1, 1.8, h))
    for zz in np.arange(z+13, z+h-1, 13):
        details.append(box(37, -31.75, float(zz), 19.5, 1.8, 1.1))
# Sparse enlarged surface joints convey the blank tiled facade at FDM scale.
# These are illustrative joint rhythms, not a tile survey or exact bay count.
for x in [-20.5, -6, 8.5]:
    cut(x, -33.3, 34, .65, .65, 113.5)
for z in [43, 60.5, 78, 95.5, 113, 130.5]:
    cut(-5, -33.3, z, 57.8, .65, .65)
# Backed ground-level window under the central white plane.
cut(-7, -33.3, 9, 38, 1.9, 22)
for x in [-19, -7, 5]:
    details.append(box(x, -32.9, 9, 1.2, 1.8, 22))
# Small glazed entrance projection visible below the omitted bridge.
# The blocked/partly obscured doorway is represented only as shallow external relief.
add(31, -33.3, 2.8, 25, 6.5, 29.2)
cut(31, -36.55, 5, 20.5, 1.8, 24)
details.append(box(31, -36.3, 5, 1.3, 1.7, 24))
# No side/rear openings, roof equipment, covered walkway, or bridge is invented.
solid = parts[0]
for p in parts[1:]: solid = solid + p
for c in cuts: solid = solid - c
for q in details: solid = solid + q
solid = solid.simplify(.0001)
m = solid.to_mesh64()
mesh = trimesh.Trimesh(np.asarray(m.vert_properties, dtype=np.float32)[:, :3],
                       np.asarray(m.tri_verts), process=True)
mesh.update_faces(mesh.nondegenerate_faces())
mesh.update_faces(mesh.unique_faces())
mesh.remove_unreferenced_vertices()
mesh.export(OUT/'model.stl')
mesh.export(OUT/'model.obj')
print('Dimensions mm:', mesh.extents, 'watertight:', mesh.is_watertight,
      'solid count:', len(solid.decompose()))
