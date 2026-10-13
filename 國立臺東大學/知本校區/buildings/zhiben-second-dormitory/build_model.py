"""Public-exterior miniature in millimeters. Rebuild: python build_model.py.
Photo-interpreted, independent scale. No interior or security systems represented.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection, OpType
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def detail(x,y,z,w,d,h):details.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def poly(points,z,h):return CrossSection([points]).extrude(h).translate((0,0,z))
def yz(points,x,w):return CrossSection([points]).extrude(w).rotate((90,0,0)).rotate((0,0,90)).translate((x,0,0))
def roof(x,y,w,d,z,rise):
 add(x,y,z-.2,w,d,.75)
 parts.append(yz([(y-d/2,z),(y+d/2,z),(y,z+rise)],x-w/2,w))
def windows(x0,x1,y,zs,w=2.3,h=4.1,step=6):
 for x in np.arange(x0,x1+.01,step):
  for z in zs:cut(float(x),y,z,w,1.4,h)


def bar(p,q,r=.65):
 return Manifold.batch_hull([box(*p,2*r,2*r,2*r),box(*q,2*r,2*r,2*r)])
add(0,0,0,150,120,2.4)
# Three parallel pitched-roof residential bars with projecting end bays.
# Dining centre is intentionally excluded and tracked separately.
for y,shift in [(-31,-6),(6,0),(43,6)]:
 add(shift,y,2.3,111,19,36)
 roof(shift,y,113,21,38.0,5.5)
 for x in [shift-47,shift+43]:
  add(x,y-6,2.3,18,26,34)
  parts.append(yz([(-10,35.8),(10,35.8),(0,40.6)],-14,28).rotate((0,0,90)).translate((x,y-6,0)))
  add(x,y-6,35.6,20,28,.7)
  # Lower forward-sloping cap characteristic of front end bays.
  parts.append(yz([(y-26,23),(y-18,23),(y-6,34),(y-6,36)],x-9,18))
  add(x,y-18,2.3,18,11,21)
  for z in [5,12,19,27]:cut(x,y-23.5,z,11,3.4,4.9)
 for x in np.arange(shift-31,shift+33,8):
  for z in [4.5,11.5,18.5,25.5,32.5]:cut(float(x),y-9.5,z,5.8,4.0,4.9)
 for z in [9.9,16.9,23.9,30.9]:detail(shift,y-10,z,75,2.2,1.1)
 # Dark projecting vertical stair bay and narrow slit openings.
 add(shift+22,y-10.2,2.3,6,3.5,37)
 for z in [7,14,21,28,35]:cut(shift+22,y-12,z,2.5,1.8,3.6)

result=Manifold.batch_boolean(parts,OpType.Add)
if cuts:result=result-Manifold.batch_boolean(cuts,OpType.Add)
if details:result=result+Manifold.batch_boolean(details,OpType.Add)
assert result.status().name=='NoError'
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and mesh.volume>0
mesh.export(OUT/'model.stl');print(OUT.name,mesh.extents,len(mesh.faces))
