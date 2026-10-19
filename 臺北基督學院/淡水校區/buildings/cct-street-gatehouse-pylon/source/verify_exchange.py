"""Independent XML/raw-STL/installed lib3mf strict-import and editable-palette checks.
No mesh repair, slicing, physical-print test or printer-tool mapping.
"""
from pathlib import Path
import collections,hashlib,json,struct,subprocess,sys,tempfile,zipfile,xml.etree.ElementTree as E
import numpy as np
import lib3mf
R=Path(__file__).resolve().parents[1];NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def stl(p):
 b=p.read_bytes();n=struct.unpack_from('<I',b,80)[0];assert len(b)==84+50*n
 return np.array([struct.unpack_from('<9f',b,96+50*i) for i in range(n)]).reshape(n,3,3)
def meshobs(m):
 it=m.GetMeshObjects();r={}
 while it.MoveNext():
  o=it.GetCurrentMeshObject();r[o.GetName()]=o
 return r
def group(m):
 it=m.GetBaseMaterialGroups();assert it.Count()==1 and it.MoveNext();return it.GetCurrentBaseMaterialGroup()
def coords(o):
 v=np.array([list(x.Coordinates) for x in o.GetVertices()]);f=np.array([list(x.Indices) for x in o.GetTriangleIndices()]);return v,f

