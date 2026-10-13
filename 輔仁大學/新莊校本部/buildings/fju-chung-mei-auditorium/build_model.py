"""Photo-derived public exterior study. Millimetres; dimensions are visual estimates.
Run with Python 3.12 and requirements.txt. No survey or interior data used.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection, Mesh64
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
# Circular hall, radial scalloped shell roof, upper lantern and front grand stair.
add(0,0,0,150,150,3)
parts.append(Manifold.cylinder(24,60.5,60.5,circular_segments=280).translate((0,6,2.8)))
# Recessed lower perimeter arcade, backing remains connected to the main hall.
for i in range(35):
 a=i*360/35
 if min(abs(a),abs(a-360))<32:continue
 cuts.append(box(0,-60,3,7,8,5).rotate((0,0,a)).translate((0,6,0)))
# Three front doors retain the high solid stage wall and visible arch shape.
for x in [-18,0,18]:arch_cut(x,-53.6,12,9,10.5,8)
# Shallow lattice facade perforations are deliberately enlarged, backed recesses.
for i in range(70):
 a=i*360/70
 if min(abs(a),abs(a-360))<26:continue
 for z in [13,16,19]:
  cuts.append(box(0,-60.3,z,1.4,2.0,1.4).rotate((0,0,a)).translate((0,6,0)))
# Top horizontal window band below roof, vertical piers at radial joints.
for i in range(70):
 a=i*360/70
 cuts.append(box(0,-60.4,23,3.7,2.6,3.0).rotate((0,0,a)).translate((0,6,0)))
parts.append(Manifold.cylinder(1.4,62,62,circular_segments=280).translate((0,6,26)))
# 70 radial barrel-like scallops. Explicit surface, not an imaginary smooth dome.
N=560; radii=[0.01,19,25,35,45,55,65];v=[]
for r in radii:
 for j in range(N):
  a=2*math.pi*j/N;t=max(0,(r-19)/46)
  z=41-13*(t**.8)+2.0*abs(math.sin(35*a))*t
  v.append((r*math.cos(a),6+r*math.sin(a),z))
# underside closes into the hall; external eave has a printable thickness of 1.4mm
for j in range(N):
 a=2*math.pi*j/N;v.append((65*math.cos(a),6+65*math.sin(a),26.6))
v.append((0,6,26.6));center=len(v)-1;f=[]
for k in range(len(radii)-1):
 for j in range(N):
  q=(j+1)%N;a=k*N+j;b=k*N+q;c=(k+1)*N+j;d=(k+1)*N+q
  f.extend([(a,c,d),(a,d,b)])
# tiny central cap
for j in range(1,N-1):f.append((0,j,j+1))
for j in range(N):
 q=(j+1)%N;a=(len(radii)-1)*N+j;b=(len(radii)-1)*N+q;c=len(radii)*N+j;d=len(radii)*N+q
 f.extend([(a,c,d),(a,d,b),(center,d,c)])
parts.append(Manifold(Mesh64(np.asarray(v,float),np.asarray(f,dtype=np.uint64))))
# Upper clerestory and shallow conical cap; ventilation recesses not hidden hollow shell.
parts.append(Manifold.cylinder(4.7,20,20,circular_segments=140).translate((0,6,40.7)))
for i in range(35):cuts.append(box(0,-20,42,2.2,2.1,2.1).rotate((0,0,i*360/35)).translate((0,6,0)))
parts.append(Manifold.cylinder(3.5,21.6,.5,circular_segments=140).translate((0,6,45)))
for i in range(10):add(0,-72+i*2.3,2.8,83,2.7,.9+i*.85)
# central sloped dedication strip is a solid ramp, fused to the stair body.
# The dedication text is omitted at this scale.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
