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
add(0,0,0,150,110,2.4)
# Three parallel five-storey residential bars; shared base connects exterior shells.
for y in [-34,0,34]:
 add(-6,y,2.3,112,19,32)
 roof(-6,y,114,21,34,3.2)
 # End staircase block with raised red-panel roof lantern, photograph verified.
 add(43,y,2.3,22,21,36)
 add(43,y,38,18,17,7)
 roof(43,y,21,20,44.6,3.1)
 for x in [37,42,47]:cut(x,y-8.6,39.4,3.4,1.6,4.0)
 for x in np.arange(-57,32,8):
  for z in [4.5,10.8,17.1,23.4,29.7]:cut(float(x),y-9.5,z,5.8,3.4,4.1)
 for x in np.arange(-61,34,8):detail(float(x),y-10,2.3,1.1,1.7,31.5)
 for z in [9,15.3,21.6,27.9]:detail(-13,y-10,z,98,2,1.2)
 # Side balconies are consolidated into thick ledges and recesses.
 for z in [9,15.3,21.6,27.9]:
  cut(54,y,z,2.3,10,4.3);detail(54.3,y,z-.7,3.4,11,1.2)
 # Unseen far rear has only conservative repeated shallow bays.
 for x in np.arange(-56,27,10):
  for z in [6,18,30]:cut(float(x),y+9.5,z,4.5,1.2,2.5)

result=Manifold.batch_boolean(parts,OpType.Add)
if cuts:result=result-Manifold.batch_boolean(cuts,OpType.Add)
if details:result=result+Manifold.batch_boolean(details,OpType.Add)
assert result.status().name=='NoError'
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and mesh.volume>0
mesh.export(OUT/'model.stl');print(OUT.name,mesh.extents,len(mesh.faces))
