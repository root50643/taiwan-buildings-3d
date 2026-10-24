#!/usr/bin/env python3
"""Compare fresh script-only build; binary Blend/ZIP timestamps are not geometry."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--original',type=Path,required=True);p.add_argument('--fresh',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
D=np.load(a.original/'mesh-data.npz');E=np.load(a.fresh/'mesh-data.npz')
arrays={k:bool(np.array_equal(D[k],E[k])) for k in D.files};assert all(arrays.values())
stl=(a.original/'model.stl').read_bytes()==(a.fresh/'model.stl').read_bytes();assert stl
views=[]
for old in sorted((a.original/'previews').glob('*.png')):
 new=a.fresh/'previews'/old.name;x=np.array(Image.open(old));y=np.array(Image.open(new));assert np.array_equal(x,y),old.name;assert old.read_bytes()==new.read_bytes(),old.name
 views.append({'view':old.stem,'pixel_exact':True,'png_byte_exact':old.read_bytes()==new.read_bytes(),'sha256':hashlib.sha256(new.read_bytes()).hexdigest()})
for report in ['geometry-validation.json','3mf-validation.json','blend-validation.json','self-intersection-validation.json']:
 assert (a.fresh/'qa'/report).exists()
a.report.write_text(json.dumps({'authoritative_mesh_data_sha256':hashlib.sha256((a.original/'mesh-data.npz').read_bytes()).hexdigest(),'geometry_vertices':len(D['vertices']),'geometry_triangles':len(D['faces']),'input_contract':'Only source/*.py, parameters.json and palette.json copied to a clean input folder; output directory was absent; no STL/NPZ/Blend/3MF or images supplied.','authoritative_arrays_exact':arrays,'stl_bytes_exact':stl,'views':views,'actual_model_reexport_render_and_edit_reopen_rerun':True,'blend_binary_hash_not_used':'Saved-file bookkeeping differs; reopened vertex/face/material equality and full buffer audit used instead.','three_mf_binary_hash_not_used':'ZIP metadata may vary; strict geometry/material readback and roundtrip drift used instead.'},indent=2)+'\n')
