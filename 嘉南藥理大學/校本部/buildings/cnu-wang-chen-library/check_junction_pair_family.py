from pathlib import Path
import numpy as np,json,trimesh,gzip,csv,hashlib
O=Path(__file__).resolve().parent;T=trimesh.load(O/'model.stl',process=False).triangles;v,ix=np.unique(T.reshape(-1,3),axis=0,return_inverse=True);m=trimesh.Trimesh(v,ix.reshape(-1,3),process=False);N=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]);N/=np.linalg.norm(N,axis=1)[:,None];e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0]
def hits(o,d):
 pp=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,pp);good=abs(det)>1e-10;inv=np.zeros(len(T));inv[good]=1/det[good];s=o-T[:,0];u=np.einsum('ij,ij->i',s,pp)*inv;q=np.cross(s,e1);vv=q@d*inv;tt=np.einsum('ij,ij->i',e2,q)*inv;ids=np.where(good&(u>=-1e-8)&(vv>=-1e-8)&(u+vv<=1+1e-8)&(tt>1e-7))[0];return sorted([(float(tt[i]),int(i)) for i in ids])
tops=[44.688,49.728,54.768,59.808,64.848,69.888,73.848];selected=[]
for v in csv.DictReader(gzip.open(O/'dense-samples.csv.gz','rt')):
 x,y,z,nz,w,ez=[float(v[k]) for k in ['x','y','z','nz','first_solid','exit_z']]
 if abs(x)<22 and -35<y<-3 and 43<z<76 and .1<nz<.6 and w<.8 and min(abs(ez-t) for t in tops)<1e-4:selected.append(v)
assert len(selected)==728,'Family membership changed: re-review required'
(O/'junction-family-selected.json').write_text(json.dumps({'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest(),'definition':{'x_abs_lt':22,'y':[-35,-3],'z':[43,76],'original_normal_z':[.1,.6],'short_first_mm_lt':.8,'exit_on_ring_top_z':tops,'exit_z_tolerance':1e-4},'count':len(selected),'samples':selected},indent=2))
rows=[];controls=[]
for r in selected:
 p=np.array([float(r[k]) for k in ['x','y','z']]);i=int(r['face']);n=N[i];hh=hits(p+n*1e-5,-n);ex=min(hh,key=lambda t:abs(t[0]-(float(r['entry'])+float(r['first_solid']))));j=ex[1];nn=N[j];bis=-n-nn;bis/=np.linalg.norm(bis);rr=hits(p+bis*1e-5,bis);controls.extend([p+bis*z for z in [1e-5,.001,.01,.02]]);common=set(ix.reshape(-1,3)[i])&set(ix.reshape(-1,3)[j]);dot=float(n@nn);line_d=np.cross(n,nn);dist=abs(float(nn@(p-T[j,0])))/np.linalg.norm(line_d) if np.linalg.norm(line_d)>1e-8 else None
 rows.append({**r,'entry_face':i,'actual_exit_face':j,'exit_normal':nn.tolist(),'entry_exit_shared_vertices':len(common),'plane_intersection_distance':dist,'actual_pair_bisector':bis.tolist(),'bisector_first_solid':rr[0][0],'bisector_exit_face':rr[0][1],'normal_pair_dot':dot,'bisector_hits':rr[:8]})
(O/'junction-pair-rays-checkpoint.json').write_text(json.dumps(rows,indent=2));flags=np.concatenate([m.contains(np.array(controls[k:k+40])) for k in range(0,len(controls),40)]).reshape(-1,4)
for r,f in zip(rows,flags):r['four_inside_controls']=f.tolist()
out={'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest(),'count':len(rows),'min_bisector_first_solid':min(r['bisector_first_solid'] for r in rows),'all_inside':bool(flags.all()),'failed_control_count':int((~flags).sum()),'samples':rows};(O/'junction-pair-family.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k!='samples'})
