"""Source-bounded corner witnesses for this fresh NYCU mesh, not a blanket exemption.
Every strict short normal chord remains retained. Only four declared vertical
convex edges qualify, within .35mm, with an actual adjacent-original-face
bisector and connected coplanar original surface patch to the sampled face.
"""
from pathlib import Path
import json,gzip,hashlib,collections
import numpy as np,trimesh
from original_rays import OriginalRays
from dense_report import load_dense_report
R=Path(__file__).resolve().parent;P=json.loads((R/'parameters.json').read_text())
m=trimesh.load(R/'model.stl',process=False);T=m.triangles;N=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]);N/=np.linalg.norm(N,axis=1)[:,None]
V,iv=np.unique(T.reshape(-1,3),axis=0,return_inverse=True);F=iv.reshape(-1,3);ed=collections.defaultdict(list);adj=collections.defaultdict(set)
for fi,f in enumerate(F):
 for i in range(3):ed[tuple(sorted((int(f[i]),int(f[(i+1)%3]))))].append(fi)
for e,fs in ed.items():
 assert len(fs)==2
 adj[fs[0]].add(fs[1]);adj[fs[1]].add(fs[0])
S=P['scale_mm_per_m'];O=np.array(P['xy_origin_m']);B=P['base_mm'][2]-.05
# These are OSM outer-corner coordinates, not fitted from the observed ray failures.
declared=[('north-west-outer',[-37.7788516,25.893032],35.9),('south-west-outer',[-58.44705697,-12.478972],35.9),('north-east-roof-corner',[26.4896656,19.481],35.9),('lower-terminal-tip',[36.2527396,3.027904],24.0)]
corners=[]
for name,xy,h in declared:
 p=(np.array(xy)-O)*S;ee=[]
 for e,fs in ed.items():
  v=V[list(e)]
  if np.linalg.norm(v[0,:2]-p)<2e-5 and np.linalg.norm(v[1,:2]-p)<2e-5 and abs(v[1,2]-v[0,2])>1e-5 and float(N[fs[0]]@N[fs[1]])<.95:
   ee.append((e,fs))
 assert ee, name
 corners.append({'name':name,'xy_m':xy,'xy_mm':p,'height_m':h,'edges':ee})
ray=OriginalRays(m);probe=np.array([.319,.557,.766]);probe/=np.linalg.norm(probe)
def inside(p):return bool(len(ray.hits(p,probe))%2)
patch_cache={}
def patch(fi):
 if fi in patch_cache:return patch_cache[fi]
 seen=set();stack=[fi];n=N[fi];a=T[fi,0]
 while stack:
  x=stack.pop()
  if x in seen:continue
  if float(n@N[x])<1-1e-6 or np.max(np.abs((T[x]-a)@n))>2e-5:continue
  seen.add(x);stack.extend(adj[x]-seen)
 patch_cache[fi]=seen;return seen

def distance(p,a,b):
 u=b-a;t=np.clip((p-a)@u/(u@u),0,1);q=a+t*u;return float(np.linalg.norm(p-q)),q
