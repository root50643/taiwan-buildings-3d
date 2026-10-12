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
def polygon(points,z,h):return CrossSection([points]).extrude(h).translate((0,0,z))
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
# M2 紅夢樓: four visible regular window tiers, external lift, bridge porch and solar canopy.
add(0,0,0,150,70,2.4)
add(0,3,2.3,132,36,53.5)
# Main concrete facade structural rhythm; no guessed rear windows.
for row in range(4):
 z=7+row*11.2
 for x in np.linspace(-51.0,57.0,13):
  cut(float(x),-15.2,z,7.5,1.6,8.6)
  window_front(float(x),-14.55,z+2.4,6.3,5.1,1.2,2)
 for x in np.linspace(-55.5,61.5,14):add(float(x),-15.7,z-.4,1.1,2.0,10.8)
for z in [5.5,16.7,27.9,39.1,50.3]:add(3,-15.5,z,125,2,1.15)
# Left lift tower, with its photographed white-clad side and X-framed glazed front.
add(-63,0,2.3,13,42,60.8)
for row in range(5):
 z=5.1+row*11.1
 cut(-61.8,-21.15,z,8.0,1.6,9.3)
 for x in [-65.5,-58.1]:detail(x,-21.5,z-.1,.95,1.7,9.5)
 details.append(beam((-65.1,-21.0,z+.5),(-58.5,-21.0,z+8.8),.95))
 details.append(beam((-65.1,-21.0,z+8.8),(-58.5,-21.0,z+.5),.95))
 detail(-61.8,-21.1,z-.2,8.3,1.5,1.0)
 # Cladding joints, kept shallow and above robust solid backing.
 cut(-69.4,0,z+3.5,.6,41,.55)
 cut(-69.4,0,z+7.0,.6,41,.55)
# Abbreviated photographed external bridge landing; its onward off-site extent is omitted.
add(-51,-23.7,17.8,35,17.6,2.0)
for x in [-66,-36]:
 add(x,-30.2,2.3,1.7,1.7,15.6)
 add(x,-30.2,19.5,1.4,1.4,4.3)
for x in np.arange(-64,-35,6):add(float(x),-31.9,19.5,1.2,1.2,4.1)
add(-51,-31.9,22.7,33,1.2,1.2)
# Lift canopy and the shallow front awning strip visible near the lower row.
add(-56,-23.2,28.8,21,9,1.5)
for x in [-65,-47]:add(x,-26.8,19.6,1.5,1.5,9.4)
add(10,-16.2,9.7,103,4.0,1.2)
# Rooftop parapet is open to air, with positive-thickness flat roof beneath.
flat_rim(0,3,55.6,132,36,2.2,1.4)
# Only the long low canopy documented in the official oblique is added.
for x in [-51,-31,-11,9,29,49]:
 for y in [-9,15]:add(x,y,55.6,1.5,1.5,7.0+(y+9)*.039)
for y in [-9,15]:add(-1,y,61.7+(y+9)*.039,103,1.5,1.2)
roof_panel(-1,3,62.9,106,28,2.2)
# Sign plaque is geometry, but tiny unreadable letters are not fabricated.
add(-61.8,-22.0,26.5,9.1,1.1,3.2)

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
