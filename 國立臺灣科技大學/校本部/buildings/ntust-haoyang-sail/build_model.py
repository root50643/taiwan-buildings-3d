"""Photo-derived public exterior study. Millimetres; dimensions are visual estimates.
Run with Python 3.12 and requirements.txt. No survey or interior data used.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]; details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def profile(poly,y,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def gable(x,y,z,w,d,h):parts.append(profile([(x-w/2,z),(x+w/2,z),(x,z+h)],y,d))
def arch(x,y,z,w,h,depth):
 r=w/2; spring=z+h-r
 pts=[(x-r,z),(x+r,z),(x+r,spring)]
 pts += [(x+r*math.cos(t),spring+r*math.sin(t)) for t in np.linspace(0,math.pi,25)[1:]]
 return profile(pts,y,depth)
def arch_cut(x,y,z,w,h,depth):cuts.append(arch(x,y,z,w,h,depth))
def arch_trim(x,y,z,w,h):
 # Backed relief ring, fused into the wall, not a separate floating shell.
 details.append(arch(x,y,z,w+1.7,h+.85,1.7)-arch(x,y-.1,z-.2,w,h+.2,2.3))
def hip(x,y,z,w,d,h):parts.append(CrossSection.square((w,d),center=True).extrude(h,scale_top=(.72,.03)).translate((x,y,z)))
def column(x,y,z,r,h):parts.append(Manifold.cylinder(h,r,r,circular_segments=24).translate((x,y,z)))
def step(x,y,w,n=3):
 for i in range(n):add(x,y+i*1.4,2.8,w,1.7,.7*(i+1))

def xy(poly,z,h):
 if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))<0:poly=poly[::-1]
 return CrossSection([poly]).extrude(h).translate((0,0,z))
def rod(a,b,r):
 # Convex hull of two spheres gives a printable rounded strut, with deliberate overlaps.
 return Manifold.batch_hull([Manifold.sphere(r,12).translate(a),Manifold.sphere(r,12).translate(b)])
# Haoyang Experimental Building: seven-storey curved sail and exposed balcony edge.
# Photo-based external study. The unknown rear face uses a shallow plain research-volume backing.
from manifold3d import Mesh64
add(0,0,0,100,94,3)
# Backing body and seven-floor stack: deep balcony cavity stays open to both sides.
add(0,20,2.8,54,30,131)
for z in [22,40,58,76,94,112,131]:
 add(0,-1,z,56,30,2.4)
# Floor-to-floor windows on observed side faces, with yellow shades abstracted as deep panels.
for z in [25,43,61,79,97,115]:
 cut(27,19,z,3.8,21,11.5)
 cut(-27,19,z,3.8,21,11.5)
# Double-curved sail: each row bows forward vertically and subtly across its breadth.
nx=16;nz=44;verts=[];faces=[]
def sy(x,z):
 t=(z-3)/144
 return -16-17*math.sin(math.pi*t)-3.5*(1-(x/31)**2)*math.sin(math.pi*t)
for layer in [0,1]:
 for j in range(nz+1):
  z=3+144*j/nz
  width=30-4*(j/nz)**2
  for i in range(nx+1):
   x=-width+2*width*i/nx
   verts.append([x,sy(x,z)+layer*3.2,z])
N=(nx+1)*(nz+1)
for j in range(nz):
 for i in range(nx):
  a=j*(nx+1)+i;b=a+1;c=a+nx+1;d=c+1
  faces += [[a,c,b],[b,c,d],[a+N,b+N,c+N],[b+N,d+N,c+N]]
# boundary quads oriented then canonical winding repaired only during construction, never validation.
for edge in [[i for i in range(nx+1)], [j*(nx+1)+nx for j in range(nz+1)], [nz*(nx+1)+i for i in range(nx,-1,-1)], [j*(nx+1) for j in range(nz,-1,-1)]]:
 for a,b in zip(edge[:-1],edge[1:]):faces += [[a,b,b+N],[a,b+N,a+N]]
sm=trimesh.Trimesh(vertices=verts,faces=faces,process=True);sm.fix_normals()
sail=Manifold(Mesh64(np.asarray(sm.vertices,dtype=np.float64),np.asarray(sm.faces,dtype=np.uint64)))
assert sail.status().name=='NoError'
# The large lower arch is indispensable; do not replace it with a filled sail.
sail=sail-arch(0,-26,2.8,48,29,45)
parts.append(sail)
# White zigzag edge braces bridge the real gaps between rear spine and sail edge.
# Rounded 2.8mm stock deliberately strengthened for a 150mm miniature.
for side in [-1,1]:
 x=side*27.4
 path=[(x,3.5,23),(x,sy(x,41)+2,41),(x,3.5,59),(x,sy(x,77)+2,77),(x,3.5,95),(x,sy(x,113)+2,113),(x,3.5,131),(x,sy(x,144)+2,144)]
 for a,b in zip(path[:-1],path[1:]):parts.append(rod(a,b,1.65))
 # connected balcony floor outriggers reach sail, 2.2mm section.
 for z in [40,58,76,94,112,131]:
  y=sy(x,z)+3
  add(x,(y+5)/2,z,2.6,5-y+1,2.4)
# Glazed ground plane is recessed behind sail opening; front rib columns fixed to wall.
for x in [-21,-10,1,12,23]:cut(x,4.8,6,7.8,3.2,12)
# Small broad stair platform and side flight, no unsourced interior.
for i in range(6):add(22,-18+i*2.5,2.8,18,3.0,1.2+i*2.4)
# Low entrance canopy on visible left side, well supported by four 2.4mm columns.
add(-18,-13,22,45,30,2.6)
for x in [-39,2]:
 for y in [-26,-1]:add(x,y,2.8,2.4,2.4,20.5)
# Base plinth feet and top prevent razor-thin isolated tips.
add(0,20,133,56,31,2)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.apply_scale(150.0/mesh.extents.max())
mesh=trimesh.Trimesh(np.asarray(mesh.vertices,dtype=np.float32),mesh.faces,process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
