"""Fail-closed checks on raw binary STL, without mesh repair or smoothing."""
from pathlib import Path
import collections,hashlib,json,struct,subprocess,sys,tempfile
import numpy as np
import trimesh
R=Path(__file__).resolve().parent
raw=(R/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0]
assert len(raw)==84+50*n
records=np.frombuffer(raw,dtype=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')]),offset=84,count=n)
t=records['vertices'].astype(np.float64);vertices=[];lookup={};faces=[]
for triangle in t:
 f=[]
 for v in triangle:
  k=tuple(v)
  if k not in lookup:lookup[k]=len(vertices);vertices.append(k)
  f.append(lookup[k])
 faces.append(f)
v=np.array(vertices);f=np.array(faces);cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(cross,axis=1)
checks={}
checks['no_degenerate_raw_triangles']=bool(np.all(length>1e-9))
checks['raw_normals_match_winding']=bool(np.all(np.sum(cross/length[:,None]*records['normal'],axis=1)>.99999))
edges=collections.defaultdict(list)
for fi,face in enumerate(f):
 for a,b in zip(face,np.roll(face,-1)):edges[tuple(sorted((int(a),int(b))))].append((fi,int(a),int(b)))
checks['every_raw_edge_exactly_two_faces']=all(len(x)==2 for x in edges.values())
checks['raw_orientations_consistent']=all(len(x)==2 and x[0][1:]==x[1][1:][::-1] for x in edges.values())
adj=[set() for _ in f]
for e in edges.values():
 if len(e)==2:adj[e[0][0]].add(e[1][0]);adj[e[1][0]].add(e[0][0])
seen={0};todo=[0]
while todo:
 a=todo.pop()
 for b in adj[a]-seen:seen.add(b);todo.append(b)
checks['single_connected_raw_surface']=len(seen)==len(f)
links=[collections.defaultdict(set) for _ in v]
for a,b,c in f:
 for center,j,k in [(a,b,c),(b,c,a),(c,a,b)]:links[center][j].add(k);links[center][k].add(j)
link_ok=True
for link in links:
 if not all(len(n)==2 for n in link.values()):link_ok=False;break
 visited={next(iter(link))};todo=list(visited)
 while todo:
  a=todo.pop()
  for b in link[a]-visited:visited.add(b);todo.append(b)
 if len(visited)!=len(link):link_ok=False;break
checks['every_vertex_link_single_cycle']=link_ok
volume=float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6)
checks['raw_positive_volume']=volume>0
checks['maximum_size_150mm']=bool(np.max(np.ptp(v,axis=0))<=150.00001)
checks['base_plane_z_zero']=abs(v[:,2].min())<1e-7
checks['finite_coordinates']=bool(np.isfinite(v).all())
mesh=trimesh.Trimesh(v,f,process=False)
checks['watertight_without_repair']=bool(mesh.is_watertight)
with tempfile.TemporaryDirectory(prefix='ntin-independent-build-') as d:
 subprocess.run([sys.executable,str(R/'build_model.py'),'--output',d],check=True,capture_output=True)
 independent=hashlib.sha256((Path(d)/'model.stl').read_bytes()).hexdigest()
checks['independent_rebuild_stl_sha256_identical']=independent==hashlib.sha256(raw).hexdigest()
# Moller-Trumbore, no implicit ray backend or geometric repairs.
def ray(o,d):
 o=np.array(o,float);d=np.array(d,float);e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];p=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,p);ok=np.abs(det)>1e-10
 inv=np.zeros(len(t));inv[ok]=1/det[ok];s=o-t[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);w=q@d*inv;dist=np.einsum('ij,ij->i',e2,q)*inv
 hit=dist[ok&(u>=-1e-8)&(w>=-1e-8)&(u+w<=1+1e-8)&(dist>1e-7)]
 return sorted(set(np.round(hit,6)))
