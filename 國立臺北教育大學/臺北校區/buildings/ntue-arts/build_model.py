"""Photo-derived public exterior study. Millimetres; dimensions are visual estimates.
Run with Python 3.12 and requirements.txt. Public plan outlines guide massing; interiors are not reconstructed.
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
# Arts hall open courtyard and bowed upper glazed entrance, from official plan.
add(0,0,0,112,150,3)
# Two deep classroom wings and front connector surround a genuinely open court.
for x in [-39,39]:add(x,6,2.8,25,126,72)
# Back connecting passage kept low: plan identifies ground corridor, height unknown.
# No invented enclosed rear wing; both observed classroom wing ends are plain.
add(0,-42,25.5,55,16,48)
# Convex semicircular front glazing mass; rear half clipped to connector.
curved=Manifold.cylinder(48,27.5,27.5,circular_segments=80) ^ box(0,-15,0,58,30,49)
parts.append(curved.translate((0,-40,25.5)))
# Four curved window bands recessed in the actual curved wall; 1.4 mm frame ribs.
for z in [29,40,51,62]:
 ring=Manifold.cylinder(8.8,28,28,circular_segments=80)-Manifold.cylinder(9.8,25.2,25.2,circular_segments=80).translate((0,0,-.5))
 cuts.append((ring ^ box(0,-16,0,60,33,10)).translate((0,-40,z)))
# Curved vertical glazing frames, fewer and thicker than actual fine mullions.
for a in range(195,346,15):
 rad=math.radians(a);x=26.1*math.cos(rad);y=-40+26.1*math.sin(rad)
 details.append(box(0,0,0,2.0,1.1,47).rotate((0,0,a)).translate((x,y,26)))
# Continuous principal horizontal floor bands stand proud of subordinate mullions.
for z,h in [(25.5,3.5),(37.8,2.2),(48.8,2.2),(59.8,2.2),(70.8,2.7)]:
 band=Manifold.cylinder(h,28.2,28.2,circular_segments=80)-Manifold.cylinder(h+1,25.0,25.0,circular_segments=80).translate((0,0,-.5))
 details.append((band ^ box(0,-15,0,60,30,h+1)).translate((0,-40,z)))
# Tall four front columns; rear backing/connector supports also join upper mass.
for x,y in [(-20,-48),(-9,-57),(9,-57),(20,-48)]:column(x,y,3,1.9,24)
# Recessed ground glazing behind open entrance lobby, never a flush solid portal.
add(0,-35,2.8,56,5,24)
for x in [-20,-10,0,10,20]:cut(x,-37.5,4,7.4,3.6,19)
# Six small window rows on visible brick entry flanks.
for x in [-41,41]:
 for z in [7,18,29,40,51,62]:cut(x,-57, z,8,5,3.5)
# Narrow full-height glazed strips flank the bowed central wall in both photos.
for x in [-30,30]:
 for z in [29,40,51,62]:cut(x,-57,z,5.0,4.5,8.8)
# Tall squared concrete caps visibly higher than central bowed glass roof.
for x in [-28,28]:add(x,-43,72.5,14,29,5)
# Front far corners softly rounded stairheads, supported by the wing masses.
for x in [-49,49]:column(x,-43,3,3.7,71)
# Wing parapets visible but roof equipment and unseen facade windows omitted.
for x in [-51.5,-26.5,26.5,51.5]:add(x,10,74,1.6,118,1.7)
# Front wide semicircular stairs fused to the base.
for i,r in enumerate([31.5,30,28.5]):
 disk=Manifold.cylinder(.7*(i+1),r,r,circular_segments=64) ^ box(0,-16,0,65,32,3)
 parts.append(disk.translate((0,-40,2.8)))

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
