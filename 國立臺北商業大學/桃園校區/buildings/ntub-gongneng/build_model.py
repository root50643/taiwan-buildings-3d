'''國立臺北商業大學公能樓：官方多向實拍之外觀量體近似。非測繪。'''
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def cyl_between(a,b,r):
 v=np.array(b)-a; L=float(np.linalg.norm(v));z=v/L
 xx=np.cross([0,1,0],z);xx/=np.linalg.norm(xx);yy=np.cross(z,xx)
 T=np.column_stack([xx,yy,z,np.array(a)])
 return Manifold.cylinder(L,r,r,circular_segments=12).transform(T)
# Main footprint identified on official campus map. Scale is photograph-estimated.
add(0,0,0,150,150,3)
add(0,4,2.8,127,117,3.6)
add(0,4,6,124,112,34)
add(0,4,39.5,106,112,13.5)
# Roof eaves, modest sloped side cap approximated; exact pitch not surveyed.
add(0,4,52,110,116,2)
add(0,4,39.5,129,85,1.8)
# Four corner stair volumes; northwest detailed by env6; northeast silhouette only.
for x in [-52,52]:
 for y in [-42,50]:
  add(x,y,5.8,21,25,62)
  add(x,y,67,23.5,27.5,1.7)
# Tall continuous corner glazing: shallow recess + narrow mullions flush to wall,
# never use many huge vertical structural columns in curtain walls.
for x,y,faces in [(-52,-42,['s','w']),(52,-42,['s']),(-52,50,['n','w'])]:
 for face in faces:
  if face in ['s','n']:
   facey=y+(-12.5 if face=='s' else 12.5)
   cut(x,facey,7.2,15.4,3,48)
   for z in np.arange(10.8,54,4):details.append(box(x,facey+(1 if face=='s' else -1),z,15.7,1.4,.8))
   details.append(box(x,facey+(1 if face=='s' else -1),7,0.9,1.4,48.5))
  else:
   cut(x-10.5,y,7.2,3,19,48)
   for z in np.arange(10.8,54,4):details.append(box(x-9.5,y,z,1.4,19.3,.8))
   details.append(box(x-9.5,y,7,1.4,.9,48.5))
# Southern parapets have groups of three narrow slots, not full-height windows.
for x in [-52,52]:
 for dx in [-4,0,4]:cut(x+dx,-55,59,1.5,3,6)
# NW upper tower band, evidenced by reverse-side photograph.
cut(-52,62.5,58.5,15.5,2.8,3.2);cut(-62.5,50,58.5,2.8,19,3.2)
# South upper loggia has 9 open bays and substantial piers. Preserve real depth.
cut(0,-50,40,83,9,11.5)
for x in np.linspace(-40,40,10):details.append(box(float(x),-51.5,39.8,1.9,5,12.5))
add(0,-51,39.4,84,3.3,2.0)
add(0,-51,51.5,86,10,2.1)
# North upper loggia as seen at right of reverse photo; same large span, unknown
# small railings omitted rather than invented. Bay rhythm approximate.
cut(0,59,40,83,8,11.5)
for x in np.linspace(-40,40,10):details.append(box(float(x),60.3,39.8,1.9,5,12.5))
add(0,60,39.4,84,3.3,2.0);add(0,60,51.5,86,9,2.1)
# South second level: five narrow windows per side of central two-storey portal.
for side in [-1,1]:
 for x in [20,25,30,35,40]:cut(side*x,-52,26,2.5,2.6,9)
# Ground porticoes at both sides retain deep entry shadows and a real open recess.
for side in [-1,1]:
 cut(side*28,-52,6.2,24,8,15)
 for x in [20,29,38]:cut(side*x,-47.5,8,5.2,2.2,8)
# Central glazed portal with inset wall; projected glass canopy and structural stays.
cut(0,-52,6.2,30,5,30)
for x in [-13,-6.5,0,6.5,13]:details.append(box(x,-50.4,6.2,1.0,1.7,27.8))
for z in [16,24]:details.append(box(0,-50.4,z,29,1.7,1.0))
for x in [-17,17]:add(x,-52,6,2.7,5.2,32)
add(0,-52,36.2,37,5.2,2.3)
add(0,-60.2,22.8,42,18.5,1.9)
# Two stays modeled thickened and joined at both ends, no zero-thickness contacts.
for x in [-12,12]:details.append(cyl_between((x,-52.3,35),(x,-68.5,23.5),.85))
for i in range(4):add(0,-71+i*1.8,2.8,45,2.6,.85*(i+1))
# North middle-level loggia, a deep recess not a black painted rectangle.
cut(0,60,24,23,12,14)
add(0,60,23.5,24,3,2.3)
for side in [-1,1]:
 for x in [20,26,32,38]:cut(side*x,60,27,2.8,2.8,9)
 cut(side*28,60,6.2,24,7,15)
 for x in [20,29,38]:cut(side*x,56,8,5.2,2.4,8)
# West double-height window rows. Distinct nine narrow bays per floor.
for y in np.linspace(-28,37,9):
 for z in [9,29]:cut(-62,y,z,2.8,4.5,15)
 # Subtle frame is backed, not a separate pilaster.
for y in np.linspace(-25,34,8):cut(-53,y,46,2.8,6,4)
# East side is unverified and deliberately unornamented; do not mirror west windows.
# Central rooftop PV field visible in 111-113 (2022-2024) school report.
# Panel count/layout/tilt are intentionally coarse approximations, not 2026 survey.
# Broad PV panel field, not raised fins. Source is the aerial image with the
# paired slot-parapet towers (Gongneng), not the image carrying the NTUB tower sign.
# Footprint is central roof only; exact surveyed edges and individual panel count
# are unavailable from the 251x188 source. 4x5 groups are a print-scale abstraction.
add(0,6,53.6,70,71,1.5)
for x in [-17.5,0,17.5]:cut(x,6,54.9,.65,72,1)
for y in [-15.3,-1.1,13.1,27.3]:cut(0,y,54.9,71,.65,1)
# Visible roof service housing, kept modest; exact rear equipment unknown.
add(21,22,53.8,13,12,7)
solid=parts[0]
for p in parts[1:]:solid+=p
for c in cuts:solid-=c
for p in details:solid+=p
assert len(solid.decompose())==1
# Align the evidenced long-window flank with the reverse-angle photograph.
solid=solid.scale((-1,1,1))
m=solid.simplify(.00001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight)