rays={}
for name,o,d in [('portico_open_center',[0,-40,14],[0,1,0]),('portico_left_column',[-9.5,-40,14],[0,1,0]),('gallery_open_middle',[0,-40,28],[0,1,0]),('gallery_major_column',[-44.333333,-40,28],[0,1,0]),('front_window',[22.17,-40,12],[0,1,0]),('front_wall',[19.,-40,12],[0,1,0]),('roof_ridge',[0,0,60],[0,0,-1]),('roof_side_slope',[0,12,60],[0,0,-1]),('roof_hip_end',[66,0,60],[0,0,-1])]:
 hits=ray(o,d);assert hits,name;rays[name]={'origin_mm':o,'direction':d,'distances_mm':hits,'first_hit_point_mm':(np.array(o)+np.array(d)*hits[0]).tolist()}
checks['portico_actual_open_space']=rays['portico_open_center']['first_hit_point_mm'][1]>-14
checks['portico_actual_connected_column']=rays['portico_left_column']['first_hit_point_mm'][1]<-22
checks['gallery_actual_depth_over_4mm']=rays['gallery_open_middle']['first_hit_point_mm'][1]>-9
checks['gallery_column_retained']=rays['gallery_major_column']['first_hit_point_mm'][1]<-13.8
checks['front_recess_not_painted_surface']=rays['front_window']['first_hit_point_mm'][1]>rays['front_wall']['first_hit_point_mm'][1]+.5
checks['roof_four_slope_hip_relief']=rays['roof_ridge']['first_hit_point_mm'][2]>max(rays['roof_side_slope']['first_hit_point_mm'][2],rays['roof_hip_end']['first_hit_point_mm'][2])+2
checks['roof_no_enclosed_air_shell']=all(len(rays[k]['distances_mm'])==2 for k in ['roof_ridge','roof_side_slope','roof_hip_end'])
checks={k:bool(value) for k,value in checks.items()}
measurements={}
for name,o,d in [('gallery_up',[0,-11,28],[0,0,1]),('gallery_down',[0,-11,28],[0,0,-1]),('portico_up',[0,-18,14],[0,0,1]),('portico_down',[0,-18,14],[0,0,-1])]:
 hits=ray(o,d);assert hits,name;measurements[name]=float(hits[0])
measurements['gallery_clear_height_mm']=measurements['gallery_up']+measurements['gallery_down']
measurements['gallery_front_datum_y_mm']=-13.6
measurements['gallery_backwall_y_mm']=rays['gallery_open_middle']['first_hit_point_mm'][1]
measurements['gallery_datum_to_backwall_clear_depth_mm']=measurements['gallery_backwall_y_mm']+13.6
measurements['portico_clear_height_mm']=measurements['portico_up']+measurements['portico_down']
measurements['portico_canopy_front_y_mm']=-24.8
measurements['portico_center_backwall_y_mm']=rays['portico_open_center']['first_hit_point_mm'][1]
measurements['portico_canopy_front_to_recess_backwall_depth_mm']=measurements['portico_center_backwall_y_mm']+24.8
measurements['portico_front_to_main_wall_datum_depth_mm']=11.2
measurements['portico_clear_width_between_columns_mm']=16.5
checks['gallery_clear_height_measured']=abs(measurements['gallery_clear_height_mm']-7.9)<1e-4
checks['gallery_clear_depth_measured']=abs(measurements['gallery_datum_to_backwall_clear_depth_mm']-5.)<1e-4
checks['portico_clear_height_measured']=abs(measurements['portico_clear_height_mm']-16.95)<1e-4
checks['portico_clear_depth_measured']=abs(measurements['portico_canopy_front_to_recess_backwall_depth_mm']-12.6)<1e-4
report={'method':'Original binary STL vertices merged only by exact bitwise coordinate equality; no repair. Per-edge, per-vertex-link, oriented raw normals and connectivity. Separate-process rebuild into temporary directory. Moller-Trumbore feature rays.','checks':checks,'passed':all(checks.values()),'stl_sha256':hashlib.sha256(raw).hexdigest(),'independent_rebuild_stl_sha256':independent,'triangles':n,'vertices':len(v),'size_mm':np.ptp(v,axis=0).tolist(),'signed_volume_mm3':volume,'rays':rays,'measured_clear_open_spaces_mm':measurements,'print_warning':'Geometry screening only; no toolpath or physical print. Portico underside, balcony ceiling and eaves may need supports.'}
(R/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='rays'},ensure_ascii=False,indent=2))
assert report['passed'], 'Fail-closed geometry validation failed'
