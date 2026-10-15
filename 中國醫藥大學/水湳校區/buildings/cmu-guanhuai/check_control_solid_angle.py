"""Resolve dense parity controls on all original triangles; retain raw failures.
This is not mesh repair or automatic acceptance of short chords.
"""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
R=Path(__file__).resolve().parent;T=trimesh.load(R/'model.stl',process=False).triangles
E1=T[:,1]-T[:,0];E2=T[:,2]-T[:,0]
def angle(p):
 a,b,c=(T-p).transpose(1,0,2);la=np.linalg.norm(a,axis=1);lb=np.linalg.norm(b,axis=1);lc=np.linalg.norm(c,axis=1)
 numerator=np.einsum('ij,ij->i',a,np.cross(b,c));den=la*lb*lc+np.einsum('ij,ij->i',a,b)*lc+np.einsum('ij,ij->i',b,c)*la+np.einsum('ij,ij->i',c,a)*lb
 return float(np.sum(2*np.arctan2(numerator,den))/(4*np.pi))
def ray(o,d):
 q=np.cross(d,E2);det=np.einsum('ij,ij->i',E1,q);ok=abs(det)>1e-13;iv=np.zeros(len(T));iv[ok]=1/det[ok];s=o-T[:,0];u=np.einsum('ij,ij->i',s,q)*iv;r=np.cross(s,E1);v=r@d*iv;t=np.einsum('ij,ij->i',E2,r)*iv
 idx=np.flatnonzero(ok&(u>=-1e-12)&(v>=-1e-12)&(u+v<=1+1e-12)&(t>1e-9));idx=idx[np.argsort(t[idx])];keep=[]
 for i in idx:
  if not keep or t[i]-t[keep[-1]]>1e-7:keep.append(i)
 return [{'face':int(i),'distance':float(t[i]),'barycentric':[float(1-u[i]-v[i]),float(u[i]),float(v[i])]} for i in keep]
weights=[[1/3]*3,[.98,.01,.01],[.01,.98,.01],[.01,.01,.98],[.495,.495,.01],[.01,.495,.495],[.495,.01,.495]]
rows=[]
for r in json.loads((R/'dense-summary.json').read_text())['control_failures']:
 fi=int(r['face']);p=np.array(weights[int(r['sample'])])@T[fi];n=np.cross(E1[fi],E2[fi]);n/=np.linalg.norm(n);o=p+n*1e-5;d=-n;h=ray(o,d);a,b=h[0]['distance'],h[1]['distance'];c=h[2]['distance'] if len(h)>2 else float('inf')
 controls=[p-n*min(1e-5,(b-a)/4),o,o+d*((a+b)/2),o+d*(b+min(1e-5,(c-b)/2))];w=[angle(q) for q in controls];expected=[1,0,1,0]
 near=[]
 for q in controls:
  cp=trimesh.triangles.closest_point(T,np.repeat(q[None,:],len(T),axis=0));ds=np.linalg.norm(cp-q,axis=1);ix=int(np.argmin(ds));near.append({'distance_mm':float(ds[ix]),'original_face':ix})
 rows.append({'original_dense_sample':r,'exact_barycentric_surface_point':p.tolist(),'strict_barycentric_hits':h,'strict_first_solid':b-a,'strict_after_air':None if not np.isfinite(c) else c-b,'all_original_triangle_solid_angle_controls':w,'control_nearest_original_surface':near,'controls_match':all(x['distance_mm']>1e-8 for x in near) and all(abs(abs(x)-e)<1e-4 for x,e in zip(w,expected))})
j={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'passed':all(x['controls_match'] for x in rows),'sample_count':len(rows),'rows':rows,'limits':'Original dense parity results and raw short segments retained. Strict barycentric hit filtering and full-triangle winding evaluated only for flagged controls; no global thickness claim.'};(R/'control-solid-angle.json').write_text(json.dumps(j,indent=2));print('resolved',sum(x['controls_match'] for x in rows),'of',len(rows));print([(x['original_dense_sample']['face'],x['all_original_triangle_solid_angle_controls']) for x in rows if not x['controls_match']]);assert j['passed']
