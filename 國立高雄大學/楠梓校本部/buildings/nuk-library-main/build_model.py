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
# Library and Information Building MAIN BLOCK only, excluding the low
# auditorium/entrance pavilion and long approach bridge. x width; negative y front.
# Ratios are public-photo estimates; this is not a survey reconstruction.
add(0,0,0,150,112,3)
# White, vertically slit semi-basement plinth.
add(0,0,2.8,126,82,8.6)
# Main brick-clad rectangular body and deeply shadowed glass crown.
add(0,0,10.9,126,82,34.2)
add(0,0,44.8,123.5,79.5,6.3)
add(0,0,50.7,133,89,1.45)
# Opposing long faces from c01-3 versus c01-2/4: the screen and
# 2-versus-4 window groups are offset in opposite apparent directions.
for side in [-1,1]:
 y=side*41
 cx=-13 # Same physical offset; rear camera reverses left/right.
 # Six narrow tall glazing groups flanking the projection, true recessed reveals.
 bays=[(-53,7.4),(-40,7.4),(19,7.4),(31,7.4),(43,7.4),(55,7.4)]
 # Rear view therefore reads 4 groups left and 2 right.
 for x,w in bays:
  cut(x,y,12,w,3.8,31)
  # Backed mullion and floor rails all >=1 mm, joined into the deep recess walls.
  for z in [18,24,30,36]:details.append(box(x,side*40.05,z,w,2.2,1.0))
  details.append(box(x,side*40.2,12,1.0,2.2,31))
 # Large elevated panel; portico remains visibly deep underneath.
 cut(cx,y,11,31,11,13)
 for x in [cx-12,cx,cx+12]:details.append(box(x,side*42.0,10.7,2.2,2.6,14.5))
 # Panel sits in front of brick and masks its facade, attached by overlap.
 add(cx,side*42.0,24,37.5,3.5,18.5)
 for z in [25.8,28.4,31.0,33.6,36.2,38.8,41.0]:cut(cx,side*43.75,z,35.5,.65,.55)
 for x in [cx-14,cx-7,cx,cx+7,cx+14]:cut(x,side*43.75,25,.5,.65,16.5)
 # Short narrow brick clerestory slot row above the big screen.
 for x in range(int(cx-16),int(cx+17),3):cut(x,y,43.2,1.5,3.4,6.5)
 # Exposed metal-screen crown on both sides, backed chunky rails for the miniature.
 for x,w in [(-48,28),(46,31)]:
  # Keep physical crown bays aligned with the same x offset.
  cut(x,side*40,45.3,w,2.3,4.8)
  for xx in range(int(x-w/2+1),int(x+w/2),6):details.append(box(xx,side*40,45.1,1.1,2,5.4))
  for z in [46.1,48.4]:details.append(box(x,side*40,z,w,2,1.0))
# Opposite long face has a visible white slotted plinth instead of the stair apron.
for x in range(11,60,4):cut(x,41,4.2,1.7,2.5,5.2)
# Side facades: broad full-height glazed curtains plus white slit basement.
for sx in [-1,1]:
 for y in [-29,-21,-13,-5,3,11,19,27]:
  cut(sx*63,y,12,3.8,5.1,31)
  for z in [18,24,30,36]:details.append(box(sx*62.1,y,z,2.2,5.1,1.0))
  details.append(box(sx*62.2,y,12,2.2,1.0,31))
 for y in range(-36,38,4):cut(sx*63,y,4.2,2.5,1.7,5.2)
 cut(sx*62,0,45.3,2.4,73,4.8)
 for y in range(-36,38,6):details.append(box(sx*62,y,45.1,2,1.1,5.4))
 for z in [46.1,48.4]:details.append(box(sx*62,0,z,2,73,1.0))
# Front approach deck is a cropped main-block apron, not the omitted long bridge.
add(0,-45,9.2,133,8,1.7)
for x in [-59,-39,-19,1,21,41,61]:add(x,-45,2.8,2.4,3,6.6)
# Main steps physically connect the miniature base to the main-block entry apron.
for i in range(7):add(-13,-53+i*1.3,2.8,35,1.6,.98*(i+1))
# Discreet roof plant volumes observed in the 2016 elevated photograph.
add(-18,14,51.8,16,12,3.2)
add(40,19,51.8,8,8,2.3)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
