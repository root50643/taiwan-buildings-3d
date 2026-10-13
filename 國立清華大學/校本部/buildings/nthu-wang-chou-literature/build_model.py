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
# Completed 2024 exterior, long elevation and downhill end photographs.
# Public exterior only, stepped terrain flattened into common display base.
def plan(poly,z,h):return CrossSection([poly]).extrude(h).translate((0,0,z))
add(0,0,0,150,108,3)
# Solid opaque surrogate behind deep glazing, no internal room reconstruction.
add(0,3,2.8,116,40,63.2)
# Public downhill elevation: stepped lower window backing and open-looking recess.
cut(0,-17,5,111,13,18)
for x in [-54,-28,0,28,54]:det(x,-19,3,3.6,17,24)
# Flared concrete buttresses visible supporting the projecting middle balcony.
for x in [-42,-12,18]:
 # Extruded x-z quadrilateral, deliberately thickened for printability.
 details.append(wedge([(x-8,3),(x-2,3),(x+8,28),(x+2,28)],-21,8))
# Rounded/chamfered balcony edge, prominent wrapping horizontal concrete band.
outline=[(-63,-18),(-57,-27),(-43,-31),(39,-31),(57,-25),(64,-15),(64,24),(-63,24)]
parts.append(plan(outline,26,4))
# Middle glazing is recessed between full-height broad piers.
cut(0,-17,32,112,4.5,13)
for x in [-53,-30,-7,16,39,54]:det(x,-18,31,2.2,6,15)
for z in [36.5,41.5]:det(0,-18,z,112,5,1.2)
# Narrow front/end bay wraps visible end, backed by solid body.
cut(58,0,32,4.4,30,13)
for y in [-12,-3,6,15]:det(58,y,31,5,1.2,15)
add(0,1,47,126,49,2.8)
# Deep vertical sun fins, recognizable long upper facade rhythm.
cut(0,-17,51,111,5,13)
for x in [-54,-39,-24,-9,6,21,36,51]:det(x,-19,49,2.3,11,17.5)
cut(58,1,51,4.4,30,13)
for y in [-11,1,13]:det(58,y,50,5,1.5,15)
# Stepped pitched roof strips; ridge/eaves height modulation follows photo outline.
# Each strip spans x, with thick closed gable fill. Not a thin unsupported roof skin.
for xa,xb,peak,eave in [(-65,-42,78,68),(-42,-12,80,70),(-12,17,82,70),(17,43,80,68),(43,65,78,66)]:
 roof=CrossSection([[(-28,64),(29,64),(29,eave-1),(0,peak),(-28,eave)]]).extrude(xb-xa).rotate((90,0,90)).translate((xa,0,0))
 parts.append(roof)
# Public exterior stair at uphill end, broad stair/ramp cheek rather than wire rails.
for i in range(10):add(63,18-i*3.7,3,9,4,3+i*2.4)
add(67,0,3,2.5,40,15)
# Back is deliberately simple: evidence does not establish complete rear facade.
solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
