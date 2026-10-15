from pathlib import Path
import gzip
import numpy as np,json,trimesh,hashlib
R=Path(__file__).resolve().parent;m=trimesh.load(R/'model.stl',process=False);d=json.loads(gzip.decompress((R/'original-face-normal-evidence.json.gz').read_bytes()));rows=[]
for s in d['samples']:
 if s['first_solid_normal_chord_mm']>=.8:continue
 h=s['all_hits'];o=np.array(s['outside_ray_origin_mm']);v=np.array(s['direction']);p=o+v*(h[0]['distance_mm']+h[1]['distance_mm'])/2
 x,y,z=(p-[0,0,1.6])/1.5
 if y>8 and z>23 and -18<x<26:
  cx,cy=(5,5)if z<39.6 else (7,3.6)if z<44.5 else (10,3.8);root=np.array([cx*1.5-p[0],cy*1.5-p[1],0]);family='north_curved_backed_glass'
 elif y<-9 and -5<x<28:root=np.array([0,1,0]);family='south_curved_backed_glass_or_slot'
 elif x<-34:root=np.array([1,0,0]);family='west_tower_backed_detail'
 elif y<-11 and (abs(x+29)<2.1 or abs(x-31)<2.1):root=np.array([0,1,0]);family='south_stair_backed_detail'
 elif y>24:root=np.array([0,-1,0]);family='north_entry_colonnade'
 else:root=np.array([0,0,-1]);family='other_solid_corner_or_backed_window'
 root=root.astype(float);root/=np.linalg.norm(root);dirs=np.array([root,*np.eye(3),*-np.eye(3)]);hit,ri,fi=m.ray.intersects_location(np.repeat(p[None,:],7,axis=0),dirs,multiple_hits=True);ds=np.einsum('ij,ij->i',hit-p,dirs[ri]);spans=[]
 for j in range(7):
  ii=np.where((ri==j)&(ds>1e-8))[0];ii=ii[np.argsort(ds[ii])]
  first=int(ii[0])if len(ii)else None
  spans.append({'direction':dirs[j].tolist(),'first_exit_distance_mm':float(ds[first])if first is not None else None,'exit_face_id':int(fi[first])if first is not None else None})
 t=m.triangles[s['sample_face_id']];lengths=np.linalg.norm(t-np.roll(t,1,axis=0),axis=1);rows.append({'original_face_id':s['sample_face_id'],'family':family,'original_surface_point_mm':s['surface_point_mm'],'first_normal_chord_mm':s['first_solid_normal_chord_mm'],'original_face_area_mm2':float(m.area_faces[s['sample_face_id']]),'minimum_triangle_altitude_mm':float(2*m.area_faces[s['sample_face_id']]/max(lengths)),'inside_first_chord_origin_mm':p.tolist(),'first_chord_midpoint_inside':s['first_chord_midpoint_inside'],'backing_direction_then_six_axes':spans,'longest_connected_root_span_mm':max(a['first_exit_distance_mm']or 0 for a in spans)})
report={'stl_sha256':d['stl_sha256'],'method':'Every original face normal chord below0.8mm retained, including tiny numerical corner facets. From verified first-material midpoint trace declared inward backing direction and six axes to FIRST exit only. Longest root span is connectivity evidence, never a minimum-wall claim.','samples':rows,'sample_count':len(rows),'below_08_root_span':sum(r['longest_connected_root_span_mm']<.8 for r in rows)};(R/'short-chord-root-evidence.json').write_text(json.dumps(report,indent=2));print('count',len(rows),'rootbelow',report['below_08_root_span'])
