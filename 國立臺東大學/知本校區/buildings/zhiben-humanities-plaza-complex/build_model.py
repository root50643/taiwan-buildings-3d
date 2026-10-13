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
# Scope is the photographed plaza-facing ensemble and oval performance hall.
# Far rear teaching wings are not reconstructed from guesswork.
# Central teaching bar is set at back of plaza with right return forming a courtyard.
add(7,30,2.3,96,22,36)
add(58,4,2.3,24,65,39)
# Stepped teaching mass and short taller end parapets; upper rear levels simplified.
add(-27,37,37.8,21,13,6.5);add(48,33,40.9,17,20,5.0)
roof(48,33,19,22,45.6,2.3)
# Oval standalone-looking performance hall at left; joined by shared printable base only.
parts.append(ellipse(-45,-12,25,23,2.3,28))
# Curved thick entrance canopy, cropped to front arc and fused into hall.
arc=ellipse(-45,-12,29,27,25.7,1.2)-ellipse(-45,-12,23,21,24,5)
arc=arc^box(-45,-31,20,65,24,15);parts.append(arc)
# Actual front entrance openings remain shallow, no interior simulation.
cut(-43,-35,3.0,14,3.4,15)
for x in [-49,-43,-37]:detail(x,-33.9,3,.9,2,15)
cut(-60,-30,3.0,5,5,14)
# Performance hall side stair: ascending toward rear along curved wall, solid-backed.
for i in range(24):add(-69,-29+i*1.55,2.3,5.5,1.75,1.15*(i+1))
# Main bar has deep bays, paired vertical window slits, pronounced slab bands.
for x in np.arange(-34,48,9):
 for z in [9.7,19.2,28.7]:cut(float(x),19,z,6.8,4,6.5)
for x in np.arange(-38,52,9):detail(float(x),17.6,7.8,1.6,3.8,30)
for z in [17,26.5,36]:detail(7,17.6,z,96,3.8,1.1)
# Right wing exterior gallery facing plaza, including projecting stair tower.
for y in np.arange(-21,31,9):
 for z in [6,15,24,33]:cut(46,y,z,4.6,6,6)
for y in np.arange(-24,35,9):detail(44.9,float(y),2.3,3,1.5,37)
for z in [12.1,21.1,30.1,39.1]:detail(44.9,4,z,3,65,1.1)
# Exposed staircase tower at near right corner with alternating horizontal platforms.
add(62,-34,2.3,15,14,39)
cut(62,-41,5,10.5,5,32)
for z in [11,20,29,38]:detail(62,-40,z,12.2,5,1.2)
# Broad central steps rise into the courtyard entrance.
add(7,14,2.3,42,12,5.6)
for i in range(9):add(7,1+i*1.1,2.3,30,1.3,.63*(i+1))
# Roof-top sawtooth shading rhythm from the photograph, thickened as small solid prisms.
for x in np.arange(-34,48,6):
 parts.append(yz([(18,38.1),(23,38.1),(21.5,40.8)],float(x),3.0))

result=Manifold.batch_boolean(parts,OpType.Add)
if cuts:result=result-Manifold.batch_boolean(cuts,OpType.Add)
if details:result=result+Manifold.batch_boolean(details,OpType.Add)
if result.status().name!='NoError':raise RuntimeError(result.status())
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and mesh.volume>0
mesh.export(OUT/'model.stl');print(OUT.name,mesh.extents,len(mesh.faces))
