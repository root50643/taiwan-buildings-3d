"""Measure front recesses by ray/triangle intersection of the delivered raw binary STL.
This is geometric relief verification, not a claim of real-building measured dimensions.
"""
from pathlib import Path
import json,struct,hashlib
import numpy as np
R=Path(__file__).resolve().parent; raw=(R/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0]
rec=np.frombuffer(raw,offset=84,dtype=np.dtype([('normal','<f4',(3,)),('v','<f4',(3,3)),('attr','<u2')]),count=n);tri=rec['v'].astype(float)
def ray(x,z):
 o=np.array([x,-80,z]);d=np.array([0.,1.,0.]);e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];h=np.cross(np.broadcast_to(d,e2.shape),e2);a=np.einsum('ij,ij->i',e1,h);ok=np.abs(a)>1e-10;f=np.zeros_like(a);f[ok]=1/a[ok];s=o-tri[:,0];u=f*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1);v=f*(q@d);t=f*np.einsum('ij,ij->i',e2,q);ok &= (u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-8);ts=sorted(t[ok]);hits=[]
 for t in ts:
  if not hits or abs(t-hits[-1])>1e-5:hits.append(float(t))
 assert hits
 return {'origin_mm':o.tolist(),'direction':[0,1,0],'intersection_distances_mm':hits,'first_hit_y_mm':hits[0]-80}
r={'entrance':ray(.137,5.173),'podium_reference':ray(.137,8.573),'between_v_glazing':ray(.137,22.173),'v_leg_reference':ray(2.21,22.173)}
a=r['entrance']['first_hit_y_mm']-r['podium_reference']['first_hit_y_mm'];b=r['between_v_glazing']['first_hit_y_mm']-r['v_leg_reference']['first_hit_y_mm']
checks={'entrance_recess_exceeds_4mm':a>4,'glazing_recess_behind_v_exceeds_2mm':b>2}
result={'passed':all(checks.values()),'checks':checks,'stl_sha256':hashlib.sha256(raw).hexdigest(),'entrance_recess_mm':a,'glazing_behind_v_mm':b,'rays':r,'limitation':'Distances are miniature STL measurements; not surveyed real-world dimensions. Recess back walls intentionally keep a printable solid core.'}
(R/'depth-ray-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,indent=2));assert result['passed']
