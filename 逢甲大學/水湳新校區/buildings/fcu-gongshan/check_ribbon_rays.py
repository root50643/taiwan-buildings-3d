from pathlib import Path
import numpy as np,trimesh,json,hashlib
P=Path(__file__).parent;F=P/'model.stl'
m=trimesh.load(F,process=False)
aa=np.array([1127.,752.]);bb=np.array([1315.,875.]);u=(bb-aa)/np.linalg.norm(bb-aa);n=np.array([-u[1],u[0]]);nw=np.array([n[0],-n[1],0.])
def xyz(t,d,z):
 q=aa+(bb-aa)*t+n*d
 return np.array([(q[0]-950)*.125,(650-q[1])*.125,z])
def hits(o,v):
 p,_,_=m.ray.intersects_location([o],[v],multiple_hits=True)
 return sorted(set(round(float(np.dot(x-o,v)),6)for x in p if np.dot(x-o,v)>0))
rows=[];ts=np.linspace(.035,.65,8)
for t in (ts[:-1]+ts[1:])/2:
 for z in [5.,9.]:
  o=xyz(t,0,z)-nw*5;hh=hits(o,nw)
  rows.append(dict(kind='original-face normal backing',t=float(t),z=z,hits_mm=hh,first_interval_mm=hh[1]-hh[0]if len(hh)>=2 else None, nominated_backing_interval_mm=hh[min(range(len(hh)),key=lambda i:abs(hh[i]-5.5))+1]-min(hh,key=lambda x:abs(x-5.5)), note="All intersections retained; nearby sloping roof can precede backing; select entry nearest5.5mm and its next exit, retaining all intersections"))
for t in ts:
 o=xyz(t,3,-1);hh=hits(o,np.array([0.,0.,1.]))
 rows.append(dict(kind='original-face vertical frame-to-base',t=float(t),hits_mm=hh,continuous_from_base=bool(len(hh)==2 and abs(hh[0]-1)<1e-5)))
result=dict(stl_sha256=hashlib.sha256(F.read_bytes()).hexdigest(),method='Unprocessed original STL triangles; ray intersections only, no mesh repair. Selected new ribbon backing and frame roots, not whole-model minimum wall.',samples=rows)
result['checks']={'all_designated_backing_chords_ge_1p299mm':all(r['nominated_backing_interval_mm']>=1.299 for r in rows if 'nominated_backing_interval_mm' in r),'all_eight_frame_roots_continuous':all(r['continuous_from_base'] for r in rows if 'continuous_from_base' in r)};result['passed']=all(result['checks'].values());assert result['passed']
(P/'ribbon-rays.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
