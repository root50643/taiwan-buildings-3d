"""赤崁樓：海神廟、文昌閣及高臺。150 mm 長邊，前方為 -Y。
依公開照片判讀的可列印外觀縮景，未測繪比例及遮蔽背面為推定。
所有屋頂為實心；窗扉為外開淺凹，柱欄加粗並與牆體相接。
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
import trimesh
import manifold3d as m
P=Path(__file__).resolve().parent
parts=[];cuts=[]
def box(x,y,z,w,d,h):return m.Manifold.cube((w,d,h),True).translate((x,y,z))
def block(x,y,z0,z1,w,d):return box(x,y,(z0+z1)/2,w,d,z1-z0)
def cyl(x,y,z0,z1,r):return m.Manifold.cylinder(z1-z0,r,r,24).translate((x,y,z0))
def rod(a,b,r):
 a=np.array(a);b=np.array(b)
 return m.Manifold.hull_points(np.vstack([np.asarray(m.Manifold.sphere(r,12).translate(tuple(v)).to_mesh().vert_properties[:,:3]) for v in [a,b]]))
def mesh_solid(v,f):
 t=trimesh.Trimesh(vertices=v,faces=f,process=True);t.fix_normals()
 return m.Manifold(m.Mesh(np.asarray(t.vertices,np.float32),np.asarray(t.faces,np.uint32)))
def roof(x,y,z,w,d,h):
 # Hip-and-gable / 歇山: skirt hips narrow to exposed upper gable ends.
 rings=[(w-3,d-3,z-1,0),(w,d,z+.25,1),(w-.7,d-.7,z+.95,.8),(w*.87,d*.74,z+h*.26,.3),(w*.71,d*.5,z+h*.53,0),(w*.71,.9,z+h,0)]
 v=[]
 for ww,dd,zz,lift in rings:
  for i,(xx,yy) in enumerate([(-ww/2,-dd/2),(0,-dd/2),(ww/2,-dd/2),(ww/2,0),(ww/2,dd/2),(0,dd/2),(-ww/2,dd/2),(-ww/2,0)]):v.append((x+xx,y+yy,zz+(lift if i%2==0 else 0)))
 f=[]
 for k in range(len(rings)-1):
  for i in range(8):
   a=k*8+i;b=k*8+(i+1)%8;c=(k+1)*8+(i+1)%8;dd=(k+1)*8+i;f += [(a,b,c),(a,c,dd)]
 for i in range(1,7):f.append((0,i+1,i))
 q=(len(rings)-1)*8
 for i in range(1,7):f.append((q,q+i,q+i+1))
 parts.append(mesh_solid(v,f))
 # Curved broad ridge; end ornaments are solid tapered silhouettes.
 for xx in np.linspace(-w*.355,w*.355,23)[:-1]:
  xx2=xx+w*.71/22;z1=z+h+.35+.85*(abs(xx)/(w*.355))**5;z2=z+h+.35+.85*(abs(xx2)/(w*.355))**5
  parts.append(rod((x+xx,y,z1),(x+xx2,y,z2),.68))
 for s in [-1,1]:
  parts.append(m.Manifold.hull_points([(x+s*(w*.355+.9),y-.65,z+h+.15),(x+s*(w*.355+.9),y+.65,z+h+.15),(x+s*(w*.355-2),y-.75,z+h),(x+s*(w*.355-2),y+.75,z+h),(x+s*(w*.355+2),y-.55,z+h+3),(x+s*(w*.355+2),y+.55,z+h+3)]))
 # Four thick corner upturns rooted into the eaves, no detached animals.
 for sx in [-1,1]:
  for sy in [-1,1]:parts.append(rod((x+sx*(w/2-4),y+sy*(d/2-2),z+1.1),(x+sx*(w/2+.35),y+sy*(d/2+.25),z+2.8),.67))
def rail(x,y,z,w,d):
 parts.append(block(x,y,z-.2,z+1.75,w,d))
 if w>d:
  for xx in np.linspace(x-w/2+.5,x+w/2-.5,max(2,int(w/3.9))):parts.append(block(float(xx),y,z-.25,z+2.8,1.05,d+.15))
 else:
  for yy in np.linspace(y-d/2+.5,y+d/2-.5,max(2,int(d/3.9))):parts.append(block(x,float(yy),z-.25,z+2.8,w+.15,1.05))
def windows(x,y,z,w,h,n):
 for xx in np.linspace(x-w/2+w/(2*n),x+w/2-w/(2*n),n):cuts.append(box(float(xx),y,z,w/n*.58,.75,h))
# Shared elongated site slice. It deliberately excludes the surrounding garden.
parts += [block(0,0,0,2.6,87,150),block(0,7,2.4,15,72,129),block(0,7,14.6,16,75,131)]
# Main two pavilions, on their retained and connected raised foundation.
for y,w,d,label in [(-29,53,42,'海神廟'),(32,49,40,'文昌閣')]:
 parts += [block(0,y,15.8,17.4,w+7,d+5),block(0,y,17,31.8,w-7,d-7),block(0,y,30.6,33,w+1,d+1)]
 # Outer columns engaged into solid facade; simplified soffit and title panel.
 for yy in [y-(d-7)/2-.4,y+(d-7)/2+.4]:
  for x in np.linspace(-(w-7)/2+1,(w-7)/2-1,6):
   parts += [cyl(float(x),yy,17.1,31.4,.88),cyl(float(x),yy,17.1,18.2,1.1),block(float(x),yy,29.8,31.5,2.35,1.5)]
  windows(0,yy+(-.15 if yy<y else .15),24,w-10,9.2,5)
 parts.append(block(0,y-(d-7)/2-.6,28,29.9,10.5,.7))
 roof(0,y,31.4,w+7,d+5,6.5)
 # Upper storey intersects lower roof, creating the familiar double eaves.
 parts += [block(0,y,33,43.3,w-14,d-14),block(0,y,34.1,35,w-8,d-8)]
 for yy in [y-(d-14)/2-.35,y+(d-14)/2+.35]:
  windows(0,yy,39,w-17,6,5)
  for x in np.linspace(-(w-14)/2+.4,(w-14)/2-.4,6):parts.append(cyl(float(x),yy,34,43.2,.65))
 rail(0,y-(d-10)/2,35,w-9,1.15);rail(0,y+(d-10)/2,35,w-9,1.15)
 # Balcony rails join core with floor plate; no unsupported free columns.
 for x in [-(w-10)/2,(w-10)/2]:rail(x,y,35,1.15,d-9)
 roof(0,y,42.8,w-1,d-2,8.1)
 # Blind side window relief, avoiding invented internal spaces.
 for side in [-1,1]:
  for yy in [y-7,y+7]:cuts.append(box(side*(w-7)/2,yy,24,.85,4,6))
# Terrace rims. Lower front railing and wall-mounted stele relief represent
# the characteristic retained base without claiming individual inscriptions.
rail(-6.6,-58.5,16,60.8,1.3)
rail(36,-58.5,16,2,1.3)
for x in [-36.8,36.8]:rail(x,6.5,16,1.3,129)
rail(0,71.4,16,73,1.3)
for x in np.linspace(-30,18,9):
 parts += [block(float(x),-58.25,2.45,10.5,3.6,2.25),block(float(x),-58.25,10.3,11.3,3.0,2.25)]
# Major front-right public exterior staircase visible in official photo17463.
# Its placement follows the image; width, 13 enlarged risers and run are inferred.
for i in range(13):
 y0=-74+i*1.21
 parts.append(block(29,(y0-58.05)/2,2.45,2.6+(i+1)*13.4/13,10,-58.05-y0+.25))
for x in [23.55,34.45]:
 parts.append(m.Manifold.hull_points([(x+dx,y,z) for dx in [-.62,.62] for y,z in [(-74.4,2.5),(-74.4,4.15),(-58.05,17.7),(-58.05,2.5)]]))
# Deliberately small, shallow exterior brick courses on the exposed base.
for z in [5,8,11,14]:cuts.append(box(0,-57.64,z,66,.35,.32))
body=m.Manifold.batch_boolean(parts,m.OpType.Add)-m.Manifold.batch_boolean(cuts,m.OpType.Add)
assert str(body.status()).endswith('NoError'),body.status()
mesh=body.to_mesh();tm=trimesh.Trimesh(vertices=mesh.vert_properties[:,:3],faces=mesh.tri_verts,process=True)
assert tm.is_watertight and tm.is_winding_consistent
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=P/'model.stl');a=ap.parse_args();tm.export(a.output)
print(json.dumps({'dimensions_mm':tm.extents.tolist(),'triangles':len(tm.faces),'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest()},indent=2))
