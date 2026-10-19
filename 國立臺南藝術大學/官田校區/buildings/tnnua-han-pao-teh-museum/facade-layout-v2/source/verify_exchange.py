"""Independent revised STL/XML/lib3mf strict import/edit and deterministic rebuild.
python facade-layout-v2/source/verify_exchange.py (installed numpy and lib3mf).
No new slicing/manufacturing claim. Original historical QA remains unchanged.
"""
from pathlib import Path
import json,hashlib,struct,zipfile,xml.etree.ElementTree as E,tempfile,subprocess,sys
import numpy as np,lib3mf
A=Path(__file__).resolve().parents[1];R=A;NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def mesh(m):
 it=m.GetMeshObjects();assert it.Count()==1 and it.MoveNext();return it.GetCurrentMeshObject()
def group(m):
 it=m.GetBaseMaterialGroups();assert it.Count()==1 and it.MoveNext();return it.GetCurrentBaseMaterialGroup()
def coords(o):
 v=np.array([list(x.Coordinates) for x in o.GetVertices()]);f=np.array([list(x.Indices) for x in o.GetTriangleIndices()]);return v,f
def main():
 raw=(R/'model-v2.stl').read_bytes()
 n=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+n*50;ref=np.array([struct.unpack_from('<9f',raw,96+50*i) for i in range(n)]).reshape(n,3,3)
 p=A/'model.3mf';pal=json.loads((A/'palette.json').read_text())['materials'];fm=json.loads((A/'face-materials.json').read_text());colors=fm['face_material_indices']
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None and set(z.namelist())=={'[Content_Types].xml','_rels/.rels','3D/3dmodel.model'};r=E.fromstring(z.read('3D/3dmodel.model'))
 assert r.get('unit')=='millimeter';ob=r.find('m:resources/m:object',NS);me=ob.find('m:mesh',NS);v=np.array([[float(t.get(k)) for k in 'xyz'] for t in me.findall('m:vertices/m:vertex',NS)]);ts=me.findall('m:triangles/m:triangle',NS);f=np.array([[int(t.get(k)) for k in ['v1','v2','v3']] for t in ts]);assert np.array_equal(v[f],ref)
 # Independently bound every red triangle to the observed exterior prism:
 # its oblique side plane or its exposed downward-facing bottom at z=60.
 red=ref[np.array(colors)==2];assert len(red)==8
 for tri in red:
  assert tri[:,1].max()<=-42+1e-5 and tri[:,2].min()>=60-1e-5 and tri[:,2].max()<=94+1e-5
  side=np.max(np.abs(17*(tri[:,0]+8)+21*(tri[:,1]+43)))<.003
  bottom=np.max(np.abs(tri[:,2]-60))<1e-5
  assert side or bottom
 assert all(t.get('pid')=='20' and t.get('p1')==t.get('p2')==t.get('p3')==str(c) for t,c in zip(ts,colors))
 assert [(x.get('name'),x.get('displaycolor')) for x in r.findall('m:resources/m:basematerials/m:base',NS)]==[(c['id'],c['srgb']+'FF') for c in pal]
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
 original={n:hashlib.sha256((A/n).read_bytes()).hexdigest() for n in ['model.3mf','face-materials.json']}
 subprocess.run([sys.executable,str(A/'source/build_appearance.py')],capture_output=True,check=True);assert all(hashlib.sha256((A/n).read_bytes()).hexdigest()==h for n,h in original.items())
 d={'source_STL_sha256':hashlib.sha256(raw).hexdigest(),'revised_3MF_sha256':original['model.3mf'],'mesh_count':1,'vertices':len(v),'triangles':n,'revised_STL_f32_coordinates_triangle_order_exact':True,'red_triangles_bounded_to_exterior_side_or_underside':len(red),'named_material_count':len(pal),'color_limit':None,'material_properties_preserved':True,'lib3mf_version':list(w.GetLibraryVersion()),'lib3mf_strict_warnings':0,'lib3mf_mesh_valid_manifold_oriented':True,'SDK_single_material_edit_preserves_other_palette_and_face_assignments':True,'SDK_writer_decimal_precision':prec,'SDK_edited_coordinate_quantization_max_mm':err,'SDK_edited_zero_area_faces':zero,'edited_test_file_delivered':False,'deterministic_3MF_and_face_manifest_rebuild_identical':True,'closed_color_volumes':False,'printer_tool_mapping':None,'GUI_tested':False,'new_FFF_validation':False,'original_manufacturing_QA_recomputed':False}
 (A/'qa/exchange-validation.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps(d,ensure_ascii=False))
if __name__=='__main__':main()
