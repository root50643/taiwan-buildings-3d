from pathlib import Path
import gzip,json,numpy as np,trimesh,hashlib
R=Path(__file__).parent;Q=R;F=R/'model.stl';m=trimesh.load(F,process=False);v,iv=np.unique(m.vertices,axis=0,return_inverse=True);f=iv[m.faces];edges={}
for i,face in enumerate(f):
 for a,b in zip(face,np.roll(face,-1)):edges.setdefault(tuple(sorted((int(a),int(b)))),[]).append(i)
crease=[]
for (a,b),fs in edges.items():
 assert len(fs)==2
 angle=float(np.arccos(np.clip(m.face_normals[fs[0]]@m.face_normals[fs[1]],-1,1)))
 if angle>np.deg2rad(10):crease.append((a,b,fs,angle))
a=np.array([v[e[0]]for e in crease]);b=np.array([v[e[1]]for e in crease]);vec=b-a;length=np.einsum('ij,ij->i',vec,vec)
d=json.loads(gzip.decompress((Q/'dense-independent-root-evidence.json.gz').read_bytes()));bad={r['sample_index']for r in json.loads((Q/'adaptive-origin-evidence.json').read_text())['samples']};out=[]
for r in d['short_roots']:
 if r['dense_sample_index']in bad or r['first_normal_chord_mm']>=.05:continue
 p=np.array(r['original_surface_point_mm']);t=np.clip(np.einsum('ij,ij->i',p-a,vec)/length,0,1);near=a+t[:,None]*vec;dist=np.linalg.norm(p-near,axis=1);j=int(np.argmin(dist));ed=crease[j]
 out.append({'sample_index':r['dense_sample_index'],'original_face_id':r['original_face_id'],'surface_point_mm':p.tolist(),'first_material_chord_mm':r['first_normal_chord_mm'],'nearest_original_crease_distance_mm':float(dist[j]),'crease_endpoints_mm':[a[j].tolist(),b[j].tolist()],'crease_original_face_ids':ed[2],'crease_dihedral_degrees':float(np.rad2deg(ed[3])),'continuous_backing_root_mm':r['longest_connected_root_span_mm']})
report={'stl_sha256':hashlib.sha256(F.read_bytes()).hexdigest(),'method':'Original shared-edge crease >10deg; exact triangle indices, no snapping. Every independently material-verified dense normal span below0.05mm retained; six invalid fixed-origin air intervals separately corrected, never treated as solid. Crease proximity is localization, not blanket approval.','samples':out,'sample_count':len(out),'max_crease_distance_mm':max(x['nearest_original_crease_distance_mm']for x in out)};(Q/'short-convex-edge-localization.json').write_text(json.dumps(report,indent=2));print(len(out),report['max_crease_distance_mm'])
