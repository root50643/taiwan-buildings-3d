"""Original TNNUA exterior miniature, millimetres. Public photo-derived estimates.
Run: python build_model.py. No source 3D assets or interior/security details used.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def det(x,y,z,w,d,h):details.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def ellipse(x,y,z,rx,ry,h):return Manifold.cylinder(h,1,1,circular_segments=128).scale((rx,ry,1)).translate((x,y,z))
def profile(poly,y,depth):
 if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))<0:poly=poly[::-1]
 return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def slope(poly,width):return CrossSection([poly]).extrude(width).rotate((90,0,90)).translate((-width/2,0,0))
def col(x,y,z,r,h):parts.append(Manifold.cylinder(h,r,r,circular_segments=24).translate((x,y,z)))
add(0,0,0,150,146,3)
# Two long wings enclose a courtyard with a lower transverse rear wing.
add(-47,3,2.8,25,116,42)
add(43,7,2.8,28,111,39)
add(0,52,2.8,95,19,34)
# Front hall elevated above a public columned space.
add(37,-42,20,47,34,30)
cut(37,-50,3.2,36,25,16.5)
for x in [19,38,56]:col(x,-50,3,1.8,18)
# Prominent projecting louvers on the public front plane.
cut(37,-59,24,29,4,23)
for z in np.arange(24,47,2.8):det(37,-60,float(z),31,6,1.2)
# Folded/sloping overhang above front hall, thickened miniature plate.
parts.append(slope([(-62,51),(-20,48),(-20,50),(-62,53)],52).translate((37,0,0)))
# Tall narrow apertures flank the central louver field.
for x in [17,58]:cut(x,-59,30,2.6,4,12)
# Long wing's external folded vertical fins, not a uniform window texture.
for y in np.arange(-43,49,11):
 parts.append(box(-60,float(y),29,6,1.8,14).rotate((0,0,0)))
 for z in [9,20]:cut(-59.5,float(y),z,3,7,4)
# Courtyard-facing long shaded openings and gallery spines.
for xx in [-34.5,29]:
 for z in [9,20,31]:
  cut(xx,7,z,4,78,6)
  for y in [-27,-13,1,15,29,43]:det(xx+(1 if xx<0 else -1),y,z,2.5,1.5,6)
# Side-wide horizontal overhangs preserve the distinctive layered slabs.
add(-47,3,44,29,119,1.8)
add(43,15,41,31,97,1.8)
# Courtyard outdoor semicircular stepped performance bowl: public exterior only.
for i in range(6):
 r=25-i*3.4
 disk=ellipse(0,15,2.9,r,r,1.2*(6-i)) ^ box(0,28,2.8,55,27,10)
 parts.append(disk)
# Middle entry canopy and exposed columns.
add(-5,-51,16,39,21,2)
for x in [-22,10]:
 for y in [-59,-43]:col(x,y,3,1.6,14)
# External staircase at right leading to upper courtyard terrace, solid underside simplified.
parts.append(slope([(-65,3),(-35,3),(-35,23),(-65,5)],9).translate((7,0,0)))
for i in range(12):add(7,-64+i*2.5,3,10,2.9,2+i*1.5)
# Rear facade beyond the observed long wings is deliberately plain.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
