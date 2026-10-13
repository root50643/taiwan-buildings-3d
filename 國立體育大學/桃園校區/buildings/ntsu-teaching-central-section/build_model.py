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

# Six visible facade bands from the official admissions oblique photo, not inferred room numbers.
# Only the central group and two narrow adjoining wing strips are included.
add(0,0,0,150,65,3)
add(0,11,2.8,133,30,108)
# Green central fin and projecting white bay flank the tall glass strip asymmetrically.
add(1,-8,2.8,5,12,115)
add(18,-5,26,26,10,85)
cut(-13,-4,28,19,5,81)
# Tall glazing's horizontal bars are backed and do not float.
for z in np.arange(32,107,5.5):D.append(box(-13,-2.2,float(z),19,2.4,1.0))
D.append(box(-13,-2.2,28,1.4,2.4,81))
# Main doorway and adjoining full-height glass bay are recessed.
cut(-9,-7,3,28,19,23)
cut(17,-5,3,23,9,23)
# Broad entrance canopy with real free porch space below.
add(-10,-16,25.4,39,30,3.2)
add(-27,-19,2.8,2.4,3.4,23)
# Source shows white diagonal canopy stay on the left; enlarged for printing.
D.append(profile([(-30,28),(-27,28),(-7,38),(-7,40)],-10,2.0))
# Wing window openings keep primary structural bays and paired opening groups.
for side in [-1,1]:
 for x in ([ -55,-40] if side<0 else [43,58]):
  for z in [8,26,44,62,80,98]:
   cut(x,-4,z,11,4,9)
   if z!=98:cut(x,-4,z+10.5,11,4,2.1)
for z in [33,50,67,84,101]:
 for x in [11,24]:cut(x,-10,z,8.7,4,9)
 # A projecting sill and central pier preserve the white projecting bay.
 add(18,-9,z-2,27,4,1.6)
# Small upper overhang is visible in the admissions photograph.
add(-7,-5,116.0,35,20,2.2)
# No full roof or PV layout reconstructed; top and rear are explicit partial cuts.

solid=P[0]
for p in P[1:]:solid=solid+p
for c in C:solid=solid-c
for d in D:solid=solid+d
assert len(solid.decompose())==1,[(p.volume(),p.bounding_box()) for p in solid.decompose()]
m=solid.simplify(.0001).to_mesh64();v=np.array(m.vert_properties,dtype=np.float32)[:,:3];v[abs(v)<.000005]=0.0
mesh=trimesh.Trimesh(v,np.array(m.tri_verts),process=True)
# Float32 source-mesh construction can collapse redundant zero-area triangles.
# Remove only zero-area construction triangles BEFORE STL export, then fail closed.
mesh.update_faces(mesh.nondegenerate_faces(height=1e-7))
assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
mesh.export(OUT/'model.stl');print(mesh.extents,len(mesh.faces),mesh.is_watertight)
