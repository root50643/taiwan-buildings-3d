"""Deliberate tampering in temporary files only; production inputs remain untouched."""
from pathlib import Path
import argparse,tempfile,copy
import sys
sys.dont_write_bytecode=True
from common import *
p=argparse.ArgumentParser();p.add_argument('--stl',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();root=a.out;D=load(a.stl,root/'parameters.json',root/'palette.json');tests={}
def reject(name,fn):
 try:fn()
 except (AssertionError,ValueError):tests[name]='REJECTED'
 else:raise AssertionError('Accepted tampering: '+name)
with tempfile.TemporaryDirectory(prefix='fail-closed-')as td:
 t=Path(td);pp=t/'parameters.json';cp=t/'palette.json';s=t/'model.stl'
 b=bytearray(a.stl.read_bytes());b[96]^=1;s.write_bytes(b);reject('changed_original_stl_bytes',lambda:load(s,root/'parameters.json',root/'palette.json'))
 for name,change in [('add_unlisted_face',lambda p:p['regions']['left_outer_brick_wall']['original_face_ids'].append(0)),('replace_face_id',lambda p:p['regions']['left_outer_brick_wall']['original_face_ids'].__setitem__(0,0)),('changed_face_fingerprint',lambda p:p['regions']['left_outer_brick_wall']['oriented_vertex_sha256_by_face_id'].__setitem__('104','0'*64))]:
  p=copy.deepcopy(D['parameters']);change(p);dump(pp,p);reject(name,lambda:load(a.stl,pp,root/'palette.json'))
 p=copy.deepcopy(D['palette']);p['white']={'srgb8':[255]*3};dump(cp,p);reject('extra_material',lambda:load(a.stl,root/'parameters.json',cp))
 p=copy.deepcopy(D['palette']);p['brick_family']['srgb8'][0]+=1;dump(cp,p);reject('changed_palette',lambda:load(a.stl,root/'parameters.json',cp))
 triangles=copy.deepcopy(D['triangles']);triangles[0]=tuple(reversed(triangles[0]));reject('reversed_winding',lambda:mapping(D['signatures'],triangles))
 triangles=copy.deepcopy(D['triangles']);triangles[0]=triangles[1];reject('duplicate_or_missing_face',lambda:mapping(D['signatures'],triangles))
 triangles=list(reversed(D['triangles']));assert mapping(D['signatures'],triangles)==list(reversed(range(14042)));tests['reordered_faces_positive_control']='EXACT_MAP'
 triangles=[(t[1],t[2],t[0])for t in D['triangles']];assert mapping(D['signatures'],triangles)==list(range(14042));tests['cyclic_rotation_positive_control']='EXACT_MAP'
assert sha(a.stl.read_bytes())==SHA;dump(root/'qa/fail-closed.json',{'status':'PASS','tests':tests,'production_original_stl_unchanged':True});print(tests)
