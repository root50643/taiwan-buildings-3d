"""Original exterior miniature geometry; dimensions in millimetres.
Public official exterior photos inform this approximation. Front is -Y.
Run this file from any directory after installing requirements.txt.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, OpType, CrossSection
OUT=Path(__file__).resolve().parent
parts,cuts,details=[],[],[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def detail(x,y,z,w,d,h):details.append(box(x,y,z,w,d,h))
def polygon(points,z,h):
 points=np.asarray(points,float)
 area=np.sum(points[:,0]*np.roll(points[:,1],-1)-np.roll(points[:,0],-1)*points[:,1])
 if area<0:points=points[::-1]
 return CrossSection([points]).extrude(h).translate((0,0,z))
def beam(p1,p2,w=1.2):
 p1=np.array(p1,float);p2=np.array(p2,float);v=p2-p1;length=np.linalg.norm(v);z=v/length
 ref=np.array([0,0,1]) if abs(z[2])<.95 else np.array([0,1,0]);x=np.cross(ref,z);x=x/np.linalg.norm(x);y=np.cross(z,x)
 transform=np.column_stack([x,y,z,p1]);return Manifold.cube((w,w,length)).translate((-w/2,-w/2,0)).transform(transform)
def window_front(x,y,z,w,h,depth=1.1,mullions=1):
 cut(x,y,z,w,depth,h)
 for k in range(1,mullions+1):detail(x-w/2+w*k/(mullions+1),y+.05,z-.05,.8,depth+.15,h+.1)
 detail(x,y+.05,z+h*.72,w+.1,depth+.15,.8)
def flat_rim(x,y,z,w,d,h=1.8,t=1.2):
 add(x,y-d/2+t/2,z,w,t,h);add(x,y+d/2-t/2,z,w,t,h)
 add(x-w/2+t/2,y,z,t,d,h);add(x+w/2-t/2,y,z,t,d,h)
def roof_panel(x,y,z,w,d,slope=2.2):
 parts.append(box(0,0,0,w,d,1.4).rotate((slope,0,0)).translate((x,y,z)))
 for xx in np.arange(-w/2+6,w/2,7):cuts.append(box(float(xx),0,1.0,.65,d+1,.6).rotate((slope,0,0)).translate((x,y,z)))
 for yy in np.arange(-d/2+6,d/2,7):cuts.append(box(0,float(yy),1.0,w+1,.65,.6).rotate((slope,0,0)).translate((x,y,z)))
# M1 水雲樓: asymmetrical L-shaped red-brick building.
# Accommodation-centre exterior photos 3–4 show a three-level rear wing and a two-level right wing.
# The nearby low gabled building is NOT included because identity/ownership is separate or unresolved.
add(0,0,0,150,108,2.4)
# Raised terrace with a broad ramp into the L-shaped recess.
add(0,10,2.3,128,76,2.3)
# Rear transverse wing and forward-projecting right wing.
add(-2,30,4.4,128,28,53.5)
add(44,1,4.4,36,83,35.4)
# Strong red-brick floor bands and overhanging parapets, the signature facade feature.
for z in [20.0,37.5,55.0]:
 add(-2,15.1,z,130,3.8,3.4)
 add(-66.1,30,z,3.8,30,3.4)
for z in [20.0,37.5]:
 add(24.9,1,z,3.8,85,3.4)
 add(44,-40.7,z,40,3.8,3.4)
 add(63.1,1,z,3.8,85,3.4)
# Tall wing grouped windows, preserving different bay widths seen in the close oblique.
for row in range(3):
 z=7.0+row*17.5
 for x,w in [(-56,12),(-39,12),(-24,7),(-11,13),(8,12),(23,7)]:
  window_front(x,15.95,z,w,10.5,1.3,1 if w<9 else 2)
# Ground-floor entry at the inside corner, below two rows of windows.
cut(17,15.9,4.6,13,1.4,13.4)
for x in [11,17,23]:detail(x,15.95,4.5,.85,1.5,13.6)
detail(17,15.95,14.9,13.2,1.5,.85)
# Long courtyard-facing side of the low right wing.
for row in range(2):
 z=7+row*17.5
 for y,w in [(-31,9),(-17,10),(-3,10),(10,8)]:
  cut(25.95,y,z,1.4,w,10.5)
  detail(25.95,y,z-.1,1.5,.85,10.7)
  detail(25.95,y,z+7.6,1.5,w+.1,.85)
# Short end: broad nearly blank upper brick panel, lower doorway and high small window.
cut(32,-40.6,4.7,10,1.2,14.8)
detail(32,-40.5,12.5,10.1,1.5,.85)
window_front(54.5,-40.65,15.7,10,4.3,1.2,1)
# Large offset name plaque and small secondary plaque are printable relief.
add(34,-42.1,22.1,20,1.8,7.0)
add(32,-41.7,19.4,12,1.5,3.0)
# Distinct broad bowl-and-stem facade inlay, simplified from the photographed artwork.
bowl=[(40,16.0),(61,16.0),(61,14.3),(56,12.5),(51,11.6),(46,12.5),(40,14.3)]
parts.append(polygon(bowl,0,.8).rotate((90,0,0)).translate((0,-40.35,0)))
add(51,-40.65,6.0,.85,1.0,6.0)
for x in [47,55]:
 for z in [6.0,8.5,11.0]:add(x,-40.7,z,1.7,1.0,1.7)
# Shallow masonry coursing is limited to broad blank end panels; no texture-only details.
for z in np.arange(25.8,36.3,2.2):cut(44,-40.53,float(z),34,.32,.55)
for z in [21,38.4]:
 for x in range(26,64,3):cut(float(x),-42.45,z,.55,.40,2.1)
# Roofs, estimated depths, and a single plain rooftop screen visible on the tall wing.
flat_rim(-2,30,57.5,128,28,2.0,1.3)
flat_rim(44,-1,40.5,36,80,1.6,1.3)
add(-35,32,57.6,30,12,5.5)
# Front platform and documented descending stairs at the right.
add(43,-44.7,2.3,42,13,2.5)
for i in range(4):add(49,-51.0+i*1.8,2.3+i*.5,28,2.8,.7)
# Ramp into the inner corner; simplified as a gentle solid slope above the continuous plinth.
# Supported thin sloping slab; exact grade is an estimate.
parts.append(box(0,0,0,17,65,1.4).rotate((2.0,0,0)).translate((13,-16.5,3.55)))
# Robust handrails: 1.2 mm bars and posts, each tied into the ramp or terrace.
for x in [4.8,21.2]:
 for y in [-44,-34,-24,-14,-4,6,14]:add(x,y,2.35,1.2,1.2,5.7)
 add(x,-15.0,7.0,1.2,60,1.2)
# Secondary front rail by the steps.
for x in [27,36,45]:add(x,-47,4.5,1.2,1.2,5.0)
add(36,-47,8.4,20,1.2,1.2)
# Unseen exterior backs are left simple rather than mirror-imaging courtyard windows.

# Union and carve all architectural relief into a single printable boundary.
result=Manifold.batch_boolean(parts,OpType.Add)
if cuts:result=result-Manifold.batch_boolean(cuts,OpType.Add)
if details:result=result+Manifold.batch_boolean(details,OpType.Add)
# Collapse sub-micron Boolean slivers before STL float32 serialization.
result=result.simplify(0.0005)
if result.status().name!='NoError':raise RuntimeError(str(result.status()))
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
if not mesh.is_watertight or len(mesh.split(only_watertight=False))!=1:
 print([(x.volume,x.bounds.tolist()) for x in mesh.split(only_watertight=False)])
 raise RuntimeError('Expected one watertight connected boundary.')
mesh.export(OUT/'model.stl');print('Exported',mesh.extents.tolist(),'mm;',len(mesh.faces),'triangles')
