"""Verify source triangle identity, manifold topology, material edits, rebuild."""
from pathlib import Path
import json,hashlib,struct,zipfile,xml.etree.ElementTree as E,tempfile,subprocess,sys,collections
import numpy as np,lib3mf
A=Path(__file__).resolve().parents[1];NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def mesh(model):
 it=model.GetMeshObjects();assert it.Count()==1 and it.MoveNext();return it.GetCurrentMeshObject()
def group(model):
 it=model.GetBaseMaterialGroups();assert it.Count()==1 and it.MoveNext();return it.GetCurrentBaseMaterialGroup()
def coords(m):return np.array([list(x.Coordinates) for x in m.GetVertices()]),np.array([list(x.Indices) for x in m.GetTriangleIndices()])
raw=(A.parent/'model.stl').read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha=='80c6ce47e2253100375bc2cd1b82ff0c539daf10016e8ea5074a026f29247e69'
n=struct.unpack_from('<I',raw,80)[0];ref=np.array([struct.unpack_from('<9f',raw,96+50*i) for i in range(n)]).reshape(n,3,3)
with zipfile.ZipFile(A/'admin-appearance.3mf') as z:
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
assert len(seen)==len(v)
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
pal=json.loads((A/'palette.json').read_text())['materials'];fm=json.loads((A/'face-materials.json').read_text());colors=fm['face_material_indices'];assert len(colors)==len(f) and set(colors)==set(range(len(pal)))
assert all(t.get('p1')==t.get('p2')==t.get('p3')==str(c) and t.get('pid')=='20' for t,c in zip(ts,colors))
w=lib3mf.get_wrapper();m=w.CreateModel();rd=m.QueryReader('3mf');rd.SetStrictModeActive(True);rd.ReadFromFile(str(A/'admin-appearance.3mf'));assert rd.GetWarningCount()==0;mo=mesh(m);vg,fg=coords(mo);assert np.array_equal(vg[fg],ref);assert mo.IsValid() and mo.IsManifoldAndOriented();assert m.GetBuildItems().Count()==1
g=group(m);ids=g.GetAllPropertyIDs();assert len(ids)==len(pal)
assert [g.GetName(t.PropertyIDs[0]) for t in mo.GetAllTriangleProperties()]==[pal[x]['id'] for x in colors]
for i,p in enumerate(pal):
 co=g.GetDisplayColor(ids[i]);assert [co.Red,co.Green,co.Blue,co.Alpha]==[int(p['srgb'][k:k+2],16) for k in [1,3,5]]+[255]
new=lib3mf.Color();new.Red=12;new.Green=34;new.Blue=56;new.Alpha=255;g.SetDisplayColor(ids[2],new)
with tempfile.TemporaryDirectory() as td:
 path=Path(td)/'edit.3mf';wr=m.QueryWriter('3mf');prec=wr.GetDecimalPrecision();wr.WriteToFile(str(path));m2=w.CreateModel();rd2=m2.QueryReader('3mf');rd2.SetStrictModeActive(True);rd2.ReadFromFile(str(path));assert rd2.GetWarningCount()==0;mo2=mesh(m2);v2,f2=coords(mo2);err=float(abs(v2[f2]-ref).max());assert err<1e-4 and mo2.IsManifoldAndOriented();assert np.all(np.linalg.norm(np.cross(v2[f2[:,1]]-v2[f2[:,0]],v2[f2[:,2]]-v2[f2[:,0]]),axis=1)>0)
 g2=group(m2);ids2=g2.GetAllPropertyIDs()
 for i,p in enumerate(pal):
  co=g2.GetDisplayColor(ids2[i]);assert [co.Red,co.Green,co.Blue,co.Alpha]==([12,34,56,255] if i==2 else [int(p['srgb'][k:k+2],16) for k in [1,3,5]]+[255])
 assert [g2.GetName(t.PropertyIDs[0]) for t in mo2.GetAllTriangleProperties()]==[pal[x]['id'] for x in colors]
files=['admin-appearance.3mf','face-materials.json','palette.json'];before={p:hashlib.sha256((A/p).read_bytes()).hexdigest() for p in files};subprocess.run([sys.executable,str(A/'source/build_appearance.py')],check=True);assert all(hashlib.sha256((A/p).read_bytes()).hexdigest()==h for p,h in before.items())
d={'source_STL_SHA256':sha,'source_STL_unchanged':True,'vertices':len(v),'triangles':len(f),'original_triangle_coordinates_and_order_exact':True,'no_subdivision':True,'dimensions_mm':np.ptp(v,axis=0).tolist(),'positive_volume_mm3':vol,'zero_area_faces':0,'duplicate_faces':0,'all_edges_two_opposed_faces':True,'vertex_links_single_cycles':True,'connected_surface':True,'material_count':len(pal),'all_faces_assigned':True,'lib3mf_strict_warnings':0,'lib3mf_valid_manifold_oriented':True,'lib3mf_import_coordinates_exact':True,'lib3mf_writer_decimal_precision':prec,'lib3mf_edit_coordinate_error_mm':err,'single_material_edit_preserves_other_colors_and_assignments':True,'deterministic_3MF_and_manifests':True,'historical_manufacturing_QA_not_recomputed':True,'FFF_and_physical_print_tested':False}
(A/'qa/exchange-validation.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))
