"""Original-triangle parity control before/inside/after every dense first chord."""
from pathlib import Path
import json,numpy as np,trimesh,hashlib
O=Path(__file__).resolve().parent;m=trimesh.load(O/'model.stl',process=False)
j=json.loads((O/'dense-first-chords.json').read_text());assert j['stl_sha256']==hashlib.sha256((O/'model.stl').read_bytes()).hexdigest()
controls=[]
for r in j['samples']:
 p=np.array(r['point_mm']);n=np.array(r['normal']);o=p+n*.0001;hs=r['hits_mm']
 controls.extend([p-n*.0001,o,o-n*((hs[0]+hs[1])/2),o-n*(hs[1]+.0001)])
flags=[]
for i in range(0,len(controls),400):
 flags.extend(m.contains(np.array(controls[i:i+400])).tolist())
 if i%12000==0:print(i,len(controls),flush=True)
fail=[]
for i,r in enumerate(j['samples']):
 got=flags[4*i:4*i+4]
 if got!=[True,False,True,False]:fail.append({'face':r['face'],'point_mm':r['point_mm'],'first_solid_mm':r['first_solid_mm'],'hits_mm':r['hits_mm'],'parity':got})
out={'passed':not fail,'stl_sha256':j['stl_sha256'],'dense_samples':len(j['samples']),'contains_points':len(controls),'expected_order':['just_inside_original_face','just_outside_original_face','mid_first_solid_chord','just_after_first_exit_air'],'expected_values':[True,False,True,False],'failure_count':len(fail),'failures':fail,'method':'process=False original triangles; independent contains checks for every dense first-chord probe. No second solid interval is substituted for a short first interval.'}
(O/'dense-parity-check.json').write_text(json.dumps(out,indent=2));print('PASS' if out['passed'] else 'FAIL',len(fail));assert out['passed']
