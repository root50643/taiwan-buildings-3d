"""NTSU photo-derived exterior section, self-built geometry in millimetres.
Unknown back and omitted building extents are plain section cuts, not surveyed facades.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
P=[];C=[];D=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):P.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):C.append(box(x,y,z,w,d,h))
def cyl(x,y,z,r,h):P.append(Manifold.cylinder(h,r,r,circular_segments=32).translate((x,y,z)))
def profile(poly,y,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def arc_strip(ro,ri,cy,z,h,span=42):
 a=np.linspace(-math.radians(span),math.radians(span),65)
 poly=[(ro*math.sin(t),cy-ro*math.cos(t)) for t in a]+[(ri*math.sin(t),cy-ri*math.cos(t)) for t in a[::-1]]
 return CrossSection([poly]).extrude(h).translate((0,0,z))

# Original oblique official photo proves a concave corner, not curved main wings.
# Recent panoramic photo has lens distortion; it supports the surviving round portico only.
add(0,0,0,150,122,3)
# Two facade segments meet at a concave corner. Each side is only a cropped part of the wing.
def wing_part(s):
 # Local x is from concave corner toward outer edge; local y is depth behind facade.
 w=box(36,12,2.8,72,24,92)
 cuts=[]
 for x in [9,23,37,51,65]:
  for row,z in enumerate([8,24,40,56,72,87]):
   if row==5:cuts.append(box(x,0,z,9,4,5))
   else:
    cuts.append(box(x-2.8,0,z,4.4,4,7));cuts.append(box(x+2.8,0,z,4.4,4,7));cuts.append(box(x,0,z+8.5,10,4,2))
 for c in cuts:w=w-c
 if s<0:w=w.mirror((1,0,0)).rotate((0,0,28))
 else:w=w.rotate((0,0,-28))
 return w.translate((0,25,0))
P += [wing_part(-1),wing_part(1)]
add(0,31,2.8,8,13,92)
# Main entrance glazing at the concave corner, recessed behind free curved colonnade.
add(0,20,2.8,60,12,18)
for x in [-22,-11,0,11,22]:cut(x,13,3,8,4,13)
# Arc roof slab/upper parapet supported by six cylindrical columns, open underneath.
P.append(arc_strip(87,79,49,19.15,18.65,42))
P.append(arc_strip(88.5,77.5,49,17.6,2.2,42))
# Open rectangular upper parapet apertures around the curved face.
for a in np.linspace(-36,36,11):
 C.append(box(0,-83,26,5.3,15,8).rotate((0,0,float(a))).translate((0,49,0)))
for a in [-37.5,-22.5,-7.5,7.5,22.5,37.5]:
 t=math.radians(a);cyl(83*math.sin(t),49-83*math.cos(t),2.8,2.7,16.8)
# Solid short side returns join the portico to the wing wall, as shown in the oblique photo.
for side in [-1,1]:
 x=side*57.3
 add(x,0,20.2,5.2,34,17.6)
 add(x,0,17.5,5.2,34,3.0)
 cut(x,-1,26,7.2,25,8)
 add(x,8,2.8,5.2,5,16.4)
# Entire building sides/back, roof PV, modern air-conditioner housings not invented.

solid=P[0]
for p in P[1:]:solid=solid+p
for c in C:solid=solid-c
for d in D:solid=solid+d
assert len(solid.decompose())==1,[(p.volume(),p.bounding_box()) for p in solid.decompose()]
m=solid.simplify(.01).to_mesh64();v=np.array(m.vert_properties,dtype=np.float32)[:,:3];v[abs(v)<.000005]=0.0
mesh=trimesh.Trimesh(v,np.array(m.tri_verts),process=True)
# Float32 source-mesh construction can collapse redundant zero-area triangles.
# Remove only zero-area construction triangles BEFORE STL export, then fail closed.
mesh.update_faces(mesh.nondegenerate_faces(height=1e-7))
assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
mesh.export(OUT/'model.stl');print(mesh.extents,len(mesh.faces),mesh.is_watertight)
