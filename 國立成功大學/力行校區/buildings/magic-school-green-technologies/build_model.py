"""Photo-informed exterior miniature. Units mm; no survey precision claimed.
Python 3.12; pip install numpy==2.5.4 trimesh==5.1.1 manifold3d==3.5.4
Run python build_model.py from any working directory. Output beside this file.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold as M, CrossSection as C
OUT=Path(__file__).resolve().parent
parts=[];cuts=[]
def box(x,y,z,w,d,h):return M.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def prism(points,depth,y):return C([points]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def gable(x,y,z,w,d,h):return prism([(x-w/2,z),(x+w/2,z),(x,z+h)],d,y)
def hip(x,y,z,w,d,h):
 pts=np.array([[x+sx*w/2,y+sy*d/2,z] for sx in [-1,1] for sy in [-1,1]]+[[x-w/2+min(w,d)*.38,y,z+h],[x+w/2-min(w,d)*.38,y,z+h]])
 return M.hull_points(pts)
def arch(x,y,z,w,h,d):
 r=w/2; spring=z+h-r
 pts=[(x-r,z),(x+r,z)]+[(x+r*np.cos(t),spring+r*np.sin(t)) for t in np.linspace(0,np.pi,25)]
 return prism(pts,d,y)
def disk(x,y,z,r,d):return M.cylinder(d,r,r,48).rotate((90,0,0)).translate((x,y+d/2,z))
def recess(x,y,z,w,h,d=1.6):cuts.append(box(x,y,z,w,d,h))
def arcrecess(x,y,z,w,h,d=1.6):cuts.append(arch(x,y,z,w,h,d))
# Main single research building; roof equipment and ship sculpture deliberately omitted.
add(0,0,0,150,112,3)
add(0,4,2.9,126,82,35)
# Setback upper core and terraced roof-garden envelope from school overview photo.
add(31,26,35,54,36,13)
# Architectural rooftop tower, visible behind the stepped garden in school photos.
add(-31,29,35,27,18,35)
recess(-31,19.8,56,20,9,2.8)
add(-31,18.5,54,30,7,2.2)
# Broad terrace: solid stepped roof, avoiding hidden cavities under landscape layers.
for i in range(8):add(-24,29-i*8,35.2,76,9,25-i*3.1)
# Blue-edged front roof is expressed geometrically with a thin projecting rim.
add(-6,-37,37.6,137,8,2)
add(-62,-6,37.6,5,66,2)
# Sloped edge upstand makes the rising roof visible in the side silhouette.
pts=[(-39,39),(34,61),(34,63),(-39,41)]
parts.append(prism(pts,3,0).rotate((0,0,90)).translate((-64,0,0)))
# Front colonnade/balcony: deep shallow bays in a solid body.
for x in [-51,-32,-13,6,25]:
 recess(x,-37.2,5,15,13,3.8)
 recess(x,-37.2,22,15,12.2,3.8)
 add(x,-39.0,20,18,1.6,2)
# Slender red facade members translated into robust ribs.
for x in [-61,-42,-23,-4,15,34]:add(x,-38,3,2,3,35.5)
# Solid left entry tower with signage area, no letters or logos.
add(-48,-26,3,24,24,35)
# Three curved red entry fins: coarse thick swept arc profiles bonded to the tower.
for k in range(3):
 x=-60+k*6; yy=-48+k*2
 pts=[(x,3),(x+2.2,3),(x+2.2,14),(x+1.2,20),(x-2,25),(x-8,29),(x-14,31),(x-15,29),(x-9,26),(x-4,22),(x-1,17),(x,11)]
 parts.append(prism(pts,2.8,yy))
 # Root-to-building tie represents broad canopy behind the photographed edge.
 add(x-3,(yy-37)/2,27,14,abs(yy+37)+2,2)
# Right side long horizontal shading strip is an exterior architectural band.
for yy in [-22,-9,4,17,30]:
 for zz in [9,22]:cuts.append(box(63.1,yy,zz,1.8,9,6))
# Rear is intentionally plain: complete rear photographs not located.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
