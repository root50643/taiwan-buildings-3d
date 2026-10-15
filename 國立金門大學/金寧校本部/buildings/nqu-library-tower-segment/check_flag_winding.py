"""All fixed-parity flagged samples: original-triangle long-double solid angle.
Boundary values remain unresolved unless original surface/interval proof is supplied.
"""
from pathlib import Path
import json,tempfile,subprocess,hashlib
import numpy as np,trimesh
R=Path(__file__).resolve().parent;m=trimesh.load(R/'model.stl',process=False);T=m.triangles;N=m.face_normals
W=np.array([[1/3]*3,[.98,.01,.01],[.01,.98,.01],[.01,.01,.98],[.495,.495,.01],[.01,.495,.495],[.495,.01,.495],[.49,.49,.02],[.49,.02,.49],[.02,.49,.49]])
a=json.loads((R/'dense-short-chords.json').read_text());points=[];rows=[]
for q in a['flags']:
 i=int(q['face']);j=int(q['sample']);p=W[j]@T[i];n=N[i];h=float(q['first_solid']);air=float(q['air_after']);air=air if air>0 else 1
 ps=[p+n*1e-5,p-n*1e-5,p-n*h/2,p-n*(h+min(1e-5,air/4))]
 rows.append(dict(face=i,sample=j,raw=q,indices=list(range(len(points),len(points)+4)),expected=[0,1,1,0]));points.extend(ps)
with tempfile.TemporaryDirectory() as td:
 D=Path(td);np.asarray(T,dtype='<f8').tofile(D/'tri');np.asarray(points,dtype='<f8').tofile(D/'pts');subprocess.run(['g++','-O3','-std=c++17',str(R/'original_winding.cpp'),'-o',str(D/'wind')],check=True);subprocess.run([str(D/'wind'),str(D/'tri'),str(D/'pts'),str(D/'w.csv')],check=True);vals=np.loadtxt(D/'w.csv',delimiter=',')[:,1]
for q in rows:
 q['winding']=[float(vals[i]) for i in q['indices']];q['points_mm']=[points[i].tolist() for i in q['indices']];q['expected_codes_confirmed']=all(abs(v-e)<1e-7 for v,e in zip(q['winding'],q['expected']))
report=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),flagged_samples=len(rows),point_count=len(points),confirmed=sum(q['expected_codes_confirmed'] for q in rows),unresolved=[q for q in rows if not q['expected_codes_confirmed']],rows=rows)
(R/'flag-winding.json').write_text(json.dumps(report,indent=2));print('flags',len(rows),'confirmed',report['confirmed']);print([(q['face'],q['sample'],q['winding']) for q in report['unresolved']]);raise SystemExit(0 if not report['unresolved'] else 1)
