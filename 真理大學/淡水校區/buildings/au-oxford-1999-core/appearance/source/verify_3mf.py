"""Strict native lib3mf reopen, all-face mapping, and real native property edit test."""
from pathlib import Path
import argparse,tempfile,collections,lib3mf,zipfile,xml.etree.ElementTree as ET
import sys
sys.dont_write_bytecode=True
from common import *
p=argparse.ArgumentParser();p.add_argument('--stl',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();root=a.out;D=load(a.stl,root/'parameters.json',root/'palette.json');w=lib3mf.get_wrapper()
def read(path,edit=False):
 m=w.CreateModel();r=m.QueryReader('3mf');r.SetStrictModeActive(True);r.ReadFromFile(str(path));assert r.GetWarningCount()==0 and m.GetUnit()==lib3mf.ModelUnit.MilliMeter
 it=m.GetMeshObjects();objs=[]
 while it.MoveNext():objs.append(it.GetCurrentMeshObject())
 assert len(objs)==1;o=objs[0];v=[tuple(q.Coordinates)for q in o.GetVertices()];f=[tuple(q.Indices)for q in o.GetTriangleIndices()];ids=mapping(D['signatures'],[[v[j]for j in q]for q in f]);props=o.GetAllTriangleProperties()
 git=m.GetBaseMaterialGroups();groups=[]
 while git.MoveNext():groups.append(git.GetCurrentBaseMaterialGroup())
 assert len(groups)==1 and groups[0].GetCount()==4;g=groups[0];property_ids=list(g.GetAllPropertyIDs())
 for i,name in enumerate(ORDER):
  c=g.GetDisplayColor(property_ids[i]);expected=(31,83,127,255)if edit and i==1 else(*D['palette'][name]['srgb8'],255)
  assert tuple([c.Red,c.Green,c.Blue,c.Alpha])==expected and g.GetName(property_ids[i])==name
 for i,pr in zip(ids,props):assert list(pr.PropertyIDs)==[property_ids[D['materials'][i]]]*3 and pr.ResourceID==g.GetResourceID()
 bit=m.GetBuildItems();items=[]
 while bit.MoveNext():items.append(bit.GetCurrent())
 assert len(items)==1 and not items[0].HasObjectTransform()
 return m,g,{'strict_warnings':0,'triangles':len(f),'vertices':len(v),'mesh_objects':1,'base_materials':4,'all_face_oriented_float32_digest':GLOBAL,'all_original_faces_map_one_to_one':True,'all_material_properties_match':True,'exact_float32_coordinates':True,'units':'millimeter','build_item_transform':'identity'}
path=root/'au-oxford-1999-core-appearance.3mf';before=sha(path.read_bytes());m,g,r=read(path)
with tempfile.TemporaryDirectory(prefix='native-edit-')as tmp:
 # Demonstrate the third-party writer limitation, then reject its changed geometry.
 rt=Path(tmp)/'writer-roundtrip.3mf';wr=m.QueryWriter('3mf');wr.SetDecimalPrecision(15);wr.WriteToFile(str(rt))
 changed=w.CreateModel();changed.QueryReader('3mf').ReadFromFile(str(rt));it=changed.GetMeshObjects();it.MoveNext();vv=[tuple(q.Coordinates)for q in it.GetCurrentMeshObject().GetVertices()]
 n_changed=sum(struct.pack('<3f',*x)!=struct.pack('<3f',*y)for x,y in zip(D['vertices'],vv));max_error=max(abs(x-y)for q,t in zip(D['vertices'],vv)for x,y in zip(q,t))
 assert n_changed>0
 try:read(rt)
 except AssertionError:pass
 else:raise AssertionError('Writer drift was not rejected')
 # Perform the real native lib3mf property edit, then serialize that property without its lossy geometry writer.
 edit_color=lib3mf.Color();edit_color.Red=31;edit_color.Green=83;edit_color.Blue=127;edit_color.Alpha=255
 g.SetDisplayColor(list(g.GetAllPropertyIDs())[1],edit_color)
 native_color=g.GetDisplayColor(list(g.GetAllPropertyIDs())[1]);native_hex=f'#{native_color.Red:02X}{native_color.Green:02X}{native_color.Blue:02X}{native_color.Alpha:02X}'
 assert native_hex=='#1F537FFF'
 # Actual editable standard-3MF base-material operation: change only its color attribute.
 # Keep all mesh XML bytes untouched; strict native lib3mf reopen checks the edited property.
 e=Path(tmp)/'material-edit.3mf'
 with zipfile.ZipFile(path)as zin,zipfile.ZipFile(e,'w',compression=zipfile.ZIP_DEFLATED)as zout:
  for info in zin.infolist():
   raw=zin.read(info.filename)
   if info.filename=='3D/3dmodel.model':
    old=('name="brick_family" displaycolor="'+D['palette']['brick_family']['hex']+'FF"').encode();new=('name="brick_family" displaycolor="'+native_hex+'"').encode();assert raw.count(old)==1;raw=raw.replace(old,new)
   zout.writestr(info,raw)
 read(e,True)
assert sha(path.read_bytes())==before
r.update({'lib3mf_version':list(w.GetLibraryVersion()),'native_lib3mf_material_setter_used':True,'actual_standard_3mf_base_material_edit_saved_strict_reopened':True,'edit_kept_all_face_assignments_and_geometry_exact':True,'original_file_unchanged':True,'native_library_writer_limitation':{'writer':'lib3mf 2.5.0 at decimal precision 15','changed_float32_vertices':n_changed,'max_coordinate_drift_mm':max_error,'exact_geometry_gate_rejects_writer_roundtrip':True,'writer_not_used_for_deliverable':True},'edit_method':'Use lib3mf SetDisplayColor, read the changed native property, and serialize only that base material displaycolor attribute in the standard 3MF XML part; preserve all vertex/triangle lexemes; strict native lib3mf reopen verifies exact geometry and actual changed material property. No alternate geometry repair.'})
dump(root/'qa/3mf-validation.json',r);print(json.dumps(r))
