"""NUU I1 資訊大樓與 R1 低層會議中心連通部分：official exterior-photo interpretation, mm, front=-Y.
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
# Main tall information building and low linked conference-center volume.
# Elliptical L1 library is deliberately outside this printable group's boundary.
add(0,0,0,150,110,2.4)
add(-19,8,2.3,76,52,95.1)
# Sparse front windows are the actual visible rhythm, not a repeated invented grid.
for x in [-49,-41,15.0]:cut(x,-18,61,2.9,1.6,8.7)
for x in [-45,-37]:cut(x,-18,41.5,2.8,1.6,8.7)
for z in [21.5,43.5,63]:cut(15,-18,z,3.1,1.6,8.1)
# Left elevation documented in official oblique (3), including grouped narrow slots.
for z in [65.5,84]:
 for yy in [-3,1.5,6,10.5]:cut(-57,yy,z,1.6,2.1,8.3)
 cut(-57,21,z,1.6,10,8.3)
# Right upper side: a narrow row with a larger inset, shown in official oblique (2).
for yy in [-10,-3,4,21,28]:cut(19,yy,63.5,1.6,2.0,7.4)
cut(19,12.5,64,1.6,8.0,7.2)
for yy in [-7]:cut(19,yy,36,1.6,4.8,8.0)
# Right lower attached dark wall with irregularly spaced short apertures.
add(21.1,16,2.3,6,38,55)
for yy,z in [(8,17),(27,19),(3,27),(13,30),(24,26),(4,43),(12,47),(22,44),(29,49)]:cut(24.1,yy,z,1.7,3.5,1.7)
# Front dark vertical tower. Only exterior recesses; the tall screen remains solid backed.
add(0,-23.7,2.3,28,12.2,84)
for z in [23,45,67]:cut(-6.0,-29.8,z,10.4,1.6,2.3)
# Top open-looking loggia is a deep front recess with a solid back against the main block.
add(-12.1,-22.5,85.5,3.2,11,7.9);add(12.1,-22.5,85.5,3.2,11,7.9)
add(0,-22.5,92.1,32,16,2.1)
# Six continuous vertical white fins and two connecting bands are true STL geometry.
for x in [3.4,5.5,7.6,9.7,11.8,13.9]:add(x,-30.8,12.0,1.0,3.0,72)
for z in [11.6,34.3]:add(8.6,-31.1,z,12.5,2.9,2.2)
# Low right continuation of the entrance screen.
add(27,-21.5,2.3,26,12.5,24.5)
for x in [17,20,23,26,29,32,35,38]:cut(x,-27.75,4.2,1.3,1.8,20.5)
# Round front-left volume, with closely spaced vertical fins.
RX,RY=-39,-20.0
roundbody=Manifold.cylinder(33.0,18.5,18.5,96).scale((1,.68,1)).translate((RX,RY,2.3));parts.append(roundbody)
parts.append(Manifold.cylinder(1.6,19.4,19.4,96).scale((1,.68,1)).translate((RX,RY,34.6)))
for deg in np.linspace(184,356,15):
 a=math.radians(float(deg));x=RX+18.5*math.cos(a);y=RY+12.58*math.sin(a)
 # Tangent front slots preserve the solid cylinder and avoid internal enclosed cuts.
 normal=np.array([math.cos(a)/18.5,math.sin(a)/12.58]);normal=normal/np.linalg.norm(normal)
 angle=math.degrees(math.atan2(normal[1],normal[0]))-90
 cuts.append(box(0,0,5.0,2.55,1.55,27.1).rotate((0,0,angle)).translate((x,y,0)))
# Large pale side frame and broad sloping soffit, prominent in both front obliques.
add(-60.2,-19.6,2.3,3.2,26,61)
# Sloping cap runs from high rear to lower front; supports join the main core and frame.
parts.append(yz_prism([(-32.5,59.0),(-6.8,65.0),(-6.8,67.0),(-32.5,61.0)],-61.8,49))
# Rectangular entrance portal with paired robust jambs and shaded opening.
for x in [-12.8,13.8]:add(x,-34.0,2.3,3.7,5.3,15.3)
add(.5,-34,15.8,30.3,5.3,5.7)
cut(0,-29.7,2.8,21.5,1.5,12.0)
for x in [-8,-4,0,4,8]:detail(x,-29.45,2.7,.8,1.5,12.2)
# R1: exposed low roof/terrace between I1 and L1, stopped before the library wall.
# Footprint and heights are photo-estimated; the buried hall interior is not modeled.
add(45,12,2.3,46,46,13.5)
# The lower front terrace tapers beside the entrance and conference-center name wall.
points=[(18,-28),(46,-38),(62,-11),(62,4),(18,4)]
parts.append(CrossSection([points]).extrude(8.5).translate((0,0,2.3)))
add(48,33.8,15.2,45.8,1.5,3.2)
add(66.8,14,15.2,1.5,40,3.2)
# Broad photographed outer stair leading onto the R1 roof terrace.
for i in range(16):add(59,-33+i*1.65,2.3+i*.82,12.0,1.9,.98)
# Stair cheeks are continuous sloping walls, not fragile rods.
for x in [52.3,65.7]:parts.append(yz_prism([(-34,2.3),(-7,15.8),(-7,18.8),(-34,5.3)],x,1.5))
# Parallel inset bands on the rear roof terrace simplify the visible planted strips.
for y in [-1,6,13,20]:cut(48.5,y,15.15,14.0,4.5,1.0)
# Small forecourt step, without duplicating library approach or landscape furniture.
for i in range(3):add(.5,-39.2-i*1.5,2.3,34,1.8,1.4-i*.35)
# Two sloped rooftop solar canopies, with public silhouette but no service equipment.
for x0 in [-28,0]:
 for x in [x0-12,x0,x0+12]:
  for y in [0,27]:add(x,y,97.2,1.4,1.4,4.0+(y/27)*1.25)
 panel=box(0,0,0,27,30,1.6).rotate((2.7,0,0)).translate((x0,13.5,101.6));parts.append(panel)
 for x in [-9,-3,3,9]:cuts.append(box(x,0,1.15,.55,30.2,.7).rotate((2.7,0,0)).translate((x0,13.5,101.6)))
 for y in [-10,0,10]:cuts.append(box(0,y,1.15,27.2,.55,.7).rotate((2.7,0,0)).translate((x0,13.5,101.6)))
# Unseen rear remains an unperforated estimated wall.
result=Manifold.batch_boolean(parts,OpType.Add)-Manifold.batch_boolean(cuts,OpType.Add)
result=result+Manifold.batch_boolean(details,OpType.Add)
if result.status().name!='NoError':raise RuntimeError(result.status())
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
if not mesh.is_watertight or len(mesh.split(only_watertight=False))!=1:
 print([(q.volume,q.bounds.tolist()) for q in mesh.split(only_watertight=False)]);raise RuntimeError('Single watertight exterior boundary required')
mesh.export(OUT/'model.stl');print('Exported',mesh.extents.tolist(),'mm;',len(mesh.faces),'triangles')
