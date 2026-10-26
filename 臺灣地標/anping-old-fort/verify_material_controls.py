#!/usr/bin/env python3
import pathlib,json,numpy as np,tempfile,shutil,argparse
from material_geometry import load_stl,load_materials,bijection
parser=argparse.ArgumentParser();parser.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);args=parser.parse_args();root=args.out;t=load_stl(root/'model.stl')[2];rng=np.random.default_rng(20261026);order=rng.permutation(len(t));mapping=bijection(t,t[order]);assert np.array_equal(mapping,order);rows=[{'control':'All faces reordered, full identity mapping recovers source indices','passed':True}]
for name,change in [('Reversed face winding',lambda q:q.__setitem__(0,q[0,[0,2,1]])),('Moved vertex',lambda q:q.__setitem__((0,0,0),q[0,0,0]+.01)),('Duplicated face / lost bijection',lambda q:q.__setitem__(0,q[1]))]:
 q=t.copy();change(q)
 try:bijection(t,q)
 except(AssertionError,KeyError):rows.append({'control':name,'rejected_as_expected':True})
 else:raise AssertionError(name)
for group,replacement,label in [('tower_front_roof_slope',812,'Rejected rear groove'),('front_stair_risers_and_treads',213,'Held landing top'),('front_stair_risers_and_treads',216,'Held landing fascia'),('tower_front_outer_plaster',1216,'Unknown cabin skin')]:
 with tempfile.TemporaryDirectory()as tmp:
  p=pathlib.Path(tmp);a=json.loads((root/'face-material-map.json').read_text());a['groups'][group]['faces'][0]['stl_face_index_0based']=replacement;(p/'face-material-map.json').write_text(json.dumps(a));shutil.copyfile(root/'model.stl',p/'model.stl')
  try:load_materials(p)
  except AssertionError:rows.append({'control':label+' cannot substitute eligible triangle','rejected_as_expected':True})
  else:raise AssertionError('Excluded face not rejected')
(root/'qa/material-controls.json').write_text(json.dumps({'all_pass':True,'controls':rows},indent=2)+'\n');print(json.dumps(rows,indent=2))
