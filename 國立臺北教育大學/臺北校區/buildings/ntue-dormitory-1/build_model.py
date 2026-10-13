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
# Dormitory 1: official sawtooth room plan, five floors, distinct central entrance.
VARIANT=1
add(0,0,0,150,76,3)
add(0,0,2.8,135,15,54)
# Six angled bedroom bays per half. Angles and dimensions are plan/photo estimates.
for side in [-1,1]:
 for x in [-56,-48,-40,-32,-24,-16,16,24,32,40,48,56]:
  angle=(-22 if x<0 else 22)*(-side)
  def local(shape):return shape.rotate((0,0,angle)).translate((x,side*16,0))
  parts.append(local(box(0,0,2.8,8.8,24,54)))
  # Deep angled brick blade, thick and genuinely connected, with higher roof tip.
  parts.append(local(box(4.2,0,2.8,2.2,28,57)))
  parts.append(local(box(0,0,56,10,27,2.2)))
  # The highest folded brick cap projects forward above the lower bedroom strips.
  parts.append(local(box(0,side*13.5,48,9.6,7.0,10.2)))
  # No mirrored unseen rear glazing for Dorm I. Dorm II rear photo supports rows.
  visible=(side<0 and (x>=-48 if VARIANT==2 else x>=-40)) or (side>0 and VARIANT==2)
  if visible:
   for z in [7,17,27,37,47]:
    cuts.append(local(box(-.4,side*(15 if z==47 else 12),z,6.2,(8.4 if z==47 else 4.4),(6.5 if z==47 else 5.4))))
    # Fine pane divisions omitted: real major recess stays wider than brick ribs.
# End stairs read as broad near-blank brick ends, not repeated bedroom windows.
for x in [-65,65]:
 add(x,0,2.8,10,49,55.4)
 add(x,0,57.5,11,50,1.5)
# Central shallow fan plan, layered entrance from two exterior photos.
central=CrossSection([[(-11,10),(11,10),(15,-28),(9,-31),(-9,-31),(-15,-28)][::-1]]).extrude(39).translate((0,0,2.8))
parts.append(central)
# Back stair core kept plain when not independently photographed.
add(0,16,2.8,19,26,53)
# Entrance remains a real recessed void with backing glazing.
cut(0,-29,3,18.2,16,12.5)
add(0,-21.5,3,18,3,12)
for x in [-6,0,6]:cut(x,-21,4,4.3,2.8,9.5)
# Two broad upper glazing bands on the central pale projection.
for z in [20,31]:cut(0,-29,z,19,6.2,5.5)
for z in [18,29,40]:add(0,-29,z,28,5,1.6)
# Distinct top brick balcony: wide dark opening bounded by deep angled returns.
add(0,-18,41,29,26,17)
cut(0,-31,45,22,9,8)
add(0,-31,56.4,31,5,1.7)
# Preserve differing observed entrance scale instead of duplicating names only.
if VARIANT==1:
 for x in [-10.5,10.5]:column(x,-29,3,1.3,14)
 add(0,-29,16,26,9,1.8)
else:
 for x in [-11,11]:add(x,-28,3,2.4,7,14)
 add(0,-28,16,27,8,2.2)
 # Dorm II photograph shows pronounced stepped rear roof and framed central stair.
 for z in [18,29,40]:add(0,29,z,21,3,1.8)
 for z in [20,31,42]:cut(0,29,z,14,4,5.8)
for i in range(4):details.append(box(0,-35+i*1.5,2.8,25,2.1,.6*(i+1)))

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
