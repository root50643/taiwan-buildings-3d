"""Weiwuying exterior miniature: continuous waving roof, sculpted ground-reaching cores.
Photo-interpreted proportions; not a measured replica. Coordinates are millimeters.
"""
from pathlib import Path
import numpy as np, math, trimesh, manifold3d as m
OUT=Path(__file__).resolve().parent

def box(x,y,z,a,b,c):return m.Manifold.cube((a,b,c),True).translate((x,y,z))
# Analytic exterior surface; the lobes below the canopy follow the publicly shown theatre cores.
CORES=[(-44,24,21,20),(-42,-23,18,17),(-5,-23,19,17),(34,-20,23,20),(40,25,20,19)]
def surfaces(x,y):
 top=16.5+9.5*np.exp(-((x+26)/29)**2-((y-12)/26)**2)+7*np.exp(-((x-27)/25)**2-((y+8)/25)**2)
 top-=6*np.exp(-((x+44)/10)**2-((y+46)/9)**2)
 # Open-air theatre scallop and coarse concentric seating at the park-side edge.
 r=np.sqrt((x-15)**2+(y-51)**2)
 bowl=5.5+max(0,r-6)*.66
 if r<27:top=min(top,bowl)
 d2=min(((x-cx)/rx)**2+((y-cy)/ry)**2 for cx,cy,rx,ry in CORES)
 q=max(0,min(1,(d2-.32)/.85));q=q*q*(3-2*q)
 bottom=min(top-2.8,2.2+12*q)
 return top,bottom
# A gently rounded rectilinear canopy, with a curved underside around the five ground-reaching cores.
NX,NY=173,125;verts=[]
for lower in [False,True]:
 for j in range(NY):
  v=-1+2*j/(NY-1)
  for i in range(NX):
   u=-1+2*i/(NX-1)
   # Soft corners, preserving the long straight canopy edges visible in the aerial photograph.
   x=68*u*(1-.025*abs(v)**12);y=47*v*(1-.025*abs(u)**12)
   top,bottom=surfaces(x,y);verts.append([x,y,bottom if lower else top])
N=NX*NY;faces=[]
for j in range(NY-1):
 for i in range(NX-1):
  a=j*NX+i;b=a+1;c=a+NX;d=c+1
  faces.extend([[a,b,d],[a,d,c],[N+a,N+d,N+b],[N+a,N+c,N+d]])
boundary=list(range(NX))+[j*NX+NX-1 for j in range(1,NY)]+[(NY-1)*NX+i for i in range(NX-2,-1,-1)]+[j*NX for j in range(NY-2,0,-1)]
for a,b in zip(boundary,boundary[1:]+boundary[:1]):faces.extend([[a,N+a,N+b],[a,N+b,b]])
tm=trimesh.Trimesh(verts,faces,process=True);tm.fix_normals();roof=m.Manifold(m.Mesh(np.asarray(tm.vertices,np.float32),np.asarray(tm.faces,np.uint32)))
# Glazed edge bands visible on the documented front and right facades.
# Cut a shallow inset following the waving edge; keep at least 1 mm below and 0.65 mm above.
def band(front,start,end):
 vs=[];steps=130
 for t in np.linspace(start,end,steps):
  if front:
   u=t/66.3;x=t;y=-47*(1-.025*abs(u)**12);inside=(0,.68);outside=(0,-1.0)
  else:
   v=t/45.825;y=t;x=68*(1-.025*abs(v)**12);inside=(-.68,0);outside=(1,0)
  z,_=surfaces(x,y)
  for dx,dy,h in [(*outside,-1.8),(*inside,-1.8),(*inside,-.65),(*outside,-.65)]:vs.append([x+dx,y+dy,z+h])
 fs=[]
 for i in range(steps-1):
  for k in range(4):a=i*4+k;b=i*4+(k+1)%4;c=(i+1)*4+(k+1)%4;d=(i+1)*4+k;fs.extend([[a,b,c],[a,c,d]])
 fs.extend([[0,2,1],[0,3,2],[(steps-1)*4,(steps-1)*4+1,(steps-1)*4+2],[(steps-1)*4,(steps-1)*4+2,(steps-1)*4+3]])
 t=trimesh.Trimesh(vs,fs,process=True);t.fix_normals();return m.Manifold(m.Mesh64(np.array(t.vertices,np.float64),np.array(t.faces,np.uint64)))
roof-=band(True,-29,65)
roof-=band(False,-44,44)
# Robust mullions subdivide the glazing rhythm. These are unioned to the same STL surface.
for x in np.arange(-27,64,3.5):
 y=-47*(1-.025*abs(x/66.3)**12);z,_=surfaces(x,y)
 roof+=box(x,y+.18,z-1.22,.7,.6,1.5)
for y in np.arange(-41,44,3.5):
 x=68*(1-.025*abs(y/45.825)**12);z,_=surfaces(x,y)
 roof+=box(x-.18,y,z-1.22,.6,.7,1.5)

# Shallow roof light-well depressions, kept open to outside without separate internal shells.
for x,y,w,d in [(-35,8,7,5),(0,14,8,6),(36,8,6,4)]:
 z,_=surfaces(x,y);roof-=box(x,y,z+.2,w,d,3)
parts=[box(0,0,1.4,150,118,2.8),roof]
# Low plinth edges remain below the open Banyan Plaza, not a solid rectangular building mass.
parts.append(box(0,-48,3.7,132,3,2.3))
# The outdoor theatre's stepped seats follow a limited semicircular segment.
for r in np.arange(9,25,2.3):
 z=5.5+(r-6)*.66
 cs=m.CrossSection.circle(float(r),96)-m.CrossSection.circle(float(r-1.3),96)
 ring=cs.extrude(1.5).translate((15,51,z-.7))
 ring ^= box(15,35,z,56,30,5)
 # Intersect with roof footprint and allow each strip to fuse into the bowl.
 parts.append(ring)
result=m.Manifold.batch_boolean(parts,m.OpType.Add).simplify(.015)
mesh=result.to_mesh64();tm=trimesh.Trimesh(np.asarray(mesh.vert_properties)[:,:3],np.asarray(mesh.tri_verts),process=True);tm.fix_normals()
(OUT/'model.stl').write_text(trimesh.exchange.stl.export_stl_ascii(tm))
print('Status:',result.status(),'size:',tm.extents,'watertight:',tm.is_watertight,'components:',len(tm.split()),'triangles:',len(tm.faces))
