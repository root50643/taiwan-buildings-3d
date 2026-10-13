"""Ray test of actual original STL portico void. No mesh repair or source inference.
Moller-Trumbore, first surface intersection; all dimensions in mm.
"""
from pathlib import Path
import numpy as np,trimesh,json,hashlib
R=Path(__file__).resolve().parent;m=trimesh.load(R/'model.stl',force='mesh',process=False);tri=m.triangles

def first(o,d):
 o=np.array(o,float);d=np.array(d,float);e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];h=np.cross(np.broadcast_to(d,e2.shape),e2);a=np.einsum('ij,ij->i',e1,h);ok=np.abs(a)>1e-10;f=np.zeros(len(a));f[ok]=1/a[ok];s=o-tri[:,0];u=f*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1);v=f*np.einsum('j,ij->i',d,q);t=f*np.einsum('ij,ij->i',e2,q);valid=ok&(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)&(t>1e-7);assert valid.any();tt=float(t[valid].min());return {'distance_mm':tt,'first_hit_mm':(o+d*tt).tolist()}
rows=[]
for x in [-30.071,-10.071,.071,10.071,30.071]:
 for z in [12.371,25.371,50.371]:
  o=[x,-40,z];v=first(o,[0,1,0]);rows.append({'kind':'front_to_recess','origin':o,'direction':[0,1,0],**v,'check':v['first_hit_mm'][1]>0})
for x in [-19.071,19.071]:
 o=[x,-40,25.371];v=first(o,[0,1,0]);rows.append({'kind':'main_column_control','origin':o,'direction':[0,1,0],**v,'check':-24<v['first_hit_mm'][1]<-22})
# Starts inside the intentionally empty gap between two main columns.
o=[-17.0,-20.571,25.371];v=first(o,[1,0,0]);rows.append({'kind':'between_columns','origin':o,'direction':[1,0,0],**v,'check':v['distance_mm']>34})
report={'method':'first-hit rays against delivered STL triangles without processing; void samples at three heights and five x positions, plus column and cross-gap controls','stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'all_checks_pass':all(x['check'] for x in rows),'rays':rows,'limitations':'Finite sampled evidence, not a universal void or full collision proof.'}
(R/'portico-void-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2));assert report['all_checks_pass']
