"""NUU K3 教學大樓（二）：official exterior-photo interpretation, mm, front=-Y.
Run python build_model.py. Public photo files are not required for rebuilding.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection,OpType
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def detail(x,y,z,w,d,h):details.append(box(x,y,z,w,d,h))
def yz_prism(points,x,width):
 if sum(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points)))<0:points=list(reversed(points))
 return CrossSection([points]).extrude(width).rotate((90,0,0)).rotate((0,0,90)).translate((x,0,0))
# Four visible occupied levels, plus the photographed open rooftop terrace.
add(-3,2,0,150,64,2.4)
add(0,0,2.3,118,29,48.3)
for z in [5.2,17.2,29.2,41.2]:
 for x in np.arange(-52.5,53,10.5):
  cut(float(x),-14.5,z,8.7,1.6,7.5)
  for dx in [-2.2,0,2.2]:detail(float(x)+dx,-14.3,z-.1,.8,1.6,7.7)
  detail(float(x),-14.3,z+5.7,8.8,1.6,.8)
  # The distinctive small inverted-U concrete sunhoods are visible in two obliques.
  add(float(x),-15.4,z+7.25,9.9,2.8,1.25)
  for dx in [-4.55,4.55]:add(float(x)+dx,-15.4,z+5.7,1.0,2.8,2.7)
# Rear: continuous external corridors, substantial concrete bands and slit parapets.
for z in [2.4,14.4,26.4,38.4,50.4]:
 add(0,17,z-.1,118,7.5,1.5)
 if z>3:
  add(0,20,z+.8,118,1.7,3.8)
  for x in np.arange(-52,53,10.4):cut(float(x),20,z+3.0,6.5,2.2,.95)
for x in np.arange(-58.5,59,11.7):add(float(x),18,2.3,1.4,5.0,48.3)
for z in [4.4,16.4,28.4,40.4]:
 for x in [-47,-23.5,0,23.5,47]:
  cut(x,14.5,z,10.0,1.6,8.2)
  detail(x,14.3,z-.1,.9,1.6,8.4)
  detail(x,14.3,z+6.3,10.1,1.6,.8)
# Plain east end wall remains plain as shown in the photos; do not mirror window grids.
# Exposed end flights include broad landings and slit parapets.
for j in range(4):
 z0=2.4+j*12;z1=z0+12;ya,yb=(-11.5,11.5) if j%2==0 else (11.5,-11.5)
 points=[(ya,z0-2),(yb,z1-2),(yb,z1)]
 for i in reversed(range(18)):
  yy0=ya+(yb-ya)*i/18;yy1=ya+(yb-ya)*(i+1)/18;zz=z0+(z1-z0)*(i+1)/18
  points.extend([(yy1,zz),(yy0,zz),(yy0,z0+(z1-z0)*i/18)])
 parts.append(yz_prism(points,-69,10.2))
 parts.append(yz_prism([(ya,z0-.5),(yb,z1-.5),(yb,z1+3.3),(ya,z0+3.3)],-69.4,1.5))
 for y,z in [(ya,z0),(yb,z1)]:
  add(-64.3,y,z-1.0,10.7,5.8,1.3)
  add(-69,y,z-.1,1.6,5.8,3.6)
  cut(-69,y,z+2.0,2.0,3.9,.9)
  cut(-59,y,z+.5,1.6,4.4,7.8)
# Rooftop edge walls and documented broad sloping solar canopy.
add(0,-14.0,50.4,118,1.5,4.1)
add(58.5,2.5,50.4,1.5,34,4.1)
for x in np.arange(-57,59,9.5):
 for y in [-13,18.5]:add(float(x),y,50.4,1.5,1.5,6.6+(y+13)*.065)
roof=box(0,0,0,121,37,1.7).rotate((3.7,0,0)).translate((0,2.5,57.1));parts.append(roof)
for x in np.arange(-56,57,7):cuts.append(box(float(x),0,1.25,.6,37.2,.75).rotate((3.7,0,0)).translate((0,2.5,57.1)))
for y in np.arange(-15,16,6):cuts.append(box(0,float(y),1.25,121.2,.6,.75).rotate((3.7,0,0)).translate((0,2.5,57.1)))
result=Manifold.batch_boolean(parts,OpType.Add)-Manifold.batch_boolean(cuts,OpType.Add)
result=result+Manifold.batch_boolean(details,OpType.Add)
if result.status().name!='NoError':raise RuntimeError(result.status())
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
if not mesh.is_watertight or len(mesh.split(only_watertight=False))!=1:
 print([(q.volume,q.bounds.tolist()) for q in mesh.split(only_watertight=False)]);raise RuntimeError('Single watertight exterior boundary required')
mesh.export(OUT/'model.stl');print('Exported',mesh.extents.tolist(),'mm;',len(mesh.faces),'triangles')
