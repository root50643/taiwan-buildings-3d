"""Hsinchu historic station exterior, photo-interpreted; units millimeters.
No photographs or third-party geometry are embedded. Regenerate model.stl with pinned dependencies.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
import manifold3d as m
OUT=Path(__file__).resolve().parent

def box(x,y,z,sx,sy,sz):
    return m.Manifold.cube((sx,sy,sz),True).translate((x,y,z))
def hull(pts):return m.Manifold.hull_points(pts)
def cyl_y(x,y,z,r,depth,n=64):return m.Manifold.cylinder(depth,r,r,n).rotate((90,0,0)).translate((x,y+depth/2,z))
def arch(x,y,z,w,h,depth):
    r=w/2
    return box(x,y,z+(h-r)/2,w,depth,h-r)+cyl_y(x,y,z+h-r,r,depth)
def profile_xz(points,y,depth):
    pts=[[x,yy,z] for yy in [y-depth/2,y+depth/2] for x,z in points]
    # Concave polygon extrusion, transform local XY to world XZ.
    return m.CrossSection([points], m.FillRule.EvenOdd).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def hip(cx,cy,w,d,z0,z1,ridge):
    return hull([[cx+s*w/2,cy+t*d/2,z0] for s in [-1,1] for t in [-1,1]]+[[cx+s*ridge/2,cy,z1] for s in [-1,1]])
parts=[box(0,0,1.5,150,80,3)]
# The historic core only. Modern side annexes and platforms are omitted.
body=box(0,5,15.9,128,37,26.4)
body+=box(0,5,4.2,131,40,2.4)
body+=box(0,5,28.3,131,40,1.8)
# Lower wings are flat-topped, with a modest raised terminal parapet on the right.
body+=box(54,-12.9,30,18,2,4)
body+=box(-57,-12.9,29.7,14,2,3.4)
# Arch-top windows: genuinely recessed into the printable wall, with robust frames.
for x in [-57,-44,-29,-16,16,29,44,57]:
    w=6.2 if abs(x)>40 else 7.3
    h=8.3 if abs(x)>40 else 10.4
    z=17.0 if abs(x)>40 else 16.1
    body-=arch(x,-13.35,z,w,h,1.3)
    outer=arch(x,-13.8,z-.6,w+1.1,h+1.2,1.0)-arch(x,-13.8,z,w,h,1.7)
    body+=outer
    body+=box(x,-13.65,z+h*.42,.8,1.4,h*.84)
    body+=box(x,-13.65,z+h*.63,w,1.4,.75)
    # First-floor rectangular windows, all shallow.
    body-=box(x,-13.3,9,w,1.3,7.6)
    body+=box(x,-13.8,9,.8,1.4,7.6)
    body+=box(x,-13.8,8.8,w,1.4,.75)
# Rusticated pilasters and stone courses.
for x in [-63,-36,-23,-10,10,23,36,63]:
    body+=box(x,-13.75,16,2.5,1.8,25)
    for z in np.arange(6,28,3.1):body+=box(x,-14,z,2.9,1.8,.65)
# Side and rear details are explicitly generalized, not a measured reconstruction.
for x in [-52,-38,-24,-10,10,24,38,52]:
    body-=arch(x,23.35,7,6.5,14,1.4)
    body+=box(x,23.4,12,.8,1.2,10)
for x in [-64,64]:
    for y in [-4,10]:
        body-=box(x,y,15,1.4,7,13)
parts.append(body)
# Large hipped green tile roof, interrupted by the two distinctive stepped gables.
parts.append(hip(0,5,97,42,28.5,43.0,51))
# Shallow ridge strip and eaves, thickened for a 0.4-mm nozzle.
parts += [box(0,5,43,51,1.4,1.2),box(0,5,28.7,100,44,1.0)]
for x in [-17.2,17.2]:
    stepped=[(x-8.8,27.8),(x-8.8,30.2),(x-6,30.2),(x-6,32.1),(x-3.8,32.1),(x-3.8,34.2),(x-2.1,34.2),(x-2.1,36),(x+2.1,36),(x+2.1,34.2),(x+3.8,34.2),(x+3.8,32.1),(x+6,32.1),(x+6,30.2),(x+8.8,30.2),(x+8.8,27.8)]
    g=profile_xz(stepped,-14,2)
    g-=cyl_y(x,-15.05,31.0,1.75,1.1)
    g+=cyl_y(x,-15.2,31,2.3,1.1)-cyl_y(x,-15.2,31,1.75,1.8)
    g+=box(x,-15.2,31,.65,1.2,3.5)+box(x,-15.2,31,3.5,1.2,.65)
    parts.append(g)
# Low, continuous street awning. Supported by the wall rather than fragile rods.
for s in [-1,1]:
    awning=hull([[s*x,y,z] for x in [10.5,66] for y,z in [(-14.3,16.3),(-23,14.7),(-14.3,15),(-23,13.4)]])
    parts.append(awning)
    for x in [15,29,43,58,65]:parts.append(box(s*x,-22,8.5,1.5,1.6,11.2))
# Projecting entrance porch and its steep little gable; open front arch is blind at rear.
porch=box(0,-21,16.7,20,17,28.0)
porch+=profile_xz([(-10,30),(0,35.8),(10,30)],-28.6,2.5)
porch-=arch(0,-24.1,3.0,13.7,22.3,14)
frame=arch(0,-29.45,3,16.4,24.2,1.5)-arch(0,-29.45,3,13.7,22.3,3)
porch+=frame
for x in [-9,9]:
    porch+=box(x,-29,16.8,2.7,2.2,28)
    for z in np.arange(5,29,2.8):porch+=box(x,-29.4,z,3.0,2.0,.65)
# Central keystone and a pitched cornice on the front gable.
porch+=profile_xz([(-1.1,25),(1.1,25),(2,29.3),(-2,29.3)],-30,1.2)
porch+=box(0,-29.7,31,2,1.6,3.6)
parts.append(porch)
# Square clock tower at roof ridge; dome has faceted, squat curved silhouette.
tower=box(0,3.3,45.2,9.4,9.4,13.4)
tower+=box(0,3.3,41.1,11.0,11,1.4)
tower+=box(0,3.3,51.9,11.1,11.1,1.3)
for x in [-4.45,4.45]:tower+=box(x,-1.7,46.8,1.1,1,9)
for y in [-1.15,7.75]:tower+=box(-4.8,y,46.8,1,1.1,9)
# Both visible clock faces carry raised hands and recessed dials.
for rear in [False,True]:
    y=8.12 if rear else -1.52
    tower-=cyl_y(0,y,47.7,3.15,1.25)
    tower+=cyl_y(0,y,47.7,3.65,1.0)-cyl_y(0,y,47.7,3.13,2)
    tower+=box(0,y,48.8,.65,1.4,2.4)
    tower+=box(.85,y,47.7,2.25,1.4,.65)
# Closed revolved cap, eight rings, including short pin thicker than the true spire.
profile=[(0,51.8),(5.5,51.8),(5.4,53),(4.5,54.4),(2.9,55.6),(1.4,56.2),(1.15,58),(1,61.5),(0,61.5)]
cap=m.CrossSection([profile]).revolve(64).translate((0,3.3,0))
parts += [tower,cap]
result=m.Manifold.batch_boolean(parts,m.OpType.Add).simplify(.002)
assert result.status()==m.Error.NoError
mesh=result.to_mesh64();tm=trimesh.Trimesh(np.asarray(mesh.vert_properties)[:,:3],np.asarray(mesh.tri_verts),process=True)
tm.fix_normals()
(OUT/'model.stl').write_bytes(trimesh.exchange.stl.export_stl(tm))
print('status',result.status(),'components',len(tm.split()),'bounds',tm.extents,'faces',len(tm.faces),'genus',result.genus())
