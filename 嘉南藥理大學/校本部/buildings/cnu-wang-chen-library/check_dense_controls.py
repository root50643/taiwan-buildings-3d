from pathlib import Path
import hashlib,json,numpy as np,trimesh
O=Path(__file__).resolve().parent;T=trimesh.load(O/'model.stl',process=False).triangles
def winding(p):
 a,b,c=(T-p).transpose(1,0,2);la=np.linalg.norm(a,axis=1);lb=np.linalg.norm(b,axis=1);lc=np.linalg.norm(c,axis=1);num=np.einsum('ij,ij->i',a,np.cross(b,c));den=la*lb*lc+np.einsum('ij,ij->i',a,b)*lc+np.einsum('ij,ij->i',b,c)*la+np.einsum('ij,ij->i',c,a)*lb;return float(np.sum(2*np.arctan2(num,den))/(4*np.pi))
a=json.loads((O/'dense-face-review.json').read_text())['control_fail_samples']
for r in a:
 p=np.array([float(r[k]) for k in ['x','y','z']]);n=np.array([float(r[k]) for k in ['nx','ny','nz']]);o=p+n*1e-5;hits=[float(x) for x in r['hits'].split(';') if x];r['solid_angle_control']=[{'point':q.tolist(),'winding':winding(q)} for q in [p-n*1e-5,o,o-n*(sum(hits[:2])/2),o-n*(hits[1]+1e-5)]];r['interval_windings']=[{'start':aa,'end':bb,'winding':winding(o-n*(aa+bb)/2)} for aa,bb in zip(hits,hits[1:])];print(r['face'],[x['winding'] for x in r['solid_angle_control']],r['interval_windings'])
report={'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest(),'samples':a,'checks':{'all_original_triangle_winding_controls_match_tangential_hits':all(np.allclose([x['winding'] for x in r['solid_angle_control']],[1,0,1,1],atol=1e-6) for r in a)}}
(O/'dense-control-solid-angle.json').write_text(json.dumps(report,indent=2))

assert all(np.allclose([x["winding"] for x in r["solid_angle_control"]],[1,0,1,1],atol=1e-6) for r in a), "Unexpected winding at parity anomaly"
