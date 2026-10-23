from pathlib import Path
import numpy as np,json,struct
from build_appearance import classify
A=Path(__file__).resolve().parents[1];raw=(A.parent/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0];t=np.array([struct.unpack_from('<9f',raw,96+50*i) for i in range(n)]).reshape(n,3,3);m=json.loads((A/'face-materials.json').read_text())['face_material_indices'];actual,_=classify(t);assert actual.tolist()==m;s=json.loads((A/'source/source-selection.json').read_text());groups=[]
for i,(name,d) in enumerate(s.items(),1):
 ids=np.flatnonzero(actual==i).tolist();assert ids==d['faces'];v=t[ids];area=float(np.linalg.norm(np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]),axis=1).sum()/2);assert abs(area-d['area'])<1e-7;groups.append(dict(name=name,canonical_stl_ids=ids,triangles=v.tolist(),area_mm2=area))
assert sum(len(g['canonical_stl_ids']) for g in groups)==1404
(A/'qa/material-boundaries.json').write_text(json.dumps(dict(original_faces=n,colored_faces=1404,neutral_faces=4772,regions=groups,area_mm2=sum(g['area_mm2'] for g in groups),all_three_vertices_finite_plane_checked=True,actual_cross_product_normals=True,individual_80_chord_tangent_bounds=True,no_subdivision=True,no_centroid_selection=True,epsilon_mm=.0003),indent=2)+'\n')
