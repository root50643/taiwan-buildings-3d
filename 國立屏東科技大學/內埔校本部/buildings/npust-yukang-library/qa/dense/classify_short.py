import math
def portable(o):
 if isinstance(o,float) and not math.isfinite(o): return None
 if isinstance(o,dict): return {k:portable(v)for k,v in o.items()}
 if isinstance(o,list): return [portable(v)for v in o]
 return o
from pathlib import Path
import numpy as np,trimesh,pandas as pd,json,gzip,hashlib,collections
from manifold3d import Manifold,Mesh64
R=Path(__file__).parent;F=R.parents[1]/'model.stl';raw=F.read_bytes();T=np.frombuffer(raw,offset=84,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')])['v'].astype(float);V,I=np.unique(T.reshape(-1,3),axis=0,return_inverse=True);faces=I.reshape(-1,3);m=trimesh.Trimesh(V,faces,process=False);nn=m.face_normals;fa=m.face_adjacency;ee=V[m.face_adjacency_edges];par=np.arange(len(T))
def root(i):
 while par[i]!=i:par[i]=par[par[i]];i=par[i]
 return int(i)
for a,b in fa:
 if nn[a]@nn[b]>1-1e-10 and np.max(abs((T[b]-T[a,0])@nn[a]))<1e-6:par[root(b)]=root(a)
patch=np.array([root(i)for i in range(len(T))]);pairs=collections.defaultdict(list)
for i,(a,b) in enumerate(fa):
 if patch[a]!=patch[b]:pairs[tuple(sorted([int(patch[a]),int(patch[b])]))].append(i)
solid=Manifold(Mesh64(np.ascontiguousarray(V),np.ascontiguousarray(faces,dtype=np.uint64)));mm=solid.to_mesh64();TT=np.asarray(mm.vert_properties)[np.asarray(mm.tri_verts)][:,:,:3]
def key(t):return min(tuple(map(tuple,np.roll(t,j,axis=0)))for j in range(3))
lookup={key(t):i for i,t in enumerate(T)};remap=[lookup[key(t)]for t in TT];assert len(set(remap))==len(T)==len(TT)
helper=(R/'diagnose.py').read_text();exec(helper[helper.index('def strict'):helper.index("d=pd.read_csv")],dict()) if False else None
tri=T.astype(np.longdouble);a=tri[:,0];e1=tri[:,1]-a;e2=tri[:,2]-a;D=np.longdouble
exec(helper[helper.index('def strict'):helper.index('d=pd.read_csv')])
DF=pd.read_csv(R/'short-original.csv.gz');out=[];replays=[]
for _,r in DF.iterrows():
 f=int(r.face);p=r[['x','y','z']].to_numpy(float);n=nn[f];o=p+n*1e-5;hits=sorted(solid.ray_cast(o,o-n*1000),key=lambda h:h.distance);h=[h for h in hits if h.distance>1e-12];xf=remap[h[1].face_id];span=(h[1].distance-h[0].distance)*1000
 if abs(span-r.first_solid)>1e-6:
  # preserve disagreement and resolve using unaccelerated longdouble original triangles.
  hh=strict(o,-n);xf=hh[1]['face_id'];span=hh[1]['distance_mm']-hh[0]['distance_mm']
  mid=o-n*(hh[0]['distance_mm']+hh[1]['distance_mm'])/2
  replays.append({'face':f,'sample':int(r['sample']),'original_span':float(r.first_solid),'strict_span':span,'hits':hh,'mid_winding':winding(mid),'outside_winding':winding(o),'after_winding':winding(o-n*(hh[1]['distance_mm']+min(1e-5,(hh[2]['distance_mm']-hh[1]['distance_mm'])/2)))if len(hh)>2 else winding(o-n*(hh[1]['distance_mm']+1e-5))})

 cand=[]
 for i in pairs[tuple(sorted([int(patch[f]),int(patch[xf])]))]:
  ea,eb=ee[i];v=eb-ea;t=np.clip((p-ea)@v/(v@v),0,1);dist=np.linalg.norm(p-ea-v*t);cand.append({'edge_id':i,'original_faces':fa[i].tolist(),'distance_mm':float(dist),'convex':bool(m.face_adjacency_convex[i]),'angle_deg':float(np.degrees(m.face_adjacency_angles[i])),'endpoints_mm':ee[i].tolist()})
 cand.sort(key=lambda x:x['distance_mm']);cl='source_first_exit_meet_at_convex_edge'if cand and cand[0]['convex']else 'individual_lip_or_corner_review'
 out.append({'face':f,'sample':int(r['sample']),'first_exit_face':int(xf),'surface_mm':p.tolist(),'first_solid_mm':float(r.first_solid),'classification_actual_span_mm':span,'air_after_mm':float(r.air_after),'source_exit_angle_deg':float(np.degrees(np.arccos(np.clip(n@nn[xf],-1,1)))),'nearest_shared_patch_edge':cand[0]if cand else None,'classification':cl})
(R/'ray-disagreements-strict.json').write_text(json.dumps(replays,indent=2))
with gzip.open(R/'short-edge-classification.json.gz','wt')as f:json.dump(portable({'sha256':hashlib.sha256(raw).hexdigest(),'method':'Original connected coplanar face patches for identification only, no geometric union or repair; source and FIRST normal exit patch common true crease; independent ray span checked against original CSV; differences above 1e-6mm retained and rechecked with original-triangle longdouble ray.','rows':out}),f)
counts=collections.Counter(x['classification']for x in out);other=[x for x in out if x['classification']!='source_first_exit_meet_at_convex_edge'];(R/'individual-short-review.json').write_text(json.dumps(portable(other),indent=2));(R/'edge-classification-summary.json').write_text(json.dumps({'counts':dict(counts),'other_sample_count':len(other),'other_face_count':len(set(x['face']for x in other)),'minimum_other_mm':min([x['first_solid_mm']for x in other]or[0]),'global_minimum_thickness_proven':False},indent=2));print(counts,len(other))
