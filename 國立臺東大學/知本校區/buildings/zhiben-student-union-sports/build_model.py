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

def ellipse(x,y,rx,ry,z,h):
 pts=[(x+rx*np.cos(t),y+ry*np.sin(t)) for t in np.linspace(0,2*np.pi,96,endpoint=False)]
 return poly(pts,z,h)
def bar(p,q,r=1):
 a=np.array(p);b=np.array(q);v=b-a;length=np.linalg.norm(v)
 # Thick exterior braces as hull between small endpoint cubes, no free decorative shells.
 return Manifold.batch_hull([box(*a,2*r,2*r,2*r),box(*b,2*r,2*r,2*r)])
add(0,0,0,150,110,2.4)
# Low sports hall, open exterior entry court, and planted folding landscape roof.
# Coordinates interpreted from architect aerial + side exterior photos.
add(-43,4,2.3,48,72,21)
add(-43,9,22.9,44,59,4.5)
add(-43,9,27.0,47,62,1.2)
# High clerestory band and broad lower galleries on lake-facing sports hall.
for x in np.arange(-62,-22,5.2):
 cut(float(x),-20.5,24.0,3.8,2.5,2)
 for z in [4.4,13.8]:cut(float(x),-32,z,3.9,4.5,7.5)
for z in [12.1,21.6]:detail(-43,-32,z,48,3,1.1)
# Right roof slopes to the ground, with two visible folds/skylight ridges.
# Prism in XZ extruded along Y through the low wing.
points=[(16,2.3),(68,2.3),(68,4.3),(48,10),(38,23),(24,26),(16,23)]
parts.append(CrossSection([points]).extrude(68).rotate((90,0,0)).translate((0,36,0)))
# Transverse shallow raised bands instead of invented roof equipment.
for y in [-5,19]:
 parts.append(CrossSection([[(34,2.3),(48,2.3),(48,16),(34,27)]]).extrude(10).rotate((90,0,0)).translate((0,y+5,0)))
# Central open entry portico: roof plate with open-to-sky oval hole.
roofplan=[(-22,-34),(17,-34),(30,-18),(24,22),(-22,26)]
canopy=poly(roofplan,21.6,1.5)-ellipse(1,7,13,12,20,5)
parts.append(canopy)
# Interior-facing exterior boundary deliberately shallow, no room layouts represented.
add(0,24,2.3,44,8,20)
# Robust Y-shaped supports visible in the public open-air entrance; thickened for printing.
for x in [-15,-2,12]:
 for y in [-27,14]:
  add(x,y,2.3,1.8,1.8,11.4)
  parts.append(bar((x,y,12.4),(x-4.5,y,21.0),.85))
  parts.append(bar((x,y,12.4),(x+4.5,y,21.0),.85))
# Slanted right wing vertical glazing stripes, cut at outer front edge.
for x in np.arange(20,61,5):
 h=max(2,22-(x-25)*.40)
 cut(float(x),-32,3.7,2.2,2.6,float(h))
# Exterior step into front entrance, and stepped landscaped apron on low wing.
for i in range(5):add(-3,-40+i*1.3,2.3,28,1.5,.5*(i+1))
# Rear kept plain unless a roof fold is actually evidenced.

result=Manifold.batch_boolean(parts,OpType.Add)
if cuts:result=result-Manifold.batch_boolean(cuts,OpType.Add)
if details:result=result+Manifold.batch_boolean(details,OpType.Add)
if result.status().name!='NoError':raise RuntimeError(result.status())
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and mesh.volume>0
mesh.export(OUT/'model.stl');print(OUT.name,mesh.extents,len(mesh.faces))
