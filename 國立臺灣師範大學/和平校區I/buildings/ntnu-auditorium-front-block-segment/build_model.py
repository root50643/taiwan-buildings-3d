"""國立臺灣師範大學公開照片近似外觀模型，毫米。
自建幾何；無使用第三方3D mesh。局部範圍及未知部分見 README / sources.json。
Python 3.12; parameters below are printable miniature dimensions, not a survey.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def profile(poly,y,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def arch(x,y,z,w,h,depth):
 r=w/2;spring=z+h-r
 pts=[(x-r,z),(x+r,z),(x+r,spring)]+[(x+r*math.cos(t),spring+r*math.sin(t)) for t in np.linspace(0,math.pi,33)[1:]]
 return profile(pts,y,depth)
def tudor(x,y,z,w,h,depth):
 # Broad four-centre-inspired head, not a Gothic needle.
 pts=[(x-w/2,z),(x+w/2,z),(x+w/2,z+h*.64),(x+w*.46,z+h*.78),(x+w*.33,z+h*.89),(x,z+h),(x-w*.33,z+h*.89),(x-w*.46,z+h*.78),(x-w/2,z+h*.64)]
 return profile(pts,y,depth)
def circle_y(x,y,z,r,d):return Manifold.cylinder(d,r,r,circular_segments=48).rotate((90,0,0)).translate((x,y+d/2,z))
def diamond(x,y,z,w,h,d):return profile([(x,z-h/2),(x+w/2,z),(x,z+h/2),(x-w/2,z)],y,d)
def sill(x,y,z,w):details.append(box(x,y,z,w,1.8,1.5))
def window(x,y,z,w,h,transom=True):
 cut(x,y,z,w,2.5,h)
 details.append(box(x,y-.3,z,w+2,1.5,1.3));details.append(box(x,y-.3,z+h-1.3,w+2,1.5,1.3))
 for xx in [x-w/2-.35,x+w/2+.35]:details.append(box(xx,y-.3,z,1.3,1.5,h))
 details.append(box(x,y+.45,z,1.0,1.4,h))
 details.append(box(x,y+.45,z+h*.49,w,1.4,1.0))
 if transom:details.append(box(x,y+.45,z+h*.79,w,1.4,1.0))
def bar_between(a,b,w,depth):
 # XZ profile with a rectangular cross section; finite 1mm+ decorative relief.
 a=np.array(a);b=np.array(b);v=b-a;n=np.array([-v[1],v[0]])/np.linalg.norm(v)*w/2
 return profile([tuple(a+n),tuple(a-n),tuple(b-n),tuple(b+n)],depth[0],depth[1])
# FRONT BLOCK / ENTRANCE SEGMENT ONLY, excludes the long auditorium and later music-building join.
add(0,0,0,150,76,3)
# Tall central gabled wall and twin two-storey towers.
add(0,12,2.8,86,31,72)
parts.append(profile([(-43,74),(43,74),(43,77),(34,77),(0,96),(-34,77),(-43,77)],12,31))
for x in [-57,57]:
 add(x,8,2.8,27,39,73)
 add(x,8,74,29,41,2.1)
 # Corner stone bands, with alternating visible relief near base.
 for xx in [x-12,x+12]:add(xx,-11.5,3,2.5,2.3,72)
 for z in [8,17,26]:add(x,-11.6,z,27,2.0,1.6)
 # Giant paired windows occur in upper tower only, lower stone panels are not floors.
 for xx in [x-5.8,x+5.8]:window(xx,-11.6,43,7.3,19)
 for xx in [x-5.8,x+5.8]:cut(xx,-11.6,12,7.3,2.0,26)
 details.append(diamond(x,-12.3,67,9,10,2.0))
 # Short side return with actual arched corner exit, selected depth only.
 cuts.append(arch(0,0,3,12,22,12).rotate((0,0,90)).translate(((-1 if x<0 else 1)*68,8,0)))
# Main facade is set BEHIND the open portico by 13mm.
# Three paired arch-topped window groups above the entrance.
for x in [-28,0,28]:
 for xx in [x-5.2,x+5.2]:
  window(xx,-3.5,43,7.4,10,False)
  cuts.append(arch(xx,-3.5,56,7.4,10,2.5))
  details.append(arch(xx,-4,56,9.1,10.8,1.4)-arch(xx,-4.2,55.8,7.4,10.2,2.2))
  details.append(box(xx,-3.7,56,1,1.4,9))
 # Paired-window common Tudor hood over the two rounded lights.
 details.append(tudor(x,-3.8,54.5,23.7,14.5,1.5)-tudor(x,-4,54.1,20.7,13.6,2.5))
 add(x,-4,53.4,24.0,2.0,2.1)
for x in [-14,14]:
 details.append(circle_y(x,-4,73,2.8,1.7))
 cuts.append(circle_y(x,-4.7,73,1,1.1))
window(0,-3.5,81,5.3,10,False)
for z in [83,87,91]:
 # Horizontal gable bands clipped against the gable silhouette.
 band=box(0,-3.7,z,76,1.5,1.1)^profile([(-43,74),(43,74),(43,77),(34,77),(0,96),(-34,77),(-43,77)],-3.7,3)
 details.append(band)
# Deep front loggia, three large rectangular openings and four robust piers.
add(0,-14,29.5,87,23,10)
for x in [-42,-14,14,42]:add(x,-23,3,4.4,6,29)
# Rear doors seen through portico; shallow recesses backed by wall.
for x in [-28,0,28]:
 cut(x,-3.5,6,18,3,20)
 details.append(box(x,-3.5,6,1.2,1.7,20))
# Portico front lintel and decorative peaked caps.
add(0,-25,29,88,2.0,2.2);add(0,-25,39,88,2.3,1.6)
for x in [-14,14]:
 parts.append(profile([(x-5.5,39),(x+5.5,39),(x,44.5)],-25,2.3))
 details.append(diamond(x,-25.5,35.5,3.8,5.4,1.8))
# Broad foyer stairs separated from pillars only by walk-through voids.
for y,h in [(-33,1.1),(-30,2.0),(-27,2.9)]:add(0,y,2.8,91,3.3,h)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert str(solid.status())=='Error.NoError', solid.status()
assert len(solid.decompose())==1, [(q.volume(),q.bounding_box()) for q in solid.decompose()]
m=solid.simplify(.000001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
assert mesh.is_watertight and mesh.is_winding_consistent
print('mm',mesh.extents,'triangles',len(mesh.faces),'watertight',mesh.is_watertight)
