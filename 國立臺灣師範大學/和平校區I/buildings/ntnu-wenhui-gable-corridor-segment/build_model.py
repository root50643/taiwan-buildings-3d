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
# OBSERVED GABLE + THREE-BAY BAT CORRIDOR SEGMENT, bounded rear cut plane.
# Overall length is deliberately cropped: does not claim all six original corridor columns.
add(0,0,0,150,101,3)
# Hall body and prominent raised base.
add(-8,8,2.8,100,65,7)
add(-8,8,9.5,96,65,45)
# Asymmetric roof: ridge over hall, extended down over eastern corridor.
roof=[(-59,54),(-11,82),(68,39),(68,42),(-11,85),(-59,57)]
parts.append(profile(roof,8,70))
parts.append(profile([(-56,53),(40,53),(40,54.74),(-11,82.5),(-56,56.25)],8,65))
# The gable below extended roof is solid over the hall only; corridor beyond remains open.
# Main end-wall four tall windows, central pair grouped beneath decorated lintel.
for x in [-43,-19,-7,25]:window(x,-24.5,12,8.2,29)
for x in [-29,9]:
 add(x,-25.2,10,4.2,3.4,35)
 parts.append(profile([(x-3,44),(x+3,44),(x+2,47),(x-2,47)],-25.2,3.4))
add(-13,-25.2,41.4,30,2.5,2.0)
# Six small rosette impressions, simplified with millimetre-safe circular relief.
for x in [-25,-20,-15,-10,-5,0]:
 details.append(circle_y(x,-25.7,44.4,1.35,1.3))
# Major round gable window and reinforced six-point motif, backed relief not floating lattice.
cuts.append(circle_y(-11,-25.2,64,6.4,3.0))
details.append(circle_y(-11,-25.6,64,7.6,2.5)-circle_y(-11,-25.8,64,6.4,3.3))
for tri in [[(-11,69.1),(-15.4,61.5),(-6.6,61.5)],[(-11,58.9),(-15.4,66.5),(-6.6,66.5)]]:
 for i in range(3):details.append(bar_between(tri[i],tri[(i+1)%3],1.05,(-24.1,2.0)))
# A recessed strip strengthens relief in the wall; no hidden interior chamber.
# Three actual-style columns sampled from the six-column arcade: selected end piece only.
for y in [-20,9,38]:
 add(59,y,3,4.8,5.2,40)
 add(59,y,3,7.1,7.2,2)
 add(59,y,37,7.8,7.8,3.4)
 # Bat-wing sloping transverse beam toward the wall, preserving the tall open passage.
 brace=[(39,48),(41,48),(59,37),(61,37),(61,40),(39,54)]
 parts.append(profile(brace,y,3.6))
 add(40,y,10,2.8,4.4,39)
# Corridor outer longitudinal beam and floor only, no filling of walk-through void.
add(59,8,38,5.3,66,3.2)
add(51,8,2.8,29,68,2.2)
# Two observed-style side entrance/window bays beneath the eave. Side recesses are larger than 0.8mm.
for y in [-5,23]:
 cut(40,y,12,2.6,14,26)
 details.append(box(40.4,y,12,1.7,1.2,26))
 details.append(box(40.4,y,30,1.7,14,1.2))
# Opposite unseen side and rear section cut are intentionally blank.

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
