#!/usr/bin/env python3
"""True per-triangle base-material 3MF; strict readback and material round trip.
Python 3 + numpy + lib3mf 2.5.0. --out is created if missing.
"""
from pathlib import Path
import argparse,json,tempfile,zipfile,xml.etree.ElementTree as ET
import numpy as np,lib3mf
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]);a=ap.parse_args();root=a.out;root.mkdir(parents=True,exist_ok=True);(root/'qa').mkdir(exist_ok=True)
d=np.load(root/'mesh-data.npz');palette=json.loads((root/'face-materials.json').read_text())['palette'];w=lib3mf.get_wrapper();m=w.CreateModel();m.SetUnit(lib3mf.ModelUnit.MilliMeter);g=m.AddBaseMaterialGroup();pids=[]
for p in palette:
 c=lib3mf.Color();c.Red,c.Green,c.Blue=[int(p['hex'][i:i+2],16) for i in (1,3,5)];c.Alpha=255;pids.append(g.AddMaterial(p['id'],c))
o=m.AddMeshObject();o.SetName('FGU Huaien Hall - original mesh with bounded appearance')
vs=[];fs=[];ps=[]
for v in d['vertices']:
 q=lib3mf.Position();q.Coordinates[:]=[float(x) for x in v];vs.append(q)
for f,mi in zip(d['faces'],d['materials']):
 q=lib3mf.Triangle();q.Indices[:]=[int(x) for x in f];fs.append(q)
 q=lib3mf.TriangleProperties();q.ResourceID=g.GetResourceID();q.PropertyIDs[:]=[pids[int(mi)]]*3;ps.append(q)
o.SetGeometry(vs,fs);o.SetAllTriangleProperties(ps);t=lib3mf.Transform();t.Fields[0][0]=t.Fields[1][1]=t.Fields[2][2]=1;m.AddBuildItem(o,t)
writer=m.QueryWriter('3mf');target=root/'fgu-huaien-hall-materials.3mf';writer.WriteToFile(str(target))
# lib3mf 2.5's decimal formatter is not float32-exact. Encode the original
# float32 values as exact round-trip decimal literals in the delivered XML.
# Geometry/material structure is untouched; strict lib3mf then checks the file.
with zipfile.ZipFile(target) as z:entries={n:z.read(n) for n in z.namelist()}
core='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',core)
xml=ET.fromstring(entries['3D/3dmodel.model']);verts=xml.findall('.//{'+core+'}vertex');assert len(verts)==len(d['vertices'])
for el,v in zip(verts,d['vertices']):
 for axis,value in zip(('x','y','z'),v):el.set(axis,repr(float(value)))
for el in xml.iter():
 for key in list(el.attrib):
  if key.endswith('}UUID'):del el.attrib[key]
entries['3D/3dmodel.model']=ET.tostring(xml,encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name,data in sorted(entries.items()):
  zi=zipfile.ZipInfo(name,(2026,10,24,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=0o644<<16;z.writestr(zi,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
def read(path,edited=False,require_exact=False):
 n=w.CreateModel();r=n.QueryReader('3mf');r.SetStrictModeActive(True);r.ReadFromFile(str(path));assert r.GetWarningCount()==0
 it=n.GetMeshObjects();assert it.MoveNext();ob=it.GetCurrentMeshObject();assert not it.MoveNext();assert ob.IsValid();vi=np.array([list(q.Coordinates) for q in ob.GetVertices()],dtype=np.float32);fi=np.array([list(q.Indices) for q in ob.GetTriangleIndices()]);delta=float(np.max(np.abs(vi-d['vertices'])));assert delta<8e-6;assert np.array_equal(fi,d['faces'])
 if require_exact:assert np.array_equal(vi,d['vertices'])
 bi=n.GetBuildItems();assert bi.MoveNext();assert not bi.MoveNext()
 it=n.GetBaseMaterialGroups();assert it.MoveNext();group=it.GetCurrentBaseMaterialGroup();assert not it.MoveNext();assert group.GetCount()==len(palette);ids=group.GetAllPropertyIDs();props=ob.GetAllTriangleProperties()
 for q,mi in zip(props,d['materials']):
  assert q.ResourceID==group.GetResourceID();assert len(set(q.PropertyIDs))==1;assert q.PropertyIDs[0]==ids[int(mi)]
 for i,p in enumerate(palette):
  c=group.GetDisplayColor(ids[i]);expect=[int(p['hex'][j:j+2],16) for j in (1,3,5)]+[255]
  if edited and i==1:expect[0]=(expect[0]+3)%256
  assert [c.Red,c.Green,c.Blue,c.Alpha]==expect;assert group.GetName(ids[i])==p['id']
 return n,group,{'strict_warnings':int(r.GetWarningCount()),'valid_object':True,'mesh_objects':1,'build_items':1,'vertices':len(vi),'triangles':len(fi),'float32_coordinates_exact':bool(np.array_equal(vi,d['vertices'])),'coordinate_max_abs_difference_mm':delta,'roundtrip_tolerance_mm':8e-6,'triangle_order_indices_exact':True,'per_triangle_materials_exact':True,'palette_colors_exact':True}
n,group,qa=read(root/'fgu-huaien-hall-materials.3mf',require_exact=True)
with tempfile.TemporaryDirectory() as td:
 path=Path(td)/'roundtrip.3mf';wr=n.QueryWriter('3mf');wr.WriteToFile(str(path));_,_,qa['roundtrip']=read(path)
 ids=group.GetAllPropertyIDs();c=group.GetDisplayColor(ids[1]);c.Red=(c.Red+3)%256;group.SetDisplayColor(ids[1],c);wr.WriteToFile(str(path));_,_,qa['material_edit_save_reopen']=read(path,True)
qa['lib3mf_version']=list(w.GetLibraryVersion());qa['actual_slicer_or_print_test']=False;(root/'qa'/'3mf-strict-roundtrip.json').write_text(json.dumps(qa,indent=2)+'\n');print(json.dumps(qa,indent=2))
