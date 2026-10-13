"""NTSU Arena, photo-derived exterior approximation; mm. Self-built geometry.
48 V support bays per architect's description, shallow curved roof and recessed doors.
Unknown rear service annexes and fine mullions omitted. Not a surveyed reconstruction.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
P=[]; C=[]
def cyl(r,z,h,n=192): return Manifold.cylinder(h,r,r,circular_segments=n).translate((0,0,z))
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def radial_box(theta,r,z,w,d,h):return box(0,-r,z,w,d,h).rotate((0,0,theta))
def rod(a,b,w):
 a=np.array(a);b=np.array(b);v=b-a;L=np.linalg.norm(v);v=v/L
 axis=np.cross([0,0,1],v);ang=math.degrees(math.acos(v[2]))
 # manifold rotation matrix from trimesh only; keep square diagonal section.
 T=trimesh.transformations.rotation_matrix(math.radians(ang),axis)
 T[:3,3]=a
 return Manifold.cube((w,w,L)).translate((-w/2,-w/2,0)).transform(T[:3])
P=[box(0,0,0,150,150,3),cyl(68,2.8,7.2),cyl(60.8,8.8,26.5),cyl(66,33.7,4.2)]
# Photographs show an unbroken base podium, deep entrances, glazing recessed behind Vs.
# Exact service/back door patterns lack evidence: only front arc gets entry detail.
for th in [-48,-24,0,24,48]:
 C.append(radial_box(th,66.5,3.1,14,8,4.8))
 # recessed solid door face intentionally stays behind a wide portal.
 P.append(radial_box(th,61.6,3,12.5,1.3,5.1))
# Main structural rhythm is supported by architect text; no invented rear windows.
for k in range(48):
 a=2*math.pi*k/48; half=math.pi/48
 def pt(t,z):return [64.3*math.sin(t),-64.3*math.cos(t),z]
 for side in [-1,1]:P.append(rod(pt(a,9.2),pt(a+side*half,34.6),1.65))
# Backed broad glazing bands only on observed front hemisphere, not tiny free mullions.
for z in [14,19,24,29]:
 band=cyl(61.2,z,.95)-cyl(60.35,z-.1,1.2)
 P.append(band ^ box(0,-43,z-.2,140,86,1.5))
# Roof is a low spherical cap, section consistent with original published cross-section.
# r=66, rise=15; top truncated to a printable >0.8 mm plateau, no sharp sphere tip.
R=(66*66+15*15)/(2*15)
profile=[(0,37.6),(66,37.6)]
for r in np.linspace(66,1.0,60)[1:]:profile.append((float(r),37.6+math.sqrt(R*R-r*r)-(R-15)))
profile += [(0,52.59)]
P.append(CrossSection([profile]).revolve(circular_segments=192))
# Roof octagon expressed as a 2mm wide, approximately 0.5–0.8mm deep backed engraved seam.
# The aerial photo shows roof lines, not a freestanding fence; groove avoids sliver rims.
roof=P[-1]
octagonal_band=cyl(18,51.05,8,8)-cyl(16,50.5,10,8)
C.append(octagonal_band)
solid=P[0]
for p in P[1:]:solid=solid+p
for c in C:solid=solid-c
assert len(solid.decompose())==1
m=solid.simplify(.0001).to_mesh64(); mesh=trimesh.Trimesh(np.array(m.vert_properties,dtype=np.float32)[:,:3],np.array(m.tri_verts),process=True)
# Canonicalize signed numerical zero in source coordinates before export.
verts=mesh.vertices.copy();verts[abs(verts)<.000005]=0.0
mesh=trimesh.Trimesh(verts,mesh.faces,process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,len(mesh.faces),mesh.is_watertight)
