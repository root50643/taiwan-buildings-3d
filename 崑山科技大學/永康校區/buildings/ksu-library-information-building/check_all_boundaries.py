from pathlib import Path
import json,numpy as np,trimesh,hashlib
R=Path(__file__).parent;Q=R;F=R/'model.stl';m=trimesh.load(F,process=False);tri=np.asarray(m.triangles,dtype=np.longdouble);a=tri[:,0];e1=tri[:,1]-a;e2=tri[:,2]-a
D=np.longdouble

def strict(o,v):
 o=np.array(o,dtype=D);v=np.array(v,dtype=D);h=np.cross(np.broadcast_to(v,e2.shape),e2);det=np.einsum('ij,ij->i',e1,h);ok=abs(det)>1e-24;inv=np.zeros(len(det),dtype=D);inv[ok]=1/det[ok];ss=o-a;u=inv*np.einsum('ij,ij->i',ss,h);q=np.cross(ss,e1);vv=inv*(q@v);t=inv*np.einsum('ij,ij->i',e2,q);ids=np.where(ok&(u>=-1e-15)&(vv>=-1e-15)&(u+vv<=1+1e-15)&(t>1e-12))[0];ids=ids[np.argsort(t[ids])];res=[]
 for f in ids:
  if not res or abs(float(t[f])-res[-1]['distance_mm'])>1e-11:res.append({'distance_mm':float(t[f]),'face_id':int(f),'barycentric':[float(1-u[f]-vv[f]),float(u[f]),float(vv[f])],'dot':float(v@m.face_normals[f])})
 return res

def winding(p):
 v=tri-np.array(p,dtype=D);v/=np.linalg.norm(v,axis=2)[:,:,None];num=np.einsum('ij,ij->i',v[:,0],np.cross(v[:,1],v[:,2]));den=1+np.einsum('ij,ij->i',v[:,0],v[:,1])+np.einsum('ij,ij->i',v[:,1],v[:,2])+np.einsum('ij,ij->i',v[:,2],v[:,0]);return float(np.arctan2(num,den).sum()/(2*np.pi))
diag=json.loads((Q/'dense-anomalies-v2.json').read_text());out=[]
for rec in diag['samples']:
 if not rec['original_flags']['first_chord_midpoint_inside']:continue
 rr=rec['original_sample'];base=np.array(rr['ray_origin_mm']);v=np.array(rr['direction']);f=rr['sample_face_id'];outrows=[]
 for dz in [0,-.001,.001,-.01,.01]:
  offset=[dz,0,0] if rec['sample_index'] in [87367,87535,94710] else [0,0,dz];origin=base+offset;q=origin+v*.0001;w=trimesh.triangles.points_to_barycentric(m.triangles[[f]],q[None,:])[0];assert min(w)>0 and max(w)<1
  h=strict(origin,v);tests=[]
  for role,t in [('before',h[0]['distance_mm']-.0001),('mid',(h[0]['distance_mm']+h[1]['distance_mm'])/2),('after_first',h[1]['distance_mm']+.0001)]:
   p=origin+v*t;near,dist,fi=trimesh.proximity.closest_point(m,[p]);tests.append({'role':role,'point_mm':p.tolist(),'winding':winding(p),'distance_to_original_surface_mm':float(dist[0]),'nearest_original_face_id':int(fi[0])})
  outrows.append({'source_face_barycentric':w.tolist(),'surface_in_plane_offset_mm':offset,'ray_origin_mm':origin.tolist(),'direction':v.tolist(),'strict_hits':h,'tests':tests})
 out.append({'sample_index':rec['sample_index'],'original_face_id':f,'controls':outrows});print(rec['sample_index'],[(a['surface_in_plane_offset_mm'],a['tests'][-1]['winding'],a['tests'][-1]['distance_to_original_surface_mm'])for a in outrows],flush=True)
(Q/'all-six-boundary-controls.json').write_text(json.dumps({'stl_sha256':hashlib.sha256(F.read_bytes()).hexdigest(),'method':'Six original first-exit postpoints lie on original surfaces (including coplanar window ceiling), not open exterior points. Original failures retained; same original triangle +/-0.001 and0.01mm in-plane X or Z controls with barycentric proof and strict hits/winding.','samples':out},indent=2))
