"""Exact source-face planar interval for the preserved normal/air boundary case.
No reclassification as bulk material or a remote exit; raw strict controls retained.
"""
from pathlib import Path
import numpy as np,trimesh,json,tempfile,subprocess,hashlib
R=Path(__file__).parent;m=trimesh.load(R/'model.stl',process=False);cases=json.loads((R/'all-after-boundary-candidates.json').read_text());reports=[]
W=np.array([[1/3]*3,[.98,.01,.01],[.01,.98,.01],[.01,.01,.98],[.495,.495,.01],[.01,.495,.495],[.495,.01,.495],[.49,.49,.02],[.49,.02,.49],[.02,.49,.49]])
for case in cases:
 q=dict(surface_point_mm=(W[case['sample']]@m.triangles[case['face']]).tolist(),original_outward_normal=m.face_normals[case['face']].tolist())
 p=np.array(q['surface_point_mm'],dtype=np.longdouble);n=np.array(q['original_outward_normal'],dtype=np.longdouble);o=p+n*1e-6;d=-n;tri=np.asarray(m.triangles[case['boundary_candidate_face']],dtype=np.longdouble);normal=np.cross(tri[1]-tri[0],tri[2]-tri[0]);normal/=np.linalg.norm(normal)
 assert abs(normal@d)<1e-15 and abs(normal@(o-tri[0]))<1e-15
 axis=int(np.argmax(abs(normal)));keep=[i for i in range(3)if i!=axis];t2=tri[:,keep];oo=o[keep];dd=d[keep];cross=lambda x,y:x[0]*y[1]-x[1]*y[0];orient=np.sign(cross(t2[1]-t2[0],t2[2]-t2[0]));lo=np.longdouble('-inf');hi=np.longdouble('inf')
 for i in range(3):
  v=t2[i];e=t2[(i+1)%3]-v;A=orient*cross(e,oo-v);B=orient*cross(e,dd)
  if abs(B)<1e-25:assert A>=0
  elif B>0:lo=max(lo,-A/B)
  else:hi=min(hi,-A/B)
 assert hi>lo and lo>=0
 pts=[];samples=[]
 for t in [lo+(hi-lo)*f for f in [.1,.5,.9]]:
  x=o+d*t;ids=[]
  for sign in [-1,1]:ids.append(len(pts));pts.append(np.asarray(x+normal*sign*1e-5,dtype=float))
  samples.append(dict(t_mm=float(t),surface=x.astype(float).tolist(),inside_outside_point_indices=ids))
 with tempfile.TemporaryDirectory()as td:
  D=Path(td);np.asarray(m.triangles,dtype='<f8').tofile(D/'tri.bin');np.array(pts).tofile(D/'pts.bin');subprocess.run(['g++','-O3',str(R/'original_winding.cpp'),'-o',str(D/'w')],check=True);subprocess.run([str(D/'w'),str(D/'tri.bin'),str(D/'pts.bin'),str(D/'out')],check=True);vals=np.loadtxt(D/'out',delimiter=',')[:,1]
 for s in samples:s['winding_inward_outward']=[float(vals[i])for i in s['inside_outside_point_indices']]
 checks={'ray_exactly_in_original_face_plane':True,'positive_length_original_triangle_boundary_interval':bool(hi>lo),'three_boundary_positions_material_below_air_above':all(abs(s['winding_inward_outward'][0]-1)<1e-7 and abs(s['winding_inward_outward'][1])<1e-7 for s in samples)}
 r=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),source_triangle=case['face'],sample=case['sample'],boundary_triangle=case['boundary_candidate_face'],original_boundary_triangle_mm=tri.astype(float).tolist(),interval_t_mm=[float(lo),float(hi)],interval_length_mm=float(hi-lo),samples=samples,checks=checks,passed=all(checks.values()),interpretation='Positive-length exterior boundary, neither open air nor extended bulk material. Raw first-normal/after-air failure is preserved; independent reviewer must decide the limited boundary case.')
 reports.append(r);assert r['passed']

result=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),count=len(reports),cases=reports,checks={'all_after_boundary_candidates_verified':all(q['passed']for q in reports)},interpretation='All sampled positive-length exterior boundary intervals are recorded; strict raw air booleans are not promoted to true.')
(R/'boundary-interval.json').write_text(json.dumps(result,indent=2));print('boundary cases',[(q['sample'],q['interval_length_mm'])for q in reports])
