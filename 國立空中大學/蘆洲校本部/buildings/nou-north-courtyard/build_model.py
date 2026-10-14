"""Original photo-derived exterior massing of National Open University North Courtyard.
Millimetres. Front is -Y; approximately 1:625 at the estimated 62 x 90 m eaves.
The red low-pitch weatherproof-roof version is represented, not an original flat roof.
No third-party 3D data, survey measurements or hidden interiors are used.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT = Path(__file__).resolve().parent
parts, cuts = [], []
BASE_H=1.8
WALL_TOP=7.2
ROOF_BOTTOM=7.05
EAVE_TOP=7.95
RIDGE_TOP=9.2

def box(x,y,z,w,d,h):
    return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):
    parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):
    cuts.append(box(x,y,z,w,d,h))
def hip(x,y,w,d,ridge_width=1.8):
    """Low hip roof with a printable flat ridge, minimum 1.8 mm at the top."""
    add(x,y,ROOF_BOTTOM,w,d,EAVE_TOP-ROOF_BOTTOM)
    if w < d:
        top=(ridge_width/w,(d-w+ridge_width)/d)
    else:
        top=((w-d+ridge_width)/w,ridge_width/d)
    parts.append(CrossSection.square((w,d),center=True).extrude(RIDGE_TOP-EAVE_TOP,scale_top=top).translate((x,y,EAVE_TOP-.03)))

# A common thin base keeps all ground-level pillars fused into one solid shell.
add(0,0,0,106,150,BASE_H)
# The four outer classroom wings. Unverified external window positions stay neutral.
for x in [-43.5,43.5]:
    add(x,0,BASE_H-.2,10.4,140.8,WALL_TOP-BASE_H+.2)
for y in [-65.0,65.0]:
    add(0,y,BASE_H-.2,96.6,10.8,WALL_TOP-BASE_H+.2)
# The central administrative crossbar is real occupied mass, not a canopy.
add(0,20.3,BASE_H-.2,86,10.6,WALL_TOP-BASE_H+.2)
# Roof eaves and low hips; overlap only above the corridor roofs, courts stay open.
for x in [-41.55,41.55]: hip(x,0,16.1,144)
hip(0,-63.4,99.2,17.2)
hip(0,64.0,99.2,16.0)
hip(0,20.3,84,20.6)
# Raised corridor floor aprons join the base; they do not fill either courtyard.
for x in [-36.15,36.15]: add(x,0,BASE_H-.12,5.5,127.5,.55)
for y in [-57.1,57.0,12.75,27.85]:add(0,y,BASE_H-.12,72.7,5.5,.55)
# Real column-and-beam circulation on the inner sides. Pillars thickened to 1.5 mm.
# Small frames and landscape pergolas are not falsely represented as structure.
for x in [-34.45,34.45]:
    for y in [-53,-44.7,-36.4,-28.1,-19.8,-11.5,-3.2,5.1,34.5,43.1,51.7]:
        add(x,y,BASE_H-.15,1.5,1.5,5.7)
    add(x,0,6.15,1.7,113.5,1.1)
for y in [-55.75,55.8,10.95,29.65]:
    for x in [-30,-22.5,-15,-7.5,0,7.5,15,22.5,30]:
        # Leave the front entrance's central sightline open.
        if y == -55.75 and abs(x)<3: continue
        add(x,y,BASE_H-.15,1.5,1.5,5.7)
    add(0,y,6.15,70.6,1.7,1.1)
# Backed inner classroom recesses: grouped windows separated by full-height wall.
# These deliberately simplify the documented low windows/doors behind the colonnade.
for x in [-38.3,38.3]:
    for y in [-49,-37,-25,-13,-1,38,49]:
        cut(x,y,3.6,1.15,5.8,1.75)
for y in [-59.6,59.6,15.0,25.6]:
    for x in [-27,-18,-9,9,18,27]:
        cut(x,y,3.6,5.0,1.15,1.75)
# Main front gate: central genuinely open passage, framing and shallow decorative blocks.
# The sign, scrolls and horse-and-carriage motifs are abstracted rather than invented.
cut(0,-64,BASE_H-.01,7.4,22,5.7)
# A broad high gate body / parapet rises above the low classroom ring.
for x in [-7.0,7.0]:add(x,-66.6,BASE_H-.15,5.2,13.2,7.7)
add(0,-66.6,7.15,19.2,13.2,1.75)
# Portal black frame is modeled as robust relief, not color alone.
for x in [-4.15,4.15,-9.05,9.05]:add(x,-73.25,BASE_H-.1,1.15,.65,6.7)
add(0,-73.25,7.10,19.2,.7,1.2)
for x in [-6.8,6.8]:
    add(x,-73.25,2.6,3.9,.6,1.4)
    add(x,-73.25,5.55,3.9,.6,1.05)
# Distinct hipped gate canopy and the higher white rear parapet visible in the photo.
add(0,-69.0,8.0,21.4,10.6,.85)
parts.append(CrossSection.square((21.4,10.6),center=True).extrude(1.75,scale_top=(.72,.24)).translate((0,-69.0,8.8)))
add(0,-66.5,9.35,16.0,1.3,1.75)
# Cuts are applied to all structural bodies, retaining the actual front-to-court door.
solid=Manifold.batch_boolean(parts, __import__('manifold3d').OpType.Add)
for c in cuts: solid=solid-c
assert len(solid.decompose())==1, 'Disconnected geometry'
m=solid.to_mesh64()
# Source vertices are directly exported; no mesh repair or post hoc remeshing.
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print({'dimensions_mm':mesh.extents.tolist(),'faces':len(mesh.faces),'watertight':mesh.is_watertight,'volume_mm3':float(mesh.volume)})
