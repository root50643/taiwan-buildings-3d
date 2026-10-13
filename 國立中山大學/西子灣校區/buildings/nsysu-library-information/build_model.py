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

def low_arch(x,y,z,w,h,depth):
 pts=[(x-w/2,z),(x+w/2,z),(x+w/2,z+h*.45)]
 pts += [(x+w/2*math.cos(t),z+h*.45+h*.55*math.sin(t)) for t in np.linspace(0,math.pi,33)[1:]]
 return profile(pts,y,depth)
def xy_poly(points,z,h):return CrossSection([points]).extrude(h).translate((0,0,z))
# Library and Information Building: three-bay short face, long flank ~1.8x.
# Front freestanding circular campus pavilion is separate and deliberately excluded.
add(0,0,0,100,150,3)
add(0,0,2.8,72,126,122)
# Full-height round piers. Window panels are recessed, not painted grids.
for x in [-36,-12,12,36]:column(x,-64.0,3,1.7,122)
for side in [-1,1]:
 for y in [-62,-31,0,31,62]:column(side*36.4,y,3,1.7,122)
# Ground-level colonnade cut back 4 mm across each short-face bay.
for x in [-24,0,24]:cut(x,-63,3,19.5,8,12)
for y in [-46,-15,15,46]:cut(-36,y,3,8,25,12)
# Nine visible upper window ranks and shallow top clerestory row.
for z in [20,31,42,53,64,75,86,97,108]:
 for bay in [-24,0,24]:
  for dx in [-8,-4,0,4,8]:cut(bay+dx,-63,z,2.7,3.2,5.2)
 # Long visible flank; same observed mullion rhythm, grouped by 4 structural bays.
 for y0 in [-46.5,-15.5,15.5,46.5]:
  for dy in [-11.7,-7.8,-3.9,0,3.9,7.8,11.7]:cut(-36,y0+dy,z,3.2,2.6,5.2)
for bay in [-24,0,24]:
 for dx in [-8,-4,0,4,8]:cut(bay+dx,-63,119,2.7,3.2,3.7)
# Rear entrance photograph supports full-height cylindrical piers and deep sheltered bays.
for x in [-36,-12,12,36]:column(x,64,3,1.7,122)
for x in [-24,0,24]:cut(x,63,3,19.5,8,12)
# Upper rear rhythm is extended from visible lower facade and typical-floor plan.
# It is a documented simplification, not separately photographed in full.
for z in [20,31,42,53,64,75,86,97,108]:
 for bay in [-24,0,24]:
  for dx in [-8,-4,0,4,8]:cut(bay+dx,63,z,2.7,3.2,5.2)
# Opposite long elevation: symmetric window rhythm is inferred from official typical-floor plans.
for z in [20,31,42,53,64,75,86,97,108]:
 for y0 in [-46.5,-15.5,15.5,46.5]:
  for dy in [-11.7,-7.8,-3.9,0,3.9,7.8,11.7]:cut(36,y0+dy,z,3.2,2.6,5.2)
# Large cantilevered crown with three shallow-arched loggia openings.
add(0,0,124,82,137,3)
add(0,0,126.8,80,135,20.2)
for x in [-26,0,26]:cuts.append(low_arch(x,-67.6,131,22,8.6,11))
# Crown's long flank has the extended openings visible in oblique view.
for y in [-50,-17,17,50]:
 a=low_arch(y,0,131,28,8.6,11).rotate((0,0,90)).translate((-40,0,0))
 cuts.append(a)
# Flat roof capped at 148 mm including base; slight rim is backed and fused.
add(0,0,147,80,135,1)
# Small supported roof stair/service volume; unobserved equipment omitted.
add(0,13,147.7,15,22,2.3)
# Entrance stair seen at short face, no freestanding statue/pavilion.
for i in range(4):add(0,-72+i*1.5,2.8,36,1.8,.5+i*.65)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
