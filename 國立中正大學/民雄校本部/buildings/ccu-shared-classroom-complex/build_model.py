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
def gable(x,y,z,w,d,h):parts.append(profile([(x-w/2,z),(x+w/2,z),(x+.55,z+h),(x-.55,z+h)],y,d))
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
# 114 disaster plans B1-5F and official tour photographs; exterior approximation.
# Front is -Y. Twin articulated wings; open central quadrangle, no infilled slab.
add(0,0,0,150,94,3)
for x in [-43,43]:
 # Four-storey front/rear bars and connecting lateral spine; pronounced recesses.
 add(x,-27,2.8,54,18,40)
 add(x,26,2.8,54,18,40)
 add(x,0,2.8,20,54,40)
 # Five-storey raised middle sections retreat laterally from four-storey shoulders.
 for y in [-27,26]:
  add(x,y,42.5,29,18,9.5)
  gable(x,y,51.8,31,20,4.8)
  # Broad shoulder roofs are real sloping solid masses.
  for dx in [-21,21]:gable(x+dx,y,42.4,15,20,2.8)
  add(x,y-9.3,42.35,55,1.4,1.1)
 # Roof of the connecting lateral spine is below raised gables.
 add(x,0,42.2,21,36,1.3)
 # Front grouping: seven groups, separated by major solid pilasters.
 for z in [6,16,26,36]:
  for dx in [-24,-18,-10.5,-3.5,3.5,10.5,18,24]:
   cut(x+dx,-35.6,z,4.7,1.6,6.3)
   details.append(box(x+dx,-35.25,z,1.2,1.7,6.3))
   details.append(box(x+dx,-35.25,z+4.3,4.7,1.7,1.2))
  add(x,-35.8,z-1.5,54.6,.9,1.15)
 # Fifth-storey two broad glazed flanking groups with central solid brick panel.
 for dx in [-10.5,3.5,10.5]:
  cut(x+dx,-35.7,44.0,5.4,1.7,6.1)
  details.append(box(x+dx,-35.25,44,1.3,1.7,6.1))
  details.append(box(x+dx,-35.25,46.5,5.4,1.7,1.2))
 # Shallow curved cap above the two central bays, attached to gable backing.
 arcpts=[(x-7.2,50.0),(x+7.2,50.0)]+[(x+7.2*math.cos(a),50.0+2.5*math.sin(a)) for a in np.linspace(0,math.pi,25)]
 details.append(profile(arcpts,-35.95,1.3))
 for dx in [-14,0,14]:add(x+dx,-35.5,24.5,2.2,1.4,26.8)
 # Side photograph: recessed bays and strong floor bands on outward-facing spine.
 outer=x+(-10 if x<0 else 10)
 for z in [6,16,26,36]:
  for y in [-13,-4,5,14]:cut(outer,y,z,1.6,5.8,6.3)
 # Inward spine openings are supported by entrance photographs; shallow relief.
 inner=x+(10 if x<0 else -10)
 for z in [6,16,26,36]:
  for y in [-12,0,12]:cut(inner,y,z,1.6,7.0,6.3)
# Central rear classroom / circulation connector visible behind entrance, lower roof.
add(0,26,2.8,34,18,30)
gable(0,26,32.5,36,20,4.5)
# Rear facade unknown: plain mass and roof, intentionally no mirrored window array.
# Central foreground portal has four robust piers and a genuinely deep open passage.
for x in [-13.5,13.5]:
 for y in [-32,-21]:add(x,y,2.8,3.4,3.4,22.6)
add(0,-26.5,24.0,31,15,2.4)
gable(0,-26.5,26.2,32,16,4.1)
# Two-storey lateral connector beams meet the wings behind the entrance columns.
for x in [-21,21]:
 add(x,-21,15.5,17,4.0,3)
 for xx in [x-6,x+6]:add(xx,-21,2.8,2.2,3.0,13.5)
# Broad entrance steps are fused to the common base.
for i in range(3):add(0,-42+i*2,2.8,31,2.8,.55*(i+1))
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
# Ground-plan aspect ratio from 114 floor diagrams: width/depth about 3:1.
solid=solid.scale((1,.64,.75))
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
