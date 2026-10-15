from pathlib import Path
import gzip,json,numpy as np,trimesh,hashlib
O=Path(__file__).resolve().parent
initial_sha=hashlib.sha256((O/'model.stl').read_bytes()).hexdigest()
m=trimesh.load(O/'model.stl',process=False);T=m.triangles
def ray(o,d):
 o=np.array(o,float);d=np.array(d,float);e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];p=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,p);good=abs(det)>1e-10;inv=np.zeros(len(T));inv[good]=1/det[good];s=o-T[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);v=q@d*inv;t=np.einsum('ij,ij->i',e2,q)*inv;return sorted(set(round(float(x),7) for x in t[good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-7)]))

rows=[];fail=[]
norm=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]);norm/=np.linalg.norm(norm,axis=1)[:,None]
weights=[[1/3,1/3,1/3],[.98,.01,.01],[.01,.98,.01],[.01,.01,.98],[.495,.495,.01],[.495,.01,.495],[.01,.495,.495]]
for i,f in enumerate(T):
 for wi,w in enumerate(weights):
  p=np.array(w)@f;n=norm[i];hs=ray(p+n*.0001,-n);hs=[x for j,x in enumerate(hs) if j==0 or x-hs[j-1]>1e-6]
  if len(hs)<2:fail.append({'face':i,'point':p.tolist(),'hits':hs});continue
  row={'face':i,'weight_index':wi,'point_mm':p.tolist(),'normal':n.tolist(),'first_solid_mm':hs[1]-hs[0],'hits_mm':hs[:4]}
  rows.append(row)
summary={'ray_intersections_all_found':not fail,'stl_sha256':initial_sha,'sample_count':len(rows),'minimum_first_chord_mm':min(r['first_solid_mm'] for r in rows),'below_0p8_count':sum(r['first_solid_mm']<.8 for r in rows),'failures':fail,'samples':rows,'limitations':'Every original face centroid and1percent inset face vertices/edges including base; first solid chord retained. Short corners not automatically approved. Dense evidence is not a global wall guarantee.'}

with gzip.open(O/'dense-first-chords.json.gz','wt',encoding='utf-8') as out:json.dump(summary,out,separators=(',',':'))
print({k:v for k,v in summary.items() if k!='samples'});assert not fail
