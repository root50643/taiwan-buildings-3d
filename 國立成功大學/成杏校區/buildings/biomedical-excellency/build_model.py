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
# Biomedical Excellency building only; hospital and separate public sculpture omitted.
add(0,0,0,150,104,3)
add(0,4,2.9,105,62,121)
# Full-height asymmetrical vertical volumes set forward of central glazed wall.
add(42,-22,2.9,29,24,141)
add(-27,-24,2.9,24,22,130)
add(-47,-23,2.9,18,24,113)
# Photographed tall open recess in left projecting block, backed by solid facade.
cuts.append(box(-27,-33,57,18,17,31))
# High solid screen above entrance; bottom opening retains visible two-storey depth.
add(17,-24,30,28,18,74)
add(30,-24,3,2,18,30)
parts.append(M.cylinder(28,1.5,1.5,24).translate((4,-31,2.9)))
# Exposed middle glazing bands; unobserved rear not fabricated.
for zz in range(8,118,10):
 recess(-6,-27.1,zz,16,7.2,1.8)
 for xx in [-11,-6,-1]:add(xx,-27.6,zz-1,.9,1.7,9.2)
# Upper central glazing spans across the full gap above the entrance screen.
for zz,hh in [(108,7.2),(118,4)]:
 recess(5,-27.1,zz,40,hh,1.8)
 for xx in [-11,-4,3,10,17,24]:add(xx,-27.6,zz-1,.9,1.7,hh+2)
# Windows in the backing wall of the high left recess remain visible.
for zz in [60,70,80]:
 for xx in [-32,-26,-20]:recess(xx,-24.6,zz,4.5,6.8,1.8)
# The right tower has one vertical glazed strip and paired slit windows.
for zz in range(10,138,10):
 recess(32,-34.1,zz,5.8,7.4,1.8)
 for xx in [42,51]:recess(xx,-34.1,zz+2,4.4,1.6,1.8)
# Left-hand vertical window strip, visible alongside stepped opaque masses.
for zz in range(8,111,10):recess(-40,-35.1,zz,4.4,7.2,1.8)
for zz in [13,27,41]:
 for xx in [-30,-20]:recess(xx,-35.1,zz,4.3,2.2,1.8)
# Lower entrance glazing and portal proportions inferred from exterior photos.
for xx in [7,14,21]:recess(xx,-27.1,7,5,15,1.8)

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
