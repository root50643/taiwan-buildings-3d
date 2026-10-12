"""Chung Tai Chan Monastery: interpreted exterior, millimeters.
Front = -Y, rear = +Y; four peripheral halls, giant central lotus window and crown.
"""
from pathlib import Path
import math,numpy as np,trimesh,manifold3d as m
OUT=Path(__file__).resolve().parent

def box(x,y,z,w,d,h):return m.Manifold.cube((w,d,h),True).translate((x,y,z))
def union(p):return m.Manifold.batch_boolean(p,m.OpType.Add)
def hull(p):return m.Manifold.hull_points(p)
def roof(x,y,z,w,d,h):
    a=hull([[x+sx*w/2,y+sy*d/2,z] for sx in [-1,1] for sy in [-1,1]]+[[x+sx*w*.30,y+sy*d*.15,z+h] for sx in [-1,1] for sy in [-1,1]])
    return a+box(x,y,z-.3,w,d,1.5)+box(x,y,z+h,w*.63,1.5,1)
def flame(cx,cy,z,width,height,depth):
    # Lotus/mandorla silhouette: pointed crown and narrowing foot.
    ts=np.linspace(0,1,64)
    r=width/2*(.33+.69*np.sin(math.pi*ts)**.75)*(1-.20*ts)
    r[-1]=0.02
    pts=[[float(r[i]),float(z+height*ts[i])] for i in range(len(ts))]+[[-float(r[i]),float(z+height*ts[i])] for i in range(len(ts)-1,-1,-1)]
    return m.CrossSection([pts]).extrude(depth).rotate((90,0,0)).translate((cx,cy,0))

parts=[box(0,0,1.5,150,108,3),box(0,4,5,143,84,6),box(0,3,8,136,78,2)]
# Broad ground-level monastery building and front transverse wings.
parts += [box(0,7,19,135,64,22),box(0,-26,16,132,16,17),box(0,-26,25,135,18,2)]
# Rear 'great stairway' triangular shoulders rising toward the central tower.
for sign in [-1,1]:
    x0=sign*16;x1=sign*58
    pts=[[x,y,z] for y in [-10,38] for x,z in [(x0,23),(x1,23),(x1,31),(x0,51)]]
    wing=hull(pts)
    # Two-dimensional repeated blind square windows across the rear sloping facade.
    cuts=[]
    for ax in np.arange(21,58,4.7):
        top=51-(ax-16)*20/42
        for z in np.arange(27,top-1.5,4.7):cuts.append(box(sign*float(ax),38.3,float(z),1.7,1.4,1.7))
    if cuts:wing-=union(cuts)
    parts.append(wing)
    # Continuous diagonal coping follows roof, no fragile floating stair rail.
    parts.append(hull([[sign*x,y,z] for x,z in [(16,51),(58,31)] for y in [-10,38] for z in [z-.45,z+1.5]]))
# Four corner halls; front pair carries tall simplified vajra staffs.
for x in [-57,57]:
    for y in [-20,27]:
        hall=box(x,y,31,17,18,17)
        hall-=box(x,y-9.2,32,7,1.3,7)
        hall-=box(x,y+9.2,32,7,1.3,7)
        parts += [hall,roof(x,y,40,22,22,4.1)]
    parts += [m.Manifold.cylinder(21,1.35,1.15,32).translate((x,-20,44)),m.Manifold.sphere(1.8,32).translate((x,-20,65)),m.Manifold.cylinder(2,1,0.85,24).translate((x,-20,66))]
    # A small ring becomes a relief disk to avoid a fragile 0.2 mm loop.
    parts.append(m.Manifold.cylinder(1.4,2.3,2.3,40).rotate((90,0,0)).translate((x,-19.3,63)))
# Central main tower and its three strongly framed vertical parts.
tower=box(0,5,56,34,35,68)
# Front pointed great window, CLOSED backing, enlarged robust border.
for cy,rot in [(-12.6,0),(22.6,180)]:
    # Both sides visible in official photographs; rear night photograph confirms window.
    cut=flame(0,-10.7,48,19,32,4).rotate((0,0,rot))
    if rot:cut=cut.translate((0,10,0))
    tower-=cut
    frame=(flame(0,-12.2,47,22,34,1.6)-flame(0,-11.5,48,19,32,3))
    if rot:frame=frame.rotate((0,0,180)).translate((0,10,0))
    parts.append(frame)
    ribs=[]
    for x in [-6,-3,0,3,6]:ribs.append(box(x,-10.9,63,.65,1.1,31))
    for z in [53,58,63,68,73]:ribs.append(box(0,-10.9,z,16,1.1,.65))
    rib=union(ribs)
    if rot:rib=rib.rotate((0,0,180)).translate((0,10,0))
    parts.append(rib)
# Side pilasters and horizontal copings.
for x in [-17.5,17.5]:parts.append(box(x,5,59,3.2,37,51))
parts.append(tower)
parts.append(box(0,5,95,28,28,16))
for z,w,d in [(45,39,39),(88,40,40),(95,34,34),(101,29,29)]:
    parts += [box(0,5,z,w,d,2),roof(0,5,z+1,w+1.5,d+1.5,3.5)]
# Front lower hall, layered gateway roofs and tiny thickened entrance columns.
parts += [box(0,-25,26,36,26,34),roof(0,-25,43,42,30,4.2),box(0,-39,19,30,15,20),roof(0,-39,28,35,19,4)]
# Shallow entrance openings retained as surface recesses in the final body.
# Central ceremonial steps terminate within the common plinth.
for i in range(10):parts.append(box(0,-49+i*1.3,3.1+(i+1)*.3,38,1.4,.6*(i+1)))
# Lotus crown: eight solid curved petals surrounding the Mani jewel.
for a in range(0,360,45):
    ts=np.linspace(0,1,30)
    outside=[[5+10*t-3*t*t,99+15*t] for t in ts]
    inside=[[3+9*t-2*t*t,99+13*t] for t in ts[::-1]]
    petal=m.CrossSection([outside+inside]).extrude(6).rotate((90,0,0)).translate((0,3,0)).rotate((0,0,a)).translate((0,5,0))
    parts.append(petal)
parts += [m.Manifold.cylinder(11,7,6,64).translate((0,5,98)),m.Manifold.sphere(7.9,80).scale((1,1,1.06)).translate((0,5,114)),m.Manifold.cylinder(10,1.65,.9,40).translate((0,5,121)),m.Manifold.sphere(1,32).translate((0,5,131))]
result=union(parts)
# Window rows, shallow wall joints, and three entrance doors.
carves=[]
for x in np.arange(-61,64,5):
    if abs(x)<19:continue
    for z in [13,19]:carves.append(box(float(x),-34.1,z,2.1,1,2.5))
for x in [-9,0,9]:carves.append(box(x,-46.4,17,5.5,2,9))
result-=union(carves)
result=result.simplify(.005)
assert result.status()==m.Error.NoError
ms=result.to_mesh64();tm=trimesh.Trimesh(np.asarray(ms.vert_properties)[:,:3],np.asarray(ms.tri_verts),process=True);tm.fix_normals()
(OUT/'model.stl').write_text(trimesh.exchange.stl.export_stl_ascii(tm));print(tm.extents,tm.is_watertight,len(tm.faces))
