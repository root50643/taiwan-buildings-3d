"""Independent original-surface containment, topology and Boolean equivalence.
Requires numpy, trimesh, manifold3d; rebuild also requires shapely2.2+.
Does not rerun historical slicing checks or claim physical printability.
"""
from pathlib import Path
import json,hashlib,struct,zipfile,xml.etree.ElementTree as E,subprocess,sys,collections
import numpy as np,trimesh,manifold3d as M
A=Path(__file__).resolve().parents[1];R=A.parent;NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
raw=(R/'model.stl').read_bytes();h=hashlib.sha256(raw).hexdigest();assert h=='5b36ea5d35e43d2b6467279a88beb9ee71a582aa977373642fbb92f1a2c693e9'
n=struct.unpack_from('<I',raw,80)[0];old=np.array([struct.unpack_from('<9f',raw,96+50*i) for i in range(n)]).reshape(n,3,3)
with zipfile.ZipFile(A/'mmu-appearance.3mf') as z:r=E.fromstring(z.read('3D/3dmodel.model'))
me=r.find('m:resources/m:object/m:mesh',NS);v=np.array([[float(x.get(k)) for k in 'xyz'] for x in me.findall('m:vertices/m:vertex',NS)]);f=np.array([[int(x.get(k)) for k in ['v1','v2','v3']] for x in me.findall('m:triangles/m:triangle',NS)]);tri=v[f];fm=json.loads((A/'face-materials.json').read_text());parents=np.array(fm['original_triangle_for_each_output_face']);assert len(parents)==len(f) and parents.min()==0 and parents.max()==n-1
cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);areas=np.linalg.norm(cross,axis=1)/2;assert areas.min()>1e-10
ocross=np.cross(old[:,1]-old[:,0],old[:,2]-old[:,0]);oa=np.linalg.norm(ocross,axis=1)/2
maxdistance=0.;minweight=1.
for i,(t,p) in enumerate(zip(tri,parents)):
 src=old[p];u,w=src[1]-src[0],src[2]-src[0];normal=ocross[p]/np.linalg.norm(ocross[p]);dist=np.abs((t-src[0])@normal);maxdistance=max(maxdistance,float(dist.max()))
 co=np.linalg.lstsq(np.stack([u,w],axis=1), (t-src[0]).T,rcond=None)[0].T;weights=np.column_stack((1-co.sum(axis=1),co));minweight=min(minweight,float(weights.min()));assert weights.min()>-1e-7 and weights.max()<1+1e-7
 assert np.dot(cross[i],ocross[p])>0
area_sum=np.bincount(parents,weights=areas,minlength=n);area_error=float(np.max(np.abs(area_sum-oa)));assert maxdistance<1e-8 and area_error<1e-6
mesh=trimesh.Trimesh(v,f,process=False);assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
edges=np.sort(mesh.edges,axis=1);unique,count=np.unique(edges,axis=0,return_counts=True);assert np.all(count==2)
assert len(mesh.split(only_watertight=False))==1
# Every vertex link must be a single cycle, including inserted boundary points.
links=collections.defaultdict(list)
for face in f:
 for k in range(3):links[int(face[k])].append((int(face[(k+1)%3]),int(face[(k+2)%3])))
for vi,pairs in links.items():
 graph=collections.defaultdict(set)
 for a,b in pairs:graph[a].add(b);graph[b].add(a)
 assert all(len(x)==2 for x in graph.values());seen=set();stack=[next(iter(graph))]
 while stack:
  a=stack.pop()
  if a not in seen:seen.add(a);stack.extend(graph[a]-seen)
 assert len(seen)==len(graph)
orig=trimesh.Trimesh(old.reshape(-1,3),np.arange(n*3).reshape(n,3),process=True)
a=M.Manifold(M.Mesh64(np.asarray(orig.vertices,dtype=np.float64),np.asarray(orig.faces,dtype=np.uint64)))
b=M.Manifold(M.Mesh64(np.asarray(v,dtype=np.float64),np.asarray(f,dtype=np.uint64)))
assert str(a.status())=='Error.NoError' and str(b.status())=='Error.NoError'
added=float((b-a).volume());removed=float((a-b).volume());assert abs(added)<1e-6 and abs(removed)<1e-6
volerr=abs(float(mesh.volume-orig.volume));assert volerr<1e-6;assert np.array_equal(mesh.bounds,orig.bounds)
original={name:hashlib.sha256((A/name).read_bytes()).hexdigest() for name in ['mmu-appearance.3mf','face-materials.json']};subprocess.run([sys.executable,str(A/'source/build_appearance.py')],check=True,capture_output=True);assert all(hashlib.sha256((A/name).read_bytes()).hexdigest()==digest for name,digest in original.items())
# Independent material-boundary locality checks on the delivered XML.
colors=np.array(fm['face_material_indices']);assert set(colors)==set(range(6))
normals=cross/np.linalg.norm(cross,axis=1)[:,None]
unknown_rear=np.all(tri[:,:,1]<20,axis=1)&(colors!=5);assert np.all(colors[unknown_rear]==0)
main_roof=np.all(tri[:,:,2]>38.39,axis=1);assert np.all(colors[main_roof]==0)
long_side=np.all(np.abs(tri[:,:,0]+69.9)<.0001,axis=1)&np.all(tri[:,:,1]<41.21,axis=1);assert np.all(colors[long_side]==0)
right=(np.all(np.abs(tri[:,:,1]-46.5)<.0001,axis=1)|np.all(np.abs(tri[:,:,1]-46.4)<.0001,axis=1))&np.all(tri[:,:,0]<-58.4999,axis=1)&(normals[:,1]>.9)
assert set(colors[right])=={1,2}
white=tri[right&(colors==2)];assert len(white)>0
assert white[:,:,0].min()>=-65.9501 and white[:,:,0].max()<=-62.4499 and white[:,:,2].min()>=20.9999 and white[:,:,2].max()<=37.9001
assert np.all(np.ptp(tri[colors==5,:,2],axis=1)<=3.0001)
d={'original_STL_sha256':h,'original_triangles':n,'original_vertices':len(orig.vertices),'subdivided_vertices':len(v),'subdivided_triangles':len(f),'original_STL_bitwise_unchanged':True,'original_face_order_unchanged':False,'every_output_triangle_mapped_to_original_face':True,'maximum_original_face_plane_distance_mm':maxdistance,'minimum_barycentric_coordinate':minweight,'max_original_face_area_partition_error_mm2':area_error,'minimum_output_triangle_area_mm2':float(areas.min()),'watertight':True,'all_edges_two_faces':True,'vertex_links_single_cycles':True,'winding_consistent':True,'surface_shells':1,'nondegenerate_faces':True,'original_volume_mm3':float(orig.volume),'subdivided_volume_mm3':float(mesh.volume),'volume_difference_mm3':volerr,'bidirectional_boolean_added_volume_mm3':added,'bidirectional_boolean_removed_volume_mm3':removed,'boolean_precision':'float64 manifold3d Mesh64; tolerances1e-6mm3, original envelope preserved','bounds_exact':True,'dimensions_mm':mesh.extents.tolist(),'rebuild_3MF_and_face_manifest_bitwise_identical':True,'original_manufacturing_QA_recomputed':False,'FFF_or_physical_print_validated':False,'photo_bounded_material_regions_verified':True,'right_end_white_region_faces':len(white),'unseen_rear_roof_long_side_neutral_verified':True}
(A/'qa/surface-subdivision-validation.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))
