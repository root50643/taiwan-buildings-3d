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
 if rec['original_flags']['first_chord_midpoint_inside']:continue
 rr=rec['original_sample'];o=np.array(rr['ray_origin_mm']);v=np.array(rr['direction']);q=o+v*.0001;ep=min(.0001,rec['strict_first_chord_mm']*.2);origin=q-v*ep;h=strict(origin,v);tests=[]
 for role,p in [('validated_outside_origin',origin),('inside_surface',q+v*ep),('first_material_midpoint',origin+v*(h[0]['distance_mm']+h[1]['distance_mm'])/2),('after_material_exit',origin+v*(h[1]['distance_mm']+.0001))]:tests.append({'role':role,'point_mm':p.tolist(),'winding':winding(p)})
 out.append({'sample_index':rec['sample_index'],'original_fixed_origin_diagnostic':rec,'validated_ray_origin_mm':origin.tolist(),'direction':v.tolist(),'surface_point_mm':q.tolist(),'epsilon_mm':ep,'strict_hits':h,'actual_first_material_span_mm':h[1]['distance_mm']-h[0]['distance_mm'],'tests':tests});print(rec['sample_index'],h[1]['distance_mm']-h[0]['distance_mm'],[(h['dot'],h['face_id'])for h in h[:2]],[(x['role'],x['winding'])for x in tests],flush=True)
(Q/'adaptive-origin-evidence.json').write_text(json.dumps({'stl_sha256':hashlib.sha256(F.read_bytes()).hexdigest(),'method':'Fixed0.0001mm outward ray origin crossed a narrower AIR gap into other solid. Original apparent short pair is EXIT then ENTRY, not solid. Recast from the already-validated near-surface outside point, retaining old values and strict normal signs. No geometry change.','samples':out},indent=2))
