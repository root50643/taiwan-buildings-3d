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
# A administration + H library, one connected courtyard group, two named buildings.
add(0,0,0,142,150,3)
# Opposed bars and linking wings. A/H plans explicitly mark reciprocal connections.
add(0,-53,2.8,130,24,69)
add(0,45,2.8,130,40,69)
for x in [-56,56]:add(x,-8,2.8,18,68,69)
# Genuine open court x +/-47, y -41..25. No roof or infill in courtyard.
# South administrative elevation: ten main bays, five broad upper window rows.
for x in [-45,-35,-25,-15,-5,5,15,25,35,45]:
 for z in [20,29,38,47,56]:
  cut(x,-65,z,8.1,4.4,5.5)
  details.append(box(x,-65,z+4.0,8.1,2.5,1.0))
# North library elevation: seven wider bays, outer two narrower.
for x in [-48,-32,-16,0,16,32,48]:
 for z in [20,29,38,47,56]:
  w=11 if abs(x)==48 else 13.5
  cut(x,65,z,w,4.4,5.5)
  details.append(box(x,65,z+4.0,w,2.5,1.0))
# Distinct close-spaced top ventilation slot band, not an extra generic floor.
for y in [-65,65]:
 for x in [-51+3*i for i in range(35)]:cut(x,y,65,1.6,4,4.5)
 for x in [-61,61]:
  for z in [47,56,65]:
   for xx in [x-1.2,x+1.2]:cut(xx,y,z,1.4,4,4)
# Ground flank glazing, keep central ceremonial portals separate.
for y in [-65,65]:
 for x in [-51,-41,41,51]:cut(x,y,4,8,4.2,11)
# Both low pale entry frames use flattened arch openings, not a round full arch.
# Profile extrusions allow real recessed passage to backed doors.
for y in [-67.6,67.6]:
 add(0,y,3,76,7.2,16)
 pts=[(-18,3),(18,3),(18,11.4),(16,13.1),(11,14.2),(0,15),(-11,14.2),(-16,13.1),(-18,11.4)]
 cuts.append(profile(pts,y,8.4))
 # Recessed frame/opening terminates against main facade, no invented through-passage.
 for x in [-10,0,10]:cut(x,(-65 if y<0 else 65),4,7,4,9)
# Admin entry stair is broader/deeper than the library threshold in sources.
for i in range(5):add(0,-73+i*1.4,2.8,72,2.0,.6*(i+1))
for i in range(3):add(0,72-i*1.2,2.8,67,1.8,.6*(i+1))
# Observed library-side return only; unobserved linked wings stay unfenestrated.
for y in [34,52]:
 for z in [20,29,38,47,56]:cut(-65,y,z,4,12,5.5)
# Flat roof outlines. Newly recorded waterproofing does not specify a new roof shape.
for y in [-65,65]:add(0,y,71.2,131,1.6,1.5)
for x in [-65,65]:add(x,0,71.2,1.6,131,1.5)
for y in [-41,25]:add(0,y,71.2,95,1.6,1.5)
for x in [-47,47]:add(x,-8,71.2,1.6,67,1.5)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
