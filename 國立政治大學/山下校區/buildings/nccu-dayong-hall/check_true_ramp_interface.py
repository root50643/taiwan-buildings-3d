"""Dense raw tests at the actual landing left boundary, not the old ramp endpoint."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
from qa_model import raw_read
A=Path(__file__).resolve().parent;_,v,f=raw_read(A/'model.stl');m=trimesh.Trimesh(v,f,process=False);S=2.5;q=lambda x:round(x*1024)/1024
end=q(-10.5-2.15);start=-28.5;lo=q(1.88);hi=q(3.8)
offsets=sorted(set([0.]+[sign*d for sign in [-1,1] for d in [1e-7,1e-6,1e-5,1e-4,.001,.01,.05,.1,.2]]+[round(float(x),5) for x in np.arange(-.2,.201,.01)]));ys=[-5,-4.6,-4.333372497558594,-4.15]
tri=m.triangles;e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];d=np.array([0,0,-1]);pv=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,pv);valid=np.abs(det)>1e-12;inv=np.divide(1,det,out=np.zeros_like(det),where=valid)
rows=[];probes=[]
for dx in offsets:
 x=end+dx;expected=hi if x>=end else lo+(x-start)/(end-start)*(hi-lo)
 for y in ys:
  origin=np.array([x,y,hi+.15])*S;tv=origin-tri[:,0];u=np.einsum('ij,ij->i',tv,pv)*inv;qv=np.cross(tv,e1);vv=qv@d*inv;dist=np.einsum('ij,ij->i',e2,qv)*inv;sel=valid&(u>=-1e-9)&(vv>=-1e-9)&(u+vv<=1+1e-9)&(dist>1e-7);assert sel.any();hit=origin[2]-dist[sel].min();err=abs(hit-expected*S)
  rows.append(dict(x_design=x,y_design=y,offset_from_true_landing_edge=dx,first_hit_mm=float(hit),expected_mm=expected*S,error_mm=float(err)));assert err<.00002,(x,y,err)
  for delta,w in [(-.03,True),(.03,False),(.6,False),(1.2,False),(1.8,False),(2.2,False)]:probes.append(dict(point_mm=(np.array([x,y,expected+delta])*S).tolist(),expected_solid=w))
got=[]
for i in range(0,len(probes),64):got.extend(m.contains(np.asarray([r['point_mm'] for r in probes[i:i+64]])).tolist())
failed=[]
for r,g in zip(probes,got):
 r['actual_solid']=g
 if r['expected_solid']!=g:failed.append(r)
r=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),true_landing_x_design=end,previous_incorrect_ramp_endpoint_design=-12.5,true_interface_ray_count=len(rows),max_ray_error_mm=max(r['error_mm'] for r in rows),rays=rows,occupancy_count=len(probes),failed=failed,probes=probes,limits='Model geometry continuity only; not surveyed access slope or building-code certification. Prior wrong-interface expectations remain in historical evidence.')
(A/'qa/true-ramp-interface.json').write_text(json.dumps(r,indent=2));print('true landing interface',len(rows),'rays',len(probes),'occupancy','failed',len(failed),'maxerror',r['max_ray_error_mm']);assert not failed,failed[:8]
