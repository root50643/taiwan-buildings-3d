from pathlib import Path
import numpy as np,json
A=Path(__file__).resolve().parents[1]
v=np.fromfile(A.parent/'model.stl',dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]),offset=84)['v'].astype(float)
m=json.loads((A/'face-materials.json').read_text())['face_material_indices']; selected=set(np.flatnonzero(m));expected=set();groups={}
for label,axis,plane,other,centers,half in [('front',1,-32.2,0,range(-55,60,10),4.25),('right',0,59.2,1,[-26,-15,-4,7],4.7)]:
 ids=[]
 for z in [14.1,38.1]:
  for c in centers:
   ix=[i for i,t in enumerate(v) if all(abs(p[axis]-plane)<.002 and c-half-.002<=p[other]<=c+half+.002 and z-.002<=p[2]<=z+18+.002 for p in t)]
   assert len(ix)==2;ids+=ix
 expected.update(ids);groups[label]={'faces':len(ids),'area_mm2':float(sum(np.linalg.norm(np.cross(v[i,1]-v[i,0],v[i,2]-v[i,0]))/2 for i in ids))}
assert selected==expected and len(selected)==64 and len(v)==3404
(A/'qa/material-boundaries.json').write_text(json.dumps({'groups':groups,'all_vertex_bounded_full_faces':True,'colored_faces':64,'neutral_faces':3340,'no_subdivision':True,'left_rear_roof_right_last_two_bays_excluded':True},indent=2)+'\n')
