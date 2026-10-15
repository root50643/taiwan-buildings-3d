from pathlib import Path
import csv,collections,json,hashlib,numpy as np,trimesh
R=Path(__file__).resolve().parent;T=trimesh.load(R/'model.stl',process=False).triangles;N=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]);N/=np.linalg.norm(N,axis=1)[:,None];rows=list(csv.DictReader((R/'short-root-classification.csv').open()));groups=collections.defaultdict(list);adj=collections.Counter();maxdist=0
for r in rows:
 p=np.array([float(r[k]) for k in ['x','y','z']]);fi=int(r['face']);ex=int(r['exit_face']);a=N[fi];b=N[ex];nshared=len(set(map(tuple,T[fi]))&set(map(tuple,T[ex])));adj[nshared]+=1
 denom=np.linalg.norm(b-np.dot(a,b)*a);pd=abs(np.dot(b,p-T[ex,0]))/denom if denom>1e-10 else None
 r['entry_exit_shared_original_vertices']=nshared;r['distance_to_two_original_plane_intersection_mm']=pd
 z=(p[2]-2)/(148/55.2);family='low_storeys_steps_slanted_columns' if z<13.05 else 'upper_storeys_terrace_and_band_junctions' if z<50.12 else 'roof_cap_and_supports';r['source_zone']=family;groups[(family,r['classification'])].append(r)
s=[]
for (family,cl),v in groups.items():
 field='pair_root' if cl=='two_actual_faces' else 'triple_root';s.append({'source_zone':family,'direction_construction':cl,'samples':len(v),'min_continuous_root_mm':min(float(r[field]) for r in v),'min_original_normal_first_mm':min(float(r['raw_first']) for r in v),'max_plane_intersection_distance_mm':max(r['distance_to_two_original_plane_intersection_mm'] or 0 for r in v),'actual_shared_vertices_histogram':dict(collections.Counter(r['entry_exit_shared_original_vertices'] for r in v))})
j={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'groups':s,'entry_exit_shared_vertices_histogram':dict(adj),'rows':rows,'limits':'Plane-intersection distance is not automatically distance to a finite shared edge. Faces without a shared edge remain explicit; inward roots do not erase original first segments, air, or failed pair directions. No global wall thickness or physical print guarantee.'};(R/'short-root-groups.json').write_text(json.dumps(j,indent=2));print(s)
