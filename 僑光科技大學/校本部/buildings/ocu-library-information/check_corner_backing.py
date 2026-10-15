"""Evidence for every original-normal short sample. Does not waive strict failures.
Actual original dihedral edges, first solid/air verification, and continuous inward adjacent-face bisector rays.
"""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
from scipy.spatial import cKDTree
from original_rays import OriginalRays
R=Path(__file__).parent;m0=trimesh.load(R/'model.stl',process=False);ray=OriginalRays(m0);v,ix=np.unique(m0.triangles.reshape(-1,3),axis=0,return_inverse=True);m=trimesh.Trimesh(v,ix.reshape(-1,3),process=False);mask=m.face_adjacency_angles>np.radians(12);edges=m.vertices[m.face_adjacency_edges[mask]];adj=m.face_adjacency[mask];samples=[];ids=[]
for i,(a,b)in enumerate(edges):
 ts=np.linspace(0,1,max(2,int(np.linalg.norm(b-a)/.5)+2));samples.extend(a+(b-a)*ts[:,None]);ids.extend([i]*len(ts))
ids=np.array(ids);tree=cKDTree(samples);data=json.loads((R/'surface-chords.json').read_text());rows=[]
probe=np.array([.319,.557,.766]);probe/=np.linalg.norm(probe)
def inside(p):return len(ray.hits(p,probe))%2==1
for q in data['short_chords']:
 p=np.array(q['surface_point_mm']);n=np.array(q['original_outward_normal']);_,j=tree.query(p,k=80);ei=np.unique(ids[j]);en=m.face_normals[adj[ei]];match=np.max(en@n,axis=1)>.99999
 candidates=ei[match] if match.any() else ei
 e=edges[candidates];a=e[:,0];v=e[:,1]-a;t=np.clip(np.einsum('ij,ij->i',p-a,v)/np.einsum('ij,ij->i',v,v),0,1);dist=np.linalg.norm(p-a-v*t[:,None],axis=1);k=int(np.argmin(dist));i=int(candidates[k]);nn=m.face_normals[adj[i]];b=-nn.sum(0);b/=np.linalg.norm(b)
 o=p+n*1e-6;h=q['all_ray_intersections_mm_face'];mid=o-n*((h[0][0]+h[1][0])/2);gap=h[2][0]-h[1][0]if len(h)>2 else 1;after=o-n*(h[1][0]+min(1e-4,gap/4));start=p+b*1e-5;bh=ray.hits(start,b)
 controls=[inside(p+b*u)for u in [1e-5,.01,.1,.4]]
 rows.append(dict(original_triangle_index=q['original_triangle_index'],sample_index=q['sample_index'],surface_point_mm=p.tolist(),original_outward_normal=n.tolist(),original_first_chord_mm=q['first_solid_chord_mm'],all_original_normal_hits=h,first_interval_midpoint_material=inside(mid),after_first_exit_air=not inside(after),true_edge_distance_mm=float(dist[k]),true_edge_mm=edges[i].tolist(),adjacent_original_faces=adj[i].tolist(),adjacent_original_normals=nn.tolist(),original_normal_matches_adjacent=bool(np.max(nn@n)>.99999),inward_bisector=b.tolist(),bisector_start_material=controls[0],continuous_first_exit_mm=bh[0][0]if bh else None,first_bisector_hit_is_outward_exit=bool(bh and np.dot(m0.face_normals[bh[0][1]],b)>1e-7),inside_controls_0p00001_0p01_0p1_0p4=controls,all_bisector_hits=bh))
checks={'all_original_normals_match_actual_adjacent_face':all(x['original_normal_matches_adjacent']for x in rows),'every_short_sample_included':len(rows)==data['under_0p8mm_count'],'all_first_original_intervals_material_then_air':all(x['first_interval_midpoint_material']and x['after_first_exit_air']for x in rows),'all_bisector_starts_and_controls_inside':all(all(x['inside_controls_0p00001_0p01_0p1_0p4'])for x in rows),'all_bisectors_start_with_exit_not_remote_entry':all(x['first_bisector_hit_is_outward_exit']for x in rows),'all_continuous_bisector_roots_ge_0p8':all(x['continuous_first_exit_mm']is not None and x['continuous_first_exit_mm']>=.8 for x in rows)}
r={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'count':len(rows),'max_true_edge_distance_mm':max(x['true_edge_distance_mm']for x in rows),'minimum_continuous_bisector_first_exit_mm':min(x['continuous_first_exit_mm']for x in rows if x['continuous_first_exit_mm']is not None),'checks':checks,'samples':rows,'status':'Evidence only, no automatic exception or global thickness guarantee. Strict surface report remains false.'};(R/'corner-backing.json').write_text(json.dumps(r));print({k:v for k,v in r.items()if k!='samples'});raise SystemExit(0 if all(checks.values()) else 1)
