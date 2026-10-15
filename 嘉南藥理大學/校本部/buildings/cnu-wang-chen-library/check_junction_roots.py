from pathlib import Path
import hashlib,json,numpy as np,trimesh
O=Path(__file__).resolve().parent;T=trimesh.load(O/'model.stl',process=False).triangles;v,ix=np.unique(T.reshape(-1,3),axis=0,return_inverse=True);m=trimesh.Trimesh(v,ix.reshape(-1,3),process=False);mask=m.face_adjacency_angles>np.radians(12);edges=v[m.face_adjacency_edges[mask]];faces=m.face_adjacency[mask];a=edges[:,0];e=edges[:,1]-a;ee=(e*e).sum(1);
def ray(o,d):
 o=np.array(o,float);d=np.array(d,float);e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];p=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,p);good=abs(det)>1e-10;inv=np.zeros(len(T));inv[good]=1/det[good];s=o-T[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);v=q@d*inv;t=np.einsum('ij,ij->i',e2,q)*inv;return sorted(set(round(float(x),7) for x in t[good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-7)]))

d=json.loads((O/'junction-probe-seeds.json').read_text());rows=[];controls=[]
for r in d['samples']:
 if r.get('first_solid',999)>=.8:continue
 p=np.array(r['surface_point']);t=np.clip(((p-a)*e).sum(1)/ee,0,1);dist=np.linalg.norm(p-a-e*t[:,None],axis=1);k=int(dist.argmin());nn=np.cross(T[faces[k],1]-T[faces[k],0],T[faces[k],2]-T[faces[k],0]);nn/=np.linalg.norm(nn,axis=1)[:,None];bis=-nn.sum(0);bis/=np.linalg.norm(bis);hs=ray(p+bis*1e-5,bis);controls.extend([p+bis*z for z in [1e-5,.001,.01,.02]]);rows.append({**r,'true_edge_distance':float(dist[k]),'true_edge':edges[k].tolist(),'adjacent_faces':faces[k].tolist(),'true_bisector':bis.tolist(),'direct_bisector_first_exit':hs[0],'all_bisector_hits':hs})
flags=m.contains(np.array(controls));out={'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest(),'count':len(rows),'max_edge_distance':max(r['true_edge_distance'] for r in rows),'minimum_direct_bisector_root':min(r['direct_bisector_first_exit'] for r in rows),'all_inward_controls_inside':bool(flags.all()),'samples':rows};(O/'junction-root-check.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k!='samples'})

assert len(rows)==14 and flags.all() and out["max_edge_distance"]<.05 and out["minimum_direct_bisector_root"]>.8, "Local junction-root check failed"
