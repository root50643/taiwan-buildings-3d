"""Designated original-surface normals and continuous vertical support roots; no skipped air."""
from pathlib import Path
import numpy as np,trimesh,json,hashlib,subprocess,tempfile,os
from original_rays import OriginalRays
R=Path(__file__).resolve().parent;m=trimesh.load(R/'model.stl',process=False);ray=OriginalRays(m);rows=[];points=[]
def add(family,o,d,minimum=.8):
 o=np.array(o,float);d=np.array(d,float);d/=np.linalg.norm(d);hits=ray.hits(o,d);assert hits,(family,o,d)
 p=o+d*hits[0][0];fi=hits[0][1];n=m.face_normals[fi];origin=p+n*1e-5;h=ray.hits(origin,-n);assert len(h)>=2
 length=h[1][0]-h[0][0];air=h[2][0]-h[1][0] if len(h)>2 else 1
 ps=[origin,p-n*1e-5,origin-n*(h[0][0]+h[1][0])/2,origin-n*(h[1][0]+min(air/4,1e-5))];ix=list(range(len(points),len(points)+4));points.extend(ps)
 rows.append(dict(family=family,original_face=fi,source_surface_mm=p.tolist(),normal=n.tolist(),normal_all_hits=h,first_normal_mm=length,required_mm=minimum,indices=ix))
for x,r in [(0,1.45),(-41.5,.6),(-35.5,.6)]:
 y=-26.5 if x==0 else -31.6
 for z in [3.13,7.37,11.03]:
  for a in [.17,1.13,2.29,3.41,4.57,5.73]:add('entrance_circular_column'if x==0 else'local_canopy_posts',[x+5*np.cos(a),y+5*np.sin(a),z],[-np.cos(a),-np.sin(a),0])
 # Original top/down normal ray through the same support footprint to the base.
 add('continuous_support_to_base',[x+.173,y+.131,60],[0,0,-1])
for x in [-40.4,-38.3,-36.2]:
 for y in [-31.73,-30.39]:add('local_canopy_plate',[x,y,20],[0,0,-1])
for x in [-9.31,-4.31,4.31,9.31]:add('deep_entry_backing',[x,-34,7.23],[0,1,0])
for x in [13.31,15.31,19.31,21.31,24.81,27.31,30.31,32.31]:
 for z in [6.13,8.17,10.93]:add('right_window_backing',[x,-33,z],[0,1,0])
for x in [17.25,28.75]:
 for z in [5.73,7.13,9.13]:add('flush_glazing_bar',[x+.113,-33,z],[0,1,0])
for x,z in [(-33,5.37),(-31.2,6.87),(-29.4,4.37),(-27.6,6.87),(-43.5,5.37),(-41,7.37)]:add('left_small_window_backing',[x+.13,-33,z],[0,1,0])
for sx in [-1,1]:
 for y in [-13.17,-1.17,10.83,22.83,34.83]:
  add('side_window_above_repaired_sill',[sx*65,y,15.37],[-sx,0,0]);add('side_window_sill',[sx*58.13,y,17],[0,0,-1])
for x in np.linspace(-69,69,13):
 for z in [20.071,40.671,41.871]:add('curved_rib_width',[x-2,-22 if z>40 else -38,z],[1,0,0])
with tempfile.TemporaryDirectory() as td:
 D=Path(td);m.triangles.astype('<f8').tofile(D/'tri');np.array(points).astype('<f8').tofile(D/'pts');subprocess.run(['g++','-O3','-fopenmp',str(R/'winding_parallel.cpp'),'-o',str(D/'w')],check=True);subprocess.run([str(D/'w'),str(D/'tri'),str(D/'pts'),str(D/'vals')],check=True,env={**os.environ,'OMP_NUM_THREADS':'4'});v=np.loadtxt(D/'vals',delimiter=',')[:,1]
for q in rows:q['controls']=[dict(expected=e,winding=float(v[i]),point_mm=points[i].tolist(),passed=bool(abs(v[i]-e)<1e-7))for i,e in zip(q['indices'],[0,1,1,0])]
checks=dict(all_designated_normal_thicknesses_ge_0p8=all(q['first_normal_mm']>=q['required_mm']-1e-5 for q in rows),all_original_winding_controls=all(c['passed']for q in rows for c in q['controls']))
o=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),count=len(rows),checks=checks,rows=rows,limits='Finite designated samples; vertical support rays use actual top surface and continuous first material span. Not global minimum wall thickness.')
(R/'designated-roots.json').write_text(json.dumps(o,indent=2));print(checks);print('fails',[(q['family'],q['source_surface_mm'],q['first_normal_mm'],[c['winding']for c in q['controls']])for q in rows if q['first_normal_mm']<.79999 or not all(c['passed']for c in q['controls'])]);raise SystemExit(0 if all(checks.values())else 1)
