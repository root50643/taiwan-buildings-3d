"""Independent original STL/XML/lib3mf strict import/edit and deterministic rebuild.
python appearance/source/verify_exchange.py (installed numpy and lib3mf).
No new slicing/manufacturing claim. Original historical QA remains unchanged.
"""
from pathlib import Path
import json,hashlib,struct,zipfile,xml.etree.ElementTree as E,tempfile,subprocess,sys
import numpy as np,lib3mf
A=Path(__file__).resolve().parents[1];R=A.parent;NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def mesh(m):
 it=m.GetMeshObjects();assert it.Count()==1 and it.MoveNext();return it.GetCurrentMeshObject()
def group(m):
 it=m.GetBaseMaterialGroups();assert it.Count()==1 and it.MoveNext();return it.GetCurrentBaseMaterialGroup()
def coords(o):
 v=np.array([list(x.Coordinates) for x in o.GetVertices()]);f=np.array([list(x.Indices) for x in o.GetTriangleIndices()]);return v,f
def main():
 raw=(R/'model.stl').read_bytes();assert hashlib.sha256(raw).hexdigest()=='ba8cec3cadb311a60aad2ea0efd669c761f98a9f73b4df87c5ffbf29009d216a'
 n=struct.unpack_from('<I',raw,80)[0];assert n==5340 and len(raw)==84+n*50;ref=np.array([struct.unpack_from('<9f',raw,96+50*i) for i in range(n)]).reshape(n,3,3)
 p=A/'millennium-appearance.3mf';pal=json.loads((A/'palette.json').read_text())['materials'];fm=json.loads((A/'face-materials.json').read_text());colors=fm['face_material_indices']
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None and set(z.namelist())=={'[Content_Types].xml','_rels/.rels','3D/3dmodel.model'};r=E.fromstring(z.read('3D/3dmodel.model'))
 assert r.get('unit')=='millimeter';ob=r.find('m:resources/m:object',NS);me=ob.find('m:mesh',NS);v=np.array([[float(t.get(k)) for k in 'xyz'] for t in me.findall('m:vertices/m:vertex',NS)]);ts=me.findall('m:triangles/m:triangle',NS);f=np.array([[int(t.get(k)) for k in ['v1','v2','v3']] for t in ts]);assert np.array_equal(v[f],ref)
 # Independent bounds: no side/back color wrapping; forward cap slopes only.
 brick=ref[np.array(colors)==1];assert len(brick)>0 and np.max(brick[:,:,1])<=-10.0+.0001
 glass=ref[np.array(colors)==3];assert len(glass)>0 and np.max(glass[:,:,1])<=-10+.0001
 main_glass=np.all(np.abs(glass[:,:,1]+14)<.0001,axis=1);arc_glass=glass[~main_glass];assert np.min(arc_glass[:,:,0])>=-18.6 and np.max(arc_glass[:,:,0])<=2.6
 rear=np.all(ref[:,:,1]>25,axis=1);assert all(c in [0,5] for c in np.array(colors)[rear])
 tiles=ref[np.array(colors)==4];assert len(tiles)>0 and np.max(tiles[:,:,1])<=9+.0001 and np.min(tiles[:,:,2])>=90-.0001
 assert len(v)==2668 and all(t.get('pid')=='20' and t.get('p1')==t.get('p2')==t.get('p3')==str(c) for t,c in zip(ts,colors))
 assert [(x.get('name'),x.get('displaycolor')) for x in r.findall('m:resources/m:basematerials/m:base',NS)]==[(c['id'],c['srgb']+'FF') for c in pal]
 # Independent topology and bounds checks on delivered XML, beyond exact STL match.
 from collections import defaultdict
 edges=defaultdict(list);neighbors=[set() for _ in f];links=[[] for _ in v]
 for fi,face in enumerate(f):
  for k in range(3):
   aa,bb=int(face[k]),int(face[(k+1)%3]);edges[tuple(sorted((aa,bb)))].append((fi,aa,bb))
   links[int(face[k])].append((int(face[(k+1)%3]),int(face[(k+2)%3])))
 assert all(len(e)==2 and e[0][1:]==e[1][1:][::-1] for e in edges.values())
 for e in edges.values():neighbors[e[0][0]].add(e[1][0]);neighbors[e[1][0]].add(e[0][0])
 seen=set();todo=[0]
 while todo:
  q=todo.pop()
  if q in seen:continue
  seen.add(q);todo.extend(neighbors[q]-seen)
 assert len(seen)==len(f)
 for link in links:
  adj=defaultdict(set)
  for aa,bb in link:adj[aa].add(bb);adj[bb].add(aa)
  assert all(len(ns)==2 for ns in adj.values());seen=set();todo=[next(iter(adj))]
  while todo:
   q=todo.pop()
   if q in seen:continue
   seen.add(q);todo.extend(adj[q]-seen)
  assert len(seen)==len(adj)
 areas=np.linalg.norm(np.cross(ref[:,1]-ref[:,0],ref[:,2]-ref[:,0]),axis=1)/2;assert np.isfinite(areas).all() and np.min(areas)>0
 dims=np.ptp(v,axis=0);assert np.max(np.abs(dims-[150,86,102.80000305175781]))<1e-9
 volume=float(np.sum(np.einsum('ij,ij->i',ref[:,0],np.cross(ref[:,1],ref[:,2])))/6);assert volume>0
 w=lib3mf.get_wrapper();model=w.CreateModel();reader=model.QueryReader('3mf');reader.SetStrictModeActive(True);reader.ReadFromFile(str(p));assert reader.GetWarningCount()==0;mo=mesh(model);vg,fg=coords(mo);assert np.array_equal(vg[fg],ref) and mo.IsValid() and mo.IsManifoldAndOriented();g=group(model);ids=g.GetAllPropertyIDs()
 assert model.GetBuildItems().Count()==1
 for i,c in enumerate(pal):
  col=g.GetDisplayColor(ids[i]);assert g.GetName(ids[i])==c['id'] and [col.Red,col.Green,col.Blue,col.Alpha]==[int(c['srgb'][k:k+2],16) for k in [1,3,5]]+[255]
 assert [g.GetName(t.PropertyIDs[0]) for t in mo.GetAllTriangleProperties()]==[pal[i]['id'] for i in colors]
 new=lib3mf.Color();new.Red=12;new.Green=34;new.Blue=56;new.Alpha=255;g.SetDisplayColor(ids[3],new)
 with tempfile.TemporaryDirectory() as td:
  q=Path(td)/'test-edit.3mf';writer=model.QueryWriter('3mf');prec=writer.GetDecimalPrecision();writer.WriteToFile(str(q));edited=w.CreateModel();rd=edited.QueryReader('3mf');rd.SetStrictModeActive(True);rd.ReadFromFile(str(q));assert rd.GetWarningCount()==0;g2=group(edited);ids2=g2.GetAllPropertyIDs();o=mesh(edited);ve,fe=coords(o);err=float(np.abs(ve[fe]-ref).max());assert err<1e-4
  assert o.IsManifoldAndOriented();zero=int(np.count_nonzero(np.linalg.norm(np.cross(ve[fe[:,1]]-ve[fe[:,0]],ve[fe[:,2]]-ve[fe[:,0]]),axis=1)==0));assert zero==0
  for i,c in enumerate(pal):
   co=g2.GetDisplayColor(ids2[i]);assert [co.Red,co.Green,co.Blue,co.Alpha]==([12,34,56,255] if i==3 else [int(c['srgb'][k:k+2],16) for k in [1,3,5]]+[255])
  assert [g2.GetName(t.PropertyIDs[0]) for t in o.GetAllTriangleProperties()]==[pal[i]['id'] for i in colors]
 original={n:hashlib.sha256((A/n).read_bytes()).hexdigest() for n in ['millennium-appearance.3mf','face-materials.json']}
 subprocess.run([sys.executable,str(A/'source/build_appearance.py')],capture_output=True,check=True);assert all(hashlib.sha256((A/n).read_bytes()).hexdigest()==h for n,h in original.items())
 d={'source_STL_sha256':hashlib.sha256(raw).hexdigest(),'appearance_3MF_sha256':original['millennium-appearance.3mf'],'mesh_count':1,'every_edge_two_opposed_faces':True,'vertex_links_single_cycles':True,'one_connected_surface_shell':True,'minimum_triangle_area_mm2':float(np.min(areas)),'dimensions_mm':dims.tolist(),'volume_mm3':volume,'geometry_difference_from_original_mm':0,'vertices':2668,'triangles':5340,'original_STL_f32_coordinates_triangle_order_exact':True,'brick_front_faces':len(brick),'dark_front_recess_faces':len(glass),'forward_terracotta_cap_faces':len(tiles),'front_only_color_boundary_verified':True,'named_material_count':len(pal),'color_limit':None,'material_properties_preserved':True,'lib3mf_version':list(w.GetLibraryVersion()),'lib3mf_strict_warnings':0,'lib3mf_mesh_valid_manifold_oriented':True,'SDK_single_material_edit_preserves_other_palette_and_face_assignments':True,'SDK_writer_decimal_precision':prec,'SDK_edited_coordinate_quantization_max_mm':err,'SDK_edited_zero_area_faces':zero,'edited_test_file_delivered':False,'deterministic_3MF_and_face_manifest_rebuild_identical':True,'closed_color_volumes':False,'printer_tool_mapping':None,'GUI_tested':False,'new_FFF_validation':False,'original_manufacturing_QA_recomputed':False}
 (A/'qa/exchange-validation.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps(d,ensure_ascii=False))
if __name__=='__main__':main()
