#!/usr/bin/env python3
"""Assign only numerically proven whole original STL faces; never regenerate geometry."""
import argparse,json,hashlib,struct,csv,shutil
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--stl',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();config=Path(__file__).resolve().parent.parent
P=json.loads((config/'parameters.json').read_text());palette=json.loads((config/'palette.json').read_text());b=a.stl.read_bytes()
assert hashlib.sha256(b).hexdigest()==P['original_stl_sha256'] and len(b)==P['original_stl_bytes']
n=struct.unpack_from('<I',b,80)[0];assert n==P['original_triangles'] and len(b)==84+n*50
raw=np.frombuffer(b,dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]),offset=84);tri=raw['v'].astype(np.float64)
cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);areas=np.linalg.norm(cross,axis=1)/2;assert np.all(areas>0);norm=cross/(2*areas[:,None]);tol=P['tolerance_mm'];B=P['numeric_bounds']
# Recompute inclusion against all three vertices, not centroids or a photo silhouette.
found=[[],[],[]];units={'windows':{},'shafts':{}}
for i,t in enumerate(tri):
 r=B['roof'];q=(t[:,1]-r['eave_y'])/(r['ridge_y']-r['eave_y']);half=r['half_eave_width']+(r['half_ridge_width']-r['half_eave_width'])*q
 if np.all(q>=-tol) and np.all(q<=1+tol) and np.all(abs(t[:,2]-(r['eave_z']+r['rise']*q))<tol) and np.all(abs(t[:,0])<=half+tol) and norm[i,1]<0 and norm[i,2]>0: found[0].append(i)
 r=B['windows']
 for j in range(r['count']):
  x=r['first_center_x']+j*r['spacing_x']
  if np.all(abs(t[:,1]-r['back_y'])<tol) and np.all(abs(t[:,0]-x)<=r['half_width']+tol) and np.all(t[:,2]>=r['z_bounds'][0]-tol) and np.all(t[:,2]<=r['z_bounds'][1]+tol) and norm[i,1]<-.99999:
   found[1].append(i);units['windows'].setdefault(str(j+1),[]).append(i)
 r=B['shafts']
 for j in range(1,r['count']+1):
  d=t[:,:2]-[r['start_x']+j*r['spacing_x'],r['center_y']];ang=np.degrees(np.arctan2(d[:,1],d[:,0]))
  if np.all(abs(np.linalg.norm(d,axis=1)-r['radius'])<tol) and np.all(t[:,2]>=r['z_bounds'][0]-tol) and np.all(t[:,2]<=r['z_bounds'][1]+tol) and np.all(ang>=r['front_arc_degrees'][0]-.001) and np.all(ang<=r['front_arc_degrees'][1]+.001) and np.ptp(ang)<=r['facet_step_degrees']+.001 and abs(norm[i,2])<tol:
   found[2].append(i);units['shafts'].setdefault(str(j),[]).append(i)
assert [len(x) for x in found]==[2,36,160] and len(set(sum(found,[])))==198
for g,ids in zip(P['groups'],found):assert g['original_face_ids']==ids, g['region']
assert len(units['windows'])==18 and all(len(x)==2 for x in units['windows'].values())
assert len(units['shafts'])==8 and all(len(x)==20 for x in units['shafts'].values())
for ids in units['windows'].values():assert abs(areas[ids].sum()-3.9*5.7)<tol
# Exact coordinate reuse; deduplication only represents shared vertices, without moving any.
vertices=[];faces=[];lookup={}
for t in tri:
 face=[]
 for xyz in t:
  key=tuple(xyz)
  if key not in lookup:lookup[key]=len(vertices);vertices.append(key)
  face.append(lookup[key])
 faces.append(face)
v=np.asarray(vertices,dtype=np.float64);f=np.asarray(faces,dtype=np.int32);assert np.array_equal(v[f],tri)
m=np.zeros(n,dtype=np.int32)
for g in P['groups']:m[g['original_face_ids']]=g['material_index']
assert np.bincount(m).tolist()==[2916,2,36,160]
a.out.mkdir(parents=True,exist_ok=True);(a.out/'qa').mkdir(exist_ok=True)
for file in ['parameters.json','palette.json']:
 if (config/file).resolve()!=(a.out/file).resolve():shutil.copyfile(config/file,a.out/file)
np.savez_compressed(a.out/'mesh-data.npz',vertices=v,faces=f,materials=m,rule_indices=m,original_triangles=tri)
with (a.out/'face-materials.csv').open('w',newline='') as file:
 w=csv.writer(file);w.writerow(['original_stl_triangle_index','material_index','material_id']);w.writerows((i,int(mi),palette[mi]['id'])for i,mi in enumerate(m))
report={'original_stl_sha256':hashlib.sha256(b).hexdigest(),'original_stl_bytes':len(b),'original_triangles':n,'unique_vertices':len(v),'source_stl_mutated':False,'coordinates_and_triangle_vertex_order_exact':True,'geometry_regenerated_repaired_or_subdivided':False,'all_three_vertices_and_normals_tested':True,'centroid_selection':False,'analytic_element_containment_not_photogrammetric_registration':True,'material_counts':dict(zip([x['id']for x in palette],np.bincount(m).tolist())),'unit_face_groups':units,'regions':[{'name':g['region'],'face_ids':g['original_face_ids'],'area_mm2':float(areas[g['original_face_ids']].sum())}for g in P['groups']]}
(a.out/'qa/face-containment.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['original_triangles','unique_vertices','material_counts','coordinates_and_triangle_vertex_order_exact']}))
