"""Lanyang Museum; photo-interpreted triangulated, interleaved cuesta volumes.
Units mm. Roof/cliff angles follow museum FAQ (20 and 70 degrees).
"""
from pathlib import Path
import math
import numpy as np
import trimesh
import manifold3d as m
OUT=Path(__file__).resolve().parent
A=math.radians(20);C=math.cos(A);S=math.sin(A);V=22.6;GROUND=3.2

def box(x,y,z,sx,sy,sz):return m.Manifold.cube((sx,sy,sz),True).translate((x,y,z))
def world(u,v,y):return [u*C+v*S,y,-u*S+v*C]
def halfwidth(x):return max(.55,.405*(65.5-x))
def block(u0,u1,shift=0,roof=V,inset=0):
    pts=[]
    for u in [u0,u1]:
        vbase=(GROUND+u*S)/C
        for v in [vbase,roof]:
            x=u*C+v*S;w=max(.55,halfwidth(x)-inset)
            for sg in [-1,1]:pts.append(world(u,v,shift+sg*w))
    return m.Manifold.hull_points(pts)
def uv_box(u,v,y,su,sv,sy):
    return box(0,0,0,su,sy,sv).rotate((0,20,0)).translate(world(u,v,y))
def side_shell(u0,u1,shift,side,roof=V,depth=.44):
    pts=[]
    for u in [u0,u1]:
        v0=(GROUND+u*S)/C
        for v in [v0,roof+.6]:
            x=u*C+v*S;w=halfwidth(x)
            for t in [-depth,.8]:pts.append(world(u,v,shift+side*(w+t)))
    return m.Manifold.hull_points(pts)
# Separate stone/glazing strips shift across the triangular plan like fragmented coastal rock.
# Their exact boundaries and widths are photo estimates, not an as-built drawing.
BANDS=[(-62,-56,0,'stone'),(-56,-32,0,'glass'),(-32,-7,3.0,'stone'),(-7,-3,1.2,'glass'),(-3,19,-2.4,'stone'),(19,24,-1.4,'glass'),(24,37,2.6,'stone'),(37,41,1.5,'glass'),(41,49,-1.0,'stone'),(49,54,-1.0,'stone')]
parts=[box(0,0,1.5,150,132,3)]
# A shallow polygonal terrace evokes the lakeside promenade without modeling a literal lake.
terrace=m.CrossSection([[[-72,-60],[63,-9],[66,14],[-59,60],[-72,58]]],m.FillRule.EvenOdd).extrude(.7).translate((0,0,2.85))
parts.append(terrace)
# Deck grooves on the small exposed lakeside terrace are only 0.35 mm deep.
for index,(u0,u1,shift,kind) in enumerate(BANDS):
    roof=V if kind=='stone' else V-.85
    b=block(u0-.08,u1+.08,shift,roof,inset=0 if kind=='stone' else .55)
    cutters=[]
    if kind=='stone':
        # Shallow panel seams on the roof: geometry, not an image texture.
        for u in np.arange(u0+2.8,u1,3.7):cutters.append(uv_box(float(u),roof+.06,shift,.42,.8,180))
        for y in np.arange(-57,58,4.3):cutters.append(uv_box((u0+u1)/2,roof+.06,float(y)+shift,u1-u0+2,.8,.42))
        # Side panel courses follow the same 20-degree construction axes.
        skins=[side_shell(u0-.1,u1+.1,shift,s,roof) for s in [-1,1]]
        shell=m.Manifold.batch_boolean(skins,m.OpType.Add)
        for v in np.arange(-23,roof,4.5):cutters.append(uv_box((u0+u1)/2,float(v),shift,u1-u0+1,.40,180)^shell)
        for u in np.arange(u0+2.8,u1,3.7):cutters.append(uv_box(float(u),0,shift,.36,100,180)^shell)
    else:
        # Larger glazed bays with robust inset mullion grid on roof and side faces.
        for u in np.arange(u0+3.8,u1,4.8):cutters.append(uv_box(float(u),roof+.05,shift,.5,.75,180))
        for y in np.arange(-57,58,7):cutters.append(uv_box((u0+u1)/2,roof+.05,float(y)+shift,u1-u0+1,.75,.5))
        shell=m.Manifold.batch_boolean([side_shell(u0-.1,u1+.1,shift,s,roof,1.0) for s in [-1,1]],m.OpType.Add)
        for v in np.arange(-20,roof,6):cutters.append(uv_box((u0+u1)/2,float(v),shift,u1-u0+1,.5,180)^shell)
        for u in np.arange(u0+3.8,u1,4.8):cutters.append(uv_box(float(u),0,shift,.5,100,180)^shell)
    if cutters:b-=m.Manifold.batch_boolean(cutters,m.OpType.Add)
    parts.append(b)
# Small front doorway block is supported directly by solid mass; no inaccessible interior.
parts.append(box(-55,-39,5.8,7,4.2,5.9))
# Low roadside retaining edge and deliberately simplified entry terrace.
parts.append(box(16,44,4.1,65,2.2,2.5))
# A short stair on the terrace, not an invented tall podium.
for i in range(3):parts.append(box(2,-56+i*1.8,3.2+i*.25,31,2,1.0+i*.5))
result=m.Manifold.batch_boolean(parts,m.OpType.Add)
# The high 70-degree end has a large glazing/stone grid, interpreted from public views.
frontcuts=[]
for v in np.arange(-20,V,4.6):frontcuts.append(uv_box(-62.12,float(v),0,1.0,.42,140))
for y in np.arange(-53,54,4.0):frontcuts.append(uv_box(-62.12,0,float(y),1.0,90,.42))
result-=m.Manifold.batch_boolean(frontcuts,m.OpType.Add)^box(0,0,103.9,500,500,200)
result=result.simplify(.0015)
# Clean flat ground and avoid tapered sub-base fragments at the rear tip.
result-=box(0,0,-50,500,500,100)
assert result.status()==m.Error.NoError
mesh=result.to_mesh64();tm=trimesh.Trimesh(np.asarray(mesh.vert_properties)[:,:3],np.asarray(mesh.tri_verts),process=True);tm.fix_normals()
(OUT/'model.stl').write_bytes(trimesh.exchange.stl.export_stl(tm))
print('status',result.status(),'components',len(tm.split()),'dimensions',tm.extents,'faces',len(tm.faces),'genus',result.genus())
