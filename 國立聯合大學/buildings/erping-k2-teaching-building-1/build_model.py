"""NUU K2 教學大樓（一）：official exterior-photo interpretation, mm, front=-Y.
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
# One solid plinth; this is an independent miniature, not campus-wide scale.
add(-3,0,0,150,64,2.4)
add(0,0,2.3,120,34,38.9)
# Three visible rows on the long window side.
for z in [5.8,18.5,31.2]:
 for x in np.arange(-54,55,10.8):
  cut(float(x),-17,z,8.5,1.5,7.9)
  for dx in [-2.1,0,2.1]:detail(float(x)+dx,-16.8,z-.1,.75,1.45,8.1)
  detail(float(x),-16.8,z+5.9,8.6,1.45,.75)
  # Photograph-backed concrete sills, not modeled service equipment.
  add(float(x),-17.6,z-.65,8.9,1.5,.8)
for x in np.arange(-59,60,10.8):add(float(x),-17.35,2.3,1.15,1.1,38.9)
# Opposite long elevation has the documented dense shading fins.
for z in [5.8,18.5,31.2]:
 for x in np.arange(-54,55,10.8):
  cut(float(x),17,z,8.7,1.5,8)
  detail(float(x),16.8,z-.1,.8,1.45,8.2)
 for x in np.arange(-59,60,5.4):add(float(x),17.8,z-.6,1.15,3.0,10.1)
# Opposite entrance end, documented by the complete 教學大樓(1) sign.
for z in [18.5,31.2]:
 cut(60,0,z,1.6,9.2,8.2)
 for yy in [-2.3,0,2.3]:detail(59.8,yy,z-.1,1.5,.8,8.4)
 detail(59.8,0,z+6,1.5,9.3,.8)
cut(60,0,2.8,1.6,10.4,10.1)
for yy in [-3.3,0,3.3]:detail(59.8,yy,2.7,1.5,.8,10.3)
add(62.2,0,13.0,5.2,13.0,1.3)
for i in range(4):add(65.6-i*1.05,0,2.3+i*.35,1.4,13,.5)
# Stair end: photographed exposed alternating flights, not a solid invented tower.
# Flight slabs and parapets are thickened for FDM; support is needed below flights.
for j in range(3):
 z0=2.4+j*12.8;z1=z0+12.8;ya,yb=(-12,12) if j%2==0 else (12,-12)
 points=[(ya,z0-2.0),(yb,z1-2.0),(yb,z1)]
 for i in reversed(range(18)):
  yy0=ya+(yb-ya)*i/18;yy1=ya+(yb-ya)*(i+1)/18;zz=z0+(z1-z0)*(i+1)/18
  points.extend([(yy1,zz),(yy0,zz),(yy0,z0+(z1-z0)*i/18)])
 parts.append(yz_prism(points,-70,10.2))
 parts.append(yz_prism([(ya,z0-.5),(yb,z1-.5),(yb,z1+2.7),(ya,z0+2.7)],-70.4,1.4))
 for y,z in [(ya,z0),(yb,z1)]:
  add(-65,y,z-1.0,10.5,5.7,1.2)
  add(-70,y,z-.1,1.5,5.7,2.9)
  cut(-60,y,z+.5,1.6,4.0,7.8)
add(-65,12,41.3,11.0,7.7,1.5)
# Main roof is a shallow barrel canopy; near end is a separate sloped solar plane.
# Solid gable-end cheeks and columns support the roof without an enclosed cavity.
for x in [-59.2,35.2]:
 points=[(-17.7,41),(-17.7,42.2)]+[(float(y),42.2+5.3*(1-(float(y)/17.7)**2)) for y in np.linspace(-17.7,17.7,33)]+[(17.7,41)]
 parts.append(yz_prism(points,x,1.4))
ys=np.linspace(-18.4,18.4,49)
def roofz(y):return 42.4+5.3*(1-(y/18.4)**2)
profile=[(float(y),roofz(float(y))) for y in ys]+[(float(y),roofz(float(y))-1.5) for y in reversed(ys)]
parts.append(yz_prism(profile,-60,96.7))
for x in np.arange(-58,37,9):
 for y in [-16.7,16.7]:add(float(x),y,40.9,1.3,1.3,2.0)
# True engraved panel grid on the curved roof; broad enough to survive reduction.
for x in np.arange(-54,36,9):
 outer=[(float(y),roofz(float(y))-.4) for y in ys]+[(float(y),roofz(float(y))+.4) for y in reversed(ys)]
 cuts.append(yz_prism(outer,float(x),.55))
for y in [-12,-6,0,6,12]:cut(-11.6,y,roofz(y)-.35,95,.55,.8)
# Smaller flat/sloped solar roof over the entrance end.
for x in [40,50,59]:
 for y in [-16,16]:add(x,y,41.0,1.35,1.35,3.8+(y+16)*.045)
roof=box(0,0,0,24.6,36.5,1.5).rotate((2.6,0,0)).translate((48.5,0,44.2));parts.append(roof)
for x in [-9,-3,3,9]:cuts.append(box(x,0,1.08,.55,36.7,.7).rotate((2.6,0,0)).translate((48.5,0,44.2)))
for y in [-12,-6,0,6,12]:cuts.append(box(0,y,1.08,24.8,.55,.7).rotate((2.6,0,0)).translate((48.5,0,44.2)))
for group,name in [(parts,'parts'),(cuts,'cuts'),(details,'details')]:
 for i,m in enumerate(group):
  if m.status().name!='NoError':print('BAD',name,i,m.status(),flush=True)
result=Manifold.batch_boolean(parts,OpType.Add)-Manifold.batch_boolean(cuts,OpType.Add)
result=result+Manifold.batch_boolean(details,OpType.Add)
if result.status().name!='NoError':raise RuntimeError(result.status())
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
if not mesh.is_watertight or len(mesh.split(only_watertight=False))!=1:
 print([(q.volume,q.bounds.tolist()) for q in mesh.split(only_watertight=False)]);raise RuntimeError('Single watertight exterior boundary required')
mesh.export(OUT/'model.stl');print('Exported',mesh.extents.tolist(),'mm;',len(mesh.faces),'triangles')
