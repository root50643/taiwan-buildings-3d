"""Photo-interpreted Luce Chapel exterior, mm.
Four doubly curved visual leaves, a higher rear pair, central skylight groove.
Filled beneath the surfaces for robust FDM; not a structural thin-shell replica.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
import manifold3d as m
OUT=Path(__file__).resolve().parent
BASE=3.2

def box(x,y,z,sx,sy,sz):return m.Manifold.cube((sx,sy,sz),True).translate((x,y,z))
def width(y,rear=False):
    t=(y-3)/50 if rear else (y+55)/57
    return 57-12*t if rear else 43+14*t

def height(x,y,rear=False):
    w=width(y,rear);s=min(1,abs(x)/w);h=94 if rear else 84
    # Slight longitudinal twist and changing flare make four curved leaves.
    t=(y-3)/50 if rear else (y+55)/57
    return BASE+h*(1-s)**1.55 + 2.4*math.sin(math.pi*t)*s*(1-s)

def solid_surface(y0,y1,rear=False,lower=0,rim_lift=0,nx=128,ny=58,grooves=False):
    vs=[]
    for j in range(ny+1):
        y=y0+(y1-y0)*j/ny;w=width(y,rear)
        for i in range(nx+1):
            s=-1+2*i/nx;x=s*w;z=height(x,y,rear)-lower+rim_lift
            # Subtle diamond-like tile joints are physically sampled into the skin.
            if grooves and .065<abs(s)<.96 and y0+2<y<y1-2:
                q=abs(s)*18;v=(y-y0)/4.0
                d1=abs((q+v+.5)%1-.5);d2=abs((q-v+.5)%1-.5)
                z-=.24*max(0,1-min(d1,d2)/.11)
            vs.append([x,y,max(BASE,z)])
    N=len(vs);vs += [[x,y,2.85] for x,y,z in vs]
    fs=[]
    def k(i,j):return j*(nx+1)+i
    for j in range(ny):
        for i in range(nx):
            a=k(i,j);b=k(i+1,j);c=k(i+1,j+1);d=k(i,j+1)
            fs += [[a,b,c],[a,c,d],[N+a,N+c,N+b],[N+a,N+d,N+c]]
    # Close all four edges without leaving an inaccessible cavity.
    boundary=[k(i,0) for i in range(nx+1)]+[k(nx,j) for j in range(1,ny+1)]+[k(i,ny) for i in range(nx-1,-1,-1)]+[k(0,j) for j in range(ny-1,0,-1)]
    for a,b in zip(boundary,boundary[1:]+boundary[:1]):fs += [[a,N+b,b],[a,N+a,N+b]]
    tm=trimesh.Trimesh(vs,fs,process=True);tm.fix_normals()
    return m.Manifold(m.Mesh(np.asarray(tm.vertices,dtype=np.float32),np.asarray(tm.faces,dtype=np.uint32)))

front=solid_surface(-55,2,False,grooves=True)
rear=solid_surface(3,53,True,grooves=True)
# The gap between pairs remains a shallow external seam, closed by a lower curved strip.
bridge=solid_surface(1.7,3.3,False,lower=2.1,ny=4)
parts=[box(0,0,1.5,150,150,3),front,rear,bridge]
# Raised border ribs reproduce the heavy concrete edges visible in official photographs.
for y0,y1,rearflag in [(-55,-53,False),(.2,2,False),(3,5,True),(51,53,True)]:
    parts.append(solid_surface(y0,y1,rearflag,rim_lift=.85,nx=128,ny=3))
result=m.Manifold.batch_boolean(parts,m.OpType.Add)
# A manufacturable 1.8-mm central skylight recess, 2.5 mm deep at each ridge.
result-=box(0,-26.4,134.7,1.8,58.8,100)
result-=box(0,28,144.7,1.8,50.4,100)
# Closed front/rear glass faces recessed between stout curved edge bands.
def facade_glazing(y,rearflag):
    w=width(y,rearflag);h=94 if rearflag else 84
    xs=np.linspace(-w+3,w-3,111)
    poly=[[-w+3,4.3],[w-3,4.3]]+[[float(x),max(4.4,height(float(x),y,rearflag)-3)] for x in xs[::-1]]
    shape=m.CrossSection([poly],m.FillRule.EvenOdd).extrude(1.8).rotate((90,0,0)).translate((0,y+.9,0))
    # Connected 1.0-mm mullions are left behind, with no floating bars.
    bars=[]
    for x in np.arange(-44,45,10):bars.append(box(float(x),y,50,1.0,4,110))
    for z in np.arange(9,96,7.5):bars.append(box(0,y,float(z),130,4,1.0))
    return shape-m.Manifold.batch_boolean(bars,m.OpType.Add)
result-=facade_glazing(-54.8,False)
result-=facade_glazing(52.8,True)
# Front doorway uses the characteristic tiny pointed canopy shape, fully fused.
door=m.CrossSection([[[-7,2.8],[-7,13],[-2,18],[2,18],[7,13],[7,2.8]]],m.FillRule.EvenOdd).extrude(3.0).rotate((90,0,0)).translate((0,-53.3,0))
result+=door
result-=box(0,-55.8,8.5,.65,1.0,9)
# Three broad front steps, flush into the common print foundation.
for i in range(3):result+=box(0,-62+i*2.1,3.15+i*.4,27,2.25,1.0+i*.8)
# Cross at the higher rear roof: minimum member thickness 1.9 mm, fused below groove.
result+=box(0,27,100.2,1.9,2.4,16)
result+=box(0,27,103.0,9.2,2.4,1.9)
result=result.simplify(.012)
assert result.status()==m.Error.NoError
mesh=result.to_mesh64();tm=trimesh.Trimesh(np.asarray(mesh.vert_properties)[:,:3],np.asarray(mesh.tri_verts),process=True);tm.fix_normals()
# STL stores float32. Quantize before export, then remove zero-area facets that
# otherwise arise where the sampled edge rib and shell become exactly coincident.
tm.vertices=np.asarray(tm.vertices,dtype=np.float32).astype(np.float64)
tm.merge_vertices()
tm.update_faces(tm.area_faces>1e-10)
tm.remove_unreferenced_vertices();tm.fix_normals()
assert tm.is_watertight and len(tm.split(only_watertight=False))==1
(OUT/'model.stl').write_bytes(trimesh.exchange.stl.export_stl(tm))
print('status',result.status(),'components',len(tm.split()),'dimensions',tm.extents,'faces',len(tm.faces),'genus',result.genus())
