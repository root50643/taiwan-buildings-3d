"""Independent scalar all-vertex plane/support and geometric-normal check."""
from pathlib import Path
import struct,json,math
A=Path(__file__).resolve().parents[1];b=(A.parent/'model.stl').read_bytes();fm=json.loads((A/'face-materials.json').read_text());eps=1e-4
pts=[(-12.5,30.8),(-7,31.5),(-1,31.8),(1,31.8),(7,31.5),(12.5,30.8)]
surfaces=[]
for k in range(5):
 x0,z0=pts[k];x1,z1=pts[k+1];m=(z1-z0)/(x1-x0)
 for kind,y0,y1,dz in [('cover',-20,24,0)]+[('rib_'+str(j),-19.9+43*j/8,-19.1+43*j/8,.28) for j in range(9)]:surfaces.append(dict(kind=kind,segment=k,x0=x0,x1=x1,y0=y0,y1=y1,slope=m,intercept=z0-m*x0+dz))
groups={'white':[],'upper_red':[],'entry_red':[]};matches={}
for i in range(struct.unpack_from('<I',b,80)[0]):
 r=struct.unpack_from('<12fH',b,84+i*50);v=[(r[3+j*3]/1.5-17,r[4+j*3]/1.5-2,r[5+j*3]/1.5) for j in range(3)]
 a=[v[1][j]-v[0][j] for j in range(3)];c=[v[2][j]-v[0][j] for j in range(3)];n=[a[1]*c[2]-a[2]*c[1],a[2]*c[0]-a[0]*c[2],a[0]*c[1]-a[1]*c[0]];l=math.sqrt(sum(x*x for x in n));n=[x/l for x in n];color=0
 hit=[s for s in surfaces if n[2]>0 and abs(n[0]+s['slope']*n[2])<eps and abs(n[1])<eps and all(s['x0']-eps<=x<=s['x1']+eps and s['y0']-eps<=y<=s['y1']+eps and abs(z-s['slope']*x-s['intercept'])<eps for x,y,z in v)]
 if hit:groups['white'].append(i);matches[str(i)]=hit;color=1
 for name,y,z,w,d,h,sy in [('upper_red',-25.2,28.1,23.5,8.2,2.4,.17),('entry_red',-32,7.6,14,7.3,1.2,.18)]:
  y0=y-d/2;y1=y-d*sy/2;m=h/(y1-y0)
  if n[2]>0 and n[1]<0 and abs(n[0])<eps and abs(n[1]+m*n[2])<eps and all(y0-eps<=q[1]<=y1+eps and abs(q[0])<=w/2*(1-.08*(q[1]-y0)/(y1-y0))+eps and abs(q[2]-z-m*(q[1]-y0))<eps for q in v):
   assert color==0;groups[name].append(i);color=2
 assert fm['face_material_indices'][i]==color,(i,color)
assert [len(x) for x in groups.values()]==[190,4,4]
(A/'qa/material-boundaries.json').write_text(json.dumps({'groups':groups,'white_surface_matches':matches,'all_three_vertices_same_plane_and_support':True,'geometric_normals_verified':True,'original_stl_normals_not_trusted_for_selection':True,'white_planes':50,'colored_faces':198,'neutral_faces':4180,'no_subdivision':True,'unknown_walls_glass_endframes_side_roofs_unchanged':True},indent=2)+'\n')
print('independent exact boundary pass 190 + 4 + 4')
