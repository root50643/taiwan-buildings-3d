"""Verify source triangle identity, manifold topology, material edits, rebuild."""
from pathlib import Path
import json,hashlib,struct,zipfile,xml.etree.ElementTree as E,tempfile,subprocess,sys,collections
import numpy as np,lib3mf,os
A=Path(__file__).resolve().parent;NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def mesh(model):
 it=model.GetMeshObjects();assert it.Count()==1 and it.MoveNext();return it.GetCurrentMeshObject()
def group(model):
 it=model.GetBaseMaterialGroups();assert it.Count()==1 and it.MoveNext();return it.GetCurrentBaseMaterialGroup()
def coords(m):return np.array([list(x.Coordinates) for x in m.GetVertices()]),np.array([list(x.Indices) for x in m.GetTriangleIndices()])
raw=(A/'model.stl').read_bytes();sha=hashlib.sha256(raw).hexdigest()
n=struct.unpack_from('<I',raw,80)[0];ref=np.array([struct.unpack_from('<9f',raw,96+50*i) for i in range(n)]).reshape(n,3,3)
with zipfile.ZipFile(A/'model.3mf') as z:
 assert z.testzip() is None;r=E.fromstring(z.read('3D/3dmodel.model'))
assert r.get('unit')=='millimeter';me=r.find('m:resources/m:object/m:mesh',NS);v=np.array([[float(t.get(k)) for k in 'xyz'] for t in me.findall('m:vertices/m:vertex',NS)]);ts=me.findall('m:triangles/m:triangle',NS);f=np.array([[int(t.get(k)) for k in ['v1','v2','v3']] for t in ts]);assert np.array_equal(v[f],ref)
area=np.linalg.norm(np.cross(ref[:,1]-ref[:,0],ref[:,2]-ref[:,0]),axis=1)/2;assert area.min()>0
edges=collections.Counter();directed=collections.Counter();neighbors=collections.defaultdict(set);links=collections.defaultdict(list)
for face in f:
 for k in range(3):
  a,b=int(face[k]),int(face[(k+1)%3]);edges[tuple(sorted((a,b)))]+=1;directed[(a,b)]+=1;neighbors[a].add(b);neighbors[b].add(a);links[a].append((b,int(face[(k+2)%3])))
assert all(n==2 for n in edges.values());assert all(directed[(a,b)]==directed[(b,a)]==1 for a,b in edges)
seen=set();stack=[0]
while stack:
 a=stack.pop()
 if a not in seen:seen.add(a);stack.extend(neighbors[a]-seen)
surface_components=[];unseen=set(range(len(v)))
while unseen:
 found=set();stack=[next(iter(unseen))]
 while stack:
  a=stack.pop()
  if a not in found:found.add(a);stack.extend(neighbors[a]-found)
 surface_components.append(len(found));unseen-=found
assert len(surface_components)==3 and sum(surface_components)==len(v)
import trimesh
raw_tm=trimesh.Trimesh(v,f,process=False);sh=raw_tm.split(only_watertight=False,repair=False)
positive=[a for a in sh if a.volume>0];negative=[a for a in sh if a.volume<0];assert len(positive)==1 and len(negative)==2
assert all(positive[0].contains([a.centroid])[0] for a in negative)
for vertex,pairs in links.items():
 graph=collections.defaultdict(set)
 for a,b in pairs:graph[a].add(b);graph[b].add(a)
 assert all(len(x)==2 for x in graph.values());seen=set();stack=[next(iter(graph))]
 while stack:
  a=stack.pop()
  if a not in seen:seen.add(a);stack.extend(graph[a]-seen)
 assert len(seen)==len(graph)
vol=float(np.einsum('ij,ij->i',ref[:,0],np.cross(ref[:,1],ref[:,2])).sum()/6);assert vol>0
assert len({tuple(sorted(map(int,t))) for t in f})==len(f)
pal=json.loads((A/'palette.json').read_text())['materials'];fm=json.loads((A/'mesh.json').read_text());colors=fm['face_materials'];assert len(colors)==len(f) and set(colors)==set(range(len(pal)))
assert all(t.get('p1')==t.get('p2')==t.get('p3')==str(c) and t.get('pid')=='2' for t,c in zip(ts,colors))
w=lib3mf.get_wrapper();m=w.CreateModel();rd=m.QueryReader('3mf');rd.SetStrictModeActive(True);rd.ReadFromFile(str(A/'model.3mf'));assert rd.GetWarningCount()==0;mo=mesh(m);vg,fg=coords(mo);assert np.array_equal(vg[fg],ref);assert mo.IsValid() and mo.IsManifoldAndOriented();assert m.GetBuildItems().Count()==1
g=group(m);ids=g.GetAllPropertyIDs();assert len(ids)==len(pal)
assert [g.GetName(t.PropertyIDs[0]) for t in mo.GetAllTriangleProperties()]==[pal[x]['id'] for x in colors]
for i,p in enumerate(pal):
 co=g.GetDisplayColor(ids[i]);assert [co.Red,co.Green,co.Blue,co.Alpha]==[int(p['srgb'][k:k+2],16) for k in [1,3,5]]+[p.get('alpha',255)]
