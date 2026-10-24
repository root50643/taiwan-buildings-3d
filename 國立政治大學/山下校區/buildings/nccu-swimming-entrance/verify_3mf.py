#!/usr/bin/env python3
"""Strict lib3mf 2.5 readback and a genuine material edit/save/reopen test.
Run with system Python containing lib3mf and numpy. Temporary edited models are
not release artifacts. lib3mf property IDs are not assumed to be zero based.
"""
from pathlib import Path
import argparse,tempfile,json,hashlib
import lib3mf,numpy as np
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,default=Path(__file__).parent);ap.add_argument('--output',type=Path);args=ap.parse_args();root=args.input;out=args.output or root/'qa';out.mkdir(parents=True,exist_ok=True)
d=json.loads((root/'mesh.json').read_text());w=lib3mf.Wrapper()
def read(path):
 m=w.CreateModel();r=m.QueryReader('3mf');r.SetStrictModeActive(True);r.ReadFromFile(str(path));it=m.GetMeshObjects();assert it.MoveNext();o=it.GetCurrentMeshObject();assert not it.MoveNext();v=np.array([list(q.Coordinates)for q in o.GetVertices()]);f=np.array([list(q.Indices)for q in o.GetTriangleIndices()]);g=m.GetBaseMaterialGroupByID(1);ids=g.GetAllPropertyIDs();colors=[[getattr(g.GetDisplayColor(i),x)for x in ['Red','Green','Blue','Alpha']]for i in ids];names=[g.GetName(i)for i in ids];mi=[]
 for j in range(len(f)):
  p=o.GetTriangleProperties(j);assert p.ResourceID==1 and len(set(p.PropertyIDs))==1;mi.append(ids.index(p.PropertyIDs[0]))
 build=m.GetBuildItems();count=0
 while build.MoveNext():count+=1
 assert count==1
 return m,r,o,v,f,np.array(mi),colors,names
m,r,o,v,f,mi,colors,names=read(root/'model.3mf');expectc=[[int(c['hex'][i:i+2],16)for i in [1,3,5]]+[255]for c in d['palette']];delta=float(np.max(abs(v-np.array(d['vertices']))))
qa={'library_version':list(w.GetLibraryVersion()),'strict_mode':True,'strict_warning_count':r.GetWarningCount(),'object_valid':o.IsValid(),'mesh_objects':1,'build_items':1,'vertices':len(v),'triangles':len(f),'geometry_max_float32_readback_delta_mm':delta,'triangle_indices_exact':bool(np.array_equal(f,d['faces'])),'per_triangle_materials_exact':bool(np.array_equal(mi,d['material_indices'])),'colors_exact':colors==expectc,'names_exact':names==[c['name']for c in d['palette']]}
assert r.GetWarningCount()==0 and o.IsValid() and delta<8e-6 and all(qa[k]for k in ['triangle_indices_exact','per_triangle_materials_exact','colors_exact','names_exact']),qa
with tempfile.TemporaryDirectory() as td:
 g=m.GetBaseMaterialGroupByID(1);pid=g.GetAllPropertyIDs()[1];color=g.GetDisplayColor(pid);old=color.Red;color.Red=(old+3)%256;g.SetDisplayColor(pid,color);fp=Path(td)/'material-edit.3mf';m.QueryWriter('3mf').WriteToFile(str(fp));m2,r2,o2,v2,f2,mi2,c2,n2=read(fp)
 qa['edit_save_reopen']={'strict_warning_count':r2.GetWarningCount(),'object_valid':o2.IsValid(),'geometry_max_delta_mm':float(np.max(abs(v-v2))),'triangle_indices_exact':bool(np.array_equal(f,f2)),'material_assignments_exact':bool(np.array_equal(mi,mi2)),'color_edit_persisted':c2[1][0]==(old+3)%256,'default_writer_precision':m.QueryWriter('3mf').GetDecimalPrecision()}
 assert r2.GetWarningCount()==0 and o2.IsValid() and np.max(abs(v-v2))<8e-6 and np.array_equal(f,f2) and np.array_equal(mi,mi2) and c2[1][0]==(old+3)%256
 (out/'3mf-readback-mesh.json').write_text(json.dumps({'vertices':v.tolist(),'faces':f.tolist(),'material_indices':mi.tolist()},separators=(',',':'))+'\n')
 (out/'3mf-edited-readback-mesh.json').write_text(json.dumps({'vertices':v2.tolist(),'faces':f2.tolist(),'material_indices':mi2.tolist()},separators=(',',':'))+'\n')
(out/'3mf-strict-roundtrip.json').write_text(json.dumps(qa,indent=2)+'\n');print(json.dumps(qa,indent=2))