def main():
 d=json.loads((R/'geometry.json').read_text());ps={p['id']:p for p in d['parts']};palette=d['materials'];ref={n:stl(R/p['stl']) for n,p in ps.items()};w=lib3mf.get_wrapper();records=[];master=None
 paths=sorted((R/'appearance').rglob('*.3mf'));assert len(paths)==5
 for path in paths:
  with zipfile.ZipFile(path) as z:
   assert z.testzip() is None and set(z.namelist())=={'[Content_Types].xml','_rels/.rels','3D/3dmodel.model'};root=E.fromstring(z.read('3D/3dmodel.model'))
  assert root.get('unit')=='millimeter'
  assert [(x.get('name'),x.get('displaycolor')) for x in root.findall('m:resources/m:basematerials/m:base',NS)]==[(p['id'],p['srgb']+'FF') for p in palette]
  obs={int(o.get('id')):o for o in root.findall('m:resources/m:object',NS)};counts={}
  for o in obs.values():
   me=o.find('m:mesh',NS)
   if me is None:continue
   name=o.get('name');p=ps[name];v=np.array([[float(q.get(k)) for k in 'xyz'] for q in me.findall('m:vertices/m:vertex',NS)]);ts=me.findall('m:triangles/m:triangle',NS);f=np.array([[int(t.get(k)) for k in ['v1','v2','v3']] for t in ts]);assert np.array_equal(v[f],ref[name]);assert np.array_equal(v,np.asarray(p['vertices'])) and np.array_equal(f,np.asarray(p['triangles']))
   assert all(t.get('pid')=='20' and t.get('p1')==t.get('p2')==t.get('p3')==str(c) for t,c in zip(ts,p['material_indices']))
   counts[name]=dict(collections.Counter(palette[i]['id'] for i in p['material_indices']))
  model=w.CreateModel();reader=model.QueryReader('3mf');reader.SetStrictModeActive(True);reader.ReadFromFile(str(path));assert reader.GetWarningCount()==0
  g=group(model);ids=g.GetAllPropertyIDs();assert [g.GetName(i) for i in ids]==[p['id'] for p in palette]
  for i,p in zip(ids,palette):
   c=g.GetDisplayColor(i);assert [c.Red,c.Green,c.Blue,c.Alpha]==[int(p['srgb'][k:k+2],16) for k in [1,3,5]]+[255]
  imported=meshobs(model);assert set(imported)==set(counts)
  for name,o in imported.items():
   v,f=coords(o);assert np.array_equal(v[f],ref[name]);assert o.IsValid() and o.IsManifoldAndOriented();props=o.GetAllTriangleProperties();assert len(props)==len(ps[name]['triangles'])
   assert all(t.ResourceID==g.GetResourceID() and len(set(t.PropertyIDs))==1 and g.GetName(t.PropertyIDs[0])==palette[k]['id'] for t,k in zip(props,ps[name]['material_indices']))
  rec={'path':str(path.relative_to(R)),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'raw_STL_mesh_coordinates_and_triangle_order_exact':True,'lib3mf_strict_warnings':0,'all_meshes_valid_manifold_oriented':True,'named_materials_and_face_assignments_exact':True,'material_face_counts':counts}
  assert model.GetBuildItems().Count()==1
  if 100 in obs:
   cs=obs[100].findall('m:components/m:component',NS);assert len(cs)==4;world=[]
   for c,p in zip(cs,d['parts']):
    assert obs[int(c.get('objectid'))].get('name')==p['id'];T=np.array([float(x) for x in c.get('transform').split()]).reshape(4,3).T;assert np.array_equal(T,np.asarray(p['assembly_transform'])[:3,:]);world.append(np.asarray(p['vertices'])@T[:3,:3].T+T[:3,3])
   world=np.concatenate(world);rec['assembly_transforms_XML_exact']=True;rec['assembled_dimensions_mm']=np.ptp(world,axis=0).tolist();assert np.max(np.abs(np.ptp(world,axis=0)-d['assembled_dimensions_mm']))<1e-12;master=model
  else:
   p=ps[next(iter(imported))];assert np.array_equal(np.asarray(p['vertices']).min(axis=0),[0,0,0]);rec['native_minXYZ_zero']=True
  records.append(rec)
 # Actual editable material round trip; SDK's default decimal writer may quantize coordinates.
 g=group(master);ids=g.GetAllPropertyIDs();col=lib3mf.Color();col.Red=12;col.Green=34;col.Blue=56;col.Alpha=255;g.SetDisplayColor(ids[4],col);errors={};edited_zero_areas={}
 with tempfile.TemporaryDirectory() as td:
  p=Path(td)/'edited.3mf';writer=master.QueryWriter('3mf');precision=writer.GetDecimalPrecision();writer.WriteToFile(str(p));m=w.CreateModel();r=m.QueryReader('3mf');r.SetStrictModeActive(True);r.ReadFromFile(str(p));assert r.GetWarningCount()==0;g2=group(m)
  for k,i in enumerate(g2.GetAllPropertyIDs()):
   c=g2.GetDisplayColor(i);assert [c.Red,c.Green,c.Blue,c.Alpha]==([12,34,56,255] if k==4 else [int(palette[k]['srgb'][j:j+2],16) for j in [1,3,5]]+[255])
  for n,o in meshobs(m).items():
   v,f=coords(o);errors[n]=float(np.max(np.abs(v[f]-ref[n])));assert errors[n]<1e-4
   edited_zero_areas[n]=int(np.count_nonzero(np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)==0));assert edited_zero_areas[n]==0 and o.IsManifoldAndOriented()
   assert [g2.GetName(t.PropertyIDs[0]) for t in o.GetAllTriangleProperties()]==[palette[k]['id'] for k in ps[n]['material_indices']]
 # Recreate delivered files, then verify their exact bytes against initial digests.
 initial={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths};subprocess.run([sys.executable,str(R/'source/build_exchange.py')],check=True,capture_output=True);assert all(hashlib.sha256(p.read_bytes()).hexdigest()==h for p,h in initial.items())
 report={'lib3mf_version':list(w.GetLibraryVersion()),'files':records,'material_count':len(palette),'color_limit':None,'deterministic_3MF_rebuild_SHA_identical':True,'SDK_single_material_edit_preserves_other_palette_and_face_assignments':True,'SDK_writer_decimal_precision':precision,'SDK_edited_roundtrip_coordinate_quantization_mm':errors,'SDK_edited_roundtrip_zero_area_triangles':edited_zero_areas,'SDK_edited_roundtrip_delivered':False,'closed_color_volumes_created':False,'printer_tool_mapping':None,'GUI_import_tested':False,'physical_print_or_fit_verified':False,'scope':'General appearance exchange; assembled master is not a print layout. Native parts still require manufacturing/slicer checks.'}
 (R/'qa/exchange-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='files'},ensure_ascii=False))
if __name__=='__main__':main()
