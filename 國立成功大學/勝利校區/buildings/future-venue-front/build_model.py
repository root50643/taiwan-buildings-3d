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
# Present surviving front building only; excludes demolished stacks and Macronix Hall.
add(0,0,0,150,76,2.8)
add(0,5,2.7,140,34,30.5)
add(0,5,33,140,34,1.0)
# Three horizontal glazed bands: subdivided shallow panels keep mullions printable.
for z in [4.8,14.9,25.0]:
 for x in np.arange(-66,67,4.4):
  if z==4.8 and (-50 < x < -18 or 39 < x < 53): continue
  for dz in [0,2.7,5.4]: recess(float(x),-12.1,z+dz,3.5,2.1,1.6)
  # A deliberately coarse single horizontal transom, integral with the wall.
  # Gap between two separate cuts leaves 0.7 mm transom material.
# Horizontal transoms are material left between the separate window recess cuts.
# Entrance is off-centre to the left, as in dated school exterior photos.
for x in [-48,-19]:add(x,-15.2,13.2,1.6,8.0,10.6)
add(-33.5,-15.2,23.0,30.6,8,1.4)
add(-33.5,-15.2,13.1,30.6,8,1.0)
# Broad external stairs are a strong solid staircase, not unsupported filigree.
for i in range(18):add(-33.5,-34.1+i*1.15,2.7,28.5,1.35,0.61*(i+1))
add(-33.5,-12.6,2.7,28.5,3.0,11.0)
# Solid sloped outer parapets replace fragile railings for small-scale print.
for x in [-48.2,-33.5,-18.8]:
 pts=[(-35,3),(-13,14),(-13,15.2),(-35,4.2)]
 # points represent Y,Z; rotate the extruded section to YZ.
 parts.append(prism(pts,1.0,0).rotate((0,0,90)).translate((x,0,0)))
# Secondary ground entrance on the right.
add(46,-12.8,2.8,13,2.7,11.8)
recess(46,-14.3,3.1,10.6,10.1,2.0)
# Unobserved present rear and ends remain plain; historical elevations not current survey.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
