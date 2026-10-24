#!/usr/bin/env python3
"""Build real per-triangle base-material 3MF with lib3mf 2.5.0. Use system Python."""
import pathlib,json,argparse,hashlib
import numpy as np
import lib3mf
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args();root=a.out;(root/'qa').mkdir(parents=True,exist_ok=True)
D=np.load(root/'mesh-data.npz');palette=json.loads((root/'palette.json').read_text())
w=lib3mf.get_wrapper();model=w.CreateModel();model.SetUnit(lib3mf.ModelUnit.MilliMeter)
group=model.AddBaseMaterialGroup();pid=[]
for d in palette:
 h=d['hex'].strip('#');c=lib3mf.Color();c.Red=int(h[0:2],16);c.Green=int(h[2:4],16);c.Blue=int(h[4:6],16);c.Alpha=255;pid.append(group.AddMaterial(d['name'],c))
o=model.AddMeshObject();o.SetName('NTIN Xin-Xin — bounded historical appearance')
verts=[];tris=[];props=[]
for v in D['vertices']:
 q=lib3mf.Position();q.Coordinates[:]=[float(x) for x in v];verts.append(q)
for f,mi in zip(D['faces'],D['materials']):
 q=lib3mf.Triangle();q.Indices[:]=[int(x) for x in f];tris.append(q)
 q=lib3mf.TriangleProperties();q.ResourceID=group.GetResourceID();q.PropertyIDs[:]=[pid[int(mi)]]*3;props.append(q)
o.SetGeometry(verts,tris);o.SetAllTriangleProperties(props)
t=lib3mf.Transform();t.Fields[0][0]=t.Fields[1][1]=t.Fields[2][2]=1;model.AddBuildItem(o,t)
model.QueryWriter('3mf').WriteToFile(str(root/'ntin-xinxin-appearance.3mf'))
# Strict read and round trip, with geometry + actual material property checks.
def read(path):
 m=w.CreateModel();r=m.QueryReader('3mf');r.SetStrictModeActive(True);r.ReadFromFile(str(path));assert r.GetWarningCount()==0
 it=m.GetMeshObjects();objs=[]
 while it.MoveNext():objs.append(it.GetCurrentMeshObject())
 assert len(objs)==1
 ob=objs[0];vs=np.array([list(x.Coordinates) for x in ob.GetVertices()]);fs=np.array([list(x.Indices) for x in ob.GetTriangleIndices()]);pr=ob.GetAllTriangleProperties();ids=[(int(x.ResourceID),list(x.PropertyIDs)) for x in pr]
 coordinate_error=float(np.max(np.abs(vs-D['vertices'])));assert coordinate_error<1e-5;assert np.array_equal(fs,D['faces'])
 groups=m.GetBaseMaterialGroups();gs=[]
 while groups.MoveNext():gs.append(groups.GetCurrentBaseMaterialGroup())
 assert len(gs)==1 and gs[0].GetCount()==len(palette)
 for q,mi in zip(pr,D['materials']):
  assert len(set(q.PropertyIDs))==1
  col=gs[0].GetDisplayColor(q.PropertyIDs[0]);actual=f'#{col.Red:02X}{col.Green:02X}{col.Blue:02X}';assert actual==palette[int(mi)]['hex'],(actual,mi)
 return m,{'strict':True,'warnings':int(r.GetWarningCount()),'mesh_objects':len(objs),'vertices':len(vs),'triangles':len(fs),'base_materials':len(palette),'all_triangle_materials_match_palette':True,'triangle_indices_exact_match':True,'vertex_max_abs_difference_mm':coordinate_error,'vertex_tolerance_mm':1e-5}
m,report=read(root/'ntin-xinxin-appearance.3mf')
def coordinates(model):
 it=model.GetMeshObjects();assert it.MoveNext();return np.array([list(v.Coordinates)for v in it.GetCurrentMeshObject().GetVertices()])
initial_coordinates=coordinates(m);tmp=root/'qa'/'roundtrip.3mf';m.QueryWriter('3mf').WriteToFile(str(tmp));again,rr=read(tmp);drift=float(np.max(np.abs(coordinates(again)-initial_coordinates)));assert drift==0;tmp.unlink()
report['additional_roundtrip_coordinate_drift_mm']=drift
report['roundtrip']=rr
# Actual base-material edit, write and strict reopen; original remains unchanged.
original_hash=hashlib.sha256((root/'ntin-xinxin-appearance.3mf').read_bytes()).hexdigest()
git=m.GetBaseMaterialGroups();assert git.MoveNext();gg=git.GetCurrentBaseMaterialGroup();edit=lib3mf.Color();edit.Red=31;edit.Green=83;edit.Blue=127;edit.Alpha=255;gg.SetDisplayColor(1,edit)
tmp=root/'qa'/'material-edit.3mf';m.QueryWriter('3mf').WriteToFile(str(tmp));edited=w.CreateModel();reader=edited.QueryReader('3mf');reader.SetStrictModeActive(True);reader.ReadFromFile(str(tmp));assert reader.GetWarningCount()==0
it=edited.GetBaseMaterialGroups();assert it.MoveNext();col=it.GetCurrentBaseMaterialGroup().GetDisplayColor(1);assert (col.Red,col.Green,col.Blue,col.Alpha)==(31,83,127,255)
obit=edited.GetMeshObjects();assert obit.MoveNext();edob=obit.GetCurrentMeshObject();assert np.array_equal(np.array([list(t.Indices)for t in edob.GetTriangleIndices()]),D['faces'])
assert np.max(np.abs(np.array([list(v.Coordinates)for v in edob.GetVertices()])-D['vertices']))<1e-5
assert all(list(q.PropertyIDs)==[pid[int(mi)]]*3 for q,mi in zip(edob.GetAllTriangleProperties(),D['materials']))
tmp.unlink();assert hashlib.sha256((root/'ntin-xinxin-appearance.3mf').read_bytes()).hexdigest()==original_hash
report['actual_material_edit_write_strict_reopen']=True;report['material_edit_preserved_face_assignments_and_geometry']=True;report['original_unchanged_after_edit_test']=True
report['lib3mf_version']=list(w.GetLibraryVersion());(root/'qa'/'3mf-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
