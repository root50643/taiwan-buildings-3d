from pathlib import Path
import gzip,json,numpy as np,trimesh,hashlib,time
from manifold3d import Manifold,Mesh64
R=Path(__file__).parent;Q=R;F=R/'model.stl';assert hashlib.sha256(F.read_bytes()).hexdigest()==json.loads((R/'evidence-index.json').read_text())['stl_sha256'];m=trimesh.load(F,process=False);v,iv=np.unique(m.vertices,axis=0,return_inverse=True);n=Manifold(Mesh64(v,np.asarray(iv[m.faces],np.uint64)));mm=n.to_mesh64();tt=np.asarray(mm.vert_properties)[:,:3][np.asarray(mm.tri_verts)]
def key(t):return tuple(sorted(tuple(x)for x in t))
lookup={key(t):i for i,t in enumerate(m.triangles)};assert len(tt)==len(m.faces)==len(lookup) and all(key(t)in lookup for t in tt);face_map=[lookup[key(t)]for t in tt]
# Exact vertex/triangle equality checked; reordered C++ acceleration does not alter any original triangle.
assert all(np.dot(np.cross(t[1]-t[0],t[2]-t[0]),m.face_normals[face_map[i]])>0 for i,t in enumerate(tt))
rows=json.loads(gzip.decompress((Q/'dense-original-casts.json.gz').read_bytes()));fixes={x['sample_index']:x for x in json.loads((Q/'unpaired-strict.json').read_text())};roots=[];flags=[];raydir=np.array([.3713906763541037,.5570860145311556,.7427813527082074]);raydir/=np.linalg.norm(raydir)
def cast(p,d):
 h=n.ray_cast(p.tolist(),(p+d*1000).tolist());return [{'distance_mm':x.distance*1000,'original_face_id':face_map[x.face_id],'point_mm':x.position,'normal':x.normal}for x in h if x.distance>1e-13]
def inside(p):return len(cast(p,raydir))%2==1
axes=np.vstack((np.eye(3),-np.eye(3)))
for i,s in enumerate(rows):
 o=np.array(s['ray_origin_mm']);d=np.array(s['direction']);surf=o+d*.0001;h=fixes[i]['strict_longdouble_hits']if i in fixes else s['all_hits'];span=h[1]['distance_mm']-h[0]['distance_mm'];ep=min(.0001,span*.2);p=o+d*(h[0]['distance_mm']+h[1]['distance_mm'])/2
 ff={'sample_index':i,'inside_surface':inside(surf+ep*d),'outside_surface':inside(surf-ep*d),'first_chord_midpoint_inside':inside(p),'after_first_exit_inside':inside(o+d*(h[1]['distance_mm']+.0001))};flags.append(ff)
 if span<.8:
  x,y,z=(p-[0,0,1.6])/1.5
  if y>8 and z>23 and -18<x<26:
   cx,cy=(5,5)if z<39.6 else (7,3.6)if z<44.5 else (10,3.8);root=np.array([cx*1.5-p[0],cy*1.5-p[1],0]);family='north_curved_backed_glass'
  elif y<-9 and -5<x<28:root=np.array([0,1,0]);family='south_curved_backed_glass_or_slot'
  elif x<-34:root=np.array([1,0,0]);family='west_tower_backed_detail'
  elif y<-11 and (abs(x+29)<2.1 or abs(x-31)<2.1):root=np.array([0,1,0]);family='south_stair_backed_detail'
  elif y>24:root=np.array([0,-1,0]);family='north_entry_colonnade'
  else:root=np.array([0,0,-1]);family='other_solid_corner_or_backed_window'
  root=root/np.linalg.norm(root);spans=[]
  for di in np.vstack((root,axes)):
   hits=cast(p,di);spans.append({'direction':di.tolist(),'first_exit':hits[0]if hits else None})
  roots.append({'dense_sample_index':i,'original_face_id':s['sample_face_id'],'family':family,'original_surface_point_mm':surf.tolist(),'first_normal_chord_mm':span,'inside_first_chord_origin_mm':p.tolist(),'midpoint_inside':ff['first_chord_midpoint_inside'],'backing_direction_then_six_axes':spans,'longest_connected_root_span_mm':max((h['first_exit']['distance_mm']if h['first_exit']else 0)for h in spans)})
 if (i+1)%10000==0:
  print(i+1,len(roots),flush=True)
report={'stl_sha256':hashlib.sha256(F.read_bytes()).hexdigest(),'method':'Read-only accelerated ray casts on exact same original float32 triangles. Exact np.unique indexing only; every imported triangle matched back to original face ID with coordinates and orientation unchanged. No mesh repair, remeshing or boolean geometry operation. Generic-direction ray parity is independent of original trimesh contains. Root span to FIRST exit only, not a minimum-wall claim.','exact_original_geometry_and_winding_equal':True,'sample_count':len(flags),'short_root_count':len(roots),'flag_counts':{k:sum(x[k]for x in flags)for k in ['inside_surface','outside_surface','first_chord_midpoint_inside','after_first_exit_inside']},'root_below_08':sum(x['longest_connected_root_span_mm']<.8 for x in roots),'samples':flags,'short_roots':roots};(Q/'dense-independent-root-evidence.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items()if k not in ['samples','short_roots']})
