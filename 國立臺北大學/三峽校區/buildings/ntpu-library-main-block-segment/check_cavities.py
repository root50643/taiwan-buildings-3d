#!/usr/bin/env python3
"""Read-only exact-weld STL cavity audit. No mesh healing or tolerance welding.
Uses trimesh containment/distance and manifold boolean set checks independently
of builder geometry. Boundary-shell count is not material component count.
"""
from pathlib import Path
import struct,json,hashlib,datetime,itertools
import numpy as np
import trimesh
import manifold3d as md
D=Path(__file__).resolve().parent

def manifold(m):
 q=md.Manifold(md.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
 assert q.status().name=='NoError'
 return q

def triangle_contact(a,b,eps=1e-7):
 """Closed triangle SAT including coplanar in-plane edge normals, in original millimeters."""
 ea=np.roll(a,-1,axis=0)-a;eb=np.roll(b,-1,axis=0)-b;na=np.cross(ea[0],ea[1]);nb=np.cross(eb[0],eb[1])
 axes=[na,nb]+[np.cross(x,y) for x in ea for y in eb]+[np.cross(na,x) for x in ea]+[np.cross(nb,x) for x in eb]
 for ax in axes:
  size=np.linalg.norm(ax)
  if size<1e-16:continue
  ax=ax/size;ap=a@ax;bp=b@ax
  if ap.max()<bp.min()-eps or bp.max()<ap.min()-eps:return False
 return True


def shell_surface_contacts(a,b):
 tree=trimesh.util.bounds_tree(np.stack([a.triangles.min(axis=1),a.triangles.max(axis=1)],axis=1));found=[];candidates=0
 for i,t in enumerate(b.triangles):
  bounds=np.r_[t.min(axis=0)-1e-7,t.max(axis=0)+1e-7]
  for k in tree.intersection(bounds):
   candidates+=1
   if triangle_contact(a.triangles[k],t):found.append([int(k),int(i)])
 return {'candidate_pairs':candidates,'contact_pairs':len(found),'first_contacts':found[:10]}



def run():
 b=(D/'model.stl').read_bytes();n=struct.unpack_from('<I',b,80)[0];assert len(b)==84+50*n
 rec=np.frombuffer(b,dtype=[('normal','<f4',(3,)),('tri','<f4',(3,3)),('attr','<u2')],offset=84,count=n)
 t=rec['tri'].astype(np.float64);v,inv=np.unique(t.reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3)
 assert np.isfinite(t).all() and (np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>0).all()
 mesh=trimesh.Trimesh(v,f,process=False);assert mesh.is_watertight and mesh.is_winding_consistent
 shells=mesh.split(only_watertight=False);outer=[s for s in shells if s.volume>0];negative=[s for s in shells if s.volume<0]
 assert len(shells)==8 and len(outer)==1 and len(negative)==7
 outer=outer[0];om=manifold(outer);rows=[];cavities=[];cms=[]
 # Reference geometry labels and centerline air probes; fixed proportional mm scale=2.5.
 specs=[(17,20,13.25,13.25,'3F_diagonal_bridge'),(35,32,13.25,18.05,'3F4F_stair'),(12,8,18.05,18.05,'4F_bridge'),(24,20,22.85,22.85,'5F_bridge'),(15,19,22.85,27.65,'5F6F_stair'),(39,43,27.65,27.65,'6F_bridge'),(21,25,32.45,32.45,'7F_bridge')]
 for i,s in enumerate(negative):
  c=trimesh.Trimesh(s.vertices,s.faces[:,::-1],process=False);assert c.is_watertight and c.is_winding_consistent and c.volume>0
  cm=manifold(c);assert (cm-om).is_empty();cavities.append(c);cms.append(cm)
  pts=np.vstack([c.vertices,c.triangles_center]);inside=outer.contains(pts);assert inside.all()
  # All required vertices and triangle centroids, not only a representative center.
  distances=[]
  for start in range(0,len(pts),256): distances.extend(trimesh.proximity.closest_point(outer,pts[start:start+256])[1].tolist())
  assert min(distances)>0
  contact=shell_surface_contacts(outer,c);assert contact['contact_pairs']==0
  matches=[]
  for xa,xb,z0,z1,name in specs:
   p=np.array([.5*(xa+xb),0,.5*(z0+z1)+1.5])*2.5
   if c.contains([p])[0]: matches.append((name,p))
  assert len(matches)==1;name,p=matches[0];assert outer.contains([p])[0] and not mesh.contains([p])[0]
  rows.append(dict(cavity_index=i,source_bridge=name,signed_volume_mm3=float(s.volume),triangles=len(s.faces),vertices=len(s.vertices),bounds_mm=s.bounds.tolist(),vertices_and_centroids_tested=len(pts),all_strictly_inside_outer=True,outer_triangle_surface_contact_check=contact,minimum_sampled_outer_surface_distance_mm=min(distances),cavity_minus_outer_empty=True,air_probe_mm=p.tolist(),air_probe_inside_cavity=True,air_probe_inside_outer=True,air_probe_inside_material=False))
 pairs=[]
 for i,j in itertools.combinations(range(7),2):
  q=cms[i]^cms[j];assert q.is_empty() and q.volume()==0
  contact=shell_surface_contacts(cavities[i],cavities[j]);assert contact['contact_pairs']==0
  pairs.append(dict(surface_contact_check=contact,cavities=[i,j],intersection_empty=True,intersection_volume_mm3=float(q.volume())))
 assert len({r['source_bridge']for r in rows})==7
 material=om
 for cm in cms:material=material-cm
 expected=float(outer.volume+sum(s.volume for s in negative));assert abs(expected-mesh.volume)<1e-6
 assert abs(material.volume()-mesh.volume)<1e-3
 raw=manifold(mesh);a=raw-material;b2=material-raw;print('set difference diagnostic',a.is_empty(),a.volume(),a.num_tri(),b2.is_empty(),b2.volume(),b2.num_tri(),flush=True)
 diagnostic=dict(raw_minus_rebooleaned=dict(empty=a.is_empty(),signed_volume_mm3=float(a.volume()),triangles=a.num_tri()),rebooleaned_minus_raw=dict(empty=b2.is_empty(),signed_volume_mm3=float(b2.volume()),triangles=b2.num_tri()),disposition='NOT an exact Boolean equivalence PASS. Re-booleaning coincident faces produced numerical residual output; not a shell in raw STL, not deleted or repaired. Proof uses raw exact signed-shell partition, strict containment, no triangle contacts and disjoint cavities instead.')
 assert sum(len(s.faces)for s in shells)==n
 exact_partition=np.concatenate([s.triangles for s in shells]);assert sorted(map(tuple,exact_partition.reshape(n,9)))==sorted(map(tuple,t.reshape(n,9)))
 result=dict(status='PASS_CAVITY_AWARE_SINGLE_CONNECTED_SOLID',checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),stl_sha256=hashlib.sha256(b).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),triangles=n,exact_weld_vertices=len(v),boundary_shells=len(shells),positive_outer_shells=1,negative_cavity_shells=7,zero_volume_residual_shells=0,all_shells_closed_and_consistent=True,cavities=rows,all_21_pairwise_cavity_boolean_intersections=pairs,reboolean_difference_diagnostic=diagnostic,raw_exact_signed_shell_triangle_partition=True,outer_minus_cavities_equals_raw_material_by_oriented_boundary_partition=True,material_volume_mm3=float(mesh.volume),single_connected_material_solid=True,connectivity_basis='One closed connected outer boundary, seven closed strictly internal disjoint air cavities, no detached positive or zero-volume shells. All outer/cavity and cavity/cavity triangle candidates tested with closed-triangle SAT including coplanar axes; zero contact. SAT implementation adapted from reviewer_mesh_core.py; no builder code imported.',geometry_repaired=False,limitations='Geometric closed-solid test, not print or structural certification. Enclosed air cavities in opaque printable glazing proxies may need slicer/process-specific treatment. Original single-boundary-shell criterion remains a distinct failed/not-applicable gate, not relabeled PASS.')
 (D/'qa/cavity-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(result['status'],result['stl_sha256'],len(rows),min(r['minimum_sampled_outer_surface_distance_mm'] for r in rows))
if __name__=='__main__':run()
