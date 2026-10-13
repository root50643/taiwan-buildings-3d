"""Photo-derived public exterior study. Millimetres; dimensions are visual estimates.
Run with Python 3.12 and requirements.txt. No survey or interior data used.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]; details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def profile(poly,y,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def gable(x,y,z,w,d,h):parts.append(profile([(x-w/2,z),(x+w/2,z),(x,z+h)],y,d))
def arch(x,y,z,w,h,depth):
 r=w/2; spring=z+h-r
 pts=[(x-r,z),(x+r,z),(x+r,spring)]
 pts += [(x+r*math.cos(t),spring+r*math.sin(t)) for t in np.linspace(0,math.pi,25)[1:]]
 return profile(pts,y,depth)
def arch_cut(x,y,z,w,h,depth):cuts.append(arch(x,y,z,w,h,depth))
def arch_trim(x,y,z,w,h):
 # Backed relief ring, fused into the wall, not a separate floating shell.
 details.append(arch(x,y,z,w+1.7,h+.85,1.7)-arch(x,y-.1,z-.2,w,h+.2,2.3))
def hip(x,y,z,w,d,h):parts.append(CrossSection.square((w,d),center=True).extrude(h,scale_top=(.72,.03)).translate((x,y,z)))
def column(x,y,z,r,h):parts.append(Manifold.cylinder(h,r,r,circular_segments=24).translate((x,y,z)))
def step(x,y,w,n=3):
 for i in range(n):add(x,y+i*1.4,2.8,w,1.7,.7*(i+1))
# D Bangxing: long five-level facade, upper rounded windows and detached-looking broad roof.
add(0,0,0,150,85,3)
add(0,8,2.8,132,43,63)
# Lower red wall panels alternate with continuous narrow light pilasters (geometry, not color).
for x in range(-59,61,13):add(x,-14.1,3,1.8,2,59)
for x in range(-52,54,13):
 for z in [8,20,33]:cut(x,-13.5,z,6.6,3.3,7)
 for z in [46,56]:arch_cut(x,-13.5,z,8,7,3.4)
# Recessed doorway at left-of-middle with broad shallow hipped canopy.
cut(-28,-13,3,16,7,9)
hip(-28,-22,10.5,33,19,4)
for x in [-42,-14]:add(x,-29,3,2,2,8)
# Upper flat eave and shallow curved/shed roof, based on the visible near end.
add(0,8,65,137,47,2)
roof=CrossSection([[( -17,67),(33,67),(33,72),(20,75),(-17,75)]]).extrude(138).rotate((0,0,90)).rotate((0,90,0))
# Long barrel-like cap represented directly by a transverse arch profile, extrusion along x.
pts=[(-17,66.5),(33,66.5),(33,69)]
pts += [(8+25*math.cos(a),69+7*math.sin(a)) for a in np.linspace(0,math.pi,33)[1:]]
parts.append(CrossSection([pts]).extrude(138).rotate((90,0,90)).translate((-69,0,0)))
# Roof supports visible above top-floor ceiling.
for x in range(-62,64,14):add(x,-15,66,1.4,1.5,6)
for z in [8,20,33,46,56]:cut(66,8,z,3,20,6)
step(-28,-34,36,3)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
