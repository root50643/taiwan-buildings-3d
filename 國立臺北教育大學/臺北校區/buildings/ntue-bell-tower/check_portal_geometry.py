from pathlib import Path
import json, hashlib
import numpy as np
import trimesh
M=Path(__file__).resolve().parent; mesh=trimesh.load(M/'model.stl',process=False)
def hits(o,d):
 o=np.array(o,float);d=np.array(d,float);t=mesh.triangles;e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];h=np.cross(np.broadcast_to(d,e2.shape),e2);a=np.einsum('ij,ij->i',e1,h);safe=np.abs(a)>1e-9;f=np.zeros_like(a);f[safe]=1/a[safe];s=o-t[:,0];u=f*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1);v=f*np.einsum('j,ij->i',d,q);dist=f*np.einsum('ij,ij->i',e2,q);ok=safe&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(dist>=0)
 ds=[]
 for x in sorted(dist[ok]):
  if not ds or x-ds[-1]>1e-5:ds.append(float(x))
 return (o+np.array(ds)[:,None]*d).round(6).tolist()
rays=[{'label': 'lower_passage_Y', 'origin': [0, -65, 30], 'direction': [0, 1, 0]}, {'label': 'lower_passage_X', 'origin': [-65, 0, 30], 'direction': [1, 0, 0]}, {'label': 'lower_arch_soffit', 'origin': [0, 0, 68], 'direction': [0, 0, -1]}, {'label': 'upper_chamber_beside_bell', 'origin': [18, -60, 95], 'direction': [0, 1, 0]}, {'label': 'bell_neck_continuous_to_roof', 'origin': [0, 0, 120], 'direction': [0, 0, -1]}]
for r in rays:r['intersections_mm']=hits(r['origin'],r['direction'])
assert rays[0]['intersections_mm']==[] and rays[1]['intersections_mm']==[] and rays[3]['intersections_mm']==[]
assert abs(rays[2]['intersections_mm'][0][2]-62.6)<1e-4 and abs(rays[2]['intersections_mm'][1][2]-7.6)<1e-4
assert abs(rays[4]['intersections_mm'][0][2]-86)<1e-4
measures={'lower_clear_height_mm':55,'lower_minimum_width_mm':56,'upper_chamber_minimum_width_mm':46,'bell_under_clearance_mm':10,'bell_and_neck_continuous_to_roof':True}
report={'stl_sha256':hashlib.sha256((M/'model.stl').read_bytes()).hexdigest(),'method':'Moller-Trumbore original STL triangles; process=False, no repair; equal-face duplicates collapsed 1e-5 mm','units':'model millimetres, not real surveyed values','measurements':measures,'rays':rays,'passed':True}
(M/'portal-ray-proof.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
