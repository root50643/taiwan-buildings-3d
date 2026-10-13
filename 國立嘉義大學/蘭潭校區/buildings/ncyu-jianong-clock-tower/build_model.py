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
# Jia-nong Clock Tower. Full exterior landmark structure, not a teaching hall.
# Four-square core and through openings based on official oblique photograph.
add(0,0,0,86,86,3)
for i in range(3):add(0,0,2.8+i*1.2,70-i*7,70-i*7,1.4)
add(0,0,5.8,54,54,132.2)
# Central open shaft connects to exterior arches. No sealed internal cavity shell.
cut(0,0,5.9,40,40,129.1)
# Broad ground arch passages, transversely linked.
for a in [0,90]:cuts.append(arch(0,0,5.8,40,48,70).rotate((0,0,a)))
# Middle tier baluster-like slots, four per face, and upper pointed-arch open belfry.
for a in [0,90,180,270]:
 for x in [-15,-5,5,15]:cuts.append(box(x,-27,66,5.2,16,18).rotate((0,0,a)))
 pts=[(-18,96),(18,96),(18,103),(14,111),(8,119),(0,126),(-8,119),(-14,111),(-18,103)]
 cuts.append(profile(pts,-27,16).rotate((0,0,a)))
 # Per-face top shallow triangular gable silhouette.
 parts.append(profile([(-21,137),(21,137),(9,137),(0,143),(-9,137)],-27,5).rotate((0,0,a)))
# Continuous tier mouldings, supported all around by walls/corner columns.
for z in [53,62,86,91,129,137]:
 outer=box(0,0,z,57,57,2.1);inner=box(0,0,z-.2,41,41,2.5);details.append(outer-inner)
# Corner pilasters strengthened for a 150mm print, with caps and orb finials.
for x in [-25,25]:
 for y in [-25,25]:
  column(x,y,5.6,3.6,135.0)
  for z in [54,62,87,130,140]:parts.append(Manifold.cylinder(2.2,5,5,circular_segments=40).translate((x,y,z)))
  parts.append(Manifold.sphere(4,circular_segments=40).translate((x,y,146)))
  parts.append(Manifold.cylinder(4.5,2.4,2.4,circular_segments=24).translate((x,y,140.6)))
# Front clock is a backed shallow relief. Far panels plain, since inscriptions are not documented.
parts.append(Manifold.cylinder(2.2,6.8,6.8,circular_segments=64).rotate((90,0,0)).translate((0,-26.6,133)))
parts.append(Manifold.cylinder(2.6,5.6,5.6,circular_segments=64).rotate((90,0,0)).translate((0,-26.7,133)))
# Hands are robust relief bars on the disc; time is an illustrative mark, not historical evidence.
details.append(box(0,-29.1,132.4,1.2,1.1,4.4))
details.append(box(2,-29.1,132.4,4.1,1.1,1.2))
# Simplified interior access stair visible through official lower arch; fused stepped solid.
for i in range(12):
 details.append(box(-12,-16+i*2.7,5.4,10,3.1,1.5+i*4.2))
# A landing is attached to the side walls, open shaft remains on the other side.
details.append(box(-12,16,50.5,17,12,3))
# Omit small lettering, bells, electrical components and antenna finer than print scale.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
