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
# CENTRAL ENTRY SEGMENT ONLY. Cropped ends and rear are deliberately plain.
# Only the observed central bay and one adjacent paired-window panel each side.
add(0,0,0,150,58,3)
add(0,4,2.8,130,31,82)
# Main piers and horizontal storey bands, including 1957 third storey.
for x in [-64,-26,26,64]:add(x,-11.5,3,3.1,2.6,83)
for z in [4,29,56,82]:add(0,-11.6,z,132,2.4,1.6)
for x in [-50,-36,36,50]:
 for z in [8,35,62]:window(x,-11.5,z,10,17)
# Chamfer-sided, three-light two-storey oriel at the central entrance.
bay=[(-22,-11),(-16,-22),(16,-22),(22,-11),(22,4),(-22,4)]
parts.append(CrossSection([bay]).extrude(57).translate((0,0,28)))
add(0,-18,27,46,13,2.4)
for z in [33,62]:
 for x in [-10.5,0,10.5]:window(x,-22,z,7.4,17)
# Polygonal side lights: relief recess on angled cheek, vertically observed.
for s in [-1,1]:
 for z in [34,63]:
  c=box(0,0,0,4.4,2.4,15).rotate((0,0,-s*28.6)).translate((s*18.8,-16.3,z));cuts.append(c)
# Deep Tudor arch goes through the bounded segment; never a flat engraved door.
cuts.append(tudor(0,4,3,26,23,40))
# Entrance voussoir-like broad outer hood, backed onto wall and bay.
details.append(tudor(0,-12.7,2.9,30,25.3,2.8)-tudor(0,-13,2.7,26,23.6,3.8))
# Central decorative panels; raised diamonds and simplified quatrefoils are wall-backed.
for x in [-10.5,0,10.5]:
 cut(x,-22,52,7.8,2.0,7.2)
 details.append(diamond(x,-22.2,55.6,5.6,5.6,3.2))
 cuts.append(circle_y(x,-22.7,55.6,1.3,2.0))
# Stout stone dividing strips between long window tiers.
for x in [-16.2,-5.2,5.2,16.2]:add(x,-22,30,1.8,2.0,53)
# Original battlement-shaped parapet caps central projection; printed slots >= 2mm.
add(0,-15,84,44,17,5)
for x in [-18,0,18]:add(x,-15,88,8,17,3.8)
for x in [-64,-26,26,64]:add(x,-11.5,83,4.2,3.8,4)
# Low central gable visible behind the crest; cut flat at back of selected segment.
parts.append(profile([(-18,84),(18,84),(0,94)],2,7))
# Steps and plinth across opening.
for y,h,w in [(-25,1.0,34),(-23,1.8,32),(-21,2.6,30)]:add(0,y,2.8,w,2.8,h)

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
