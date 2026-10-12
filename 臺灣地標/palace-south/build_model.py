"""Palace Museum Southern Branch + Zhimei Bridge.
Original photo-interpreted curved analytical solids; millimeters; no measured replica.
"""
from pathlib import Path
import math,numpy as np,trimesh,manifold3d as m
OUT=Path(__file__).resolve().parent

def box(x,y,z,w,d,h):return m.Manifold.cube((w,d,h),True).translate((x,y,z))
def union(p):return m.Manifold.batch_boolean(p,m.OpType.Add)
def from_mesh(v,f):
    tm=trimesh.Trimesh(v,f,process=True);tm.fix_normals()
    return m.Manifold(m.Mesh(np.array(tm.vertices,dtype=np.float32),np.array(tm.faces,dtype=np.uint32)))
def sample_path(ctrl,n=100):
    # Clamped Catmull-Rom through XY, half width and elevation control points.
    q=np.asarray(ctrl,dtype=float);out=[]
    for tt in np.linspace(0,len(q)-1,n):
        i=min(int(tt),len(q)-2);t=tt-i
        a=q[max(i-1,0)];b=q[i];c=q[i+1];d=q[min(i+2,len(q)-1)]
        out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t**3))
    return np.asarray(out)
def sweep_mass(path):
    # Solid below a bowed roof; no hidden interior shell.
    vs=[];faces=[]
    k=11
    for i,(x,y,w,h) in enumerate(path):
        d=path[min(i+1,len(path)-1),:2]-path[max(i-1,0),:2];d=d/np.linalg.norm(d);nr=np.array([-d[1],d[0]])
        section=[(-1,2.8),(1,2.8)]
        for u in np.linspace(1,-1,k-2):section.append((float(u*.94),float(h-1.4*abs(u)**2)))
        for u,z in section:vs.append([x+nr[0]*w*u,y+nr[1]*w*u,z])
    for j in range(len(path)-1):
        for i in range(k):
            b=(i+1)%k;a=j*k+i;c=j*k+b;d=(j+1)*k+b;e=(j+1)*k+i;faces += [[a,c,d],[a,d,e]]
    for base in [0,(len(path)-1)*k]:
        for i in range(1,k-1):faces.append([base,base+i+1,base+i] if base==0 else [base,base+i,base+i+1])
    return from_mesh(vs,faces)
def bar(a,b,r):
    a=np.asarray(a);b=np.asarray(b);d=b-a;l=np.linalg.norm(d)
    # Convex hull of end spheres yields a robust connected capsule.
    return m.Manifold.batch_hull([m.Manifold.sphere(r,16).translate(a),m.Manifold.sphere(r,16).translate(b)])
def prism_poly(points,depth,cy):return m.CrossSection([points]).extrude(depth).rotate((90,0,0)).translate((0,cy,0))

parts=[box(0,0,1.5,150,150,3)]
# Main original museum only. A later second pavilion seen on the park map is excluded.
ink_path=sample_path([(1,66,2.2,9),(-17,53,10.5,18),(-34,35,17,25),(-29,18,16,24),(-5,8,13,20),(16,0,3.1,10)],130)
ink=sweep_mass(ink_path)
# Glass/steel 'flying white' volume interweaves along the opposing curve.
glass_path=sample_path([(-1,63,3,14),(12,50,8,20),(33,34,12,25),(43,20,10,26),(34,4,8,22),(17,-6,2.8,17)],130)
glass=sweep_mass(glass_path)
# Repeated roof/curtain-wall frames, thickened and fused in the STL itself.
ribs=[]
for idx in range(6,len(glass_path)-4,7):
    p=glass_path[idx];d=glass_path[idx+1,:2]-glass_path[idx-1,:2];d/=np.linalg.norm(d);n=np.array([-d[1],d[0]])
    w=p[2]+.75;h=p[3]+.65
    rings=[]
    for off in [-.55,.55]:
        cx,cy=p[:2]+d*off
        rings.append([cx,cy,w,h])
    ribs.append(sweep_mass(np.array(rings)))
# Horizontal glazing bars follow the true model wall and overlap it in volume.
for z in [8,13,18,23]:
    ids=[i for i,p in enumerate(glass_path) if p[3]>z+2.2][::4]
    for sign in [-1,1]:
        line=[]
        for i in ids:
            p=glass_path[i];d=glass_path[min(i+1,len(glass_path)-1),:2]-glass_path[max(i-1,0),:2];d/=np.linalg.norm(d);n=np.array([-d[1],d[0]])*sign
            w=p[2]*(1-.06*(z-2.8)/(p[3]-4.2))
            xy=p[:2]+n*w
            line.append([xy[0],xy[1],z])
        for a,b in zip(line[:-1],line[1:]):ribs.append(bar(a,b,.43))
parts += [ink,glass]+ribs
# Trapezoidal glazed entry portal under the high linking volume.
portal=prism_poly([(-3,3),(20,3),(17,25),(2,25)],9,7)
portal-=prism_poly([(-.8,5),(17.4,5),(14.9,22.5),(3.8,22.5)],2.4,-.7)
parts.append(portal)
# Roof surface disks are too small at this scale; a few parallel shallow bands
# encode the material change rather than pretending to reproduce 36,000 pieces.
# Open-air center court: solid landscape below the two curved exterior volumes.
parts.append(m.Manifold.cylinder(.8,20,20,80).scale((1,1.4,1)).translate((0,31,2.75)))
# Curved approach and Zhimei Bridge, raised deck intentionally filled to base.
# Solid support below avoids a huge unsupported span at 150 mm desktop scale.
ts=np.linspace(0,1,110)
bridge=[]
for t in ts:
    x=4+21*math.sin(math.pi*t)-1.5*t
    y=-67+69*t
    bridge.append([x,y,3.9,5.1+.7*math.sin(math.pi*t)])
parts.append(sweep_mass(np.array(bridge)))
# Sinuous bow arch on the bridge's outer edge, with thickened hangers.
archpts=[]
for t in np.linspace(0,1,70):
    x=4+21*math.sin(math.pi*t)-1.5*t+3.4
    y=-67+69*t
    z=5.6+12.4*math.sin(math.pi*t)**.88
    archpts.append([x,y,z])
for a,b in zip(archpts[:-1],archpts[1:]):parts.append(bar(a,b,1.05))
for t in np.linspace(.06,.94,19):
    x=4+21*math.sin(math.pi*t)-1.5*t+3.4;y=-67+69*t
    z=5.6+12.4*math.sin(math.pi*t)**.88
    parts.append(bar([x,y,4.9],[x,y,z],.7))
# Continuous inside parapet and broad landing tie the bridge into the main entry.
rail=[]
for t in np.linspace(0,1,65):rail.append([4+21*math.sin(math.pi*t)-1.5*t-3.2,-67+69*t,6.2+.7*math.sin(math.pi*t)])
for a,b in zip(rail[:-1],rail[1:]):parts.append(bar(a,b,.66))
parts.append(box(8,-3,4,15,11,2.5))
result=union(parts).simplify(.004)
assert result.status()==m.Error.NoError
ms=result.to_mesh64();tm=trimesh.Trimesh(np.asarray(ms.vert_properties)[:,:3],np.asarray(ms.tri_verts),process=True);tm.fix_normals()
(OUT/'model.stl').write_text(trimesh.exchange.stl.export_stl_ascii(tm));print(tm.extents,tm.is_watertight,len(tm.faces))
