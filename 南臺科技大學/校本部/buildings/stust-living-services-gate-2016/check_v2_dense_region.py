"""Fail-closed dense original-normal screening of entire V/fold/nose region.
Selection uses source geometry bounds, not measured thickness. No repaired mesh.
"""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
O=Path(__file__).resolve().parent
m=trimesh.load(O/'model.stl',process=False);T=m.triangles
p=json.loads((O/'draft-parameters.json').read_text());s=p['scale_mm_per_m'];B=s*1.2
j=json.loads((O/'dense-first-chords.json').read_text());assert j['stl_sha256']==hashlib.sha256((O/'model.stl').read_bytes()).hexdigest()
source=T/s;source[:,:,2]-=1.2
xy=lambda q:np.array([(q[0]-1000)*p['aerial_m_per_pixel'],(800-q[1])*p['aerial_m_per_pixel']])
a=xy(p['source_pixel_polygons']['body_provisional'][0]);b=xy(p['source_pixel_polygons']['body_provisional'][3]);u=(b-a)/np.linalg.norm(b-a);n=np.array([u[1],-u[0]])
c=source.mean(axis=1);dep=(c[:,:2]-a)@n;along=(c[:,:2]-a)@u
selection=(dep>-.8)&(dep<4.2)&(along>.3)&(along<np.linalg.norm(b-a)-.3)&(c[:,2]>2.64)&(c[:,2]<13.6)
ids=set(np.where(selection)[0].tolist());rows=[r for r in j['samples'] if r['face'] in ids]
# Add actual first-exit triangle identity for the lowest chord in each original face.
worst={}
for r in rows:
 i=r['face']
 if i not in worst or r['first_solid_mm']<worst[i]['first_solid_mm']:worst[i]=r
exits=[]
for i,r in worst.items():
 point=np.array(r['point_mm']);normal=np.array(r['normal']);exitpoint=point+normal*.0001-normal*r['hits_mm'][1]
 closest=trimesh.triangles.closest_point(T,np.repeat(exitpoint[None,:],len(T),axis=0));distance=np.linalg.norm(closest-exitpoint,axis=1);fi=int(np.argmin(distance))
 exits.append(dict(r,first_exit_face=fi,first_exit_point_mm=exitpoint.tolist(),exit_face_normal=m.face_normals[fi].tolist(),exit_face_distance_mm=float(distance[fi])))
checks={'correct_stl_bound_to_dense_samples':True,'every_selected_face_has_all_seven_probes':len(rows)==7*len(ids),'all_region_first_solid_chords_above_0p8mm':all(r['first_solid_mm']>=.8 for r in rows),'exit_faces_on_original_surface':all(r['exit_face_distance_mm']<1e-4 for r in exits)}
out={'passed':all(checks.values()),'checks':checks,'stl_sha256':j['stl_sha256'],'selection':'Original face centroid: facade-along0.3..L-0.3m, inwarddepth-0.8..4.2m, sourceZ2.64..13.6m. All normals, including groove sides/floors/tops and finite nose/underside. Selection does not depend on measured thickness.','faces':len(ids),'dense_probes':len(rows),'minimum_first_solid_chord_mm':min(r['first_solid_mm'] for r in rows),'original_face_minimum_exit_records':exits,'limitations':'Finite sampling including1percent inset corners/edges; excludes geometric far-end0.3m boundary regions, separately retained in whole-mesh dense file. Not global minimum-wall certification or print test.'}
(O/'v2-dense-region-check.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k!='original_face_minimum_exit_records'});assert out['passed']
