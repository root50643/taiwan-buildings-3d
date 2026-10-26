#!/usr/bin/env python3
"""Independent direct binary-STL baseline versus delivered arrays; no material helper import."""
from pathlib import Path
import argparse,struct,hashlib,json
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=a.out
baseline=json.loads((r/'baseline-identity.json').read_text());mapping=baseline['selected_public_mapping_entries'];pairs={'model.stl':'model.stl','build_model.py':'build_model.py','legacy-render_preview.py':'render_preview.py','legacy-sources.md':'sources.md'}
checks={n:hashlib.sha256((r/n).read_bytes()).hexdigest()==mapping[old] for n,old in pairs.items()};assert all(checks.values())
b=(r/'model.stl').read_bytes();count=struct.unpack_from('<I',b,80)[0];assert count==3618 and len(b)==180984
tri=np.asarray([struct.unpack_from('<9f',b,84+i*50+12)for i in range(count)],np.float32).reshape(-1,3,3);d=np.load(r/'mesh-data.npz');actual=d['vertices'][d['faces']];assert np.array_equal(tri,actual);assert np.array_equal(d['original_triangle_index'],np.arange(count))
mask=json.loads((r/'face-material-map.json').read_text());expected=np.zeros(count,np.int32);ids={'plaster':1,'roof':2,'brick':3}
for g in mask['groups'].values():
 for f in g['faces']:expected[f['stl_face_index_0based']]=ids[g['palette_key']]
assert np.array_equal(expected,d['materials']);assert np.count_nonzero(expected)==158;assert np.bincount(expected,minlength=4).tolist()==[3460,14,2,142]
report={'all_pass':True,'method':'Separate direct struct binary-STL parser and retained public four-file hash mapping; no material_geometry helper import.','four_baseline_files_match_public_mapping':checks,'full_vertex_coordinates_face_order_and_winding_exact':True,'source_face_indices_exact':True,'per_face_material_indices_exact':True,'materials':[3460,14,2,142],'geometry_changed':False,'new_building_count':0,'baseline_scene_materials_not_claimed_known':True}
(r/'qa/baseline-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
