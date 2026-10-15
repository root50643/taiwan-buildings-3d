from pathlib import Path
import hashlib,json,numpy as np,trimesh
O=Path(__file__).resolve().parent;T=trimesh.load(O/'model.stl',process=False).triangles;N=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]);N/=np.linalg.norm(N,axis=1)[:,None];v,ix=np.unique(T.reshape(-1,3),axis=0,return_inverse=True);m=trimesh.Trimesh(v,ix.reshape(-1,3),process=False);
def ray(o,d):
 o=np.array(o,float);d=np.array(d,float);e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];p=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,p);good=abs(det)>1e-10;inv=np.zeros(len(T));inv[good]=1/det[good];s=o-T[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);v=q@d*inv;t=np.einsum('ij,ij->i',e2,q)*inv;return sorted(set(round(float(x),7) for x in t[good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-7)]))

all_pairs=json.loads((O/'junction-pair-family.json').read_text())['samples'];fail=[r for r in all_pairs if r['bisector_first_solid']<.8 or not all(r['four_inside_controls'])];q={'samples':fail};rows=[];points=[]
for r in q['samples']:
 p=np.array([float(r[k]) for k in ['x','y','z']]);fs=[r['entry_face'],r['actual_exit_face'],r['bisector_exit_face']];ns=N[fs];d=-ns.sum(0);d/=np.linalg.norm(d);hs=ray(p+d*1e-5,d);points.extend([p+d*t for t in [1e-5,.001,.01,.02]]);rows.append({'face':fs[0],'sample':r['sample'],'point':p.tolist(),'three_actual_faces':fs,'normals':ns.tolist(),'signed_inward_dots':(ns@d).tolist(),'direction':d.tolist(),'first_exit':hs[0],'hits':hs[:8],'old_normal_first_solid':float(r['first_solid']),'old_normal_air_after':float(r['air_after']),'old_pair_first':r['bisector_first_solid']})
f=np.concatenate([m.contains(np.array(points[k:k+40])) for k in range(0,len(points),40)]).reshape(-1,4)
for r,ff in zip(rows,f):r['inside_controls']=ff.tolist()
out={'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest(),'count':len(rows),'min_first_exit':min(r['first_exit'] for r in rows),'controls_all_inside':bool(f.all()),'below_0p8':sum(r['first_exit']<.8 for r in rows),'rows':rows};(O/'junction-triple-controls.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k!='rows'})

good_pairs=[r for r in all_pairs if r not in fail]
checks={'all728_covered':len(rows)+len(good_pairs)==728,'two_face_roots_survive':all(r['bisector_first_solid']>=.8 and all(r['four_inside_controls']) for r in good_pairs),'three_face_roots_survive':all(r['first_exit']>=.8 and all(r['inside_controls']) and max(r['signed_inward_dots'])<0 for r in rows)}
summary={'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest(),'passed':all(checks.values()),'checks':checks,'family_samples':728,'two_face_count':len(good_pairs),'two_face_minimum_first_mm':min(r['bisector_first_solid'] for r in good_pairs),'three_face_count':len(rows),'three_face_minimum_first_mm':min(r['first_exit'] for r in rows),'three_face_maximum_signed_dot':max(max(r['signed_inward_dots']) for r in rows),'original_normal_and_air_retained':True,'limits':'Bounded classified family only. All original short normal/air and failed pair-direction rays remain in full CSV and pair report. A three-face inward root is not an all-direction minimum wall claim.14 representative roots do not stand for all728.'}
(O/'junction-family-review.json').write_text(json.dumps(summary,indent=2));assert summary['passed'],summary
