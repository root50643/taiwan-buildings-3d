from pathlib import Path
import numpy as np,json,gzip,collections
P=Path(__file__).parent/'classify_nearplanar.py';s=P.read_text();__file__=str(P);exec(s[:s.index('helper=')])
D=json.loads((R/'nearplanar-individual-short-review.json').read_text());graph=collections.defaultdict(list)
for i,(af,bf)in enumerate(fa):
 a,b=int(patch[af]),int(patch[bf])
 if a!=b and m.face_adjacency_convex[i] and m.face_adjacency_angles[i]>.0001:graph[a].append((b,i));graph[b].append((a,i))

def dist(p,i):
 a,b=ee[i];v=b-a;t=np.clip((p-a)@v/(v@v),0,1);return float(np.linalg.norm(p-a-v*t))
out=[]
for row in D:
 f=row['face'];xf=row['first_exit_face'];p=np.array(row['surface_mm']);start=int(patch[f]);end=int(patch[xf]);q=[(start,[])];seen={start};found=[]
 while q:
  a,path=q.pop(0)
  if a==end:found=path;break
  if len(path)>=3:continue
  for b,i in graph[a]:
   if b in seen or dist(p,i)>1.5:continue
   if sum(m.face_adjacency_angles[j]for j in path+[i])>np.radians(170):continue
   seen.add(b);q.append((b,path+[i]))
 n=nn[f];o=p+n*1e-5;hh=sorted(solid.ray_cast(o,o-n*1000),key=lambda h:h.distance);mid=o-n*((hh[0].distance+hh[1].distance)*500)
 vec=-(nn[f]+nn[xf]);length=np.linalg.norm(vec);vec=vec/max(length,1e-30);hits=sorted(solid.ray_cast(mid,mid+vec*1000),key=lambda h:h.distance);hit=next((h for h in hits if h.distance>1e-12),None);rootdist=hit.distance*1000 if hit else None
 rr={**row,'convex_chain':[{'edge':i,'original_faces':fa[i].tolist(),'angle_deg':float(np.degrees(m.face_adjacency_angles[i])),'distance_from_surface_mm':dist(p,i),'endpoints_mm':ee[i].tolist()}for i in found],'source_exit_inward_bisector':vec.tolist(),'first_material_midpoint_mm':mid.tolist(),'bisector_first_exit_mm':rootdist,'bisector_exit_original_face':int(remap[hit.face_id])if hit else None,'accepted_geometric_classification':bool(found and length>.1 and rootdist is not None and rootdist>=.8)}
 out.append(rr)
with gzip.open(R/'convex-chain-bisector-evidence.json.gz','wt')as f:json.dump({'stl_sha256':hashlib.sha256(raw).hexdigest(),'method':'At most3 actual convex original-edge links between connected nearplanar source/first-exit patches, all source-to-edge distances <=1.5mm and summed turns <170degrees; source/exit inward-normal bisector traced only to first material exit. Identification does not alter mesh.','rows':out},f)
bad=[r for r in out if not r['accepted_geometric_classification']];(R/'unclassified-short-final.json').write_text(json.dumps(bad,indent=2));summ={'total':len(out),'convex_chain_and_bisector_over_0_8':len(out)-len(bad),'remaining':len(bad),'remaining_faces':len(set(x['face']for x in bad)),'minimum_bisector_root_accepted_mm':min([x['bisector_first_exit_mm']for x in out if x['accepted_geometric_classification']]or[0]),'not_approval':True};(R/'convex-chain-summary.json').write_text(json.dumps(summ,indent=2));print(summ)
