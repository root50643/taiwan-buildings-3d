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
# N22: historic principal rectangular front block only; unseen annex excluded.
add(0,0,0,150,65,3)
add(0,4,2.8,136,40,39)
add(0,4,41,141,45,2.2)
# Broad projecting entrance screen, rendered as robust backed grille.
add(-12,-18,15,42,7,26)
for x in range(-30,8,3):
 for z in range(18,40,3):cut(x,-21.5,z,1.6,2,1.6)
# Ground entrance beneath deep canopy, fixed columns retain roof support.
cut(-12,-16,4,34,6,10)
add(-12,-22,14,45,12,2)
for x in [-32,8]:details.append(box(x,-21,3,2.2,5,13))
step(-12,-28,38,4)
# Three window levels, visible narrow pilasters and horizontal spandrels.
for x in [-61,-49,20,32,44,56]:
 for z in [6,19,32]:
  cut(x,-16, z,8.3,2,8)
  details.append(box(x,-16,z,1,1.4,8))
  details.append(box(x,-16,z+4,8.3,1.4,.9))
for x in [-67,-55,-43,14,26,38,50,62,68]:add(x,-16.7,3,1.5,1.8,39)
# Right end wall seen in official oblique photo: mostly plain with framing strips.
for y in [-13,2,17]:add(68.4,y,3,1.4,1.3,39)
# No invented rear windows, rooftop tanks, air-conditioning or side annexes.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
