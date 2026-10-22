from pathlib import Path
import numpy as np,json
A=Path(__file__).resolve().parents[1]
v=np.fromfile(A.parent/'model.stl',dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]),offset=84)['v'].astype(float)
m=json.loads((A/'face-materials.json').read_text())['face_material_indices'];selected=set(np.flatnonzero(m));expected=set();groups={};e=.001
for x in range(0,56,5):
 ids=[]
 for i,t in enumerate(v):
  if not all(x-.75-e<=p[0]<=x+.75+e and 44-e<=p[1]<=49+e and 39-e<=p[2]<=63+e for p in t):continue
  side=all(abs(p[0]-(x-.75))<e for p in t) or all(abs(p[0]-(x+.75))<e for p in t)
  tip=all(abs(p[1]-49)<e for p in t) and (all(p[2]<=50.5+e for p in t) or all(p[2]>=52.1-e for p in t))
  if side or tip:ids.append(i)
 assert len(ids)==20;expected.update(ids);groups[str(x)]={'faces':20,'area_mm2':float(sum(np.linalg.norm(np.cross(v[i,1]-v[i,0],v[i,2]-v[i,0]))/2 for i in ids))}
assert selected==expected and len(selected)==240 and len(v)==7246
(A/'qa/material-boundaries.json').write_text(json.dumps({'groups':groups,'all_vertex_bounded_full_faces':True,'colored_faces':240,'neutral_faces':7006,'no_subdivision':True,'beam_and_end_blades_and_other_elevations_excluded':True},indent=2)+'\n')
