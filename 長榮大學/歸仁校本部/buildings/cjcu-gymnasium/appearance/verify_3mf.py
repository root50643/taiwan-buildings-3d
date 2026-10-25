#!/usr/bin/env python3
"""Independent strict lib3mf reader only; never rewrite source coordinates."""
from pathlib import Path
import argparse,json,lib3mf,numpy as np
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent);a=p.parse_args();root=a.out;D=np.load(root/'mesh-data.npz');palette=json.loads((root/'palette.json').read_text())
w=lib3mf.get_wrapper();m=w.CreateModel();r=m.QueryReader('3mf');r.SetStrictModeActive(True);r.ReadFromFile(str(root/'cjcu-gymnasium-roof-illustration.3mf'));assert r.GetWarningCount()==0
it=m.GetMeshObjects();objs=[]
while it.MoveNext():objs.append(it.GetCurrentMeshObject())
assert len(objs)==1;o=objs[0];v=np.array([list(x.Coordinates) for x in o.GetVertices()],dtype='<f4');f=np.array([list(x.Indices) for x in o.GetTriangleIndices()],dtype=np.int32);pr=o.GetAllTriangleProperties();assert v.tobytes()==D['vertices'].tobytes() and f.tobytes()==D['faces'].tobytes()
groups=m.GetBaseMaterialGroups();gs=[]
while groups.MoveNext():gs.append(groups.GetCurrentBaseMaterialGroup())
assert len(gs)==1 and gs[0].GetCount()==2
for q,mi in zip(pr,D['materials']):
 assert len(set(q.PropertyIDs))==1 and q.ResourceID==gs[0].GetResourceID();col=gs[0].GetDisplayColor(q.PropertyIDs[0]);actual=f'#{col.Red:02X}{col.Green:02X}{col.Blue:02X}';assert actual==palette[int(mi)]['hex'] and col.Alpha==255
report={'strict_lib3mf_reader':True,'warnings':int(r.GetWarningCount()),'lib3mf_version':list(w.GetLibraryVersion()),'mesh_objects':1,'triangles':len(f),'vertices':len(v),'exact_original_float32_geometry_and_face_order':True,'zero_coordinate_tolerance_mm':0,'all_triangle_base_material_properties_exact':True,'opaque_materials':2,'writer_used':'direct deterministic core XML, preserving exact decimal float32 values; no library rewrite'}
(root/'qa'/'strict-3mf-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
