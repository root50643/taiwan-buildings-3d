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
# Medical humanities museum: retained central block + west wing roof mass, not demolished auditorium.
add(0,11,0,150,124,3)
# Long westward front wing and orthogonal west return inferred from public exterior aerial.
add(-13,0,2.8,110,29,35)
add(-55,32,2.8,28,64,35)
add(-13,0,37,113,32,1.7);hip(-13,0,38.3,112,31,8)
add(-55,32,37,31,67,1.7)
parts.append(CrossSection.square((66,30),center=True).extrude(8,scale_top=(.72,.03)).rotate((0,0,90)).translate((-55,32,38.3)))
# Higher central block on the east end, small east stub and hipped roof visible in aerial.
add(39,0,2.8,45,46,36)
add(39,0,38,48,49,1.8);hip(39,0,39.3,47,48,12)
add(63,0,2.8,17,29,35);add(63,0,37,19,32,1.7);hip(63,0,38.3,18,31,7)
# South-facing central three arches on both levels.
for x in [28,39,50]:
 for z,h in [(5,13),(23,13)]:
  arch_cut(x,-23,z,8.4,h,3.4)
  outer=arch(x,-23.6,z-.4,10.3,h+1.2,2.4);inner=arch(x,-24,z,8.4,h+.1,3.6)
  details.append(outer-inner)
  if z==23:
   details.append(box(x,-22.9,z+5,8.8,2,1))
   details.append(box(x,-22.7,z,1,2.2,12))
for x in [21,33.5,44.5,57]:
 column(x,-23.65,22,1,16)
 add(x,-24,21,2.8,3,1.5);add(x,-24,37,2.8,3,1.5)
add(39,-23.7,20.5,44,2.7,2)
add(39,-23.7,38,47,3,1.8)
# Curved baroque-style central pediment with round medallion; small ornament simplified.
pts=[(22,38),(56,38),(56,42),(46,46),(45,49)]
pts += [(39+6*math.cos(t),49+6*math.sin(t))for t in np.linspace(0,math.pi,33)[1:]]
pts += [(32,46),(22,42)]
parts.append(profile(pts,-23,4))
cuts.append(Manifold.cylinder(3,2.2,2.2,circular_segments=40).rotate((90,0,0)).translate((39,-23.5,50)))
# Backed surround to the round opening.
ring=Manifold.cylinder(1.5,3,3,circular_segments=40)-Manifold.cylinder(2,2.2,2.2,circular_segments=40).translate((0,0,-.2))
details.append(ring.rotate((90,0,0)).translate((39,-24.6,50)))
step(39,-31,40,5)
# West front arcade: lower semicircular recesses; upper paired columns and solid parapet.
for x in [-59,-47,-35,-23,-11,1]:
 arch_cut(x,-14.5,5,9,13,3.2)
 cut(x,-14.5,24,10,3.2,11)
 for xx in [x-4.4,x+4.4]:column(xx,-15,23,.85,13)
 add(x,-15,21.5,12,2,2)
# West return and all unseen rear windows are intentionally blank rather than guessed.
# No rebuilt historic towers, dormers, auditorium, fence, modern hospital or interior.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
