"""Validate the original delivered STL, source rebuild and Blender mesh agreement.
Usage: python validate_model.py --output validation.json
Requires Blender on PATH (or --blender path). Does not repair the delivered file.
"""
from pathlib import Path
import argparse, hashlib, json, os, shutil, struct, subprocess, sys, tempfile
import numpy as np
import trimesh
p=argparse.ArgumentParser();p.add_argument('--output',default='validation.json');p.add_argument('--blender',default='blender');a=p.parse_args()
root=Path(__file__).resolve().parent; path=root/'model.stl';raw=path.read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest()
# Validate the original binary STL's saved normal vectors before any mesh processing.
n=struct.unpack_from('<I',raw,80)[0]
records=np.frombuffer(raw,offset=84,dtype=np.dtype([('normal','<f4',(3,)),('v','<f4',(3,3)),('attr','<u2')]),count=n)
tri=records['v'].astype(float); saved=records['normal'].astype(float)
calc=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);norm=np.linalg.norm(calc,axis=1)
unit=calc/np.maximum(norm[:,None],1e-30)
mesh=trimesh.load(path,force='mesh',process=True)
edges,cnt=np.unique(np.sort(mesh.edges,axis=1),axis=0,return_counts=True)
# Face-connected components without optional graph packages.
edgefaces={}; parent=list(range(len(mesh.faces)))
def find(i):
 while parent[i]!=i: parent[i]=parent[parent[i]]; i=parent[i]
 return i
def union(i,j):
 i,j=find(i),find(j)
 if i!=j:parent[j]=i
links=[[] for _ in mesh.vertices]
for fi,(i,j,k) in enumerate(mesh.faces):
 for u,v in [(i,j),(j,k),(k,i)]:
  key=tuple(sorted((int(u),int(v))))
  if key in edgefaces: union(fi,edgefaces[key])
  else:edgefaces[key]=fi
 for v,u,w in [(i,j,k),(j,k,i),(k,i,j)]:links[v].append((u,w))
comps=len({find(i) for i in range(len(parent))});badlinks=0
for pairs in links:
 adj={}
 for u,v in pairs:adj.setdefault(int(u),set()).add(int(v));adj.setdefault(int(v),set()).add(int(u))
 if not adj or any(len(v)!=2 for v in adj.values()):badlinks+=1;continue
 seen=set();todo=[next(iter(adj))]
 while todo:
  v=todo.pop()
  if v in seen:continue
  seen.add(v);todo.extend(adj[v]-seen)
 if len(seen)!=len(adj):badlinks+=1
checks={'binary_stl_length':len(raw)==84+50*n,'finite_coordinates_and_normals':bool(np.isfinite(tri).all() and np.isfinite(saved).all()),'original_normals_unit':bool(np.allclose(np.linalg.norm(saved,axis=1),1,atol=1e-5)),'original_normals_match_winding':bool(np.allclose(saved,unit,atol=1e-5)),'nondegenerate_original_faces':bool((norm>1e-9).all()),'watertight':bool(mesh.is_watertight),'winding_consistent':bool(mesh.is_winding_consistent),'every_edge_two_faces':bool((cnt==2).all()),'vertex_links_single_cycles':badlinks==0,'one_connected_surface_shell':comps==1,'no_disconnected_enclosed_shell':comps==1,'positive_volume':bool(mesh.volume>0),'base_z_zero':abs(float(mesh.bounds[0,2]))<1e-6,'longest_dimension_150mm':abs(float(mesh.extents.max())-150)<1e-5}
with tempfile.TemporaryDirectory() as td:
 tmp=Path(td);shutil.copy(root/'build_model.py',tmp/'build_model.py')
 subprocess.run([sys.executable,str(tmp/'build_model.py')],check=True,capture_output=True,text=True)
 rebuild=sha((tmp/'model.stl').read_bytes());checks['source_rebuild_hash_matches']=rebuild==sha(raw)
 # Inspect mesh data from saved editable scene, never rely on the image alone.
 expr="import bpy,json; from pathlib import Path; objs=[o for o in bpy.context.scene.objects if o.type=='MESH']; assert len(objs)==1; o=objs[0]; Path("+repr(str(tmp/'blend.json'))+").write_text(json.dumps({'vertices':[list(o.matrix_world@v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons]}))"
 subprocess.run([a.blender,'-b',str(root/'scene.blend'),'-t','2','--python-expr',expr],check=True,capture_output=True,text=True)
 b=json.loads((tmp/'blend.json').read_text());bv=np.array(b['vertices']);bf=np.array(b['faces'])
 def geometry_hash(t):
  # Compare orientation-independent exact printed triangle positions to 0.00001 mm.
  records=[]
  for face in t:records.append(tuple(sorted(tuple(round(float(x),5) for x in v) for v in face)))
  return sha(json.dumps(sorted(records),separators=(',',':')).encode())
 stl_geom=geometry_hash(tri);blend_geom=geometry_hash(bv[bf]);checks['blend_stl_geometry_agree']=stl_geom==blend_geom
bottom=np.isclose(mesh.triangles[:,:,2],0,atol=1e-6).all(axis=1)
report={'passed':all(checks.values()),'checks':checks,'dimensions_mm':mesh.extents.tolist(),'triangles':len(mesh.faces),'vertices':len(mesh.vertices),'surface_shells':comps,'nonmanifold_edges':int((cnt!=2).sum()),'bad_vertex_links':badlinks,'volume_mm3':float(mesh.volume),'base_contact_area_mm2':float(mesh.area_faces[bottom].sum()),'stl_sha256':sha(raw),'rebuild_stl_sha256':rebuild,'stl_geometry_sha256':stl_geom,'blend_geometry_sha256':blend_geom,'limitations':['Not a slicer validation or physical print test.','Exterior photo-based miniature; depth and unseen elevations are estimates.','One connected surface shell excludes separate hidden cavity shells; exhaustive self-intersection testing is not claimed.']}
(root/a.output).write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(0 if report['passed'] else 1)
