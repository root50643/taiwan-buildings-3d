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
# Pink three-storey classroom building, matched to official news4 + second-angle env1.
# Main long gabled bar and shorter perpendicular return, not detached D building.
add(9,4,2.3,104,29,30)
roof(9,4,107,32,32.0,7.5)
# Front left gable volume projects forward, with lower brick staircase side.
add(-48,-4,2.3,27,42,23)
# Both official obliques show two parallel gabled roof ridges, staggered at west ends.
add(-48,25,2.3,34,26,30)
roof(-48,25,37,29,32.0,7.2)
# The lower brick projection exposes the main bar's western upper gable.
add(-48,-4,25.0,28,43,.9)
# Window/column rhythm: two large lower floors, small upper corridor windows.
for x in np.arange(-34,61,7.4):
 for z in [5,16]:cut(float(x),-10.5,z,4.8,2.2,7.6)
 cut(float(x),-10.5,27.0,3.5,3.4,4.0)
 detail(float(x)-3.1,-11.0,2.3,1.2,2.3,29.8)
 for z in [8.4,19.4]:detail(float(x),-10.0,z,4.9,1.5,.7)
# Paired front return gable openings and vertical slit groups on the projected wing.
for x in [-54,-48,-42]:
 for z in [7,18]:cut(x,-25,z,1.5,2,6)
cut(-48,-25,27,8.5,2,4.3)
# Front portico frame projects from return, supported by robust columns.
add(-30,-20,21,24,13,1.2)
for x in [-41,-19]:add(x,-24,2.3,1.7,1.7,19.1)
# Exterior stair visible at the left, solid underneath for printability.
for i in range(17):add(-64,-31+i*1.1,2.3,8.5,1.3,.65*(i+1))
# Wall bands distinguish red masonry storeys without relying on preview color.
add(7,-11,12.1,104,1.1,.9);add(7,-11,23.2,104,1.1,.9)
# Second-angle return openings; unseen distant rear deliberately plain.
for y in [-6,2,10]:
 for z in [6,17]:cut(-61.5,y,z,1.5,2.3,5.5)

result=Manifold.batch_boolean(parts,OpType.Add)
if cuts:result=result-Manifold.batch_boolean(cuts,OpType.Add)
if details:result=result+Manifold.batch_boolean(details,OpType.Add)
if result.status().name!='NoError':raise RuntimeError(result.status())
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and mesh.volume>0
mesh.export(OUT/'model.stl');print(OUT.name,mesh.extents,len(mesh.faces))
