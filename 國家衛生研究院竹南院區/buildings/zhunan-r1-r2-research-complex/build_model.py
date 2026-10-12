"""NHRI Zhunan R1/R2: public-exterior reference miniature, not surveyed geometry.
Units: millimetres. Rebuild with Python 3.12 and requirements.txt.
Only open exterior relief is cut into otherwise solid masses; no interiors.
"""
from pathlib import Path
import json
import numpy as np
import trimesh
from manifold3d import Manifold, OpType
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]
def box(x,y,z,w,d,h):
    return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h): parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h): cuts.append(box(x,y,z,w,d,h))
# Coordinates are presentation coordinates: the principal courtyard faces -Y.
# Right wing R1 / left wing R2 follows official map aligned to courtyard axis.
add(0,0,0,144,150,3)
for s in [-1,1]:
    cx=s*48.5
    # Each bar is visibly divided into two broad roof/facade blocks.
    for cy in [-33.5,33.5]:
        add(cx,cy,2.8,36,57,57.2)
        # Flat cap and small rear/front parapet silhouettes, no rooftop equipment.
        add(cx,cy,59.5,36,57,.9)
        # Outer facades: broad eight-tier gridded glazing fields, witnessed in
        # Futsu's public campus photograph. Deep wall remains behind each pane.
        for yy in np.linspace(cy-20,cy+20,7):
            for zz in np.arange(7.2,51,5.7):
                cut(s*66.4,float(yy),float(zz),1.7,4.6,4.3)
        # Inner courtyard face: larger vertically paired openings in four tiers.
        for yy in np.linspace(cy-20,cy+20,6):
            for zz in [10.2,21.6,33.0,44.4]:
                cut(s*30.5,float(yy),zz,1.65,5.8,9.0)
        # Shallow integral outer horizontal shade rails, 0.8 mm thick.
        for zz in np.arange(6.4,52,5.7):
            add(s*66.6,cy,float(zz),.85,47,.85)
    # Recessed central joint, like the narrow vertical dark split in outer view.
    add(cx,0,2.8,32,10.4,54.8)
    for zz in np.arange(7.1,51,5.7):
        cut(s*64.5,0,float(zz),1.4,5.8,4.3)
    # Courtyard-facing tall return slot beside the near end mass.
    for zz in [10.2,21.6,33,44.4]:
        cut(s*30.5,-58.0,zz,1.65,3.2,8.8)
    # Near end: tall glass bay beneath a dark clerestory/stone crown.
    # All mullions and louvers are printable relief on a solid backing.
    for xx in [cx-7.6,cx-2.5,cx+2.5,cx+7.6]:
        for zz in np.arange(7.2,49,4.5):
            cut(xx,-62.0,float(zz),3.95,1.8,3.4)
    cut(cx,-62.0,54.0,23.0,1.8,3.0)
    for zz in np.arange(6.4,50,4.5):
        add(cx,-62.35,float(zz),25.8,1.5,.85)
    # Two fine vertical ribs break the large glazing field as in the front photo.
    for xx in [cx-1.4,cx+1.4]:
        add(xx,-62.25,6.4,.9,1.5,43.4)
    add(cx,-62.4,50.5,27.4,1.8,1.3)
    # Far end is not fully visible in the reference set: plain conservative wall,
    # deliberately no fabricated window pattern on that unverified elevation.
    # Low open gallery along the courtyard edge, attached to the common base.
    add(s*27.2,-17,2.8,9.5,112,.9)
    for yy in np.arange(-64.5,38,8.2):
        add(s*23.0,float(yy),3.5,1.8,1.8,9.4)
    add(s*23.0,-13.7,12.0,2.1,103.5,1.5)
# Public map shows an H-like central crossing, not a continuous rear U-shaped bar.
# Set-back cross volume and forward-projecting central glass-fronted head.
add(0,1,2.8,98,17.5,41.2)
add(0,7,2.8,23,43,47.5)
add(0,-18.5,2.8,27,22,50.7)
add(0,-18.5,52.8,29,24,1.25)
# Central front glazing: narrow stone jambs and prominent continuous verticals.
for xx in [-7.3,-2.45,2.45,7.3]:
    for zz in np.arange(8.0,48,5):
        cut(xx,-29.5,float(zz),3.8,1.7,3.9)
for xx in [-1.0,1.0]: add(xx,-29.65,9.5,.85,1.2,39.5)
# Entry represented only by exterior relief, no doorway or interior cavity.
cut(0,-29.5,3.2,4.1,1.4,5.6)
add(0,-30.0,8.8,6.1,1.65,1.1)
for i in range(3): add(0,-30.8-i*1.2,3,8.5,1.5,1.2-i*.3)
# Visible glazed connectors flanking the central head.
for s in [-1,1]:
    for xx in [s*17.8,s*23.1,s*28.2]:
        for zz in np.arange(8,39,5.6):
            cut(xx,-7.7,float(zz),3.7,1.6,4.35)
# Rear of central spine is reference-limited and therefore intentionally plain.
# No invented laboratory layouts, facilities, access controls or equipment.
solid=Manifold.batch_boolean(parts,OpType.Add)
solid=solid-Manifold.batch_boolean(cuts,OpType.Add)
if solid.status().name!='NoError': raise RuntimeError(str(solid.status()))
m=solid.to_mesh()
mesh=trimesh.Trimesh(vertices=np.asarray(m.vert_properties)[:,:3],faces=np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl'); mesh.export(OUT/'model.obj')
print(json.dumps({'dimensions_mm':mesh.extents.tolist(),'faces':len(mesh.faces),'watertight':mesh.is_watertight,'manifold_status':str(solid.status())},indent=2))
