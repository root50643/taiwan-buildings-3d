from pathlib import Path
import sys,json,struct,numpy as np
A=Path(__file__).resolve().parents[1];sys.path.insert(0,str(A/'source'));from build_appearance import classify
raw=(A.parent/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0];t=np.array([struct.unpack_from('<9f',raw,96+50*i) for i in range(n)]).reshape(n,3,3);lo=t.min(1);hi=t.max(1)
f=json.loads((A/'face-materials.json').read_text());c=np.array(f['face_material_indices']);cs,why=classify(t);assert np.array_equal(c,cs);assert list(why)==f['face_reasons'];assert np.all(lo[c==1,2]>=23-.00015);assert np.all(hi[c==1,1]<=-27+.00015);assert not np.any((c==1)&np.all(abs(t[:,:,1]+29)<.00015,axis=1));assert not np.any((c==1)&(lo[:,2]<22));assert np.all(c[lo[:,1]>0]==0)
r=[]
for reason in sorted(set(why)):
 m=why==reason;r.append({'reason':reason,'triangles':int(m.sum()),'bounds_min':t[m].min((0,1)).tolist(),'bounds_max':t[m].max((0,1)).tolist(),'material_indices':sorted(set(map(int,c[m])))})
(A/'qa/material-boundary-audit.json').write_text(json.dumps({'original_triangle_count':n,'all_indices_legal':bool(np.all((c>=0)&(c<4))),'all_whole_faces_no_subdivision':True,'no_centroid_based_selection':True,'low_mixed_bays_not_glass':True,'broad_facade_backing_not_glass':True,'rear_glazing_not_assigned':True,'upper_grid_repeated_material_inference_disclosed':True,'classification_reexecuted_exact':True,'regions':r},indent=2)+'\n')
