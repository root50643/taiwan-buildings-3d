"""奇美博物館：主館外觀 150 mm FDM 縮景。
觀察官方正面照：中軸三角山牆與列柱門廊、後方圓頂及天使輪廓、
平展兩翼與端部亭閣。深度、背面、非主立面比例為推定；無內部。
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
def cyl(x,y,z0,z1,r,n=32):return m.Manifold.cylinder(z1-z0,r,r,n).translate((x,y,z0))
def roof(x,y,z,w,d,h,tw,td):return m.Manifold.hull_points([(x+sx*ww/2,y+sy*dd/2,zz) for zz,ww,dd in [(z,w,d),(z+h,tw,td)] for sx in [-1,1] for sy in [-1,1]])
def rod(a,b,r):
 return m.Manifold.hull_points(np.vstack([np.asarray(m.Manifold.sphere(r,10).translate(tuple(v)).to_mesh().vert_properties[:,:3]) for v in [a,b]]))
def pediment(x,y,z,w,d,h):
 return m.Manifold.hull_points([(x+xx,y+yy,z+zz) for yy in [-d/2,d/2] for xx,zz in [(-w/2,0),(w/2,0),(0,h)]])
def arch_cut(x,y,z,w,h,depth=.8):
 r=w/2
 return block(x,y,z,z+h-r,w,depth)+m.Manifold.cylinder(depth,r,r,32).rotate((90,0,0)).translate((x,y+depth/2,z+h-r))
def parapet(x,y,z,w,d):
 for yy in [y-d/2,y+d/2]:
  parts.append(block(x,yy,z-.3,z+1.05,w,1.1))
  for xx in np.linspace(x-w/2+.4,x+w/2-.4,max(2,int(w/6))):parts.append(block(float(xx),yy,z-.2,z+1.65,.95,1.2))
 for xx in [x-w/2,x+w/2]:parts.append(block(xx,y,z-.3,z+1.05,1.1,d))
# Architectural slab and ground-stage plinth; no fountain, bridge or garden.
parts += [block(0,0,0,2.4,150,76),block(0,4,2.2,3.8,143,54)]
# Main gallery wings and center rotunda. Rear wall is a conservative solid
# extrapolation, intentionally without invented technical rooms/details.
parts += [block(0,6,3.5,21.4,137,46),block(0,-7,3.5,23.7,26,29)]
# Continuous stone banding gives the photographed two-storey facade.
for z,h in [(3.8,.9),(11.4,.7),(20.5,.7),(21.3,1.0)]:parts.append(block(0,6,z,z+h,139.3,48))
parts.append(block(0,8,21.7,22.8,134,43))
parapet(0,8,22.4,135,44)
# Symmetric projecting bays next to the portico and at terminal pavilions.
for side in [-1,1]:
 x=side*22
 parts += [block(x,-15,3.7,22.1,11,6),block(x,-15,21.8,23,12.6,7.7)]
 for xx in [x-4.6,x+4.6]:parts.append(block(xx,-18.25,4,21.6,.85,.75))
 cuts += [arch_cut(x,-18.08,5,2.9,6.5,.85),arch_cut(x,-18.08,14.2,3.2,6.2,.85)]
 # Long wing windows in two rows. Sills and flat pediments are enlarged relief.
 for xx in np.linspace(side*30,side*54,7):
  cuts += [arch_cut(float(xx),-17.03,5.1,2.0,5.5,.8),block(float(xx),-17.03,14.1,19.5,1.9,.8)]
  parts += [block(float(xx),-17.18,13.65,14.15,2.6,.85),block(float(xx),-17.15,19.4,19.9,2.6,.75)]
  # A central mullion remains as relief, not a detached wire.
  parts.append(block(float(xx),-17.07,14.0,19.6,.46,.8))
 # Terminal pavilions with shallow rounded center crown seen in the photo.
 x=side*62
 parts += [block(x,-4,3.5,23.2,14,29),block(x,-4,22.6,24,15.5,30.3)]
 for xx in [x-6.4,x+6.4]:parts.append(block(xx,-18.55,4,22.9,1.2,.85))
 cuts += [arch_cut(x,-18.5,5.0,5.0,7,.95),arch_cut(x,-18.5,14.5,4.7,6.5,.95)]
 crown=m.Manifold.cylinder(1.9,4.5,4.5,40).rotate((90,0,0)).translate((x,-17.6,23.6)) ^ block(x,-18.6,23.3,29,10,3)
 parts += [crown,block(x,-18.6,23.1,24.1,11,2.6),cyl(x,-18.2,27.3,29,.65),m.Manifold.sphere(.8,16).translate((x,-18.2,29.1))]
 # Engaged side columns and external blind windows, without hidden spaces.
 for yy in [-11,-3,5]:cuts.append(block(side*69.2,yy,6,12,2.5,3.5))
# Rear mass restrained: long stone belts and two shallow terminal returns.
parts += [block(0,29,4.4,5.3,136,.9),block(0,29,19.6,20.5,136,.9)]
# Central projecting six-column portico. All columns link the base and beam;
# true exterior open gaps are intentional and may require local supports.
for i in range(4):
 y0=-31+i*.95
 parts.append(block(0,(y0-17.3)/2,2.3,2.4+(i+1)*.35,26.8-i*.2,-17.3-y0+.15))
parts.append(block(0,-22.5,3.6,4.15,25,12))
for x in np.linspace(-9.8,9.8,6):
 parts += [cyl(float(x),-25,4.0,5.05,1.15),m.Manifold.cylinder(15.5,.87,.75,32).translate((float(x),-25,4.9)),cyl(float(x),-25,20.0,21.3,1.13),block(float(x),-25,20.95,21.8,2.35,2.35)]
parts += [block(0,-22,21.1,22.5,26,12),block(0,-22,22.3,23.25,27.1,12.6),pediment(0,-22,23.1,27.4,13,4.7)]
# Thin inset triangular tympanum is expressed by a shallow face recess.
small=pediment(0,-28.35,23.7,22.5,.8,3.15);cuts.append(small)
# Central doorway on visible rear wall of the portico.
for x in [-6,0,6]:cuts.append(block(x,-21.5,4.2,15.6,2.9,1.0))
# Round drum and smooth dome positioned behind the triangular pediment.
parts += [cyl(0,-6,22.9,28,9.1,64),cyl(0,-6,26.6,28.1,9.8,64)]
# One integrated ribbed dome surface, avoiding microscopic Boolean seams.
# Sixteen broad shallow flutes are part of the dome itself, not loose rods.
v=[];f=[];N=192;R=28
for j in range(R):
 t=(np.pi/2)*(j/(R-1))*.987
 for k in range(N):
  phi=2*np.pi*k/N
  rr=(9.3+.22*max(0,np.cos(16*phi))**8)*np.cos(t)
  v.append((rr*np.cos(phi),-6+rr*np.sin(phi),27.6+9.3*.92*np.sin(t)))
for j in range(R-1):
 for k in range(N):
  a=j*N+k;b=j*N+(k+1)%N;c=(j+1)*N+(k+1)%N;d=(j+1)*N+k;f.extend([(a,b,c),(a,c,d)])
for k in range(1,N-1):f.append((0,k+1,k))
apex=len(v);v.append((0,-6,27.6+9.3*.92))
for k in range(N):f.append(((R-1)*N+k,(R-1)*N+(k+1)%N,apex))
t=trimesh.Trimesh(vertices=v,faces=f,process=True);t.fix_normals()
parts.append(m.Manifold(m.Mesh(np.asarray(t.vertices,np.float32),np.asarray(t.faces,np.uint32))))
parts += [cyl(0,-6,35.63,37.17,1.73,31),cyl(0,-6,36.81,38.3,1.13,29)]
# Robust abstract Glory Angel silhouette, not a reproduction of sculpture detail.
parts += [m.Manifold.sphere(1,20).scale((.9,.7,2.2)).translate((0,-6,39.8)),m.Manifold.sphere(.74,20).translate((0,-6,42.1))]
for s in [-1,1]:
 parts.append(m.Manifold.hull_points([(s*.3,-6.55,39.1),(s*.3,-5.45,39.1),(s*2.7,-6.5,41.6),(s*2.7,-5.5,41.6),(s*1.3,-6.5,39.0),(s*1.3,-5.5,39)]))
parts.append(rod((0,-6,40.6),(1.15,-6.7,42.7),.6))
body=m.Manifold.batch_boolean(parts,m.OpType.Add)-m.Manifold.batch_boolean(cuts,m.OpType.Add)
assert str(body.status()).endswith('NoError'),body.status()
body=body.as_original().simplify(.004)
mesh=body.to_mesh();tm=trimesh.Trimesh(vertices=mesh.vert_properties[:,:3],faces=mesh.tri_verts,process=True)
assert tm.is_watertight and tm.is_winding_consistent
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=P/'model.stl');a=ap.parse_args();tm.export(a.output)
print(json.dumps({'dimensions_mm':tm.extents.tolist(),'triangles':len(tm.faces),'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest()},indent=2))
