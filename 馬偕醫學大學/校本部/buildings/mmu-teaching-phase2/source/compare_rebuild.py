#!/usr/bin/env python3
"""Exact geometry/material/STL and all nine rendered PNG byte/pixel comparisons."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('reference',type=Path);p.add_argument('rebuilt',type=Path);p.add_argument('--report',type=Path,required=True);a=p.parse_args();A=np.load(a.reference/'mesh-data.npz');B=np.load(a.rebuilt/'mesh-data.npz');arrays={k:bool(np.array_equal(A[k],B[k]))for k in('vertices','faces','materials')};stl=(a.reference/'model.stl').read_bytes()==(a.rebuilt/'model.stl').read_bytes();views=['front','oblique','right','left','rear','top','road-side','rear-g','aerial'];images=[]
for name in views:
 p=a.reference/'previews'/f'{name}.png';q=a.rebuilt/'previews'/f'{name}.png';byte=p.read_bytes()==q.read_bytes();pixel=np.array_equal(np.array(Image.open(p).convert('RGBA')),np.array(Image.open(q).convert('RGBA')));images.append({'view':name,'bytes_identical':byte,'pixels_identical':pixel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
r={'fresh_process_public_numeric_inputs_only':True,'arrays_exact':arrays,'stl_bytes_identical':stl,'pngs':images,'all_pass':all(arrays.values())and stl and all(x['bytes_identical']and x['pixels_identical']for x in images)};a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));assert r['all_pass']
