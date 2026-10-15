from pathlib import Path
import json,numpy as np,trimesh,hashlib
R=Path(__file__).parent;Q=R;F=R/'model.stl';m=trimesh.load(F,process=False);d=json.loads((Q/'adaptive-origin-evidence.json').read_text());out=[]
for s in d['samples']:
 o=np.array(s['validated_ray_origin_mm']);v=np.array(s['direction']);h=s['strict_hits'];p=o+v*(h[0]['distance_mm']+h[1]['distance_mm'])/2;root=np.array([7.5-p[0],7.5-p[1],0]);root/=np.linalg.norm(root);spans=[]
 for di in np.vstack((root,np.eye(3),-np.eye(3))):
  hit,ri,fi=m.ray.intersects_location([p],[di],multiple_hits=True);ds=(hit-p)@di;ii=np.where(ds>1e-10)[0];ii=ii[np.argsort(ds[ii])];f=int(ii[0]);spans.append({'direction':di.tolist(),'first_exit_distance_mm':float(ds[f]),'original_exit_face_id':int(fi[f]),'hit_point_mm':hit[f].tolist()})
 out.append({'sample_index':s['sample_index'],'validated_first_material_chord_mm':s['actual_first_material_span_mm'],'first_material_midpoint_mm':p.tolist(),'midpoint_inside':bool(m.contains([p])[0]),'directions':spans,'maximum_continuous_root_mm':max(x['first_exit_distance_mm']for x in spans)})
r={'stl_sha256':hashlib.sha256(F.read_bytes()).hexdigest(),'method':'Six corrected outside-origin normal segments, each independently checked from true material midpoint to first exit along radial backing and6axes. No bridging across air.','samples':out,'passed':all(x['midpoint_inside']and x['maximum_continuous_root_mm']>=.8 for x in out)};(Q/'corrected-origin-root-check.json').write_text(json.dumps(r,indent=2));print(r['passed'],[(x['sample_index'],x['validated_first_material_chord_mm'],x['maximum_continuous_root_mm'])for x in out])
