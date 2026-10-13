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

# Long administration complex with open middle court and rear twin towers.
# Pre-repair exterior, no claim to represent temporary 2026 construction conditions.
add(0,0,0,98,150,3)
# Seven setback tiers form the visually pyramidal front block.
levels=[(78,48,3,13),(74,46,15,10),(65,42,25,10),(56,37,35,10),(47,32,45,10),(39,27,55,10),(31,23,65,10)]
parts.append(CrossSection.square((78,48),center=True).extrude(60,scale_top=(31/78,23/48)).translate((0,-37,15)))
for w,d,z,h in levels:
 if z==3:add(0,-37,z,w,d,h)
 add(0,-37,z+h-1,w+3,d+2,1.8)
 for x in [-w*.33,0,w*.33]:
  cut(x,-37-d/2,z+2.1,w*.22,7,5.0)
  if z>15:details.append(box(x,-37-d/2,z+2.1,1.4,3,5))
 for side in [-1,1]:
  for y in [-d*.3,0,d*.3]:cut(side*w/2,-37+y,z+2.1,7,d*.20,5)
# Broad layered crown with recessed shadow lines.
for k in range(4):add(0,-37,75+k*1.5,35+k*3.2,26+k*2.8,1.7)
# Fluid cloud-wall buttresses reconstructed as solid profiled ribbons in front.
# The curving outline is deliberately coarser and thicker for miniature printing.
for side in [-1,1]:
 for xx,zmax in [(side*13,71),(side*28,49)]:
  front=[]
  for t in np.linspace(0,1,28):
   z=16+(zmax-16)*t
   yy=-68+13*t+2.0*math.sin(t*math.pi*2)
   if abs(xx)>20:yy+=6.0
   front.append((yy,z))
  poly=front+[(yy+12,z) for yy,z in front[::-1]]
  area=sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))
  if area<0:poly=poly[::-1]
  (parts if abs(xx)>20 else details).append(CrossSection([poly]).extrude(5.5).rotate((90,0,90)).translate((xx-2.75,0,0)))
# Side porch towers and heavy caps by the lower entrance.
for x in [-40,40]:
 add(x,-52,3,7,9,33)
 cut(x,-56,13,3,3,13)
 for k in range(3):add(x,-52,34+k*1.5,11+k*2.5,12+k*2.3,1.6)
# Cloud-shaped front porte-cochere retains three real openings.
add(0,-66,23,48,14,4)
# Side cloud-wall arches: the visible side is a genuine pointed, scalloped opening.
for x in [-21,21]:
 add(x,-66,3,4.2,18,22)
 yz=[(-72,2.9),(-60,2.9),(-60,12),(-61,12.5),(-61,15),(-62.5,16),(-63,18),(-64.8,19.5),(-66,21),(-67.2,19.5),(-69,18),(-69.5,16),(-71,15),(-71,12.5),(-72,12)]
 yz=[(y-1.3,z) for y,z in yz]
 cuts.append(CrossSection([yz]).extrude(6).rotate((90,0,90)).translate((x-3,0,0)))
# Front frame has curved haunches under a broad near-flat crown, not a solid doorway.
add(0,-73,3,46,4,22)
front_arch=[(-17,2.9),(17,2.9),(17,14),(16.8,16),(16,18),(14.5,20),(12,21),(-12,21),(-14.5,20),(-16,18),(-16.8,16),(-17,14)]
cuts.append(profile(front_arch,-73,6))
for k in range(3):add(0,-66,26+k*1.5,47+k*2,14+k,1.5)
# Long low lateral colonnades surround an entirely open courtyard.
for x in [-34,34]:
 add(x,19,22,10,74,3)
 for y in [-13,0,13,26,39,51]:add(x,y,2.8,3.5,4,20)
 add(x,19,3,10,74,2)
# Rear shallow cross-block, twin tall pierced belfry/drum towers.
add(0,56,3,68,18,26)
for x in [-26,26]:
 add(x,55,3,11,15,64)
 # Small lower slots; upper tower is open between four substantial corner piers.
 cut(x,55,15,4,19,9)
 for z,h in [(34,20.5),(57,7.5)]:
  cut(x,55,z,7,19,h)
  cut(x,55,z,15,10,h)
 for z in [29,66]:
  for k in range(3):add(x,55,z+k*1.5,15+k*2.5,19+k*2.5,1.6)
for x in [-14,0,14]:
 cut(x,66,8,9,3.5,13)
for z in [19,25]:add(0,56,z,68,21,1.6)
# Court circular pavement is flat relief, connected to base; central court remains roofless.
column(0,20,2.9,23,1.1)
# Shallow steps in front, not landscape trees or adjacent campus buildings.
for i in range(4):add(0,-74+i*1.3,2.8,43,1.5,.5*(i+1))
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert str(solid.status())=='Error.NoError' and solid.volume()>0 and len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
