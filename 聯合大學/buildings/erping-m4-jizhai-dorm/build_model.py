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
# M4 霽齋樓: narrow three-level slab; entry on short end; two stacked central grille windows;
# large cantilevered roof cornice and long solar canopy with a small documented open patch.
add(0,0,0,76,150,2.4)
add(0,8,2.3,54,122,46.0)
# The actual short front end has one central stair-window stack, not a generic window grid.
for z in [19.0,33.2]:
 window_front(0,-53.1,z,7.1,12.4,1.3,3)
 for zz in [z+3.4,z+7.3]:detail(0,-53.15,zz,7.2,1.4,.8)
add(0,-53.65,30.6,8.1,1.8,2.5)
# Small asymmetrical entry and a separate sign plaque.
cut(0,-53.15,2.7,10.3,1.4,12.3)
for x in [-5.0,-1.5,5.0]:detail(x,-53.15,2.6,.85,1.6,12.5)
detail(0,-53.15,10.6,10.4,1.6,.85)
add(0,-54.0,15.2,13.1,3.4,1.4)
add(16.8,-53.7,8.0,18.0,1.6,5.8)
add(7.8,-53.65,22.0,7.4,1.6,2.8)
# Only broad architectural facade seams are represented; no resident or security details.
for z in [17.5,25.0,32.0,39.5,46.5]:cut(0,-53.04,z,53.5,.38,.55)
# East long elevation partly verified from the aerial exterior: grouped rectangular windows.
# Bay rhythm and occluded lower extent are approximate; west/back stay intentionally plain.
for y in [-43,-31,-19,-7,5,17,29,41,53,63]:
 for z in [6.0,20.2,34.4]:
  cut(27.05,y,z,1.3,7.5,8.8)
  for yy in [y-2.4,y,y+2.4]:detail(27.0,yy,z-.1,1.5,.8,9.0)
  detail(27.0,y,z+6.3,1.5,7.6,.8)
# Eaves project 2 mm; flat parapet and canopy remain open to the exterior.
add(0,8,48.0,58,126,1.6)
flat_rim(0,8,49.4,58,126,2.0,1.3)
for y in [-43,-22,-1,20,41,62]:
 for x in [-22,0,22]:
  # Leave the photographed opening without a guessed tank or replacement object.
  if x==0 and y==41:continue
  add(x,y,49.5,1.5,1.5,7.7+(y+43)*.035)
for x in [-22,22]:
 parts.append(box(0,0,0,1.5,109,1.4).rotate((2.0,0,0)).translate((x,9.5,58.0)))
roof_panel(0,9.5,58.8,50,111,2.0)
# Through the solar sheet only; the building's flat roof remains solid below.
cut(0,40,54.0,11.0,18.0,12.0)
# Shallow front apron, integrated into the base. No invented staircase.
add(0,-59.2,2.3,16,13,1.0)

# Union and carve all architectural relief into a single printable boundary.
result=Manifold.batch_boolean(parts,OpType.Add)
if cuts:result=result-Manifold.batch_boolean(cuts,OpType.Add)
if details:result=result+Manifold.batch_boolean(details,OpType.Add)
if result.status().name!='NoError':raise RuntimeError(str(result.status()))
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
if not mesh.is_watertight or len(mesh.split(only_watertight=False))!=1:
 print([(x.volume,x.bounds.tolist()) for x in mesh.split(only_watertight=False)])
 raise RuntimeError('Expected one watertight connected boundary.')
mesh.export(OUT/'model.stl');print('Exported',mesh.extents.tolist(),'mm;',len(mesh.faces),'triangles')
