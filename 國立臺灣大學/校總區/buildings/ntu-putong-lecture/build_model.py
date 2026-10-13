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

def ell(x,y,z,rx,ry,h):return Manifold.cylinder(h,1,1,circular_segments=128).scale((rx,ry,1)).translate((x,y,z))
def circle_cut(x,y,z,r,d):cuts.append(Manifold.cylinder(d,r,r,circular_segments=24).rotate((90,0,0)).translate((x,y+d/2,z)))
def ramp_x(x,y,z,w,d,h):parts.append(profile([(x-w/2,z),(x+w/2,z),(x+w/2,z+h)],y,d))
# N11. Distinct central tall arched-glass bay and open-facing tiered wings.
add(0,0,0,150,98,3)
add(0,12,2.8,134, 50,47)
# Ends project forward; central stair bay is taller than roof parapet.
for x in [-56,56]:add(x,-18,2.8,22,29,48)
add(0,-20,2.8,25,17,51)
gable(0,-20,53,25,17,5)
arch_cut(0,-28.5,16,12,34,2);arch_trim(0,-28.5,16,12,34)
for x in [-3,3]:details.append(box(x,-28.3,16,1,1.5,26))
for z in range(20,47,5):details.append(box(0,-28.3,z,12,1.5,1))
circle_cut(0,-28.5,54,1.6,2)
# Main three upper corridor rows; public exterior openings backed for printability.
for x in [-44,-31,-18,18,31,44]:
 for z in [25,34,43]:cut(x,-13,z,10,2.3,5.5)
for x in [-56,56]:
 for z in [25,34,43]:cut(x,-32.5,z,15,2.4,5.5)
for z in [22.5,31.5,40.5,49.5]:
 add(0,-13,z,134,1.5,1.1)
 for x in [-56,56]:add(x,-32.5,z,23,1.5,1.1)
# Tall ground arcade visible in official multi-angle photographs.
for x in [-39,-20,20,39]:arch_cut(x,-13,3.1,12,15,3.5);arch_trim(x,-13,3.1,12,15)
for x in [-56,56]:arch_cut(x,-32.5,3.1,12,15,3.5)
for x in [-8,8]:cut(x,-28.5,4,3,2,9)
# Canopy line above open entrance arcade, simplified solid strip.
add(0,-16,18,88,7,1.5)
step(0,-35,29,4)
# Roof kept flat behind the evidence-backed central pediment; unobserved rear blank.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
