"""Original mesh two canopy posts: normal cross-sections and nine continuous base roots."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
from original_rays import OriginalRays
R=Path(__file__).parent;m=trimesh.load(R/'model.stl',process=False);ray=OriginalRays(m);S=1.209283792097708;A=np.array([[-np.sqrt(3)/2,-.5,0],[.5,-np.sqrt(3)/2,0],[0,0,1.]])
def pt(x,y,z):return A@np.array([x*.86,y,z+1.5])*S
rows=[]
for x in [-15,-9]:
 widths=[];roots=[]
 for z in np.linspace(.1,2.9,7):
  p=pt(x,-17,z)
  for axis,nom in [(0,1.2*.86*S),(1,1.2*S)]:
   d=A[:,axis];hits=ray.hits(p-d*200,d);assert len(hits)%2==0
   iv=[(a,b)for a,b in zip(hits[::2],hits[1::2])if a[0]<=200<=b[0]];assert len(iv)==1
   width=iv[0][1][0]-iv[0][0][0];assert width>=nom-1e-5
   widths.append(dict(z_mm=p[2],axis=axis,normal=d.tolist(),normal_solid_width_mm=width,nominal_mm=nom,original_hits=hits))
 for dx in [-.55,0,.55]:
  for dy in [-.55,0,.55]:
   p=pt(x+dx,-17+dy,0);o=[p[0],p[1],-1];hits=ray.hits(o,[0,0,1]);required=pt(x,-17,3.9)[2];assert abs(hits[0][0]-1)<1e-5 and hits[1][0]-1>=required-1e-5
   roots.append(dict(xy_mm=o[:2],first_exit_z_mm=hits[1][0]-1,required_continuous_to_canopy_z_mm=required,original_hits=hits))
 rows.append(dict(local_center_m=[x,-17],normal_section_mm=[1.2*.86*S,1.2*S],normal_samples=widths,base_to_canopy_roots=roots))
r=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),passed=True,supports=rows,limits='Only both designated canopy posts: seven levels, two original normal axes and nine base-to-canopy first-interval roots each. No whole-model minimum-wall guarantee.')
(R/'support-roots.json').write_text(json.dumps(r,indent=2));print('Two original square canopy posts, all normal widths and nine base-to-canopy roots passed.')