r=load_dense_report(R);assert r['stl_sha256']==hashlib.sha256((R/'model.stl').read_bytes()).hexdigest()
rows=[];unknown=[]
for q in r['short_chords']:
 fi=q['original_triangle_index'];p=np.array(q['surface_point_mm']);n=np.array(q['original_outward_normal']);candidates=[]
 for c in corners:
  if not (B-1e-5<=p[2]<=B+c['height_m']*S+1e-5 and np.linalg.norm(p[:2]-c['xy_mm'])<=.35):continue
  for e,fs in c['edges']:
   dd,near=distance(p,*V[list(e)])
   if dd<=.35 and any(fi in patch(f) for f in fs):candidates.append((dd,c,e,fs,near))
 if not candidates:unknown.append(q);continue
 dd,c,e,fs,near=min(candidates,key=lambda x:x[0]);pp=next(patch(f) for f in fs if fi in patch(f));d=-(N[fs[0]]+N[fs[1]]);d/=np.linalg.norm(d)
 h=ray.hits(p-d*1e-6,d);nh=q['all_ray_intersections_mm_face'];no=p+n*1e-6
 assert len(nh)>=2 and len(h)>=2
 first=h[1][0]-h[0][0];normal_first=nh[1][0]-nh[0][0]
 controls=[]
 def control(role,pt,expect):
  v=inside(pt);controls.append({'role':role,'point_mm':np.array(pt).tolist(),'expected_material':expect,'actual_material':v,'passed':v==expect})
 control('normal-before-entry',no,False)
 control('normal-first-mid',no-n*((nh[0][0]+nh[1][0])/2),True)
 gap=nh[2][0]-nh[1][0] if len(nh)>2 else None
 control('normal-following-air',no-n*(nh[1][0]+min(.001,gap/4 if gap else .001)),False)
 for t in [1e-5,.001,.01,.1,.4,.8]:control('root-interior-'+str(t),p+d*t,True)
 ro=p-d*1e-6;control('root-before-entry',ro,False);control('root-first-mid',ro+d*((h[0][0]+h[1][0])/2),True)
 rootgap=h[2][0]-h[1][0] if len(h)>2 else None
 control('root-following-air',ro+d*(h[1][0]+min(.001,rootgap/4 if rootgap else .001)),False)
 checks={'declared_edge_tube':dd<=.35,'original_face_in_connected_coplanar_edge_patch':any(f in pp for f in fs),'edge_has_two_original_faces':len(fs)==2,'noncoplanar_original_dihedral':float(N[fs[0]]@N[fs[1]])<.95,'root_is_inward_to_both_faces':all(float(d@N[f])<-.05 for f in fs),'root_enters_sample_face':float(d@n)<-.05,'root_first_entry_at_offset':abs(h[0][0]-1e-6)<2e-5,'root_first_continuous_interval_ge_0p8':first>=.8,'root_first_exit_orientation':float(N[h[1][1]]@d)>1e-7,'all_direct_material_air_controls':all(x['passed'] for x in controls)}
 rows.append({'original_triangle_index':fi,'sample_index':q['sample_index'],'surface_point_mm':p.tolist(),'original_outward_normal':n.tolist(),'source_corner':c['name'],'source_corner_m':c['xy_m'],'declared_tube_radius_mm':.35,'distance_to_original_edge_mm':dd,'closest_original_edge_point_mm':near.tolist(),'actual_edge_vertex_ids':list(e),'actual_edge_endpoints_mm':V[list(e)].tolist(),'adjacent_original_face_ids':fs,'adjacent_original_face_normals':N[fs].tolist(),'connected_coplanar_patch_face_ids':sorted(pp),'all_original_normal_hits_mm_face':nh,'original_first_material_mm':normal_first,'original_following_air_mm':gap,'root_rule':'negative normalized sum of the two actual original adjacent outward face normals','fixed_root_direction':d.tolist(),'all_root_hits_mm_face':h,'continuous_root_first_material_mm':first,'root_following_air_mm':rootgap,'controls':controls,'checks':checks,'passed':all(checks.values())})
checks={'all_original_short_rows_retained':len(rows)+len(unknown)==len(r['short_chords']),'all_short_rows_have_specific_original_edge_witness':not unknown,'all_witness_checks_pass':all(x['passed'] for x in rows)}
out={'stl_sha256':r['stl_sha256'],'passed':all(checks.values()),'checks':checks,'original_short_count':len(r['short_chords']),'witness_count':len(rows),'unknown':unknown,'source_corner_counts':dict(collections.Counter(x['source_corner']for x in rows)),'maximum_edge_distance_mm':max((x['distance_to_original_edge_mm']for x in rows),default=None),'minimum_continuous_root_first_material_mm':min((x['continuous_root_first_material_mm']for x in rows),default=None),'failed_witnesses':[{'face':x['original_triangle_index'],'sample':x['sample_index'],'checks':x['checks']}for x in rows if not x['passed']],'scope':'Finite source-bounded convex-edge evidence only. Does not erase original short normal diagnostics or establish global minimum wall thickness. Full interval screen and independent review required.'}
with (R/'corner-root-witnesses.json.gz').open('wb')as f,gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0)as g:g.write(json.dumps(rows,separators=(',',':')).encode())
out['witness_file']='corner-root-witnesses.json.gz';out['witness_sha256']=hashlib.sha256((R/out['witness_file']).read_bytes()).hexdigest();(R/'corner-roots.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));assert out['passed']
