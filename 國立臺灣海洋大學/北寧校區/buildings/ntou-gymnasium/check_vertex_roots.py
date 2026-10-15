"""Supplement to preserved two-face roots: true incident vertex normals only.
Tests two/three-face cones, never skips an earlier air interval to find a wall.
"""
from pathlib import Path
import json,numpy as np,trimesh,itertools,hashlib
from original_rays import OriginalRays
R=Path(__file__).parent;m0=trimesh.load(R/'model.stl',process=False);V,inv=np.unique(m0.triangles.reshape(-1,3),axis=0,return_inverse=True);F=inv.reshape(-1,3);m=trimesh.Trimesh(V,F,process=False);ray=OriginalRays(m0);N=m.face_normals
VF=[[]for _ in V]
for i,f in enumerate(F):
 for v in f:VF[v].append(i)
old=json.loads((R/'dense-corner-backing.json').read_text());rows=[]
for q in old['samples']:
 p=np.array(q['surface_point_mm']);fi=q['original_triangle_index'];n=N[fi];candidates=[]
 # retain original two-face choice as an explicitly recorded candidate
 choices=[(q['inward_bisector'],q['adjacent_original_faces'],None,q['true_edge_distance_mm'])]
 for vi in F[fi]:
  dist=float(np.linalg.norm(p-V[vi]))
  if dist>.8:continue
  fs=VF[vi];uniq=[]
  for f in fs:
   if not any(np.linalg.norm(N[f]-N[g])<1e-6 for g in uniq):uniq.append(f)
  for k in [2,3]:
   for faces in itertools.combinations(uniq,k):
    nn=N[list(faces)]
    if max(nn@n)<.99999:continue
    d=-nn.sum(0)
    if np.linalg.norm(d)<1e-6:continue
    d/=np.linalg.norm(d)
    if np.any(nn@d>=-1e-7):continue
    choices.append((d,faces,int(vi),dist))
 for d,faces,vi,dist in choices:
  d=np.array(d);start=p+d*1e-5;h=ray.hits(start,d);length=h[0][0]if h else None
  controls=[len(ray.hits(p+d*t,np.array([.319,.557,.766])/np.linalg.norm([.319,.557,.766])))%2==1 for t in [1e-5,.01,.1,.4]]
  valid=length is not None and length>=.8 and all(controls) and N[h[0][1]]@d>1e-7
  candidates.append(dict(direction=d.tolist(),incident_original_faces=list(map(int,faces)),vertex_index=vi,vertex_or_edge_distance_mm=dist,first_exit_mm=length,controls=controls,first_hit=h[0]if h else None,valid=bool(valid)))
 valid=[c for c in candidates if c['valid']];chosen=min(valid,key=lambda c:c['vertex_or_edge_distance_mm'])if valid else None
 rows.append(dict(face=fi,sample=q['sample_index'],surface=p.tolist(),original_first_chord_mm=q['original_first_chord_mm'],original_two_face_first_exit_mm=q['continuous_first_exit_mm'],candidates=candidates,chosen=chosen))
checks={'every_short_sample_has_true_incident_continuous_root':all(q['chosen']is not None for q in rows)}
r=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),count=len(rows),checks=checks,rows=rows,limits='Finite directions from true incident faces; all rejected choices retained. Does not waive original strict short-normal failure or certify global wall thickness.')
(R/'vertex-roots.json').write_text(json.dumps(r));print(checks,'failed',[(q['face'],q['sample'])for q in rows if q['chosen']is None]);raise SystemExit(0 if all(checks.values())else 1)
