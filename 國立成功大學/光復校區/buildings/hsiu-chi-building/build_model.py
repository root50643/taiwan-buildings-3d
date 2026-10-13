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
# A022 single continuous elongated building; detached neighbours omitted.
add(0,0,0,150,83,3)
add(0,9,2.9,136,30,39)
add(-48,0,2.9,37,48,37)
add(54,7,2.9,28,36,46)
# Long shallow tiled roof, simplified ridge parallel to the long facade.
parts.append(gable(0,0,41,32,100,4).rotate((0,0,90)).translate((8,9,0)))
# Main stair/entrance tower: shallow convex front and stepped top.
pts=[(-26,15),(10,15),(10,-18)]+[(float(x),float(-18-7*(1-((x+8)/18)**2))) for x in np.linspace(10,-26,25)[1:]]
parts.append(C([pts[::-1]]).extrude(53).translate((0,0,2.9)))
# Clearly articulated convex floor bands, not a flat texture; 1 mm proud of curved face.
for z in [31,40,49]:
 band=[(-25.6,-13),(9.6,-13)]+[(float(x),float(-19-7*(1-((x+8)/18)**2))) for x in np.linspace(9.6,-25.6,25)]
 parts.append(C([band[::-1]]).extrude(1.5).translate((0,0,z)))
# Asymmetric stepped top remains curved in plan.
cuts.append(box(-19,0,50,14,52,7))
# Front openings retain substantial piers. No detached shade strips.
for x in [-20,-11,-2,7]:
 for z in [29,37,45]:recess(x,-24, z,4.2,4.7,14)
for x in [-2,5]:recess(x,-24,51.5,3,2.2,14)
# Entrance gateway and broad rising public stair, all fused to base and tower.
add(-8,-25,10,31,14,17)
recess(-8,-32.1,12,23,8.5,3)
recess(-8,-32.1,22,23,3.2,3)
for i in range(7):add(-8,-35+i*.8,3+i,25,8.8-i*.7,1.2)
# Left low volume with arc-headed public facade openings.
# One broad shallow segmental arch with two thick inner piers, as in the source entrance.
ap=[(-64,5),(-32,5)]+[(float(x),float(27+4*(1-((x+48)/16)**2))) for x in np.linspace(-32,-64,33)]
opening=prism(ap,8,-24.1)
for x in [-55,-41]:opening=opening-box(x,-24.1,4,3,10,29)
cuts.append(opening)
for x in [-60,-48,-36]:recess(x,-24.1,34,5.3,3,2)
# Long eastern front and high end tower, distinguished by window bands.
for x in [18,29,37,48,59]:
 for z in [8,18,28]:recess(x,-11.1 if x>=42 else -6.1,z,5.5,4.4,2)
for x in [20,33,46,59]:recess(x,-11.1 if x>=42 else -6.1,37,6.5,3.3,2)
for y in [-4,6,16]:
 for z in [9,21,33,43]:cuts.append(box(68.1,y,z,2,4.5,4.6))
# Back elevations are unverified: plain massing, no invented detail.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.01)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
