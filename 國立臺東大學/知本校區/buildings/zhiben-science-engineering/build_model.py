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
add(0,0,0,150,100,2.4)
# Five-storey principal facade group; open rear courts beyond it are not duplicated.
# Three high pitched-roof bars, stepped facade and shallow open balcony recesses.
for x,y,w,d,h in [(-43,4,40,28,41),(-5,2,35,31,43),(37,6,37,29,45)]:
 add(x,y,2.3,w,d,h);roof(x,y,w+2,d+2,h+2.1,6)
# Forward glazing bay on left, structurally filled behind shallow glazing relief.
add(-52,-16,15,24,14,21)
cut(-52,-23,17,19,1.8,16)
for x in [-60,-56,-52,-48,-44]:detail(x,-22.8,17,.7,1.1,16)
for z in [21,26,31]:detail(-52,-22.8,z,19,1.1,.7)
# Visible projecting concrete frame around glazed bay.
add(-52,-23.2,35.2,26,2.0,1.3)
add(-64,-19,15,1.5,11,21.5);add(-40,-19,15,1.5,11,21.5)
# Photo-visible narrow forward wings: deeper than the connecting gallery facade.
# Three solid narrow vertical wings and projecting white portal frames.
for x,y,zmax in [(-30,-15.5,43),(0,-16.2,45),(38,-12.0,47)]:
 add(x,y,2.3,8.5,8.0,zmax-2.3)
 for z in [6,14,22,30,38]:cut(x,y-4,z,3.1,1.9,4.6)
# Open external galleries between the risalits, with visible slab edges and piers.
for x0,x1,y in [(-23,-7,-13.5),(7,22,-13.5),(26,31,-8.5),(45,52,-8.5)]:
 for z in [5,13.2,21.4,29.6,37.8]:
  cut((x0+x1)/2,y,z,x1-x0,6,6)
 for z in [11,19.2,27.4,35.6]:detail((x0+x1)/2,y-1.4,z,x1-x0+.6,4.0,1.2)
 for x in np.arange(x0,x1,7.0):detail(float(x),y-1.4,2.3,1.3,4.0,41)
# Front gable projection roof lips on narrow wings.
for x,y,z in [(-30,-15.5,43),(0,-16.2,45),(38,-12.0,47)]:add(x,y,z,9.5,9,1.0)
# Photo-based rhythm of narrow openings, deliberately consolidated into printable pairs.


# Central lower canopy with thickened, supported slab.
add(-5,-14,21.5,29,3,1.2)
# Open balcony-like vertical recess between main bars; depth intentionally shallow.
cut(15,-13.5,6,7.5,7,38)
for z in [12.5,20.7,28.9,37.1]:detail(15,-12.8,z,8,4,1.2)
# Stair tower and flat terrace top on right.
add(21,10,44,12,15,5.0);add(21,10,48.5,15,18,1.3)
# Right gable end vertical louvers simplified to three shallow slots.
for y in [-2,5,12]:
 for z in [8,19,30]:cut(55.6,y,z,1.2,2,6)
# Low rear return documented by school oblique; far rear facade intentionally plain.
add(48,29,2.3,30,27,21);roof(48,29,32,29,23,4)

result=Manifold.batch_boolean(parts,OpType.Add)
if cuts:result=result-Manifold.batch_boolean(cuts,OpType.Add)
if details:result=result+Manifold.batch_boolean(details,OpType.Add)
if result.status().name!='NoError':raise RuntimeError(result.status())
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and mesh.volume>0
mesh.export(OUT/'model.stl')
print(OUT.name,mesh.extents,len(mesh.faces))
