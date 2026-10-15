"""All short-normal samples not in proven backing bands: true entry/exit face
pairs and, when intercepted, actual third-face inward cone. Original failures retained.
"""
from pathlib import Path
import numpy as np,trimesh,json,csv,gzip,hashlib
R=Path(__file__).resolve().parent;T=trimesh.load(R/'model.stl',process=False).triangles;E1=T[:,1]-T[:,0];E2=T[:,2]-T[:,0];N=np.cross(E1,E2);N/=np.linalg.norm(N,axis=1)[:,None]
def hits(o,d):
 q=np.cross(d,E2);det=np.einsum('ij,ij->i',E1,q);ok=abs(det)>1e-11;iv=np.zeros(len(T));iv[ok]=1/det[ok];s=o-T[:,0];u=np.einsum('ij,ij->i',s,q)*iv;r=np.cross(s,E1);v=r@d*iv;t=np.einsum('ij,ij->i',E2,r)*iv;ix=np.where(ok&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-8))[0];ix=ix[np.argsort(t[ix])];return t[ix],ix

def winding(p):
 v=T-p;a,b,c=v[:,0],v[:,1],v[:,2];la=np.linalg.norm(a,axis=1);lb=np.linalg.norm(b,axis=1);lc=np.linalg.norm(c,axis=1);num=np.einsum('ij,ij->i',a,np.cross(b,c));den=la*lb*lc+np.einsum('ij,ij->i',a,b)*lc+np.einsum('ij,ij->i',b,c)*la+np.einsum('ij,ij->i',c,a)*lb;return float(abs(np.sum(2*np.arctan2(num,den)))/(4*np.pi))
j=json.loads((R/'local-back-roots.json').read_text());excluded={(r['face'],r['sample']) for r in j['arch_transition_exclusions']};backed={(r['face'],r['sample']) for r in j['samples']}-excluded
rows=[];fails=[]
for r in csv.DictReader(gzip.open(R/'dense-samples.csv.gz','rt')):
 key=int(r['face']),int(r['sample'])
 if float(r['first_solid'])>=.8 or key in backed:continue
 p=np.array([float(r[a]) for a in ['x','y','z']]);n=N[key[0]];f,ix=hits(p+n*1e-5,-n);target=1e-5+float(r['first_solid']);ei=int(ix[np.argmin(abs(f-target))]);assert abs(f[np.argmin(abs(f-target))]-target)<1e-5
 planes=[key[0],ei];attempts=[];accepted=False
 for depth in [2,3,4]:
  normals=N[planes];d=-normals.sum(axis=0);ln=np.linalg.norm(d)
  if ln<1e-8:break
  d/=ln;dots=normals@d;hh,ff=hits(p+d*1e-5,d);length=float(hh[0]+1e-5) if len(hh) else 0.;controls=[winding(p+d*v) for v in [1e-5,.001,.01,.05]]
  offset=np.einsum('ij,ij->i',normals,T[planes,0])-normals@p;distance=float(np.linalg.norm(np.linalg.lstsq(normals,offset,rcond=None)[0]))
  attempt={'face_planes':planes.copy(),'direction':d.tolist(),'dot_with_each_actual_outward_normal':dots.tolist(),'first_solid_mm':length,'actual_first_exit_face':int(ff[0]) if len(ff) else None,'four_near_point_winding_numbers':controls,'distance_to_actual_plane_intersection_mm':distance,'hits_mm':hh.tolist()};attempts.append(attempt)
  if length>=.8 and max(dots)<-.001 and all(abs(w-1)<1e-6 for w in controls):accepted=True;break
  if not len(ff) or int(ff[0]) in planes:break
  planes.append(int(ff[0]))
 record={'face':key[0],'sample':key[1],'surface_point_mm':p.tolist(),'original_first_solid_mm':float(r['first_solid']),'original_air_after':r['air_after'],'actual_normal_exit_face':ei,'attempts':attempts,'accepted_local_corner_root':accepted};rows.append(record)
 if not accepted:fails.append(record)
report={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'passed':not fails,'checks':{'every_remaining_short_sample_has_explicit_local_actual_face_cone_root':not fails},'sample_count':len(rows),'samples':rows,'failures':fails,'limits':'Directions are sums of two/three/four actual inward face normals, never later distant wall sums. These prove nominated finite-corner roots, not global directional wall thickness or print strength. All original short normals, subsequent air and failed intermediate directions are retained.'}
(R/'corner-root-check.json').write_text(json.dumps(report,indent=2));print('CORNERS',len(rows),'fail',len(fails));raise SystemExit(0 if not fails else 1)
