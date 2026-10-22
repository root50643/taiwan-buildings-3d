from pathlib import Path
import json,struct,numpy as np
A=Path(__file__).resolve().parents[1];raw=(A.parent/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0];t=np.array([struct.unpack_from('<9f',raw,96+50*i) for i in range(n)]).reshape(n,3,3);c=np.array(json.loads((A/'face-materials.json').read_text())['face_material_indices']);eps=.00015
normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);selected=np.zeros(n,dtype=bool);counts={}
for x in [-31,20]:
 lo=t.min(axis=1);hi=t.max(axis=1)
 def box(a,b):return np.all(lo>=np.array(a)-eps,axis=1)&np.all(hi<=np.array(b)+eps,axis=1)
 left=box([x-4.5,-16.5,2.8],[x-2.15,-16.5,56.8]);right=box([x+2.15,-16.5,2.8],[x+4.5,-16.5,56.8]);upper=box([x-4.5,-16.5,54],[x+4.5,-16.5,56.8]);cap=box([x-6,-17,56],[x+6,-17,57.8]);m=(left|right|upper|cap)&(normal[:,1]<0);selected|=m
 counts[str(x)]={'front_frame':int(((left|right|upper)&m).sum()),'cap_front':int((cap&m).sum())}
assert np.array_equal(c==1,selected);assert selected.sum()==128
r={'full_triangle_membership_only':True,'no_centroid_or_subdivision':True,'outward_normals_verified':True,'two_tower_regions':counts,'glass_crossbars_side_cheeks_mixed_horizontal_bands_excluded':True,'neutral_faces':int((c==0).sum()),'colored_face_indices':np.where(selected)[0].tolist()}
(A/'qa/material-boundaries.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
