"""Independent all-three-vertices checks against original radial planes, not centroids."""
from pathlib import Path
import numpy as np,struct,json,hashlib
A=Path(__file__).resolve().parents[1];raw=(A.parent/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0]
t=np.array([struct.unpack_from('<9f',raw,96+50*i) for i in range(n)]).reshape(n,3,3);c=np.array(json.loads((A/'face-materials.json').read_text())['face_material_indices']);eps=.002
expected=np.zeros(n,int);counts={}
for a in [-150,-120,-90,-60,-30]:
 q=np.deg2rad(a);r=t[:,:,0]*np.cos(q)+t[:,:,1]*np.sin(q);s=-t[:,:,0]*np.sin(q)+t[:,:,1]*np.cos(q)
 for z in [52,76]:
  m=(np.abs(r-51.5).max(1)<eps)&(np.abs(s).max(1)<=6.25+eps)&(t[:,:,2].min(1)>=z-eps)&(t[:,:,2].max(1)<=z+13.2+eps)
  assert m.sum()==8;expected[m]=1;counts[f'glass_{a}_{z}']=int(m.sum())
for a in [-165,-135,-105,-75,-45,-15]:
 q=np.deg2rad(a);r=t[:,:,0]*np.cos(q)+t[:,:,1]*np.sin(q);s=-t[:,:,0]*np.sin(q)+t[:,:,1]*np.cos(q)
 m=(r.min(1)>=45.4-eps)&(r.max(1)<=54.6+eps)&(abs(s).max(1)<=5.8+eps)&(t[:,:,2].min(1)>=3-eps)&(t[:,:,2].max(1)<=11.3+eps)&((abs(r-54.6).max(1)<eps)|(abs(s-5.8).max(1)<eps)|(abs(s+5.8).max(1)<eps))
 assert m.sum()==6 and np.all(expected[m]==0);expected[m]=2;counts[f'plinth_{a}']=int(m.sum())
assert np.array_equal(c,expected);assert np.bincount(c).tolist()==[4806,80,36]
# Crown openings, artificial rear, base and continuous awning must not acquire material claims.
for m in [np.all(abs(t[:,:,1])<eps,axis=1),t[:,:,2].min(1)>=99.5-eps,t[:,:,2].max(1)<=3+eps,(t[:,:,2].min(1)>=45-eps)&(t[:,:,2].max(1)<=47.4+eps)]:assert np.all(c[m]==0)
d={'triangles':n,'all_vertices_full_existing_faces':True,'no_centroid_or_subdivision':True,'expected_face_map_exact':True,'counts':counts,'material_counts':[4806,80,36],'unsegmented_awning_crown_base_rear_held_neutral':True,'source_sha256':hashlib.sha256(raw).hexdigest()}
(A/'qa/boundary-validation.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))