new=lib3mf.Color();new.Red=12;new.Green=34;new.Blue=56;new.Alpha=173;g.SetDisplayColor(ids[2],new)
with tempfile.TemporaryDirectory() as td:
 path=Path(td)/'edit.3mf';wr=m.QueryWriter('3mf');prec=wr.GetDecimalPrecision();wr.WriteToFile(str(path));m2=w.CreateModel();rd2=m2.QueryReader('3mf');rd2.SetStrictModeActive(True);rd2.ReadFromFile(str(path));assert rd2.GetWarningCount()==0;mo2=mesh(m2);v2,f2=coords(mo2);err=float(abs(v2[f2]-ref).max());assert err<1e-4 and mo2.IsManifoldAndOriented();assert np.all(np.linalg.norm(np.cross(v2[f2[:,1]]-v2[f2[:,0]],v2[f2[:,2]]-v2[f2[:,0]]),axis=1)>0)
 g2=group(m2);ids2=g2.GetAllPropertyIDs()
 for i,p in enumerate(pal):
  co=g2.GetDisplayColor(ids2[i]);assert [co.Red,co.Green,co.Blue,co.Alpha]==([12,34,56,173] if i==2 else [int(p['srgb'][k:k+2],16) for k in [1,3,5]]+[p.get('alpha',255)])
 assert [g2.GetName(t.PropertyIDs[0]) for t in mo2.GetAllTriangleProperties()]==[pal[x]['id'] for x in colors]
# Actual native 3MF vertex edit/write/read, independent of XML text editing.
m3=w.CreateModel();rr=m3.QueryReader('3mf');rr.SetStrictModeActive(True);rr.ReadFromFile(str(A/'model.3mf'));mo3=mesh(m3);point=mo3.GetVertex(0);point.Coordinates[0]+=.25;mo3.SetVertex(0,point)
with tempfile.TemporaryDirectory() as td:
 pth=Path(td)/'vertex-edit.3mf';m3.QueryWriter('3mf').WriteToFile(str(pth));m4=w.CreateModel();r4=m4.QueryReader('3mf');r4.SetStrictModeActive(True);r4.ReadFromFile(str(pth));assert r4.GetWarningCount()==0;v4,f4=coords(mesh(m4));expected_v=vg.copy();expected_v[0,0]+=.25;assert np.max(np.abs(v4-expected_v))<1e-4 and np.array_equal(f4,fg)
 assert [group(m4).GetName(t.PropertyIDs[0]) for t in mesh(m4).GetAllTriangleProperties()]==[pal[x]['id'] for x in colors]
files=['model.stl','model.3mf','mesh.json','palette.json'];before={p:hashlib.sha256((A/p).read_bytes()).hexdigest() for p in files};subprocess.run([os.environ.get('BUILD_PYTHON',sys.executable),str(A/'build_model.py')],check=True);assert all(hashlib.sha256((A/p).read_bytes()).hexdigest()==h for p,h in before.items())
d={'native_3mf_single_vertex_edit_save_reopen':True,'test_vertex_delta_x_mm':.25,'source_STL_SHA256':sha,'source_STL_unchanged':True,'vertices':len(v),'triangles':len(f),'original_triangle_coordinates_and_order_exact':True,'no_subdivision':True,'dimensions_mm':np.ptp(v,axis=0).tolist(),'positive_volume_mm3':vol,'zero_area_faces':0,'duplicate_faces':0,'all_edges_two_opposed_faces':True,'vertex_links_single_cycles':True,'connected_surface':False,'boundary_shells':3,'one_positive_outer_two_negative_approx_interior_shells':True,'material_body_connected':True,'material_count':len(pal),'all_faces_assigned':True,'lib3mf_strict_warnings':0,'lib3mf_valid_manifold_oriented':True,'lib3mf_import_coordinates_exact':True,'lib3mf_writer_decimal_precision':prec,'lib3mf_edit_coordinate_error_mm':err,'single_material_edit_preserves_other_colors_alpha_and_assignments':True,'all_materials_opaque':all(p.get('alpha',255)==255 for p in pal),'test_edited_material_alpha':173,'STL_has_no_transparency':True,'deterministic_3MF_and_manifests':True,'new_geometry_manufacturing_QA_separate_report':True,'FFF_and_physical_print_tested':False}
(A/'qa/exchange-validation.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))
