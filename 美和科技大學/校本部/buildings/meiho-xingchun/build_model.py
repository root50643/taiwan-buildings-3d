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
# G Xingchun/Medical Biotechnology: unequal glass towers, butterfly crowns and curved galleries.
add(0,0,0,150,106,3)
add(0,14,2.8,110,55,108)
# Stepped upper rear wings.
add(-35,14,110,40,55,2)
add(34,14,110,42,55,10)
add(34,14,119,45,58,2)
# Deep entrance recess and recessed gallery strips.
cut(0,-14,3,23,13,15)
for x in [-43,0,44]:
 for z in range(19,110,10):cut(x,-14,z,17,8,6.3)
# Unequal projecting full-height glazed vertical bays.
for x,top in [(-23,104),(23,119)]:
 add(x,-18,2.8,18,13,top-2.8)
 cut(x,-24.5,11,14,2.5,top-16)
 # Mullions and transoms fused to shallow curtain wall backing.
 for xx in [x-5,x+5]:details.append(box(xx,-24.5,11,1.1,2.7,top-16))
 for z in range(16,int(top)-4,7):details.append(box(x,-24.5,z,14,2.7,1.1))
 # Crown consists of split shouldered masses flanking a narrow central strip.
 parts.append(profile([(x-12.5,top-.2),(x-12.5,top+17),(x-9,top+17),(x-5,top+15),(x-2,top+11),(x-2,top-.2)][::-1],-17,14))
 parts.append(profile([(x+2,top-.2),(x+2,top+11),(x+6,top+17),(x+9,top+18),(x+12.5,top+15),(x+12.5,top-.2)][::-1],-17,14))
 add(x,-17,top-.2,3,11,20)
 cut(x,-24.5,top,3,3,18)
 # Butterfly silhouette, solid thickness and central support.
 profile_pts=[(x-17,top+24),(x-11,top+22),(x-5,top+18),(x,top+17),(x+5,top+18),(x+11,top+22),(x+17,top+24),(x+15,top+26),(x+9,top+24),(x+4,top+20),(x,top+19),(x-4,top+20),(x-9,top+24),(x-15,top+26)]
 parts.append(profile(profile_pts,-17,15))
 add(x,-17,top+15,3,10,5)
 # Pair of high shoulders shaped as shallow gables, crown base trim.
 add(x,-18,top-1,27,17,2)
# Rounded small balconies at both sides, every other gallery level retained.
for x in [-45,44]:
 for z in range(21,110,11):
  balcony=Manifold.cylinder(1.8,10,10,circular_segments=48).translate((x,-14,z))
  parts.append(balcony)
  ring=Manifold.cylinder(3.2,10,10,circular_segments=48)-Manifold.cylinder(3.3,8.5,8.5,circular_segments=48)
  parts.append(ring.translate((x,-14,z+1.6)))
# Distinct low stone-fronted pylons with backed arched niches, entry portico.
for x in [-47,47]:
 add(x,-21,3,19,18,26);arch_cut(x,-30,5,7,15,2.5)
 for xx in [x-6,x+6]:cut(xx,-30,11,1.8,2.5,14)
 add(x,-21,29,21,20,1.6)
add(0,-23,15,25,24,2)
for x in [-10,10]:add(x,-33,3,2.4,2.5,12.3)
step(0,-40,48,5)
# Visible right return window bands; back remains explicitly unobserved and simplified.
for z in range(20,111,11):
 for y in [0,12,25]:cut(55,y,z,3,8,6)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
