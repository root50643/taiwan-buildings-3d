"""Original photo-derived NTHU exterior miniature, dimensions in millimetres.
No source 3D assets, survey plans, or interior arrangements used.
Run: python build_model.py (see requirements.txt).
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]; details=[]
def box(x,y,z,w,d,h): return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h): parts.append(box(x,y,z,w,d,h))
def det(x,y,z,w,d,h): details.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h): cuts.append(box(x,y,z,w,d,h))
def ellipse(x,y,z,rx,ry,h): return Manifold.cylinder(h,1,1,circular_segments=96).scale((rx,ry,1)).translate((x,y,z))
def wedge(poly,y,depth): return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def column(x,y,z,r,h): parts.append(Manifold.cylinder(h,r,r,circular_segments=24).translate((x,y,z)))
# Original exterior approximation from architect-supplied 2019 photos.
# Only public facade envelope; roof plant and all internal installations omitted.
add(0,0,0,150,118,3)
add(0,0,2.8,118,76,108.2)
# Lower dark plinth and strong upper light frame have geometric offsets.
add(0,-.5,31,122,79,78)
# Long facade deeply recessed shade screen, six upper levels.
for z in [34,46,58,70,82,94]:
 cut(0,-40,z,113,4.5,9.5)
 for x in [-53,-35,-17,1,19,37,55]:det(x,-40,z,1.3,5,9.5)
 # Three broad shade slats per level, joined to mullions and solid backing.
 for zz in [z+1.4,z+4.1,z+6.8]:det(0,-40,zz,113,5,1.2)
# End elevation: two perforated wings around tall projecting opaque core.
add(60,1,29,6,22,85)
for z in [35,47,59,71,83,95]:
 for y in [-29,-18,21,32]:cut(61,y,z,4.5,6.8,7.5)
# Slender vertical slots in central facade core, shown as shallow grooves.
for y in [-5,0,5]:cut(63,y,50,1.8,1.2,50)
# Lower public exterior windows, shallow and robust.
for x in [-49,-31,-13,5,23,41,53]:cut(x,-38,19,6,3,3.5)
cut(-11,-38,7,68,3,6)
for y in [-29,-16,19,31]:
 for z in [7,19]:cut(59,y,z,3,6,5)
# Upper roof is a simple flat closed cap, no sensitive service equipment modeled.
# Unknown rear becomes plain envelope; connecting neighbor bridge not included.
solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
