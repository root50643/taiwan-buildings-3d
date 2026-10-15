import csv,gzip,json,numpy as np,trimesh,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;T=trimesh.load(O/'model.stl',process=False).triangles;rows=list(csv.DictReader(gzip.open(O/'dense-samples.csv.gz','rt')));e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0]
def ray(o,d):
 p=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,p);good=abs(det)>1e-13;iv=np.zeros(len(T));iv[good]=1/det[good];s=o-T[:,0];u=np.einsum('ij,ij->i',s,p)*iv;q=np.cross(s,e1);v=q@d*iv;t=np.einsum('ij,ij->i',e2,q)*iv;h=np.sort(t[good&(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)&(t>1e-9)]);return h[np.r_[True,np.diff(h)>1e-7]] if len(h) else h
ctrl=['inside_control','outside_control','mid_control','after_exit_control']
valid=[r for r in rows if [r[k] for k in ctrl]==['1','0','1','0'] and abs(float(r['entry'])-1e-5)<1e-6];short=sorted([r for r in valid if float(r['first_solid'])<.8],key=lambda r:float(r['first_solid']));fails=[r for r in rows if [r[k] for k in ctrl]!=['1','0','1','0']];rng=np.random.default_rng(13579);choices=short[:15]+[r for r in short if float(r['air_after'])>.01 and float(r['air_after'])<10][:15]+[valid[i] for i in rng.choice(len(valid),25,replace=False)];proof=[]
for r in choices:
 p=np.array([float(r[k]) for k in ['x','y','z']]);n=np.array([float(r[k]) for k in ['nx','ny','nz']]);h=ray(p+n*1e-5,-n);old=np.array([float(x) for x in r['hits'].split(';') if x]);r=dict(r);r['numpy_hits']=h.tolist();r['numpy_matches']=len(h)==len(old) and bool(np.allclose(h,old,atol=2e-7,rtol=1e-8));r['triangle_vertices']=T[int(r['face'])].tolist();r['triangle_area_mm2']=float(np.linalg.norm(np.cross(e1[int(r['face'])],e2[int(r['face'])]))/2);proof.append(r)
regions={
 'central_curved_glass':lambda x,y,z:abs(x)<22 and -35<y<-3 and 43<z<76,
 'north_upper_grid_screen':lambda x,y,z:y>20 and 45<z<63,
 'entry_canopy':lambda x,y,z:abs(x)<24 and -65<y<-51 and 15<z<23,
 'south_terrace_grid':lambda x,y,z:y<-32 and 43<z<47,
}
summary={}
for label,sel in regions.items():
 group=[r for r in valid if sel(*[float(r[k]) for k in ['x','y','z']])];ss=sorted(group,key=lambda r:float(r['first_solid']));summary[label]={'aabb_only_not_semantic_assignment':True,'samples':len(group),'below_0p8':sum(float(r['first_solid'])<.8 for r in group),'minimum':ss[:8]}
out={'stl_sha256':'353a5ce7fcd15a798f8bbf932e73d67b95ef856c60623cc3d7831f46dd609897','original_faces':len(T),'samples':len(rows),'samples_per_original_triangle':7,'barycentric_samples':[[1/3]*3,[.98,.01,.01],[.01,.98,.01],[.01,.01,.98],[.495,.495,.01],[.01,.495,.495],[.495,.01,.495]],'method':'Original-facet cross normals; start 1e-5mm outside. Full positive Moller-Trumbore hits via independent C++ BVH, no skipped first segment, deduplicate 1e-7mm. Four parity controls use independent oblique rays: inward close point, outward origin, first-solid midpoint, immediate post-exit. Short first intervals retained even when a later wall is thick. Selected all-triangle numpy verification.','valid_control_samples':len(valid),'short_below_0p8_valid_samples':len(short),'short_unique_faces':len({r['face'] for r in short}),'minimum_valid_short':short[:30],'control_fail_count':len(fails),'control_fail_samples':fails,'numpy_crosscheck_all_match':all(r['numpy_matches'] for r in proof),'numpy_crosschecks':proof,'region_summary':summary,'per_sample':{str(i):{'n':sum(r['sample']==str(i) for r in rows),'short_valid':sum(r['sample']==str(i) for r in short)} for i in range(7)},'limitations':'Finite original triangle samples, not a global minimum-thickness proof. Normal short chords at lips/corners and grooves require geometric classification; a count below 0.8 is not alone proof of an unsupported wall. Control failures and near numerical-resolution segments are reported, not counted as safe.'}
(O/'dense-face-review.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:out[k] for k in ['samples','valid_control_samples','short_below_0p8_valid_samples','short_unique_faces','control_fail_count','numpy_crosscheck_all_match','per_sample']},indent=2))

assert out["samples"]==len(T)*7 and out["numpy_crosscheck_all_match"], "Dense sampling completeness/crosscheck failed"
