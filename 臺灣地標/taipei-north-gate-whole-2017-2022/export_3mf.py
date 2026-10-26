#!/usr/bin/env python3
"""Build real per-triangle base-material 3MF with lib3mf 2.5.0. Use system Python."""
import pathlib,json,argparse,hashlib,zipfile,re,io,xml.etree.ElementTree as ET
import numpy as np
import lib3mf
from mesh_topology import check_topology
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);a=p.parse_args();root=a.out;(root/'qa').mkdir(parents=True,exist_ok=True)
with np.load(root/'mesh-data.npz') as archive:D={k:archive[k].copy() for k in ['vertices','faces','materials']}
palette=json.loads((root/'editable-parts.json').read_text())['palette']
w=lib3mf.get_wrapper();model=w.CreateModel();model.SetUnit(lib3mf.ModelUnit.MilliMeter)
group=model.AddBaseMaterialGroup();pid=[]
for d in palette:
 h=d['hex'].strip('#');c=lib3mf.Color();c.Red=int(h[0:2],16);c.Green=int(h[2:4],16);c.Blue=int(h[4:6],16);c.Alpha=255;pid.append(group.AddMaterial(d['name'],c))
o=model.AddMeshObject();o.SetName('Taipei North Gate — source-bounded exterior approximation')
verts=[];tris=[];props=[]
for v in D['vertices']:
 q=lib3mf.Position();q.Coordinates[:]=[float(x) for x in v];verts.append(q)
for f,mi in zip(D['faces'],D['materials']):
 q=lib3mf.Triangle();q.Indices[:]=[int(x) for x in f];tris.append(q)
 q=lib3mf.TriangleProperties();q.ResourceID=group.GetResourceID();q.PropertyIDs[:]=[pid[int(mi)]]*3;props.append(q)
o.SetGeometry(verts,tris);o.SetAllTriangleProperties(props)
t=lib3mf.Transform();t.Fields[0][0]=t.Fields[1][1]=t.Fields[2][2]=1;model.AddBuildItem(o,t)
def exact_float32_vertex_serialization(path):
 # lib3mf 2.5.0 decimal writer multiplies float coordinates before formatting;
 # at precision 9 this can shift even exact 94.5 by one float32 ULP.
 # Bound that raw writer drift, then serialize the already-authored canonical
 # float32 coordinates with 9 significant digits. This is part of the exporter,
 # not a tolerance relaxation: the delivered/reloaded coordinates must be exact.
 raw=path.read_bytes();buf=io.BytesIO()
 with zipfile.ZipFile(io.BytesIO(raw))as zi,zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED)as zo:
  for item in zi.infolist():
   data=zi.read(item.filename)
   if item.filename=='3D/3dmodel.model':
    text=data.decode('utf-8');nodes=ET.fromstring(text).findall('.//{*}vertex');assert len(nodes)==len(D['vertices'])
    parsed=np.array([[float(n.attrib[k])for k in ['x','y','z']]for n in nodes]);delta=float(np.max(np.abs(parsed-D['vertices'])));assert delta<2e-5
    count=[0]
    def replace(match):
     v=D['vertices'][count[0]];count[0]+=1
     return '<vertex x="'+format(float(v[0]),'.9g')+'" y="'+format(float(v[1]),'.9g')+'" z="'+format(float(v[2]),'.9g')+'" />'
    text=re.sub(r'<vertex\s+[^>]+/>',replace,text);assert count[0]==len(nodes);data=text.encode('utf-8')
   zo.writestr(item,data)
 path.write_bytes(buf.getvalue());return delta
writer=model.QueryWriter('3mf');writer.SetDecimalPrecision(9);writer.WriteToFile(str(root/'taipei-north-gate-whole-2017-2022.3mf'));raw_writer_delta=exact_float32_vertex_serialization(root/'taipei-north-gate-whole-2017-2022.3mf')
# Strict read and round trip, with geometry + actual material property checks.
def read(path):
 m=w.CreateModel();r=m.QueryReader('3mf');r.SetStrictModeActive(True);r.ReadFromFile(str(path));assert r.GetWarningCount()==0
 it=m.GetMeshObjects();objs=[]
 while it.MoveNext():objs.append(it.GetCurrentMeshObject())
 assert len(objs)==1
 assert m.GetUnit()==lib3mf.ModelUnit.MilliMeter
 assert m.GetBuildItems().Count()==1
 ob=objs[0];vs=np.array([list(x.Coordinates) for x in ob.GetVertices()]);fs=np.array([list(x.Indices) for x in ob.GetTriangleIndices()]);pr=ob.GetAllTriangleProperties();ids=[(int(x.ResourceID),list(x.PropertyIDs)) for x in pr]
 coordinate_error=float(np.max(np.abs(vs-D['vertices'])));assert coordinate_error<2e-5;assert np.array_equal(fs,D['faces']);assert np.array_equal(vs.astype(np.float32),D['vertices'])
 groups=m.GetBaseMaterialGroups();gs=[]
 while groups.MoveNext():gs.append(groups.GetCurrentBaseMaterialGroup())
 assert len(gs)==1 and gs[0].GetCount()==len(palette)
 assert len(pr)==len(D['materials'])
 for q,mi in zip(pr,D['materials']):
  assert q.ResourceID==gs[0].GetResourceID()
  assert len(set(q.PropertyIDs))==1
  col=gs[0].GetDisplayColor(q.PropertyIDs[0]);actual=f'#{col.Red:02X}{col.Green:02X}{col.Blue:02X}';assert actual==palette[int(mi)]['hex'].upper(),(actual,mi)
 topology=check_topology(vs,fs,path.name);assert topology['all_pass'],topology
 return m,{'topology':topology,'strict':True,'warnings':int(r.GetWarningCount()),'mesh_objects':len(objs),'build_items':1,'model_units':'millimetre','all_triangle_property_resources_match_group':True,'vertices':len(vs),'triangles':len(fs),'base_materials':len(palette),'all_triangle_materials_match_palette':True,'triangle_indices_exact_match':True,'vertices_exact_after_float32_cast':True,'vertex_max_abs_difference_mm':coordinate_error,'vertex_tolerance_mm':2e-5}
m,report=read(root/'taipei-north-gate-whole-2017-2022.3mf');tmp=root/'qa'/'roundtrip.3mf';writer=m.QueryWriter('3mf');writer.SetDecimalPrecision(9);writer.WriteToFile(str(tmp));roundtrip_raw_writer_delta=exact_float32_vertex_serialization(tmp);_,rr=read(tmp);tmp.unlink()
report['raw_lib3mf_writer_max_abs_drift_mm']=raw_writer_delta;report['roundtrip_raw_writer_max_abs_drift_mm']=roundtrip_raw_writer_delta;report['export_serialization']='Canonical float32 vertices serialized with 9 significant digits after bounded lib3mf decimal-writer drift check; both strict reloaded models must match exactly.';report['roundtrip']=rr;report['lib3mf_version']=list(w.GetLibraryVersion());report['3mf_sha256']=hashlib.sha256((root/'taipei-north-gate-whole-2017-2022.3mf').read_bytes()).hexdigest();(root/'qa'/'3mf-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
