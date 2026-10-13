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
 return Manifold.hull([box(*a,2*r,2*r,2*r),box(*b,2*r,2*r,2*r)])
add(0,0,0,150,110,2.4)
# Exterior rear bar and side returns form the architect-documented open courtyard.
# School front photograph is shown on -Y; courtyard opens toward +Y.
add(-4,-23,2.3,124,22,32)
add(-53,9,2.3,26,57,32)
add(45,9,2.3,26,57,32)
# Set-back roof volume and distinctive sloping tower cap from school photograph.
add(3,-17,33.9,18,19,10)
parts.append(yz([(-29,40),(-5,43),(-5,44.2),(-29,41.2)],-8,24))
# Three storeys of perforated sun screens on left, thickened to printable square recesses.
# Dense real pattern consolidated; no claim of exact perforation count.
for cx in [-52,-34,-16]:
 for z in [4.8,14.1,23.4]:
  add(cx,-34,z,15.4,1.4,7.4)
  for x in np.arange(cx-6.6,cx+7,2.2):
   for zz in np.arange(z+.8,z+7,2.2):
    # Screen body is fused to backing to avoid unsupported miniature islands.
    cut(float(x),-34.5,float(zz),1.05,1.2,1.05)
# Front structural piers and floor edge bands.
for x in [-62,-43,-25,-6]:detail(x,-34.1,2.3,1.7,2.2,31.8)
for z in [12.3,21.6,30.9]:detail(-34,-34.1,z,60,2.2,1.2)
# Right office block has long double windows rather than perforated screens.
for x in [22,39,54]:
 for z in [5.5,15,24.5]:
  cut(x,-34,z,12.3,2.5,5.7)
  for dx in [-3.9,0,3.9]:detail(x+dx,-33.3,z,.8,1.6,5.8)
# External courtyard galleries on both sides and back wall, based on built-photo evidence.
for y in np.arange(-9,34,9):
 for z in [5,14.4,23.8]:
  cut(-40,y,z,4.4,6.2,6.5);cut(32,y,z,4.4,6.2,6.5)
for x in np.arange(-28,29,9):
 for z in [5,14.4,23.8]:cut(float(x),-12,z,6.3,4.2,6.5)
# Open courtyard raised platform and broad external stairs, not interior circulation.
add(-3,8,2.3,70,39,5.5)
for i in range(8):add(-3,46-i*1.3,2.3,61,1.5,.7*(i+1))
# Plain courtyard parapet strips, side piers kept substantial.
for z in [12,21.4,30.8]:
 add(-39,8,z,1.5,57,1);add(31,8,z,1.5,57,1)
# No claim that conceptual model photographs establish unseen as-built roof detail.

result=Manifold.batch_boolean(parts,OpType.Add)
if cuts:result=result-Manifold.batch_boolean(cuts,OpType.Add)
if details:result=result+Manifold.batch_boolean(details,OpType.Add)
if result.status().name!='NoError':raise RuntimeError(result.status())
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and mesh.volume>0
mesh.export(OUT/'model.stl');print(OUT.name,mesh.extents,len(mesh.faces))
