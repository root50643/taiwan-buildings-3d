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
 raw=(R/'model.stl').read_bytes();assert hashlib.sha256(raw).hexdigest()=='f00727291f2ad83bf84b95f260ab252fa5089c47b2a0d52b6fd8ee97d038382e'
 n=struct.unpack_from('<I',raw,80)[0];assert n==2448 and len(raw)==84+n*50;ref=np.array([struct.unpack_from('<9f',raw,96+50*i) for i in range(n)]).reshape(n,3,3)
 p=A/'huayu-appearance.3mf';pal=json.loads((A/'palette.json').read_text())['materials'];fm=json.loads((A/'face-materials.json').read_text());colors=fm['face_material_indices']
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None and set(z.namelist())=={'[Content_Types].xml','_rels/.rels','3D/3dmodel.model'};r=E.fromstring(z.read('3D/3dmodel.model'))
 assert r.get('unit')=='millimeter';ob=r.find('m:resources/m:object',NS);me=ob.find('m:mesh',NS);v=np.array([[float(t.get(k)) for k in 'xyz'] for t in me.findall('m:vertices/m:vertex',NS)]);ts=me.findall('m:triangles/m:triangle',NS);f=np.array([[int(t.get(k)) for k in ['v1','v2','v3']] for t in ts]);reference_surface=ref;ref=v[f];assert len(f)==3008 and len(v)==1476
 assert all(t.get('pid')=='20' and t.get('p1')==t.get('p2')==t.get('p3')==str(c) for t,c in zip(ts,colors))
 assert [(x.get('name'),x.get('displaycolor')) for x in r.findall('m:resources/m:basematerials/m:base',NS)]==[(c['id'],c['srgb']+'FF') for c in pal]
 w=lib3mf.get_wrapper();model=w.CreateModel();reader=model.QueryReader('3mf');reader.SetStrictModeActive(True);reader.ReadFromFile(str(p));assert reader.GetWarningCount()==0;mo=mesh(model);vg,fg=coords(mo);import_error=float(np.abs(vg[fg]-ref).max());assert import_error<1e-5 and mo.IsValid() and mo.IsManifoldAndOriented();g=group(model);ids=g.GetAllPropertyIDs()
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
 d={'source_STL_sha256':hashlib.sha256(raw).hexdigest(),'appearance_3MF_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mesh_count':1,'vertices':1476,'triangles':3008,'original_STL_f32_coordinates_triangle_order_exact':False,'original_STL_bitwise_unchanged':True,'surface_subdivision_verified_separately':True,'SDK_import_coordinate_rounding_max_mm':import_error,'named_material_count':len(pal),'color_limit':None,'material_properties_preserved':True,'lib3mf_version':list(w.GetLibraryVersion()),'lib3mf_strict_warnings':0,'lib3mf_mesh_valid_manifold_oriented':True,'SDK_single_material_edit_preserves_other_palette_and_face_assignments':True,'SDK_writer_decimal_precision':prec,'SDK_edited_coordinate_quantization_max_mm':err,'SDK_edited_zero_area_faces':zero,'edited_test_file_delivered':False,'closed_color_volumes':False,'printer_tool_mapping':None,'GUI_tested':False,'new_FFF_validation':False,'original_manufacturing_QA_recomputed':False}
 (A/'qa/exchange-validation.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps(d,ensure_ascii=False))
if __name__=='__main__':main()
