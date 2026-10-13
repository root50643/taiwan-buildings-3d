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
# A01 administration centre. Exterior shell estimated from official aerial and front photographs.
# Model coordinate front=-Y; all dimensions mm. Independent miniature scale.
add(0,0,0,150,135,3)
# Four-storey side wings; rear bar encloses a genuinely open central rear courtyard.
for x in [-47,47]:add(x,2,2.8,38,86,43.2)
add(0,36,2.8,132,20,43.2)
# Central entrance bar has a deep, two-level column porch and upper enclosed storey.
add(0,-.5,2.8,59,15,33.5)
add(0,-9,31.5,60,28,14.5)
# Aerial shows a white roof court, not evidence of a void to ground. Fill the lower body.
add(0,17,2.8,59,24,43.2)
# Set-back U-shaped upper window band above the lower side-wing roofs.
add(0,38,45.6,90,16,12.4)
for xx in [-38,38]:add(xx,24,45.6,14,42,12.4)
for xx in range(-24,25,6):cut(xx,30,48,4.2,3,8)
for xx in [-38,38]:
 for xxx in [xx-3,xx+3]:cut(xxx,3,48,4.2,3,8)
for side in [-1,1]:
 for yy in [10,18,26,34]:cut(side*45,yy,48,3,4.8,8)
# Large stepped forecourt climbs to the main entry; lateral access remains below.
for i in range(12):add(0,-58+i*3,2.8,66,3.3,1+i*.9)
for x in [-32.5,32.5]:
 for i in range(6):add(x,-56+i*6,3.2,2.5,6.2,3+i*1.8)
# Main colonnade, genuinely open between four tall square piers.
for x in [-26,-9,9,26]:add(x,-20,14.4,2.2,2.2,17.3)
# Entry glazing recesses behind the colonnade.
for x in [-22,-11,0,11,22]:cut(x,-8,15,8,3.2,13)
for x in [-22,-11,11,22]:cut(x,-8,4,8,3.1,8)
# Front wings: broad two-storey recess with double-height projecting piers.
for x in [-47,47]:
 cut(x,-41,3.1,34,8,22)
 for xx in [x-15,x-7.5,x,x+7.5,x+15]:details.append(box(xx,-43.4,3,1.8,2.8,23))
 # visible glazing set back from the free-standing piers, two levels
 for xx in [x-11,x-3.6,x+3.6,x+11]:
  for z in [5,16]:cut(xx,-37.1,z,5.1,2.8,7)
 # two upper storeys have separate punched windows and slender vertical fins
 for xx in [x-13.5,x-6.7,x,x+6.7,x+13.5]:
  for z in [27,37]:cut(xx,-41.4,z,4.9,3.2,6.2)
  add(xx-3,-42,26.6,1.2,2.0,17.5)
 add(x,-42,25,38.8,2.6,1.3)
# Central upper facade: dense vertical window rhythm, with solid end piers.
for x in range(-24,25,6):
 cut(x,-23,34.5,4.3,3.2,8)
 add(x-2.8,-24,33.8,1.0,2.0,10)
# Side elevations follow the documented oblique aerial rhythm, not assumed interiors.
for side in [-1,1]:
 for y in [-32,-21,-10,1,12,23,34]:
  for z in [6,17,28,38]:cut(side*66,y,z,3.2,7,6)
 # Lower central body is roofed; do not cut hypothetical hidden interior windows.
# Rear elevation not clearly photographed: keep plain, except footprint/eave.
# Low roof parapets and documented aerial photovoltaic areas, fused relief rather than floating panels.
for x in [-47,47]:
 add(x,2,45.6,38.5,86.5,1.3)
 for xx in [x-12,x-4,x+4,x+12]:
  for yy in [-30,-20,-10,0,10,20,30]:
   if abs(xx)>46 or yy<0:add(xx,yy,46.6,6.5,8.5,.9)
add(0,36,45.6,132.5,20.5,1.3)
add(0,-9,45.6,60.5,28.5,1.3)
# U-shaped upper roof perimeter, with the open rooftop court between its returns.
add(0,38,57.6,91,16.8,1.3)
for xx in [-38,38]:add(xx,24,57.6,14.8,42.8,1.3)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
