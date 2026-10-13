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
# Former Chung-Cheng Hall, now Food Biotechnology Pilot Plant.
# Public facades only: no process machinery, room layout, or security details.
add(0,0,2.3,126,87,27)
add(0,-1,29,129,90,2.2)
# Central elevated clerestory with broad cornice.
add(0,-22,30.9,53,31,13)
add(0,-22,43.5,58,35,2.6)
# Low barrel roof running along the rear hall, seen in official oblique.
pts=[(-23,30.8),(23,30.8)]+[(float(23*np.cos(t)),float(30.8+7*np.sin(t))) for t in np.linspace(0,np.pi,25)]
# Extrude x-z section along Y; polygon orientation corrected before construction.
a=np.array(pts);area=np.sum(a[:,0]*np.roll(a[:,1],-1)-np.roll(a[:,0],-1)*a[:,1]);pts=pts if area>0 else pts[::-1]
parts.append(CrossSection([pts]).extrude(50).rotate((90,0,0)).translate((0,38,0)))
# Central front two-storey deep portico; five full-height slender piers.
cut(5,-43.5,3.2,54,9,24)
for x in [-23,-10,3,16,29]:detail(x,-44,2.3,2.5,7,27)
# Front right rectangular window wing.
for x in [40,49,58]:
 for z in [5,17]:
  cut(x,-43.5,z,5.4,1.8,7);detail(x,-43,z,.8,1.2,7)
# Left front corner lattice, thickened and fused to solid backing for reliable printing.
for z in [5,11,17,23,28]:detail(-45,-44.1,z,35,1.4,.8)
for x in np.arange(-61,-26,8):
 for z in [5,17]:
  details.append(bar((float(x),-44, z),(float(min(x+8,-27)),-44,z+11),.5))
  details.append(bar((float(x),-44,z+11),(float(min(x+8,-27)),-44,z),.5))
# Lattice continues around left side corner; remainder has tall external columns.
for y in np.arange(-39,-14,8):
 for z in [5,17]:
  details.append(bar((-63.2,float(y),z),(-63.2,float(y+8),z+11),.5))
  details.append(bar((-63.2,float(y),z+11),(-63.2,float(y+8),z),.5))
for y in [-8,3,14,25,36]:
 cut(-63,y,4,4,7,23);detail(-64,y-4.3,2.3,3,2,27)
# Clerestory glazing, narrow fluted piers and cornice dentils.
for x in [-21,-11,-1,9,19]:
 cut(x,-37.5,33,6,2,9)
 detail(x-4,-38,31,1.3,2,12.6)
for x in np.arange(-27,28,2.7):detail(float(x),-38.5,41.5,1.0,2.6,2.1)
for i in range(4):add(4,-48-i*1.1,2.3,66,1.3,3.0-i*.6)

result=Manifold.batch_boolean(parts,OpType.Add)
if cuts:result=result-Manifold.batch_boolean(cuts,OpType.Add)
if details:result=result+Manifold.batch_boolean(details,OpType.Add)
assert result.status().name=='NoError'
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and mesh.volume>0
mesh.export(OUT/'model.stl');print(OUT.name,mesh.extents,len(mesh.faces))
