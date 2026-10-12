"""NHRI Zhunan second-phase single dormitory exterior miniature, dimensions in mm.
Photo-derived front facade; unsurveyed depth/rear are deliberately plain estimates.
Run with Python 3.12+ after installing requirements.txt. No reference photos required.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]
def box(x,y,z,w,d,h):
    return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h): parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h): cuts.append(box(x,y,z,w,d,h))
def bay(x,zheight):
    # Broad flat front plus two beveled corner faces, read directly from front photograph.
    poly=[(x-4.5,-7.8),(x+4.5,-7.8),(x+4.5,-25),(x+2.8,-27),(x-2.8,-27),(x-4.5,-25)]
    parts.append(CrossSection([poly[::-1]]).extrude(zheight).translate((0,0,3)))
    for z in np.arange(5.2,zheight+1,7.25):
        if z+3.3 > zheight+2: continue
        cut(x,-27,z,5.6,1.5,3.3)
        # Angled recessed window panels continue round the projected bay corners.
        cuts.append(box(0,0,z,2.0,1.3,3.3).rotate((0,0,-40)).translate((x-3.45,-26.0,0)))
        cuts.append(box(0,0,z,2.0,1.3,3.3).rotate((0,0,40)).translate((x+3.45,-26.0,0)))
# Single solid base, independently scaled display miniature (not uniform campus scale).
add(0,0,0,150,76,3)
# Photo shows a broad background residential wing behind stepped projecting bays.
add(0,7,2.8,133,31,65.0)
# Taller blank end piers; side/rear depth is an estimate, not an as-built footprint.
add(-62,-.5,2.8,12,46,71.5)
add(62,.5,2.8,12,44,73.5)
# Central recessed glazed stack, left and right blank side strips.
add(0,-12,3,19,21,72)
# Paired polygonal bays climb inward; right highest pair slightly exceeds left pair.
for x,h in [(-54,24),(-45,24),(-36,44),(-27,44),(-18,71),(-9,71),
             (18,77),(27,77),(36,46),(45,46),(54,25),(63,25)]:
    bay(x,h)
# Left edge of central glazing is x=-4.5; front entrance/glazing centered at x=5.5.
# Cut grid across glass wall, leaving integral mullions >= 1.1 mm.
for z in np.arange(5.5,73,7.25):
    for x in [1.1,6.4]: cut(x,-22.5,float(z),4.2,1.5,4.2)
# Background window ribbons visible above low and mid-height stepped bays.
for x,min_z in [(-48,29),(-35,49),(42,51),(54,30)]:
    for z in np.arange(6,62,7.25):
        if z >= min_z:
            cut(x,-8.5,float(z),10.5,1.5,4.5)
# Robust photo-visible horizontal breaks within central glass stack.
for z in [28.8,51.2,67.2]: add(5,-23.1,z,18.6,1.8,1.4)
# Roof parapet band represented in relief; no unsupported thin rails or roof equipment.
add(4,-12.1,75,20,21.2,1.25)
# Entrance recess and gently vaulted porch read from lower center of public photo.
cut(5,-22.5,3.0,8.8,2.0,6.7)
# A shallow curved arch band has minimum 1.3 mm wall and 1.5 mm cantilever.
xs=np.linspace(-3,13,25)
upper=[(float(x),9.5+2.25*(1-((float(x)-5)/8)**2)) for x in xs]
lower=[(float(x),8.1+2.25*(1-((float(x)-5)/8)**2)) for x in xs[::-1]]
arch=CrossSection([(upper+lower)[::-1]]).extrude(2.4).rotate((90,0,0)).translate((0,-22.0,0))
parts.append(arch)
# Steps and short landing join the base and facade; no inferred outdoor stairs.
for i in range(4): add(5,-32.8+i*1.9,3,12.4,2.1,.6*(i+1))
add(5,-26.1,3,12.4,2.7,2.4)
solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
solid=solid.simplify(0.0001)
m=solid.to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties, dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.update_faces(mesh.nondegenerate_faces())
mesh.update_faces(mesh.unique_faces())
mesh.remove_unreferenced_vertices()
mesh.export(OUT/'model.stl')
mesh.export(OUT/'model.obj')
print('Dimensions (mm):',mesh.extents,'watertight:',mesh.is_watertight,'body count:',len(solid.decompose()))
