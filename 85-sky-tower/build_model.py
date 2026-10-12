"""85 Sky Tower. Photo-interpreted exterior, millimeters. Not survey geometry."""
from pathlib import Path
import math, numpy as np, trimesh, manifold3d as m
OUT=Path(__file__).resolve().parent

def box(x,y,z,sx,sy,sz):return m.Manifold.cube((sx,sy,sz),True).translate((x,y,z))
def profile(points,depth):
 # CCW outline in X,Z; extrusion along Y.
 vs=[[x,y,z] for y in [-depth/2,depth/2] for x,z in points];n=len(points);fs=[]
 for i in range(n):j=(i+1)%n;fs.extend([[i,j,n+j],[i,n+j,n+i]])
 for i in range(1,n-1):fs.extend([[0,i+1,i],[n,n+i,n+i+1]])
 tm=trimesh.Trimesh(vs,fs,process=True);tm.fix_normals()
 return m.Manifold(m.Mesh64(np.array(tm.vertices,np.float64),np.array(tm.faces,np.uint64)))
def crest(x,w,z,depth):
 # Raised outer corners with shallow curved centre, visible on official photograph.
 pts=[(-w/2,z-2),(w/2,z-2)]
 for i in range(25):
  xx=w/2-i*w/24;top=z+1.8+2.6*(abs(xx)/(w/2))**3;pts.append((xx,top))
 return profile(pts,depth).translate((x,0,0))
parts=[box(0,0,1.4,68,46,2.8)]
# Connected lower podium and terrace.
parts += [box(0,0,9.4,59,33,14),box(0,0,17.4,58,33,2),box(0,-4,4.1,64,39,2.8)]
for z in [5.5,8.1,10.7,13.3,15.9]:parts.append(box(0,0,z,59.6,33.6,.7))
# Two legs retain a real through opening above the low central podium.
for s in [-1,1]:
 x=s*19.8
 parts += [box(x,0,49.8,20,27,65.8),crest(x,20,83.7,27)]
 # Recessed-looking facade panel expressed by thickened stiles and a lintel.
 for y in [-13.6,13.6]:
  for dx in [-8.6,8.6]:parts.append(box(x+dx,y,45.3,.9,.75,44))
  parts.append(box(x,y,67,18,.75,1.0))
  for z in np.arange(24.0,82.0,2.2):parts.append(box(x,y,float(z),18.8,.5,.4))
  for dx in [-5.8,-2.9,0,2.9,5.8]:parts.append(box(x+dx,y,53,.45,.48,60))
# The official oblique photograph shows side facade banding; use a robust abstract rhythm.
for sign in [-1,1]:
 for z in np.arange(23,84,2.4):parts.append(box(sign*29.85,0,float(z),.55,25,.38))
 for y in [-9,-4.5,0,4.5,9]:parts.append(box(sign*29.80,y,53,.72,.5,61))
 for z in np.arange(90,134,2.2):parts.append(box(sign*12.55,0,float(z),.55,24,.36))
 for y in [-9,-4.5,0,4.5,9]:parts.append(box(sign*12.50,y,112,.72,.5,44))
# Central podium has curved upturned side shoulders, but does not fill the void.
parts += [box(0,0,21.2,20,25,8),crest(0,20,23,25)]
# Main central tower starts at the skybridge; an open throat is preserved below.
parts += [box(0,0,96.6,24.8,25.6,72.4),box(0,0,62.8,26.5,27,5)]
# Tall stepped side ribs visually separate central column from the two wings.
for s in [-1,1]:parts.append(box(s*10.5,0,103.6,3.7,27.3,68))
for y in [-13.0,13.0]:
 for x in [-9,9]:parts.append(box(x,y,104.4,.8,.7,58))
 for z in np.arange(65.7,135,1.65):parts.append(box(0,y,float(z),18.4,.48,.36))
 for x in np.arange(-7.5,8,2.5):parts.append(box(float(x),y,102.3,.38,.47,63.4))
 # Broader belt zones visible in the official exterior reference.
 for z in [74,105,123]:parts.append(box(0,y,z,24,.65,1.5))
parts += [crest(0,24.8,133.3,25.6),box(0,0,134.8,17,19,3)]
# Recessed cupola and thickened antenna; tip is 1.4 mm diameter.
parts += [m.Manifold.cylinder(2.2,5,4.5,48).translate((0,0,136.7)),m.Manifold.sphere(4.5,48).scale((1,1,1.15)).translate((0,0,139)),m.Manifold.cylinder(5.9,1.35,.7,32).translate((0,0,144.1))]
result=m.Manifold.batch_boolean(parts,m.OpType.Add).simplify(.003)
mesh=result.to_mesh64();tm=trimesh.Trimesh(np.asarray(mesh.vert_properties)[:,:3],np.asarray(mesh.tri_verts),process=True);tm.fix_normals()
(OUT/'model.stl').write_text(trimesh.exchange.stl.export_stl_ascii(tm))
print('Status:',result.status(),'size:',tm.extents,'watertight:',tm.is_watertight,'components:',len(tm.split()),'triangles:',len(tm.faces))
