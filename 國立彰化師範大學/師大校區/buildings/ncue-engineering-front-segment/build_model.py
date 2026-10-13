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
# College of Engineering / former Comprehensive Teaching Building.
# Observed principal facade segment, including lower platform and right-hand return.
add(0,0,0,150,69,3)
# Main screen-fronted academic bar, cut at a deliberately limited 28mm depth.
add(-17,3,3,100,28,86)
# Distinctive tall folded glass/stair core and framed wall to its right.
add(45,6,3,27,33,93)
# Lower right return visible behind the main facade is included for massing only.
add(63,20,3,17,28,76)
# Deep six-storey sunshade screen with unequal fin density retained.
for row,z in enumerate([20,31,42,53,64,75]):
 for col,x in enumerate([-60,-47,-34,-21,-8,5,18]):
  cut(x,-11.6,z,11,5.2,8)
  # Window frame at back of recess; thick real vertical shade fins at front.
  details.append(box(x,-10.5,z,1.1,4.2,8))
  # Alternating asymmetric clusters capture the original facade's louver rhythm.
  for dx in ([-4,-2.0,2.5] if (row+col)%3==0 else [-4,-2.0]):
   details.append(box(x+dx,-14.5,z,1.1,6,8))
 for x in [-66.5,-53.5,-40.5,-27.5,-14.5,-1.5,11.5,24.5]:add(x,-13,z-1,1.5,5.5,10)
 add(-20,-13,z-1.2,96,6,1.4)
# Top recessed ribbon and raised horizontal roof visor.
for x in [-57,-44,-31,-18,-5,8,21]:cut(x,-11.5,86,10,3,2.3)
add(-19,-13.5,89,102,8,1.6)
# A solid-backed screen rhythm at the top rather than a fragile standalone railing.
for x in range(-63,25,4):add(x,-13,83,1.1,4,4)
# Double-recessed folded curtain wall, observed in architect MG_3730 photograph.
# Front is -Y. The profile moves inward (+Y) twice as it rises, then returns.
# Exact depth is NOT surveyed: 4.2 mm is a legible miniature estimate.
# Shared profile drives glass AND mullions, so this is genuine solid curvature.
GLASS_PROFILE=[(17,-12.6),(24,-12.6),(27,-12.3),(30,-11.0),
 (33,-9.1),(36,-8.4),(43,-8.4),(47,-9.0),(50,-11.6),
 (53,-12.6),(56,-12.6),(59,-12.0),(62,-10.1),(65,-8.4),
 (72,-8.4),(79,-8.8),(85,-10.1),(89,-11.0)]
HORIZONTAL_RIB_Z=[18,26.5,35,43.5,52,60.5,69,77.5,87.5]
# One explicitly triangulated front surface avoids coplanar Boolean seams between
# curved glazing and its own ribs. Ribs have 1.1 mm flat tops and .3 mm shoulders.
from manifold3d import Mesh
rib_x=[30.9,36.3,41.7,47.1]
xs=sorted(set([30.0,48.0]+[v+d for v in rib_x for d in [-.85,-.55,.55,.85]]))
zs=sorted(set([z for z,y in GLASS_PROFILE]+[v+d for v in HORIZONTAL_RIB_Z for d in [-.3,0,1.1,1.4]]))
zs=[z for z in zs if 17<=z<=89]
def strength(v,centers):
 return max([max(0,min(1,(.85-abs(v-c))/.3)) for c in centers])
verts=[]
for back in [False,True]:
 for z in zs:
  for x in xs:
   y=float(np.interp(z,[q[0] for q in GLASS_PROFILE],[q[1] for q in GLASS_PROFILE]))
   relief=max(strength(x,rib_x),strength(z,[q+.55 for q in HORIZONTAL_RIB_Z]))
   verts.append([x,10.5 if back else y-1.4*relief,z])
nx=len(xs);nz=len(zs);n=nx*nz;faces=[]
for j in range(nz-1):
 for i in range(nx-1):
  a=j*nx+i;b=a+1;c=b+nx;d=a+nx
  faces += [[a,b,c],[a,c,d],[a+n,c+n,b+n],[a+n,d+n,c+n]]
boundary=list(range(nx))+[j*nx+nx-1 for j in range(1,nz)]+[i+(nz-1)*nx for i in range(nx-2,-1,-1)]+[j*nx for j in range(nz-2,0,-1)]
for a,b in zip(boundary,boundary[1:]+boundary[:1]):faces += [[a,b+n,b],[a,a+n,b+n]]
glass=Manifold(Mesh(np.asarray(verts,dtype=np.float32),np.asarray(faces,dtype=np.uint32)))
assert glass.status().name=='NoError' and glass.volume()>0
cut(39,-4,17,17.4,29,72)
details.append(glass)
# Characteristic open rectangular slot in tower's upper right, genuinely through.
cut(52,6,82,5,38,10)
# Four rows of paired windows on the tan right facade.
for z in [23,35,47,59,71]:
 for x in [49,56]:cut(x,-11.1,z,4.6,3.2,7)
# Lower base and a sloping stair flank from official architect photos.
add(-22,-12.5,3,92,6,16)
for i in range(12):add(-58+i*4.4,-17.2,2.8,4.6,8,.8+i*1.17)
# Entrance is recess behind projecting lobby frame and canopy.
cut(38,-11.1,3,20,5,11)
add(39,-17,14,25,12,1.6)
for x in [29,39,49]:add(x,-16,14,1.3,13,1.8)
# Squat rooftop boxes documented in the elevated photograph.
add(-54,5,89,24,20,6)
add(40,8,95,22,20,4)
add(66,20,78,12,18,4)
# Right visible return fenestration, other closure planes intentionally plain.
for z in [20,31,42,53,64]:
 for y in [14,24]:cut(71.5,y,z,3.5,6,7)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
