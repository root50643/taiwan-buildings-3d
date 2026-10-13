"""NUU J1 活動中心：官方外觀照片詮釋，毫米單位。Front = -Y.
Run python build_model.py. This source needs no reference images or absolute paths.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection, OpType
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def detail(x,y,z,w,d,h):details.append(box(x,y,z,w,d,h))
def cyl(x,y,z,r,h,rt=None,n=96):return Manifold.cylinder(h,r,r if rt is None else rt,n).translate((x,y,z))
def poly(points,z,h):return CrossSection([points]).extrude(h).translate((0,0,z))
R=155.0;CY=120.0
angles=np.linspace(-21,21,65)
arc=[(R*math.sin(math.radians(t)),CY-R*math.cos(math.radians(t))) for t in angles]
outline=arc+[(arc[-1][0],37),(arc[0][0],37)]
add(0,2,0,150,102,2.4)
# Exterior forecourt terrace and documented broad, curved entrance steps.
for i in range(7):
 r=R+10-i*1.35
 points=[(r*math.sin(math.radians(t)),CY-r*math.cos(math.radians(t))) for t in np.linspace(-17.6,17.6,65)]
 points += [(points[-1][0],-18),(points[0][0],-18)]
 parts.append(poly(points,2.3+i*.5,.65))
# Single solid core; no interior rooms or enclosed cavity shells.
parts.append(poly(outline,5.5,74.5))
# Curved floor bands and parapet are actual printable relief.
for z,h in [(33.5,2.8),(53.7,3.3),(72.7,7.3)]:
 p=[((R+.65)*math.sin(math.radians(t)),CY-(R+.65)*math.cos(math.radians(t))) for t in angles]
 p += [(p[-1][0],-14),(p[0][0],-14)]
 parts.append(poly(p,z,h))
# Curved facade bays. Shallow tangent cuts preserve a solid backing.
def front_window(deg,z,w,h,mullions=1):
 t=math.radians(deg);x=R*math.sin(t);y=CY-R*math.cos(t)
 cuts.append(box(0,0,z,w,1.65,h).rotate((0,0,deg)).translate((x,y,0)))
 for k in range(mullions):
  xx=w*((k+1)/(mullions+1)-.5)
  details.append(box(xx,0,z-.1,.85,1.65,h+.2).rotate((0,0,deg)).translate((x,y+.18,0)))
 details.append(box(0,0,z+h-2,w+.1,1.65,.8).rotate((0,0,deg)).translate((x,y+.18,0)))
for t in [-16,-8,0,8,16]:
 front_window(t,7.0,17.5,12.5,2)
 front_window(t,21.0,17.5,8.5,2)
 front_window(t,40,17.5,9.0,2)
for t in np.linspace(-16.1,18.8,14):front_window(float(t),59.5,5.4,10.4,1)
# Vertical frames of the two lower window rows and modest sign panel.
for t in [-20,-12,-4,4,12,20]:
 rad=math.radians(t);x=R*math.sin(rad);y=CY-R*math.cos(rad)
 parts.append(box(0,0,5.4,1.6,2.8,28.4).rotate((0,0,t)).translate((x,y,0)))
add(0,-35.65,35.8,19,1.2,3.1)
# Left glazed round stair tower with thick mullions, lower drum and cornice.
TX,TY=-58,-24
parts.append(cyl(TX,TY,2.3,13.3,11.6));parts.append(cyl(TX,TY,13.5,12.6,66.8))
for deg in np.arange(145,361,18):
 a=math.radians(deg);x=TX+12.6*math.cos(a);y=TY+12.6*math.sin(a)
 for z in np.arange(15,78,7):
  cuts.append(box(0,0,float(z),3.2,1.6,5.95).rotate((0,0,float(deg+90))).translate((x,y,0)))
for deg in range(160,326,24):
 a=math.radians(deg);cuts.append(box(0,0,4.8,4.2,1.6,6.2).rotate((0,0,deg+90)).translate((TX+13.3*math.cos(a),TY+13.3*math.sin(a),0)))
parts.append(cyl(TX,TY,12.5,14,1.8));parts.append(cyl(TX,TY,79.4,14,3.1))
parts.append(cyl(TX,TY,82.2,12.8,5.5,7.0))
parts.append(cyl(TX,TY,87.5,7.0,1.6))
# Open cupola: six 1.8 mm posts, no enclosed inner shell. Small finial thickened.
parts.append(cyl(TX,TY,88.7,5.1,2.9))
for deg in range(0,360,60):
 a=math.radians(deg);parts.append(cyl(TX+4.35*math.cos(a),TY+4.35*math.sin(a),91.2,.9,11.9,n=24))
parts.append(cyl(TX,TY,102.8,6.9,1.6));parts.append(cyl(TX,TY,104.2,6.5,7.8,1.75))
parts.append(cyl(TX,TY,111.8,1.75,2.6));parts.append(cyl(TX,TY,114.2,.8,2.8,n=24))
# Right plain full-height core. Its unseen rear is left plain.
add(61,-.5,2.3,13,75,84)
# Visible left wing, with narrow upper windows and a recessed middle colonnade.
add(-62,14,5.4,14,49,73.3)
for yy in [0,7,14,21,28]:
 cut(-69.1,yy,44,1.7,4.5,8.6)
 cut(-69.1,yy,65,1.7,1.7,4.5)
 cut(-69.1,yy,15.5,1.7,4.7,6.9)
cut(-69.1,13.8,29,3,40,11.8)
for yy in [-3,5,13,21,29]:detail(-69,yy,28.9,3.1,1.45,12)
# Shallow gable shed roof of the gymnasium, clearly visible behind the front parapet.
# Cross-section in XY is rotated to make a solid prism running in Y.
roof=CrossSection([[(-56,0),(56,0),(56,1.8),(0,9.5),(-56,1.8)]]).extrude(47)
parts.append(roof.rotate((90,0,0)).translate((0,37,78.7)))
# Exterior roof seams, low relief only. Not invented equipment.
for xx in np.arange(-52,53,7):
 hh=1.8+7.7*(1-abs(xx)/56)
 add(float(xx),13.5,78.5+hh,.75,46.8,.5)
# Basic side terrace follows the photographed right entrance ramp, no detached rails.
add(61,-39,2.3,21,9,1.5)
result=Manifold.batch_boolean(parts,OpType.Add)-Manifold.batch_boolean(cuts,OpType.Add)
result=result+Manifold.batch_boolean(details,OpType.Add)
if result.status().name!='NoError':raise RuntimeError(result.status())
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
if not mesh.is_watertight or len(mesh.split(only_watertight=False))!=1:
 print([(q.volume,q.bounds.tolist()) for q in mesh.split(only_watertight=False)]);raise RuntimeError('Single watertight boundary required')
mesh.export(OUT/'model.stl');print('Exported',mesh.extents.tolist(),'mm;',len(mesh.faces),'triangles')
