"""Every original triangle: centre and 3 near-edge probes, original face normals.
Finite sample audit, not a global min-wall proof. Records short first solid chords without hiding them.
"""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
from original_rays import OriginalRays
R=Path(__file__).parent;m=trimesh.load(R/'model.stl',process=False);t=m.triangles;n=m.face_normals
weights=np.array([[1/3]*3,[.49,.49,.02],[.49,.02,.49],[.02,.49,.49]])
points=np.einsum('sv,fvd->fsd',weights,t).reshape(-1,3);normals=np.repeat(n,4,axis=0);dirs=-normals;origins=points+normals*.000001
rows=[];low=[];epsilon=.000001
ray=OriginalRays(m)
for idx,(o,d)in enumerate(zip(origins,dirs)):
 unique=ray.hits(o,d)
 assert len(unique)>=2 and abs(unique[0][0]-epsilon)<.00001,(idx,unique)
 chord=unique[1][0]-unique[0][0]
 row={'original_triangle_index':idx//4,'sample_index':idx%4,'surface_point_mm':points[idx].tolist(),'original_outward_normal':normals[idx].tolist(),'first_solid_chord_mm':chord,'all_ray_intersections_mm_face':unique}
 rows.append(row)
 if chord<.8:low.append(row)
r={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'original_triangles':len(t),'samples':len(rows),'minimum_sampled_first_chord_mm':min(v['first_solid_chord_mm']for v in rows),'under_0p8mm_count':len(low),'short_chords':low,'all_samples':rows,'checks':{'every_original_triangle_four_samples':len(rows)==len(t)*4,'all_original_surface_entry_hits_confirmed':True,'all_sampled_first_chords_ge_0p8mm':len(low)==0},'limits':'Near corners may have short grazing chords. This report does not label every short chord as a thin wall or waive it; independently review location and root. No global minimum-wall or printed-part claim.'}
r['passed']=all(r['checks'].values())
(R/'surface-chords.json').write_text(json.dumps(r));assert r['passed']
print({k:v for k,v in r.items()if k not in ['all_samples','short_chords']})
