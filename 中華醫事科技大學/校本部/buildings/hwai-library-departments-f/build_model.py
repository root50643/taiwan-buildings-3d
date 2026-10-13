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
# F/F1-F4: one connected group, not five duplicated standalone buildings.
# Official current diagram: west spine, F2/F3 east fingers, southern library bar.
add(0,0,0,102,150,3)
add(-32,5,2.8,21,128,61)
# Three eastward bars form two real open-to-east courts.
add(0,-49,2.8,77,38,61)
for y in [-3,36]:add(0,y,2.8,77,24,61)
# F4 northern continuation remains part of the common west spine; G is excluded.
add(-32,61,2.8,22,16,61)
# Library east-end drum is observed in the public front photo, not map-only styling.
parts.append(Manifold.cylinder(48,12,12,circular_segments=72).translate((34,-49,17)))
# True tall opening below drum and canopy; back wall retained, pair of thick supports.
cut(38,-49,3,18,18,15)
for y in [-58,-40]:details.append(box(41,y,3,4.2,4.0,16))
add(38,-49,17,20,30,2.2)
# Curved horizontal glazing stripes above the entrance.
for z in [24,32,40,48,56]:
 ring=Manifold.cylinder(4.5,12.4,12.4,circular_segments=72).translate((34,-49,z))-Manifold.cylinder(5,10.4,10.4,circular_segments=72).translate((34,-49,z-.2))
 cuts.append(ring^box(45,-49,z,22,28,5))
# Narrow flanking east-end windows; copied only where photos show them.
for z in [23,31,39,47,55]:
 for y in [-64,-34]:cut(38,y,z,3.2,5,4.3)
# A stepped hipped cap over round glass and higher white shoulders.
parts.append(Manifold.cylinder(4.5,13,9,circular_segments=72).translate((34,-49,64)))
for y in [-66,-32]:add(26,y,63,20,3,7)
hip(0,-49,63,78,40,3.4)
# Southern facade visible from school gate: seven ranks with dark louver/window strips.
for z in [8,16,24,32,40,48,56]:
 for x in [-32,-19,-6,7,20]:
  cut(x,-68,z,9.5,3.2,4.5)
  add(x,-68.4,z+4.7,10.5,1.2,1.0)
# East-facing connecting spine and first two open wings: deep colonnade bays from overview.
for y in [-3,36]:
 for z in [7,15,23,31,39,47,55]:
  for x in [-13,0,13,26]:cut(x,y-12,z,9.5,5.2,5.5)
  # Visible finger-end terrace slots.
  cut(38,y,z,4.8,17,5.5)
 hip(0,y,63,78,26,3)
# Open west-spine gallery faces toward the two courts, not filled-in courtyard walls.
for y in [-23,17]:
 for z in [7,15,23,31,39,47,55]:cut(-21.5,y,z,5,10,5.2)
hip(-32,6,63,24,128,2.6)
# West and far northern elevations and roof services are insufficiently observed;
# leave simplified envelope rather than copying the front windows to unseen faces.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
