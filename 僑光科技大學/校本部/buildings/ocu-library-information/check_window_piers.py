"""Actual east paired-window pier width and continuous rear backing; original surface rays."""
from pathlib import Path
import numpy as np,trimesh,json,hashlib
from original_rays import OriginalRays
R=Path(__file__).parent;m=trimesh.load(R/'model.stl',process=False);ray=OriginalRays(m);S=1.6552519477888414;a=np.radians(-2.5);A=np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1.]])
rows=[]
for z in [23,28,33,38]:
 for f in [.05,.25,.5,.75,.95]:
  p=A@(np.array([29,-5.89,z+2.7*f])+[0,0,1.3])*S;sections=[]
  for d,required in [(A@np.array([1.,0,0]),.65*S),(A@np.array([0.,1,0]),20*S)]:
   h=ray.hits(p-d*250,d);pairs=[(x,y)for x,y in zip(h[::2],h[1::2])if x[0]<250<y[0]];assert len(pairs)==1;v=pairs[0][1][0]-pairs[0][0][0];assert v>=required-1e-5
   sections.append(dict(axis=d.tolist(),continuous_original_solid_width_mm=v,required_mm=required,all_original_hits=h))
  rows.append(dict(local_z_m=z+2.7*f,world_point_mm=p.tolist(),width_and_backing=sections))
report=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),checks={'twenty_designated_pier_sections_actual_width_and_continuous_backing':len(rows)==20},passed=True,samples=rows,minimum_width_mm=min(x['width_and_backing'][0]['continuous_original_solid_width_mm']for x in rows),limits='Designated formerly narrow east paired-window piers, not global wall thickness. Opposite-face width is tested directly rather than substituted by an unrelated corner bisector.')
(R/'window-piers.json').write_text(json.dumps(report,indent=2));print(report['minimum_width_mm'])
