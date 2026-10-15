"""All short normal samples in source-defined shallow backed glazing/cladding.
Original first solid and following air remain unchanged; no longest-ray search.
"""
from pathlib import Path
import json,csv,gzip,hashlib,numpy as np,trimesh,collections
R=Path(__file__).resolve().parent;T=trimesh.load(R/'model.stl',process=False).triangles;E1=T[:,1]-T[:,0];E2=T[:,2]-T[:,0];S=150/62;BASE=2

def hits(o,d):
 q=np.cross(d,E2);det=np.einsum('ij,ij->i',E1,q);ok=abs(det)>1e-13;iv=np.zeros(len(T));iv[ok]=1/det[ok];ss=o-T[:,0];u=np.einsum('ij,ij->i',ss,q)*iv;r=np.cross(ss,E1);v=r@d*iv;t=np.einsum('ij,ij->i',E2,r)*iv;ix=np.flatnonzero(ok&(u>=-1e-12)&(v>=-1e-12)&(u+v<=1+1e-12)&(t>1e-9));ix=ix[np.argsort(t[ix])];keep=[]
 for i in ix:
  if not keep or t[i]-t[keep[-1]]>1e-7:keep.append(i)
 return [{'face':int(i),'distance_mm':float(t[i]),'point_mm':(o+d*t[i]).tolist()} for i in keep]
def inside(p):return len(hits(p,np.array([.713123,.431977,.552111])))%2==1
rows=[];unknown=[]
for r in csv.DictReader(gzip.open(R/'dense-samples.csv.gz','rt')):
 if float(r['first_solid'])>=.8:continue
 p=np.array([float(r[k]) for k in ['x','y','z']]);n=np.array([float(r[k]) for k in ['nx','ny','nz']]);x,y,z=(p-[0,0,BASE])/S;family=None;back=None
 if -19.71<=y<=-19.52 and 26.49<=z<=29.61 and abs(n[1])<.2:family='south_upper_glass_shallow_pane_division';back=np.array([0.,1.,0.])
 elif 17.82<=x<=18.01 and 26.49<=z<=29.61 and abs(n[0])<.2:family='east_upper_glass_shallow_pane_division';back=np.array([-1.,0.,0.])
 elif 17.34<=x<=18.01 and 12.7<=z<=25.3 and abs(n[0])<.2:family='east_cladding_band_backed_edge';back=np.array([-1.,0.,0.])
 if family is None:unknown.append(r);continue
 d=back-.15*n;d/=np.linalg.norm(d);assert np.dot(d,n)<-.05;h=hits(p+d*1e-5,d);ctrl=[inside(p+d*t) for t in [1e-5,.001,.01,.05,.1]]
 rows.append({'family':family,'original_sample':r,'root_direction':d.tolist(),'entry_normal_dot_root':float(np.dot(d,n)),'first_root_mm':float(h[0]['distance_mm']+1e-5) if h else None,'all_root_hits':h,'near_root_inside_controls':ctrl,'passed':bool(h and h[0]['distance_mm']>=.8 and all(ctrl))})
counts=collections.Counter(x['family'] for x in rows);j={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'passed':not unknown and all(x['passed'] for x in rows),'checks':{'all_original_short_normals_assigned_to_source_backed_relief':not unknown,'all_nominated_root_first_segments_and_controls_pass':all(x['passed'] for x in rows)},'family_counts':dict(counts),'families':[{'family':k,'samples':v,'minimum_original_first_mm':min(float(x['original_sample']['first_solid']) for x in rows if x['family']==k),'minimum_direct_root_mm':min(x['first_root_mm'] for x in rows if x['family']==k)} for k,v in counts.items()],'unclassified':unknown,'rows':rows,'limits':'Source-bounded shallow relief has tangent-to-back original normals. Root direction is fixed toward actual parent wall with 0.15 inward normal bias. Original normal thickness and later air are not replaced; finite sampling does not guarantee every direction or physical print.'};(R/'backed-relief-roots.json').write_text(json.dumps(j,indent=2));print('families',j['families'],'unknown',len(unknown),'failed',sum(not x['passed'] for x in rows));print(unknown[:2]);assert j['passed']
