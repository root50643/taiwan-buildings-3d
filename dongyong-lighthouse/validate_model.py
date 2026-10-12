"""Non-mutating STL topology, normals and source-rebuild validation.
Usage: python validate_model.py. Run beside model.stl and build_model.py.
The 2-manifold vertex-link test detects point-touch singularities beyond edges.
"""
import hashlib,json,struct,sys,tempfile,subprocess
from pathlib import Path
import numpy as np
import trimesh
HERE=Path(__file__).resolve().parent;stl=HERE/'model.stl'
mesh=trimesh.load(stl,force='mesh',process=True)
_,counts=np.unique(np.sort(mesh.edges,axis=1),axis=0,return_counts=True)
adj=[[] for _ in mesh.vertices]
for x,y,z in mesh.faces:adj[x].append((y,z));adj[y].append((x,z));adj[z].append((x,y))
bad_links=0
for pairs in adj:
 d={}
 for x,y in pairs:d.setdefault(int(x),set()).add(int(y));d.setdefault(int(y),set()).add(int(x))
 if not d or any(len(v)!=2 for v in d.values()):bad_links+=1;continue
 pending=[next(iter(d))];seen=set()
 while pending:
  v=pending.pop()
  if v in seen:continue
  seen.add(v);pending.extend(d[v]-seen)
 if len(seen)!=len(d):bad_links+=1
raw=stl.read_bytes();n=struct.unpack_from('<I',raw,80)[0]
dtype=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attr','<u2')]);tri=np.frombuffer(raw, dtype=dtype,offset=84,count=n)
cross=np.cross(tri['vertices'][:,1]-tri['vertices'][:,0],tri['vertices'][:,2]-tri['vertices'][:,0]);length=np.linalg.norm(cross,axis=1);valid=length>1e-10
unit=cross[valid]/length[valid,None];stored=tri['normal'][valid];dot=np.einsum('ij,ij->i',unit,stored)
parts=mesh.split(only_watertight=False);bottom=np.isclose(mesh.triangles[:,:,2],mesh.bounds[0,2],atol=1e-5).all(axis=1)
def canonical(m):
 t=np.round(m.triangles,5);rows=[]
 for v in t:
  v=v[np.lexsort((v[:,2],v[:,1],v[:,0]))];rows.append(v.reshape(-1))
 rows=np.array(rows);rows=rows[np.lexsort(tuple(rows[:,i] for i in range(8,-1,-1)))];return hashlib.sha256(rows.astype('<f8').tobytes()).hexdigest()
with tempfile.TemporaryDirectory() as tmp:
 dest=Path(tmp)/'rebuild.stl';r=subprocess.run([sys.executable,str(HERE/'build_model.py'),'--output',str(dest)],capture_output=True,text=True)
 rebuilt=trimesh.load(dest,force='mesh',process=True) if r.returncode==0 and dest.exists() else None
 rebuild_equal=rebuilt is not None and canonical(mesh)==canonical(rebuilt)
 checks={'finite_coordinates':bool(np.isfinite(mesh.vertices).all()),'nondegenerate_faces':bool((mesh.area_faces>1e-9).all()),'watertight':bool(mesh.is_watertight),'winding_consistent':bool(mesh.is_winding_consistent),'stored_normals_match_winding':bool(valid.all() and (dot>.999).all()),'single_connected_boundary':len(parts)==1,'all_edges_two_faces':bool((counts==2).all()),'all_vertex_links_single_cycles':bad_links==0,'positive_volume':bool(mesh.volume>0),'single_shell_no_enclosed_cavity_boundary':len(parts)==1,'base_on_z_zero':abs(float(mesh.bounds[0,2]))<1e-4,'flat_contact_area':float(mesh.area_faces[bottom].sum())>1,'longest_edge_150mm':abs(float(mesh.extents.max())-150)<.02,'source_rebuild_matches_canonical_triangles':bool(rebuild_equal)}
 report={'passed':all(checks.values()),'checks':checks,'units':'mm','dimensions_mm':mesh.extents.tolist(),'triangles':len(mesh.faces),'vertices':len(mesh.vertices),'boundary_components':len(parts),'volume_mm3':float(mesh.volume),'contact_area_mm2':float(mesh.area_faces[bottom].sum()),'euler_number':int(mesh.euler_number),'nonmanifold_edges':int(np.sum(counts!=2)),'nonmanifold_vertex_links':bad_links,'minimum_normal_dot':float(dot.min()),'stl_sha256':hashlib.sha256(raw).hexdigest(),'canonical_triangle_sha256':canonical(mesh),'source_rebuild_returncode':r.returncode,'limitations':['Digital topology validation is not a physical print test.','No separate triangle/triangle self-intersection test is performed; source uses manifold3d Boolean solids.','Minimum relief details and supports need inspection in the chosen slicer.']}
 (HERE/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(0 if report['passed'] else 1)
