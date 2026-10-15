"""Every original face x10 rays, preserved flags, long-double exact-hit/open-interval winding checks.
No repair. A grazing hit may be retained without treating it as a material exit only when
its barycentric location is on a triangle edge and full original-triangle winding agrees.
"""
from pathlib import Path
import tempfile,subprocess,csv,json,hashlib,gzip,shutil,numpy as np,trimesh
from original_rays import OriginalRays
R=Path(__file__).resolve().parent;m=trimesh.load(R/'model.stl',process=False);T=m.triangles;N=m.face_normals;ray=OriginalRays(m)
W=np.array([[1/3]*3,[.98,.01,.01],[.01,.98,.01],[.01,.01,.98],[.495,.495,.01],[.01,.495,.495],[.495,.01,.495],[.49,.49,.02],[.49,.02,.49],[.02,.49,.49]])
flags=[];short=[];count=0
with tempfile.TemporaryDirectory()as td:
 D=Path(td);np.asarray(T,dtype='<f8').tofile(D/'triangles.bin')
 for src,name in [('dense_original.cpp','dense'),('exact_original_rays.cpp','exact'),('original_winding.cpp','winding')]:subprocess.run(['g++','-O3','-std=c++17',str(R/src),'-o',str(D/name)],check=True,capture_output=True)
 subprocess.run([str(D/'dense'),str(D/'triangles.bin'),str(D/'dense.csv')],check=True,capture_output=True)
 with (D/'dense.csv').open()as f:
  for q in csv.DictReader(f):
   count+=1;i=int(q['face']);s=int(q['sample']);p=W[s]@T[i];n=N[i]
   assert abs(float(q['entry'])-1e-5)<1e-7 and float(q['first_solid'])>0
   if [int(q[k])for k in ['inside_control','outside_control','mid_control','after_exit_control']]!=[1,0,1,0]:flags.append(q)
   if float(q['first_solid'])<.8:
    h=ray.hits(p+n*1e-6,-n);assert len(h)>=2 and abs(h[0][0]-1e-6)<1e-7
    short.append(dict(original_triangle_index=i,sample_index=s,surface_point_mm=p.tolist(),original_outward_normal=n.tolist(),first_solid_chord_mm=h[1][0]-h[0][0],all_ray_intersections_mm_face=h))
 queries=np.array([[W[int(q['sample'])]@T[int(q['face'])]+N[int(q['face'])]*1e-5,-N[int(q['face'])]]for q in flags]);queries.tofile(D/'queries.bin');reviews=[]
 if flags:
  subprocess.run([str(D/'exact'),str(D/'triangles.bin'),str(D/'queries.bin'),str(D/'exact.csv')],check=True,capture_output=True)
  pts=[]
  for i,line in enumerate((D/'exact.csv').read_text().splitlines()):
   hits=[]
   for val in line.split(';')[1:]:
    t,face,u,v,nd=map(float,val.split(','));rec=dict(t_mm=t,face=int(face),barycentric=[1-u-v,u,v],normal_dot_ray=nd)
    if hits and abs(t-hits[-1]['t_mm'])<1e-10:hits[-1]['faces'].append(rec)
    else:hits.append(dict(t_mm=t,faces=[rec]))
   o,d=queries[i];test=[o,o+d*2e-5]
   for j,h in enumerate(hits):test.append(o+d*((h['t_mm']+hits[j+1]['t_mm'])/2 if j+1<len(hits)else h['t_mm']+.01))
   ids=list(range(len(pts),len(pts)+len(test)));pts.extend(test);reviews.append(dict(original_flag=flags[i],exact_hits=hits,point_indices=ids,points_mm=[p.tolist()for p in test]))
  np.array(pts).tofile(D/'points.bin');subprocess.run([str(D/'winding'),str(D/'triangles.bin'),str(D/'points.bin'),str(D/'winding.csv')],check=True,capture_output=True)
  wind=np.loadtxt(D/'winding.csv',delimiter=',')[:,1]
  for q in reviews:
   vals=wind[q['point_indices']];q['longdouble_winding']=vals.tolist();assert abs(vals[0])<1e-7 and abs(vals[1]-1)<1e-7 and abs(vals[2]-1)<1e-7
   state=[round(float(x))for x in vals[2:]];assert all(abs(v-s)<1e-7 for v,s in zip(vals[2:],state));grazes=[]
   for j in range(1,len(state)):
    if state[j]==state[j-1]:
     edge=all(min(h['barycentric'])<1e-10 for h in q['exact_hits'][j]['faces']);assert edge,('nontransition hit inside triangle',q)
     grazes.append(j)
   exits=[j for j in range(1,len(state))if state[j-1]==1 and state[j]==0];assert exits
   q['edge_grazing_nontransition_hit_indices']=grazes;q['true_first_material_exit_hit_index']=exits[0];q['true_first_solid_length_mm']=q['exact_hits'][exits[0]]['t_mm']-q['exact_hits'][0]['t_mm'];q['original_csv_first_solid_retained']=float(q['original_flag']['first_solid'])
 with (D/'dense.csv').open('rb')as f,gzip.GzipFile(filename=str(R/'dense-original.csv.gz'),mode='wb',mtime=0)as g:shutil.copyfileobj(f,g)
sha=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest();assert count==len(T)*10
checks=dict(all_original_faces_ten_samples=count==len(T)*10,all_original_surface_entry_hits_confirmed=True,all_flagged_source_outside_inside_winding_valid=True,all_flagged_open_intervals_classified=True,nontransition_hits_only_exact_triangle_edges=True)
report=dict(stl_sha256=sha,original_triangles=len(T),samples=count,original_fixed_direction_flags=len(flags),short_normal_count=len(short),checks=checks,passed=True,flag_reviews=reviews,limits='Finite original-face samples. Six original flags retained; long-double full-triangle winding resolves numerical parity and edge-tangent intersections. No global wall or printed-part claim. Earlier rejected geometry has distinct SHA and is not covered.')
(R/'dense-transitions.json').write_text(json.dumps(report,indent=2));(R/'dense-short-chords.json').write_text(json.dumps(dict(stl_sha256=sha,samples=count,under_0p8mm_count=len(short),short_chords=short,passed=False,limits='Strict short-normal intervals retained; supplementary backing does not waive them.')));print({k:v for k,v in report.items()if k!='flag_reviews'})
